from django.db import models
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.contrib.auth.models import User

# ==========================================
# AUTHENTICATION & USER PROFILE
# ==========================================
class UserProfile(models.Model):
    ROLE_ADMIN = 'ADMIN'
    ROLE_TRAINER = 'TRAINER'
    ROLE_MEMBER = 'MEMBER'

    ROLE_CHOICES = (
        (ROLE_ADMIN, 'Admin'),
        (ROLE_TRAINER, 'Trainer'),
        (ROLE_MEMBER, 'Member'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_MEMBER)
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ImageField(upload_to="Static/images/profiles", null=True, blank=True)
    trainer = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='user_profiles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} ({self.role})"


# Create your models here.
class About(models.Model):
    image = models.ImageField(upload_to="Static/images", null=True, blank=True)
    head  = models.CharField(max_length=100)
    description = models.TextField(null=True)
    video_url = models.URLField(max_length=255, null=True, blank=True)
    experience_years = models.IntegerField(default=10)

    class Meta:
        verbose_name_plural = "About Us"

    def __str__(self):
        return self.head

class Team(models.Model):
    image = models.ImageField(upload_to="Static/images", null=True, blank=True) 
    name  = models.CharField(max_length=50)
    post  = models.CharField(max_length=50)
    bio   = models.TextField(null=True, blank=True)
    facebook = models.CharField(max_length=200, default="#")
    twitter = models.CharField(max_length=200, default="#")
    instagram = models.CharField(max_length=200, default="#")

    def __str__(self):
        return f"{self.name} - {self.post}"

class contacts(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=20)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name_plural = "Contacts"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.email})"

class Services(models.Model):
    image = models.ImageField(upload_to="Static/images", null=True, blank=True)
    head = models.CharField(max_length=100)
    description = models.TextField(null=True)
    icon_class = models.CharField(max_length=50, default="flaticon-002-dumbell")
    tag = models.CharField(max_length=50, default="FITNESS")

    class Meta:
        verbose_name_plural = "Services"

    def __str__(self):
        return self.head

class Membership(models.Model):
    name = models.CharField(max_length=50)
    price = models.CharField(max_length=20)
    period = models.CharField(max_length=50, default="SINGLE CLASS")
    description = models.TextField(null=True)
    features_list = models.TextField(help_text="Comma-separated features list", default="Free riding, Unlimited equipments, Personal trainer, Weight loss classes, No time restriction")
    is_popular = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.price}"

    @property
    def get_features(self):
        return [f.strip() for f in self.features_list.split(',') if f.strip()]

class Feature(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon_class = models.CharField(max_length=50, default="flaticon-034-stationary-bike")

    def __str__(self):
        return self.title

class BlogPost(models.Model):
    CATEGORY_CHOICES = [
        ('Fitness', 'Fitness'),
        ('Workout', 'Workout'),
        ('Nutrition', 'Nutrition'),
        ('Motivation', 'Motivation'),
    ]
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)
    author = models.CharField(max_length=50, default="Admin")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Fitness')
    image = models.ImageField(upload_to="Static/images", null=True, blank=True)
    snippet = models.TextField(help_text="Short description for list view")
    content = models.TextField(help_text="Full article content")
    read_time = models.CharField(max_length=20, default="5 min read")
    comments_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class GalleryItem(models.Model):
    CATEGORY_CHOICES = [
        ('workout', 'Workout'),
        ('fitness', 'Fitness'),
        ('yoga', 'Yoga'),
        ('boxing', 'Boxing'),
        ('equipment', 'Equipment'),
    ]
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='workout')
    image = models.ImageField(upload_to="Static/images", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.category})"


