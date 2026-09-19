from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models, transaction
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import CustomSignupForm, CustomLoginForm, UserProfileForm
from .models import UserProfile, BMIRecord, Booking, WorkoutLog, BodyMetrics
from .decorators import role_required, get_user_role


def signup_view(request):
    """
    Public Member Registration endpoint.
    Public signup ALWAYS creates role='MEMBER'.
    """
    if request.user.is_authenticated:
        return redirect('/dashboard/')

    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        email=form.cleaned_data['email'],
                        password=form.cleaned_data['password'],
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name']
                    )
                    # Force role='MEMBER' for all public signups
                    profile, _ = UserProfile.objects.get_or_create(user=user)
                    profile.role = 'MEMBER'
                    profile.phone = form.cleaned_data.get('phone', '')
                    profile.save()

                    login(request, user)
                    messages.success(request, f"Welcome to IronPeak Fitness Studio, {user.first_name}! Your member account has been created.")
                    return redirect('/member-dashboard/')
            except Exception as e:
                messages.error(request, f"Registration failed: {str(e)}")
        else:
            messages.error(request, "Please correct the errors in the registration form below.")
    else:
        form = CustomSignupForm()

    return render(request, 'auth/signup.html', {'form': form})


def login_view(request):
    """
    Authentication login endpoint.
    Supports username or email authentication.
    Redirects user to their role-specific dashboard.
    """
    if request.user.is_authenticated:
        return redirect('/dashboard/')

    next_url = request.GET.get('next', '')

    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Support login by email
            user_obj = User.objects.filter(email__iexact=username_or_email).first()
            username = user_obj.username if user_obj else username_or_email

            user = authenticate(request, username=username, password=password)

            if user is not None:
                if not user.is_active:
                    messages.error(request, "Your account is currently deactivated. Please contact IronPeak support.")
                else:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                    
                    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                        return redirect(next_url)
                    
                    return redirect('/dashboard/')
            else:
                messages.error(request, "Invalid username/email or password.")
    else:
        form = CustomLoginForm()

    return render(request, 'auth/login.html', {'form': form, 'next': next_url})


def logout_view(request):
    """
    Logout endpoint - terminates session safely.
    """
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out successfully.")
    return redirect('/login/')


@login_required
def role_dashboard_router(request):
    """
    Central Dashboard Dispatcher.
    Routes authenticated users to their designated role dashboard:
      - ADMIN -> /admin-dashboard/ (or executive analytics)
      - TRAINER -> /trainer-dashboard/
      - MEMBER -> /member-dashboard/
    """
    if request.user.is_superuser:
        return redirect('/admin-dashboard/')

    role = get_user_role(request.user)

    if role == 'ADMIN':
        return redirect('/admin-dashboard/')
    elif role == 'TRAINER':
        return redirect('/trainer-dashboard/')
    elif role == 'MEMBER':
        return redirect('/member-dashboard/')
    else:
        return redirect('/member-dashboard/')


@login_required
def profile_view(request):
    """Self-service user profile view"""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    # Calculate personal stats summary for profile
    user_bookings_count = Booking.objects.filter(models.Q(user=request.user) | models.Q(member_name__iexact=request.user.get_full_name())).count()
    user_workouts_count = WorkoutLog.objects.filter(models.Q(user=request.user) | models.Q(member_name__iexact=request.user.get_full_name())).count()
    latest_bmi = BMIRecord.objects.filter(models.Q(user=request.user) | models.Q(name__iexact=request.user.get_full_name())).first()

    context = {
        'profile': profile,
        'bookings_count': user_bookings_count,
        'workouts_count': user_workouts_count,
        'latest_bmi': latest_bmi,
    }
    return render(request, 'profile/profile.html', context)


@login_required
def edit_profile_view(request):
    """Edit personal information view"""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()

            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('/profile/')
    else:
        form = UserProfileForm(instance=profile, user=request.user)

    return render(request, 'profile/edit_profile.html', {'form': form, 'profile': profile})


@login_required
def change_password_view(request):
    """Change password view"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in after password change
            messages.success(request, 'Your password was successfully updated!')
            return redirect('/profile/')
        else:
            messages.error(request, 'Please correct the errors in the password form below.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'auth/change_password.html', {'form': form})
