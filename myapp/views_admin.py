from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum, Count
from django.core.paginator import Paginator
from .models import UserProfile, Team, Membership, GymClass, Booking, Attendance, Payment, BMIRecord
from .decorators import admin_required
from .forms import UserManagementForm, RoleChangeForm, GymClassForm
from myapp.views_dashboard import dashboard as executive_analytics_view
from myapp.ai_engine import automations


@admin_required
def admin_dashboard_view(request):
    """
    ADMIN DASHBOARD VIEW
    Displays full gym management KPIs, member & trainer counts, financial analytics,
    churn prediction summary, and quick management links.
    """
    total_users = User.objects.count()
    admin_count = UserProfile.objects.filter(role='ADMIN').count()
    trainer_count = UserProfile.objects.filter(role='TRAINER').count()
    member_count = UserProfile.objects.filter(role='MEMBER').count()
    active_users_count = User.objects.filter(is_active=True).count()

    total_revenue = Payment.objects.filter(status='Completed').aggregate(total=Sum('amount'))['total'] or 0
    pending_revenue = Payment.objects.filter(status='Pending').aggregate(total=Sum('amount'))['total'] or 0
    total_bookings = Booking.objects.count()
    today_attendance = Attendance.objects.count()

    recent_users = User.objects.select_related('profile').order_by('-date_joined')[:5]
    recent_payments = Payment.objects.select_related('membership').order_by('-payment_date')[:5]
    recent_bookings = Booking.objects.select_related('gym_class').order_by('-booking_date')[:5]

    # AI Executive Daily Briefing (Gemini-powered, cached, with local fallback)
    ai_briefing = automations.generate_executive_briefing()

    context = {
        'total_users': total_users,
        'admin_count': admin_count,
        'trainer_count': trainer_count,
        'member_count': member_count,
        'active_users_count': active_users_count,
        'total_revenue': total_revenue,
        'pending_revenue': pending_revenue,
        'total_bookings': total_bookings,
        'today_attendance': today_attendance,
        'recent_users': recent_users,
        'recent_payments': recent_payments,
        'recent_bookings': recent_bookings,
        'ai_briefing': ai_briefing,
    }
    return render(request, 'admin/dashboard.html', context)


@admin_required
def admin_automations_view(request):
    """
    ADMIN AI AUTOMATIONS CENTER
    - AI Executive Daily Briefing (Gemini + local fallback)
    - AI Retention Action Drafts for high-risk churn members
    A ?regen=1 query param forces regeneration (bypasses the cache).
    """
    force = request.GET.get('regen') == '1'
    briefing = automations.generate_executive_briefing(force=force)
    retention = automations.generate_retention_drafts(force=force)
    context = {
        'briefing': briefing,
        'retention': retention,
        'metrics': briefing.get('metrics', {}),
    }
    return render(request, 'admin/automations.html', context)


@admin_required
def admin_user_list_view(request):
    """
    Admin User Management list view with search, role filter, status filter, and pagination.
    """
    search_query = request.GET.get('q', '').strip()
    role_filter = request.GET.get('role', '').strip()
    status_filter = request.GET.get('status', '').strip()

    users = User.objects.select_related('profile').all().order_by('-date_joined')

    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(profile__phone__icontains=search_query)
        )

    if role_filter:
        users = users.filter(profile__role=role_filter)

    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)

    paginator = Paginator(users, 10) # 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'roles': UserProfile.ROLE_CHOICES,
    }
    return render(request, 'admin/users.html', context)


