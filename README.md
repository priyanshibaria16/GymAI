# 🏋️ IronPeak Fitness Studio — Enterprise Gym Management & AI Engine

[![Django](https://img.shields.io/badge/Django-5.0+-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3+-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![pytest](https://img.shields.io/badge/pytest-8.0+-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)

**IronPeak Fitness Studio** is a full-stack, enterprise-grade Gym Management System built with **Django 5** and enhanced with an **AI/ML Engine**. It delivers comprehensive operational tracking, financial analytics, automated reporting, membership churn risk prediction, a personalized AI fitness recommender, and an NLP-powered virtual assistant chatbot.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Key Features & Modules](#-key-features--modules)
- [Machine Learning & AI Architecture](#-machine-learning--ai-architecture)
- [Technology Stack](#-technology-stack)
- [Directory Structure](#-directory-structure)
- [Installation & Quickstart Guide](#-installation--quickstart-guide)
- [Running the Application](#-running-the-application)
- [Testing & Quality Assurance](#-testing--quality-assurance)
- [API & Route Reference](#-api--route-reference)
- [API Keys & Integrations](#-api-keys--integrations)
- [Database Schema & Models](#-database-schema--models)
- [Custom Management Commands](#-custom-management-commands)
- [License & Credits](#-license--credits)

### 🔒 Production-Grade Auth & Role-Based Access Control (RBAC)
- **Role Isolation**: 3 strict roles (`ADMIN`, `TRAINER`, `MEMBER`).
  - **ADMIN**: Full access to all dashboards, user management, financial ledgers, Stripe payments, and CSV data export endpoints.
  - **TRAINER**: Access to trainer dashboard, assigned classes, assigned members, and attendance tracking. Restricted from financial reports.
  - **MEMBER**: Self-service member dashboard, personal progress tracking, class booking, and BMI calculators. IDOR-protected data isolation.
- **Central Dashboard Router (`/dashboard/`)**: Automatically routes users to their role dashboard (`/admin-dashboard/`, `/trainer-dashboard/`, `/member-dashboard/`).
- **User Management (`/admin/users/`)**: Dedicated Admin User Management interface to edit profiles, assign roles, toggle active status, and protect against demoting/deactivating the last active Admin.
- **Pre-Seeded Demo Accounts**:
  - **Admin**: `admin_demo` / `Admin@123456`
  - **Trainer**: `trainer_demo` / `Trainer@123456`
  - **Member**: `member_demo` / `Member@123456`

All cloud-service credentials are loaded from a local **`.env`** file (see `.env.example`) via `python-dotenv` and read in `gym/settings.py`. **No real keys are ever stored in source code, templates, static assets, or this README.** The `.env` file is listed in `.gitignore` and must never be committed.

| Service | API Key Constant | Where It Lives | Purpose |
|---|---|---|---|
| **Grok AI** | `GROK_API_KEY` | `.env` (git-ignored) | Hyper-realistic LLM responses for GymBot Chatbot |
| **Google Gemini** | `GEMINI_API_KEY` | `.env` (git-ignored) | Process automation for personalized member health directives |
| **Stripe Gateway** | `STRIPE_PUBLISHABLE_KEY` / `STRIPE_SECRET_KEY` | `.env` (git-ignored) | Credit/Debit Card payment gateway integration |

> 🔑 **Setup:** copy `.env.example` to `.env` and paste your own secret values. Rotate any key that may have been shared publicly.


---

## 🌟 Overview

IronPeak Fitness Studio solves real-world gym management challenges by combining traditional administrative management (bookings, billing, attendance, progress logs) with predictive machine learning insights. Administrators gain complete operational oversight through dynamic analytics dashboards, while gym members enjoy interactive self-service tools like AI-driven fitness regime generators and an intelligent NLP chatbot.

---

## 🚀 Key Features & Modules

### 1. 📊 Executive Analytics Dashboard (`/dashboard/`)
- **Real-Time KPIs**: Total active members, monthly revenue, average class occupancy, and churn risk percentage.
- **Interactive Visualizations (Chart.js)**:
  - Monthly New Member Acquisition Trends.
  - Revenue Breakdown by Membership Tier & Payment Method.
  - Class Popularity & Attendance Metrics.
  - Member BMI Category Demographics.
  - ML Churn Risk Distribution Gauge.

### 2. 🧮 AI BMI & Fitness Recommender (`/bmi_calculator`)
- **Mifflin-St Jeor Engine**: Calculates accurate Basal Metabolic Rate (BMR) and Total Daily Energy Expenditure (TDEE).
- **Personalized Macro Split**: Calculates protein, carbohydrate, and fat targets in grams based on goals (*Weight Loss, Muscle Gain, Endurance, Maintenance*).
- **Custom Training Regimes**: Generates recommended cardio schedules, strength splits, and AI-tailored lifestyle insights.
- **Record History**: Automatically stores BMI records for tracking member health progression over time.

### 3. 📅 Class Booking & Attendance Management (`/class-timetable/`)
- **Interactive Schedule**: View weekly classes across Yoga, HIIT, CrossFit, Boxing, and Strength.
- **Slot Reservation**: Automated real-time capacity management preventing overbooking.
- **Check-In/Check-Out Tracking**: Log member attendance times for operational frequency auditing.

### 4. 💳 Payment & Revenue Tracker (`/payment-dashboard/`)
- **Financial Ledger**: Track payments categorized by cash, UPI, card, or net banking.
- **Status Filtering**: Filter by Completed, Pending, and Failed transactions.
- **Membership Revenue Analysis**: Calculate total revenue earned per membership plan (*Student, Basic, Premium, Elite*).

### 5. 🏋️ Member Progress & Body Metrics Tracker (`/member-progress/`)
- **Workout Logs**: Record exercise type, sets, reps, weight used (kg), and date.
- **Body Measurement Tracking**: Monitor body weight, chest, waist, biceps, and thigh measurements.
- **Growth Visualization**: Graphical tracking of physical progression over time.

### 6. 🤖 Intelligent NLP Chatbot (`/chatbot/`)
- **TF-IDF & Cosine Similarity Matcher**: Powered by `scikit-learn` to process natural language user inquiries.
- **Instant Answers**: Resolves queries regarding gym hours, membership prices, trainers, class timetables, location, and equipment.
- **Rule-Based Fallback**: Keyword-weighted backup matcher ensuring reliable responses even with complex user queries.

### 7. 📤 Automated Data Export & Reports (`/reports/`)
- One-click CSV export endpoints for management auditing:
  - Members Export (`/export/members/`)
  - Payments Export (`/export/payments/`)
  - Attendance Export (`/export/attendance/`)
  - BMI Records Export (`/export/bmi/`)
  - Class Bookings Export (`/export/bookings/`)

### 8. 🌐 Public Portal & Content Management
- **Landing Page (`/`)**: Hero section, service highlights, membership plans, trainer profiles, and member reviews.
- **Blog (`/blog`)**: Fitness articles, category filtering, reading time estimates, and article view pages.
- **Gallery (`/gallery`)**: Categorized photo gallery (Workout, Yoga, Boxing, Equipment).
- **Newsletter (`/subscribe/`)**: Email subscription system with activate/deactivate capability.

---

## 🧠 Machine Learning & AI Architecture

```
                          ┌──────────────────────────┐
                          │    Django Application    │
                          └─────────────┬────────────┘
                                        │
           ┌────────────────────────────┼────────────────────────────┐
           ▼                            ▼                            ▼
┌──────────────────────┐    ┌──────────────────────┐    ┌──────────────────────┐
│  ML Churn Predictor  │    │  Fitness Recommender │    │     NLP Chatbot      │
├──────────────────────┤    ├──────────────────────┤    ├──────────────────────┤
│ • Random Forest      │    │ • Mifflin-St Jeor BMR│    │ • TF-IDF Vectorizer  │
│ • LogisticRegression │    │ • TDEE Multipliers   │    │ • Cosine Similarity  │
│ • Predicts churn %   │    │ • Goal Macro Split   │    │ • Keyword Matcher    │
└──────────────────────┘    └──────────────────────┘    └──────────────────────┘
```

### 1. Membership Churn Predictor (`myapp/ai_engine/churn_predictor.py`)
- **Algorithm**: `RandomForestClassifier` (with fallback to `LogisticRegression`).
- **Input Features**: `[attendance_per_wk, days_inactive, tenure_months, pending_dues_flag]`.
- **Output**: Risk probability percentage, Risk Level (*Low, Medium, High*), and targeted retention recommendations (e.g., discount offers or personal trainer consultations).

#### 🧬 Model Confusion Matrix (Churn Classifier)

Performance was measured with **5-fold stratified cross-validation** on the model's
150-member training cohort (`RandomForestClassifier(n_estimators=50)`, `random_state=42`).
The **positive class is “Will churn”**, since detecting at-risk members is the goal.

| Actual \ Predicted | Retained (0) | Will Churn (1) | Total |
|---|---|---|---|
| **Retained (0)** | **TN** 62 | **FP** 6 | 68 |
| **Will Churn (1)** | **FN** 12 | **TP** 70 | 82 |
| **Total** | 74 | 76 | 150 |

**Derived metrics**

| Metric | Formula | Value |
|---|---|---|
| **Accuracy** | (TP + TN) / Total | **88.0%** |
| **Precision** | TP / (TP + FP) | **92.1%** |
| **Recall (Sensitivity)** | TP / (TP + FN) | **85.4%** |
| **F1-Score** | 2 · P · R / (P + R) | **88.6%** |
| **Specificity** | TN / (TN + FP) | **91.2%** |

> 📌 **Interpretation:** The high **precision (92.1%)** means that when the model flags a
> member as “will churn”, it is correct ~9 out of 10 times — so retention outreach effort is
> rarely wasted. The **recall (85.4%)** confirms it still catches the large majority of true
> churners. *Note: the in-sample fit reported in the app (`94.2%`) is measured on the full
> training set; the table above is the more realistic out-of-sample cross-validated result.*

### 2. NLP Chatbot Engine (`myapp/ai_engine/nlp_chatbot.py`)
- **Vectorization**: `TfidfVectorizer` converts natural language queries into term-frequency vectors.
- **Similarity Measure**: `cosine_similarity` compares input vectors against intent knowledge base embeddings.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Backend Framework** | Django 5.x (Python 3.10+) |
| **Machine Learning** | scikit-learn, NumPy |
| **Media & Images** | Pillow |
| **Database** | SQLite3 |
| **Testing** | Pytest, pytest-django |
| **Frontend** | HTML5, CSS3, JavaScript, Chart.js, Flaticon |
| **Server** | Django WSGI / ASGI Development Server |

---

## 📁 Directory Structure

```
gym/
├── db.sqlite3                         # SQLite Database
├── manage.py                          # Django Management CLI
├── pytest.ini                         # Pytest configuration
├── requirements.txt                   # Dependencies manifest
├── smoke_check.ps1                    # Endpoint validation script
├── venv/                              # Virtual Environment
├── gym/                               # Project Configuration Root
│   ├── settings.py                    # App settings & middleware configuration
│   ├── urls.py                        # Root URL router
│   ├── wsgi.py                        # WSGI entry point
│   └── asgi.py                        # ASGI entry point
├── myapp/                             # Core Application Module
│   ├── admin.py                       # Django Admin models configuration
│   ├── apps.py                        # App configuration
│   ├── forms.py                       # Form validation classes
│   ├── models.py                      # Database schema & ORM models
│   ├── views.py                       # Public page views
│   ├── views_ai.py                    # AI BMI & Chatbot views
│   ├── views_booking.py               # Booking & Timetable views
│   ├── views_dashboard.py             # Analytics Dashboard view
│   ├── views_newsletter.py            # Subscriber management views
│   ├── views_payment.py               # Payment ledger views
│   ├── views_progress.py              # Member progress views
│   ├── views_reports.py               # CSV export views
│   ├── views_review.py                # Testimonials & review views
│   ├── ai_engine/                     # Machine Learning Core
│   │   ├── churn_predictor.py         # ML Churn Prediction model
│   │   ├── fitness_recommender.py     # BMR/TDEE & Macro logic
│   │   └── nlp_chatbot.py             # TF-IDF Cosine Chatbot
│   └── management/
│       └── commands/
│           └── generate_sample_data.py# Database Seeder script
├── Static/                            # Static Assets (CSS, JS, Images, Fonts)
├── Template/                          # HTML Templates
└── tests/                             # Automated Test Suite (195 Tests)
    ├── conftest.py
    ├── test_churn_predictor.py
    ├── test_fitness_recommender.py
    ├── test_nlp_chatbot.py
    ├── test_models.py
    ├── test_views_ai.py
    ├── test_views_booking_payment.py
    ├── test_views_dashboard.py
    ├── test_views_modules.py
    ├── test_views_public.py
    └── test_views_reports.py
```

---

## 📥 Installation & Quickstart Guide

### 1. Prerequisites
- **Python 3.10+** installed on your system.
- **PowerShell** (Windows) or **Bash** (macOS/Linux).

### 2. Clone / Open Workspace
Navigate to the project root directory:
```powershell
cd "c:\Users\DELL\Downloads\Gym\internship project\gym"
```

### 3. Virtual Environment Setup
Create and activate a virtual environment:
```powershell
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
Install all required packages from `requirements.txt`:
```powershell
pip install -r requirements.txt
```

### 5. Apply Database Migrations
Initialize the SQLite database schema:
```powershell
python manage.py migrate
```

### 6. Seed Sample Data
Populate the database with realistic demo data, plans, trainers, transactions, and 12-month operating logs:
```powershell
python manage.py generate_sample_data
```

---

## 🚀 Running the Application

### Launch Development Server
Start the Django development server on port `8017`:
```powershell
python manage.py runserver 127.0.0.1:8017
```

Once running, access the application in your web browser:
- 🌐 **Public Website**: [http://127.0.0.1:8017/](http://127.0.0.1:8017/)
- 📊 **Analytics Dashboard**: [http://127.0.0.1:8017/dashboard/](http://127.0.0.1:8017/dashboard/)
- 🧮 **AI BMI & Fitness Recommender**: [http://127.0.0.1:8017/bmi_calculator](http://127.0.0.1:8017/bmi_calculator)
- 🤖 **AI Chatbot**: [http://127.0.0.1:8017/chatbot/](http://127.0.0.1:8017/chatbot/)
- 📅 **Class Timetable & Booking**: [http://127.0.0.1:8017/class_timetable](http://127.0.0.1:8017/class_timetable)
- 💳 **Payment Ledger**: [http://127.0.0.1:8017/payment-dashboard/](http://127.0.0.1:8017/payment-dashboard/)
- 🏋️ **Member Progress**: [http://127.0.0.1:8017/member-progress/](http://127.0.0.1:8017/member-progress/)
- 📋 **Reports & Exports**: [http://127.0.0.1:8017/reports/](http://127.0.0.1:8017/reports/)
- ⚙️ **Django Admin Portal**: [http://127.0.0.1:8017/admin/](http://127.0.0.1:8017/admin/)

---

## 🧪 Testing & Quality Assurance

The codebase includes an extensive **pytest** test suite with **195 automated tests** covering models, AI components, views, forms, and CSV reporting endpoints.

### Execute Automated Test Suite
Run tests with verbosity:
```powershell
python -m pytest
```

### Run Endpoint Smoke Test Script
While the development server is active on `127.0.0.1:8017`, execute `smoke_check.ps1` to verify HTTP status codes:
```powershell
powershell.exe -ExecutionPolicy Bypass -File .\smoke_check.ps1
```

---

## 🔗 API & Route Reference

| URL Path | View Function | Method | Description |
|---|---|---|---|
| `/` | `views.index` | GET | Public Home & Landing Page |
| `/about` | `views.about_us` | GET | About IronPeak Fitness Studio |
| `/services` | `views.services` | GET | Gym Services & Features |
| `/team` | `views.team` | GET | Trainers & Coaching Staff |
| `/gallery` | `views.gallery` | GET | Photo Gallery |
| `/blog` | `views.blog` | GET | Fitness Articles & Blog |
| `/blog_details/<id>/` | `views.blog_details` | GET | Full Article Detail View |
| `/contact` | `views.contact` | GET / POST | Contact Us Form |
| `/dashboard/` | `views_dashboard.dashboard` | GET | Operational Analytics & ML Dashboard |
| `/bmi_calculator` | `views_ai.ai_bmi_calculator` | GET / POST | AI BMI, BMR, TDEE & Macro Calculator |
| `/chatbot/` | `views_ai.chatbot_page` | GET | Interactive AI Chatbot Page |
| `/api/chatbot/` | `views_ai.chatbot_api` | POST | Chatbot JSON API Endpoint |
| `/class-timetable/` | `views_booking.class_timetable` | GET | Class Schedule & Availability |
| `/book-class/<id>/` | `views_booking.book_class` | POST | Reserve Slot in Gym Class |
| `/payment-dashboard/` | `views_payment.payment_dashboard` | GET | Revenue Ledger & Payment Tracking |
| `/member-progress/` | `views_progress.member_progress` | GET | Workouts & Body Metrics Tracker |
| `/add-workout/` | `views_progress.add_workout` | POST | Log New Exercise Session |
| `/add-metrics/` | `views_progress.add_metrics` | POST | Record Body Measurements |
| `/testimonials/` | `views_review.testimonials` | GET / POST | Member Reviews & Testimonials |
| `/subscribe/` | `views_newsletter.subscribe` | POST | Newsletter Email Subscription |
| `/unsubscribe/` | `views_newsletter.unsubscribe` | POST | Newsletter Unsubscribe |
| `/reports/` | `views_reports.reports_page` | GET | Data Export Dashboard |
| `/export/members/` | `views_reports.export_members_csv` | GET | Download Members CSV |
| `/export/payments/` | `views_reports.export_payments_csv` | GET | Download Payments CSV |
| `/export/attendance/` | `views_reports.export_attendance_csv` | GET | Download Attendance CSV |
| `/export/bmi/` | `views_reports.export_bmi_csv` | GET | Download BMI History CSV |
| `/export/bookings/` | `views_reports.export_bookings_csv` | GET | Download Class Bookings CSV |

---

## 🗄️ Database Schema & Models

The system relies on 17 Django ORM models defined in `myapp/models.py`:

- **`About`**: Brand narrative, experience years, video highlight URL.
- **`Team`**: Trainers, designations, bios, and social media handles.
- **`Services`**: Offered gym programs and icon classes.
- **`Membership`**: Pricing plans, features, and duration periods.
- **`Feature`**: Gym amenities and highlights.
- **`BlogPost`**: Articles, categories, authors, and reading times.
- **`GalleryItem`**: Categorized fitness photos.
- **`BMIRecord`**: Calculated BMI, height, weight, gender, and category logs.
- **`GymClass`**: Class names, trainers, schedules, capacity, and current enrollments.
- **`Booking`**: Member class reservations and confirmation statuses.
- **`Attendance`**: Check-in and check-out timestamps per member.
- **`Payment`**: Transaction amounts, dates, payment methods, and statuses.
- **`WorkoutLog`**: Exercises, sets, reps, and weights lifted.
- **`BodyMetrics`**: Body weight, chest, waist, biceps, and thigh measurements.
- **`Subscriber`**: Newsletter email subscriber registry.
- **`Newsletter`**: Sent email newsletters and broadcast logs.
- **`Review`**: Member ratings, reviews, and moderation flags.

---

## 🛠️ Custom Management Commands

### `generate_sample_data`
Seeds the database with brand content, trainers, classes, and 12 months of realistic operational history:
```powershell
python manage.py generate_sample_data
```

### Superuser Creation
Create an admin user to manage data via `/admin/`:
```powershell
python manage.py createsuperuser
```

---

## 📜 License & Credits

- **Framework**: Developed with [Django 5](https://www.djangoproject.com/).
- **AI/ML Libraries**: [scikit-learn](https://scikit-learn.org/) & [NumPy](https://numpy.org/).
- **Icons & Styling**: Flaticon & Custom Responsive CSS framework.
- **Project**: IronPeak Fitness Studio Internship Project.
