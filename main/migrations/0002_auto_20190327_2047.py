# Generated by Django 2.1.1 on 2019-03-28 01:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test_score',
            name='student',
            field=models.CharField(max_length=200),
        ),
    ]