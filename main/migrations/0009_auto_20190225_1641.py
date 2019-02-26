# Generated by Django 2.1.1 on 2019-02-25 22:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_auto_20190225_1637'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rubric',
            name='measure',
        ),
        migrations.AddField(
            model_name='category',
            name='measure',
            field=models.ManyToManyField(to='main.Measure'),
        ),
        migrations.RemoveField(
            model_name='rubric',
            name='assigned_to',
        ),
        migrations.AddField(
            model_name='rubric',
            name='assigned_to',
            field=models.ManyToManyField(to='main.Evaluator'),
        ),
        migrations.RemoveField(
            model_name='rubric',
            name='category',
        ),
        migrations.AddField(
            model_name='rubric',
            name='category',
            field=models.ManyToManyField(to='main.Category'),
        ),
    ]
