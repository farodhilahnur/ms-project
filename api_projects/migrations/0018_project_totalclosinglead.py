# Generated by Django 3.2.4 on 2021-10-06 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_projects', '0017_customstatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='totalClosingLead',
            field=models.IntegerField(blank=True, db_column='totalClosingLead', default=0, null=True, verbose_name='total Closing Lead'),
        ),
    ]
