from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import (
    views_dashboard, views_bmi, views_booking,
    views_payment, views_progress, views_newsletter,
    views_review, views_reports, views_ai,
    views_auth, views_admin, views_trainer, views_member
)

urlpatterns = [
    # Public Pages
    path('', views.index, name='index.html'),
    path('index/', views.index, name='index'),
    path('blog', views.blog, name='blog.html'),
    path('about', views.about_us, name='about-us.html'),
    path('blog_details', views.blog_details, name='blog-details.html'),
    path('blog_details/<int:pk>/', views.blog_details, name='blog-detail'),
    path('class_details', views.calss_details, name='class-details.html'),
    path('class_timetable', views_booking.class_timetable, name='class_timetable.html'),
    path('contact', views.contact, name='contact.html'),
    path('gallery', views.gallery, name='gallery.html'),
    path('team', views.team, name='team.html'),
    path('services', views.services, name='services.html'),

    # Authentication Routes (supporting both underscore and hyphen aliases for compatibility)
    path('signup/', views_auth.signup_view, name='signup'),
    path('login/', views_auth.login_view, name='login'),
    path('logout/', views_auth.logout_view, name='logout'),
    path('profile/', views_auth.profile_view, name='profile'),
    path('profile/edit/', views_auth.edit_profile_view, name='edit-profile'),
    path('profile/edit-alias/', views_auth.edit_profile_view, name='edit_profile'),
    path('change-password/', views_auth.change_password_view, name='change-password'),
    path('change-password-alias/', views_auth.change_password_view, name='change_password'),

    # Password Reset Routes
    path('forgot-password/', auth_views.PasswordResetView.as_view(
        template_name='auth/forgot_password.html',
        email_template_name='auth/password_reset_email.html',
        subject_template_name='auth/password_reset_subject.txt',
        success_url='/password-reset/done/'
    ), name='forgot-password'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='auth/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='auth/password_reset_confirm.html',
        success_url='/reset/done/'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='auth/password_reset_complete.html'
    ), name='password_reset_complete'),

    # Central & Role-Specific Dashboards (supporting both hyphen and underscore aliases)
    path('dashboard/', views_auth.role_dashboard_router, name='dashboard'),
    path('dashboard/role/', views_auth.role_dashboard_router, name='role_dashboard'),
    path('admin-dashboard/', views_admin.admin_dashboard_view, name='admin-dashboard'),
    path('admin-dashboard-alias/', views_admin.admin_dashboard_view, name='admin_dashboard'),
    path('executive-analytics/', views_dashboard.dashboard, name='executive-analytics'),
    path('trainer-dashboard/', views_trainer.trainer_dashboard_view, name='trainer-dashboard'),
    path('trainer-dashboard-alias/', views_trainer.trainer_dashboard_view, name='trainer_dashboard'),
    path('member-dashboard/', views_member.member_dashboard_view, name='member-dashboard'),
    path('member-dashboard-alias/', views_member.member_dashboard_view, name='member_dashboard'),

    # Admin User Management Routes
    path('admin/users/', views_admin.admin_user_list_view, name='admin-user-list'),
    path('admin/users/list/', views_admin.admin_user_list_view, name='admin_user_list'),
    path('admin/users/add/', views_admin.admin_add_member_view, name='admin-add-member'),
    path('admin/users/<int:user_id>/', views_admin.admin_user_detail_view, name='admin-user-detail'),
    path('admin/users/<int:user_id>/detail/', views_admin.admin_user_detail_view, name='admin_user_detail'),
    path('admin/users/<int:user_id>/edit/', views_admin.admin_user_edit_view, name='admin-user-edit'),
    path('admin/users/<int:user_id>/edit-alias/', views_admin.admin_user_edit_view, name='admin_user_edit'),
    path('admin/users/<int:user_id>/role/', views_admin.admin_user_role_view, name='admin-user-role'),
    path('admin/users/<int:user_id>/role-alias/', views_admin.admin_user_role_view, name='admin_user_role'),
    path('admin/users/<int:user_id>/status/', views_admin.admin_user_status_view, name='admin-user-status'),
    path('admin/users/<int:user_id>/status-alias/', views_admin.admin_user_status_view, name='admin_user_status'),

    # Admin AI Automations Center
    path('admin/automations/', views_admin.admin_automations_view, name='admin-automations'),

    # Admin Class Management (add/edit/delete + assign trainer)
    path('admin/classes/', views_admin.admin_class_list_view, name='admin-class-list'),
    path('admin/classes/add/', views_admin.admin_class_form_view, name='admin-class-add'),
    path('admin/classes/<int:class_id>/edit/', views_admin.admin_class_form_view, name='admin-class-edit'),
    path('admin/classes/<int:class_id>/delete/', views_admin.admin_class_delete_view, name='admin-class-delete'),

    # Protected Feature Modules
    path('bmi_calculator', views_ai.ai_bmi_calculator, name='bmi-calculator.html'),
    path('ai-bmi/', views_ai.ai_bmi_calculator, name='ai_bmi'),
    path('ai-recommender/', views_ai.chatbot_page, name='ai_recommender'),
    path('class-timetable/', views_booking.class_timetable, name='class-timetable'),
    path('class-timetable-alias/', views_booking.class_timetable, name='class_schedule'),
    path('book-class/', views_booking.book_class, name='book_class'),
    path('book-class/<int:class_id>/', views_booking.book_class, name='book-class'),
    path('payment-dashboard/', views_payment.payment_dashboard, name='payment-dashboard'),
    path('payment-dashboard-alias/', views_payment.payment_dashboard, name='payment_dashboard'),
    path('api/stripe-payment/', views_payment.process_stripe_payment, name='stripe-payment'),
    path('member-progress/', views_progress.member_progress, name='member-progress'),
    path('member-progress-alias/', views_progress.member_progress, name='member_progress'),
    path('add-workout/', views_progress.add_workout, name='add-workout'),
    path('add-workout-alias/', views_progress.add_workout, name='add_workout'),
    path('add-metrics/', views_progress.add_metrics, name='add-metrics'),
    path('attendance/', views_booking.class_timetable, name='attendance_page'),
    path('trainer/mark-attendance/', views_trainer.trainer_mark_attendance_view, name='trainer-mark-attendance'),
    path('trainer/class/<int:class_id>/attendance/', views_trainer.trainer_class_attendance_view, name='trainer-class-attendance'),

    # Newsletter & Chatbot
    path('subscribe/', views_newsletter.subscribe, name='subscribe'),
    path('unsubscribe/', views_newsletter.unsubscribe, name='unsubscribe'),
    path('chatbot/', views_ai.chatbot_page, name='chatbot'),
    path('api/chatbot/', views_ai.chatbot_api, name='chatbot-api'),

    # Testimonials & Reviews
    path('testimonials/', views_review.testimonials, name='testimonials'),

    # Reports & Exports (ADMIN Only)
    path('reports/', views_reports.reports_page, name='reports'),
    path('export/members/', views_reports.export_members_csv, name='export-members'),
    path('export/payments/', views_reports.export_payments_csv, name='export-payments'),
    path('export/payments-legacy/', views_reports.export_payments_csv, name='export-members-payments'),
    path('export/attendance/', views_reports.export_attendance_csv, name='export-attendance'),
    path('export/bmi/', views_reports.export_bmi_csv, name='export-bmi'),
    path('export/bookings/', views_reports.export_bookings_csv, name='export-bookings'),
]
