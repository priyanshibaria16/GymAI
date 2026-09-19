"""
Integration tests for Module 1: Analytics Dashboard
Verifies stats aggregation, chart data serialization and ML churn analytics.
"""
import json

import pytest

pytestmark = pytest.mark.django_db


class TestDashboardRendering:
    def test_dashboard_renders_with_empty_db(self, admin_client):
        response = admin_client.get('/executive-analytics/')
        assert response.status_code == 200
        assert 'dashboard.html' in [t.name for t in response.templates]

    def test_dashboard_renders_with_data(
            self, admin_client, sample_bmi_record, sample_payment,
            sample_gym_class, sample_booking, sample_attendance,
            sample_subscriber, approved_review, sample_membership):
        response = admin_client.get('/executive-analytics/')
        assert response.status_code == 200


class TestDashboardStats:
    def test_stats_cards_aggregate_correctly(
            self, admin_client, sample_bmi_record, sample_payment,
            pending_payment, sample_gym_class, sample_attendance,
            sample_subscriber, approved_review, unapproved_review):
        response = admin_client.get('/executive-analytics/')
        ctx = response.context
        assert ctx['total_members'] == 1          # distinct BMI record names
        assert float(ctx['total_revenue']) == 2500.00  # Completed only
        assert ctx['active_classes'] == 1
        assert ctx['avg_bmi'] == pytest.approx(22.9, abs=0.05)
        assert ctx['total_attendance'] == 1
        assert ctx['total_subscribers'] == 1
        assert ctx['avg_rating'] == 5.0           # approved reviews only

    def test_empty_db_yields_zero_stats(self, admin_client):
        ctx = admin_client.get('/executive-analytics/').context
        assert ctx['total_members'] == 0
        assert float(ctx['total_revenue']) == 0
        assert ctx['avg_bmi'] == 0
        assert ctx['avg_rating'] == 0


class TestDashboardChartData:
    def test_chart_data_is_valid_json(self, admin_client, sample_bmi_record, sample_payment):
        ctx = admin_client.get('/executive-analytics/').context
        for key in ('signup_labels', 'signup_data', 'membership_labels',
                    'membership_data', 'revenue_labels', 'revenue_data',
                    'attendance_labels', 'attendance_data', 'class_labels',
                    'class_data', 'payment_labels', 'payment_data',
                    'bmi_labels', 'bmi_data'):
            parsed = json.loads(ctx[key])
            assert isinstance(parsed, list), f'{key} must serialize to a list'

    def test_signup_labels_cover_12_months(self, admin_client):
        ctx = admin_client.get('/executive-analytics/').context
        assert len(json.loads(ctx['signup_labels'])) == 12
        assert len(json.loads(ctx['signup_data'])) == 12

    def test_bmi_category_distribution_counts(self, admin_client, sample_bmi_record):
        ctx = admin_client.get('/executive-analytics/').context
        labels = json.loads(ctx['bmi_labels'])
        data = json.loads(ctx['bmi_data'])
        assert labels == ['Underweight', 'Healthy', 'Overweight', 'Obese']
        assert data[labels.index('Healthy')] == 1


class TestDashboardChurnAnalytics:
    def test_churn_data_present_in_context(self, admin_client, sample_bmi_record):
        ctx = admin_client.get('/executive-analytics/').context
        churn = ctx['churn_data']
        assert 'at_risk_members' in churn
        assert 'risk_distribution' in churn

    def test_churn_evaluates_db_members(self, admin_client, sample_bmi_record, sample_attendance):
        ctx = admin_client.get('/executive-analytics/').context
        churn = ctx['churn_data']
        names = [m['name'] for m in churn['at_risk_members']]
        assert 'Aarav Sharma' in names
        for member in churn['at_risk_members']:
            assert 0 <= member['risk_probability'] <= 100
            assert member['risk_level'] in ('Low', 'Medium', 'High')

    def test_churn_falls_back_to_demo_members_when_db_empty(self, admin_client):
        ctx = admin_client.get('/executive-analytics/').context
        churn = ctx['churn_data']
        assert len(churn['at_risk_members']) > 0
