from django.urls import path
from apps.crm.admin import admin_site
from apps.crm.views.main_views import user_login, user_logout, dashboard

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('admin/', admin_site.urls)
]