import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from myapp.models import UserProfile, Booking, WorkoutLog, BMIRecord

@pytest.mark.django_db
class TestSecurityDataIsolation:

    def test_member_isolated_progress_data(self, client, sample_gym_class):
        """Member A cannot see Member B's workout logs or progress data."""
        user_a = User.objects.create_user('member_a', 'a@test.com', 'Pass123!')
        user_a.profile.role = UserProfile.ROLE_MEMBER
        user_a.profile.save()

        user_b = User.objects.create_user('member_b', 'b@test.com', 'Pass123!')
        user_b.profile.role = UserProfile.ROLE_MEMBER
        user_b.profile.save()

        # Log workout for Member A
        WorkoutLog.objects.create(
            user=user_a,
            member_name='Member A',
            exercise='Dragon Flags 99',
            sets=5,
            reps=5,
            weight_used=100.0
        )

        # Log workout for Member B
        WorkoutLog.objects.create(
            user=user_b,
            member_name='Member B',
            exercise='Zurcher Squats 88',
            sets=4,
            reps=8,
            weight_used=80.0
        )

        # Login as Member A and view progress page
        client.force_login(user_a)
        res_a = client.get(reverse('member-progress'))
        assert res_a.status_code == 200
        content_a = res_a.content.decode('utf-8')
        assert 'Dragon Flags 99' in content_a
        assert 'Zurcher Squats 88' not in content_a

    def test_member_dashboard_isolated_bookings(self, client, sample_gym_class):
        """Member dashboard shows only the logged-in member's own bookings."""
        user_a = User.objects.create_user('user_a', 'a@test.com', 'Pass123!')
        user_a.profile.role = UserProfile.ROLE_MEMBER
        user_a.profile.save()

        user_b = User.objects.create_user('user_b', 'b@test.com', 'Pass123!')
        user_b.profile.role = UserProfile.ROLE_MEMBER
        user_b.profile.save()

        Booking.objects.create(user=user_a, gym_class=sample_gym_class, member_name='User A', status='CONFIRMED')
        Booking.objects.create(user=user_b, gym_class=sample_gym_class, member_name='User B', status='CONFIRMED')

        client.force_login(user_a)
        res = client.get(reverse('member_dashboard'))
        assert res.status_code == 200
        context_bookings = res.context['recent_bookings']
        assert all(b.user == user_a for b in context_bookings)