@admin_required
def admin_user_detail_view(request, user_id):
    """View detailed user information"""
    target_user = get_object_or_404(User.objects.select_related('profile'), id=user_id)
    target_profile, _ = UserProfile.objects.get_or_create(user=target_user)

    user_bookings = Booking.objects.filter(Q(user=target_user) | Q(member_name__iexact=target_user.get_full_name()))[:10]
    user_payments = Payment.objects.filter(Q(user=target_user) | Q(member_name__iexact=target_user.get_full_name()))[:10]
    user_bmi = BMIRecord.objects.filter(Q(user=target_user) | Q(name__iexact=target_user.get_full_name())).first()

    context = {
        'target_user': target_user,
        'target_profile': target_profile,
        'user_bookings': user_bookings,
        'user_payments': user_payments,
        'user_bmi': user_bmi,
    }
    return render(request, 'admin/user_detail.html', context)


@admin_required
def admin_user_edit_view(request, user_id):
    """Edit user information by Admin"""
    target_user = get_object_or_404(User, id=user_id)
    target_profile, _ = UserProfile.objects.get_or_create(user=target_user)

    if request.method == 'POST':
        form = UserManagementForm(request.POST)
        if form.is_valid():
            new_role = form.cleaned_data['role']
            new_status = form.cleaned_data['is_active']

            # Safeguard: Check last active admin
            active_admin_count = User.objects.filter(is_active=True, profile__role='ADMIN').count()
            if target_profile.role == 'ADMIN' and (new_role != 'ADMIN' or not new_status):
                if active_admin_count <= 1:
                    messages.error(request, "Operation blocked: System must maintain at least one active Admin user.")
                    return redirect('/admin/users/')

            with transaction.atomic():
                target_user.first_name = form.cleaned_data['first_name']
                target_user.last_name = form.cleaned_data['last_name']
                target_user.email = form.cleaned_data['email']
                target_user.is_active = new_status
                target_user.save()

                target_profile.phone = form.cleaned_data['phone']
                target_profile.role = new_role
                target_profile.save()

            messages.success(request, f"User '{target_user.username}' updated successfully.")
            return redirect('/admin/users/')
    else:
        initial_data = {
            'first_name': target_user.first_name,
            'last_name': target_user.last_name,
            'email': target_user.email,
            'phone': target_profile.phone,
            'role': target_profile.role,
            'is_active': target_user.is_active,
        }
        form = UserManagementForm(initial=initial_data)

    context = {
        'target_user': target_user,
        'form': form,
    }
    return render(request, 'admin/edit_user.html', context)


@admin_required
def admin_user_role_view(request, user_id):
    """Change user role with last-admin safeguard"""
    if request.method == 'POST':
        target_user = get_object_or_404(User, id=user_id)
        target_profile, _ = UserProfile.objects.get_or_create(user=target_user)
        new_role = request.POST.get('role')

        if new_role not in dict(UserProfile.ROLE_CHOICES):
            messages.error(request, "Invalid role specified.")
            return redirect('/admin/users/')

        # Safeguard against zero active admins
        if target_profile.role == 'ADMIN' and new_role != 'ADMIN':
            active_admin_count = User.objects.filter(is_active=True, profile__role='ADMIN').count()
            if active_admin_count <= 1:
                messages.error(request, "Action blocked: Cannot change role of the last active Admin account.")
                return redirect('/admin/users/')

        target_profile.role = new_role
        target_profile.save()
        messages.success(request, f"Role for '{target_user.username}' changed to {new_role}.")

    return redirect('/admin/users/')


@admin_required
def admin_user_status_view(request, user_id):
    """Toggle user active/inactive status with last-admin safeguard"""
    if request.method == 'POST':
        target_user = get_object_or_404(User, id=user_id)
        target_profile, _ = UserProfile.objects.get_or_create(user=target_user)

        # Safeguard: Do not allow admin to deactivate self or last admin
        if target_user == request.user:
            messages.error(request, "You cannot deactivate your own currently authenticated account.")
            return redirect('/admin/users/')

        if target_user.is_active and target_profile.role == 'ADMIN':
            active_admin_count = User.objects.filter(is_active=True, profile__role='ADMIN').count()
            if active_admin_count <= 1:
                messages.error(request, "Action blocked: Cannot deactivate the last active Admin account.")
                return redirect('/admin/users/')

        target_user.is_active = not target_user.is_active
        target_user.save()

        status_label = "activated" if target_user.is_active else "deactivated"
        messages.success(request, f"User '{target_user.username}' has been {status_label}.")

    return redirect('/admin/users/')


