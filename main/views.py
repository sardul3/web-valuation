from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from .models import Rubric, Student, Measure, Category, evaluate_rubric, Evaluator, Outcome, Cycle, Test_score, Test, Student
from django.contrib import messages
from .forms import RegisterForm
import csv
import codecs
import io
from django.utils.timezone import datetime
from django.db.models import Avg, Count, Min, Sum


def homepage(request):
    return render(request, 'main/homepage.html', {})

@login_required
def evaluatorhome(request):
    rubrics = Rubric.objects.all()
    students = Student.objects.all()
    evaluations = evaluate_rubric.objects.all()
    evaluated_flag = []
    for stu in students:
        if evaluations.filter(student=stu.name,evaluated_by=request.user.username).exists():
            evaluated_flag.append(stu.name)



    email_address = request.user.email
    measure = Measure.objects.filter(evaluator__in = Evaluator.objects.filter(email=email_address))
    context = {'rubrics':rubrics, 'students':students, 'evaluations':evaluations, 'measures':measure,
                'evaluated_flag':evaluated_flag}

    return render(request, 'main/evaluatorhome.html', context)


@login_required
def grade(request):
    rubrics = Rubric.objects.filter(id=1)[0]
    measures = Measure.objects.all()
    students = Student.objects.all()
    evaluations = evaluate_rubric.objects.all()
    categories = Category.objects.all()
    context = {'rubric':rubrics, 'students': students, 'measures':measures, 'evaluations':evaluations
            , 'row_num' : range(rubrics.max_row), 'row_col':range(rubrics.max_col), 'categories':categories}

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

    return render(request, 'main/evaluator_rubric_select.html',context)


def evaluator_rubric_select(request, measure_id):
    measures = Measure.objects.get(id=measure_id)
    students = measures.student.all()
    rubric = measures.rubric
    categories = Category.objects.all()
    evaluations = evaluate_rubric.objects.all()

    evaluated_flag = []
    for stu in students:
        if evaluations.filter(student=stu.name,evaluated_by=request.user.username).exists():
            evaluated_flag.append(stu.name)

    context = { 'measures':measures, 'students':students, 'measure_id':measure_id, 'rubric':rubric, 'categories':categories
                ,'row_num':range(rubric.max_row), 'col_num': range(rubric.max_col), 'evaluated_flag':evaluated_flag}
    return render(request, 'main/evaluator_rubric_select.html', context)

def evaluate_students(request):
    return render(request, 'main/evaluate_students.html')


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
    today = datetime.today()

    cycle = Cycle(year=year, semester=semester, startDate=today)
    cycle.save()
    messages.add_message(request, messages.SUCCESS, 'Cycle created successfully')

    return HttpResponseRedirect(reverse('main:dashboard'))

def cycle(request, cycle_id):
    outcomes = Outcome.objects.filter(cycle=cycle_id)
    evaluators = Evaluator.objects.all()
    measures = Measure.objects.all()
    rubrics = Rubric.objects.all()
    cycle = Cycle.objects.get(id=cycle_id)

    context = {'cycle_id':cycle_id, 'outcomes': outcomes, 'evaluators': evaluators, 'measures': measures, 'rubrics': rubrics, 'cycle':cycle}
    return render(request, 'main/cycle.html', context)

def end_cycle(request, cycle_id):
    cycle = Cycle.objects.filter(id=cycle_id).update(isCurrent=False, endDate=datetime.today())

    messages.add_message(request, messages.WARNING, 'Cycle was deleted successfully')

    return HttpResponseRedirect(reverse('main:dashboard'))



def outcome_detail(request, outcome_id):
    outcome = Outcome.objects.get(id=outcome_id)
    measures = Measure.objects.filter(outcome=outcome)
    rubrics = Rubric.objects.all()
    students = None
    evaluators = Evaluator.objects.all()
    num_of_evaluations = []


    for measure in measures:
        students = measure.student.all()
        evaluations = evaluate_rubric.objects.filter(measure=measure).count()
        if(evaluations>0):
            num_of_evaluations.append(measure.measureTitle)
        print(num_of_evaluations)



    context = {'outcome_id': outcome_id, 'outcome': outcome, 'measures': measures, 'rubrics':rubrics,
                'students': students, 'evaluators': evaluators, 'num_of_evaluations':num_of_evaluations}
    return render(request, 'main/outcome_detail.html', context)

