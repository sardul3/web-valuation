from django.db import models
from django.contrib.auth.models import  User

class Evaluator(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=200)
    invited_by = models.CharField(max_length=200, default="Admin")
    perc_completed = models.FloatField(null=True,blank=True,default=0.0)

    def __str__(self):
        return self.name

class Student(models.Model):
    name = models.CharField(max_length=200)
    classification = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Cycle(models.Model):
    year = models.PositiveIntegerField()
    semester = models.CharField(max_length=200)
    startDate = models.DateField(default=None)
    endDate = models.DateField(default=None, null=True)
    isCurrent = models.BooleanField(default=True)

    def __str_(self):
        return self.year

class Rubric(models.Model):
    title = models.CharField(max_length=200, blank=True, default="Untitled")
    isWeighted = models.BooleanField(null=True, default=False)
    max_row = models.PositiveIntegerField(null=True)
    max_col = models.PositiveIntegerField(null=True)
    created_by = models.CharField(max_length=200)
    assigned_to = models.ManyToManyField(Evaluator)
    ascending = models.BooleanField(null=True, default=True)

    def __str__(self):
        return self.title


class Category(models.Model):
    categoryTitle = models.CharField(max_length=200)
    index_x = models.PositiveIntegerField(null=True)
    index_y = models.PositiveIntegerField(null=True)
    rubric = models.ForeignKey(Rubric, null=True, on_delete = models.CASCADE)

    def __str__(self):
        return self.categoryTitle


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    credit_hours = models.PositiveIntegerField(default=3)


class Outcome(models.Model):
    title = models.CharField(max_length=200, default='', null=True)
    status = models.BooleanField(default=True)
    cycle = models.ManyToManyField(Cycle)
    course = models.ManyToManyField(Course)

    def __str__(self):
        return self.title



class Test(models.Model):
    test_name = models.CharField(max_length=200, default='Test')
    created_by = models.CharField(max_length=200)

    def __str__(self):
        return self.test_name


class Test_score(models.Model):
    student = models.ForeignKey(Student, null=True, on_delete=models.CASCADE)
    score = models.PositiveIntegerField()
    test = models.CharField(max_length=200, default='Test', null=True, blank=True)

    def __str__(self):
        return self.test



class Measure(models.Model):
    CUTOFF_TYPES = (('Percentage', 'Percentage'),
                  ('Percentile', 'Percentile'),
                  ('Average', 'Average')
                 )
    cutoff_type = models.CharField(max_length = 100, choices=CUTOFF_TYPES, default='Percentage')

    TOOL_TYPES = (('Rubric', 'Rubric'),
                  ('Test score', 'Test score')
                  )
    tool_type = models.CharField(max_length=100, choices=TOOL_TYPES, default='Rubric')

    STATUS_TYPES = (('passing', 'passing'),
                    ('failing', 'failing'),
                    ('passed', 'passed'),
                    ('failed', 'failed')
                    )
    status = models.CharField(max_length=100, choices=STATUS_TYPES, default='failing')
    statusPercent = models.FloatField(default=0.0)
    evaluationPercent = models.FloatField(default=0.0)
    measureTitle = models.CharField(max_length=200, default='', null=True)
    outcome = models.ForeignKey(Outcome, null=True, on_delete = models.CASCADE)
    cutoff_percentage = models.FloatField(null=True, blank = True, default=0)
    cutoff_score = models.FloatField(null=True, blank=True, default=0)
    rubric = models.ForeignKey(Rubric,null=True, blank = True, on_delete = models.CASCADE)
    test_score = models.ForeignKey(Test_score, null=True, blank = True, on_delete = models.CASCADE)
    student = models.ManyToManyField(Student)
    evaluator = models.ManyToManyField(Evaluator)

    def __str__(self):
        return self.measureTitle



class evaluate_rubric(models.Model):
    rubric = models.CharField(max_length=200)
    grade_score = models.FloatField()
    student = models.CharField(max_length=200)
    measure = models.ForeignKey(Measure, null=True, on_delete=models.CASCADE)
    evaluated_by = models.CharField(max_length=200)


    def __str__(self):
        return self.student

class evaluation_flag(models.Model):
    student_name = models.CharField(max_length=200)
    measure = models.ForeignKey(Measure, on_delete=models.CASCADE)

class custom_students(models.Model):
    student_name = models.CharField(max_length=200)
    measure = models.ForeignKey(Measure,null=True,on_delete=models.CASCADE)
    evaluator = models.ForeignKey(Evaluator,null=True,on_delete=  models.CASCADE)
    graded = models.BooleanField(null=True,default=False)
    grade = models.FloatField(null=True)

class Broadcast(models.Model):
    sender = models.CharField(max_length=200)
    receiver = models.CharField(max_length=200)
    message = models.CharField(max_length=400)
    sent_at = models.DateTimeField()
    read = models.BooleanField(default=False)
