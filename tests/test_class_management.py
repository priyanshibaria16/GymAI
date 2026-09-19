"""
Tests for Admin class management (add/edit/delete + assign trainer) and the
trainer per-class roster / attendance flow.
"""
from datetime import date, time

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from myapp.models import (
    UserProfile, Team, GymClass, Booking, Attendance, Membership,
)


@pytest.fixture
def team(db):
    return Team.objects.create(name="Priya Joshi", post="Yoga Trainer")


@pytest.fixture
def other_team(db):
    return Team.objects.create(name="Vikram Shah", post="HIIT Trainer")


@pytest.fixture
def trainer_with_team(db, team):
    user = User.objects.create_user('coach_priya', 'priya@test.com', 'TrainerPass123!')
    user.first_name = 'Priya'
    user.last_name = 'Joshi'
    user.save()
    user.profile.role = UserProfile.ROLE_TRAINER
    user.profile.trainer = team
    user.profile.save()
    return user


@pytest.fixture
def trainer_with_team_client(client, trainer_with_team):
    client.force_login(trainer_with_team)
    return client


@pytest.fixture
def their_class(team):
    return GymClass.objects.create(
        name="Power Yoga", trainer=team.name, assigned_trainer=team,
        schedule_day="Tuesday", schedule_time=time(6, 30),
        duration_minutes=60, capacity=10, current_enrolled=1,
    )


@pytest.fixture
def other_class(other_team):
    return GymClass.objects.create(
        name="HIIT", trainer=other_team.name, assigned_trainer=other_team,
        schedule_day="Monday", schedule_time=time(7, 0),
        capacity=15,
    )


@pytest.fixture
def enrolled_member(db, their_class):
    user = User.objects.create_user('member_one', 'm1@test.com', 'MemberPass123!')
    user.first_name = 'Aarav'
    user.last_name = 'Sharma'
    user.save()
    Booking.objects.create(
        user=user, member_name=user.get_full_name(), member_email=user.email,
        gym_class=their_class, status='Confirmed',
    )
    return user


# --------------------------------------------------------------------------- #
# Admin class management
# --------------------------------------------------------------------------- #
@pytest.mark.django_db
class TestAdminClassManagement:

    def test_admin_can_view_class_list(self, admin_client):
        response = admin_client.get(reverse('admin-class-list'))
        assert response.status_code == 200

    def test_admin_can_create_and_assign_class(self, admin_client, team):
        response = admin_client.post(reverse('admin-class-add'), {
            'name': 'Spin Cycling',
            'assigned_trainer': team.id,
            'schedule_day': 'Wednesday',
            'schedule_time': '18:00',
            'duration_minutes': 45,
            'capacity': 12,
            'description': 'Indoor cycling',
        })
        assert response.status_code == 302
        cls = GymClass.objects.get(name='Spin Cycling')
        assert cls.assigned_trainer == team
        # legacy text field kept in sync
        assert cls.trainer == team.name

    def test_admin_can_edit_class_trainer(self, admin_client, their_class, other_team):
        response = admin_client.get(reverse('admin-class-edit', args=[their_class.id]))
        assert response.status_code == 200
        response = admin_client.post(reverse('admin-class-edit', args=[their_class.id]), {
            'name': their_class.name,
            'assigned_trainer': other_team.id,
            'schedule_day': their_class.schedule_day,
            'schedule_time': '06:30',
            'duration_minutes': 60,
            'capacity': 10,
        })
        assert response.status_code == 302
        their_class.refresh_from_db()
        assert their_class.assigned_trainer == other_team
        assert their_class.trainer == other_team.name

    def test_admin_can_delete_class(self, admin_client, their_class):
        pk = their_class.id
        response = admin_client.post(reverse('admin-class-delete', args=[pk]))
        assert response.status_code == 302
        assert not GymClass.objects.filter(pk=pk).exists()

    def test_delete_is_post_only(self, admin_client, their_class):
        response = admin_client.get(reverse('admin-class-delete', args=[their_class.id]))
        assert response.status_code == 302  # redirect, no delete
        assert GymClass.objects.filter(pk=their_class.id).exists()

    def test_member_cannot_access_class_admin(self, member_client):
        assert member_client.get(reverse('admin-class-list')).status_code == 403

    def test_anonymous_redirected(self, client):
        response = client.get(reverse('admin-class-list'))
        assert response.status_code == 302
        assert reverse('login') in response.url


# --------------------------------------------------------------------------- #
# Trainer roster + attendance
# --------------------------------------------------------------------------- #
@pytest.mark.django_db
class TestTrainerClassAttendance:

    def test_dashboard_only_shows_assigned_classes(self, trainer_with_team_client, their_class, other_class):
        response = trainer_with_team_client.get(reverse('trainer-dashboard'))
        assert response.status_code == 200
        classes = list(response.context['assigned_classes'])
        assert their_class in classes
        assert other_class not in classes

    def test_trainer_can_view_own_roster(self, trainer_with_team_client, their_class, enrolled_member):
        response = trainer_with_team_client.get(
            reverse('trainer-class-attendance', args=[their_class.id]))
        assert response.status_code == 200
        roster = response.context['roster']
        assert len(roster) == 1
        assert roster[0]['member_name'] == enrolled_member.get_full_name()

    def test_trainer_cannot_view_other_class_roster(self, trainer_with_team_client, other_class):
        response = trainer_with_team_client.get(
            reverse('trainer-class-attendance', args=[other_class.id]))
        assert response.status_code == 403

    def test_trainer_marks_class_attendance(self, trainer_with_team_client, their_class, enrolled_member):
        response = trainer_with_team_client.post(reverse('trainer-mark-attendance'), {
            'gym_class_id': their_class.id,
            'member_user_id': enrolled_member.id,
            'member_name': enrolled_member.get_full_name(),
            'action': 'mark_present',
        })
        assert response.status_code == 302
        assert Attendance.objects.filter(
            gym_class=their_class, user=enrolled_member).exists()

    def test_mark_attendance_blocked_for_other_trainers_class(
            self, trainer_with_team_client, other_class, enrolled_member):
        response = trainer_with_team_client.post(reverse('trainer-mark-attendance'), {
            'gym_class_id': other_class.id,
            'member_name': 'Someone',
            'action': 'mark_present',
        })
        assert response.status_code == 403
        assert not Attendance.objects.filter(gym_class=other_class).exists()

    def test_member_cannot_access_trainer_attendance(self, member_client, their_class):
        response = member_client.get(
            reverse('trainer-class-attendance', args=[their_class.id]))
        assert response.status_code == 403
