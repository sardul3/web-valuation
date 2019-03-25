from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'main'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('home', views.evaluatorhome, name='evaluatorhome'),
    path('rubric', views.rubric, name = 'rubric'),
    path('grade', views.grade, name = 'grade'),
    path('dashboard', views.dashboard, name = 'dashboard'),
    path('newCycle', views.newCycle, name = 'newCycle'),
    path('cycle/<int:cycle_id>', views.cycle, name = 'cycle'),
    path('register', views.register, name='register'),
    path('login', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout', auth_views.LogoutView.as_view(template_name='main/logout.html'), name='logout'),


]
