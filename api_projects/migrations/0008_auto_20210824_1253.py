# Generated by Django 3.2.4 on 2021-08-24 05:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_projects', '0007_auto_20210824_1241'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='totalChannel',
            field=models.IntegerField(blank=True, db_column='totalChannel', default=0, null=True, verbose_name='totalChannel'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='totalLead',
            field=models.IntegerField(blank=True, db_column='totalLead', default=0, null=True, verbose_name='total Lead'),
        ),
        migrations.AlterField(
            model_name='channel',
            name='leadRate',
            field=models.CharField(blank=True, db_column='leadRate', default=0, max_length=100, null=True, verbose_name='lead_rate'),
        ),
        migrations.AlterField(
            model_name='channel',
            name='totalLead',
            field=models.IntegerField(blank=True, db_column='totalLead', default=0, null=True, verbose_name='total Lead'),
        ),
        migrations.AlterField(
            model_name='project',
            name='totalCampaign',
            field=models.IntegerField(blank=True, db_column='totalCampaign', default=0, null=True, verbose_name='total Campaign'),
        ),
        migrations.AlterField(
            model_name='project',
            name='totalGroup',
            field=models.IntegerField(blank=True, db_column='totalGroup', default=0, null=True, verbose_name='total Group'),
        ),
        migrations.AlterField(
            model_name='project',
            name='totalLead',
            field=models.IntegerField(blank=True, db_column='totalLead', default=0, null=True, verbose_name='total Lead'),
        ),
    ]