def upload(request, measure_id, outcome_id):
    if request.method=='POST' and request.FILES:
        measure = Measure.objects.filter(id=measure_id)
        test_name = request.POST.get('test_title')
        max_points = request.POST.get('max_points')

        total_points = 0

        csvfile = request.FILES['csv_file']
        datset = csvfile.read().decode("UTF-8")
        io_string = io.StringIO(datset)


        for column in csv.reader(io_string, delimiter=",", quotechar="|"):
            total_points += int(column[1])
            student = Student.objects.create(name=column[0])
            student_score = Test_score(student=student, test=test_name, score=int(column[1]))
            student_score.save()
            measure.update(test_score=student_score)

        number_of_students = Test_score.objects.filter(test=test_name).count()
        print(total_points)
        print(number_of_students)
        average = total_points / number_of_students
        print(average)

        return HttpResponseRedirect(reverse_lazy('main:outcome_detail', kwargs={'outcome_id':outcome_id}))

    return HttpResponseRedirect(reverse_lazy('main:outcome_detail', kwargs={'outcome_id':outcome_id}))




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


def add_learning_outcome(request, cycle_id):
    title = request.POST.get('outcome_title')
    outcome = Outcome(title=title)
    outcome.save()
    cycle_found = Cycle.objects.get(id=cycle_id)
    outcome.cycle.add(cycle_found)

    messages.add_message(request, messages.SUCCESS, 'Learning outcome created')

    return HttpResponseRedirect(reverse_lazy('main:cycle', kwargs={'cycle_id':cycle_id}))

def update_measure(request, measure_id):
    measure_title = request.POST.get('measure_title')
    cutoff_score = request.POST.get('cutoff_score')
    cutoff_percent = request.POST.get('cutoff_percent')
    cutoff_type = request.POST.get('cutoff_selection')
    tool_type = request.POST.get('tool_selection')
    measure = Measure.objects.filter(id=measure_id).update(measureTitle= measure_title,
    cutoff_score= cutoff_score,cutoff_percentage= cutoff_percent,
    cutoff_type=cutoff_type, tool_type=tool_type)

    messages.add_message(request, messages.SUCCESS, 'Measure was edited successfully')

    url = request.POST.get("url")
    return redirect(url)

    return render(request, 'main/cycle.html')

def new_measure(request, outcome_id):
    measure_title = request.POST.get('measure_title')
    cutoff_score = request.POST.get('cutoff_score')
    cutoff_percent = request.POST.get('cutoff_percent')
    tool_type = request.POST.get('tool_selection')
    cutoff_type = request.POST.get('cutoff_selection')

    outcome_found = Outcome.objects.get(id=outcome_id)
    measure = Measure(measureTitle= measure_title,
                      cutoff_score= cutoff_score,cutoff_percentage= cutoff_percent,
                      outcome=outcome_found, tool_type=tool_type, cutoff_type=cutoff_type)
    measure.save()

    messages.add_message(request, messages.SUCCESS, 'New measure is added to the outcome')

    url = request.POST.get("url")
    return redirect(url)
    return render(request, 'main/cycle.html')

def add_rubric_to_measure(request, measure_id, outcome_id):
    rubric_title = request.POST.get('select_rubric', None)
    rubric_found = Rubric.objects.get(title = rubric_title)
    measure = Measure.objects.filter(id=measure_id).update(rubric=rubric_found)

    messages.add_message(request, messages.SUCCESS, 'Rubric is now associated with the measure')

    return HttpResponseRedirect(reverse_lazy('main:outcome_detail', kwargs={'outcome_id':outcome_id}))

def delete_measure(request, measure_id):
    Measure.objects.filter(id=measure_id).delete()

    messages.add_message(request, messages.WARNING, 'Measure was removed successfully')

    url = request.POST.get("url")
    return redirect(url)
    return render(request, 'main/cycle.html')

def add_test_to_measure(request, measure_id):
    return HttpResponseRedirect(reverse_lazy('main:upload'))

def test_rubric(request):
    rows = 0
    cols = 0
    if request.method == 'POST':
        rows = int(request.POST.get('rows'))
        cols = int(request.POST.get('cols'))
        print(rows)
        print(cols)
        return render(request, 'main/created_test_rubric.html', {'rows':range(rows), 'cols':range(cols),'row_num':rows, 'col_num': cols})
    return render(request, 'main/test_rubric.html')


