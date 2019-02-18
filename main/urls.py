from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('home', views.evaluatorhome, name='evaluatorhome'),
    path('login', views.user_login, name = 'user_login'),
    
]
