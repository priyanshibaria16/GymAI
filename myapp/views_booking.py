"""
Views for Class Booking & Attendance module (Module 3).
Handles class timetable display, booking, and attendance tracking.
"""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from myapp.models import GymClass, Booking, Attendance
from myapp.forms import BookingForm


def class_timetable(request):
    """Display all gym classes with booking availability"""
    classes = GymClass.objects.all()
    
    # Group classes by day for timetable view
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    timetable = {}
    for day in days_order:
        day_classes = classes.filter(schedule_day=day)
        if day_classes.exists():
            timetable[day] = day_classes
    
    # Chart data: Class popularity
    class_names = []
    class_enrolled = []
    class_capacity = []
    for gc in classes:
        class_names.append(gc.name)
        class_enrolled.append(gc.current_enrolled)
        class_capacity.append(gc.capacity)
    
    context = {
        'timetable': timetable,
        'classes': classes,
        'class_names': json.dumps(class_names),
        'class_enrolled': json.dumps(class_enrolled),
        'class_capacity': json.dumps(class_capacity),
    }
    
    return render(request, 'class-timetable.html', context)


def book_class(request, class_id):
    """Handle class booking"""
    gym_class = get_object_or_404(GymClass, id=class_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            if gym_class.is_full:
                context = {
                    'gym_class': gym_class,
                    'form': form,
                    'error': 'Sorry, this class is fully booked!',
                }
                return render(request, 'booking-confirmation.html', context)
            
            user_obj = request.user if request.user.is_authenticated else None

            # Create booking with user association
            booking = Booking.objects.create(
                user=user_obj,
                member_name=form.cleaned_data['member_name'],
                member_email=form.cleaned_data.get('member_email', ''),
                gym_class=gym_class,
                status='Confirmed'
            )
            
            # Update enrollment count
            gym_class.current_enrolled += 1
            gym_class.save()
            
            context = {
                'booking': booking,
                'gym_class': gym_class,
                'success': True,
            }
            return render(request, 'booking-confirmation.html', context)
    else:
        initial = {}
        if request.user.is_authenticated:
            initial['member_name'] = request.user.get_full_name() or request.user.username
            initial['member_email'] = request.user.email
        form = BookingForm(initial=initial)
    
    context = {
        'gym_class': gym_class,
        'form': form,
    }
    return render(request, 'booking-confirmation.html', context)
