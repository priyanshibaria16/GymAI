"""
Admin AI Automations for IronPeak Fitness Studio.

Two automations are provided, each powered by Gemini with a deterministic
local fallback so the admin UI always renders useful output even when the
API key or network is unavailable:

  1. generate_executive_briefing() -> an AI-written daily operations briefing.
  2. generate_retention_drafts()   -> personalized outreach drafts for at-risk
                                      (High churn) members.

A tiny in-process TTL cache avoids hammering the API on every page refresh.
"""
import re
import time
from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone

from myapp.models import (
    User, UserProfile, Payment, Booking, Attendance, GymClass, BMIRecord,
)
from myapp.ai_engine import gemini_client
from myapp.views_ai import get_churn_prediction_data

# ---- simple in-process cache -------------------------------------------------
_CACHE = {}
_CACHE_TTL = 300  # seconds


def _cached(key, func, force=False, ttl=_CACHE_TTL):
    now = time.time()
    entry = _CACHE.get(key)
    if not force and entry and (now - entry["ts"]) < ttl:
        return entry["val"]
    value = func()
    _CACHE[key] = {"ts": now, "val": value}
    return value


def clear_cache():
    """Mostly used by tests / manual refresh."""
    _CACHE.clear()


# ---- metrics -----------------------------------------------------------------
def gather_executive_metrics():
    """Aggregate the numbers used to build the briefing/retention prompts."""
    now = timezone.now()
    month_ago = now - timedelta(days=30)

    total_revenue = Payment.objects.filter(status="Completed").aggregate(
        t=Sum("amount"))["t"] or 0
    month_revenue = Payment.objects.filter(
        status="Completed", payment_date__gte=month_ago.date()).aggregate(
        t=Sum("amount"))["t"] or 0
    pending_revenue = Payment.objects.filter(status="Pending").aggregate(
        t=Sum("amount"))["t"] or 0

    capacity = GymClass.objects.aggregate(c=Sum("capacity"))["c"] or 0
    enrolled = GymClass.objects.aggregate(e=Sum("current_enrolled"))["e"] or 0
    occupancy_pct = round((enrolled / capacity) * 100, 1) if capacity else 0.0

    churn = get_churn_prediction_data()
    dist = churn.get("risk_distribution", {})

    return {
        "generated_at": now.strftime("%d %b %Y, %H:%M"),
        "total_members": UserProfile.objects.filter(role="MEMBER").count(),
        "active_members": User.objects.filter(
            profile__role="MEMBER", is_active=True).count(),
        "total_trainers": UserProfile.objects.filter(role="TRAINER").count(),
        "total_users": User.objects.count(),
        "total_revenue": total_revenue,
        "month_revenue": month_revenue,
        "pending_revenue": pending_revenue,
        "total_bookings": Booking.objects.count(),
        "month_bookings": Booking.objects.filter(booking_date__gte=month_ago).count(),
        "attendance_month": Attendance.objects.filter(date__gte=month_ago.date()).count(),
        "total_classes": GymClass.objects.count(),
        "occupancy_pct": occupancy_pct,
        "bmi_records": BMIRecord.objects.count(),
        "churn": churn,
        "high_risk": dist.get("High", 0),
        "medium_risk": dist.get("Medium", 0),
        "low_risk": dist.get("Low", 0),
    }


# ---- Automation 1: Executive Daily Briefing ---------------------------------
_BRIEFING_SYSTEM = (
    "You are the senior operations analyst for IronPeak Fitness Studio, a gym "
    "management platform. Write clear, concise, professional executive briefings "
    "for the gym owner. Never invent numbers that are not provided."
)


def _briefing_fallback(m):
    top_risk = m["churn"]["at_risk_members"][:3]
    risk_names = ", ".join(x["name"] for x in top_risk) or "none flagged"
    lines = [
        f"IronPeak daily briefing for {m['generated_at']}.",
        f"Membership: {m['active_members']} active of {m['total_members']} members "
        f"and {m['total_trainers']} trainers on staff ({m['total_users']} total accounts).",
        f"Finance: ₹{m['month_revenue']} collected this month, ₹{m['total_revenue']} "
        f"lifetime, with ₹{m['pending_revenue']} still pending.",
        f"Engagement: {m['month_bookings']} bookings this month, "
        f"{m['attendance_month']} check-ins, class occupancy at {m['occupancy_pct']}%.",
        f"Retention: {m['high_risk']} high-risk, {m['medium_risk']} medium-risk members. "
        f"Highest concern: {risk_names}.",
        "Priority actions: (1) Contact the high-risk members listed with renewal offers; "
        "(2) chase pending payments to protect this month's revenue; "
        "(3) review low-occupancy classes and reschedule or promote them.",
    ]
    return "\n".join(lines)


