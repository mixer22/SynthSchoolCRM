from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from apps.students.models import Experience
from apps.schedule.models import Lesson, Group


@login_required
def dashboard(request):
    user = request.user

    balance_obj = Experience.get_for_user(user)

    total_xp = balance_obj.total_xp if balance_obj else 0

    level = total_xp // 1000
    xp_in_level = total_xp % 1000
    xp_percent = int((xp_in_level / 1000) * 100) if total_xp else 0
    xp_left = 1000 - xp_in_level

    student = getattr(user, "student_profile", None)

    lessons = []

    groups = []

    subscription = None

    recent_attendance = []

    used = 0

    total = 0

    remaining = 0

    debt = 0

    progress = 0

    streak = 0

    if student:

        lessons = (

            Lesson.objects

            .filter(group__enrollments__student=student)

            .select_related("group")

            .distinct()

            .order_by("weekday", "time")

        )

        groups = (

            Group.objects

            .filter(enrollments__student=student)

            .distinct()

        )

        subscription = (

            student.subscriptions

            .filter(is_active=True)

            .order_by("-created_at")

            .first()

        )

        if subscription:

            used = subscription.used_lessons

            total = subscription.total_lessons

            remaining = max(total - used, 0)

            debt = max(used - total, 0)

            # ✅ НОРМАЛЬНЫЙ ПРОГРЕСС

            if total > 0:
                progress = int((used / total) * 100)

        # =========================

        # 📊 ATTENDANCE

        # =========================

        attendances = student.attendances.order_by("-date")

        recent_attendance = attendances[:12][::-1]

        # streak (подряд present/late начиная с последнего дня)

        for att in attendances:

            if att.status in ["present", "late"]:

                streak += 1

            else:

                break

    return render(request, "dashboard/dashboard.html", {

        "user": user,

        "balance": total_xp,

        "level": level,
        "xp_in_level": xp_in_level,
        "xp_percent": xp_percent,
        "xp_left": xp_left,

        "groups": groups,
        "lessons": lessons,

        "subscription": subscription,

        "used": used,
        "total": total,
        "remaining": remaining,
        "debt": debt,

        "progress": progress,

        "recent_attendance": recent_attendance,
        "streak": streak,
    })

LEVEL_REWARDS = {
    1: "🎉 Старт",
    5: "🍫 Сладость",
    10: "🎁 Стикеры",
    20: "👕 Мерч",
    30: "🎓 Сертификат",
}

@login_required
def levels_page(request):
    user = request.user
    xp = Experience.get_for_user(user)

    total_xp = xp.total_xp if xp else 0
    level = total_xp // 1000

    return render(request, "dashboard/levels.html", {
        "level": level,
        "total_xp": total_xp,
        "rewards": LEVEL_REWARDS
    })

@login_required
def payment_page(request):
    student = request.user.student_profile

    subscription = (
        student.subscriptions
        .filter(is_active=True)
        .order_by("-created_at")
        .first()
    )

    return render(request, "dashboard/payment.html", {
        "subscription": subscription
    })


def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            # 🔥 УМНАЯ РОУТИНГ ЛОГИКА
            if user.role == "teacher":
                return redirect('/admin/')  # позже можно teacher dashboard

            return redirect(request.GET.get('next') or 'dashboard')

        return render(request, 'auth/login.html', {
            "error": "Неверный логин или пароль"
        })

    return render(request, 'auth/login.html')


def user_logout(request):
    logout(request)
    return redirect('login')
