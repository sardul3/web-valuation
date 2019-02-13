from django.shortcuts import render

# Create your views here.


def homepage(request):
    return render(request, 'main/homepage.html', {})


def evaluatorhome(request):
    return render(request, 'main/evaluatorhome.html', {})