def _build_briefing(force=False):
    m = gather_executive_metrics()
    prompt = (
        "Write an executive daily briefing (max ~180 words) for the gym owner using "
        "ONLY these metrics. Structure it as: Overall health, Revenue, "
        "Engagement, Retention risk, and 3 prioritized action items.\n\n"
        f"Generated: {m['generated_at']}\n"
        f"Active members: {m['active_members']} / total members: {m['total_members']}\n"
        f"Trainers: {m['total_trainers']} | Total accounts: {m['total_users']}\n"
        f"Revenue this month: ₹{m['month_revenue']} | Lifetime completed: ₹{m['total_revenue']} "
        f"| Pending dues: ₹{m['pending_revenue']}\n"
        f"Bookings this month: {m['month_bookings']} | Attendance check-ins (30d): {m['attendance_month']}\n"
        f"Active classes: {m['total_classes']} | Average occupancy: {m['occupancy_pct']}%\n"
        f"Churn risk — High: {m['high_risk']}, Medium: {m['medium_risk']}, Low: {m['low_risk']}\n"
        f"Top at-risk members: "
        + ", ".join(
            f"{x['name']} ({x['risk_probability']}%, {x['days_inactive']}d inactive)"
            for x in m["churn"]["at_risk_members"][:5]
        )
    )
    result = gemini_client.generate_text(prompt, system=_BRIEFING_SYSTEM, temperature=0.4)
    if result["ok"]:
        return {"text": result["text"], "source": "gemini",
                "model": result["model"], "error": "", "metrics": m}
    return {"text": _briefing_fallback(m), "source": "fallback",
            "model": result.get("model", ""), "error": result.get("error", ""),
            "metrics": m}


def generate_executive_briefing(force=False):
    return _cached("executive_briefing", lambda: _build_briefing(force), force=force)


# ---- Automation 2: Retention Action Drafts ----------------------------------
def _retention_fallback_message(name, days_inactive, offer, pending_amount):
    pending_line = (
        f" Your account currently has ₹{pending_amount} in dues we can help sort out."
        if pending_amount else ""
    )
    return (
        f"Hi {name}, it's been {days_inactive} days since we last saw you at IronPeak "
        f"and we'd love to get you back! {offer}{pending_line} Reply YES and we'll set "
        f"up a free session with your trainer."
    )


def _build_retention_drafts(force=False):
    m = gather_executive_metrics()
    high_risk = [
        x for x in m["churn"]["at_risk_members"] if x["risk_level"] == "High"
    ]
    drafts = []
    for member in high_risk:
        name = member["name"]
        pending = Payment.objects.filter(
            member_name__iexact=name, status="Pending").aggregate(
            t=Sum("amount"))["t"] or 0
        drafts.append({
            "name": name,
            "risk_probability": member["risk_probability"],
            "days_inactive": member["days_inactive"],
            "attendance_per_wk": member["attendance_per_wk"],
            "tenure_months": member["tenure_months"],
            "pending_amount": pending,
            "recommended_offer": member["recommendation"],
            "message": _retention_fallback_message(
                name, member["days_inactive"],
                f"So we're offering: {member['recommendation']}." if member["recommendation"]
                else "Come back with a special renewal offer.",
                pending,
            ),
            "personalized": False,
        })

    if not drafts:
        return {"drafts": [], "source": "gemini" if gemini_client.is_configured() else "fallback",
                "error": "", "metrics": m}

    # Ask Gemini once for personalized one-liners, mapped back by name.
    listing = "\n".join(
        f"- {d['name']} | inactive {d['days_inactive']} days | "
        f"pending dues ₹{d['pending_amount']} | offer: {d['recommended_offer']}"
        for d in drafts
    )
    prompt = (
        "Write ONE short (max 35 words), warm, persuasive WhatsApp retention message "
        "for each at-risk gym member below. Reference how long they've been away and, "
        "when present, the pending dues and the offer. Output EXACTLY one line per "
        "member in this format and nothing else:\n"
        "NAME||message\n\nMembers:\n" + listing
    )
    result = gemini_client.generate_text(
        prompt, system=_BRIEFING_SYSTEM, temperature=0.6)
    if result["ok"]:
        mapping = {}
        for line in re.split(r"[\r\n]+", result["text"]):
            if "||" in line:
                key, msg = line.split("||", 1)
                mapping[key.strip().lower()] = msg.strip()
        for d in drafts:
            text = mapping.get(d["name"].strip().lower())
            if text:
                d["message"] = text
                d["personalized"] = True
        return {"drafts": drafts, "source": "gemini", "error": "", "metrics": m}

    return {"drafts": drafts, "source": "fallback",
            "error": result.get("error", ""), "metrics": m}


def generate_retention_drafts(force=False):
    return _cached("retention_drafts", lambda: _build_retention_drafts(force), force=force)
