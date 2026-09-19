from functools import wraps
from django.shortcuts import redirect, render
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin
from .models import UserProfile

def get_user_role(user):
    """Retrieve user role safely from UserProfile or fallback to MEMBER."""
    if not user.is_authenticated:
        return None
    if hasattr(user, 'profile'):
        return user.profile.role
    # Fallback safe auto-creation
    profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'role': 'MEMBER'})
    return profile.role


def role_required(*allowed_roles):
    """
    Decorator enforcing role-based access control.
    Supports single or multiple roles (e.g., @role_required('ADMIN', 'TRAINER')).
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.path.startswith('/api/'):
                    return JsonResponse({'error': 'Authentication required'}, status=401)
                messages.warning(request, 'Please log in to access this page.')
                return redirect(f'/login/?next={request.path}')

            if not request.user.is_active:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.path.startswith('/api/'):
                    return JsonResponse({'error': 'Account inactive'}, status=403)
                messages.error(request, 'Your account is currently inactive.')
                return redirect('/login/')

            # Superuser bypasses role checks
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            role = get_user_role(request.user)
            if role in allowed_roles:
                return view_func(request, *args, **kwargs)

            # Unauthorized
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.path.startswith('/api/'):
                return JsonResponse({'error': 'You do not have permission to perform this action.'}, status=403)

            return render(request, '403.html', {'message': 'You do not have permission to access this page.'}, status=403)

        return _wrapped_view
    return decorator


def admin_required(view_func):
    return role_required('ADMIN')(view_func)

def trainer_required(view_func):
    return role_required('TRAINER')(view_func)

def member_required(view_func):
    return role_required('MEMBER')(view_func)


# CBV Mixins
class RoleRequiredMixin(AccessMixin):
    allowed_roles = ()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not request.user.is_active:
            messages.error(request, 'Your account is currently inactive.')
            return redirect('/login/')

        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        role = get_user_role(request.user)
        if role in self.allowed_roles:
            return super().dispatch(request, *args, **kwargs)

        return render(request, '403.html', {'message': 'You do not have permission to access this page.'}, status=403)


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ('ADMIN',)

class TrainerRequiredMixin(RoleRequiredMixin):
    allowed_roles = ('TRAINER',)

class MemberRequiredMixin(RoleRequiredMixin):
    allowed_roles = ('MEMBER',)
