from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'main'

urlpatterns = [
    #path('', views.homepage, name='homepage'),
    path('home', views.evaluatorhome, name='evaluatorhome'),

    path('test_rubric/', views.test_rubric, name = 'test_rubric'),
    path('created_test_rubric/', views.created_test_rubric, name = 'created_test_rubric'),
    path('rubric_render/', views.rubric_render, name = 'rubric_render'),

    path('upload', views.upload, name = 'upload'),
    path('grade', views.grade, name = 'grade'),
    path('add_rubric_to_measure/<int:measure_id>', views.add_rubric_to_measure, name = 'add_rubric_to_measure'),
    path('add_test_to_measure/<int:measure_id>', views.add_test_to_measure, name = 'add_test_to_measure'),
    path('update_measure/<int:measure_id>', views.update_measure, name="update_measure"),
    path('new_measure/<int:outcome_id>', views.new_measure, name="new_measure"),
    path('delete_measure/<int:measure_id>', views.delete_measure, name="delete_measure"),
    path('dashboard', views.dashboard, name = 'dashboard'),
    path('newCycle', views.newCycle, name = 'newCycle'),
    path('cycle/<int:cycle_id>', views.cycle, name = 'cycle'),
    path('upload', views.upload, name='upload'),
    path('add_learning_outcome/<int:cycle_id>', views.add_learning_outcome, name="add_learning_outcome"),
    path('add_evaluator', views.add_evaluator, name="add_evaluator"),
    path('register', views.register, name='register'),
    path('', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout', auth_views.LogoutView.as_view(template_name='main/logout.html'), name='logout'),


]
