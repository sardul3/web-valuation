# Generated by Django 2.1.1 on 2019-04-26 01:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0028_auto_20190423_2247'),
    ]

    operations = [
        migrations.AddField(
            model_name='outcome',
            name='desc',
            field=models.CharField(max_length=600, null=True),
        ),
    ]
