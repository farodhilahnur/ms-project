# Generated by Django 3.2.4 on 2022-03-28 06:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_projects', '0031_auto_20220328_1258'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectadmin',
            name='email',
            field=models.CharField(blank=True, db_column='email', max_length=1000, null=True),
        ),
    ]
