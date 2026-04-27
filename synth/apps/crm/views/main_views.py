from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from apps.students.models import Experience
from apps.schedule.models import Lesson, Group


@login_required
def dashboard(request):
    user = request.user

    balance_obj = Experience.get_for_user(user)

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
                progress = 100 - round((total / used) * 100, 1)

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

        "balance": balance_obj.total_xp,

        "groups": groups,

        "lessons": lessons,

        "subscription": subscription,

        "used": used,

        "total": total,

        "remaining": remaining,

        "debt": debt,

        "progress": progress,  # 🔥 ВАЖНО

        "recent_attendance": recent_attendance,

        "streak": streak,

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
