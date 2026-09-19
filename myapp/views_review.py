"""
Views for Testimonials & Reviews module (Module 7).
Displays approved reviews with rating charts, handles review submission.
"""
from django.shortcuts import render, redirect
from django.db.models import Avg, Count
from myapp.models import Review
from myapp.forms import ReviewForm
from myapp.utils.chart_helpers import get_rating_distribution
import json


def testimonials(request):
    """Display testimonials with rating chart and review submission form"""
    
    # Handle review submission
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.is_approved = False  # Requires admin approval
            if request.user.is_authenticated:
                # Bind the review to the signed-in user account
                review.user = request.user
                if not review.member_name:
                    review.member_name = request.user.get_full_name() or request.user.username
            review.save()
            return redirect('testimonials')
    else:
        form = ReviewForm()
    
    # Approved reviews
    reviews = Review.objects.filter(is_approved=True)
    
    # Stats
    total_reviews = reviews.count()
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    
    # Rating distribution chart data
    rating_labels, rating_data = get_rating_distribution(Review)
    
    # Star breakdown for display
    star_breakdown = []
    for i in range(5, 0, -1):
        count = reviews.filter(rating=i).count()
        percentage = (count / total_reviews * 100) if total_reviews > 0 else 0
        star_breakdown.append({
            'stars': i,
            'count': count,
            'percentage': round(percentage, 1),
        })
    
    context = {
        'reviews': reviews,
        'form': form,
        'total_reviews': total_reviews,
        'avg_rating': round(avg_rating, 1),
        'rating_labels': rating_labels,
        'rating_data': rating_data,
        'star_breakdown': star_breakdown,
        'submitted': request.method == 'POST' and form.is_valid() if request.method == 'POST' else False,
    }
    
    return render(request, 'testimonials.html', context)
