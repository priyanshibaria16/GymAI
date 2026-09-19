"""
Tests for the Admin AI Automations (Gemini-powered, with local fallback).

The conftest autouse fixtures force GEMINI_API_KEY='' and clear the module
cache, so every assertion here exercises the deterministic local path and
never makes a live network call.
"""
import pytest
from django.urls import reverse

from myapp.ai_engine import automations, gemini_client


@pytest.mark.django_db
class TestGeminiClient:

    def test_unconfigured_without_key(self, settings):
        settings.GEMINI_API_KEY = ''
        assert gemini_client.is_configured() is False
        result = gemini_client.generate_text("hello")
        assert result['ok'] is False
        assert result['source'] == 'unconfigured'

    def test_generate_text_never_raises_on_network_error(self, settings, monkeypatch):
        settings.GEMINI_API_KEY = 'fake-key'
        import urllib.request

        def _boom(*args, **kwargs):
            raise urllib.error.URLError("no network")

        monkeypatch.setattr(urllib.request, 'urlopen', _boom)
        result = gemini_client.generate_text("hello")
        assert result['ok'] is False
        assert result['source'] == 'gemini'
        assert result['error']  # a message is captured, no exception raised


@pytest.mark.django_db
class TestExecutiveBriefing:

    def test_briefing_fallback_without_key(self):
        briefing = automations.generate_executive_briefing()
        assert briefing['source'] == 'fallback'
        assert briefing['text']
        assert 'IronPeak' in briefing['text']
        assert 'metrics' in briefing

    def test_metrics_shape(self):
        m = automations.gather_executive_metrics()
        for key in ('total_members', 'month_revenue', 'pending_revenue',
                    'high_risk', 'occupancy_pct', 'churn'):
            assert key in m

    def test_briefing_is_cached(self):
        first = automations.generate_executive_briefing()
        second = automations.generate_executive_briefing()
        assert first is second  # same cached object
        forced = automations.generate_executive_briefing(force=True)
        assert forced is not first  # force bypasses cache


@pytest.mark.django_db
class TestRetentionDrafts:

    def test_retention_returns_dict(self):
        retention = automations.generate_retention_drafts()
        assert 'drafts' in retention
        assert retention['source'] in ('gemini', 'fallback')

    def test_high_risk_draft_has_message(self, sample_bmi_record, pending_payment):
        # Build a member likely to be high risk (lots of inactivity via defaults)
        retention = automations.generate_retention_drafts()
        for d in retention['drafts']:
            assert d['message']
            assert d['name']
            assert 'risk_probability' in d


@pytest.mark.django_db
class TestAutomationsAccess:

    def test_admin_can_view_automations_page(self, admin_client):
        response = admin_client.get(reverse('admin-automations'))
        assert response.status_code == 200
        assert 'briefing' in response.context
        assert 'retention' in response.context

    def test_member_cannot_view_automations(self, member_client):
        response = member_client.get(reverse('admin-automations'))
        assert response.status_code == 403

    def test_anonymous_redirected_to_login(self, client):
        response = client.get(reverse('admin-automations'))
        assert response.status_code == 302
        assert reverse('login') in response.url

    def test_dashboard_shows_ai_briefing(self, admin_client):
        response = admin_client.get(reverse('admin_dashboard'))
        assert response.status_code == 200
        assert response.context['ai_briefing'] is not None
        assert response.context['ai_briefing']['text']
