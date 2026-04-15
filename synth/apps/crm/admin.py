from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.crm.admin_site import admin_site

from apps.users.models import User
from apps.students.models import Enrollment, CoinBalance, Transaction
from apps.schedule.models import Group, Lesson


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


@admin.register(Lesson, site=admin_site)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('group', 'weekday', 'time')

    def response_add(self, request, obj, post_url_continue=None):
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect("/admin/schedule/")


@admin.register(CoinBalance, site=admin_site)
class CoinBalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance')


@admin.register(Transaction, site=admin_site)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'created_at')