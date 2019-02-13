from django.contrib import admin
from .models import (Evaluator, Administrator,
                    Rubric, Objective, Measure)

# Register your models here.
admin.site.register(Evaluator)
admin.site.register(Administrator)
admin.site.register(Rubric)
admin.site.register(Objective)
admin.site.register(Measure)
