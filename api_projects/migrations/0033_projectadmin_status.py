# Generated by Django 3.2.4 on 2022-03-28 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_projects', '0032_projectadmin_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectadmin',
            name='status',
            field=models.CharField(blank=True, db_column='status', default='active', max_length=1000, null=True, verbose_name='Status'),
        ),
    ]
