"""
Views for AI/ML Modules:
- Module 18: AI-Based BMI & Fitness Recommender
- Module 22: Chatbot with NLP & Grok AI
- Module 19: ML-Based Membership Churn Prediction
"""

import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from myapp.models import BMIRecord, Payment, Attendance, GymClass
from myapp.ai_engine.fitness_recommender import generate_ai_recommendation
from myapp.ai_engine.nlp_chatbot import get_bot_response
from myapp.ai_engine.churn_predictor import train_and_predict_churn
from myapp.decorators import get_user_role


def _bmi_history(request, full_name):
    """Role-scoped BMI history: members see only their own, admins see all,
    trainers and anonymous visitors see none (no cross-member data leak)."""
    if not request.user.is_authenticated:
        return BMIRecord.objects.none()
    role = get_user_role(request.user)
    if role == 'MEMBER':
        return BMIRecord.objects.filter(
            Q(user=request.user) | Q(name__iexact=full_name)
            | Q(name__iexact=request.user.username)
        )[:10]
    if role == 'ADMIN' or request.user.is_superuser:
        return BMIRecord.objects.all()[:10]
    return BMIRecord.objects.none()


def ai_bmi_calculator(request):
    """
    Module 18: AI-Based BMI & Fitness Recommendation View
    Calculates BMI + BMR/TDEE + Macro ratios + Workout split + AI insight
    """
    result = None
    default_name = ''
    if request.user.is_authenticated:
        default_name = request.user.get_full_name() or request.user.username

    form_data = {
        'name': default_name,
        'height': '',
        'weight': '',
        'age': '25',
        'gender': 'Male',
        'activity_level': 'moderate',
        'fitness_goal': 'weight_loss'
    }

    # Role-scoped BMI history (members: own only, admin: all, others: none)
    history = _bmi_history(request, default_name)

    if request.method == 'POST':
        name = request.POST.get('name', default_name or 'Member').strip()
        height = float(request.POST.get('height', 170))
        weight = float(request.POST.get('weight', 70))
        age = int(request.POST.get('age', 25))
        gender = request.POST.get('gender', 'Male')
        activity_level = request.POST.get('activity_level', 'moderate')
        fitness_goal = request.POST.get('fitness_goal', 'weight_loss')

        form_data = {
            'name': name,
            'height': height,
            'weight': weight,
            'age': age,
            'gender': gender,
            'activity_level': activity_level,
            'fitness_goal': fitness_goal
        }

        # Run AI Recommendation Engine
        ai_res = generate_ai_recommendation(
            height_cm=height,
            weight_kg=weight,
            age=age,
            gender=gender,
            activity_level=activity_level,
            fitness_goal=fitness_goal
        )

        user_obj = request.user if request.user.is_authenticated else None

        # Save to DB history
        BMIRecord.objects.create(
            user=user_obj,
            name=name,
            height=height,
            weight=weight,
            age=age,
            gender=gender,
            bmi_value=ai_res['bmi'],
            category=ai_res['category']
        )

        result = {
            'name': name,
            'height': height,
            'weight': weight,
            'age': age,
            'gender': gender,
            'activity_level': activity_level.replace('_', ' ').title(),
            'fitness_goal': fitness_goal.replace('_', ' ').title(),
            **ai_res
        }

        # Refresh history (role-scoped)
        history = _bmi_history(request, default_name)

    # Macro Chart JSON Data
    macro_labels = json.dumps(['Protein', 'Carbs', 'Fats'])
    if result:
        macro_data = json.dumps([result['protein_g'], result['carbs_g'], result['fats_g']])
        macro_colors = json.dumps(['rgba(245, 54, 92, 0.8)', 'rgba(94, 114, 228, 0.8)', 'rgba(255, 214, 0, 0.8)'])
    else:
        macro_data = json.dumps([120, 200, 60])
        macro_colors = json.dumps(['rgba(245, 54, 92, 0.8)', 'rgba(94, 114, 228, 0.8)', 'rgba(255, 214, 0, 0.8)'])

    context = {
        'form_data': form_data,
        'result': result,
        'history': history,
        'macro_labels': macro_labels,
        'macro_data': macro_data,
        'macro_colors': macro_colors,
    }
    return render(request, 'bmi-calculator.html', context)


@csrf_exempt
def chatbot_api(request):
    """
    Module 22: NLP & Grok AI Chatbot API Endpoint (AJAX)
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
        except Exception:
            message = request.POST.get('message', '')

        reply = get_bot_response(message)
        return JsonResponse({'reply': reply, 'status': 'success'})

    return JsonResponse({'reply': 'Send a POST request with a message!', 'status': 'error'})


def chatbot_page(request):
    """
    Module 22: Dedicated Chatbot Interface Page
    """
    return render(request, 'chatbot.html')


def get_churn_prediction_data():
    """Helper to collect database member metrics and feed into ML Churn Model"""
    members = BMIRecord.objects.values_list('name', flat=True).distinct()
    if not members:
        members = ['Aarav Sharma', 'Rohan Mehta', 'Vikram Shah', 'Neha Verma', 'Ananya Patel', 'Karan Gupta']

    members_feature_list = []
    for m in members:
        att_count = Attendance.objects.filter(member_name=m).count()
        att_per_wk = round(min(6.0, max(0.5, att_count / 4.0)), 1)
        has_pending = Payment.objects.filter(member_name=m, status='Pending').exists()
        
        last_att = Attendance.objects.filter(member_name=m).order_by('-date').first()
        days_inactive = (2026 - 2026) * 365 + 12 if not last_att else (30 - min(28, last_att.date.day))

        members_feature_list.append({
            'name': m,
            'attendance_per_wk': att_per_wk,
            'days_inactive': days_inactive,
            'tenure_months': random_tenure(m),
            'has_pending_dues': has_pending
        })

    return train_and_predict_churn(members_feature_list)


def random_tenure(name):
    """Deterministically assign realistic tenure in months"""
    return (len(name) * 3) % 18 + 1
