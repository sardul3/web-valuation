from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Rubric, Student, Measure, Category, evaluate_rubric, Evaluator, Outcome, Cycle
from django.contrib import messages
from .forms import RegisterForm
from num2words import num2words
# Create your views here.



def homepage(request):
    return render(request, 'main/homepage.html', {})

@login_required
def evaluatorhome(request):
    rubrics = Rubric.objects.all()
    students = Student.objects.all()
    evaluatons = evaluate_rubric.objects.all()
    context = {'rubrics':rubrics, 'students':students, 'evaluations':evaluatons}

    return render(request, 'main/evaluatorhome.html', context)

@login_required
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

@login_required
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

@login_required
def dashboard(request):
    rubrics = Rubric.objects.all()
    evaluators = Evaluator.objects.all()
    outcomes = Outcome.objects.all()
    cycles = Cycle.objects.all()
    notifications = evaluate_rubric.objects.all()

    context = {'rubrics':rubrics, 'evaluators': evaluators, 'outcomes': outcomes,
                'cycles': cycles, 'notifications':notifications}
    return render(request, 'main/adminhome.html', context)


@login_required
def newCycle(request):
    year = request.POST.get('year')
    semester = request.POST.get('semester')

    cycle = Cycle(year=year, semester=semester)
    cycle.save()

    return HttpResponseRedirect(reverse('main:dashboard'))

def cycle(request, cycle_id):
    outcomes = Outcome.objects.all();

    context = {'cycle_id':cycle_id, 'outcomes': outcomes}
    return render(request, 'main/cycle.html', context)


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, 'Account created')
            return redirect('/')
        else:
            return render(request, 'main/register.html', {'form': form})

    else:
        form = RegisterForm()
        return render(request, 'main/register.html', {'form': form})
