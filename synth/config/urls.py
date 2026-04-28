from django.urls import path

from apps.crm.admin_site import admin_site
from apps.crm.views.main_views import dashboard, user_login, user_logout, payment_page, levels_page


urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path("payment/", payment_page, name="payment"),
    path("levels/", levels_page, name="levels"),

    # custom crm admin
    path('admin/', admin_site.urls),
]