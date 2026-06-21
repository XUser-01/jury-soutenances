from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
   path('admin/', admin.site.urls),
    path('admin/planning/', lambda request: __import__('django.shortcuts', fromlist=   ['redirect']).redirect('/session/1/planning/'), name='admin_planning'),
    path('login/', auth_views.LoginView.as_view(template_name='planification/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('', include('planification.urls')),
]