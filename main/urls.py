from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'main'

urlpatterns = [
    #path('', views.homepage, name='homepage'),
    path('home', views.evaluatorhome, name='evaluatorhome'),
    path('rubric/', views.new_rubric, name = 'rubric'),
    path('new_rubric', views.new_rubric, name = 'new_rubric'),
    path('upload', views.upload, name = 'upload'),
    path('grade', views.grade, name = 'grade'),
    path('add_rubric_to_measure/<int:measure_id>', views.add_rubric_to_measure, name = 'add_rubric_to_measure'),
    path('add_test_to_measure/<int:measure_id>', views.add_test_to_measure, name = 'add_test_to_measure'),
    path('update_measure/<int:measure_id>', views.update_measure, name="update_measure"),
    path('new_measure/<int:outcome_id>', views.new_measure, name="new_measure"),
    path('dashboard', views.dashboard, name = 'dashboard'),
    path('newCycle', views.newCycle, name = 'newCycle'),
    path('cycle/<int:cycle_id>', views.cycle, name = 'cycle'),
    path('upload', views.upload, name='upload'),
    path('add_learning_outcome/<int:outcome_id>', views.add_learning_outcome, name="add_learning_outcome"),
    path('add_evaluator', views.add_evaluator, name="add_evaluator"),
    path('register', views.register, name='register'),
    path('', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout', auth_views.LogoutView.as_view(template_name='main/logout.html'), name='logout'),


]
