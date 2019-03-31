from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Rubric, Student, Measure, Category, evaluate_rubric, Evaluator, Outcome, Cycle, Test_score
from django.contrib import messages
from .forms import RegisterForm
import csv
import codecs
import io

col = None
row = None
def homepage(request):
    return render(request, 'main/homepage.html', {})

@login_required
def evaluatorhome(request):
    rubrics = Rubric.objects.all()
    students = Student.objects.all()
    evaluatons = evaluate_rubric.objects.all()
    context = {'rubrics':rubrics, 'students':students, 'evaluations':evaluatons}

    return render(request, 'main/evaluatorhome.html', context)


def new_rubric(request):

    if request.method == "POST":
        cols = request.POST.get('cols')
        rows = request.POST.get('rows')
        context = {'cols': cols, 'rows': rows}
        print(rows)
        print(cols)
        return render(request, 'main/rubric_create.html', context)
    return render(request, 'main/rubric_create.html')

@login_required
def rubric(request):
    if request.method == "POST":

        created_by = request.POST.get('created_by')
        title = request.POST.get('title')
        category = request.POST.get('category')
        measure = request.POST.get('measure')

        x = request.POST.get("rows", '')
        print(x)
        measureText = request.POST.get('measureText')
        weight = request.POST.get('weight')

        rubric = Rubric(created_by=created_by, title=title, category=Category(categoryTitle=category, measure=Measure(measureTitle=measure, measureText=measureText,weight=weight)))
        rubric.save()

        rubrics = Rubric.objects.filter(title=title)
        context = {'rubrics':rubrics}

        return render(request, 'main/rubric.html', context)
    return render(request, 'main/rubric_create.html')


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
    outcomes = Outcome.objects.filter(cycle=cycle_id);
    evaluators = Evaluator.objects.all();
    measures = Measure.objects.all();
    rubrics = Rubric.objects.all();

    context = {'cycle_id':cycle_id, 'outcomes': outcomes, 'evaluators': evaluators, 'measures': measures, 'rubrics': rubrics}
    return render(request, 'main/cycle.html', context)

def upload(request):
    if request.method=='POST' and request.FILES:
        csvfile = request.FILES['csv_file']
        datset = csvfile.read().decode("UTF-8")
        io_string = io.StringIO(datset)


        for column in csv.reader(io_string, delimiter=",", quotechar="|"):
            student_score = Test_score(student=column[0], test_name=column[1], score=column[2])
            student_score.save()

        context = {'test_scores': Test_score.objects.all()}
        return render(request, 'main/upload.html', context)

    return render(request, 'main/upload.html')




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

def add_evaluator(request):
    if request.method == 'POST':
        evaluator = Evaluator(request.POST.get('evaluator_email'))
        evaluator.save()
    return HttpResponseRedirect(reverse('main:dashboard'))

def add_learning_outcome(request, outcome_id):
    title = request.POST.get('outcome_title')
    outcome = Outcome(title=title)

    outcome.save()

    return render(request, 'main/cycle.html')

def update_measure(request, measure_id):
    measure_title = request.POST.get('measure_title')
    measure_desc = request.POST.get('measure_desc')
    cutoff_score = request.POST.get('cutoff_score')
    cutoff_percent = request.POST.get('cutoff_percent')

    measure = Measure.objects.filter(id=measure_id).update(measureTitle= measure_title,measureText= measure_desc,cutoff_score= cutoff_score,cutoff_percentage= cutoff_percent)

    return render(request, 'main/cycle.html')

def new_measure(request, outcome_id):
    measure_title = request.POST.get('measure_title')
    measure_desc = request.POST.get('measure_desc')
    cutoff_score = request.POST.get('cutoff_score')
    cutoff_percent = request.POST.get('cutoff_percent')

    outcome_found = Outcome.objects.get(id=outcome_id)
    measure = Measure(measureTitle= measure_title,measureText= measure_desc,cutoff_score= cutoff_score,cutoff_percentage= cutoff_percent, outcome=outcome_found)

    measure.save()

    return render(request, 'main/cycle.html')
