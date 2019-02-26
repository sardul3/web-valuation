from django.shortcuts import render

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Rubric, Student, Measure, Category
# Create your views here.


def homepage(request):
    return render(request, 'main/homepage.html', {})


def evaluatorhome(request):
    rubrics = Rubric.objects.all()
    students = Student.objects.all()
    context = {'rubrics':rubrics, 'students':students}

    return render(request, 'main/evaluatorhome.html', context)

def rubric(request):
    if request.method == "POST":
        created_by = request.POST.get('created_by')
        title = request.POST.get('title')
        category = request.POST.get('category')
        measure = request.POST.get('measure')
        measureText = request.POST.get('measureText')
        weight = request.POST.get('weight')

        rubric = Rubric(created_by=created_by, title=title, category=Category(categoryTitle=category, measure=Measure(measureTitle=measure, measureText=measureText,weight=weight)))
        rubric.save()

        rubrics = Rubric.objects.filter(title=title)
        context = {'rubrics':rubrics}

        return render(request, 'main/rubric.html', context)
    return render(request, 'main/rubric.html')


def grade(request):
    rubrics = Rubric.objects.all()

    measures = Measure.objects.all()
    students = Student.objects.all()
    context = {'rubrics':rubrics, 'students': students, 'measures':measures}
    if request.method == 'POST':
        score = request.POST.get('score')
        print(score)
    return render(request, 'main/evaluatorrubric.html',context)
