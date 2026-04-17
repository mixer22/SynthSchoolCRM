from django.urls import path

from apps.crm.admin_site import admin_site
from apps.crm.views.main_views import dashboard, user_login, user_logout


urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),

    # custom crm admin
    path('admin/', admin_site.urls),
]