from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from myapp.models import (
    About, Team, contacts, Services, Membership,
    Feature, BlogPost, GalleryItem, GymClass, Review,
    BMIRecord, Payment, Attendance
)


def index(request):
    """Public dynamic homepage view fetching all sections from DB"""
    about = About.objects.first()
    memberships = Membership.objects.all()
    team = Team.objects.all()
    services = Services.objects.all()
    features = Feature.objects.all()
    classes = GymClass.objects.all()[:6]
    reviews = Review.objects.filter(is_approved=True)[:6]
    blogs = BlogPost.objects.all()[:3]

    context = {
        'about': about,
        'memberships': memberships,
        'team': team,
        'services': services,
        'features': features,
        'classes': classes,
        'reviews': reviews,
        'blogs': blogs,
    }
    return render(request, 'index.html', context)


def about_us(request):
    """Dynamic About Us view"""
    about = About.objects.first()
    team = Team.objects.all()
    features = Feature.objects.all()
    reviews = Review.objects.filter(is_approved=True)[:4]

    stats = {
        'total_members': BMIRecord.objects.values('name').distinct().count() or 150,
        'total_trainers': Team.objects.count() or 6,
        'total_classes': GymClass.objects.count() or 10,
        'happy_clients': contacts.objects.count() or 85,
    }

    context = {
        'about': about,
        'team': team,
        'features': features,
        'reviews': reviews,
        'stats': stats,
    }
    return render(request, 'about-us.html', context)


def services(request):
    """Dynamic Services & Pricing view"""
    services_list = Services.objects.all()
    memberships = Membership.objects.all()
    classes = GymClass.objects.all()[:4]

    context = {
        'services': services_list,
        'memberships': memberships,
        'classes': classes,
    }
    return render(request, 'services.html', context)


def team(request):
    """Dynamic Team Members view"""
    team_members = Team.objects.all()
    context = {
        'team': team_members,
    }
    return render(request, 'team.html', context)


def blog(request):
    """Dynamic Blog list view with search & category filter"""
    category = request.GET.get('category', '')
    query = request.GET.get('q', '')

    blogs = BlogPost.objects.all()
    if category:
        blogs = blogs.filter(category__iexact=category)
    if query:
        blogs = blogs.filter(title__icontains=query)

    recent_blogs = BlogPost.objects.all()[:4]

    context = {
        'blogs': blogs,
        'recent_blogs': recent_blogs,
        'selected_category': category,
        'search_query': query,
    }
    return render(request, 'blog.html', context)


def blog_details(request, pk=None):
    """Dynamic Blog Detail view"""
    if pk:
        article = get_object_or_404(BlogPost, pk=pk)
    else:
        article = BlogPost.objects.first()

    recent_blogs = BlogPost.objects.exclude(id=article.id if article else None)[:3]

    context = {
        'blog': article,
        'recent_blogs': recent_blogs,
    }
    return render(request, 'blog-details.html', context)


def gallery(request):
    """Dynamic Gallery view with category filtering"""
    category = request.GET.get('category', 'all')
    items = GalleryItem.objects.all()
    if category != 'all':
        items = items.filter(category=category)

    context = {
        'gallery_items': items,
        'selected_category': category,
    }
    return render(request, 'gallery.html', context)


def contact(request):
    """Dynamic Contact page view with form submission"""
    submitted = False
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        comment = request.POST.get('comment')

        if name and email and comment:
            contacts.objects.create(
                name=name,
                email=email,
                phone=phone or '',
                comment=comment
            )
            submitted = True

    context = {
        'submitted': submitted,
    }
    return render(request, 'contact.html', context)


def calss_details(request):
    """Dynamic Class Details view"""
    classes = GymClass.objects.all()
    first_class = classes.first()
    context = {
        'classes': classes,
        'gym_class': first_class,
    }
    return render(request, 'class-details.html', context)


def page_not_found(request, exception=None):
    """Themed 404 handler (wired via handler404 in gym/urls.py)."""
    return render(request, '404.html', status=404)
