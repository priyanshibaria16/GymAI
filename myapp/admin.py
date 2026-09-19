from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from myapp.models import (
    UserProfile, About, Team, contacts, Services, Membership,
    BMIRecord, GymClass, Booking, Attendance,
    Payment, WorkoutLog, BodyMetrics, Subscriber,
    Newsletter, Review, Feature, BlogPost, GalleryItem
)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile & Role'
    fk_name = 'user'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'profile__role')

    def get_role(self, instance):
        return instance.profile.role if hasattr(instance, 'profile') else 'MEMBER'
    get_role.short_description = 'Role'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'created_at', 'updated_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']


# Core Models
@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    list_display = ['head', 'experience_years', 'video_url']

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'post', 'facebook', 'twitter', 'instagram']
    search_fields = ['name', 'post']

@admin.register(contacts)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'created_at']
    search_fields = ['name', 'email', 'phone']

@admin.register(Services)
class ServicesAdmin(admin.ModelAdmin):
    list_display = ['head', 'tag', 'icon_class']

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'period', 'is_popular']
    list_filter = ['is_popular']

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ['title', 'icon_class']

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'read_time', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'content']

@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'created_at']
    list_filter = ['category']


# Modules Admin Registrations
@admin.register(BMIRecord)
class BMIRecordAdmin(admin.ModelAdmin):
    list_display = ['name', 'height', 'weight', 'age', 'gender', 'bmi_value', 'category', 'created_at']
    list_filter = ['category', 'gender', 'created_at']
    search_fields = ['name']

@admin.register(GymClass)
class GymClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'trainer', 'schedule_day', 'schedule_time', 'capacity', 'current_enrolled']
    list_filter = ['schedule_day', 'trainer']
    search_fields = ['name', 'trainer']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['member_name', 'member_email', 'gym_class', 'booking_date', 'status']
    list_filter = ['status', 'gym_class', 'booking_date']
    search_fields = ['member_name', 'member_email']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['member_name', 'date', 'check_in_time', 'check_out_time']
    list_filter = ['date']
    search_fields = ['member_name']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['member_name', 'membership', 'amount', 'payment_date', 'method', 'status']
    list_filter = ['method', 'status', 'payment_date']
    search_fields = ['member_name']

@admin.register(WorkoutLog)
class WorkoutLogAdmin(admin.ModelAdmin):
    list_display = ['member_name', 'exercise', 'sets', 'reps', 'weight_used', 'date']
    list_filter = ['exercise', 'date']
    search_fields = ['member_name']

@admin.register(BodyMetrics)
class BodyMetricsAdmin(admin.ModelAdmin):
    list_display = ['member_name', 'body_weight', 'chest', 'waist', 'biceps', 'thighs', 'date']
    list_filter = ['date']
    search_fields = ['member_name']

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'subscribed_date', 'is_active']
    list_filter = ['is_active', 'subscribed_date']
    search_fields = ['email']

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['subject', 'sent_date', 'recipients_count']
    search_fields = ['subject']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['member_name', 'rating', 'date', 'is_approved']
    list_filter = ['rating', 'is_approved', 'date']
    search_fields = ['member_name', 'review_text']
    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = "Approve selected reviews"