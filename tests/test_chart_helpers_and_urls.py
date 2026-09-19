"""
Unit tests for chart_helpers (Chart.js data aggregators)
and URL routing sanity checks.
"""
import json
from datetime import date, time

import pytest
from django.urls import reverse, resolve

from myapp.utils.chart_helpers import (
    get_monthly_signups, get_membership_distribution, get_revenue_trend,
    get_attendance_by_day, get_class_popularity,
    get_payment_method_distribution, get_bmi_category_distribution,
    get_rating_distribution,
)
from myapp.models import (
    BMIRecord, Membership, Payment, Attendance, GymClass, Review,
)

pytestmark = pytest.mark.django_db


class TestMonthlySignups:
    def test_returns_12_month_series(self):
        labels, data = get_monthly_signups(BMIRecord)
        assert len(json.loads(labels)) == 12
        assert len(json.loads(data)) == 12

    def test_counts_current_month_records(self, sample_bmi_record):
        labels, data = get_monthly_signups(BMIRecord)
        assert sum(json.loads(data)) == 1


class TestMembershipDistribution:
    def test_counts_payments_per_plan(self, sample_payment):
        labels, data, colors = get_membership_distribution(Membership, Payment)
        labels = json.loads(labels)
        data = json.loads(data)
        assert 'Standard Plan' in labels
        assert data[labels.index('Standard Plan')] == 1

    def test_empty_payments_falls_back_to_plans(self, sample_membership):
        labels, data, _ = get_membership_distribution(Membership, Payment)
        assert json.loads(data) == [1]


class TestRevenueTrend:
    def test_sums_completed_payments_only(self, sample_payment, pending_payment):
        labels, data = get_revenue_trend(Payment)
        assert sum(json.loads(data)) == pytest.approx(2500.0)

    def test_empty_db_returns_zero_series(self):
        labels, data = get_revenue_trend(Payment)
        assert sum(json.loads(data)) == 0


class TestAttendanceByDay:
    def test_weekday_bucketing(self, sample_attendance):
        labels, data = get_attendance_by_day(Attendance)
        days = json.loads(labels)
        counts = json.loads(data)
        assert days == ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                        'Friday', 'Saturday', 'Sunday']
        assert sum(counts) == 1


class TestClassPopularity:
    def test_enrollment_counts(self, sample_gym_class):
        labels, data = get_class_popularity(GymClass)
        assert json.loads(labels) == ['HIIT Fat Burn']
        assert json.loads(data) == [5]


class TestPaymentMethodDistribution:
    def test_method_counts(self, sample_payment):
        labels, data, colors = get_payment_method_distribution(Payment)
        labels = json.loads(labels)
        assert 'UPI' in labels
        assert len(json.loads(colors)) == len(labels)


class TestBMICategoryDistribution:
    def test_category_counts(self, sample_bmi_record):
        labels, data, colors = get_bmi_category_distribution(BMIRecord)
        labels = json.loads(labels)
        counts = json.loads(data)
        assert counts[labels.index('Healthy')] == 1
        assert sum(counts) == 1


class TestRatingDistribution:
    def test_rating_counts_only_approved(self, approved_review, unapproved_review):
        labels, data = get_rating_distribution(Review)
        counts = json.loads(data)
        assert counts == [0, 0, 0, 0, 1]  # approved 5-star only


class TestURLRouting:
    @pytest.mark.parametrize('url_name,expected_path', [
        ('dashboard', '/dashboard/'),
        ('chatbot', '/chatbot/'),
        ('chatbot-api', '/api/chatbot/'),
        ('payment-dashboard', '/payment-dashboard/'),
        ('member-progress', '/member-progress/'),
        ('reports', '/reports/'),
        ('export-members', '/export/members/'),
        ('export-payments', '/export/payments/'),
        ('export-attendance', '/export/attendance/'),
        ('export-bmi', '/export/bmi/'),
        ('export-bookings', '/export/bookings/'),
        ('testimonials', '/testimonials/'),
        ('subscribe', '/subscribe/'),
    ])
    def test_named_urls_reverse_correctly(self, url_name, expected_path):
        assert reverse(url_name) == expected_path

    def test_book_class_url_with_argument(self):
        assert reverse('book-class', kwargs={'class_id': 7}) == '/book-class/7/'

    def test_home_resolves_to_index_view(self):
        match = resolve('/')
        assert match.func.__name__ == 'index'
