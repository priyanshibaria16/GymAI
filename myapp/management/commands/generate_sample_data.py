"""
Django Management Command: python manage.py generate_sample_data
Seeds IronPeak Fitness Studio with realistic, on-brand content and a believable
12-month operating history (gradual member growth, organic revenue spread).
"""
import random
from datetime import datetime, timedelta
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils import timezone

from myapp.models import (
    About, Team, Services, Feature, BlogPost, GalleryItem,
    Membership, BMIRecord, GymClass, Booking,
    Attendance, Payment, WorkoutLog, BodyMetrics,
    Subscriber, Review, contacts,
)

BASE_DIR = Path(settings.BASE_DIR)
IMG_DIR = BASE_DIR / 'Static' / 'img'

random.seed(2019)  # deterministic, reproducible dataset


def img_file(relative_path):
    """Open a bundled static image as a Django File for ImageField uploads.

    The explicit ``name`` keeps uploads portable - without it Django would
    inherit the absolute Windows path of the source file.
    """
    path = IMG_DIR / relative_path
    if path.exists():
        return File(open(path, 'rb'), name=relative_path.replace('\\', '/'))
    return None


class Command(BaseCommand):
    help = 'Seeds IronPeak Fitness Studio with realistic brand content and 12 months of operating data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Seeding IronPeak Fitness Studio...'))
        now = timezone.now()

        member_names = [
            'Aarav Sharma', 'Ananya Patel', 'Rohan Mehta', 'Priya Joshi',
            'Vikram Shah', 'Neha Verma', 'Karan Gupta', 'Pooja Trivedi',
            'Rahul Desai', 'Siddharth Rao', 'Deepika Nair', 'Amit Kumar',
            'Sneha Kulkarni', 'Aditya Singh', 'Meera Reddy', 'Harsh Vora',
        ]

        # ---------------------------------------------------------------
        # 1. Brand content: About, Features, Services
        # ---------------------------------------------------------------
        self.stdout.write('Seeding brand content...')
        About.objects.all().delete()
        About.objects.create(
            head='BUILT IN 2019 TO PUSH AHMEDABAD FORWARD',
            description=(
                'IronPeak Fitness Studio opened its doors in August 2019 in a 6,000 sq ft '
                'corner of Prahlad Nagar with 40 members, second-hand racks and one belief: '
                'training should be measured, not guessed. Seven years later we are home to '
                '300+ active members, 6 certified coaches and an in-house AI layer that tracks '
                'BMI, predicts drop-off risk and plans every workout. Our mission is simple - '
                'make serious training accessible, measurable and sustainable for every body in Ahmedabad.'
            ),
            video_url='https://www.youtube.com/watch?v=ml6cT4AZdqI',
            experience_years=7,
            image=img_file('about-us.jpg'),
        )

        Feature.objects.all().delete()
        features_data = [
            ('flaticon-034-stationary-bike', 'AI-Powered Tracking',
             'BMI, BMR and churn analytics built in - your progress is measured weekly, never guessed.'),
            ('flaticon-022-dumbbell', 'Certified Coaching',
             'Six full-time coaches with national certifications and 4-9 years on the floor.'),
            ('flaticon-002-dumbell', 'Premium Equipment',
             'Imported strength racks, calibrated plates and a dedicated cardio deck - serviced monthly.'),
            ('flaticon-052-weightlifter', 'Recovery Suite',
             'Steam, sauna and stretching zone included with Premium and Elite memberships.'),
        ]
        for icon, title, desc in features_data:
            Feature.objects.create(icon_class=icon, title=title, description=desc)

        Services.objects.all().delete()
        services_data = [
            ('services-1.jpg', 'flaticon-002-dumbell', 'Personal Training', 'PERSONAL TRAINING',
             'One-on-one programming with a dedicated coach - assessment, weekly sessions and nutrition check-ins.'),
            ('services-2.jpg', 'flaticon-034-stationary-bike', 'Group Classes', 'GROUP CLASSES',
             'Power Yoga, HIIT, Zumba, CrossFit WODs and Boxing - 8+ sessions every week, booked in one click.'),
            ('services-3.jpg', 'flaticon-022-dumbbell', 'AI Fitness Reports', 'AI FITNESS',
             'BMI/BMR/TDEE analysis, macro targets and a personalised workout split generated from your goals.'),
            ('services-4.jpg', 'flaticon-052-weightlifter', 'Corporate Wellness', 'CORPORATE',
             'Team memberships, on-site assessments and flexible billing for companies around SG Highway.'),
        ]
        for image, icon, head, tag, desc in services_data:
            Services.objects.create(
                head=head, description=desc, icon_class=icon, tag=tag,
                image=img_file(f'services/{image}'),
            )

        # ---------------------------------------------------------------
        # 2. Coaches (Team)
        # ---------------------------------------------------------------
        self.stdout.write('Seeding coaches...')
        Team.objects.all().delete()
        coaches = [
            ('Priya Joshi', 'Yoga & Flexibility Coach', 'team-1.jpg',
             '8 years teaching vinyasa and mobility; leads our 6:30 AM Power Yoga bench.'),
            ('Vikram Shah', 'HIIT & Fat Loss Specialist', 'team-2.jpg',
             '6 years coaching metabolic conditioning; members average 4-6 kg loss in the first trimester.'),
            ('Rohan Mehta', 'Strength & Powerlifting Coach', 'team-3.jpg',
             '9 years on the platform; state-level powerlifter and our head of the Iron Zone.'),
            ('Karan Gupta', 'CrossFit Level-2 Coach', 'team-4.jpg',
             '5 years running WOD programming; builds the Thursday CrossFit Challenge from scratch.'),
            ('Ananya Iyer', 'Pilates & Dance Fitness Coach', 'team-5.jpg',
             '4 years across Pilates reformer and Zumba choreography; Friday nights are hers.'),
            ('Dev Chauhan', 'Boxing & Conditioning Coach', 'team-6.jpg',
             '7 years of amateur boxing; runs pad-work circuits every Saturday morning.'),
        ]
        for name, post, image, bio in coaches:
            Team.objects.create(
                name=name, post=post, bio=bio, image=img_file(f'team/{image}'),
                facebook='#', twitter='#', instagram='#',
            )

        # ---------------------------------------------------------------
        # 3. Membership plans (realistic tiered pricing)
        # ---------------------------------------------------------------
        self.stdout.write('Seeding membership plans...')
        Membership.objects.all().delete()
        memberships_data = [
            ('Student Plan', '900', 'MONTHLY', False,
             'Unrestricted student pass - valid ID required at signup.',
             'Gym floor access (off-peak), Locker room, BMI & AI fitness report, 2 group classes / month'),
            ('Basic Plan', '1200', 'MONTHLY', False,
             'Everything you need to train consistently on the floor.',
             'Full gym floor access, Locker room, Unlimited cardio deck, BMI & AI fitness report, App progress tracking'),
            ('Premium Plan', '2500', 'MONTHLY', True,
             'Our most popular plan - floor access plus the full class calendar.',
             'Everything in Basic, Unlimited group classes, 1 PT assessment / quarter, Steam & sauna access, Guest pass (1 / month)'),
            ('Elite Plan', '4000', 'MONTHLY', False,
             'All-access membership with dedicated coaching built in.',
             'Everything in Premium, 4 personal training sessions / month, Custom nutrition & macro plan, Priority class booking, Quarterly body-composition scan'),
        ]
        memberships = []
        for name, price, period, popular, desc, features in memberships_data:
            memberships.append(Membership.objects.create(
                name=name, price=price, period=period, is_popular=popular,
                description=desc, features_list=features,
            ))

        # ---------------------------------------------------------------
        # 4. BMI Records - growth weighted toward recent months
        # ---------------------------------------------------------------
        self.stdout.write('Seeding BMI records...')
        BMIRecord.objects.all().delete()
        for _ in range(75):
            days_ago = int(360 * (random.random() ** 1.6))  # recent-biased growth
            created_date = now - timedelta(days=days_ago)
            name = random.choice(member_names)
            height = round(random.uniform(152, 188), 1)
            weight = round(random.uniform(48, 102), 1)
            age = random.randint(19, 52)
            gender = random.choice(['Male', 'Male', 'Female'])

            bmi_value = round(weight / ((height / 100) ** 2), 1)
            if bmi_value < 18.5:
                cat = 'Underweight'
            elif bmi_value < 25:
                cat = 'Healthy'
            elif bmi_value < 30:
                cat = 'Overweight'
            else:
                cat = 'Obese'

            rec = BMIRecord.objects.create(
                name=name, height=height, weight=weight, age=age,
                gender=gender, bmi_value=bmi_value, category=cat,
            )
            rec.created_at = created_date
            rec.save()

        # ---------------------------------------------------------------
        # 5. Weekly class schedule
        # ---------------------------------------------------------------
        self.stdout.write('Seeding class schedule...')
        GymClass.objects.all().delete()
        classes_data = [
            ('Power Yoga', 'Priya Joshi', 'Monday', '06:30', 20, 16, 'Studio 2',
             'Flow-based vinyasa to open the week - runs Mon/Wed/Fri at 6:30 AM in Studio 2.'),
            ('HIIT Fat Burn', 'Vikram Shah', 'Tuesday', '07:30', 15, 15, 'Main Floor',
             '45 minutes of interval circuits engineered for maximum calorie burn. Tuesday and Thursday mornings.'),
            ('Strength Foundations', 'Rohan Mehta', 'Wednesday', '18:00', 18, 13, 'Iron Zone',
             'Squat, hinge, press and pull with barbell fundamentals - perfect first step into lifting.'),
            ('CrossFit WOD', 'Karan Gupta', 'Thursday', '19:00', 25, 21, 'CrossFit Bay',
             'The daily workout of the day: Olympic lifts, gymnastics and engine work, scaled to your level.'),
            ('Zumba Dance Party', 'Ananya Iyer', 'Friday', '19:00', 30, 27, 'Studio 2',
             'End the week moving - 60 minutes of choreographed dance cardio. No experience needed.'),
            ('Boxing Conditioning', 'Dev Chauhan', 'Saturday', '08:00', 16, 11, 'Combat Corner',
             'Pad-work circuits, footwork drills and core finishers. Gloves provided for your first month.'),
            ('Weekend Cardio Blast', 'Vikram Shah', 'Saturday', '17:30', 20, 14, 'Main Floor',
             'Treadmill, rower and bike intervals in a group energy - Saturday evening sweat session.'),
            ('Sunday Core & Mobility', 'Priya Joshi', 'Sunday', '09:00', 15, 8, 'Studio 2',
             'Deep core work and full-body mobility to recover before the week starts.'),
        ]
        created_classes = []
        for name, trainer, day, time_str, cap, enrolled, studio, desc in classes_data:
            created_classes.append(GymClass.objects.create(
                name=name, trainer=trainer, schedule_day=day,
                schedule_time=datetime.strptime(time_str, '%H:%M').time(),
                capacity=cap, current_enrolled=enrolled,
                description=f'{desc} ({studio}, capacity {cap}.)',
            ))

        # ---------------------------------------------------------------
        # 6. Bookings
        # ---------------------------------------------------------------
        self.stdout.write('Seeding bookings...')
        Booking.objects.all().delete()
        for gc in created_classes:
            for _ in range(random.randint(4, 9)):
                member = random.choice(member_names)
                Booking.objects.create(
                    member_name=member,
                    member_email=f"{member.lower().replace(' ', '.')}@gmail.com",
                    gym_class=gc,
                    status=random.choice(['Confirmed'] * 7 + ['Pending', 'Cancelled']),
                )

        # ---------------------------------------------------------------
        # 7. Payments - gradual growth, organic spread, plan-weighted
        # ---------------------------------------------------------------
        self.stdout.write('Seeding payments...')
        Payment.objects.all().delete()
        # older -> newer month: slow, believable growth in paying members
        monthly_volumes = [4, 5, 5, 6, 7, 7, 8, 9, 9, 11, 12, 13]
        # Premium is most popular, then Basic, Elite, Student
        plan_weights = [0.22, 0.34, 0.30, 0.14]
        methods = ['UPI'] * 5 + ['Cash'] * 2 + ['Card'] * 2 + ['Net Banking']

        for month_offset, volume in enumerate(monthly_volumes):
            for _ in range(volume):
                days_ago = random.randint(month_offset * 30, month_offset * 30 + 28)
                days_ago = min(days_ago, 360)
                membership = random.choices(memberships, weights=plan_weights, k=1)[0]
                Payment.objects.create(
                    member_name=random.choice(member_names),
                    membership=membership,
                    amount=float(membership.price),
                    payment_date=(now - timedelta(days=days_ago)).date(),
                    method=random.choice(methods),
                    status=random.choices(
                        ['Completed', 'Pending', 'Failed'], weights=[0.86, 0.10, 0.04], k=1
                    )[0],
                )

        # ---------------------------------------------------------------
        # 8. Attendance - recent 60 days, peak-biased
        # ---------------------------------------------------------------
        self.stdout.write('Seeding attendance...')
        Attendance.objects.all().delete()
        for _ in range(160):
            days_ago = int(60 * (random.random() ** 1.3))
            att_date = (now - timedelta(days=days_ago)).date()
            in_hour = random.choice([6, 7, 7, 8, 18, 19, 19, 20])  # morning & evening peaks
            in_time = datetime.strptime(f'{in_hour:02d}:{random.randint(0, 59):02d}', '%H:%M').time()
            duration_min = random.randint(45, 100)
            out_dt = datetime.combine(att_date, in_time) + timedelta(minutes=duration_min)
            Attendance.objects.create(
                member_name=random.choice(member_names),
                check_in_time=in_time,
                check_out_time=out_dt.time(),
                date=att_date,
            )

        # ---------------------------------------------------------------
        # 9. Workout logs & body metrics (visible progress arcs)
        # ---------------------------------------------------------------
        self.stdout.write('Seeding progress data...')
        WorkoutLog.objects.all().delete()
        BodyMetrics.objects.all().delete()
        exercises = ['Bench Press', 'Squats', 'Deadlift', 'Shoulder Press',
                     'Bicep Curls', 'Tricep Dips', 'Lat Pulldown', 'Leg Press']

        tracked = [
            ('Aarav Sharma', 84.5, -0.6),   # cutting: steady loss
            ('Ananya Patel', 61.0, -0.3),
            ('Rohan Mehta', 78.2, 0.25),    # bulking: slow gain
            ('Sneha Kulkarni', 68.4, -0.5),
            ('Aditya Singh', 72.9, 0.15),
            ('Meera Reddy', 58.6, -0.2),
        ]
        for name, start_weight, weekly_trend in tracked:
            weight = start_weight
            for w in range(8):
                weight += weekly_trend + random.uniform(-0.3, 0.3)
                BodyMetrics.objects.create(
                    member_name=name,
                    body_weight=round(weight, 1),
                    chest=round(random.uniform(36, 42), 1),
                    waist=round(random.uniform(29, 35), 1),
                    biceps=round(random.uniform(13, 16), 1),
                    thighs=round(random.uniform(20, 24), 1),
                    date=(now - timedelta(weeks=7 - w)).date(),
                )
            lift = random.uniform(30, 60)
            for _ in range(10):
                lift += random.uniform(0.5, 2.0)  # progressive overload
                WorkoutLog.objects.create(
                    member_name=name,
                    exercise=random.choice(exercises),
                    sets=random.choice([3, 4, 5]),
                    reps=random.choice([6, 8, 10, 12]),
                    weight_used=round(lift, 1),
                    date=(now - timedelta(days=random.randint(0, 45))).date(),
                )

        # ---------------------------------------------------------------
        # 10. Newsletter subscribers
        # ---------------------------------------------------------------
        self.stdout.write('Seeding subscribers...')
        Subscriber.objects.all().delete()
        for i, name in enumerate(member_names):
            Subscriber.objects.create(
                email=f"{name.lower().replace(' ', '.')}@gmail.com",
                is_active=(i != len(member_names) - 1),  # one churned subscriber
            )

        # ---------------------------------------------------------------
        # 11. Testimonials - specific, outcome-driven
        # ---------------------------------------------------------------
        self.stdout.write('Seeding testimonials...')
        Review.objects.all().delete()
        testimonials = [
            ('Pooja Trivedi', 5,
             "I joined the Premium plan in March and followed Vikram's HIIT program with the "
             'AI macro targets - down 8 kg in 4 months and my resting heart rate dropped from 84 to 68.'),
            ('Rahul Desai', 5,
             "Rohan rebuilt my deadlift from scratch after a back injury. 100 kg to 140 kg in "
             'seven months of Wednesday Strength Foundations, pain-free the whole way.'),
            ('Siddharth Rao', 4,
             'The churn alerts are real - the front desk called me when I skipped two weeks and '
             'honestly that call got me back. Equipment is always serviced; peak hours can get busy.'),
            ('Deepika Nair', 5,
             "As a night-shift nurse I needed flexible timing. The 5 AM to 10 PM window works for "
             'me, and the BMI report tracked my 6 kg loss better than any app I tried before.'),
            ('Harsh Vora', 5,
             'Signed up for the Student Plan at 900 rupees expecting a bare-bones gym - got the '
             'same coaches, same equipment and a Zumba class that keeps me showing up.'),
        ]
        for name, rating, text in testimonials:
            Review.objects.create(
                member_name=name, rating=rating, review_text=text, is_approved=True,
            )

        # ---------------------------------------------------------------
        # 12. Blog posts
        # ---------------------------------------------------------------
        self.stdout.write('Seeding blog posts...')
        BlogPost.objects.all().delete()
        posts = [
            ('5 Warm-Up Mistakes That Are Slowing Your Progress',
             '5-warm-up-mistakes-that-are-slowing-your-progress', 'Workout', 'Rohan Mehta',
             'Static stretching before heavy lifts, skipping shoulder prep, and four more warm-up '
             'habits our coaches see every single week on the floor.',
             'Walk into any gym at 7 AM and you will see the same warm-up: two minutes on the '
             'treadmill, one lazy arm circle, straight to the bench. At IronPeak we track injury '
             'reports across 300+ members, and the pattern is clear - most strains happen in the '
             'first working set, not the last.\n\nThe five mistakes we fix most often: (1) static '
             'stretching cold muscles instead of raising tissue temperature first, (2) skipping '
             'movement-specific ramp-up sets, (3) treating the rotator cuff as optional, (4) '
             'warming up the same way for squat day and cardio day, and (5) cutting the warm-up '
             'short when the gym is crowded.\n\nThe fix takes eight minutes: three minutes of '
             'light cardio to break a sweat, two dynamic mobility drills for the joints you will '
             'load, and two to three ramp-up sets at 40-60% of your working weight. Ask any '
             'IronPeak coach to walk you through it - it is free, and it is the cheapest injury '
             'prevention you will ever get.'),
            ('How Much Protein Do You Really Need? A Practical Guide',
             'how-much-protein-do-you-really-need', 'Nutrition', 'Ananya Iyer',
             '1.6 g per kg? 2.2 g? We break down the research into numbers you can actually hit '
             'with a Gujarati kitchen.',
             'Every supplement shop in Ahmedabad has an answer; very few are backed by evidence. '
             'The research consensus for members training 3-5 times a week sits between 1.6 and '
             '2.2 grams of protein per kilogram of body weight per day, with the higher end '
             'useful during a calorie deficit.\n\nFor a 70 kg member cutting weight, that is '
             'roughly 110-150 g of protein daily. In practical terms: a bowl of dal is about '
             '9 g, a paneer bhurji serving around 20 g, four egg whites 14 g, and a scoop of '
             'whey 24 g. You do not need exotic foods - you need a plan and consistency.\n\nOur '
             'AI fitness report on the BMI page already calculates your personal protein, carb '
             'and fat targets from your weight and goal. Bring those numbers to any coach and '
             'they will translate them into meals you actually eat.'),
            ('The 20-Minute HIIT Protocol Our Coaches Swear By',
             'the-20-minute-hiit-protocol-our-coaches-swear-by', 'Workout', 'Vikram Shah',
             'Short on time? This is the exact interval structure behind our sold-out Tuesday '
             'HIIT Fat Burn sessions.',
             'The Tuesday 7:30 AM HIIT Fat Burn class has been full for three months straight, '
             'and the format is simple enough to run anywhere. Total time: 20 minutes.\n\n'
             'Structure: 40 seconds of work, 20 seconds of transition, eight stations, two '
             'rounds. Stations we rotate: battle ropes, rower sprints, kettlebell swings, ski '
             'erg, box step-ups, medicine ball slams, bike sprints and burpees. Heart rate '
             'target during work intervals: 85-92% of max.\n\nWhy it works: intensity, not '
             'duration, drives the afterburn effect. Two focused rounds beat forty minutes of '
             'half-effort jogging for calorie expenditure per minute. Try it twice a week for '
             'four weeks and watch your AI fitness report - the TDEE and body-weight trends do '
             'not lie.'),
            ('Strength Training After 30: What Changes and What Doesn’t',
             'strength-training-after-30', 'Fitness', 'Rohan Mehta',
             'Recovery slows, tendons take longer to adapt - but muscle growth absolutely does '
             'not stop. What members over 30 should adjust.',
             'The most common myth we hear at the front desk: "I missed the window." You did '
             'not. Members who start lifting at 35-50 at IronPeak add measurable strength '
             'every single quarter - our progress tracker data confirms it.\n\nWhat actually '
             'changes: recovery takes 24-48 hours longer than it did at 20, tendons adapt more '
             'slowly than muscle, and sleep quality becomes the biggest performance variable. '
             'What does not change: the stimulus-response mechanism of muscle growth, the '
             'benefits of progressive overload, or the importance of showing up.\n\nOur '
             'adjustments for members over 30: an extra rest day between heavy sessions, '
             'deload weeks every sixth week, warm-ups treated as mandatory, and volume '
             'progressed slowly. Strength after 30 is absolutely buildable - it is just earned '
             'with patience instead of recklessness.'),
            ('Sleep Is a Workout: Why Recovery Determines Your Results',
             'sleep-is-a-workout-recovery-guide', 'Motivation', 'Priya Joshi',
             'Members sleeping under 6 hours lose 60% more of their weight from muscle instead '
             'of fat. The recovery case for 7-8 hours.',
             'We can program your training, calculate your macros and track every rep - but we '
             'cannot out-train your sleep habits. Research on calorie-restricted adults shows '
             'that sleeping 5.5 hours versus 8.5 hours shifts weight loss away from fat and '
             'toward lean muscle, even with identical diet and training.\n\nFor our members the '
             'practical markers are simple: 7-8 hours per night, a consistent wake time, no '
             'caffeine after 4 PM, and screens out of the bedroom in the final hour. Morning '
             '6:30 AM class regulars tend to self-correct quickly because nobody makes a 6 AM '
             'yoga class on four hours of sleep twice.\n\nIf your progress stalls for two '
             'weeks, check your training and diet first - then check your sleep. It is the '
             'third pillar, and at IronPeak we track it in every coaching conversation.'),
        ]
        for title, slug, category, author, snippet, content in posts:
            BlogPost.objects.create(
                title=title, slug=slug, category=category, author=author,
                snippet=snippet, content=content,
                read_time=f'{max(3, len(content.split()) // 200)} min read',
                comments_count=random.randint(2, 18),
                created_at=now - timedelta(days=random.randint(3, 90)),
            )

        # ---------------------------------------------------------------
        # 13. Gallery captions
        # ---------------------------------------------------------------
        self.stdout.write('Seeding gallery...')
        GalleryItem.objects.all().delete()
        gallery_items = [
            ('Free-weight zone during the evening peak', 'equipment', 'gallery-1.jpg'),
            ('Power Yoga flow, Monday 6:30 AM batch', 'yoga', 'gallery-2.jpg'),
            ('Thursday CrossFit WOD - barbell cycling', 'workout', 'gallery-3.jpg'),
            ('New imported racks arriving, 2025', 'equipment', 'gallery-4.jpg'),
            ('Zumba Dance Party, Friday night full house', 'workout', 'gallery-5.jpg'),
            ('Member milestone board - 100 kg club', 'fitness', 'gallery-6.jpg'),
            ('Boxing Conditioning pad work, Combat Corner', 'boxing', 'gallery-7.jpg'),
            ('Annual member meetup & strongman demo', 'fitness', 'gallery-8.jpg'),
            ('Cardio deck overlooking the main floor', 'equipment', 'gallery-9.jpg'),
        ]
        for title, category, image in gallery_items:
            GalleryItem.objects.create(
                title=title, category=category, image=img_file(f'gallery/{image}'),
            )

        # ---------------------------------------------------------------
        # 14. Contact inquiries
        # ---------------------------------------------------------------
        if contacts.objects.count() == 0:
            self.stdout.write('Seeding contact inquiries...')
            inquiries = [
                ('Kunal Bhatt', 'kunal.bhatt@gmail.com', '9825011432',
                 'Do you offer couple discounts on the Premium plan?'),
                ('Ritika Shah', 'ritika.shah@outlook.com', '9978645210',
                 'Looking for morning yoga batches near Prahlad Nagar.'),
                ('Manoj Panchal', 'manoj.panchal@yahoo.com', '9879312456',
                 'Corporate wellness enquiry for a 25-person team at SG Highway.'),
            ]
            for name, email, phone, comment in inquiries:
                contacts.objects.create(name=name, email=email, phone=phone, comment=comment)

        self.stdout.write(self.style.SUCCESS(
            'IronPeak Fitness Studio seeded: brand content, 4 plans, 8 weekly classes, '
            '12 months of payments and a full operating history.'
        ))
