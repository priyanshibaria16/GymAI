"""
Shared pytest fixtures for the Gym Management System test suite.
"""
import io
from datetime import date, time
from decimal import Decimal

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from myapp.models import (
    UserProfile, About, Team, contacts, Services, Membership, Feature,
    BlogPost, GalleryItem, BMIRecord, GymClass, Booking,
    Attendance, Payment, WorkoutLog, BodyMetrics, Subscriber, Review,
)
from django.contrib.auth.models import User

@pytest.fixture
def admin_user(db):
    user = User.objects.create_superuser('test_admin', 'admin@test.com', 'AdminPass123!')
    user.profile.role = UserProfile.ROLE_ADMIN
    user.profile.save()
    return user

@pytest.fixture
def trainer_user(db):
    user = User.objects.create_user('test_trainer', 'trainer@test.com', 'TrainerPass123!')
    user.profile.role = UserProfile.ROLE_TRAINER
    user.profile.save()
    return user

@pytest.fixture
def member_user(db):
    user = User.objects.create_user('test_member', 'member@test.com', 'MemberPass123!')
    user.profile.role = UserProfile.ROLE_MEMBER
    user.profile.save()
    return user

@pytest.fixture
def admin_client(client, admin_user):
    client.force_login(admin_user)
    return client

@pytest.fixture
def trainer_client(client, trainer_user):
    client.force_login(trainer_user)
    return client

@pytest.fixture
def member_client(client, member_user):
    client.force_login(member_user)
    return client



def tiny_png(name='test.png'):
    """Generate a real 1x1 PNG upload so ImageField.url works in templates."""
    buffer = io.BytesIO()
    Image.new('RGB', (1, 1), color=(255, 0, 0)).save(buffer, format='PNG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/png')


@pytest.fixture(autouse=True)
def _sandbox_media(tmp_path, settings):
    """Keep uploaded test images out of the project directory."""
    settings.MEDIA_ROOT = tmp_path / 'media'


@pytest.fixture(autouse=True)
def _disable_gemini(settings):
    """Force AI automations to use the deterministic local fallback.

    Guarantees the test suite never makes a live network call to Gemini,
    regardless of whether a real key is present in .env.
    """
    settings.GEMINI_API_KEY = ''


@pytest.fixture(autouse=True)
def _clear_ai_cache():
    """Reset the in-process automations cache between tests."""
    from myapp.ai_engine import automations
    automations.clear_cache()
    yield
    automations.clear_cache()



@pytest.fixture
def sample_membership(db):
    return Membership.objects.create(
        name="Standard Plan",
        price="2500",
        period="MONTHLY",
        description="Gym floor + Group classes",
        features_list="Free riding, Unlimited equipments, Personal trainer",
        is_popular=True,
    )


@pytest.fixture
def sample_gym_class(db):
    return GymClass.objects.create(
        name="HIIT Fat Burn",
        trainer="Vikram Shah",
        schedule_day="Monday",
        schedule_time=time(7, 0),
        duration_minutes=60,
        capacity=20,
        current_enrolled=5,
        description="High intensity interval training",
    )


@pytest.fixture
def full_gym_class(db):
    return GymClass.objects.create(
        name="Power Yoga",
        trainer="Priya Joshi",
        schedule_day="Tuesday",
        schedule_time=time(6, 30),
        capacity=2,
        current_enrolled=2,
    )


@pytest.fixture
def sample_bmi_record(db):
    return BMIRecord.objects.create(
        name="Aarav Sharma",
        height=175.0,
        weight=70.0,
        age=28,
        gender="Male",
        bmi_value=22.9,
        category="Healthy",
    )


@pytest.fixture
def sample_payment(db, sample_membership):
    return Payment.objects.create(
        member_name="Aarav Sharma",
        membership=sample_membership,
        amount=Decimal("2500.00"),
        payment_date=date.today(),
        method="UPI",
        status="Completed",
    )


@pytest.fixture
def pending_payment(db, sample_membership):
    return Payment.objects.create(
        member_name="Rohan Mehta",
        membership=sample_membership,
        amount=Decimal("1500.00"),
        payment_date=date.today(),
        method="Cash",
        status="Pending",
    )


@pytest.fixture
def sample_attendance(db):
    return Attendance.objects.create(
        member_name="Aarav Sharma",
        check_in_time=time(7, 15),
        check_out_time=time(8, 45),
        date=date.today(),
    )


@pytest.fixture
def sample_contact(db):
    return contacts.objects.create(
        name="Neha Verma",
        email="neha@example.com",
        phone="9876543210",
        comment="Interested in VIP plan",
    )


@pytest.fixture
def sample_team(db):
    return Team.objects.create(
        name="Priya Joshi",
        post="Yoga Trainer",
        bio="Certified yoga specialist with 8 years of experience.",
        image=tiny_png('team.png'),
    )


@pytest.fixture
def sample_service(db):
    return Services.objects.create(
        head="Personal Training",
        description="One-on-one coaching sessions",
        image=tiny_png('service.png'),
    )


@pytest.fixture
def sample_about(db):
    return About.objects.create(
        head="About Tech Innovation Gym",
        description="The best gym in Ahmedabad",
        experience_years=10,
    )


@pytest.fixture
def sample_feature(db):
    return Feature.objects.create(
        title="Modern Equipment",
        description="Imported strength machinery",
    )


@pytest.fixture
def sample_blog(db):
    return BlogPost.objects.create(
        title="10 Tips for Fat Loss",
        slug="10-tips-for-fat-loss",
        author="Admin",
        category="Fitness",
        snippet="Short snippet",
        content="Full article content here.",
    )


@pytest.fixture
def sample_gallery_item(db):
    return GalleryItem.objects.create(
        title="Morning Workout",
        category="workout",
    )


@pytest.fixture
def sample_booking(db, sample_gym_class):
    return Booking.objects.create(
        member_name="Aarav Sharma",
        member_email="aarav@example.com",
        gym_class=sample_gym_class,
        status="Confirmed",
    )


@pytest.fixture
def sample_workout_log(db):
    return WorkoutLog.objects.create(
        member_name="Aarav Sharma",
        exercise="Bench Press",
        sets=3,
        reps=10,
        weight_used=60.0,
        date=date.today(),
    )


@pytest.fixture
def sample_body_metrics(db):
    return BodyMetrics.objects.create(
        member_name="Aarav Sharma",
        body_weight=70.0,
        chest=38.0,
        waist=32.0,
        biceps=14.0,
        thighs=22.0,
        date=date.today(),
    )


@pytest.fixture
def sample_subscriber(db):
    return Subscriber.objects.create(email="member@example.com", is_active=True)


@pytest.fixture
def approved_review(db):
    return Review.objects.create(
        member_name="Aarav Sharma",
        rating=5,
        review_text="Amazing trainers and facilities!",
        is_approved=True,
    )


@pytest.fixture
def unapproved_review(db):
    return Review.objects.create(
        member_name="Anonymous",
        rating=2,
        review_text="Needs improvement.",
        is_approved=False,
    )