# ==========================================
# MODULE 1 & 2: BMI Calculator
# ==========================================
class BMIRecord(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    CATEGORY_CHOICES = [
        ('Underweight', 'Underweight'),
        ('Healthy', 'Healthy'),
        ('Overweight', 'Overweight'),
        ('Obese', 'Obese'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='bmi_records')
    name = models.CharField(max_length=50)
    height = models.FloatField(help_text="Height in cm")
    weight = models.FloatField(help_text="Weight in kg")
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    bmi_value = models.FloatField()
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - BMI: {self.bmi_value:.1f} ({self.category})"


# ==========================================
# MODULE 3: Class Booking & Attendance
# ==========================================
class GymClass(models.Model):
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    name = models.CharField(max_length=50)
    trainer = models.CharField(max_length=50)
    assigned_trainer = models.ForeignKey(
        Team, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='classes',
        help_text="Trainer (team member) this class is assigned to.",
    )
    schedule_day = models.CharField(max_length=10, choices=DAY_CHOICES)
    schedule_time = models.TimeField()
    duration_minutes = models.IntegerField(default=60)
    capacity = models.IntegerField(default=20)
    current_enrolled = models.IntegerField(default=0)
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['schedule_day', 'schedule_time']
        verbose_name_plural = "Gym Classes"

    def __str__(self):
        return f"{self.name} - {self.schedule_day} {self.schedule_time}"

    @property
    def available_slots(self):
        return self.capacity - self.current_enrolled

    @property
    def is_full(self):
        return self.current_enrolled >= self.capacity

    @property
    def occupancy_percentage(self):
        if self.capacity > 0:
            return int((self.current_enrolled / self.capacity) * 100)
        return 0


class Booking(models.Model):
    STATUS_CHOICES = [
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Pending', 'Pending'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='bookings')
    member_name = models.CharField(max_length=50)
    member_email = models.EmailField(max_length=100, null=True, blank=True)
    gym_class = models.ForeignKey(GymClass, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Confirmed')

    class Meta:
        ordering = ['-booking_date']

    def __str__(self):
        return f"{self.member_name} - {self.gym_class.name} ({self.status})"


class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='attendances')
    member_name = models.CharField(max_length=50)
    gym_class = models.ForeignKey(GymClass, on_delete=models.SET_NULL, null=True, blank=True, related_name='attendances')
    check_in_time = models.TimeField()
    check_out_time = models.TimeField(null=True, blank=True)
    date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['-date', '-check_in_time']

    def __str__(self):
        return f"{self.member_name} - {self.date}"


# ==========================================
# MODULE 4: Payment & Revenue Tracker
# ==========================================
class Payment(models.Model):
    METHOD_CHOICES = [
        ('Cash', 'Cash'),
        ('UPI', 'UPI'),
        ('Card', 'Card'),
        ('Net Banking', 'Net Banking'),
    ]
    STATUS_CHOICES = [
        ('Completed', 'Completed'),
        ('Pending', 'Pending'),
        ('Failed', 'Failed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='payments')
    member_name = models.CharField(max_length=50)
    membership = models.ForeignKey(Membership, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    method = models.CharField(max_length=15, choices=METHOD_CHOICES, default='Cash')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Completed')

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"{self.member_name} - ₹{self.amount} ({self.status})"


# ==========================================
# MODULE 5: Member Progress Tracker
# ==========================================
class WorkoutLog(models.Model):
    EXERCISE_CHOICES = [
        ('Bench Press', 'Bench Press'),
        ('Squats', 'Squats'),
        ('Deadlift', 'Deadlift'),
        ('Shoulder Press', 'Shoulder Press'),
        ('Bicep Curls', 'Bicep Curls'),
        ('Tricep Dips', 'Tricep Dips'),
        ('Lat Pulldown', 'Lat Pulldown'),
        ('Leg Press', 'Leg Press'),
        ('Lunges', 'Lunges'),
        ('Plank', 'Plank'),
        ('Running', 'Running'),
        ('Cycling', 'Cycling'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='workout_logs')
    member_name = models.CharField(max_length=50)
    exercise = models.CharField(max_length=30, choices=EXERCISE_CHOICES)
    sets = models.IntegerField(default=3)
    reps = models.IntegerField(default=10)
    weight_used = models.FloatField(help_text="Weight in kg", default=0)
    date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.member_name} - {self.exercise} ({self.date})"


class BodyMetrics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='body_metrics')
    member_name = models.CharField(max_length=50)
    body_weight = models.FloatField(help_text="Weight in kg")
    chest = models.FloatField(help_text="Chest in inches", null=True, blank=True)
    waist = models.FloatField(help_text="Waist in inches", null=True, blank=True)
    biceps = models.FloatField(help_text="Biceps in inches", null=True, blank=True)
    thighs = models.FloatField(help_text="Thighs in inches", null=True, blank=True)
    date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Body Metrics"

    def __str__(self):
        return f"{self.member_name} - {self.body_weight}kg ({self.date})"


# ==========================================
# MODULE 6: Newsletter & Notifications
# ==========================================
class Subscriber(models.Model):
    email = models.EmailField(max_length=100, unique=True)
    subscribed_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-subscribed_date']

    def __str__(self):
        return f"{self.email} ({'Active' if self.is_active else 'Inactive'})"


class Newsletter(models.Model):
    subject = models.CharField(max_length=200)
    content = models.TextField()
    sent_date = models.DateTimeField(auto_now_add=True)
    recipients_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-sent_date']

    def __str__(self):
        return f"{self.subject} ({self.sent_date.strftime('%Y-%m-%d')})"


# ==========================================
# MODULE 7: Testimonials & Reviews
# ==========================================
class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    member_name = models.CharField(max_length=50)
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    review_text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.member_name} - {self.rating} Stars"