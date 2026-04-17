from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from apps.schedule.models import Lesson, Group
from apps.students.models import CoinBalance, StudentProfile


@login_required
def dashboard(request):
    user = request.user

    balance = CoinBalance.get_for_user(user)

    # 🔥 через Enrollment → StudentProfile
    try:
        student_profile = user.student_profile
    except StudentProfile.DoesNotExist:
        student_profile = None

    if student_profile:
        lessons = (
            Lesson.objects
            .filter(group__enrollments__student=student_profile)
            .select_related('group')
            .distinct()
            .order_by('weekday', 'time')
        )

        groups = (
            Group.objects
            .filter(enrollments__student=student_profile)
            .distinct()
        )
    else:
        lessons = Lesson.objects.none()
        groups = Group.objects.none()

    return render(request, 'dashboard/dashboard.html', {
        "user": user,
        "balance": balance.balance,
        "groups": groups,
        "lessons": lessons,
    })


from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect


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