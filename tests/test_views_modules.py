"""
Integration tests for Modules 5, 6 and 7:
- Member Progress Tracker (workout logs + body metrics)
- Newsletter subscribe/unsubscribe
- Testimonials & Reviews
"""
from datetime import date

import pytest

from myapp.models import (
    Subscriber, WorkoutLog, BodyMetrics, Review,
)

pytestmark = pytest.mark.django_db


class TestNewsletter:
    def test_subscribe_creates_active_subscriber(self, client):
        response = client.post('/subscribe/', {'email': 'new@example.com'})
        assert response.status_code == 302
        assert Subscriber.objects.filter(email='new@example.com', is_active=True).exists()

    def test_subscribe_reactivates_inactive_subscriber(self, client, sample_subscriber):
        sample_subscriber.is_active = False
        sample_subscriber.save()
        client.post('/subscribe/', {'email': 'member@example.com'})
        sample_subscriber.refresh_from_db()
        assert sample_subscriber.is_active is True

    def test_subscribe_does_not_duplicate(self, client, sample_subscriber):
        client.post('/subscribe/', {'email': 'member@example.com'})
        assert Subscriber.objects.filter(email='member@example.com').count() == 1

    def test_unsubscribe_deactivates_subscriber(self, client, sample_subscriber):
        response = client.post('/unsubscribe/', {'email': 'member@example.com'})
        assert response.status_code == 302
        sample_subscriber.refresh_from_db()
        assert sample_subscriber.is_active is False

    def test_get_requests_redirect_home(self, client):
        assert client.get('/subscribe/').status_code == 302
        assert client.get('/unsubscribe/').status_code == 302


class TestMemberProgress:
    def test_progress_page_renders(
            self, member_client, sample_workout_log, sample_body_metrics):
        response = member_client.get('/member-progress/')
        assert response.status_code == 200

    def test_progress_page_filters_by_member(
            self, admin_client, sample_workout_log, sample_body_metrics):
        WorkoutLog.objects.create(
            member_name='Other Person', exercise='Squats',
            sets=3, reps=8, weight_used=80.0, date=date.today(),
        )
        response = admin_client.get('/member-progress/', {'member': 'Aarav'})
        logs = response.context['workout_logs']
        assert logs.count() == 1
        assert logs[0].member_name == 'Aarav Sharma'

    def test_unique_member_list_in_context(self, admin_client, sample_workout_log):
        ctx = admin_client.get('/member-progress/').context
        assert 'Aarav Sharma' in ctx['unique_members']

    def test_add_workout_creates_log_and_redirects(self, member_client):
        response = member_client.post('/add-workout/', {
            'member_name': 'Test Lifter',
            'exercise': 'Deadlift',
            'sets': 5,
            'reps': 5,
            'weight_used': 120.0,
            'date': date.today().isoformat(),
        })
        assert response.status_code == 302
        assert WorkoutLog.objects.filter(exercise='Deadlift').exists()

    def test_add_workout_invalid_form_does_not_save(self, member_client):
        member_client.post('/add-workout/', {'member_name': '', 'exercise': ''})
        assert WorkoutLog.objects.count() == 0

    def test_add_metrics_creates_record_and_redirects(self, member_client):
        response = member_client.post('/add-metrics/', {
            'member_name': 'Test Lifter',
            'body_weight': 78.5,
            'chest': 40.0,
            'waist': 33.0,
            'biceps': 15.0,
            'thighs': 23.0,
            'date': date.today().isoformat(),
        })
        assert response.status_code == 302
        assert BodyMetrics.objects.filter(body_weight=78.5).exists()


class TestTestimonials:
    def test_page_shows_only_approved_reviews(
            self, client, approved_review, unapproved_review):
        response = client.get('/testimonials/')
        assert response.status_code == 200
        reviews = list(response.context['reviews'])
        assert len(reviews) == 1
        assert reviews[0].member_name == 'Aarav Sharma'

    def test_average_rating_computed(self, client, approved_review):
        ctx = client.get('/testimonials/').context
        assert ctx['avg_rating'] == 5.0
        assert ctx['total_reviews'] == 1

    def test_submit_review_redirects_and_requires_approval(self, client):
        response = client.post('/testimonials/', {
            'member_name': 'Reviewer',
            'rating': 4,
            'review_text': 'Great gym!',
        })
        assert response.status_code == 302
        review = Review.objects.get(member_name='Reviewer')
        assert review.is_approved is False

    def test_invalid_review_rerenders_form(self, client):
        response = client.post('/testimonials/', {'member_name': '', 'rating': 5, 'review_text': ''})
        assert response.status_code == 200
        assert Review.objects.count() == 0
