# Generated by Django 2.1.7 on 2019-05-04 03:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0047_remove_category_score_measure'),
    ]

    operations = [
        migrations.CreateModel(
            name='tempCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=200)),
                ('code', models.CharField(max_length=400)),
            ],
        ),
    ]
