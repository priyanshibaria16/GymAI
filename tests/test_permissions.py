import pytest
from django.urls import reverse
from myapp.models import UserProfile

@pytest.mark.django_db
class TestRolePermissions:

    def test_dashboard_router_redirects(self, client, admin_user, trainer_user, member_user):
        """Central /dashboard/ route redirects each user role to their specific dashboard."""
        # Admin
        client.force_login(admin_user)
        res_admin = client.get(reverse('dashboard'))
        assert res_admin.status_code == 302
        assert res_admin.url == '/admin-dashboard/'

        # Trainer
        client.force_login(trainer_user)
        res_trainer = client.get(reverse('dashboard'))
        assert res_trainer.status_code == 302
        assert res_trainer.url == '/trainer-dashboard/'

        # Member
        client.force_login(member_user)
        res_member = client.get(reverse('dashboard'))
        assert res_member.status_code == 302
        assert res_member.url == '/member-dashboard/'

    def test_unauthenticated_dashboard_redirects_to_login(self, client):
        """Unauthenticated requests to /dashboard/ redirect to login page."""
        response = client.get(reverse('role_dashboard'))
        assert response.status_code == 302
        assert reverse('login') in response.url

    def test_member_cannot_access_admin_dashboard(self, member_client):
        """Member accessing admin dashboard gets 403 Forbidden."""
        response = member_client.get(reverse('admin_dashboard'))
        assert response.status_code == 403

    def test_member_cannot_access_payment_dashboard(self, member_client):
        """Member accessing payments gets 403 Forbidden."""
        response = member_client.get(reverse('payment-dashboard'))
        assert response.status_code == 403

    def test_trainer_cannot_access_payment_dashboard(self, trainer_client):
        """Trainer accessing financial payments gets 403 Forbidden."""
        response = trainer_client.get(reverse('payment-dashboard'))
        assert response.status_code == 403

    def test_trainer_cannot_access_reports_page(self, trainer_client):
        """Trainer accessing reports page gets 403 Forbidden."""
        response = trainer_client.get(reverse('reports'))
        assert response.status_code == 403

    def test_admin_can_access_all_dashboards(self, admin_client):
        """Admin has full access across all sections."""
        assert admin_client.get(reverse('admin_dashboard')).status_code == 200
        assert admin_client.get(reverse('trainer_dashboard')).status_code == 200
        assert admin_client.get(reverse('member_dashboard')).status_code == 200
        assert admin_client.get(reverse('payment-dashboard')).status_code == 200
        assert admin_client.get(reverse('reports')).status_code == 200

    def test_trainer_cannot_access_member_dashboard(self, trainer_client):
        """Trainer accessing the member self-service dashboard gets 403 Forbidden."""
        assert trainer_client.get(reverse('member-dashboard')).status_code == 403

    def test_trainer_only_sees_assigned_member_progress(self, trainer_client, sample_workout_log):
        """A trainer with no assigned members must NOT see any member's progress data."""
        response = trainer_client.get('/member-progress/')
        assert response.status_code == 200
        # sample_workout_log belongs to an unrelated member and trainer has none assigned
        assert response.context['workout_logs'].count() == 0
        assert response.context['unique_members'] == []
