from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from ..students.models import User, CoinBalance, Enrollment, Transaction
from ..schedule.models import Lesson, Group


class CustomAdminSite(admin.AdminSite):
    site_header = "SINT CRM"
    site_title = "SINT Admin"
    index_title = "Управление школой"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('schedule/', self.admin_view(self.schedule_view), name="schedule"),
            path('group/<int:group_id>/', self.admin_view(self.group_view), name="group_view"),
            path('group/<int:group_id>/add-user/', self.admin_view(self.add_user_to_group), name="group_add_user"),
            path('group/<int:group_id>/remove-user/<int:user_id>/', self.admin_view(self.remove_user_from_group),
                 name="group_remove_user"),
            path('user/<int:user_id>/', self.admin_view(self.user_view), name="user_view"),
            path('lesson/<int:lesson_id>/delete/', self.admin_view(self.delete_lesson), name="delete_lesson"),
            path('user/<int:user_id>/add-coins/', self.admin_view(self.add_coins), name="add_coins"),
        ]
        return custom_urls + urls

    def user_view(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        groups = Group.objects.filter(enrollment__user=user)

        balance_obj, _ = CoinBalance.objects.get_or_create(user=user)

        return TemplateResponse(request, "admin/user_page.html", {
            **self.each_context(request),
            "user_obj": user,
            "groups": groups,
            "balance": balance_obj.balance,
        })

    def group_view(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)

        enrolled_users = User.objects.filter(enrollment__group=group)
        all_users = User.objects.all()

        return TemplateResponse(request, "admin/group_page.html", {
            **self.each_context(request),
            "group": group,
            "enrolled_users": enrolled_users,
            "all_users": all_users,
        })

    def add_user_to_group(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        user_id = request.GET.get("user_id")

        user = get_object_or_404(User, id=user_id)

        Enrollment.objects.get_or_create(user=user, group=group)

        return HttpResponseRedirect(f"/admin/group/{group_id}/")

    def remove_user_from_group(self, request, group_id, user_id):
        Enrollment.objects.filter(group_id=group_id, user_id=user_id).delete()
        return HttpResponseRedirect(f"/admin/group/{group_id}/")

    def schedule_view(self, request):
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
                "key": f"{t.hour}_{t.minute:02d}"  # ВАЖНО
            })

            current += step

        lessons = Lesson.objects.select_related('group').all()

        schedule_map = {}
        for lesson in lessons:
            key = f"{lesson.weekday}_{lesson.time.hour}_{lesson.time.minute:02d}"
            schedule_map[key] = lesson

        context = {
            **self.each_context(request),
            "days": days,
            "time_slots": time_slots,
            "schedule_map": schedule_map,
        }

        return TemplateResponse(request, "admin/schedule.html", context)

    def delete_lesson(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        lesson.delete()
        return HttpResponseRedirect("/admin/schedule/")

    def add_coins(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        balance, _ = CoinBalance.objects.get_or_create(user=user)

        if request.method == "POST":
            amount = int(request.POST.get("amount", 0))

            balance.balance += amount
            balance.save()

        return HttpResponseRedirect(f"/admin/user/{user_id}/")

    def index(self, request, extra_context=None):
        context = {
            **self.each_context(request),
        }
        return TemplateResponse(request, "admin/index.html", context)


admin_site = CustomAdminSite(name='custom_admin')


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 1


@admin.register(User, site=admin_site)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Дополнительно", {
            "fields": ("age", "role", "phone", "notes")
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Дополнительно", {
            "fields": ("age", "role", "phone")
        }),
    )

    list_display = ('username', 'email', 'is_active', 'role')


@admin.register(Group, site=admin_site)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [EnrollmentInline]


@admin.register(Enrollment, site=admin_site)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'group')
    def has_module_permission(self, request):
        return False

@admin.register(Lesson, site=admin_site)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('group', 'weekday', 'time')
    list_filter = ('group', 'weekday')

    def response_add(self, request, obj, post_url_continue=None):
        return HttpResponseRedirect("/admin/schedule/")

    def response_change(self, request, obj):
        return HttpResponseRedirect("/admin/schedule/")


@admin.register(CoinBalance, site=admin_site)
class CoinBalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance')


@admin.register(Transaction, site=admin_site)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'created_at')
    def has_module_permission(self, request):
        return False