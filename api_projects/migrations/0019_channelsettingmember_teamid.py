# Generated by Django 3.2.4 on 2021-11-23 23:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_projects', '0018_project_totalclosinglead'),
    ]

    operations = [
        migrations.AddField(
            model_name='channelsettingmember',
            name='teamId',
            field=models.IntegerField(blank=True, db_column='teamId', null=True, verbose_name='Team Id'),
        ),
    ]