# Generated by Django 3.2.4 on 2022-01-27 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_projects', '0024_channel_channelurl'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channel',
            name='channelUrl',
            field=models.CharField(blank=True, db_column='channelUrl', max_length=1000, null=True, unique=True, verbose_name='Channel URL'),
        ),
    ]
