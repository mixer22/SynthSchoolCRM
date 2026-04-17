from datetime import datetime, timedelta, time

from django.contrib.auth.hashers import make_password
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from apps.users.models import User
from apps.students.models import (
    CoinBalance,
    StudentProfile,
)
from apps.schedule.models import Lesson, Group
from apps.crm.services.coins import add_coins
from apps.crm.services.groups import add_student_to_group, remove_student_from_group
# =========================
# USER PAGE
# =========================
def user_view(admin_site, request, user_id):
    user = get_object_or_404(User, id=user_id)

    groups = Group.objects.filter(enrollments__student__user=user)

    balance_obj = CoinBalance.get_for_user(user)

    return TemplateResponse(request, "admin/user_page.html", {
        **admin_site.each_context(request),
        "user_obj": user,
        "groups": groups,
        "balance": balance_obj.balance,
    })


# =========================
# STUDENTS LIST
# =========================
def students_list_view(request, admin_site):
    age = request.GET.get("age")
    group_id = request.GET.get("group")

    students = StudentProfile.objects.select_related("user").prefetch_related("enrollments__group")

    if age:
        students = students.filter(age=age)

    if group_id:
        students = students.filter(enrollments__group_id=group_id)

    groups = Group.objects.all()
    ages = list(range(6, 19))

    return TemplateResponse(request, "admin/students_list.html", {
        **admin_site.each_context(request),
        "students": students,
        "groups": groups,
        "ages": ages,
        "selected_age": age,
        "selected_group": group_id,
    })


def create_student_view(admin_site, request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")

        age = request.POST.get("age")
        parent_name = request.POST.get("parent_name")
        parent_phone = request.POST.get("parent_phone")

        if User.objects.filter(username=username).exists():
            return render(request, "admin/create_student.html", {
                "error": "Пользователь уже существует",
                **admin_site.each_context(request)
            })

        # создаем пользователя
        user = User.objects.create(
            username=username,
            password=make_password(password),
            first_name=first_name,
            last_name=last_name,
            role='student'
        )

        # создаем профиль
        StudentProfile.objects.create(
            user=user,
            age=age if age else None,
            parent_name=parent_name,
            parent_phone=parent_phone
        )

        return redirect("/admin/students/")

    return render(request, "admin/create_student.html", {
        **admin_site.each_context(request)
    })


# =========================
# GROUPS LIST
# =========================
def groups_list_view(request, admin_site):
    groups = Group.objects.annotate(
        students_count=Count('enrollments')
    )

    lessons = Lesson.objects.select_related('group')

    lesson_map = {
        lesson.group_id: lesson
        for lesson in lessons
    }

    return TemplateResponse(request, "admin/groups_list.html", {
        **admin_site.each_context(request),
        "groups": groups,
        "lesson_map": lesson_map,
    })


# =========================
# GROUP PAGE
# =========================
def group_view(admin_site, request, group_id):
    group = get_object_or_404(Group, id=group_id)

    enrolled_students = StudentProfile.objects.filter(
        enrollments__group=group
    ).select_related('user')

    available_students = StudentProfile.objects.exclude(
        id__in=enrolled_students.values_list("id", flat=True)
    ).select_related('user')

    return TemplateResponse(request, "admin/group_page.html", {
        **admin_site.each_context(request),
        "group": group,
        "enrolled_students": enrolled_students,
        "available_students": available_students,
    })


# =========================
# ADD / REMOVE USER FROM GROUP
# =========================
def add_user(admin_site, request, group_id):
    group = get_object_or_404(Group, id=group_id)
    student_id = request.GET.get("student_id")

    student = get_object_or_404(StudentProfile, id=student_id)

    add_student_to_group(student, group)  # 🔥 FIX

    return HttpResponseRedirect(f"/admin/group/{group_id}/")



def remove_user(admin_site, request, group_id, user_id):
    student = get_object_or_404(StudentProfile, id=user_id)
    group = get_object_or_404(Group, id=group_id)

    remove_student_from_group(student, group)

    return HttpResponseRedirect(f"/admin/group/{group_id}/")


# =========================
# SCHEDULE
# =========================
def schedule_view(admin_site, request):
    days = [(i, d) for i, d in enumerate(["ПН","ВТ","СР","ЧТ","ПТ","СБ","ВС"])]

    start = datetime.strptime("10:00", "%H:%M")
    end = datetime.strptime("18:00", "%H:%M")
    step = timedelta(hours=1)

    time_slots = []
    current = start

    while current <= end:
        t = current.time()
        time_str = t.strftime("%H:%M")  # 🔥 ВАЖНО

        time_slots.append({
            "time": t,
            "time_str": time_str,  # 🔥 добавили
        })

        current += step

    lessons = Lesson.objects.select_related('group').all()

    # 🔥 ГЛАВНЫЙ ФИКС
    schedule_map = {
        f"{l.weekday}_{l.time.strftime('%H:%M')}": l
        for l in lessons
    }

    # группы, у которых уже есть урок
    busy_group_ids = Lesson.objects.values_list('group_id', flat=True)

    # только свободные группы
    groups = Group.objects.exclude(id__in=busy_group_ids)

    return TemplateResponse(request, "admin/schedule.html", {
        **admin_site.each_context(request),
        "days": days,
        "time_slots": time_slots,
        "schedule_map": schedule_map,
        "groups": groups,
    })


# =========================
# DELETE LESSON
# =========================
def delete_lesson(admin_site, request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    lesson.delete()

    return HttpResponseRedirect("/admin/schedule/")


# =========================
# COINS
# =========================
def add_coins_view(admin_site, request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        amount = int(request.POST.get("amount", 0))
        add_coins(user, amount)

    return HttpResponseRedirect(f"/admin/user/{user_id}/")


def add_lesson_view(admin_site, request):
    weekday = request.GET.get("weekday")
    time_str = request.GET.get("time")
    group_id = request.GET.get("group_id")

    if not (weekday and time_str and group_id):
        return redirect("/admin/schedule/")

    try:
        weekday = int(weekday)

        # 🔥 РУЧНОЙ ПАРСИНГ (100% работает)
        hour, minute = map(int, time_str.split(":"))
        lesson_time = time(hour, minute)

        group = Group.objects.get(id=group_id)

    except Exception as e:
        print("ERROR:", e)
        return redirect("/admin/schedule/")

    # проверка на дубликат
    lesson, created = Lesson.objects.get_or_create(
        group=group,
        weekday=weekday,
        time=lesson_time
    )

    print("CREATED:", created)

    return redirect("/admin/schedule/")

def delete_lesson(admin_site, request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    lesson.delete()
    return redirect("/admin/schedule/")

def create_group_view(admin_site, request):
    if request.method == "POST":
        name = request.POST.get("name")

        if name:
            Group.objects.create(name=name)

        return redirect("/admin/groups/")

    return TemplateResponse(request, "admin/group_create.html", {
        **admin_site.each_context(request),
    })

def delete_group(admin_site, request, group_id):
    group = get_object_or_404(Group, id=group_id)

    # безопасное удаление (сначала можно будет усложнить позже)
    group.delete()

    return redirect("/admin/groups/")
