"""
Model layer tests: properties, computed fields and string representations
for all Django models (BMIRecord, GymClass, Booking, Membership, etc.)
"""
import time

import pytest

from myapp.models import (
    Membership, GymClass, Booking, BMIRecord, Subscriber, Review,
    Payment, Attendance, WorkoutLog, Team,
)

pytestmark = pytest.mark.django_db


class TestMembership:
    def test_get_features_splits_comma_separated_list(self, sample_membership):
        features = sample_membership.get_features
        assert features == ['Free riding', 'Unlimited equipments', 'Personal trainer']

    def test_get_features_strips_whitespace_and_empty_entries(self):
        m = Membership.objects.create(name='X', price='100', features_list=' a , ,b, ')
        assert m.get_features == ['a', 'b']

    def test_str_includes_name_and_price(self, sample_membership):
        assert 'Standard Plan' in str(sample_membership)
        assert '2500' in str(sample_membership)


class TestGymClass:
    def test_available_slots(self, sample_gym_class):
        assert sample_gym_class.available_slots == 15

    def test_is_full_false_when_slots_remain(self, sample_gym_class):
        assert sample_gym_class.is_full is False

    def test_is_full_true_when_capacity_reached(self, full_gym_class):
        assert full_gym_class.is_full is True
        assert full_gym_class.available_slots == 0

    def test_occupancy_percentage(self, sample_gym_class):
        assert sample_gym_class.occupancy_percentage == 25

    def test_occupancy_percentage_zero_capacity(self):
        gc = GymClass.objects.create(
            name='Empty', trainer='None', schedule_day='Monday',
            schedule_time='07:00', capacity=0, current_enrolled=0,
        )
        assert gc.occupancy_percentage == 0

    def test_str_contains_name_and_day(self, sample_gym_class):
        text = str(sample_gym_class)
        assert 'HIIT Fat Burn' in text
        assert 'Monday' in text


class TestBooking:
    def test_default_status_is_confirmed(self, sample_booking):
        assert sample_booking.status == 'Confirmed'

    def test_str_contains_member_and_class(self, sample_booking):
        text = str(sample_booking)
        assert 'Aarav Sharma' in text
        assert 'HIIT Fat Burn' in text

    def test_cascade_delete_with_class(self, sample_booking, sample_gym_class):
        sample_gym_class.delete()
        assert Booking.objects.count() == 0


class TestBMIRecord:
    def test_str_contains_bmi_value_and_category(self, sample_bmi_record):
        text = str(sample_bmi_record)
        assert 'Aarav Sharma' in text
        assert '22.9' in text
        assert 'Healthy' in text

    def test_ordering_newest_first(self, sample_bmi_record):
        time.sleep(0.02)  # ensure a distinct created_at timestamp
        newer = BMIRecord.objects.create(
            name='Second', height=160, weight=55, age=22,
            gender='Female', bmi_value=21.5, category='Healthy',
        )
        assert BMIRecord.objects.first() == newer


class TestPayment:
    def test_str_contains_amount_and_status(self, sample_payment):
        text = str(sample_payment)
        assert 'Aarav Sharma' in text
        assert 'Completed' in text

    def test_membership_set_null_on_delete(self, sample_payment, sample_membership):
        sample_membership.delete()
        sample_payment.refresh_from_db()
        assert sample_payment.membership is None


class TestMiscModelStr:
    def test_attendance_str(self, sample_attendance):
        assert 'Aarav Sharma' in str(sample_attendance)

    def test_workout_log_str(self, sample_workout_log):
        assert 'Bench Press' in str(sample_workout_log)

    def test_team_str(self, sample_team):
        assert str(sample_team) == 'Priya Joshi - Yoga Trainer'

    def test_subscriber_str_active(self, sample_subscriber):
        assert 'Active' in str(sample_subscriber)

    def test_subscriber_str_inactive(self, sample_subscriber):
        sample_subscriber.is_active = False
        sample_subscriber.save()
        assert 'Inactive' in str(sample_subscriber)

    def test_review_str(self, approved_review):
        assert '5 Stars' in str(approved_review)
