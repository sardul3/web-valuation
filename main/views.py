from django.shortcuts import render

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

# Create your views here.


def homepage(request):
    return render(request, 'main/homepage.html', {})


def evaluatorhome(request):
    return render(request, 'main/evaluatorhome.html', {})

def user_login(request):
    if request.method == 'POST':
        # get the username and password from the user
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username)
        print(password)

        # django authenticates the credentials
        user = authenticate(username='s', password='s')

        if user:
            if user.is_active:
                # user is logged in and redirected to home page
                login(request, user)
                return HttpResponseRedirect(reverse('evaluatorhome'))
            else:
                return HttpResponse('Account is not active')
        # if there is no valid user
        else:
            print('someone tried to login with invalid credentials')
            return HttpResponse('Invalid username or password')
    # for someone trying to log in
    else:
        return render(request, 'registration/login.html', {})
