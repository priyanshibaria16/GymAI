"""
Views for the Member Analytics Dashboard (Module 1).
Aggregates data from all models and renders interactive Chart.js visualizations.
"""
from django.shortcuts import render
from django.db.models import Sum, Count, Avg
from myapp.models import (
    BMIRecord, GymClass, Booking, Attendance,
    Payment, Membership, WorkoutLog, BodyMetrics,
    Subscriber, Review
)
from myapp.utils.chart_helpers import (
    get_monthly_signups, get_membership_distribution,
    get_revenue_trend, get_attendance_by_day,
    get_class_popularity, get_payment_method_distribution,
    get_bmi_category_distribution
)
from myapp.views_ai import get_churn_prediction_data
from myapp.decorators import admin_required


@admin_required
def dashboard(request):
    """Main analytics dashboard view with stats cards and charts (ADMIN ONLY)"""

    
    # Stats cards data
    total_members = BMIRecord.objects.values('name').distinct().count()
    total_revenue = Payment.objects.filter(status='Completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    active_classes = GymClass.objects.count()
    avg_bmi = BMIRecord.objects.aggregate(avg=Avg('bmi_value'))['avg'] or 0
    total_bookings = Booking.objects.filter(status='Confirmed').count()
    total_attendance = Attendance.objects.count()
    total_subscribers = Subscriber.objects.filter(is_active=True).count()
    avg_rating = Review.objects.filter(is_approved=True).aggregate(
        avg=Avg('rating')
    )['avg'] or 0

    # Chart data
    signup_labels, signup_data = get_monthly_signups(BMIRecord)
    membership_labels, membership_data, membership_colors = get_membership_distribution(Membership, Payment)
    revenue_labels, revenue_data = get_revenue_trend(Payment)
    attendance_labels, attendance_data = get_attendance_by_day(Attendance)
    class_labels, class_data = get_class_popularity(GymClass)
    payment_labels, payment_data, payment_colors = get_payment_method_distribution(Payment)
    bmi_labels, bmi_data, bmi_colors = get_bmi_category_distribution(BMIRecord)

    # ML Churn Analytics
    churn_data = get_churn_prediction_data()

    context = {
        # Stats
        'total_members': total_members,
        'total_revenue': total_revenue,
        'active_classes': active_classes,
        'avg_bmi': round(avg_bmi, 1),
        'total_bookings': total_bookings,
        'total_attendance': total_attendance,
        'total_subscribers': total_subscribers,
        'avg_rating': round(avg_rating, 1),
        # Charts
        'signup_labels': signup_labels,
        'signup_data': signup_data,
        'membership_labels': membership_labels,
        'membership_data': membership_data,
        'membership_colors': membership_colors,
        'revenue_labels': revenue_labels,
        'revenue_data': revenue_data,
        'attendance_labels': attendance_labels,
        'attendance_data': attendance_data,
        'class_labels': class_labels,
        'class_data': class_data,
        'payment_labels': payment_labels,
        'payment_data': payment_data,
        'payment_colors': payment_colors,
        'bmi_labels': bmi_labels,
        'bmi_data': bmi_data,
        'bmi_colors': bmi_colors,
        # Churn Analytics
        'churn_data': churn_data,
    }
    
    return render(request, 'dashboard.html', context)
