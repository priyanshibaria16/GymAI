from django import forms
from myapp.models import (
    BMIRecord, Booking, GymClass, WorkoutLog, 
    BodyMetrics, Subscriber, Review, Team
)


class BMICalculatorForm(forms.Form):
    """Form for BMI Calculator - uses simple form (not ModelForm) for flexibility"""
    name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'Your Name',
            'class': 'form-control'
        })
    )
    height = forms.FloatField(
        widget=forms.NumberInput(attrs={
            'placeholder': 'Height / cm',
            'class': 'form-control',
            'min': '50',
            'max': '300',
            'step': '0.1'
        })
    )
    weight = forms.FloatField(
        widget=forms.NumberInput(attrs={
            'placeholder': 'Weight / kg',
            'class': 'form-control',
            'min': '10',
            'max': '500',
            'step': '0.1'
        })
    )
    age = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'placeholder': 'Age',
            'class': 'form-control',
            'min': '5',
            'max': '120'
        })
    )
    gender = forms.ChoiceField(
        choices=[('', 'Select Gender')] + BMIRecord.GENDER_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )


class BookingForm(forms.Form):
    """Form for booking a gym class"""
    member_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'Your Name',
            'class': 'form-control'
        })
    )
    member_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Your Email (optional)',
            'class': 'form-control'
        })
    )


class WorkoutLogForm(forms.ModelForm):
    """Form for logging workouts"""
    class Meta:
        model = WorkoutLog
        fields = ['member_name', 'exercise', 'sets', 'reps', 'weight_used', 'date']
        widgets = {
            'member_name': forms.TextInput(attrs={
                'placeholder': 'Your Name',
                'class': 'form-control'
            }),
            'exercise': forms.Select(attrs={
                'class': 'form-control'
            }),
            'sets': forms.NumberInput(attrs={
                'placeholder': 'Sets',
                'class': 'form-control',
                'min': '1'
            }),
            'reps': forms.NumberInput(attrs={
                'placeholder': 'Reps',
                'class': 'form-control',
                'min': '1'
            }),
            'weight_used': forms.NumberInput(attrs={
                'placeholder': 'Weight (kg)',
                'class': 'form-control',
                'min': '0',
                'step': '0.5'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }


class BodyMetricsForm(forms.ModelForm):
    """Form for recording body measurements"""
    class Meta:
        model = BodyMetrics
        fields = ['member_name', 'body_weight', 'chest', 'waist', 'biceps', 'thighs', 'date']
        widgets = {
            'member_name': forms.TextInput(attrs={
                'placeholder': 'Your Name',
                'class': 'form-control'
            }),
            'body_weight': forms.NumberInput(attrs={
                'placeholder': 'Body Weight (kg)',
                'class': 'form-control',
                'min': '20',
                'step': '0.1'
            }),
            'chest': forms.NumberInput(attrs={
                'placeholder': 'Chest (inches)',
                'class': 'form-control',
                'step': '0.1'
            }),
            'waist': forms.NumberInput(attrs={
                'placeholder': 'Waist (inches)',
                'class': 'form-control',
                'step': '0.1'
            }),
            'biceps': forms.NumberInput(attrs={
                'placeholder': 'Biceps (inches)',
                'class': 'form-control',
                'step': '0.1'
            }),
            'thighs': forms.NumberInput(attrs={
                'placeholder': 'Thighs (inches)',
                'class': 'form-control',
                'step': '0.1'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }


class SubscriberForm(forms.ModelForm):
    """Form for newsletter subscription"""
    class Meta:
        model = Subscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter your email...',
                'class': 'form-control',
                'style': 'background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: #fff;'
            })
        }


class ReviewForm(forms.ModelForm):
    """Form for submitting testimonials/reviews"""
    class Meta:
        model = Review
        fields = ['member_name', 'rating', 'review_text']
        widgets = {
            'member_name': forms.TextInput(attrs={
                'placeholder': 'Your Name',
                'class': 'form-control'
            }),
            'rating': forms.Select(attrs={
                'class': 'form-control'
            }),
            'review_text': forms.Textarea(attrs={
                'placeholder': 'Share your experience...',
                'class': 'form-control',
                'rows': 4
            }),
        }


# ==========================================
# AUTHENTICATION & USER MANAGEMENT FORMS
# ==========================================
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from myapp.models import UserProfile

class CustomSignupForm(forms.Form):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-control'}))
    username = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email Address', 'class': 'form-control'}))
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'placeholder': 'Phone Number', 'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'}), required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'form-control'}), required=True)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get('password')
        confirm_pwd = cleaned_data.get('confirm_password')

        if pwd and confirm_pwd and pwd != confirm_pwd:
            self.add_error('confirm_password', "Passwords do not match.")

        if pwd:
            try:
                validate_password(pwd)
            except forms.ValidationError as error:
                self.add_error('password', error)

        return cleaned_data


class CustomLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username or Email', 'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'}))


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    profile_image = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control-file'}))

    class Meta:
        model = UserProfile
        fields = ['phone', 'profile_image']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email


class UserManagementForm(forms.Form):
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))


class RoleChangeForm(forms.Form):
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))


class GymClassForm(forms.ModelForm):
    """Admin form to create/edit a gym class and assign it to a trainer (Team member)."""
    class Meta:
        model = GymClass
        fields = ['name', 'assigned_trainer', 'schedule_day', 'schedule_time',
                  'duration_minutes', 'capacity', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'ip-input', 'placeholder': 'e.g. HIIT Fat Burn'}),
            'assigned_trainer': forms.Select(attrs={'class': 'ip-input'}),
            'schedule_day': forms.Select(attrs={'class': 'ip-input'}),
            'schedule_time': forms.TimeInput(attrs={'class': 'ip-input', 'type': 'time'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'ip-input', 'min': '5', 'placeholder': '60'}),
            'capacity': forms.NumberInput(attrs={'class': 'ip-input', 'min': '1', 'placeholder': '20'}),
            'description': forms.Textarea(attrs={'class': 'ip-input', 'rows': 3, 'placeholder': 'Class description (optional)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_trainer'].queryset = Team.objects.all().order_by('name')
        self.fields['assigned_trainer'].empty_label = '— Unassigned —'
        self.fields['assigned_trainer'].required = False
        self.fields['capacity'].initial = self.fields['capacity'].initial or 20

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Keep the legacy text field in sync so all existing templates keep working.
        if instance.assigned_trainer:
            instance.trainer = instance.assigned_trainer.name
        elif not instance.trainer:
            instance.trainer = 'Staff'
        if commit:
            instance.save()
        return instance

