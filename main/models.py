from django.db import models
from django.contrib.auth.models import  User

class Evaluator(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=200)

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

    def __str_(self):
        return self.year


class Category(models.Model):
    categoryTitle = models.CharField(max_length=200)

    def __str__(self):
        return self.categoryTitle

class Rubric(models.Model):
    title = models.CharField(max_length=200, blank=True, default="Untitled", primary_key=True)
    created_by = models.CharField(max_length=200)
    assigned_to = models.ManyToManyField(Evaluator)
    category = models.ManyToManyField(Category)

    def __str__(self):
        return self.title


class Outcome(models.Model):
    title = models.CharField(max_length=200, default='', null=True)
    status = models.BooleanField(default=True)
    cycle = models.ManyToManyField(Cycle)


class Test(models.Model):
    test_name = models.CharField(max_length=200, default='Test', primary_key=True)
    created_by = models.CharField(max_length=200)

class Test_score(models.Model):
    student = models.CharField(max_length=200, null=True)
    score = models.PositiveIntegerField()
    test = models.ForeignKey(Test, null=True, on_delete = models.CASCADE)

    def __str__(self):
        return self.student


class Measure(models.Model):
    measureTitle = models.CharField(max_length=200, default='', null=True)
    measureText = models.CharField(max_length=200, blank = True, null=True)
    outcome = models.ForeignKey(Outcome, null=True, on_delete = models.CASCADE)
    cutoff_percentage = models.FloatField(null=True, blank = True, default=0)
    cutoff_score = models.FloatField(null=True, blank=True, default=0)
    rubric = models.OneToOneField(Rubric,null=True, blank = True, on_delete = models.CASCADE)
    test_score = models.OneToOneField(Test, null=True, blank = True, on_delete = models.CASCADE)


class evaluate_rubric(models.Model):
    rubric = models.CharField(max_length=200)
    grade_score = models.FloatField()
    student = models.CharField(max_length=200)

    def __str__(self):
        out = self.student + " scored "+ self.grade_score + " in rubric: "+ self.rubric
        return out



