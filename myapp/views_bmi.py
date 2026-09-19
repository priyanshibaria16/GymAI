"""
Views for the BMI Calculator module (Module 2).
Handles BMI calculation, stores records, and returns visual chart data.
"""
from django.shortcuts import render
from myapp.models import BMIRecord
from myapp.forms import BMICalculatorForm
import json


def calculate_bmi(height_cm, weight_kg):
    """Calculate BMI from height (cm) and weight (kg)"""
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 1)


def get_bmi_category(bmi_value):
    """Determine BMI category based on value"""
    if bmi_value < 18.5:
        return 'Underweight'
    elif bmi_value < 25:
        return 'Healthy'
    elif bmi_value < 30:
        return 'Overweight'
    else:
        return 'Obese'


def get_category_color(category):
    """Return color code for BMI category"""
    colors = {
        'Underweight': '#3498db',  # Blue
        'Healthy': '#2ecc71',       # Green
        'Overweight': '#f39c12',    # Orange
        'Obese': '#e74c3c',         # Red
    }
    return colors.get(category, '#95a5a6')


def bmi_calculator(request):
    """Handle BMI calculation form and display results with chart"""
    result = None
    form = BMICalculatorForm()
    history = BMIRecord.objects.all()[:10]  # Latest 10 records
    
    if request.method == 'POST':
        form = BMICalculatorForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            height = form.cleaned_data['height']
            weight = form.cleaned_data['weight']
            age = form.cleaned_data['age']
            gender = form.cleaned_data['gender']
            
            # Calculate BMI
            bmi_value = calculate_bmi(height, weight)
            category = get_bmi_category(bmi_value)
            color = get_category_color(category)
            
            # Save to database
            record = BMIRecord.objects.create(
                name=name,
                height=height,
                weight=weight,
                age=age,
                gender=gender,
                bmi_value=bmi_value,
                category=category
            )
            
            # Build result dict
            result = {
                'name': name,
                'bmi_value': bmi_value,
                'category': category,
                'color': color,
                'height': height,
                'weight': weight,
                'age': age,
                'gender': gender,
            }
            
            # Refresh history after save
            history = BMIRecord.objects.all()[:10]
    
    # Chart data for BMI gauge (doughnut chart)
    # Build history chart data for user's BMI over time
    history_labels = []
    history_data = []
    if result:
        user_records = BMIRecord.objects.filter(name=result['name']).order_by('created_at')[:10]
        for rec in user_records:
            history_labels.append(rec.created_at.strftime('%d %b %Y'))
            history_data.append(rec.bmi_value)
    
    context = {
        'form': form,
        'result': result,
        'history': history,
        'history_labels': json.dumps(history_labels),
        'history_data': json.dumps(history_data),
    }
    
    return render(request, 'bmi-calculator.html', context)
