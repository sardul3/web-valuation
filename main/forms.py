from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import CoOrdinator

class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self):
        user = super().save(commit=False)
        user.is_staff = False
        user.save()
        return user

class CoOrdinatorRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    department = forms.CharField(label="Department",required=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2','department']

    def save(self):
        user = super().save(commit=False)
        user.is_staff = True
        user.save()
        return user