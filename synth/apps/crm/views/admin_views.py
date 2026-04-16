from datetime import datetime, timedelta

from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect

from apps.users.models import User
from apps.students.models import CoinBalance
from apps.schedule.models import Lesson, Group

from apps.crm.services.coins import add_coins
from apps.crm.services.groups import add_user_to_group, remove_user_from_group


def user_view(admin_site, request, user_id):
    user = get_object_or_404(User, id=user_id)

    groups = Group.objects.filter(enrollment__user=user)
    balance_obj, _ = CoinBalance.objects.get_or_create(user=user)

    return TemplateResponse(request, "admin/user_page.html", {
        **admin_site.each_context(request),
        "user_obj": user,
        "groups": groups,
        "balance": balance_obj.balance,
    })


def students_list_view(request, admin_site):
    students = User.objects.filter(role='student')

    # ===== ФИЛЬТРЫ =====
    age = request.GET.get("age")
    group_id = request.GET.get("group")

    if age:
        students = students.filter(age=age)

    if group_id:
        students = students.filter(enrollment__group_id=group_id)

    # оптимизация
    students = students.prefetch_related(
        "enrollment_set__group"
    ).select_related(
        "student_profile"  # 🔥 теперь правильно
    )

    groups = Group.objects.all()
    ages = list(range(6, 19))  # 🔥 фикс вместо split

    context = {
        **admin_site.each_context(request),
        "students": students,
        "groups": groups,
        "ages": ages,
        "selected_age": age,
        "selected_group": group_id,
    }

    return TemplateResponse(request, "admin/students_list.html", context)


def groups_list_view(request, admin_site):
    groups = Group.objects.annotate(
        students_count=Count('enrollment')
    )

    lessons = Lesson.objects.select_related('group')

    lesson_map = {
        lesson.group_id: lesson
        for lesson in lessons
    }

    context = {
        **admin_site.each_context(request),  # ✅ вот так
        "groups": groups,
        "lesson_map": lesson_map,
    }

    return TemplateResponse(request, "admin/groups_list.html", context)


def group_view(admin_site, request, group_id):
    group = get_object_or_404(Group, id=group_id)

    enrolled_users = User.objects.filter(enrollment__group=group)

    all_users = User.objects.filter(role='student').exclude(
        id__in=enrolled_users.values_list('id', flat=True)
    )

    return TemplateResponse(request, "admin/group_page.html", {
        **admin_site.each_context(request),
        "group": group,
        "enrolled_users": enrolled_users,
        "all_users": all_users,
    })


def add_user(admin_site, request, group_id):
    group = get_object_or_404(Group, id=group_id)
    user_id = request.GET.get("user_id")

    user = get_object_or_404(User, id=user_id)

    add_user_to_group(user, group)

    return HttpResponseRedirect(f"/admin/group/{group_id}/")


def remove_user(admin_site, request, group_id, user_id):
    remove_user_from_group(user_id, group_id)
    return HttpResponseRedirect(f"/admin/group/{group_id}/")


def schedule_view(admin_site, request):
    days = [
        (0, "ПН"),
        (1, "ВТ"),
        (2, "СР"),
        (3, "ЧТ"),
        (4, "ПТ"),
        (5, "СБ"),
        (6, "ВС"),
    ]

    start = datetime.strptime("10:00", "%H:%M")
    end = datetime.strptime("18:00", "%H:%M")
    step = timedelta(minutes=60)

    time_slots = []
    current = start

    while current <= end:
        t = current.time()

        time_slots.append({
            "time": t,
            "key": f"{t.hour}_{t.minute:02d}"
        })

        current += step

    lessons = Lesson.objects.select_related('group').all()

    schedule_map = {}
    for lesson in lessons:
        key = f"{lesson.weekday}_{lesson.time.hour}_{lesson.time.minute:02d}"
        schedule_map[key] = lesson

    return TemplateResponse(request, "admin/schedule.html", {
        **admin_site.each_context(request),
        "days": days,
        "time_slots": time_slots,
        "schedule_map": schedule_map,
    })


def delete_lesson(admin_site, request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    lesson.delete()

    return HttpResponseRedirect("/admin/schedule/")


def add_coins_view(admin_site, request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        amount = int(request.POST.get("amount", 0))
        add_coins(user, amount)

    return HttpResponseRedirect(f"/admin/user/{user_id}/")