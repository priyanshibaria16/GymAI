"""
Views for Member Progress Tracker module (Module 5).
Tracks workout logs, body metrics, and visualizes progress with charts.
Includes object-level authorization & role isolation.
"""
import json
from collections import defaultdict
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from myapp.models import WorkoutLog, BodyMetrics, UserProfile
from myapp.forms import WorkoutLogForm, BodyMetricsForm
from myapp.decorators import get_user_role


@login_required
def member_progress(request):
    """Display member progress with workout logs, body metrics, and charts"""
    role = get_user_role(request.user)
    user_name = request.user.get_full_name() or request.user.username
    is_admin = (role == 'ADMIN') or request.user.is_superuser

    # Object-Level Authorization Filter (strict role isolation)
    if role == 'MEMBER':
        # Members can ONLY see their own records (IDOR Protection)
        member_name = user_name
        own_q = Q(user=request.user) | Q(member_name__iexact=user_name) | Q(member_name__iexact=request.user.username)
        workout_logs = WorkoutLog.objects.filter(own_q).order_by('-date')[:20]
        body_metrics = BodyMetrics.objects.filter(own_q).order_by('-date')[:10]
        metrics_base = BodyMetrics.objects.filter(own_q)
        unique_members = [member_name]
    elif role == 'TRAINER' and not is_admin:
        # Trainers can ONLY see the progress of members assigned to them.
        try:
            trainer_team = request.user.profile.trainer
        except UserProfile.DoesNotExist:
            trainer_team = None
        if trainer_team:
            assigned = UserProfile.objects.filter(trainer=trainer_team).select_related('user')
            assigned_ids = [p.user_id for p in assigned]
            assigned_names = [p.user.get_full_name() or p.user.username for p in assigned]
        else:
            assigned_ids, assigned_names = [], []
        scope_q = Q(user_id__in=assigned_ids)
        if assigned_names:
            scope_q |= Q(member_name__in=assigned_names)
        member_name = request.GET.get('member', '').strip()
        w_base = WorkoutLog.objects.filter(scope_q)
        b_base = BodyMetrics.objects.filter(scope_q)
        if member_name:
            w_base = w_base.filter(member_name__icontains=member_name)
            b_base = b_base.filter(member_name__icontains=member_name)
        workout_logs = w_base.order_by('-date')[:20]
        body_metrics = b_base.order_by('-date')[:10]
        metrics_base = b_base
        unique_members = sorted(set(assigned_names))
    else:
        # Admin can filter by member_name or view all
        member_name = request.GET.get('member', '').strip()
        if member_name:
            workout_logs = WorkoutLog.objects.filter(member_name__icontains=member_name).order_by('-date')[:20]
            body_metrics = BodyMetrics.objects.filter(member_name__icontains=member_name).order_by('-date')[:10]
            metrics_base = BodyMetrics.objects.filter(member_name__icontains=member_name)
        else:
            workout_logs = WorkoutLog.objects.all().order_by('-date')[:20]
            body_metrics = BodyMetrics.objects.all().order_by('-date')[:10]
            metrics_base = BodyMetrics.objects.all()
        all_members = list(
            WorkoutLog.objects.values_list('member_name', flat=True).distinct()
        ) + list(
            BodyMetrics.objects.values_list('member_name', flat=True).distinct()
        )
        unique_members = sorted(set(all_members))

    # Weight trend chart
    weight_labels = []
    weight_data = []
    metrics_ordered = metrics_base.order_by('date')[:10]
    for m in metrics_ordered:
        weight_labels.append(m.date.strftime('%d %b %Y'))
        weight_data.append(m.body_weight)

    # Radar chart data
    radar_labels = json.dumps(['Chest', 'Waist', 'Biceps', 'Thighs', 'Weight(÷2)'])
    if body_metrics.exists():
        latest = body_metrics.first()
        radar_data = json.dumps([
            latest.chest or 0,
            latest.waist or 0,
            latest.biceps or 0,
            latest.thighs or 0,
            (latest.body_weight or 0) / 2
        ])
    else:
        radar_data = json.dumps([0, 0, 0, 0, 0])

    # Workout volume chart
    exercise_volume = defaultdict(float)
    for log in workout_logs:
        volume = log.sets * log.reps * log.weight_used
        exercise_volume[log.exercise] += volume

    exercise_labels = json.dumps(list(exercise_volume.keys()))
    exercise_data = json.dumps([round(v, 1) for v in exercise_volume.values()])

    # Pre-fill forms for authenticated members
    initial_workout = {'member_name': user_name} if role == 'MEMBER' else {}
    initial_metrics = {'member_name': user_name} if role == 'MEMBER' else {}

    workout_form = WorkoutLogForm(initial=initial_workout)
    metrics_form = BodyMetricsForm(initial=initial_metrics)

    context = {
        'workout_logs': workout_logs,
        'body_metrics': body_metrics,
        'unique_members': unique_members,
        'selected_member': member_name,
        'weight_labels': json.dumps(weight_labels),
        'weight_data': json.dumps(weight_data),
        'radar_labels': radar_labels,
        'radar_data': radar_data,
        'exercise_labels': exercise_labels,
        'exercise_data': exercise_data,
        'workout_form': workout_form,
        'metrics_form': metrics_form,
        'user_role': role,
    }

    return render(request, 'member-progress.html', context)


@login_required
def add_workout(request):
    """Handle workout log form submission with user association"""
    if request.method == 'POST':
        form = WorkoutLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            if request.user.is_authenticated:
                log.user = request.user
                if get_user_role(request.user) == 'MEMBER':
                    log.member_name = request.user.get_full_name() or request.user.username
            log.save()
    return redirect('member-progress')


@login_required
def add_metrics(request):
    """Handle body metrics form submission with user association"""
    if request.method == 'POST':
        form = BodyMetricsForm(request.POST)
        if form.is_valid():
            metrics = form.save(commit=False)
            if request.user.is_authenticated:
                metrics.user = request.user
                if get_user_role(request.user) == 'MEMBER':
                    metrics.member_name = request.user.get_full_name() or request.user.username
            metrics.save()
    return redirect('member-progress')
