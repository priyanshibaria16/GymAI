"""
Chart helper functions for generating data for Chart.js visualizations.
Used by the Analytics Dashboard and other chart-based views.
"""
import json
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from django.db.models import Sum, Count, Avg
from django.utils import timezone


def get_monthly_signups(BMIRecord):
    """Returns monthly BMI record counts for the last 12 months"""
    labels = []
    data = []
    now = timezone.now()
    
    for i in range(11, -1, -1):
        month_date = now - timedelta(days=i * 30)
        month_name = month_date.strftime('%b %Y')
        count = BMIRecord.objects.filter(
            created_at__year=month_date.year,
            created_at__month=month_date.month
        ).count()
        labels.append(month_name)
        data.append(count)
    
    return json.dumps(labels), json.dumps(data)


def get_membership_distribution(Membership, Payment):
    """Returns membership plan distribution based on payments"""
    labels = []
    data = []
    colors = [
        'rgba(255, 99, 132, 0.8)',
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 206, 86, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(153, 102, 255, 0.8)',
        'rgba(255, 159, 64, 0.8)',
    ]
    
    memberships = Membership.objects.all()
    for i, m in enumerate(memberships):
        count = Payment.objects.filter(membership=m).count()
        if count > 0:
            labels.append(m.name)
            data.append(count)
    
    # If no payment data, show membership plans with equal weight
    if not data:
        for m in memberships:
            labels.append(m.name)
            data.append(1)
    
    return json.dumps(labels), json.dumps(data), json.dumps(colors[:len(labels)])


def get_revenue_trend(Payment):
    """Returns monthly revenue for the last 12 months"""
    labels = []
    data = []
    now = timezone.now()
    
    for i in range(11, -1, -1):
        month_date = now - timedelta(days=i * 30)
        month_name = month_date.strftime('%b %Y')
        total = Payment.objects.filter(
            payment_date__year=month_date.year,
            payment_date__month=month_date.month,
            status='Completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        labels.append(month_name)
        data.append(float(total))
    
    return json.dumps(labels), json.dumps(data)


def get_attendance_by_day(Attendance):
    """Returns attendance count grouped by day of week"""
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    data = []
    
    for i, day in enumerate(days):
        # iso_week_day: Monday=1, Sunday=7
        count = Attendance.objects.filter(date__week_day=i + 2 if i < 6 else 1).count()
        data.append(count)
    
    return json.dumps(days), json.dumps(data)


def get_class_popularity(GymClass):
    """Returns class popularity based on enrollment"""
    labels = []
    data = []
    
    classes = GymClass.objects.all()
    for gc in classes:
        labels.append(gc.name)
        data.append(gc.current_enrolled)
    
    return json.dumps(labels), json.dumps(data)


def get_payment_method_distribution(Payment):
    """Returns payment method distribution"""
    labels = []
    data = []
    colors = [
        'rgba(46, 204, 113, 0.8)',   # Cash - Green
        'rgba(52, 152, 219, 0.8)',   # UPI - Blue
        'rgba(155, 89, 182, 0.8)',   # Card - Purple
        'rgba(241, 196, 15, 0.8)',   # Net Banking - Yellow
    ]
    
    methods = Payment.objects.values('method').annotate(count=Count('method')).order_by('-count')
    for m in methods:
        labels.append(m['method'])
        data.append(m['count'])
    
    return json.dumps(labels), json.dumps(data), json.dumps(colors[:len(labels)])


def get_bmi_category_distribution(BMIRecord):
    """Returns BMI category distribution"""
    labels = ['Underweight', 'Healthy', 'Overweight', 'Obese']
    colors = [
        'rgba(52, 152, 219, 0.8)',   # Blue
        'rgba(46, 204, 113, 0.8)',   # Green
        'rgba(241, 196, 15, 0.8)',   # Yellow
        'rgba(231, 76, 60, 0.8)',    # Red
    ]
    data = []
    
    for category in labels:
        count = BMIRecord.objects.filter(category=category).count()
        data.append(count)
    
    return json.dumps(labels), json.dumps(data), json.dumps(colors)


def get_rating_distribution(Review):
    """Returns review rating distribution (1-5 stars)"""
    labels = ['1 Star', '2 Stars', '3 Stars', '4 Stars', '5 Stars']
    data = []
    
    for rating in range(1, 6):
        count = Review.objects.filter(rating=rating, is_approved=True).count()
        data.append(count)
    
    return json.dumps(labels), json.dumps(data)
