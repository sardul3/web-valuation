from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'main'

urlpatterns = [
    path('eval', views.homepage, name='homepage'),
    path('home', views.evaluatorhome, name='evaluatorhome'),
    path('broadcast', views.broadcast, name='broadcast'),
    path('mark_read/<int:alert_id>', views.mark_read, name='mark_read'),
    path('delete_notification/<int:notification_id>', views.delete_notification, name='delete_notification'),

    path('upload_test_score_evaluator/<int:measure_id>', views.upload_test_score_evaluator, name = 'upload_test_score_evaluator'),

    path('generate_outcome_report/<int:outcome_id>', views.generate_outcome_report, name = 'generate_outcome_report'),
         path('generate_cycle_report/<int:cycle_id>', views.generate_cycle_report, name = 'generate_cycle_report'),

     path('admin_instructions', views.admin_instructions, name = 'admin_instructions'),



    path('create_curriculum', views.create_curriculum, name = 'create_curriculum'),



    path('test_rubric/', views.test_rubric, name = 'test_rubric'),
    path('created_test_rubric/', views.created_test_rubric, name = 'created_test_rubric'),
    path('rubric_render/<int:rubric_id>', views.rubric_render, name = 'rubric_render'),

    path('edit_rubric/<int:rubric_id>', views.edit_rubric, name = 'edit_rubric'),

    path('edit_evaluation_student/<int:evaluation_id>', views.edit_evaluation_student, name='edit_evaluation_student'),
    path('view_score/<int:evaluation_id>', views.view_score, name='view_score'),
    path('evaluate_students/', views.evaluate_students, name = 'evaluate_students'),

    path('view_test_score/<str:test_score_test>/<int:measure_id>', views.view_test_score, name = 'view_test_score'),
    path('edit_test_score/<int:measure_id>/<str:student_name>', views.edit_test_score, name = 'edit_test_score'),


    path('assign_evaluator/<int:measure_id>/<int:outcome_id>', views.assign_evaluator, name = 'assign_evaluator'),
    path('assign_evaluatorToTest/<int:measure_id>/<int:outcome_id>', views.assign_evaluatorToTest, name = 'assign_evaluatorToTest'),


    path('evaluate_single_student/<int:rubric_row>/<int:rubric_id>/<int:measure_id>', views.evaluate_single_student, name = "evaluate_single_student"),

    path('remove_rubric_association/<int:measure_id>/<int:outcome_id>', views.remove_rubric_association, name = "remove_rubric_association"),
    path('remove_test_association/<int:measure_id>/<int:outcome_id>', views.remove_test_association, name = "remove_test_association"),

    path('view_rubric_data/<int:measure_id>', views.view_rubric_data, name = "view_rubric_data"),

    path('remove_evaluator_access/<int:evaluator_id>/<int:measure_id>/<int:outcome_id>', views.remove_evaluator_access, name = "remove_evaluator_access"),
    path('delete_student/<int:outcome_id>/<int:measure_id>/<int:student_id>', views.delete_student, name = "delete_student"),


    path('migrate_cycle/<int:cycle_id>', views.migrate_cycle, name = "migrate_cycle"),
    path('reactivate_cycle/<int:cycle_id>', views.reactivate_cycle, name = "reactivate_cycle"),




    path('add_individual_student/<int:outcome_id>/<int:measure_id>', views.add_individual_student, name = 'add_individual_student'),
    path('upload_student/<int:outcome_id>/<int:measure_id>', views.upload_student, name = 'upload_student'),

    path('evaluator_rubric_select/<int:measure_id>', views.evaluator_rubric_select, name = 'evaluator_rubric_select'),
        path('evaluator_test_select/<int:measure_id>', views.evaluator_test_select, name = 'evaluator_test_select'),


    path('outcome_detail/<int:outcome_id>', views.outcome_detail, name = 'outcome_detail'),


    path('update_outcome/<int:outcome_id>/<int:cycle_id>', views.update_outcome, name = 'update_outcome'),
    path('delete_outcome/<int:outcome_id>/<int:cycle_id>', views.delete_outcome, name = 'delete_outcome'),

    path('end_cycle/<int:cycle_id>', views.end_cycle, name = 'end_cycle'),


    path('outcomes', views.outcomes, name = 'outcomes'),
    path('rubrics', views.rubrics, name = 'rubrics'),
    path('cycles', views.cycles, name = 'cycles'),




    path('upload/<int:measure_id>/<int:outcome_id>', views.upload, name = 'upload'),
    path('add_test_score/<int:measure_id>/<int:outcome_id>', views.add_test_score, name = 'add_test_score'),
    path('add_test_score_evaluator/<int:measure_id>', views.add_test_score_evaluator, name = 'add_test_score_evaluator'),


    path('grade', views.grade, name = 'grade'),
    path('add_rubric_to_measure/<int:measure_id>/<int:outcome_id>', views.add_rubric_to_measure, name = 'add_rubric_to_measure'),

    path('past_assessments', views.past_assessments, name = 'past_assessments'),


    path('add_test_to_measure/<int:measure_id>', views.add_test_to_measure, name = 'add_test_to_measure'),
    path('update_measure/<int:measure_id>', views.update_measure, name="update_measure"),
    path('new_measure/<int:outcome_id>', views.new_measure, name="new_measure"),
    path('delete_measure/<int:measure_id>', views.delete_measure, name="delete_measure"),
    path('dashboard', views.dashboard, name = 'dashboard'),
    path('newCycle', views.newCycle, name = 'newCycle'),
    path('cycle/<int:cycle_id>', views.cycle, name = 'cycle'),
    # path('upload', views.upload, name='upload'),
    path('add_learning_outcome/<int:cycle_id>', views.add_learning_outcome, name="add_learning_outcome"),
    path('add_evaluator/<int:outcome_id>/<int:measure_id>', views.add_evaluator, name="add_evaluator"),
    path('register', views.register, name='register'),
    path('registerCo', views.registerCo, name='registerCo'),
    path('', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout', auth_views.LogoutView.as_view(template_name='main/logout.html'), name='logout'),


]
