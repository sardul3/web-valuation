# Generated by Django 2.1.1 on 2019-03-28 03:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20190327_2249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outcome',
            name='title',
            field=models.CharField(max_length=200, null=True),
        ),
    ]