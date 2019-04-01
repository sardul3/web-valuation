from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from .models import Rubric, Student, Measure, Category, evaluate_rubric, Evaluator, Outcome, Cycle, Test_score, Test
from django.contrib import messages
from .forms import RegisterForm
import csv
import codecs
import io

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

    return render(request, 'main/rubric_create.html')

@login_required
def rubric(request):
    rows = int(request.GET.get('rows'))
    cols = int(request.GET.get('cols'))
    print(rows)
    print(cols)

    title_found = request.GET.get('title')
    rubric = Rubric.objects.create(title=title_found)
    print(rubric)
    for row in range(rows):
        for col in range(cols):
            key = str(row)+str(col)
            print(key)
            content = request.GET.get(key)
            print(content)
            category = Category.objects.create(categoryTitle=content)
            print(category)
            rubric.category.add(category)

    print(rubric)

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

def add_learning_outcome(request, cycle_id, outcome_id):
    title = request.POST.get('outcome_title')
    outcome = Outcome(title=title)
    outcome.save()
    cycle_found = Cycle.objects.get(id=cycle_id)
    outcome.cycle.add(cycle_found)


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

def add_rubric_to_measure(request, measure_id):
    rubric_title = request.POST.get('select_rubric', None)
    rubric_found = Rubric.objects.get(title = rubric_title)
    measure = Measure.objects.filter(id=measure_id).update(rubric=rubric_found)

    return HttpResponseRedirect(reverse_lazy('main:upload'))

def delete_measure(request, measure_id):
    Measure.objects.filter(id=measure_id).delete()
    return render(request, 'main/cycle.html')

def add_test_to_measure(request, measure_id):

    return HttpResponseRedirect(reverse_lazy('main:upload'))
