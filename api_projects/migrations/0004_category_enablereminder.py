# Generated by Django 3.2.4 on 2021-08-19 05:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_projects', '0003_auto_20210816_1703'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='enableReminder',
            field=models.BooleanField(blank=True, db_column='enableReminder', null=True, verbose_name='enableReminder'),
        ),
    ]