@admin_required
def admin_add_member_view(request):
    """
    Admin: Create a new member (or trainer) account directly from the management panel.
    POST: Validates and creates a Django User + UserProfile atomically.
    """
    from django.contrib.auth.models import User
    from django.contrib.auth.password_validation import validate_password
    from django.core.exceptions import ValidationError

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        role = request.POST.get('role', 'MEMBER').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        errors = []

        if not username:
            errors.append('Username is required.')
        elif User.objects.filter(username__iexact=username).exists():
            errors.append(f"Username '{username}' is already taken.")

        if email and User.objects.filter(email__iexact=email).exists():
            errors.append(f"Email '{email}' is already registered.")

        if not password:
            errors.append('Password is required.')
        elif password != confirm_password:
            errors.append('Passwords do not match.')
        else:
            try:
                validate_password(password)
            except ValidationError as e:
                errors.extend(e.messages)

        if role not in dict(UserProfile.ROLE_CHOICES):
            errors.append('Invalid role selected.')

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, 'admin/add_member.html', {
                'post_data': request.POST,
                'roles': UserProfile.ROLE_CHOICES,
            })

        with transaction.atomic():
            new_user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            profile, _ = UserProfile.objects.get_or_create(user=new_user)
            profile.role = role
            profile.phone = phone
            profile.save()

        messages.success(request, f"✅ Account '{username}' created successfully as {role}.")
        return redirect('/admin/users/')

    return render(request, 'admin/add_member.html', {
        'roles': UserProfile.ROLE_CHOICES,
    })


@admin_required
def admin_class_list_view(request):
    """
    ADMIN CLASS MANAGEMENT
    Lists every gym class with its assigned trainer and live enrollment count,
    and exposes add / edit / delete actions.
    """
    search_query = request.GET.get('q', '').strip()
    classes = GymClass.objects.select_related('assigned_trainer').order_by(
        'schedule_day', 'schedule_time')
    if search_query:
        classes = classes.filter(
            Q(name__icontains=search_query) |
            Q(trainer__icontains=search_query) |
            Q(schedule_day__icontains=search_query)
        )

    # Annotate live confirmed enrollment count per class
    roster_counts = {
        c.pk: Booking.objects.filter(gym_class=c, status='Confirmed').count()
        for c in classes
    }
    class_rows = [{'cls': c, 'enrolled': roster_counts.get(c.pk, 0)} for c in classes]

    context = {
        'class_rows': class_rows,
        'total_classes': classes.count(),
        'search_query': search_query,
    }
    return render(request, 'admin/classes.html', context)


@admin_required
def admin_class_form_view(request, class_id=None):
    """Create a new class or edit an existing one, including trainer assignment."""
    target = get_object_or_404(GymClass, pk=class_id) if class_id else None

    if request.method == 'POST':
        form = GymClassForm(request.POST, instance=target)
        if form.is_valid():
            obj = form.save()
            messages.success(
                request,
                f"Class '{obj.name}' {'updated' if class_id else 'created'} successfully."
            )
            return redirect('/admin/classes/')
    else:
        form = GymClassForm(instance=target)

    context = {
        'form': form,
        'editing': bool(class_id),
        'target': target,
    }
    return render(request, 'admin/class_form.html', context)


@admin_required
def admin_class_delete_view(request, class_id):
    """Delete a gym class (POST only)."""
    if request.method != 'POST':
        return redirect('/admin/classes/')
    target = get_object_or_404(GymClass, pk=class_id)
    name = target.name
    target.delete()
    messages.success(request, f"Class '{name}' was deleted.")
    return redirect('/admin/classes/')

