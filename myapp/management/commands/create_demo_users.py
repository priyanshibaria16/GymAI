from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from myapp.models import UserProfile, GymClass, Booking, WorkoutLog, BodyMetrics, Payment, BMIRecord

class Command(BaseCommand):
    help = 'Creates default demo accounts for Admin, Trainer, and Member roles'

    def handle(self, *args, **options):
        # 1. Admin Demo User
        admin_user, created = User.objects.get_or_create(
            username='admin_demo',
            defaults={
                'email': 'admin@ironpeak.in',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        admin_user.set_password('Admin@123456')
        admin_user.save()
        admin_profile, _ = UserProfile.objects.get_or_create(user=admin_user)
        admin_profile.role = UserProfile.ROLE_ADMIN
        admin_profile.phone = '+91 98765 00001'
        admin_profile.save()
        self.stdout.write(self.style.SUCCESS("['ADMIN'] Account created/updated: admin_demo / Admin@123456"))

        # 2. Trainer Demo User
        trainer_user, created = User.objects.get_or_create(
            username='trainer_demo',
            defaults={
                'email': 'trainer@ironpeak.in',
                'first_name': 'Trainer',
                'last_name': 'Coach',
                'is_staff': True,
                'is_superuser': False
            }
        )
        trainer_user.set_password('Trainer@123456')
        trainer_user.save()
        trainer_profile, _ = UserProfile.objects.get_or_create(user=trainer_user)
        trainer_profile.role = UserProfile.ROLE_TRAINER
        trainer_profile.phone = '+91 98765 00002'
        trainer_profile.save()
        self.stdout.write(self.style.SUCCESS("['TRAINER'] Account created/updated: trainer_demo / Trainer@123456"))

        # 3. Member Demo User
        member_user, created = User.objects.get_or_create(
            username='member_demo',
            defaults={
                'email': 'member@ironpeak.in',
                'first_name': 'Demo',
                'last_name': 'Member',
                'is_staff': False,
                'is_superuser': False
            }
        )
        member_user.set_password('Member@123456')
        member_user.save()
        member_profile, _ = UserProfile.objects.get_or_create(user=member_user)
        member_profile.role = UserProfile.ROLE_MEMBER
        member_profile.phone = '+91 98765 00003'
        member_profile.save()
        self.stdout.write(self.style.SUCCESS("['MEMBER'] Account created/updated: member_demo / Member@123456"))

        # Link sample records to demo member if available
        gym_class = GymClass.objects.first()
        if gym_class:
            Booking.objects.get_or_create(
                user=member_user,
                gym_class=gym_class,
                defaults={
                    'member_name': member_user.get_full_name(),
                    'member_email': member_user.email,
                    'status': 'CONFIRMED'
                }
            )

        WorkoutLog.objects.get_or_create(
            user=member_user,
            exercise='Bench Press',
            defaults={
                'member_name': member_user.get_full_name(),
                'sets': 4,
                'reps': 10,
                'weight_used': 60.0,
            }
        )

        BMIRecord.objects.get_or_create(
            user=member_user,
            defaults={
                'name': member_user.get_full_name(),
                'height': 175.0,
                'weight': 70.0,
                'age': 25,
                'gender': 'Male',
                'bmi_value': 22.86,
                'category': 'Normal weight'
            }
        )

        self.stdout.write(self.style.SUCCESS("Demo users setup completed successfully."))
