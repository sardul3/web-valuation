# Generated by Django 2.1.1 on 2019-04-08 00:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_evaluate_rubric_evaluated_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='measure',
            name='measureText',
        ),
    ]
