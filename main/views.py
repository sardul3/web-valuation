from django.shortcuts import render

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Rubric, Student, Measure, Category, evaluate_rubric, Evaluator, Outcome, Cycle
# Create your views here.


def homepage(request):
    return render(request, 'main/homepage.html', {})


def evaluatorhome(request):
    rubrics = Rubric.objects.all()
    students = Student.objects.all()
    evaluatons = evaluate_rubric.objects.all()
    context = {'rubrics':rubrics, 'students':students, 'evaluations':evaluatons}

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
    evaluations = evaluate_rubric.objects.all()
    context = {'rubrics':rubrics, 'students': students, 'measures':measures, 'evaluations':evaluations}

    if request.method == 'POST':
        rubrics = Rubric.objects.all()
        measures = Measure.objects.all()
        students = Student.objects.all()
        evaluated_student = request.POST.get('student_dd',None)
        evaluated_rubric = request.POST.get('rubric_dd',None)
        decimal_place = request.POST.get('decimal_dd', None)

        scores = []
        sum = 0
        for i in range(len(measures)):
            score = request.POST.get('score'+str(i+1))
            sum+=int(score)
            average = sum/len(measures)
            average = round(average,int(decimal_place))

        evaluation = evaluate_rubric(rubric=evaluated_rubric, grade_score=average, student=evaluated_student)
        evaluation.save()

        context = {'rubrics':rubrics, 'students': students, 'measures':measures,
                    'avg':average, 'evaluations':evaluations }

        return render(request, 'main/evaluatorhome.html', context)

    return render(request, 'main/evaluatorrubric.html',context)

def dashboard(request):
    rubrics = Rubric.objects.all()
    evaluators = Evaluator.objects.all()
    outcomes = Outcome.objects.all()
    cycles = Cycle.objects.all()
    notifications = evaluate_rubric.objects.all()

    context = {'rubrics':rubrics, 'evaluators': evaluators, 'outcomes': outcomes,
                'cycles': cycles, 'notifications':notifications}
    return render(request, 'main/adminhome.html', context)

def newCycle(request):
    year = request.POST.get('year')
    semester = request.POST.get('semester')

    cycle = Cycle(year=year, semester=semester)
    cycle.save()

    return HttpResponseRedirect(reverse('main:dashboard'))
