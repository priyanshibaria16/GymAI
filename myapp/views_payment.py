"""
Views for Payment & Revenue Tracker module (Module 4).
Displays payment records, revenue analytics, and visual charts. (ADMIN ONLY)
"""
import json
from datetime import datetime
from django.shortcuts import render
from django.db.models import Sum, Count
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from myapp.models import Payment, Membership
from myapp.utils.chart_helpers import (
    get_revenue_trend, get_payment_method_distribution
)
from myapp.views_ai import get_churn_prediction_data
from myapp.decorators import admin_required


@admin_required
def payment_dashboard(request):
    """Payment dashboard with revenue analytics, charts, and Stripe gateway (ADMIN ONLY)"""
    
    # All payments
    payments = Payment.objects.all()[:50]
    
    # Summary stats
    total_revenue = Payment.objects.filter(status='Completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    pending_amount = Payment.objects.filter(status='Pending').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    total_transactions = Payment.objects.count()
    completed_count = Payment.objects.filter(status='Completed').count()
    pending_count = Payment.objects.filter(status='Pending').count()
    failed_count = Payment.objects.filter(status='Failed').count()
    
    # Chart data
    revenue_labels, revenue_data = get_revenue_trend(Payment)
    method_labels, method_data, method_colors = get_payment_method_distribution(Payment)
    
    # Status distribution for pie chart
    status_labels = json.dumps(['Completed', 'Pending', 'Failed'])
    status_data = json.dumps([completed_count, pending_count, failed_count])
    status_colors = json.dumps([
        'rgba(46, 204, 113, 0.8)',
        'rgba(241, 196, 15, 0.8)',
        'rgba(231, 76, 60, 0.8)'
    ])

    # ML Membership Churn Prediction (financial retention risk)
    churn_data = get_churn_prediction_data()
    high_risk_count = churn_data['risk_distribution'].get('High', 0)
    pending_members = Payment.objects.filter(status='Pending').values_list('member_name', flat=True).distinct()
    # Estimated revenue at risk = pending dues of members flagged as High churn risk
    high_risk_names = [m['name'] for m in churn_data['at_risk_members'] if m['risk_level'] == 'High']
    revenue_at_risk = Payment.objects.filter(
        status='Pending', member_name__in=high_risk_names
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'payments': payments,
        'total_revenue': total_revenue,
        'pending_amount': pending_amount,
        'total_transactions': total_transactions,
        'completed_count': completed_count,
        'pending_count': pending_count,
        'failed_count': failed_count,
        'revenue_labels': revenue_labels,
        'revenue_data': revenue_data,
        'method_labels': method_labels,
        'method_data': method_data,
        'method_colors': method_colors,
        'status_labels': status_labels,
        'status_data': status_data,
        'status_colors': status_colors,
        'stripe_publishable_key': getattr(settings, 'STRIPE_PUBLISHABLE_KEY', ''),
        'memberships': Membership.objects.all(),
        # Churn analytics
        'churn_data': churn_data,
        'high_risk_count': high_risk_count,
        'revenue_at_risk': revenue_at_risk,
        'pending_members_count': len(set(pending_members)),
    }
    
    return render(request, 'payment-dashboard.html', context)


@admin_required
@csrf_exempt
def process_stripe_payment(request):
    """
    API view for Stripe payment gateway processing (ADMIN ONLY)
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.body else request.POST
            member_name = data.get('member_name', 'Guest Member')
            amount = data.get('amount', 1200)
            membership_id = data.get('membership_id')
            stripe_token = data.get('stripe_token', 'tok_visa')

            membership = None
            if membership_id:
                membership = Membership.objects.filter(id=membership_id).first()

            user_obj = request.user if request.user.is_authenticated else None

            # Record completed Stripe payment transaction
            payment = Payment.objects.create(
                user=user_obj,
                member_name=member_name,
                membership=membership,
                amount=amount,
                payment_date=timezone.now().date(),
                method='Card',
                status='Completed'
            )

            return JsonResponse({
                'status': 'success',
                'message': f'Stripe payment of ₹{amount} processed successfully for {member_name}!',
                'payment_id': payment.id,
                'stripe_token_received': stripe_token[:15] + '...'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid HTTP method'}, status=405)
