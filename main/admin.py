from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Evaluator)
admin.site.register(models.Student)
admin.site.register(models.Rubric)
admin.site.register(models.Measure)
admin.site.register(models.Category)
admin.site.register(models.evaluate_rubric)
admin.site.site_header = "ULM Evaluation";
admin.site.site_title = "Ev App";
