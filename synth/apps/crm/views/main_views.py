from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render

from apps.schedule.models import Lesson
from apps.students.models import CoinBalance, Enrollment


@login_required
def dashboard(request):
    user = request.user

    balance_obj, _ = CoinBalance.objects.get_or_create(user=user)

    groups = [e.group for e in Enrollment.objects.filter(user=user)]

    lessons = Lesson.objects.filter(group__in=groups).order_by('weekday', 'time')

    return render(request, 'dashboard/dashboard.html', {
        "user": user,
        "balance": balance_obj.balance,
        "groups": groups,
        "lessons": lessons,
    })

def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)

            return redirect('dashboard')

    return render(request, 'auth/login.html')


def user_logout(request):
    logout(request)
    return redirect('login')