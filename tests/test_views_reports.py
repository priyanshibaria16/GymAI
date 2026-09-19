"""
Integration tests for Module 8: Reports Export
Every export endpoint must return a valid CSV attachment with correct
headers and data rows.
"""
import csv
import io

import pytest

pytestmark = pytest.mark.django_db


def parse_csv(response):
    """Decode an HttpResponse body into a list of CSV rows."""
    assert response['Content-Type'] == 'text/csv'
    return list(csv.reader(io.StringIO(response.content.decode('utf-8'))))


class TestReportsPage:
    def test_reports_page_renders_stats(
            self, admin_client, sample_contact, sample_payment,
            sample_attendance, sample_bmi_record, sample_booking):
        response = admin_client.get('/reports/')
        assert response.status_code == 200
        ctx = response.context
        assert ctx['total_contacts'] == 1
        assert ctx['total_payments'] == 1
        assert ctx['total_attendance'] == 1
        assert ctx['total_bmi_records'] == 1
        assert ctx['total_bookings'] == 1


class TestMembersExport:
    def test_export_members_csv(self, admin_client, sample_contact):
        response = admin_client.get('/export/members/')
        rows = parse_csv(response)
        assert 'gym_members.csv' in response['Content-Disposition']
        assert rows[0] == ['Name', 'Email', 'Phone', 'Comment']
        assert rows[1] == ['Neha Verma', 'neha@example.com', '9876543210', 'Interested in VIP plan']

    def test_export_members_empty_db(self, admin_client):
        rows = parse_csv(admin_client.get('/export/members/'))
        assert len(rows) == 1  # header only


class TestPaymentsExport:
    def test_export_payments_csv(self, admin_client, sample_payment):
        rows = parse_csv(admin_client.get('/export/payments/'))
        assert rows[0] == ['Member Name', 'Membership', 'Amount', 'Date', 'Method', 'Status']
        row = rows[1]
        assert row[0] == 'Aarav Sharma'
        assert row[1] == 'Standard Plan'
        assert row[4] == 'UPI'
        assert row[5] == 'Completed'

    def test_export_payments_null_membership_shows_na(self, admin_client):
        from decimal import Decimal
        from myapp.models import Payment
        Payment.objects.create(member_name='Solo', amount=Decimal('100.00'))
        rows = parse_csv(admin_client.get('/export/payments/'))
        assert rows[1][1] == 'N/A'


class TestAttendanceExport:
    def test_export_attendance_csv(self, admin_client, sample_attendance):
        rows = parse_csv(admin_client.get('/export/attendance/'))
        assert rows[0] == ['Member Name', 'Date', 'Check In', 'Check Out']
        assert rows[1][0] == 'Aarav Sharma'
        assert rows[1][2] == '07:15'
        assert rows[1][3] == '08:45'

    def test_export_attendance_missing_checkout_shows_na(self, admin_client):
        from datetime import date, time
        from myapp.models import Attendance
        Attendance.objects.create(
            member_name='No Checkout', check_in_time=time(9, 0), date=date.today(),
        )
        rows = parse_csv(admin_client.get('/export/attendance/'))
        assert rows[1][3] == 'N/A'


class TestBMIExport:
    def test_export_bmi_csv(self, admin_client, sample_bmi_record):
        rows = parse_csv(admin_client.get('/export/bmi/'))
        assert rows[0] == ['Name', 'Height (cm)', 'Weight (kg)', 'Age', 'Gender', 'BMI', 'Category', 'Date']
        row = rows[1]
        assert row[0] == 'Aarav Sharma'
        assert float(row[5]) == pytest.approx(22.9, abs=0.01)
        assert row[6] == 'Healthy'


class TestBookingsExport:
    def test_export_bookings_csv(self, admin_client, sample_booking):
        rows = parse_csv(admin_client.get('/export/bookings/'))
        assert rows[0] == ['Member Name', 'Email', 'Class', 'Booking Date', 'Status']
        row = rows[1]
        assert row[0] == 'Aarav Sharma'
        assert row[2] == 'HIIT Fat Burn'
        assert row[4] == 'Confirmed'

    def test_export_bookings_null_email_shows_na(self, admin_client, sample_gym_class):
        from myapp.models import Booking
        Booking.objects.create(member_name='NoMail', gym_class=sample_gym_class)
        rows = parse_csv(admin_client.get('/export/bookings/'))
        emails = [r[1] for r in rows[1:]]
        assert 'N/A' in emails
