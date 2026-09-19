import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from myapp.models import UserProfile

@pytest.mark.django_db
class TestUserManagement:

    def test_admin_user_list_view(self, admin_client, member_user, trainer_user):
        """Admin can list all registered users."""
        response = admin_client.get(reverse('admin_user_list'))
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        assert member_user.username in content
        assert trainer_user.username in content

    def test_non_admin_cannot_access_user_list(self, member_client, trainer_client):
        """Non-admin users cannot access user management endpoints."""
        assert member_client.get(reverse('admin_user_list')).status_code == 403
        assert trainer_client.get(reverse('admin_user_list')).status_code == 403

    def test_admin_change_user_role(self, admin_client, member_user):
        """Admin can promote a member to trainer role."""
        url = reverse('admin_user_role', kwargs={'user_id': member_user.id})
        response = admin_client.post(url, {'role': UserProfile.ROLE_TRAINER})
        assert response.status_code == 302

        member_user.refresh_from_db()
        assert member_user.profile.role == UserProfile.ROLE_TRAINER

    def test_admin_toggle_user_status(self, admin_client, member_user):
        """Admin can deactivate and activate user accounts."""
        url = reverse('admin_user_status', kwargs={'user_id': member_user.id})
        # Deactivate
        response = admin_client.post(url)
        assert response.status_code == 302
        member_user.refresh_from_db()
        assert member_user.is_active is False

        # Reactivate
        response = admin_client.post(url)
        assert response.status_code == 302
        member_user.refresh_from_db()
        assert member_user.is_active is True

    def test_last_active_admin_protection(self, admin_client, admin_user):
        """System blocks deactivating or demoting the last active Admin account."""
        # Ensure admin_user is the only active admin
        User.objects.filter(profile__role=UserProfile.ROLE_ADMIN).exclude(id=admin_user.id).delete()

        # 1. Attempt to demote last admin
        role_url = reverse('admin_user_role', kwargs={'user_id': admin_user.id})
        res_role = admin_client.post(role_url, {'role': UserProfile.ROLE_MEMBER})
        assert res_role.status_code == 302
        admin_user.refresh_from_db()
        assert admin_user.profile.role == UserProfile.ROLE_ADMIN

        # 2. Attempt to deactivate last admin
        status_url = reverse('admin_user_status', kwargs={'user_id': admin_user.id})
        res_status = admin_client.post(status_url)
        assert res_status.status_code == 302
        admin_user.refresh_from_db()
        assert admin_user.is_active is True
