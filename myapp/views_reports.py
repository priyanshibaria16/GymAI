"""
Views for Reports Export module (Module 8).
Handles CSV export of members, payments, and attendance data. (ADMIN ONLY)
"""
import csv
from django.shortcuts import render
from django.http import HttpResponse
from myapp.models import contacts, Payment, Attendance, BMIRecord, Booking
from myapp.decorators import admin_required


@admin_required
def reports_page(request):
    """Display report selection page (ADMIN ONLY)"""
    stats = {
        'total_contacts': contacts.objects.count(),
        'total_payments': Payment.objects.count(),
        'total_attendance': Attendance.objects.count(),
        'total_bmi_records': BMIRecord.objects.count(),
        'total_bookings': Booking.objects.count(),
    }
    return render(request, 'reports.html', stats)


@admin_required
def export_members_csv(request):
    """Export all contacts/members data as CSV (ADMIN ONLY)"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="gym_members.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Email', 'Phone', 'Comment'])
    
    for c in contacts.objects.all():
        writer.writerow([c.name, c.email, c.phone, c.comment])
    
    return response


@admin_required
def export_payments_csv(request):
    """Export all payment records as CSV (ADMIN ONLY)"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="gym_payments.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Member Name', 'Membership', 'Amount', 'Date', 'Method', 'Status'])
    
    for p in Payment.objects.all():
        writer.writerow([
            p.member_name,
            p.membership.name if p.membership else 'N/A',
            p.amount,
            p.payment_date.strftime('%Y-%m-%d'),
            p.method,
            p.status
        ])
    
    return response


@admin_required
def export_attendance_csv(request):
    """Export all attendance records as CSV (ADMIN ONLY)"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="gym_attendance.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Member Name', 'Date', 'Check In', 'Check Out'])
    
    for a in Attendance.objects.all():
        writer.writerow([
            a.member_name,
            a.date.strftime('%Y-%m-%d'),
            a.check_in_time.strftime('%H:%M'),
            a.check_out_time.strftime('%H:%M') if a.check_out_time else 'N/A'
        ])
    
    return response


@admin_required
def export_bmi_csv(request):
    """Export all BMI records as CSV (ADMIN ONLY)"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="gym_bmi_records.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Height (cm)', 'Weight (kg)', 'Age', 'Gender', 'BMI', 'Category', 'Date'])
    
    for b in BMIRecord.objects.all():
        writer.writerow([
            b.name, b.height, b.weight, b.age, b.gender,
            b.bmi_value, b.category, b.created_at.strftime('%Y-%m-%d')
        ])
    
    return response


@admin_required
def export_bookings_csv(request):
    """Export all booking records as CSV (ADMIN ONLY)"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="gym_bookings.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Member Name', 'Email', 'Class', 'Booking Date', 'Status'])
    
    for b in Booking.objects.all():
        writer.writerow([
            b.member_name,
            b.member_email or 'N/A',
            b.gym_class.name,
            b.booking_date.strftime('%Y-%m-%d %H:%M'),
            b.status
        ])
    
    return response
