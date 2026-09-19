import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from myapp.models import UserProfile

@pytest.mark.django_db
class TestAuthentication:

    def test_signup_forces_member_role(self, client):
        """Public signup must strictly set role='MEMBER' even if someone posts role='ADMIN'."""
        signup_url = reverse('signup')
        payload = {
            'username': 'newmember',
            'email': 'newmember@example.com',
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!',
            'first_name': 'New',
            'last_name': 'Member',
            'phone': '9876543210',
            'role': 'ADMIN'  # Attempting privilege escalation
        }
        response = client.post(signup_url, payload)
        assert response.status_code == 302
        assert response.url == '/member-dashboard/'

        user = User.objects.get(username='newmember')
        assert user.profile.role == UserProfile.ROLE_MEMBER

    def test_signup_password_mismatch(self, client):
        """Signup fails when password and confirm_password do not match."""
        signup_url = reverse('signup')
        payload = {
            'username': 'baduser',
            'email': 'baduser@example.com',
            'password': 'Password123!',
            'confirm_password': 'DifferentPassword123!',
            'first_name': 'Bad',
            'last_name': 'User',
        }
        response = client.post(signup_url, payload)
        assert response.status_code == 200
        assert not User.objects.filter(username='baduser').exists()

    def test_login_success(self, client, member_user):
        """Valid credentials log in successfully and redirect to dashboard router."""
        login_url = reverse('login')
        response = client.post(login_url, {
            'username': 'test_member',
            'password': 'MemberPass123!'
        })
        assert response.status_code == 302
        assert response.url == reverse('dashboard')

    def test_login_invalid_credentials(self, client, member_user):
        """Invalid credentials stay on login page with error."""
        login_url = reverse('login')
        response = client.post(login_url, {
            'username': 'test_member',
            'password': 'WrongPassword'
        })
        assert response.status_code == 200
        assert '_auth_user_id' not in client.session

    def test_logout(self, member_client):
        """Logout clears session and redirects to login page."""
        logout_url = reverse('logout')
        response = member_client.get(logout_url)
        assert response.status_code == 302
        assert response.url == reverse('login')

    def test_profile_view_authenticated(self, member_client, member_user):
        """Authenticated user can view their profile."""
        profile_url = reverse('profile')
        response = member_client.get(profile_url)
        assert response.status_code == 200
        assert member_user.username in response.content.decode('utf-8')

    def test_edit_profile(self, member_client, member_user):
        """User can edit their first_name, last_name, email, and phone."""
        edit_url = reverse('edit_profile')
        response = member_client.post(edit_url, {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'member@test.com',
            'phone': '9998887770'
        })
        assert response.status_code == 302
        member_user.refresh_from_db()
        assert member_user.first_name == 'Updated'
        assert member_user.profile.phone == '9998887770'

    def test_change_password(self, member_client, member_user):
        """User can change password with correct current password."""
        change_pass_url = reverse('change_password')
        response = member_client.post(change_pass_url, {
            'old_password': 'MemberPass123!',
            'new_password1': 'BrandNewPassword123!',
            'new_password2': 'BrandNewPassword123!',
        })
        assert response.status_code == 302
        member_user.refresh_from_db()
        assert member_user.check_password('BrandNewPassword123!')
