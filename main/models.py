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
    # outcome = models.ForeignKey(Outcome, on_delete=models.CASCADE)
    # rubrics = models.ForeignKey(Rubric, on_delete=models.CASCADE)

    def __str_(self):
        return self.year

class Measure(models.Model):
    measureTitle = models.CharField(max_length=200)
    measureText = models.CharField(max_length=200)
    weight = models.PositiveIntegerField(null=True, default=1)


    def __str__(self):
        return self.measureTitle

class Outcome(models.Model):
    title = models.CharField(max_length=200)
    measure = models.ForeignKey(Measure, on_delete=models.CASCADE)

    def __str__(self):
        return self.title



class Category(models.Model):
    categoryTitle = models.CharField(max_length=200)
    measure = models.ManyToManyField(Measure)

    def __str__(self):
        return self.categoryTitle


class Rubric(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    created_by = models.CharField(max_length=200)
    assigned_to = models.ManyToManyField(Evaluator)
    category = models.ManyToManyField(Category)

    def __str__(self):
        return self.title

class evaluate_rubric(models.Model):
    rubric = models.CharField(max_length=200)
    grade_score = models.FloatField()
    student = models.CharField(max_length=200)

    def __str__(self):
        out = self.student + " scored "+ self.grade_score + " in rubric: "+ self.rubric
        return out