def created_test_rubric(request):
    if request.method == 'POST':
        row_num = int(request.POST.get('row_num'))
        row_col = int(request.POST.get('col_num'))
        rubric_title = request.POST.get("rubric_title")
        rubric_new = Rubric(title=rubric_title, max_row=row_num, max_col=row_col)
        rubric_new.save()
        for x in range(row_num):
            for y in range(row_col):
                text = request.POST.get(str(x)+str(y))
                category = Category(categoryTitle=text,index_x=x,index_y=y,rubric=rubric_new)
                category.save()

    return render(request, 'main/test_rubric.html')

def rubric_render(request, rubric_id):
    rubrics = Rubric.objects.filter(id=rubric_id)[0]
    categories = Category.objects.all()
    context = {'rubric': rubrics, 'categories':categories, 'row_num' : range(rubrics.max_row), 'row_col':range(rubrics.max_col)}
    return render(request, 'main/rubric_render_admin.html',context)

def add_individual_student(request, outcome_id, measure_id):
    student_name = request.POST.get('student_name')
    student = Student(name=student_name)
    student.save()

    measure = Measure.objects.get(id=measure_id)
    measure.student.add(student)

    messages.add_message(request, messages.SUCCESS, 'Successfully added Student added to the Measure')

    return HttpResponseRedirect(reverse_lazy('main:outcome_detail', kwargs={'outcome_id':outcome_id}))

def upload_student(request, outcome_id, measure_id):
    if request.method=='POST' and request.FILES:
        measure = Measure.objects.get(id=measure_id)

        csvfile = request.FILES['csv_file']
        datset = csvfile.read().decode("UTF-8")
        io_string = io.StringIO(datset)

        for column in csv.reader(io_string, delimiter=",", quotechar="|"):

            student = Student(name=column[0], classification=column[1])
            student.save()
            measure.student.add(student)

            messages.add_message(request, messages.SUCCESS, 'Successfully added Student added to the Measure')

        return HttpResponseRedirect(reverse_lazy('main:outcome_detail', kwargs={'outcome_id':outcome_id}))

    return HttpResponseRedirect(reverse_lazy('main:outcome_detail', kwargs={'outcome_id':outcome_id}))

def add_evaluator(request, outcome_id, measure_id):
    measure = Measure.objects.get(id=measure_id)

    if request.method == 'POST':
        evaluator = Evaluator(name = request.POST.get('evaluator_name'), email=request.POST.get('evaluator_email'))
        evaluator.save()
        measure.evaluator.add(evaluator)

        messages.add_message(request, messages.SUCCESS, 'Successfully added Evaluator added to the Measure')


    return HttpResponseRedirect(reverse_lazy('main:outcome_detail', kwargs={'outcome_id':outcome_id}))

def update_outcome(request, outcome_id, cycle_id):
    new_outcome_text = request.POST.get('outcome_title')
    outcome = Outcome.objects.filter(id = outcome_id).update(title = new_outcome_text)

    messages.add_message(request, messages.SUCCESS, 'Outcome was edited successfully')

    return HttpResponseRedirect(reverse_lazy('main:cycle', kwargs={'cycle_id':cycle_id}))

def delete_outcome(request, outcome_id, cycle_id):
    outcome = Outcome.objects.filter(id=outcome_id).delete()
    messages.add_message(request, messages.WARNING, 'Outcome was deleted successfully')

    return HttpResponseRedirect(reverse_lazy('main:cycle', kwargs={'cycle_id':cycle_id}))

def view_test_score(request, test_score_test, measure_id):


    measure = Measure.objects.get(id=measure_id)
    test_score = Test_score.objects.filter(test=test_score_test)
    total_students = test_score.count()
    test_average = test_score.aggregate(Avg('score'))['score__avg']
    above_threshold = test_score.filter(score__gte = 75).count()
    percentage = above_threshold / total_students * 100
    greater_than_avg = test_score.filter(score__gte = test_average).count()
    passed = False
    margin = 0.0

    bin_array = []
    for student_score in test_score:
        if(measure.cutoff_type == 'Percentage'):
            if(student_score.score>=measure.cutoff_score):
                bin_array.append(student_score.student.name)

        elif(measure.cutoff_type == 'Average'):
            if(student_score.score>=measure.cutoff_percentage):
                bin_array.append(student_score.student.name)

    print(bin_array)

    if(measure.cutoff_type == 'Percentage'):
            above_threshold = test_score.filter(score__gte = measure.cutoff_score).count()
            percentage = above_threshold / total_students * 100
            if(percentage>=measure.cutoff_percentage):
                passed = True
            else:
                margin = measure.cutoff_percentage - percentage
    elif(measure.cutoff_type == 'Average'):
            test_average = test_score.aggregate(Avg('score'))['score__avg']
            above_threshold = test_score.filter(score__gte = test_average).count()
            percentage = above_threshold / total_students * 100
            if(percentage>=measure.cutoff_percentage):
                passed = True
            else:
                margin = measure.cutoff_percentage - percentage


    context = {'test_score': test_score, 'total_students':total_students,
                'test_average': test_average, 'above_threshold': above_threshold,
                'percentage':percentage, 'greater_than_avg': greater_than_avg,
                'measure':measure, 'passed':passed, 'bin_array': bin_array,
                 'count': range(len(bin_array)), 'margin':margin}
    return render(request, 'main/test_scores.html', context)

