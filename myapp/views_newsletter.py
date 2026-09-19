"""
Views for Newsletter & Notification module (Module 6).
Handles email subscription and unsubscription.
"""
from django.shortcuts import render, redirect
from django.http import JsonResponse
from myapp.models import Subscriber
from myapp.forms import SubscriberForm


def subscribe(request):
    """Handle newsletter subscription from footer form"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            # Check if already subscribed
            existing = Subscriber.objects.filter(email=email).first()
            if existing:
                if not existing.is_active:
                    existing.is_active = True
                    existing.save()
            else:
                Subscriber.objects.create(email=email, is_active=True)
        
        # Redirect back to the referring page
        referer = request.META.get('HTTP_REFERER', '/')
        return redirect(referer)
    
    return redirect('/')


def unsubscribe(request):
    """Handle newsletter unsubscription"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            subscriber = Subscriber.objects.filter(email=email).first()
            if subscriber:
                subscriber.is_active = False
                subscriber.save()
        
        referer = request.META.get('HTTP_REFERER', '/')
        return redirect(referer)
    
    return redirect('/')
