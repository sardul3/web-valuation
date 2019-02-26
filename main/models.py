from django.db import models

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

class Measure(models.Model):
    measureTitle = models.CharField(max_length=200)
    measureText = models.CharField(max_length=200)
    weight = models.PositiveIntegerField(null=True, default=1)


    def __str__(self):
        return self.measureTitle


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
    rubric = models.ForeignKey(Rubric, on_delete=models.CASCADE)
    evaluator = models.ForeignKey(Evaluator, on_delete=models.CASCADE)
    grade_score = models.PositiveIntegerField()
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
