from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from myapp.decorators import trainer_required
from myapp.models import UserProfile, GymClass, Attendance, Booking


def _trainer_team(user):
    """Return the Team instance linked to this trainer user, or None."""
    profile = getattr(user, 'profile', None)
    return profile.trainer if profile else None


def _trainer_classes(user):
    """Gym classes assigned to this trainer (FK first, name match as fallback)."""
    team = _trainer_team(user)
    if team:
        qs = GymClass.objects.filter(assigned_trainer=team)
        if qs.exists():
            return qs
        # Fall back to name matching for classes not yet linked by FK
        return GymClass.objects.filter(Q(assigned_trainer=team) | Q(trainer__iexact=team.name)).distinct()
    if user.get_full_name():
        return GymClass.objects.filter(trainer__icontains=user.get_full_name())
    return GymClass.objects.none()


@login_required
@trainer_required
def trainer_dashboard_view(request):
    """
    Trainer Dashboard View:
    Displays classes assigned to trainer, assigned members, attendance overview,
    and allows the trainer to mark today's attendance for their members.
    """
    try:
        trainer_profile = request.user.profile
    except UserProfile.DoesNotExist:
        trainer_profile = None

    # Get assigned classes (scoped to this trainer)
    assigned_classes = _trainer_classes(request.user)

    # Get assigned members
    if trainer_profile and trainer_profile.trainer:
        assigned_members = UserProfile.objects.filter(
            trainer=trainer_profile.trainer
        ).select_related('user')
    else:
        assigned_members = UserProfile.objects.none()

    today = timezone.now().date()

    # Build today's attendance map {user_id: attendance_object}
    member_user_ids = [m.user_id for m in assigned_members]
    todays_records = Attendance.objects.filter(
        user_id__in=member_user_ids, date=today
    )
    today_attendance_map = {rec.user_id: rec for rec in todays_records}

    # Annotate each member with today's attendance status
    members_with_status = []
    for profile in assigned_members:
        att = today_attendance_map.get(profile.user_id)
        members_with_status.append({
            'profile': profile,
            'attendance': att,
            'is_present': att is not None,
        })

    total_class_bookings = Booking.objects.count()
    present_today = len(today_attendance_map)

    context = {
        'assigned_classes': assigned_classes,
        'assigned_classes_count': assigned_classes.count(),
        'assigned_members': assigned_members,
        'assigned_members_count': assigned_members.count(),
        'total_class_bookings': total_class_bookings,
        'members_with_status': members_with_status,
        'today': today,
        'present_today': present_today,
    }
    return render(request, 'trainer/dashboard.html', context)


@login_required
@trainer_required
def trainer_class_attendance_view(request, class_id):
    """
    Per-class roster + attendance for a trainer's assigned class.
    Shows the members enrolled (confirmed bookings) and lets the trainer mark
    present / absent for today. Access is limited to the trainer the class is
    assigned to (or an admin superuser).
    """
    gym_class = get_object_or_404(GymClass, pk=class_id)

    # Access control: only the assigned trainer (or superuser) may view this.
    if not request.user.is_superuser:
        team = _trainer_team(request.user)
        owns = (gym_class.assigned_trainer_id == team.pk) if team else False
        if not owns and request.user.get_full_name():
            owns = gym_class.trainer.lower() == request.user.get_full_name().lower()
        if not owns:
            return render(request, '403.html',
                          {'message': 'This class is not assigned to you.'}, status=403)

    today = timezone.now().date()
    bookings = gym_class.bookings.filter(status='Confirmed').order_by('member_name')

    # Today's attendance for this class, keyed by user_id and by member_name.
    todays = Attendance.objects.filter(gym_class=gym_class, date=today)
    att_by_user = {a.user_id: a for a in todays if a.user_id}
    att_by_name = {a.member_name.lower(): a for a in todays}

    roster = []
    present_count = 0
    for b in bookings:
        record = None
        if b.user_id:
            record = att_by_user.get(b.user_id)
        if record is None:
            record = att_by_name.get(b.member_name.lower())
        is_present = record is not None
        if is_present:
            present_count += 1
        roster.append({
            'booking': b,
            'user_id': b.user_id,
            'member_name': b.member_name,
            'attendance': record,
            'is_present': is_present,
        })

    context = {
        'gym_class': gym_class,
        'roster': roster,
        'roster_count': len(roster),
        'present_count': present_count,
        'absent_count': len(roster) - present_count,
        'today': today,
    }
    return render(request, 'trainer/class_attendance.html', context)


@login_required
@trainer_required
def trainer_mark_attendance_view(request):
    """
    Trainer marks attendance (present/absent) for a member for today.
    POST-only. Works at member level (dashboard) or class level (roster page).
    Expects: action (mark_present | mark_absent), and either member_user_id
    or member_name; optional gym_class_id + next redirect.
    """
    if request.method != 'POST':
        return redirect('trainer-dashboard')

    member_user_id = request.POST.get('member_user_id')
    member_name = request.POST.get('member_name', '').strip()
    gym_class_id = request.POST.get('gym_class_id')
    action = request.POST.get('action', 'mark_present')
    today = timezone.now().date()

    # Resolve optional class (and enforce ownership when present)
    gym_class = None
    redirect_url = 'trainer-dashboard'
    if gym_class_id:
        gym_class = GymClass.objects.filter(pk=gym_class_id).first()
        if gym_class is None:
            messages.error(request, 'Class not found.')
            return redirect('trainer-dashboard')
        if not request.user.is_superuser:
            team = _trainer_team(request.user)
            owns = (gym_class.assigned_trainer_id == team.pk) if team else False
            if not owns and request.user.get_full_name():
                owns = gym_class.trainer.lower() == request.user.get_full_name().lower()
            if not owns:
                return render(request, '403.html',
                              {'message': 'This class is not assigned to you.'}, status=403)
        redirect_url = f'/trainer/class/{gym_class.pk}/attendance/'

    # Resolve the member user (optional) and display name
    member_user = None
    display_name = member_name
    if member_user_id:
        member_user = User.objects.filter(id=member_user_id).first()
        if member_user:
            display_name = member_user.get_full_name() or member_user.username
    if not display_name and member_user:
        display_name = member_user.get_full_name() or member_user.username
    if not display_name:
        messages.error(request, 'Member not found.')
        return redirect(redirect_url if redirect_url.startswith('/') else 'trainer-dashboard')

    base_kwargs = {'date': today}
    if member_user:
        base_kwargs['user'] = member_user
    else:
        base_kwargs['user'] = None
        base_kwargs['member_name'] = display_name
    if gym_class:
        base_kwargs['gym_class'] = gym_class
    else:
        base_kwargs['gym_class'] = None

    if action == 'mark_present':
        record, created = Attendance.objects.get_or_create(
            **base_kwargs,
            defaults={
                'member_name': display_name,
                'check_in_time': timezone.now().time(),
            }
        )
        if created:
            messages.success(request, f"\u2705 {display_name} marked PRESENT for today.")
        else:
            messages.info(request, f"{display_name} was already marked present.")

    elif action == 'mark_absent':
        deleted, _ = Attendance.objects.filter(**base_kwargs).delete()
        if deleted:
            messages.success(request, f"\u274c {display_name} marked ABSENT for today.")
        else:
            messages.info(request, f"{display_name} had no attendance record for today.")

    return redirect(redirect_url if redirect_url.startswith('/') else 'trainer-dashboard')
