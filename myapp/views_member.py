from django.shortcuts import render, redirect
from django.db.models import Q
from .models import UserProfile, Booking, Attendance, BMIRecord, WorkoutLog, BodyMetrics, GymClass
from .decorators import role_required
from .ai_engine.fitness_recommender import generate_ai_recommendation


@role_required('MEMBER', 'ADMIN')
def member_dashboard_view(request):
    """
    MEMBER DASHBOARD VIEW
    Personal self-service dashboard displaying member's bookings, attendance,
    BMI summary, fitness recommendations, workout history, and shortcuts.
    Object-level isolation ensures members only view their own data.
    """
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    full_name = request.user.get_full_name() or request.user.username

    # Object-level filtering: user = request.user or member_name matching
    user_query = Q(user=request.user) | Q(member_name__iexact=full_name) | Q(member_name__iexact=request.user.username)
    name_query = Q(user=request.user) | Q(name__iexact=full_name) | Q(name__iexact=request.user.username)

    my_bookings = Booking.objects.filter(user_query).select_related('gym_class').order_by('-booking_date')[:5]
    my_attendance = Attendance.objects.filter(user_query).order_by('-date', '-check_in_time')[:5]
    my_latest_bmi = BMIRecord.objects.filter(name_query).order_by('-created_at').first()
    my_workouts = WorkoutLog.objects.filter(user_query).order_by('-date')[:5]
    my_metrics = BodyMetrics.objects.filter(user_query).order_by('-date').first()

    # Generate personalized fitness recommendation if BMI record exists
    recommendation = None
    if my_latest_bmi:
        recommendation = generate_ai_recommendation(
            height_cm=my_latest_bmi.height,
            weight_kg=my_latest_bmi.weight,
            age=my_latest_bmi.age,
            gender=my_latest_bmi.gender,
            activity_level='moderate',
            fitness_goal='weight_loss'
        )

    # Upcoming available classes for shortcut
    available_classes = GymClass.objects.all()[:4]

    context = {
        'profile': profile,
        'trainer': profile.trainer,
        'full_name': full_name,
        'my_bookings': my_bookings,
        'recent_bookings': my_bookings,
        'active_bookings_count': my_bookings.count(),
        'my_attendance': my_attendance,
        'my_latest_bmi': my_latest_bmi,
        'latest_bmi': my_latest_bmi,
        'my_workouts': my_workouts,
        'recent_workouts': my_workouts,
        'workout_count': my_workouts.count(),
        'my_metrics': my_metrics,
        'recommendation': recommendation,
        'available_classes': available_classes,
    }
    return render(request, 'member/dashboard.html', context)
