from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from .models import( Rubric, Student, Measure, Category, evaluate_rubric,
        Evaluator, Outcome, Cycle, Test_score, Test, Student, evaluation_flag,
        custom_students, Broadcast, Course, Notification, category_score,
        CoOrdinator, Invited_Coordinator,InvitedCo, Log, Department)
from django.contrib import messages
from .forms import RegisterForm, CoOrdinatorRegisterForm
import csv
import codecs
import io
from django.utils.timezone import datetime
from django.db.models import Avg, Count, Min, Sum
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import send_mail
from itertools import chain
import csv

def test_score_data(test_score_test, measure_id):
    measure = Measure.objects.get(id=measure_id)
    test_score = custom_students.objects.filter(measure=measure, graded=True, current=True)
    total_students = custom_students.objects.filter(measure=measure, current=True).count()

    passed = False
    margin = 0.0
    data = {}
    above_threshold = None
    percentage = None

    test_average = 0
    above_test_average = 0

    bin_array = []
    for student_score in test_score:
        if(measure.cutoff_type == 'Percentage'):
            if(student_score.grade>=measure.cutoff_score):
                bin_array.append(student_score.student_name)

        elif(measure.cutoff_type == 'Average'):
            if(student_score.grade>=measure.cutoff_percentage):
                bin_array.append(student_score.student_name)


    if(measure.cutoff_type == 'Percentage'):
        if custom_students.objects.filter(measure=measure, graded=True, current=True).count()>0:
            above_threshold = test_score.filter(grade__gte = measure.cutoff_score).count()
            percentage = above_threshold / total_students * 100
            test_average = test_score.aggregate(Avg('grade'))['grade__avg']
            above_test_average = custom_students.objects.filter(measure=measure, current=True, graded = True, grade__gte = test_average).count()

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

    data = dict(test_score= test_score, total_students = total_students,
                        test_average= test_average, above_threshold= above_threshold,
                        percentage=percentage, above_test_average = above_test_average,
                        measure=measure, passed=passed, bin_array=bin_array,
                         count=range(len(bin_array)), margin= margin)

    return data

def status(measure_id, score):
    measure = Measure.objects.get(id=measure_id)
    if measure.cutoff_score>score:
        return 'Failed'
    else:
        return 'Passed'

def print_report(request,test_score, measure_id):
    print_data = test_score_data(test_score, measure_id)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="test_score.csv"'

    writer = csv.writer(response)
    writer.writerow(['Student Name', 'Grade', 'Evaluated by', 'Status'])


    for score in print_data['test_score']:
        if Evaluator.objects.filter(id=score.evaluator_id).exists():
            ev_name = Evaluator.objects.get(id=score.evaluator_id).email
        else:
            ev_name = 'Evaluator'
        writer.writerow([score.student_name, score.grade, ev_name , status(measure_id, score.grade) ])

    return response



def rubric_data(measure_id):
    measure = Measure.objects.get(id=measure_id)

    evaluator_count = 0
    student_count = 0
    evaluated_student_count = 0
    rubric_average = 0

    students = measure.student.all()
    evaluator_count = measure.evaluator.all().count()
    student_count = custom_students.objects.filter(measure=measure, current=True).count()
    evaluated_student_count = custom_students.objects.filter(measure=measure, grade__isnull = False, current=True).count()

    number_of_pass_cases = custom_students.objects.filter(measure=measure,grade__gte = measure.cutoff_score, current=True).count()

    if evaluated_student_count>0:
        percent_pass_cases = number_of_pass_cases/evaluated_student_count * 100.0

    else:
        percent_pass_cases=0

    evaluated_list = custom_students.objects.filter(measure=measure, graded=True, current=True).order_by('student_name')
    ev_cats = category_score.objects.filter(student__in = evaluated_list)

    bin_array = []
    for student_score in evaluated_list:
        if(measure.cutoff_type == 'Percentage'):
            if(student_score.grade>=measure.cutoff_score):
                bin_array.append(student_score.student_name)

    passed = False
    if(measure.cutoff_type == 'Percentage'):

            if(percent_pass_cases>=measure.cutoff_percentage):
                passed = True
                Measure.objects.filter(id=measure_id).update(status='passing')


    data = {
        'evaluator_count':evaluator_count,
        'student_count':student_count,
        'evaluated_student_count': evaluated_student_count,
        'number_of_pass_cases': number_of_pass_cases,
        'percent_pass_cases': percent_pass_cases,
        'evaluated_list':evaluated_list, 'bin_array':bin_array, 'measure':measure, 'passed':passed,
        'ev_cats':ev_cats
    }


    return data


def print_report_rubric(request, measure_id):
    rubric_datas = rubric_data(measure_id)
    print(rubric_datas['evaluated_list'])
    name = Measure.objects.get(id=measure_id).measureTitle

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="rubric.csv"'

    writer = csv.writer(response)
    cat_arr = ['Student Name', 'Grade', 'Evaluated by', 'Status']
    cat_scores = rubric_datas['ev_cats']

    writer.writerow(cat_arr)

    for score in rubric_datas['evaluated_list']:
        if Evaluator.objects.filter(id=score.evaluator_id).exists():
            ev_name = Evaluator.objects.get(id=score.evaluator_id).email
        else:
            ev_name = 'Evaluator'
        writer.writerow([score.student_name, score.grade, ev_name , status(measure_id, score.grade) ])

    return response


def perc_update(eval):
    student_count=0
    evaluated_count=0
    for st in custom_students.objects.filter(evaluator=eval):
        if st.graded:
            evaluated_count+=1
        student_count+=1
    if student_count==0:
        eval.perc_completed=0
    else:
        perc = 100.0*(evaluated_count/student_count)
        eval.perc_completed=perc
    eval.save()
    return



def admin_test(user):
    return user.is_staff

def super_admin_test(user):
    return user.is_superuser

def homepage(request):
    rubrics = Rubric.objects.all()
    students = Student.objects.all()
    evaluations = evaluate_rubric.objects.all()
    measures = Measure.objects.all()
    flags = evaluation_flag.objects.all()
    alerts = Broadcast.objects.filter(receiver=request.user.email, read=False).order_by('-sent_at')
    alerts_count = alerts.count()

    flag = []

    email_address = request.user.email
    cycle_filter = []
    measure = Measure.objects.filter(evaluator__in = Evaluator.objects.filter(email=email_address), current=True )
    for m in measure:
        if m.rubric or m.test_score:
            print(m)
            for o in Outcome.objects.all():
                if m.outcome == o:
                    print(o)
                    x = (o.cycle.values())
                    for val in x:
                        print(val)
                        if val['isCurrent'] == True:
                            cycle_filter.append(val['id'])

    x = []
    y = 0
    for me in measure:
        x = me.student.all()
        y = evaluate_rubric.objects.filter(measure=me, grade_score__isnull=False).count()
        for f in flags:
            if f.measure == me:
                flag.append(f.student_name)
    student_count = len(x)
    eval_student = y
    if student_count==0:
        perc=100.0
    else:
        perc =100.0* (eval_student/student_count)

    eval = request.user.email
    current_eval = 0
    for myeval in Evaluator.objects.all():
        if(myeval.email==eval):
            current_eval = myeval
    myeval.perc_completed = perc
    myeval.save()

    cust_student_list=[]
    for stu in custom_students.objects.all():
        for evaluator in stu.measure.evaluator.all():
            if(evaluator.email==email_address):
                cust_student_list.append(stu)
    for mea in measure:
        total=0.0
        graded =0

        for cu in cust_student_list:
            if cu.evaluator is not None:
                if cu.measure == mea and cu.evaluator.email==request.user.email:
                    total+=1
                    if cu.graded:
                        #print(cu.student_name)
                        graded+=1

        #print("Graded",graded)
        #print("Total",total)
        if graded==0:
            mea.evaluationPercent=0.0
        else:
            mea.evaluationPercent = (graded/total)*100.0

    context = {'rubrics':rubrics, 'students':students, 'evaluations':evaluations, 'measures':measure, 'percent':perc, 'flag':cust_student_list
    , 'now':'active','alerts':alerts, 'alerts_count':alerts_count, 'cycle_filter':len(cycle_filter)}

    return render(request, 'main/evaluatorhome.html', context)




@user_passes_test(admin_test)
def outcomes(request):
    coordinator = CoOrdinator.objects.get(request.user.email)
    dept = coordinator.dept
    outcomes = Outcome.objects.filter(dept=dept);
    measures = Measure.objects.all(dept=dept)
    cycles = Cycle.objects.all(dept=dept)
    data = dict()
    for measure in measures:
        evaluations = evaluate_rubric.objects.filter(measure=measure).count()
        if(evaluations>0):
            if measure.tool_type == 'Rubric':
                data.update({measure.id: rubric_data(measure.id)})
            elif measure.tool_type == 'Test score':
                data.update({measure.id: test_score_data(measure.test_score, measure.id)})

    context = {'cordinator':cordinator,'outcomes':outcomes, 'measures':measures, 'cycles':cycles, 'outcome': 'active','notification_count' : Notification.objects.filter(read=False, to=request.user.email).count(),
    'notifications' : Notification.objects.filter(read=False, to=request.user.email).order_by('-created_at' ), 'data':data
}
    return render(request, 'main/outcomes.html', context)

def rubrics(request):
    cordinator = CoOrdinator.objects.get(email=request.user.email)
    dept=cordinator.dept
    rubrics = Rubric.objects.filter(dept=dept)
    msgs = Broadcast.objects.filter(receiver=request.user.email).order_by('-sent_at')
    msgs_count = Broadcast.objects.filter(receiver=request.user.email, read=False).order_by('-sent_at').count()


    print(Notification.objects.filter(read=False, to=request.user.email))
    context = {'cordinator':cordinator,'evaluator': Evaluator.objects.all(),'rubrics':rubrics, 'rubric': 'active','notification_count' : Notification.objects.filter(read=False, to=request.user.email).count(),
    'notifications' : Notification.objects.filter(read=False, to=request.user.email).order_by('-created_at'), 'msgs':msgs, 'msgs_count': msgs_count}
    return render(request, 'main/rubrics.html', context)

