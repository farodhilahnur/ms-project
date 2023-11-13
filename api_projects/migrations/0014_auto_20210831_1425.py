# Generated by Django 3.2.4 on 2021-08-31 07:25

import api_projects.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_projects', '0013_auto_20210829_2046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='detail',
            field=models.CharField(blank=True, db_column='detail', max_length=1000, null=True, verbose_name='Detail'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='name',
            field=models.CharField(blank=True, db_column='name', max_length=1000, null=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='picture',
            field=models.CharField(blank=True, db_column='picture', max_length=1000, null=True, verbose_name='Picture'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='status',
            field=models.CharField(blank=True, db_column='status', default='running', max_length=1000, null=True, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='category',
            name='availability',
            field=models.CharField(blank=True, db_column='availability', max_length=1000, null=True, verbose_name='Availability'),
        ),
        migrations.AlterField(
            model_name='category',
            name='color',
            field=models.CharField(blank=True, db_column='color', max_length=1000, null=True, verbose_name='Color'),
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(blank=True, db_column='name', max_length=1000, null=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='category',
            name='picture',
            field=models.CharField(blank=True, db_column='picture', max_length=1000, null=True, verbose_name='Picture'),
        ),
        migrations.AlterField(
            model_name='channel',
            name='detail',
            field=models.CharField(blank=True, db_column='detail', max_length=1000, null=True, verbose_name='Detail'),
        ),
        migrations.AlterField(
            model_name='channel',
            name='distributionType',
            field=models.CharField(blank=True, db_column='distributionType', max_length=1000, null=True, verbose_name='Distribution Type'),
        ),
        migrations.AlterField(
            model_name='channel',
            name='leadRate',
            field=models.CharField(blank=True, db_column='leadRate', default=0, max_length=1000, null=True, verbose_name='lead_rate'),
        ),
        migrations.AlterField(
            model_name='channel',
            name='name',
            field=models.CharField(blank=True, db_column='name', max_length=1000, null=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='channel',
            name='picture',
            field=models.CharField(blank=True, db_column='picture', max_length=1000, null=True, verbose_name='Picture'),
        ),
        migrations.AlterField(
            model_name='channel',
            name='status',
            field=models.CharField(blank=True, db_column='status', default='running', max_length=1000, null=True, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='channel',
            name='uniqueCode',
            field=models.CharField(db_column='uniqueCode', default=api_projects.utils.get_uuid, editable=False, max_length=1000, unique=True),
        ),
        migrations.AlterField(
            model_name='channelmedia',
            name='name',
            field=models.CharField(blank=True, db_column='name', max_length=1000, null=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='channelmedia',
            name='picture',
            field=models.CharField(blank=True, db_column='picture', max_length=1000, null=True, verbose_name='Picture'),
        ),
        migrations.AlterField(
            model_name='channelmedia',
            name='type',
            field=models.CharField(blank=True, db_column='type', max_length=1000, null=True, verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='field',
            name='alias',
            field=models.CharField(blank=True, db_column='alias', max_length=1000, null=True, verbose_name='Alias'),
        ),
        migrations.AlterField(
            model_name='field',
            name='displayedas',
            field=models.CharField(blank=True, db_column='displayedas', max_length=1000, null=True, verbose_name='Displayedas'),
        ),
        migrations.AlterField(
            model_name='field',
            name='name',
            field=models.CharField(db_column='name', max_length=1000, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='field',
            name='type',
            field=models.CharField(blank=True, db_column='type', max_length=1000, null=True, verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='form',
            name='detail',
            field=models.CharField(blank=True, db_column='detail', max_length=1000, null=True, verbose_name='Detail'),
        ),
        migrations.AlterField(
            model_name='form',
            name='name',
            field=models.CharField(blank=True, db_column='name', max_length=1000, null=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='form',
            name='type',
            field=models.CharField(blank=True, db_column='type', max_length=1000, null=True, verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='media',
            name='name',
            field=models.CharField(db_column='name', max_length=1000, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='media',
            name='picture',
            field=models.CharField(blank=True, db_column='picture', max_length=1000, null=True, verbose_name='Picture'),
        ),
        migrations.AlterField(
            model_name='media',
            name='type',
            field=models.CharField(blank=True, db_column='type', max_length=1000, null=True, verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='project',
            name='detail',
            field=models.CharField(blank=True, db_column='detail', max_length=1000, null=True, verbose_name='Detail'),
        ),
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(blank=True, db_column='name', max_length=1000, null=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='project',
            name='status',
            field=models.CharField(blank=True, db_column='status', default='running', max_length=1000, null=True, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='projectstatus',
            name='color',
            field=models.CharField(blank=True, db_column='color', max_length=1000, null=True, verbose_name='Color'),
        ),
        migrations.AlterField(
            model_name='projectstatus',
            name='name',
            field=models.CharField(blank=True, db_column='name', max_length=1000, null=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='status',
            name='color',
            field=models.CharField(blank=True, db_column='color', max_length=1000, null=True, verbose_name='Color'),
        ),
        migrations.AlterField(
            model_name='status',
            name='detail',
            field=models.CharField(blank=True, db_column='detail', max_length=1000, null=True, verbose_name='Detail'),
        ),
        migrations.AlterField(
            model_name='status',
            name='name',
            field=models.CharField(blank=True, db_column='name', max_length=1000, null=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='status',
            name='tenantCategory',
            field=models.CharField(blank=True, db_column='tenantCategory', max_length=1000, null=True, verbose_name='Detail'),
        ),
    ]
