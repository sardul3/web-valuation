from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'main'

urlpatterns = [
    #path('', views.homepage, name='homepage'),
    path('home', views.evaluatorhome, name='evaluatorhome'),
    path('rubric', views.rubric, name = 'rubric'),
    path('upload', views.upload, name = 'upload'),
    path('grade', views.grade, name = 'grade'),
    path('update_measure/<int:measure_id>', views.update_measure, name="update_measure"),
    path('dashboard', views.dashboard, name = 'dashboard'),
    path('newCycle', views.newCycle, name = 'newCycle'),
    path('cycle/<int:cycle_id>', views.cycle, name = 'cycle'),
    path('upload', views.upload, name='upload'),
    path('add_learning_outcome', views.add_learning_outcome, name="add_learning_outcome"),
    path('add_evaluator', views.add_evaluator, name="add_evaluator"),
    path('register', views.register, name='register'),
    path('', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout', auth_views.LogoutView.as_view(template_name='main/logout.html'), name='logout'),


]
