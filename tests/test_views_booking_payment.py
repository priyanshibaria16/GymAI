"""
Integration tests for Module 3 & 4:
- Class Booking & Attendance (timetable, booking flow, capacity handling)
- Payment & Revenue Tracker dashboard
"""
import pytest

from myapp.models import Booking, GymClass

pytestmark = pytest.mark.django_db


class TestClassTimetable:
    def test_timetable_renders(self, client, sample_gym_class):
        response = client.get('/class-timetable/')
        assert response.status_code == 200
        assert 'class-timetable.html' in [t.name for t in response.templates]

    def test_timetable_groups_classes_by_day(self, client, sample_gym_class):
        response = client.get('/class-timetable/')
        timetable = response.context['timetable']
        assert 'Monday' in timetable
        assert 'Tuesday' not in timetable

    def test_timetable_provides_chart_data(self, client, sample_gym_class):
        response = client.get('/class-timetable/')
        assert 'HIIT Fat Burn' in response.context['class_names']
        assert '5' in response.context['class_enrolled']
        assert '20' in response.context['class_capacity']

    def test_timetable_empty_db(self, client):
        assert client.get('/class-timetable/').status_code == 200


class TestBookClass:
    def test_get_shows_booking_form(self, client, sample_gym_class):
        response = client.get(f'/book-class/{sample_gym_class.id}/')
        assert response.status_code == 200
        assert 'form' in response.context

    def test_post_creates_confirmed_booking(self, client, sample_gym_class):
        response = client.post(f'/book-class/{sample_gym_class.id}/', {
            'member_name': 'Test Booker',
            'member_email': 'booker@example.com',
        })
        assert response.status_code == 200
        assert response.context['success'] is True
        booking = Booking.objects.get(member_name='Test Booker')
        assert booking.status == 'Confirmed'
        assert booking.gym_class == sample_gym_class

    def test_post_increments_enrollment_count(self, client, sample_gym_class):
        client.post(f'/book-class/{sample_gym_class.id}/', {'member_name': 'Member A'})
        sample_gym_class.refresh_from_db()
        assert sample_gym_class.current_enrolled == 6

    def test_booking_full_class_shows_error(self, client, full_gym_class):
        response = client.post(f'/book-class/{full_gym_class.id}/', {
            'member_name': 'Late Booker',
        })
        assert response.status_code == 200
        assert 'fully booked' in response.context['error']
        assert Booking.objects.count() == 0

    def test_invalid_form_rerenders_without_booking(self, client, sample_gym_class):
        response = client.post(f'/book-class/{sample_gym_class.id}/', {'member_name': ''})
        assert response.status_code == 200
        assert Booking.objects.count() == 0

    def test_nonexistent_class_returns_404(self, client):
        assert client.get('/book-class/99999/').status_code == 404

    def test_email_is_optional(self, client, sample_gym_class):
        response = client.post(f'/book-class/{sample_gym_class.id}/', {
            'member_name': 'No Email Member',
        })
        assert response.context['success'] is True


class TestPaymentDashboard:
    def test_dashboard_renders(self, admin_client, sample_payment):
        response = admin_client.get('/payment-dashboard/')
        assert response.status_code == 200

    def test_revenue_counts_only_completed_payments(
            self, admin_client, sample_payment, pending_payment):
        response = admin_client.get('/payment-dashboard/')
        ctx = response.context
        assert float(ctx['total_revenue']) == 2500.00
        assert float(ctx['pending_amount']) == 1500.00

    def test_transaction_counts(self, admin_client, sample_payment, pending_payment):
        response = admin_client.get('/payment-dashboard/')
        ctx = response.context
        assert ctx['total_transactions'] == 2
        assert ctx['completed_count'] == 1
        assert ctx['pending_count'] == 1
        assert ctx['failed_count'] == 0

    def test_empty_db_renders_with_zero_totals(self, admin_client):
        response = admin_client.get('/payment-dashboard/')
        assert response.status_code == 200
        assert float(response.context['total_revenue']) == 0
