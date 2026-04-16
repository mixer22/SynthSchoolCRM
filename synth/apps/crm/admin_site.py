from django.contrib import admin
from django.urls import path

from apps.crm.views import admin_views


class CustomAdminSite(admin.AdminSite):
    site_header = "SINT CRM"
    site_title = "SINT Admin"
    index_title = "Управление школой"

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path('schedule/', self.admin_view(self.wrap(admin_views.schedule_view))),
            path('group/<int:group_id>/', self.admin_view(self.wrap(admin_views.group_view))),
            path('group/<int:group_id>/add-user/', self.admin_view(self.wrap(admin_views.add_user))),
            path('group/<int:group_id>/remove-user/<int:user_id>/', self.admin_view(self.wrap(admin_views.remove_user))),
            path('groups/', self.admin_view(lambda request: admin_views.groups_list_view(request, self)), name="groups_list"),
            path('user/<int:user_id>/', self.admin_view(self.wrap(admin_views.user_view))),
            path('lesson/<int:lesson_id>/delete/', self.admin_view(self.wrap(admin_views.delete_lesson))),
            path('user/<int:user_id>/add-coins/', self.admin_view(self.wrap(admin_views.add_coins_view))),
            path('students/', self.admin_view(lambda request: admin_views.students_list_view(request, self)), name="students_list"),
        ]

        return custom_urls + urls

    def wrap(self, view):
        def wrapper(request, *args, **kwargs):
            return view(self, request, *args, **kwargs)
        return wrapper


admin_site = CustomAdminSite(name='custom_admin')