from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import CoOrdinator,InvitedCo,tempCode

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
    code = forms.CharField(label="Code", required=True)
    def clean_email(self):
        print(self)
        email_found = False
        data = self.cleaned_data['email']
        for em in InvitedCo.objects.all():
            if em.pending:
                if em.email==data:
                    email_found = True
        if not email_found:
            raise forms.ValidationError('You must be invited to register!!')
        if email_found:
            return data


    class Meta:
        model = User
        fields = ['username', 'email', 'code','password1', 'password2']

    def save(self):
        user = super().save(commit=False)
        user.is_staff = True
        user.save()
        return user