@user_passes_test(admin_test)
def cycles(request):
    cordinator = CoOrdinator.objects.get(email=request.user.email)
    dept = cordinator.dept
    cycles = Cycle.objects.filter(dept=dept)

    msgs = Broadcast.objects.filter(receiver=request.user.email).order_by('-sent_at')

    context = {'cordinator':cordinator,'cycles':cycles, 'cycle': 'active','notification_count' : Notification.objects.filter(read=False, to=request.user.email).count(),
    'notifications' : Notification.objects.filter(read=False, to=request.user.email).order_by('-created_at'), 'msgs':msgs,'msgs_count': Broadcast.objects.filter(receiver=request.user.email, read=False).order_by('-sent_at').count()}
    return render(request, 'main/cycles.html', context)


@login_required
def evaluatorhome(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            email = request.POST.get('email')
            department = request.POST.get('department')
            invited_Coordinator = Invited_Coordinator.objects.create(email=email, department=department,
                                                                     invited_by=request.user.username)
            evaluators = Evaluator.objects.all()
            for eval in evaluators:
                if eval.email == invited_Coordinator:
                    Invited_Coordinator.objects.filter(email=email, department=department).update(accepted=True)

            messages.add_message(request, messages.SUCCESS, 'Coordinator was invited successfully')

            context = {'now': 'active', 'cordinator':InvitedCo.objects.all(), 'departments':Department.objects.all()}
            return render(request, 'main/invite.html', context)
        context = {'now': 'active', 'cordinator':InvitedCo.objects.all(),'departments':Department.objects.all()}
        return render(request, 'main/invite.html', context)

    if request.user.is_staff:
        cordinator = CoOrdinator.objects.filter(email=request.user.email)[0]
        dept = cordinator.dept
        outcomes = Outcome.objects.filter(dept=dept)
        measures = Measure.objects.filter(dept=dept)
        cycles = Cycle.objects.filter(dept=dept)
        eval_a = Evaluator.objects.filter(dept=dept)
        courses = Course.objects.filter(dept=dept)

        for ev in Evaluator.objects.filter(dept=dept):
            perc_update(ev)

        data = dict()
        for measure in measures:
            evaluations = evaluate_rubric.objects.filter(measure=measure).count()
            if (evaluations > 0):
                if measure.tool_type == 'Rubric':
                    data.update({measure.id: rubric_data(measure.id)})
                elif measure.tool_type == 'Test score':
                    data.update({measure.id: test_score_data(measure.test_score, measure.id)})

        cyc = Cycle.objects.filter(dept=dept)
        mycyc = 0
        for cycles in cyc:
            if (cycles.isCurrent):
                mycyc = cycles
        outcome_a = Outcome.objects.filter(dept=dept)
        outcome_list = []
        for oc in outcome_a:
            for v in oc.cycle.all():
                if (v == mycyc):
                    outcome_list.append(oc)
        measure_a = Measure.objects.filter(dept=dept)
        measure_list = []
        for me in measure_a:
            for o in outcome_list:
                if (me.outcome == o):
                    measure_list.append(me)
        evaluator_list = []
        for eval in eval_a:
            for mymea in measure_list:
                for eval_more in mymea.evaluator.all():
                    if (eval == eval_more):
                        evaluator_list.append(eval)

        msgs = Broadcast.objects.filter(receiver=request.user.email).order_by('-sent_at')
        msgs_count = Broadcast.objects.filter(receiver=request.user.email, read = False).order_by('-sent_at').count()
        evaluator_list = Evaluator.objects.filter(dept = dept)
        context = {'cordinator':CoOrdinator.objects.get(email=request.user.email),'evaluator': evaluator_list, 'dashboard': 'active', 'outcomes': outcomes, 'measures': measures,
                   'data': data,
                   'notification_count': Notification.objects.filter(read=False, to=request.user.email).count(), 'msgs':msgs, 'msgs_count':msgs_count,
                   'notifications': Notification.objects.filter(read=False, to=request.user.email).order_by('-created_at'), 'cycles': cyc,'mycyc':mycyc,'courses':courses
                   }
        return render(request, 'main/adminhome.html', context)
    else:
        rubrics = Rubric.objects.all()
        students = Student.objects.all()
        evaluations = evaluate_rubric.objects.all()
        measures = Measure.objects.all()
        flags = evaluation_flag.objects.all()
        alerts = Broadcast.objects.filter(receiver=request.user.email, read=False).order_by('-sent_at')
        alerts_count = alerts.count()

        flag = []

        email_address = request.user.email
        cycle_filter = []
        measure = Measure.objects.filter(evaluator__in = Evaluator.objects.filter(email=email_address), current=True )
        for m in measure:
            if m.rubric or m.test_score:
                print(m)
                for o in Outcome.objects.all():
                    if m.outcome == o:
                        print(o)
                        x = (o.cycle.values())
                        for val in x:
                            print(val)
                            if val['isCurrent'] == True:
                                cycle_filter.append(val['id'])

        x = []
        y = 0
        for me in measure:
            x = me.student.all()
            y = evaluate_rubric.objects.filter(measure=me, grade_score__isnull=False).count()
            for f in flags:
                if f.measure == me:
                    flag.append(f.student_name)
        student_count = len(x)
        eval_student = y
        if student_count==0:
            perc=100.0
        else:
            perc =100.0* (eval_student/student_count)

        eval = request.user.email
        current_eval = 0
        for myeval in Evaluator.objects.all():
            if(myeval.email==eval):
                current_eval = myeval
        myeval.perc_completed = perc
        myeval.save()

        cust_student_list=[]
        for stu in custom_students.objects.all():
            for evaluator in stu.measure.evaluator.all():
                if(evaluator.email==email_address):
                    cust_student_list.append(stu)
        for mea in measure:
            total=0.0
            graded =0

            for cu in cust_student_list:
                if cu.evaluator is not None:
                    if cu.measure == mea and cu.evaluator.email==request.user.email:
                        total+=1
                        if cu.graded:
                            #print(cu.student_name)
                            graded+=1

            #print("Graded",graded)
            #print("Total",total)
            if graded==0:
                mea.evaluationPercent=0.0
            else:
                mea.evaluationPercent = (graded/total)*100.0

        context = {'rubrics':rubrics, 'students':students, 'evaluations':evaluations, 'measures':measure, 'percent':perc, 'flag':cust_student_list
        , 'now':'active','alerts':alerts, 'alerts_count':alerts_count, 'cycle_filter':len(cycle_filter)}

        return render(request, 'main/evaluatorhome.html', context)


@login_required
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

    cust_student_list = []
    for stu in custom_students.objects.filter(graded=False):
        for evaluator in stu.measure.evaluator.all():
            if (evaluator.email == request.user.email):
                cust_student_list.append(stu)

    for stu in cust_student_list:
        print(stu.student_name, stu.evaluator)
    final_cust=[]
    for st in cust_student_list:
        if st.measure==measures:
            final_cust.append(st)
    for st in final_cust:
        print(st.student_name)

    maximum_rows = rubric.max_col
    cat_index = range(1, maximum_rows)
    if rubric.isWeighted:
        cat_index=range(1,maximum_rows-1)

    super_cat=[]
    for cat in categories:
        if cat.rubric==rubric:
            if cat.index_y in cat_index and cat.index_x==0:
                super_cat.append(cat.categoryTitle)
    alerts = Broadcast.objects.filter(receiver=request.user.email, read=False).order_by('-sent_at')
    alerts_count = alerts.count()
    print(len(final_cust))

    context = { 'measures':measures, 'students':students, 'measure_id':measure_id, 'rubric':rubric, 'categories':categories
                ,'row_num':range(rubric.max_row), 'col_num': range(rubric.max_col), 'evaluated_flag':final_cust,'super_cat':super_cat,
                'alerts':alerts, 'alerts_count':alerts_count, 'flag_count':len(final_cust)}
    return render(request, 'main/evaluator_rubric_select.html', context)



def evaluator_test_select(request, measure_id):
    measures = Measure.objects.get(id=measure_id)
    test = measures.test_score
    email = request.user.email
    evaluator = Evaluator.objects.filter(email=email)[0]
    evaluations = custom_students.objects.filter(evaluator=evaluator, measure=measures)
    evaluations_count = custom_students.objects.filter(evaluator=evaluator, measure=measures, graded=False).count()
    print(evaluations_count)
    context = {'measure':measures, 'test':test, 'evaluations':evaluations, 'measure_id':measure_id, 'evaluations_count':evaluations_count}
    return render(request, 'main/evaluator_test_select.html', context)


def edit_test_score(request, measure_id, student_name):
    measures = Measure.objects.get(id=measure_id)
    test = measures.test_score
    email = request.user.email
    evaluator = Evaluator.objects.filter(email=email)[0]
    student = custom_students.objects.get(evaluator=evaluator, measure=measures, student_name=student_name)
    context = {'measure':measures, 'test':test, 'student':student, 'measure_id':measure_id}
    return render(request, 'main/edit_test_select.html', context)


def evaluate_students(request):
    return render(request, 'main/evaluate_students.html')


def add_test_score_evaluator(request,measure_id):
    measure = Measure.objects.filter(id=measure_id)
    test_name = request.POST.get('test_title')
    student_id = request.POST.get('student_to_be_evaluated')
    email = request.user.email
    evaluator = Evaluator.objects.filter(email=email)[0]
    measures = Measure.objects.get(id=measure_id)


    score = request.POST.get('score')
    student_score = custom_students.objects.filter(id=student_id, evaluator=evaluator, measure=measures)
    student_score.update(grade=score, graded=True)

    student = Student.objects.create(name=custom_students.objects.get(id=student_id).student_name)

    msg = evaluator.name + ' evaluated '+ student.name
    Notification.objects.create(message=msg, created_at = datetime.today(), to = evaluator.invited_by)


    test_score_student = Test_score.objects.create(student=student, score=score, test=test_name)
    Measure.objects.filter(id=measure_id).update(test_score=test_score_student)

    return HttpResponseRedirect(reverse_lazy('main:evaluator_test_select',kwargs={'measure_id':measure_id}))


@user_passes_test(admin_test)
def dashboard(request):
    cordinator = CoOrdinator.objects.get(email=request.user.email)
    dept = cordinator.dept
    outcomes = Outcome.objects.filter(dept=dept)
    measures = Measure.objects.filter(dept=dept)
    cycles = Cycle.objects.filter(dept=dept)
    eval_a = Evaluator.objects.filter(dept=dept)
    courses = Course.objects.filter(dept=dept)

    for ev in Evaluator.objects.filter(dept=dept):
        perc_update(ev)

    data = dict()
    for measure in measures:
        evaluations = evaluate_rubric.objects.filter(measure=measure).count()
        if(evaluations>0):
            if measure.tool_type == 'Rubric':
                data.update({measure.id: rubric_data(measure.id)})
            elif measure.tool_type == 'Test score':
                data.update({measure.id: test_score_data(measure.test_score, measure.id)})

    cyc = Cycle.objects.filter(dept=dept)
    mycyc = 0
    for cycles in cyc:
        if (cycles.isCurrent):
            mycyc = cycles
    outcome_a = Outcome.objects.filter(dept=dept)
    outcome_list = []
    for oc in outcome_a:
        for v in oc.cycle.all():
            if (v == mycyc):
                outcome_list.append(oc)
    measure_a = Measure.objects.filter(dept=dept)
    measure_list = []
    for me in measure_a:
        for o in outcome_list:
            if (me.outcome == o):
                measure_list.append(me)
    evaluator_list = []
    for eval in eval_a:
        for mymea in measure_list:
            for eval_more in mymea.evaluator.all():
                if (eval == eval_more):
                    evaluator_list.append(eval)
    evaluator_list = Evaluator.objects.filter(dept = dept)

    msgs = Broadcast.objects.filter(receiver=request.user.email).order_by('-sent_at')
    context = {'evaluator': evaluator_list, 'dashboard':'active', 'outcomes':outcomes, 'measures':measures, 'data':data, 'cordinator':cordinator,
            'notification_count' : Notification.objects.filter(read=False, to=request.user.email).count(),
            'notifications' : Notification.objects.filter(read=False, to=request.user.email).order_by('-created_at'), 'cycles':cyc,'mycyc':mycyc,'courses':courses,
            'msgs':msgs,'msgs_count': Broadcast.objects.filter(receiver=request.user.email, read=False).order_by('-sent_at').count()
            }
    return render(request, 'main/adminhome.html', context)

@login_required
def newCycle(request):
    cordinator = CoOrdinator.objects.get(email=request.user.email)
    dept = cordinator.dept
    year = request.POST.get('year')
    semester = request.POST.get('semester')
    today = datetime.today()

    cycle = Cycle(year=year, semester=semester, startDate=today, coordinator=cordinator, dept=dept)
    cycle.save()
    messages.add_message(request, messages.SUCCESS, 'Cycle created successfully')

    text = cordinator.name + " ( " + cordinator.email + " ) " + 'created a new cycle, ' + cycle.year + " " + cycle.semester
    Log.objects.create(message=text, created_at=datetime.today(), subject=cordinator.dept, cor=cordinator.email)

    url = request.POST.get("url")
    return redirect(url)
    return HttpResponseRedirect(reverse_lazy('main:dashboard'))

@user_passes_test(admin_test)
def cycle(request, cycle_id):
    cordinator = CoOrdinator.objects.get(email=request.user.email)
    dept = cordinator.dept
    outcomes = Outcome.objects.filter(cycle=cycle_id)
    evaluators = Evaluator.objects.filter(dept=dept)
    measures = Measure.objects.filter(dept=dept)
    rubrics = Rubric.objects.filter(dept=dept)
    cycle = Cycle.objects.get(id=cycle_id)
    prev= Cycle.objects.all()
    courses = Course.objects.filter(dept=dept)
    prev_cycles = []
    for cy in prev:
        if cy.coordinator==cordinator and cy != cycle:
            prev_cycles.append(cy)
    all_outcomes = Outcome.objects.filter(dept=dept)


    for outcome in outcomes:
        flag, pending_flag = outcome_test(outcome.id)
        if not pending_flag:
            Outcome.objects.filter(id=outcome.id).update(status=flag)
            if flag:
                Outcome.objects.filter(id=outcome.id).update(status_help='passing')
            else:
                Outcome.objects.filter(id=outcome.id).update(status_help='failing')

    msgs = Broadcast.objects.filter(receiver=request.user.email).order_by('-sent_at')

    context = {'cordinator':cordinator,'evaluator': Evaluator.objects.all(),'cycle_id':cycle_id, 'outcomes': outcomes, 'evaluators': evaluators,
                'measures': measures, 'rubrics': rubrics, 'cycle':cycle, 'prev_cycles':prev_cycles, 'all_outcomes': all_outcomes,
                'courses':courses,'notification_count' : Notification.objects.filter(read=False, to=request.user.email).count(),
                'notifications' : Notification.objects.filter(read=False, to=request.user.email).order_by('-created_at'), 'msgs':msgs
                ,'msgs_count': Broadcast.objects.filter(receiver=request.user.email, read=False).order_by('-sent_at').count()}
    return render(request, 'main/cycle.html', context)

@user_passes_test(admin_test)
def end_cycle(request, cycle_id):
    cycle = Cycle.objects.filter(id=cycle_id).update(isCurrent=False, endDate=datetime.today())

    cycle_d = Cycle.objects.get(id=cycle_id)

    measures = Measure.objects.all()
    outcomes = Outcome.objects.all()
    for oc in outcomes:
        for cyc in oc.cycle.all():
            print(oc)
            if cyc == cycle_d:
                for me in measures:
                    if me.outcome==oc:
                        Measure.objects.filter(id=me.id).update(current=False)


    text = request.user.username + " ( " + request.user.email + " ) " + 'ended the cycle, ' + str(cycle_d.year) + ' ' + cycle_d.semester
    Log.objects.create(message=text, created_at=datetime.today(), cor=request.user.email)

    messages.add_message(request, messages.WARNING, 'Cycle was deleted successfully')

    return HttpResponseRedirect(reverse_lazy('main:dashboard'))

def migrate_cycle(request, cycle_id):
    cordinator = CoOrdinator.objects.get(email=request.user.email)
    dept = cordinator.dept
    from_cycle_id = request.POST.get('cycle_migrate')
    from_cycle = Cycle.objects.get(id=from_cycle_id)
    outcomes = Outcome.objects.filter(cycle=from_cycle)

    to_cycle = Cycle.objects.get(id = cycle_id)

    for outcome in outcomes:
        measures = Measure.objects.filter(outcome = outcome)
        new_outcome = Outcome.objects.create(title=outcome.title, status = outcome.status, dept=dept)
        new_outcome.cycle.add(to_cycle)
        for mea in measures:
            new_measure = Measure(measureTitle= mea.measureTitle,
                      cutoff_score= mea.cutoff_score,cutoff_percentage= mea.cutoff_percentage,
                      outcome=new_outcome, tool_type=mea.tool_type, cutoff_type=mea.cutoff_type,coordinator=cordinator,dept=dept)
            new_measure.save()
            if mea.tool_type=='Rubric':
                Measure.objects.filter(id=new_measure.id).update(rubric=mea.rubric)
            elif mea.tool_type=='Test score':
                Measure.objects.filter(id=new_measure.id).update(test_score=mea.test_score)

    text = cordinator.name + " ( " + cordinator.email + " ) " + 'bulk migrated data from ' + str(from_cycle.year) + ' ' + str(from_cycle.semester) + ' to ' + str(to_cycle.year) + ' ' + str(to_cycle.semester)
    Log.objects.create(message=text, created_at=datetime.today(), subject = cordinator.dept, cor=cordinator.email)


    return HttpResponseRedirect(reverse('main:cycle', kwargs={'cycle_id':cycle_id}) )

def migrate_outcome(request, cycle_id):
    from_outcome_list = request.POST.getlist('outcomes')
    to_cycle = Cycle.objects.get(id=cycle_id)
    cordinator = CoOrdinator.objects.filter(email=request.user.email)[0]
    dept = cordinator.dept

    for outcomes in from_outcome_list:
        measures = Measure.objects.filter(outcome=outcomes)
        outcome = Outcome.objects.get(id = outcomes)
        new_outcome = Outcome.objects.create(title=outcome.title, status = outcome.status, dept=dept)
        new_outcome.cycle.add(to_cycle)

        for mea in measures:
            new_measure = Measure(measureTitle= mea.measureTitle,
                      cutoff_score= mea.cutoff_score,cutoff_percentage= mea.cutoff_percentage,
                      outcome=new_outcome, tool_type=mea.tool_type, cutoff_type=mea.cutoff_type,coordinator=cordinator,dept=dept)
            new_measure.save()
            if mea.tool_type=='Rubric':
                Measure.objects.filter(id=new_measure.id).update(rubric=mea.rubric)
            elif mea.tool_type=='Test score':
                Measure.objects.filter(id=new_measure.id).update(test_score=mea.test_score)

        for m in Measure.objects.all():
            if m.outcome == outcome:
                Measure.objects.filter(id=m.id).update(current=True)
        text = request.user.username + " ( " + request.user.email + " ) " + 'migrated outcome, '+ outcome.title + ' to the cycle, ' + str(to_cycle.year) +  " " + str(to_cycle.semester)
        Log.objects.create(message=text, created_at=datetime.today(), cor=request.user.email)

    return HttpResponseRedirect(reverse('main:cycle', kwargs={'cycle_id':cycle_id}) )

def migrate_measure(request, outcome_id, cycle_id):
    outcome = Outcome.objects.get(id=outcome_id)
    cordinator = CoOrdinator.objects.filter(email=request.user.email)[0]
    dept = cordinator.dept

    measures_to_add = request.POST.getlist('measures')
    for m_id in measures_to_add:
        measure = Measure.objects.get(id=m_id)
        new_measure = Measure.objects.create(measureTitle= measure.measureTitle,
                  cutoff_score= measure.cutoff_score,cutoff_percentage= measure.cutoff_percentage,
                  outcome=outcome, tool_type=measure.tool_type, cutoff_type=measure.cutoff_type, dept=dept)
        text = request.user.username + " ( " + request.user.email + " ) " + 'migrated measure, '+ measure.measureTitle + ' to a new cycle'
        Log.objects.create(message=text, created_at=datetime.today(), cor=request.user.email)
    return HttpResponseRedirect(reverse_lazy('main:outcome_detail', kwargs={'outcome_id':outcome_id}))




def reactivate_cycle(request, cycle_id):
    cycle = Cycle.objects.filter(id=cycle_id).update(isCurrent=True, endDate=None)
    cycle_r = Cycle.objects.get(id=cycle_id)
    text = request.user.username + " ( " + request.user.email + " ) " + 'reactivated the old cycle, '+ str(cycle_r.year) + ' ' + str(cycle_r.semester)
    Log.objects.create(message=text, created_at=datetime.today(), cor=request.user.email)

    return HttpResponseRedirect(reverse('main:dashboard'))



def outcome_detail(request, outcome_id):
    cordinator = CoOrdinator.objects.get(email=request.user.email)
    dept = cordinator.dept
    outcome = Outcome.objects.get(id=outcome_id)
    cycle_id = None
    for cyc in outcome.cycle.all():
        cycle_id = cyc.id
    print(cycle_id)
    measures = Measure.objects.filter(outcome=outcome)
    all_measures = Measure.objects.filter(dept=dept)
    rubrics = Rubric.objects.filter(dept=dept)
    students = None
    evaluators = Evaluator.objects.filter(dept=dept)
    num_of_evaluations = []
    test_data = {}
    data = {}
    custom_student = None
    for measure in measures:
        students = measure.student.all()
        evaluations = evaluate_rubric.objects.filter(measure=measure).count()
        if(evaluations>0):
            num_of_evaluations.append(measure.measureTitle)

        if measure.tool_type == 'Rubric':
            if measure.rubric:
                if len(num_of_evaluations)  > 0:
                    data = rubric_data(measure.id)
                    if(data['percent_pass_cases']>=measure.cutoff_percentage):
                        Measure.objects.filter(id=measure.id).update(status='passing', statusPercent = data['percent_pass_cases'])
                    else:
                        Measure.objects.filter(id=measure.id).update(status='failing', statusPercent = data['percent_pass_cases'])



        if measure.tool_type=='Test score':
            if measure.test_score!= None and custom_students.objects.filter(measure=measure, graded=True, current=True).count()>0:
                test_data = test_score_data(measure.test_score.test, measure.id)

                if test_data['passed']==True:
                     Measure.objects.filter(id=measure.id).update(status='passing', statusPercent = test_data['percentage'])
                else:
                     Measure.objects.filter(id=measure.id).update(status='failing', statusPercent = test_data['percentage'])

    msgs = Broadcast.objects.filter(receiver=request.user.email).order_by('-sent_at')


    context = {'cordinator':cordinator,'evaluator': Evaluator.objects.filter(dept=dept),'outcome_id': outcome_id, 'outcome': outcome, 'measures': measures, 'rubrics':rubrics,
                'students': students, 'evaluators': evaluators, 'num_of_evaluations':num_of_evaluations, 'all_measures':all_measures,
                'test_data':test_data, 'rubric_data':data, 'custom_student': custom_student, 'cycle_id':cycle_id,
                'notification_count' : Notification.objects.filter(read=False, to=request.user.email).count(),
                'notifications' : Notification.objects.filter(read=False, to=request.user.email).order_by('-created_at'), 'msgs':msgs,
                'msgs_count': Broadcast.objects.filter(receiver=request.user.email, read=False).order_by('-sent_at').count()}
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

        email = request.user.email
        for eval in Evaluator.objects.all():
            if eval.email == email:
                evaluator = eval
            else:
                evaluator = Evaluator.objects.create(email=email)

        for column in csv.reader(io_string, delimiter=",", quotechar="|"):
            total_points += int(column[1])
            student = Student.objects.create(name=column[0])
            student_score = Test_score(student=student, test=test_name, score=int(column[1]))
            student_score.save()
            custom_students.objects.create(measure=Measure.objects.get(id=measure_id), student_name = column[0], grade=int(column[1]), graded=True, evaluator = evaluator )
            measure.update(test_score=student_score)

        for m in measure:
            if m.tool_type=='Test score':
                if m.test_score!= None and custom_students.objects.filter(measure=m, graded=True, current=True).count()>0:
                    test_data = test_score_data(m.test_score.test, m.id)

                    if test_data['passed']==True:
                        Measure.objects.filter(id=m.id).update(status='passing', statusPercent = test_data['percentage'])
                    else:
                        Measure.objects.filter(id=m.id).update(status='failing', statusPercent = test_data['percentage'])


        number_of_students = Test_score.objects.filter(test=test_name).count()
        average = total_points / number_of_students


        messages.add_message(request, messages.SUCCESS, 'Test data uploaded with success')


        return HttpResponseRedirect(reverse_lazy('main:outcome_detail', kwargs={'outcome_id':outcome_id}))

    return HttpResponseRedirect(reverse_lazy('main:outcome_detail', kwargs={'outcome_id':outcome_id}))

def add_test_score(request,measure_id, outcome_id):
    measure = Measure.objects.filter(id=measure_id)
    test_name = request.POST.get('test_title')
    student_name = request.POST.get('student_name')
    student = Student.objects.create(name=student_name)

    score = request.POST.get('score')
    student_score = Test_score(student=student, test=test_name, score=score)
    student_score.save()


    cust_stu  = custom_students(student_name=student_name,measure=Measure.objects.get(id=measure_id), grade=score, graded=True)
    cust_stu.save()

    measure.update(test_score=student_score)
    for m in measure:
        if m.tool_type=='Test score':
            if m.test_score!= None and custom_students.objects.filter(measure=m, graded=True, current=True).count()>0:
                test_data = test_score_data(m.test_score.test, m.id)

                if test_data['passed']==True:
                    Measure.objects.filter(id=m.id).update(status='passing', statusPercent = test_data['percentage'])
                else:
                    Measure.objects.filter(id=m.id).update(status='failing', statusPercent = test_data['percentage'])


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
            messages.add_message(request, messages.SUCCESS, 'Please check your credentials')
            return render(request, 'main/register.html', {'form': form})

    else:
        form = RegisterForm()
        return render(request, 'main/register.html', {'form': form})


def registerCo(request):
    if request.method == "POST":
        form = CoOrdinatorRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            dept = form.cleaned_data.get('department')
            myinvited = InvitedCo.objects.filter(email=email)[0]
            co = CoOrdinator(name=username, email=email, department=dept, dept=myinvited.dept)
            co.save()
            messages.success(request, 'Account created')
            inv = InvitedCo.objects.filter(email=email)[0]
            print(email)
            print(inv)
            inv.pending = False
            inv.save()
            text = inv.email + ' accepted your invitation'
            Log.objects.create(message=text, created_at=datetime.today(), subject=inv.dept, cor=inv.email)
            return redirect('/')
        else:
            messages.add_message(request, messages.SUCCESS, 'Please check your credentials')
            return render(request, 'main/registerCo.html', {'form': form})

    else:
        form = CoOrdinatorRegisterForm()
        return render(request, 'main/registerCo.html', {'form': form})


def add_learning_outcome(request, cycle_id):
    cordinator = CoOrdinator.objects.get(email=request.user.email)
    dept = cordinator.dept
    title = request.POST.get('outcome_title')
    desc = request.POST.get('outcome_desc')
    outcome = Outcome(title=title, desc=desc,coordinator=cordinator,dept=dept)
    outcome.save()

    course_id = request.POST.getlist('course')
    for c_id in course_id:
        found_course = Course.objects.get(id=c_id)
        outcome.course.add(found_course)

    cycle_found = Cycle.objects.get(id=cycle_id)
    outcome.cycle.add(cycle_found)

    text = cordinator.name + " ( " + cordinator.email + " ) " + 'added a new learning outcome, '+ outcome.title + ' to the cycle, ' + str(cycle_found.year) + " " + str(cycle_found.semester)
    Log.objects.create(message=text, created_at=datetime.today(), subject=cordinator.dept, cor=cordinator.email)


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

    text = request.user.username + " ( " + request.user.email + " ) " + 'updated the measure, '+ Measure.objects.get(id=measure_id).measureTitle
    Log.objects.create(message=text, created_at=datetime.today(), cor=request.user.email)


    url = request.POST.get("url")
    return redirect(url)

    return render(request, 'main/cycle.html')

def new_measure(request, outcome_id):
    cordinator = CoOrdinator.objects.get(email=request.user.email)
    dept = cordinator.dept
    measure_title = request.POST.get('measure_title')
    cutoff_score = request.POST.get('cutoff_score')
    cutoff_percent = request.POST.get('cutoff_percent')
    tool_type = request.POST.get('tool_selection')
    cutoff_type = request.POST.get('cutoff_selection')

    outcome_found = Outcome.objects.get(id=outcome_id)
    measure = Measure(measureTitle= measure_title,
                      cutoff_score= cutoff_score,cutoff_percentage= cutoff_percent,
                      outcome=outcome_found, tool_type=tool_type, cutoff_type=cutoff_type,coordinator=cordinator,dept=dept)
    measure.save()

    messages.add_message(request, messages.SUCCESS, 'New measure is added to the outcome')

    text = cordinator.name + " ( " + cordinator.email + " ) " + 'created a new measure, '+ measure.measureTitle
    Log.objects.create(message=text, created_at=datetime.today(), subject=cordinator.dept, cor=cordinator.email)


    url = request.POST.get("url")
    return redirect(url)
    return render(request, 'main/cycle.html')

def add_rubric_to_measure(request, measure_id, outcome_id):
    rubric_title = request.POST.get('select_rubric', None)
    rubric_found = Rubric.objects.filter(title = rubric_title)[0]
    measure = Measure.objects.filter(id=measure_id).update(rubric=rubric_found)

    messages.add_message(request, messages.SUCCESS, 'Rubric is now associated with the measure')

    return HttpResponseRedirect(reverse_lazy('main:outcome_detail', kwargs={'outcome_id':outcome_id}))

def delete_measure(request, measure_id):
    measure_d = Measure.objects.get(id=measure_id).measureTitle
    measure = Measure.objects.filter(id=measure_id).delete()
    messages.add_message(request, messages.WARNING, 'Measure was removed successfully')

    text = request.user.username + " ( " + request.user.email + " ) " + 'deleted a measure, ' + measure_d
    Log.objects.create(message=text, created_at=datetime.today(), cor=request.user.email)

    url = request.POST.get("url")
    return redirect(url)
    return render(request, 'main/cycle.html')

def add_test_to_measure(request, measure_id):
    return HttpResponseRedirect(reverse_lazy('main:upload'))

def test_rubric(request):
    rows = 0
    cols = 0
    cordinator = CoOrdinator.objects.get(email=request.user.email)

    if request.method == 'POST':
        rows = int(request.POST.get('rows'))
        cols = int(request.POST.get('cols'))
        weight = request.POST.get('weight')
        ascending = request.POST.get('asc')
        colminus = cols
        isWeighted = True
        isAscending =True
        col_index = 0
        if(weight=="no"):
            isWeighted=False
        if isWeighted:
            cols+=1
        if ascending=="descending":
            isAscending = False

        cols_ = range(0, cols)
        mylist = []
        for x in range(cols):
            if isAscending:
                mylist.append(x)
            else:
                if isWeighted:
                    myval = cols-x-1
                else:
                    myval = cols - x
                mylist.append(myval)
        return render(request, 'main/created_test_rubric.html', {'cordinator':cordinator,'rows':range(rows), 'cols':cols_,'row_num':rows, 'col_num': cols,'isWeighted':isWeighted,'colmin':colminus,'isAsc':isAscending,'col_ind':col_index,'mylist':mylist})
    return render(request, 'main/test_rubric.html', {'cordinator':cordinator})


def created_test_rubric(request):
    if request.method == 'POST':
        cordinator = CoOrdinator.objects.get(email=request.user.email)
        dept=cordinator.dept
        row_num = int(request.POST.get('row_num'))
        row_col = int(request.POST.get('col_num'))
        rubric_title = request.POST.get("rubric_title")
        isWeighted = request.POST.get("isWeighted")
        isAscending = request.POST.get("isAscending")
        rubric_new = Rubric(title=rubric_title, max_row=row_num, max_col=row_col,isWeighted=isWeighted,ascending=isAscending,coordinator=cordinator,dept=dept)
        rubric_new.save()
        for x in range(row_num):
            for y in range(row_col):
                text = request.POST.get(str(x)+str(y))
                category = Category(categoryTitle=text,index_x=x, index_y=y, rubric=rubric_new)
                category.save()

        messages.add_message(request, messages.SUCCESS, 'Successfull creation of rubric')

        text = request.user.username + " ( " + request.user.email + " ) " + 'created a new rubric, ' + rubric_new.title
        Log.objects.create(message=text, created_at=datetime.today(), cor=request.user.email)


    return HttpResponseRedirect(reverse_lazy('main:rubrics'))


def rubric_render(request, rubric_id):
    rubrics = Rubric.objects.filter(id=rubric_id)[0]
    categories = Category.objects.all()
    context = {'rubric': rubrics, 'categories':categories, 'row_num' : range(rubrics.max_row), 'row_col':range(rubrics.max_col)}
    return render(request, 'main/rubric_render_admin.html',context)

def edit_rubric(request, rubric_id):
    rubric_found = Rubric.objects.get(id=rubric_id)
    categories = Category.objects.all()
    rows = range(rubric_found.max_row)
    cols = range(rubric_found.max_col)

    if request.method == 'POST':
        rubric_title = request.POST.get('rubric_title')
        Rubric.objects.filter(id=rubric_id).update(title=rubric_title)
        for x in rows:
            for y in cols:
                text = request.POST.get(str(x)+str(y))
                category = Category.objects.filter(index_x=x,index_y=y,rubric=rubric_found )
                category.update(categoryTitle=text)

        messages.add_message(request, messages.SUCCESS, 'Successfully edited the rubric')

        text = request.user.username + " ( " + request.user.email + " ) " + 'edited the rubric, ' + rubric_found.title
        Log.objects.create(message=text, created_at=datetime.today(), cor=request.user.email)


        return HttpResponseRedirect(reverse_lazy('main:dashboard'))

    context={'rubric_id':rubric_id,'rubric':rubric_found,'rows': rows, 'cols': cols, 'categories':categories}
    return render(request, 'main/edit_rubric.html', context)

def add_individual_student(request, outcome_id, measure_id):
    student_name = request.POST.get('student_name')
    student = Student(name=student_name)
    student.save()

    measure = Measure.objects.get(id=measure_id)
    measure.student.add(student)

    messages.add_message(request, messages.SUCCESS, 'Successfully added Student added to the Measure')

    text = request.user.username + " ( " + request.user.email + " ) " + 'added students to  ' + measure.measureTitle
    Log.objects.create(message=text, created_at=datetime.today(), cor=request.user.email)


    return HttpResponseRedirect(reverse_lazy('main:outcome_detail', kwargs={'outcome_id':outcome_id}))

def delete_student(request, outcome_id, measure_id, student_id):
    student = Student.objects.get(id=student_id)
    measure = Measure.objects.get(id=measure_id)
    measure.student.remove(student)
    messages.add_message(request, messages.SUCCESS, 'Student deleted')
    for st in custom_students.objects.all():
        if(st.student_name==student.name and st.measure==measure):
            st.delete()

    return HttpResponseRedirect(reverse_lazy('main:outcome_detail', kwargs={'outcome_id':outcome_id}))


def upload_student(request, outcome_id, measure_id):
    if request.method=='POST' and request.FILES:
        measure = Measure.objects.get(id=measure_id)

        csvfile = request.FILES['csv_file']
        datset = csvfile.read().decode("UTF-8")
        io_string = io.StringIO(datset)

        for column in csv.reader(io_string, delimiter=",", quotechar="|"):

            student = Student(name=column[0], classification=column[1])
            # cust = custom_students(student_name=column[0],measure=measure)
            # cust.save()
            student.save()
            measure.student.add(student)


        messages.add_message(request, messages.SUCCESS, 'Successfully added Students to the Measure')

        text = request.user.username + " ( " + request.user.email + " ) " + 'added students via file upload to measure, ' + measure.measureTitle
        Log.objects.create(message=text, created_at=datetime.today(), cor=request.user.email)


        return HttpResponseRedirect(reverse_lazy('main:outcome_detail', kwargs={'outcome_id':outcome_id}))

    return HttpResponseRedirect(reverse_lazy('main:outcome_detail', kwargs={'outcome_id':outcome_id}))

def add_evaluator(request, outcome_id, measure_id):
    cordinator = CoOrdinator.objects.get(email=request.user.email);
    measure = Measure.objects.get(id=measure_id)
    evals = Evaluator.objects.all()
    dept = cordinator.dept
    flag = False
    if request.method == 'POST':
        for ev in evals:
            if ev.email == request.POST.get('evaluator_email'):
                evaluator = ev
                flag = True
        print(flag)
        if not flag:
            evaluator = Evaluator(name = request.POST.get('evaluator_name'), email=request.POST.get('evaluator_email'),coordinator=cordinator, invited_by=cordinator.email,dept=dept)
            evaluator.save()

        measure.evaluator.add(evaluator)
        email = request.POST.get('evaluator_email')
        email_send = EmailMessage('Regarding Measure Evaluation', 'Hi' + evaluator.name + ',\n' + ' please go to: \nhttps://evapp-wolfteam.herokuapp.com/register \nYou have been assigned some evaluations\n\n -'+ request.user.username, to=[email])
        email_send.send()
        messages.add_message(request, messages.SUCCESS, 'Successfully added Evaluator added to the Measure')

        text = request.user.username + " ( " + request.user.email + " ) " + 'added evaluators to measure, ' + measure.measureTitle
        Log.objects.create(message=text, created_at=datetime.today(), cor=request.user.email)



    return HttpResponseRedirect(reverse_lazy('main:outcome_detail', kwargs={'outcome_id':outcome_id}))

def add_preexisting_evaluator(request, outcome_id, measure_id):
    measure = Measure.objects.get(id=measure_id)

    if request.method == 'POST':
        evaluator_list = request.POST.getlist('evaluators')
        print(evaluator_list)
        for ev in evaluator_list:
            evaluator = Evaluator.objects.get(id=ev)
            measure.evaluator.add(evaluator)

            email = evaluator.email
            email_send = EmailMessage('Regarding Measure Evaluation', 'Hi, please go to: \nhttps://evapp-wolfteam.herokuapp.com/register/ \nYou have been assigned some evaluations\n\n -Admin', to=[email])
        email_send.send()
        messages.add_message(request, messages.SUCCESS, 'Successfully added Evaluator added to the Measure')

        text = request.user.username + " ( " + request.user.email + " ) " + 'added evaluators to measure, ' + measure.measureTitle
        Log.objects.create(message=text, created_at=datetime.today(), cor=request.user.email)



    return HttpResponseRedirect(reverse_lazy('main:outcome_detail', kwargs={'outcome_id':outcome_id}))




def update_outcome(request, outcome_id, cycle_id):
    new_outcome_text = request.POST.get('outcome_title')
    new_outcome_desc = request.POST.get('outcome_desc')
    outcome_course = request.POST.getlist('course')
    for course in outcome_course:
        outcome_found = Outcome.objects.get(id=outcome_id)
        course_found = Course.objects.get(id=course)
        outcome_found.course.add(course_found)
    outcome = Outcome.objects.filter(id = outcome_id).update(title = new_outcome_text, desc=new_outcome_desc)

    messages.add_message(request, messages.SUCCESS, 'Outcome was edited successfully')

    text = request.user.username + " ( " + request.user.email + " ) " + 'updated the outcome, ' + new_outcome_text
    Log.objects.create(message=text, created_at=datetime.today(), cor=request.user.email)


    return HttpResponseRedirect(reverse_lazy('main:cycle', kwargs={'cycle_id':cycle_id}))

def delete_outcome(request, outcome_id, cycle_id):
    title = Outcome.objects.get(id=outcome_id).title
    outcome = Outcome.objects.filter(id=outcome_id).delete()
    messages.add_message(request, messages.WARNING, 'Outcome was deleted successfully')

    text = request.user.username + " ( " + request.user.email + " ) " + 'deleted the outcome, ' + title
    Log.objects.create(message=text, created_at=datetime.today(), cor=request.user.email)


    return HttpResponseRedirect(reverse_lazy('main:cycle', kwargs={'cycle_id':cycle_id}))

def view_test_score(request, test_score_test, measure_id):
    cordinator = CoOrdinator.objects.get(email=request.user.email)
    print_data = test_score_data(test_score_test, measure_id)
    context = test_score_data(test_score_test, measure_id)
    context.update({'cordinator':cordinator,'msgs': Broadcast.objects.filter(receiver=request.user.email).order_by('-sent_at'),  'notification_count': Notification.objects.filter(read=False, to=request.user.email).count(),
     'notifications': Notification.objects.filter(read=False, to=request.user.email).order_by('-created_at'), 'print_data':print_data,
     'msgs':Broadcast.objects.filter(receiver=request.user.email).order_by('-sent_at'), 'msgs_count':Broadcast.objects.filter(receiver=request.user.email, read= False).order_by('-sent_at').count()})

    return render(request, 'main/test_scores.html', context)


def evaluate_single_student(request, rubric_row, rubric_id, measure_id):
    student_id = int(request.POST.getlist('student_to_be_evaluated')[0])
    print(student_id)
    student_real = custom_students.objects.get(id=student_id)
    student_name = student_real.student_name
    rub = Rubric.objects.get(id=rubric_id)
    rubric_name = Rubric.objects.get(id=rubric_id).title
    measure = Measure.objects.get(id=measure_id)
    categories=Category.objects.all()
    scores = []
    avg = 0
    total = 0
    count=0
    myscore=0

    maximum_rows = rub.max_col
    cat_index = range(1, maximum_rows)
    header = range(1,rub.max_col)
    if rub.isWeighted:
        cat_index = range(1,maximum_rows-1)
    super_cat = []
    for cat in categories:
        if cat.rubric == rub:
            if cat.index_y in cat_index and cat.index_x == 0:
                super_cat.append(cat.categoryTitle)

    super_header=[]
    for cat in categories:
        if cat.rubric==rub:
            if cat.index_x in header and cat.index_y==0:
                super_header.append(cat.categoryTitle)

    myvals = category_score.objects.filter(student=student_real)
    for vals in myvals:
        vals.delete()
    mysc = request.POST.getlist('cat_field')
    for x in range(0,rub.max_row-1):
        print(mysc[x])
        score = mysc[x]
        custom_cat = category_score(student=student_real, header=super_header[x], score=mysc[x])
        if score.isdigit():
            myscore = int(score)
        else:
            if rub.ascending:
                myscore=super_cat.index(score)+1
            else:
                myscore=len(super_cat)-super_cat.index(score)

        max_col = rub.max_col
        if rub.isWeighted:
            if score.isdigit():
                maximum = max(mysc)

            else:
                maximum=len(mysc)
            for cat in Category.objects.filter(rubric=rub):
                if cat.index_y==max_col-1:
                    if cat.index_x==x+1:
                        myscore = float(cat.categoryTitle)*int(myscore)/100.0
                        print(myscore)
        scores.append(myscore)
        total += float(myscore)
        count = count + 1
        custom_cat.save()
    if rub.isWeighted:
        avg = total
    else:
        avg = total/count
    evaluated = evaluate_rubric(rubric=rubric_name, grade_score=avg,
                student=student_name, measure=measure, evaluated_by = request.user.email)

    evaluated.save()
    eval = Evaluator.objects.filter(email=request.user.email)[0]
    print(eval)

    overall_assignments = custom_students.objects.filter(evaluator=eval).count()
    print(overall_assignments)
    completed_assignments = custom_students.objects.filter(evaluator=eval, graded=True).count()
    print(completed_assignments)
    perc_evaluated = (completed_assignments/overall_assignments) * 100.0
    print(perc_evaluated)
    eval.perc_completed = perc_evaluated

    student_real.graded=True
    student_real.grade = avg
    student_real.evaluator = eval
    student_real.save()
    flag = evaluation_flag(student_name=student_name, measure=measure)
    flag.save()

    msg = student_real.evaluator.name + ' evaluated '+ student_real.student_name
    Notification.objects.create(message=msg, created_at = datetime.today())


    messages.add_message(request, messages.SUCCESS, 'Student was evaluated successfully')

    return HttpResponseRedirect(reverse_lazy('main:homepage'))


def remove_rubric_association(request, measure_id, outcome_id):
    measure = Measure.objects.filter(id = measure_id)
    measure.update(rubric=None, statusPercent=0.0, current=False)
    custom_students.objects.filter(measure__in=measure, graded=True).update(current=False)


    messages.add_message(request, messages.SUCCESS, 'Removed rubric association')

    return HttpResponseRedirect(reverse_lazy('main:outcome_detail', kwargs={'outcome_id':outcome_id}))

def remove_test_association(request, measure_id, outcome_id):
    measure = Measure.objects.filter(id = measure_id)
    measure.update(test_score=None, statusPercent=0.0, current=False)
    custom_students.objects.filter(measure__in=measure, graded=True).update(current=False)

    messages.add_message(request, messages.SUCCESS, 'Removed test association')


    return HttpResponseRedirect(reverse_lazy('main:outcome_detail', kwargs={'outcome_id':outcome_id}))

def remove_evaluator_access(request, evaluator_id, measure_id, outcome_id):
    evaluator = Evaluator.objects.get(id=evaluator_id)
    measure = Measure.objects.get(id=measure_id)
    measure.evaluator.remove(evaluator)

    messages.add_message(request, messages.SUCCESS, 'Evaluator access removed')
    text = request.user.username + " ( " + request.user.email + " ) " + 'removed the evaluator, ' + evaluator.name + " ( " + evaluator.email + " ) from measure, " + measure.measureTitle
    Log.objects.create(message=text, created_at=datetime.today(), cor=request.user.email)


    return HttpResponseRedirect(reverse_lazy('main:outcome_detail', kwargs={'outcome_id':outcome_id}))

def view_rubric_data(request, measure_id):
    measure = Measure.objects.get(id=measure_id)
    cordinator = CoOrdinator.objects.get(email=request.user.email)

    context = rubric_data(measure_id)
    context.update({'cordinator':cordinator,'msgs': Broadcast.objects.filter(receiver=request.user.email).order_by('-sent_at'),  'notification_count': Notification.objects.filter(read=False, to=request.user.email).count(),
     'notifications': Notification.objects.filter(read=False, to=request.user.email).order_by('-created_at'),
     'msgs':Broadcast.objects.filter(receiver=request.user.email).order_by('-sent_at'), 'msgs_count':Broadcast.objects.filter(receiver=request.user.email, read=False).order_by('-sent_at').count()})

    return render(request, 'main/rubric_scores.html', context)

def past_assessments(request):
    evaluations = evaluate_rubric.objects.filter(evaluated_by=request.user.email).order_by('-id')

    email = request.user.email
    evaluator = Evaluator.objects.filter(email=email)
    if len(evaluator)==0:
        messages.add_message(request, messages.SUCCESS, 'No past assessments')
        return render(request, 'main/past_assessments.html', {})
    else:
        evaluator = evaluator[0]
    scores = custom_students.objects.filter(evaluator=evaluator, graded=True).order_by('-id')
    print(scores)
    alerts = Broadcast.objects.filter(receiver=request.user.email, read=False).order_by('-sent_at')
    alerts_count = alerts.count()
    cust_stu = custom_students.objects.filter(evaluator=evaluator)
    context = {'past':'active', 'evaluations': evaluations, 'scores':scores,
                'alerts':alerts, 'alerts_count':alerts_count,'cust_stu':cust_stu}
    return render(request, 'main/past_assessments.html', context)


def view_score(request,evaluation_id):
    evaluation_found = evaluate_rubric.objects.get(id=evaluation_id)
    measure = evaluation_found.measure
    email_eval = Evaluator.objects.filter(name=evaluation_found.evaluated_by)[0]
    mystudent = 0
    for stu in custom_students.objects.all():

        if (stu.measure == measure and stu.student_name == evaluation_found.student and stu.evaluator == email_eval):
            mystudent = stu
            mystudent.graded = False
    current_cat = category_score.objects.filter(student=mystudent)
    context = {'cats':current_cat}
    return render(request,'main/view_score.html',context)



def edit_evaluation_student(request,cust_id):
    mystudent = custom_students.objects.get(id=cust_id)
    measure = mystudent.measure
    measure_id = measure.id
    cat_score = category_score.objects.filter(student=mystudent)
    data = ["dummy"]
    for c_s in cat_score:
        data.append(c_s.score)
    print(data)
    measures = measure
    students = measures.student.all()
    rubric = measures.rubric
    categories = Category.objects.all()
    evaluations = evaluate_rubric.objects.all()
    evaluated_flag = []
    for stu in students:
        if evaluations.filter(student=stu.name, evaluated_by=request.user.username).exists():
            evaluated_flag.append(stu.name)

    cust_student_list = []
    for stu in custom_students.objects.all():
        for evaluator in stu.measure.evaluator.all():
            if (evaluator.email == request.user.email):
                cust_student_list.append(stu)
    final_cust = []
    for st in cust_student_list:
        if st.measure == measures:
            final_cust.append(st)

    maximum_rows = rubric.max_col
    cat_index = range(1, maximum_rows)
    if rubric.isWeighted:
        cat_index=range(1,maximum_rows-1)
    super_cat = []
    for cat in categories:
        if cat.rubric == rubric:
            if cat.index_y in cat_index and cat.index_x == 0:
                super_cat.append(cat.categoryTitle)
    context = {'measures': measures, 'mystudent':mystudent, 'measure_id': measure_id, 'rubric': rubric,
               'categories': categories, 'data':data
        , 'row_num': range(rubric.max_row), 'col_num': range(rubric.max_col), 'evaluated_flag': final_cust,
               'super_cat': super_cat}

    return render(request,'main/evaluator_edit_rubric_select.html',context)




def assign_evaluator(request, measure_id, outcome_id):
    measure = Measure.objects.get(id=measure_id)
    evaluator_email = request.POST.get('evaluator_email')
    students = request.POST.getlist('students')

    evaluator = Evaluator.objects.filter(email=evaluator_email)[0]

    for student in students:

        custom_student = custom_students(student_name = student, measure=measure, evaluator=evaluator, type=measure.tool_type)
        custom_student.save()
    messages.add_message(request, messages.SUCCESS, 'Assigned evaluator a task')

    text = request.user.username + " ( " + request.user.email + " ) " + 'assigned some tasks to the evaluator, ' + evaluator_email
    Log.objects.create(message=text, created_at=datetime.today(), cor=request.user.email)


    return HttpResponseRedirect(reverse_lazy('main:outcome_detail', kwargs={'outcome_id':outcome_id}))

def assign_evaluatorToTest(request, measure_id, outcome_id):
    measure = Measure.objects.get(id=measure_id)
    evaluator_email = request.POST.get('evaluator_email')
    students = request.POST.getlist('students')

    evaluator = Evaluator.objects.filter(email=evaluator_email)[0]
    measure.evaluator.add(evaluator)

    for student in students:
        custom_student = custom_students(student_name = student, measure=measure, evaluator=evaluator, type=measure.tool_type)
        custom_student.save()
    messages.add_message(request, messages.SUCCESS, 'Evaluator assigned to test')


    text = request.user.username + " ( " + request.user.email + " ) " + 'assigned some tasks to the evaluator, ' + evaluator_email
    Log.objects.create(message=text, created_at=datetime.today(), cor=request.user.email)

    return HttpResponseRedirect(reverse_lazy('main:outcome_detail', kwargs={'outcome_id':outcome_id}))

def broadcast(request):
    send_to = request.POST.getlist('evaluator')
    message = request.POST.get('message')
    for x in send_to:
        broadcast = Broadcast.objects.create(sender=request.user.username, receiver=x,message=message, sent_at=datetime.today())
    messages.add_message(request, messages.SUCCESS, 'Message sent')

    return HttpResponseRedirect(reverse_lazy('main:dashboard'))

def broadcast_super(request):
    send_to = request.POST.getlist('evaluator')
    message = request.POST.get('message')
    for x in send_to:
        broadcast = Broadcast.objects.create(sender=request.user.username, receiver=x,message=message, sent_at=datetime.today())
    messages.add_message(request, messages.SUCCESS, 'Message sent')


    return HttpResponseRedirect(reverse_lazy('main:super_admin_home'))


def create_curriculum(request):
    cordinator = CoOrdinator.objects.get(email=request.user.email)
    dept=cordinator.dept
    title = request.POST.get('title')
    description = request.POST.get('description')
    credit_hours = request.POST.get('credit_hours')
    Course.objects.create(title=title, description=description, credit_hours=credit_hours,coordinator=cordinator,dept=dept)
    messages.add_message(request, messages.SUCCESS, 'course object created')

    url = request.POST.get("url1")
    print("Url is",url)
    return redirect(url)
    return HttpResponseRedirect(reverse_lazy('main:dashboard'))

def mark_read(request, alert_id):
    alert = Broadcast.objects.filter(id=alert_id).order_by('-sent_at')
    alert.update(read=True)
    print(alert)
    messages.add_message(request, messages.SUCCESS, 'Message mark read')

    return HttpResponseRedirect(reverse_lazy('main:homepage'))



def delete_notification(request, notification_id):
    notification = Notification.objects.filter(id=notification_id)
    notification.update(read=True)
    print(request.build_absolute_uri())
    messages.add_message(request, messages.SUCCESS, 'Notifications removed with success')

    url = request.POST.get("url")
    return redirect(url)
    return HttpResponseRedirect(reverse_lazy('main:dashboard'))

def delete_notifications(request):
    notification = Notification.objects.all()
    notification.update(read = True)
    messages.add_message(request, messages.SUCCESS, 'Notifications removed with success')

    print(request.build_absolute_uri())
    url = request.POST.get("urls")
    return redirect(url)
    return HttpResponseRedirect(reverse_lazy('main:dashboard'))

def upload_test_score_evaluator(request, measure_id):

    if request.method=='POST' and request.FILES:
        measure = Measure.objects.filter(id=measure_id)
        evaluator = Evaluator.objects.filter(email=request.user.email)[0]
        students = custom_students.objects.filter(measure__in = measure, evaluator = evaluator)

        test_name = request.POST.get('test_title')
        max_points = request.POST.get('max_points')
        total_points = 0

        csvfile = request.FILES['csv_file']
        datset = csvfile.read().decode("UTF-8")
        io_string = io.StringIO(datset)

        for column in csv.reader(io_string, delimiter=",", quotechar="|"):
            total_points += int(column[1])
            student = Student.objects.create(name=column[0])
            for st in students:
                if st.student_name == student.name:
                    student_score = Test_score(student=student, test=test_name, score=int(column[1]))
                    student_score.save()
                    measure.update(test_score=student_score)
                    cust_st = custom_students.objects.filter(measure__in = measure, student_name=st.student_name, evaluator=evaluator)
                    cust_st.update(graded=True, grade=int(column[1]))

        number_of_students = Test_score.objects.filter(test=test_name).count()
        average = total_points / number_of_students

    return HttpResponseRedirect(reverse_lazy('main:homepage'))

def generate_outcome_report(request, outcome_id):
    cordinator = CoOrdinator.objects.get(email=request.user.email)

    outcome = Outcome.objects.get(id=outcome_id)
    measures = Measure.objects.filter(outcome=outcome)
    data = dict()
    evaluated_student_count = 0
    number_of_pass_cases = 0
    measure = None

    for measure in measures:
        evaluated_student_count = custom_students.objects.filter(measure=measure, grade__isnull = False, current=True).count()
        number_of_pass_cases = custom_students.objects.filter(measure=measure,grade__gte = measure.cutoff_score, current=True).count()
        data.update({ measure.id: [evaluated_student_count, number_of_pass_cases, measure.measureTitle, measure.statusPercent, measure.status]})
        print(data)
    if measure is None:
        context = {'cordinator':cordinator,'outcome': outcome, 'measures': measures, 'evaluated_student_count': evaluated_student_count,
                   'number_of_pass_cases': number_of_pass_cases,'mymeasure':measure,
                       'msgs':Broadcast.objects.filter(receiver=request.user.email, read=False).order_by('-sent_at'), 'msgs_count':Broadcast.objects.filter(receiver=request.user.email, read=False).order_by('-sent_at').count()}
    else:

        context = {'cordinator':cordinator,'outcome':outcome, 'measures':measures, 'evaluated_student_count':evaluated_student_count,
                   'number_of_pass_cases':number_of_pass_cases, 'data':data, 'measure_id':measure.id,
                   'count':measures.count()+1,'mymeasure':measure,
                       'msgs':Broadcast.objects.filter(receiver=request.user.email, read=False).order_by('-sent_at'), 'msgs_count':Broadcast.objects.filter(receiver=request.user.email, read=False).order_by('-sent_at').count()}

    return render(request, 'main/outcome_report.html', context)

def admin_instructions(request):
    cordinator = CoOrdinator.objects.get(email=request.user.email)
    return render(request, 'main/admin_instructions.html', {'notification_count' : Notification.objects.filter(read=False, to=request.user.email).count(),
    'notifications' : Notification.objects.filter(read=False, to=request.user.email).order_by('-created_at' ), 'cordinator':cordinator,
    'msgs':Broadcast.objects.filter(receiver=request.user.email, read=False).order_by('-sent_at'), 'msgs_count':Broadcast.objects.filter(receiver=request.user.email, read=False).order_by('-sent_at').count()})

def superadmin_instructions(request):
    return render(request, 'main/superadmin_instructions.html', {'notification_count' : Notification.objects.filter(read=False).count(),
    'notifications' : Notification.objects.filter(read=False).order_by('-created_at' ),'cordinator':InvitedCo.objects.all()})

def generate_cycle_report(request, cycle_id):
    cordinator = CoOrdinator.objects.get(email=request.user.email)

    cycle = Cycle.objects.get(id=cycle_id)
    outcomes = Outcome.objects.filter(cycle=cycle)
    data = dict()
    me = []
    count = 0
    num=0
    measures = None
    outcome = None


    for outcome in outcomes:
        measures = Measure.objects.filter(outcome=outcome)
        for measure in measures:
            evaluated_student_count = custom_students.objects.filter(measure=measure, grade__isnull = False, current=True).count()
            number_of_pass_cases = custom_students.objects.filter(measure=measure,grade__gte = measure.cutoff_score, current=True).count()
            count = count + 1
            me.append([evaluated_student_count, number_of_pass_cases,  outcome.title, measure.measureTitle,  measure.statusPercent, measure.status, Measure.objects.filter(outcome=outcome).count(), outcome.id])
    if(measures):
        num = measures.count()
    else:
        num = 0
    context ={'cordinator':cordinator,'outcomes':outcomes, 'measures':measures, 'cycle_id': cycle_id,
    'count':range(len(me)), 'data':me, 'outcome': outcome, 'num': num,
    'notification_count' : Notification.objects.filter(read=False, to=request.user.email).count(),
    'notifications' : Notification.objects.filter(read=False, to=request.user.email).order_by('-created_at'),
        'msgs':Broadcast.objects.filter(receiver=request.user.email, read=False).order_by('-sent_at'), 'msgs_count':Broadcast.objects.filter(receiver=request.user.email, read=False).order_by('-sent_at').count()


    }

    return render(request, 'main/cycle_report.html', context)

@user_passes_test(super_admin_test)
def super_admin_home(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        department = request.POST.get('department')
        name = request.POST.get('name')
        if CoOrdinator.objects.filter(email=email).exists():
            messages.add_message(request, messages.SUCCESS, 'Coordinator already exists')
        else:
            invited_Coordinator = Invited_Coordinator.objects.create(email=email, department=department, invited_by=request.user.username)
            flag = False
            for ob in Department.objects.all():
                if(ob.dept_name==department):
                    flag=True
            if flag:
                department = Department.objects.filter(dept_name=department)[0]
            else:
                department = Department.objects.create(dept_name=department)
            evaluators = Evaluator.objects.all()
            co = InvitedCo(email=email, pending=True, dept=department, name=name)
            co.save()
            email = co.email
            email_send = EmailMessage('Regarding Measure Evaluation:', 'Hi,' + str(co.name) + '\n You have been invited as a coordinator for '+ str(co.dept.dept_name) + ' department.\n Please visit and create an account at: \nhttps://evapp-wolfteam.herokuapp.com/registerCo \n Please sign up to continue.\n\n -'+ request.user.username, to=[email])
            email_send.send()

            for eval in evaluators:
                if eval.email == invited_Coordinator:
                    Invited_Coordinator.objects.filter(email=email, department=department).update(accepted=True)

            messages.add_message(request, messages.SUCCESS, 'Coordinator was invited successfully')
        print(Department.objects.all())

        context= {'now':'active','cordinator':InvitedCo.objects.all(), 'departments':Department.objects.all()}
        return render(request, 'main/invite.html', context)
    print(Department.objects.all())
    context= {'now':'active','cordinator':InvitedCo.objects.all(), 'departments':Department.objects.all()}
    return render(request, 'main/invite.html',context)

@user_passes_test(super_admin_test)
def super_admin_past(request):
    myinvitees = InvitedCo.objects.all().order_by('-id')
    invitees = Invited_Coordinator.objects.filter(invited_by=request.user.username).order_by('id')
    context = {'past':'active', 'invitees':invitees,'myinvitees':myinvitees,'cordinator':InvitedCo.objects.all()}
    return render(request, 'main/invite_status.html', context)

def outcome_test(outcome_id):
    outcome = Outcome.objects.get(id=outcome_id)
    measures = Measure.objects.filter(outcome = outcome)
    flag = True
    pending_flag = True
    for measure in measures:
        if measure.status == 'failing':
            flag = False
        if not measure.status == 'pending':
            pending_flag = False
    return (flag,pending_flag)

def cycle_report_test(cycle_id):
    cycle = Cycle.objects.get(id=cycle_id)
    outcomes = cycle.outcome.all()
    print(outcomes)
    return outcomes == None


def evaluator_instructions(request):
    return render(request, 'main/evaluator_instructions.html', {'alerts':Broadcast.objects.filter(receiver=request.user.email, read=False).order_by('-sent_at'),
    'alerts_count':Broadcast.objects.filter(receiver=request.user.email, read=False).order_by('-sent_at').count()})

@user_passes_test(super_admin_test)
def logs(request):
    logs = Log.objects.filter(read=False).order_by('-created_at')
    logs_count = logs.count()
    context = {"logs":logs, 'log':'active', 'logs_count':logs_count, 'cordinator':InvitedCo.objects.all()}
    return render(request, 'main/logs.html', context)

def clear_log(request):
    Log.objects.filter(read=False).update(read=True)
    logs = Log.objects.filter(read=False).order_by('-created_at')
    context = {"logs":logs, 'log':'active', }
    messages.add_message(request, messages.SUCCESS, 'Removed all the logs')

    return render(request, 'main/logs.html', context)

def clear_log_cor(request):
    cordinator = CoOrdinator.objects.get(email = request.user.email)
    dept = cordinator.dept
    dept_id = dept.id

    Log.objects.filter(read=False, subject=dept).update(read=True)
    logs = Log.objects.filter(read=False).order_by('-created_at')
    logs = Log.objects.filter(subject=dept,read=False)
    context={'logs':logs, 'cordinator':cordinator, 'log_dept':'active', 'dept_id':dept_id,
    'notification_count' : Notification.objects.filter(read=False, to=request.user.email).count(),
    'notifications' : Notification.objects.filter(read=False, to=request.user.email).order_by('-created_at' ),
     'msgs_count': Broadcast.objects.filter(receiver=request.user.email, read=False).order_by('-sent_at').count(),
    'msgs':Broadcast.objects.filter(receiver=request.user.email).order_by('-sent_at'), 'department_name':cordinator.department}

    return render(request, 'main/dept_log.html', context)


def download(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students.csv"'

    writer = csv.writer(response)
    writer.writerow(['Sanjiv', 'Senior'])
    writer.writerow(['Sagar', 'Sophomore'])
    writer.writerow(['Nick', 'Freshman'])
    writer.writerow(['AJ', 'Junior'])
    writer.writerow(['Alexa', 'Sophomore'])


    return response

def download_test(request, measure_id):
    measure = Measure.objects.get(id=measure_id)
    students = measure.student.all()
    print(students)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="test.csv"'

    writer = csv.writer(response)
    if students.count()>0:
        for student in students:
            writer.writerow([student.name, ])
    else:
        writer.writerow(['Alexa', 88])
        writer.writerow(['Sagar', 45])
        writer.writerow(['Nischal', 95])



    return response

def department_view(request, cordinator_id):
    cordinator = CoOrdinator.objects.get(id=cordinator_id)
    dept = cordinator.dept
    department_name = cordinator.department
    print(dept)
    cordinators = CoOrdinator.objects.filter(dept=dept)
    print(cordinators)
    for logs in Log.objects.filter(subject=dept):
        for co in cordinators:
            if(logs.cor==co.email):
                CoOrdinator.objects.filter(id=co.id).update(last_online=logs.created_at)

    context = {'cordinator':cordinator, 'dept_id':dept.id, 'list_dept':'active', 'cordinators':cordinators
    , 'notification_count' : Notification.objects.filter(read=False, to=request.user.email).count(),
    'notifications' : Notification.objects.filter(read=False, to=request.user.email).order_by('-created_at' ),
     'msgs_count': Broadcast.objects.filter(receiver=request.user.email, read=False).order_by('-sent_at').count(),
    'msgs':Broadcast.objects.filter(receiver=request.user.email).order_by('-sent_at'), 'department_name':department_name}
    return render(request, 'main/department_view.html', context)

def dept_log(request, dept_id):
    print(dept_id)
    cordinator = CoOrdinator.objects.get(email=request.user.email)
    department_name = cordinator.department
    department = Department.objects.get(id=dept_id)
    logs = Log.objects.filter(subject=department, read=False)
    context={'logs':logs, 'cordinator':cordinator, 'log_dept':'active', 'dept_id':dept_id,
    'notification_count' : Notification.objects.filter(read=False, to=request.user.email).count(),
    'notifications' : Notification.objects.filter(read=False, to=request.user.email).order_by('-created_at' ),
     'msgs_count': Broadcast.objects.filter(receiver=request.user.email, read=False).order_by('-sent_at').count(),
    'msgs':Broadcast.objects.filter(receiver=request.user.email).order_by('-sent_at'), 'department_name':department_name}
    return render(request, 'main/dept_log.html', context)


def assignments(request, evaluator_id, measure_id, outcome_id):
    cordinator = CoOrdinator.objects.get(email=request.user.email)
    measure = Measure.objects.get(id=measure_id)
    evaluator = Evaluator.objects.get(id=evaluator_id)
    custom_st = custom_students.objects.filter(evaluator=evaluator, measure=measure)
    context = {'cordinator':cordinator,'assignments':custom_st, 'evaluator':evaluator.name, 'measure_id':measure_id
                , 'outcome_id':outcome_id, 'evaluator_id':evaluator_id,'notification_count' : Notification.objects.filter(read=False, to=request.user.email).count(),
                'notifications' : Notification.objects.filter(read=False, to=request.user.email).order_by('-created_at' ),
                 'msgs_count': Broadcast.objects.filter(receiver=request.user.email, read=False).order_by('-sent_at').count(),
                'msgs':Broadcast.objects.filter(receiver=request.user.email).order_by('-sent_at')}
    return render(request, 'main/assignments.html', context)

def delete_assignment(request, assignment_id, evaluator_id, measure_id, outcome_id):
    custom_students.objects.filter(id=assignment_id).delete()
    cordinator = CoOrdinator.objects.get(email=request.user.email)
    measure = Measure.objects.get(id=measure_id)
    evaluator = Evaluator.objects.get(id=evaluator_id)
    custom_st = custom_students.objects.filter(evaluator=evaluator, measure=measure)
    context = {'cordinator':cordinator,'assignments':custom_st, 'evaluator':evaluator.name,
    'measure_id':measure.id, 'outcome_id':outcome_id, 'evaluator_id':evaluator.id,'notification_count' : Notification.objects.filter(read=False, to=request.user.email).count(),
    'notifications' : Notification.objects.filter(read=False, to=request.user.email).order_by('-created_at' ),
     'msgs_count': Broadcast.objects.filter(receiver=request.user.email, read=False).order_by('-sent_at').count(),
    'msgs':Broadcast.objects.filter(receiver=request.user.email).order_by('-sent_at')}

    return render(request, 'main/assignments.html', context)

def create_department(request):
    dept_name = request.POST.get('dept')
    Department.objects.create(dept_name=dept_name)

    return HttpResponseRedirect(reverse_lazy('main:super_admin_home'))
