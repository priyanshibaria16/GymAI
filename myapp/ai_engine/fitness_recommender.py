"""
AI-Based BMI & Fitness Recommender System
Calculates BMR/TDEE, predicts recommended fitness regime & macronutrient distribution using decision logic & Google Gemini AI process automation.
"""
import json
import urllib.request
import urllib.error
from django.conf import settings


def calculate_bmr(weight_kg, height_cm, age, gender):
    """Mifflin-St Jeor Equation for BMR"""
    if str(gender).lower() == 'female':
        return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    else:
        return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5


def calculate_tdee(bmr, activity_level):
    """Activity multipliers for Total Daily Energy Expenditure"""
    multipliers = {
        'sedentary': 1.2,        # Little/no exercise
        'light': 1.375,         # 1-3 days/week
        'moderate': 1.55,       # 3-5 days/week
        'very_active': 1.725,    # 6-7 days/week
        'extra_active': 1.9     # Hard exercise/job
    }
    multiplier = multipliers.get(str(activity_level).lower(), 1.375)
    return round(bmr * multiplier)


import os
import json
import urllib.request
import urllib.error
from django.conf import settings

def generate_gemini_automated_insight(height_cm, weight_kg, age, gender, bmi, category, goal_text, tdee):
    """
    Automated process engine powered by Google Gemini 3.6 Flash.
    Generates personalized fitness insights and automated coaching summaries for gym members.
    Bypasses live API during unit tests to allow deterministic test assertions.
    """
    if 'PYTEST_CURRENT_TEST' in os.environ:
        return None

    gemini_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not gemini_key:
        return None

    prompt = (
        f"Act as an automated expert fitness coach at IronPeak Fitness Studio. "
        f"Synthesize an automated 2-sentence personalized fitness & nutrition coaching directive for a {age}-year-old {gender} "
        f"with Height: {height_cm}cm, Weight: {weight_kg}kg, BMI: {bmi} ({category}), Goal: {goal_text}, TDEE: {tdee} kcal. "
        f"Keep the tone encouraging, direct, and actionable."
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={gemini_key}"
    payload = {
        'contents': [{'parts': [{'text': prompt}]}]
    }

    try:
        req = urllib.request.Request(
            url,
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload).encode('utf-8')
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            cand = res_data['candidates'][0]['content']['parts']
            text = ' '.join([c['text'] for c in cand if 'text' in c]).strip()
            if text:
                return text
    except Exception:
        pass
    return None


def generate_ai_recommendation(height_cm, weight_kg, age, gender, activity_level='moderate', fitness_goal='weight_loss'):
    """
    AI Recommendation Engine:
    Predicts calorie target, macro split, workout schedule, and lifestyle advice.
    """
    height_m = height_cm / 100.0
    bmi = round(weight_kg / (height_m ** 2), 1)

    bmr = calculate_bmr(weight_kg, height_cm, age, gender)
    tdee = calculate_tdee(bmr, activity_level)

    # Goal adjustment
    if fitness_goal == 'weight_loss':
        target_calories = round(tdee - 500)
        goal_text = "Caloric Deficit (Fat Loss Focus)"
        workout_type = "High-Intensity Interval Training (HIIT) + Compound Resistance"
        cardio_min = "30-40 mins / day (4-5 days/week)"
        strength_days = "3 days / week (Full Body Split)"
        protein_ratio, carb_ratio, fat_ratio = 40, 30, 30
    elif fitness_goal == 'muscle_gain':
        target_calories = round(tdee + 400)
        goal_text = "Caloric Surplus (Hypertrophy & Muscle Gain)"
        workout_type = "Heavy Progressive Overload & Hypertrophy Split"
        cardio_min = "15-20 mins light incline walk (2-3 days/week)"
        strength_days = "5 days / week (Push-Pull-Legs Split)"
        protein_ratio, carb_ratio, fat_ratio = 30, 50, 20
    elif fitness_goal == 'endurance':
        target_calories = round(tdee + 150)
        goal_text = "Stamina & Cardiovascular Endurance"
        workout_type = "Crossfit, Rowing, Long-Distance Cardio & Core Stability"
        cardio_min = "45-60 mins / day (5 days/week)"
        strength_days = "2 days / week (Circuit Training)"
        protein_ratio, carb_ratio, fat_ratio = 25, 55, 20
    else:  # maintenance
        target_calories = round(tdee)
        goal_text = "Maintenance & Functional Fitness"
        workout_type = "Balanced Strength Training + Aerobic Conditioning"
        cardio_min = "25 mins / day (3 days/week)"
        strength_days = "4 days / week (Upper/Lower Split)"
        protein_ratio, carb_ratio, fat_ratio = 30, 40, 30

    # Macro grams
    protein_g = round((target_calories * (protein_ratio / 100.0)) / 4)
    carbs_g = round((target_calories * (carb_ratio / 100.0)) / 4)
    fats_g = round((target_calories * (fat_ratio / 100.0)) / 9)

    # BMI Category & AI Advice
    if bmi < 18.5:
        category = "Underweight"
        ai_insight = "Your BMI indicates you are underweight. Focus on nutrient-dense whole foods and progressive strength training to build healthy muscle mass safely."
    elif bmi < 25.0:
        category = "Healthy"
        ai_insight = "Congratulations! Your BMI is in the healthy range. Maintain your current balanced lifestyle with consistent strength and mobility work."
    elif bmi < 30.0:
        category = "Overweight"
        ai_insight = "Your BMI falls into the overweight category. Increasing daily step count, focusing on protein-dense meals, and 4x weekly workouts will help optimize your body composition."
    else:
        category = "Obese"
        ai_insight = "Your BMI indicates obesity. We recommend a structured, low-impact exercise program (walking, swimming, cycling) combined with a sustainable caloric deficit. Consult our gym trainers for guidance."

    # Try Gemini 3.6 Flash process automation for personalized coaching insight
    gemini_insight = generate_gemini_automated_insight(
        height_cm, weight_kg, age, gender, bmi, category, goal_text, tdee
    )
    if gemini_insight:
        ai_insight = f"[🤖 Gemini AI Automation] {gemini_insight}"

    return {
        'bmi': bmi,
        'category': category,
        'bmr': round(bmr),
        'tdee': tdee,
        'target_calories': target_calories,
        'goal_text': goal_text,
        'workout_type': workout_type,
        'cardio_recommendation': cardio_min,
        'strength_recommendation': strength_days,
        'protein_g': protein_g,
        'carbs_g': carbs_g,
        'fats_g': fats_g,
        'protein_ratio': protein_ratio,
        'carb_ratio': carb_ratio,
        'fat_ratio': fat_ratio,
        'ai_insight': ai_insight,
    }
