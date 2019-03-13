from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('home', views.evaluatorhome, name='evaluatorhome'),
    path('rubric', views.rubric, name = 'rubric'),
    path('grade', views.grade, name = 'grade'),
    path('dashboard', views.dashboard, name = 'dashboard'),
    path('newCycle', views.newCycle, name = 'newCycle'),

]
