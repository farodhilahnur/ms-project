# Generated by Django 3.2.4 on 2022-01-25 09:05

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api_projects', '0021_alter_channel_leadrate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='createdAt',
            field=models.DateTimeField(blank=True, db_column='createdAt', default=django.utils.timezone.now, null=True, verbose_name='Created At'),
        ),
        migrations.AlterField(
            model_name='channel',
            name='createdAt',
            field=models.DateTimeField(blank=True, db_column='createdAt', default=django.utils.timezone.now, null=True, verbose_name='Created At'),
        ),
        migrations.AlterField(
            model_name='channelclick',
            name='createdAt',
            field=models.DateTimeField(blank=True, db_column='createdAt', default=django.utils.timezone.now, null=True, verbose_name='Created At'),
        ),
        migrations.AlterField(
            model_name='channelgroup',
            name='createdAt',
            field=models.DateTimeField(blank=True, db_column='createdAt', default=django.utils.timezone.now, null=True, verbose_name='Created At'),
        ),
        migrations.AlterField(
            model_name='channelsettingmember',
            name='createdAt',
            field=models.DateTimeField(blank=True, db_column='createdAt', default=django.utils.timezone.now, null=True, verbose_name='Created At'),
        ),
        migrations.AlterField(
            model_name='customstatus',
            name='createdAt',
            field=models.DateTimeField(blank=True, db_column='createdAt', default=django.utils.timezone.now, null=True, verbose_name='Created At'),
        ),
        migrations.AlterField(
            model_name='field',
            name='createdAt',
            field=models.DateTimeField(blank=True, db_column='createdAt', default=django.utils.timezone.now, null=True, verbose_name='Created At'),
        ),
        migrations.AlterField(
            model_name='form',
            name='createdAt',
            field=models.DateTimeField(blank=True, db_column='createdAt', default=django.utils.timezone.now, null=True, verbose_name='Created At'),
        ),
        migrations.AlterField(
            model_name='formfield',
            name='createdAt',
            field=models.DateTimeField(blank=True, db_column='createdAt', default=django.utils.timezone.now, null=True, verbose_name='Created At'),
        ),
        migrations.AlterField(
            model_name='project',
            name='createdAt',
            field=models.DateTimeField(blank=True, db_column='createdAt', default=django.utils.timezone.now, null=True, verbose_name='Created At'),
        ),
        migrations.AlterField(
            model_name='projectproduct',
            name='createdAt',
            field=models.DateTimeField(blank=True, db_column='createdAt', default=django.utils.timezone.now, null=True, verbose_name='Created At'),
        ),
        migrations.AlterField(
            model_name='projectstatus',
            name='createdAt',
            field=models.DateTimeField(blank=True, db_column='createdAt', default=django.utils.timezone.now, null=True, verbose_name='Created At'),
        ),
        migrations.AlterField(
            model_name='projectteam',
            name='createdAt',
            field=models.DateTimeField(blank=True, db_column='createdAt', default=django.utils.timezone.now, null=True, verbose_name='Created At'),
        ),
        migrations.AlterField(
            model_name='userproject',
            name='createdAt',
            field=models.DateTimeField(blank=True, db_column='createdAt', default=django.utils.timezone.now, null=True, verbose_name='Created At'),
        ),
    ]