def evaluate_single_student(request, rubric_row, rubric_id, measure_id):
    student_name = request.POST.getlist('student_to_be_evaluated')[0]
    rubric_name = Rubric.objects.get(id=rubric_id).title
    measure = Measure.objects.get(id=measure_id)
    scores = []
    avg = 0
    total = 0
    count=0
    for x in range(rubric_row-1):
        score = request.POST.get('score'+str(x+1))
        scores.append(score)
        total += int(score)
        count = count +1
    print(scores)
    print(count)
    print(total)

    avg = total/count
    print(avg)
    evaluated = evaluate_rubric(rubric=rubric_name, grade_score=avg,
                student=student_name, measure=measure, evaluated_by = request.user.username)
    evaluated.save()
    return HttpResponseRedirect(reverse_lazy('main:evaluatorhome'))

def remove_rubric_association(request, measure_id, outcome_id):
    measure = Measure.objects.filter(id = measure_id)
    measure.update(rubric=None)

    return HttpResponseRedirect(reverse_lazy('main:outcome_detail', kwargs={'outcome_id':outcome_id}))

def remove_test_association(request, measure_id, outcome_id):
    measure = Measure.objects.filter(id = measure_id)
    measure.update(test_score=None)

    return HttpResponseRedirect(reverse_lazy('main:outcome_detail', kwargs={'outcome_id':outcome_id}))

def remove_evaluator_access(request, evaluator_id, measure_id, outcome_id):
    evaluator = Evaluator.objects.get(id=evaluator_id)
    measure = Measure.objects.get(id=measure_id)
    measure.evaluator.remove(evaluator)

    return HttpResponseRedirect(reverse_lazy('main:outcome_detail', kwargs={'outcome_id':outcome_id}))



def view_rubric_data(request, measure_id):
    measure = Measure.objects.get(id=measure_id)

    total_count = 0;
    evaluator_count = 0;
    student_count = 0;
    evaluated_student_count = 0;

    students = measure.student.all()
    # evaluator_count = measure.evaluator.all().count()
    # student_count = measure.student.all().count()
    evaluated_student_count = evaluate_rubric.objects.filter(measure=measure).count()
    # total_count = evaluator_count * student_count

    # avg_points = evaluate_rubric.objects.filter(measure=measure).aggregate(Avg('grade_score'))['grade_score__avg']

    number_of_pass_cases = evaluate_rubric.objects.filter(grade_score__gte = measure.cutoff_score).count()
    percent_pass_cases = number_of_pass_cases/evaluated_student_count * 100

    # number_pass_cases_avg = evaluate_rubric.objects.filter(grade_score__gte = avg_points).count()
    # percent_pass_cases_avg = number_pass_cases_avg/total_count * 100

    # data = {
    #     'total_count': total_count,
    #     'evaluator_count':evaluator_count,
    #     'student_count':student_count,
    #     'evaluated_student_count': evaluated_student_count,
    #     'avg_points': avg_points,
    #     'number_of_pass_cases': number_of_pass_cases,
    #     'percent_pass_cases': percent_pass_cases,
    #     'number_pass_cases_avg':number_pass_cases_avg,
    #     'percent_pass_cases_avg': percent_pass_cases_avg
    # }
    # print(data)

    evaluated_list = evaluate_rubric.objects.filter(measure = measure)

    bin_array = []
    for student_score in evaluated_list:
        if(measure.cutoff_type == 'Percentage'):
            if(student_score.grade_score>=measure.cutoff_score):
                bin_array.append(student_score.student)

    passed = False
    if(measure.cutoff_type == 'Percentage'):
            if(percent_pass_cases>=measure.cutoff_percentage):
                passed = True


    context = {'evaluated_list':evaluated_list, 'bin_array':bin_array, 'measure':measure, 'passed':passed}


    return render(request, 'main/rubric_scores.html', context)
