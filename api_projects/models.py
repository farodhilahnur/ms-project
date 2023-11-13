import django
from django.db import models
from django.utils import timezone
from django.utils.timezone import now
from .utils import get_uuid

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(db_column='name', max_length=1000, blank=True, null=True, verbose_name='Name')
    sort = models.IntegerField(db_column='sort', blank=True, null=True,  verbose_name='Sort')
    color = models.CharField(db_column='color', max_length=1000, blank=True, null=True,  verbose_name='Color')
    availability = models.CharField(db_column='availability', max_length=1000, blank=True, null=True,  verbose_name='Availability')
    picture = models.CharField(db_column='picture', max_length=1000, blank=True, null=True,  verbose_name='Picture')
    isActive = models.BooleanField(db_column='isActive', default=True, verbose_name='Is Active')
    enableReminder = models.BooleanField(db_column='enableReminder', blank=True, null=True, verbose_name='enableReminder')
    class Meta:
        db_table = 'tbl_mastercategory'

class Status(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, db_column='category_id', on_delete=models.CASCADE, blank=True, null=True, related_name='category')
    name = models.CharField(db_column='name', max_length=1000, blank=True, null=True, verbose_name='Name')
    point = models.IntegerField(db_column='point', blank=True, null=True,  verbose_name='Sort')
    detail = models.CharField(db_column='detail',  max_length=1000, blank=True, null=True,  verbose_name='Detail')
    sort = models.IntegerField(db_column='sort', blank=True, null=True,  verbose_name='Sort')
    color = models.CharField(db_column='color', max_length=1000, blank=True, null=True,  verbose_name='Color')
    isActive = models.BooleanField(db_column='isActive', default=True, verbose_name='Is Active')
    tenantCategory = models.CharField(db_column='tenantCategory', max_length=1000, blank=True, null=True, verbose_name='Detail')
    class Meta:
        db_table = 'tbl_masterstatus'

class Media(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(db_column='name', max_length=1000, null=False, verbose_name='Name')
    sort = models.IntegerField(db_column='sort', blank=True, null=True,  verbose_name='Sort')
    type = models.CharField(db_column='type', max_length=1000, blank=True, null=True,  verbose_name='Type')
    picture = models.CharField(db_column='picture', max_length=1000, blank=True, null=True,  verbose_name='Picture')
    isActive = models.BooleanField(db_column='isActive', default=True, blank=True, null=True, verbose_name='Is Active')
    accountId = models.IntegerField(db_column='accountId', blank=True, null=True,  verbose_name='Account Id')
    class Meta:
        db_table = 'tbl_mastermedia'

class Field(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(db_column='name', max_length=1000, null=False, verbose_name='Name')
    type = models.CharField(db_column='type', max_length=1000, blank=True, null=True,  verbose_name='Type')
    mandatory = models.BooleanField(db_column='mandatory', blank=True, null=True, verbose_name='Mandatory')
    displayedas = models.CharField(db_column='displayedas', max_length=1000, blank=True, null=True,  verbose_name='Displayedas')
    alias = models.CharField(db_column='alias', max_length=1000, blank=True, null=True,  verbose_name='Alias')
    parameters = models.JSONField(blank=True, null=True)
    createdAt = models.DateTimeField(db_column='createdAt', blank=True, null=True, default=django.utils.timezone.now, verbose_name='Created At')
    createdBy = models.IntegerField(db_column='createdBy', blank=True, null=True, verbose_name='Created By')
    form = models.ManyToManyField('Form', through = 'FormField')

    class Meta:
        db_table = 'tbl_field'
    def save(self, *args, **kwargs):
        return super(Field, self).save(*args, **kwargs)

class Project(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(db_column='name', max_length=1000, blank=True, null=True, verbose_name='Name')
    detail = models.CharField(db_column='detail',  max_length=1000, blank=True, null=True,  verbose_name='Detail')
    createdAt = models.DateTimeField(db_column='createdAt', blank=True, null=True, default=django.utils.timezone.now, verbose_name='Created At')
    createdBy = models.IntegerField(db_column='createdBy', blank=True, null=True,  verbose_name='Created By')
    modifiedAt = models.DateTimeField(db_column='modifiedAt', blank=True, null=True,  verbose_name='Modified At')
    modifiedBy = models.IntegerField(db_column='modifiedBy', blank=True, null=True,  verbose_name='Modified By')
    accountId = models.IntegerField(db_column='accountId', blank=True, null=True,  verbose_name='Account Id')
    periodEnd = models.DateTimeField(db_column='periodEnd', blank=True, null=True,  verbose_name='Periode End')
    periodStart = models.DateTimeField(db_column='periodStart', blank=True, null=True, verbose_name='Periode Start')
    status = models.CharField(db_column='status', max_length=1000, default="running", blank=True, null=True, verbose_name='Status')
    totalCampaign = models.IntegerField(db_column='totalCampaign', default=0, blank=True, null=True, verbose_name='total Campaign')
    totalLead = models.IntegerField(db_column='totalLead', default=0, blank=True, null=True,  verbose_name='total Lead')
    totalClosingLead = models.IntegerField(db_column='totalClosingLead', default=0, blank=True, null=True,  verbose_name='total Closing Lead')
    totalGroup = models.IntegerField(db_column='totalGroup', default=0, blank=True, null=True,  verbose_name='total Group')
    duplicate_lead = models.BooleanField(db_column='duplicate_lead', default=False)
    picture = models.CharField(db_column='picture', max_length=1000, blank=True, null=True,  verbose_name='Picture') 

    class Meta:
        db_table = 'tbl_project'
    def save(self, *args, **kwargs):
        self.modifiedAt = timezone.now()
        return super(Project, self).save(*args, **kwargs)
    
class ProjectTeam(models.Model):
    id = models.AutoField(primary_key=True)
    teamId = models.IntegerField(db_column='teamId', blank=True, null=True,  verbose_name='Team Id')
    project = models.ForeignKey(Project, db_column='projectId', on_delete=models.CASCADE)
    accountId = models.IntegerField(db_column='accountId', blank=True, null=True,  verbose_name='Account Id')
    createdAt = models.DateTimeField(db_column='createdAt', blank=True, null=True, default=django.utils.timezone.now, verbose_name='Created At')
    createdBy = models.IntegerField(db_column='createdBy', blank=True, null=True,  verbose_name='Created By')
    class Meta:
        db_table = 'tbl_projectteam'
    def save(self, *args, **kwargs):
        return super(ProjectTeam, self).save(*args, **kwargs)

class ProjectStatus(models.Model):
    id = models.AutoField(primary_key=True)
    point = models.IntegerField(db_column='point', blank=True, null=True,  verbose_name='Point')
    project = models.ForeignKey(Project, db_column='projectId', on_delete=models.CASCADE)
    accountId = models.IntegerField(db_column='accountId', blank=True, null=True,  verbose_name='Account Id')
    name = models.CharField(db_column='name', max_length=1000, blank=True, null=True, verbose_name='Name')
    detail = models.CharField(db_column='detail',  max_length=1000, blank=True, null=True, verbose_name='Detail')
    createdAt = models.DateTimeField(db_column='createdAt', blank=True, null=True, default=django.utils.timezone.now, verbose_name='Created At')
    createdBy = models.IntegerField(db_column='createdBy', blank=True, null=True,  verbose_name='Created By')
    modifiedAt = models.DateTimeField(db_column='modifiedAt', blank=True, null=True,  verbose_name='Modified At')
    modifiedBy = models.IntegerField(db_column='modifiedBy', blank=True, null=True,  verbose_name='Modified By')
    color = models.CharField(db_column='color', max_length=1000, blank=True, null=True, verbose_name='Color')
    category = models.ForeignKey(Category, db_column='categoryId', blank=True, null=True, on_delete=models.CASCADE)
    sort = models.IntegerField(db_column='sort', blank=True, null=True,  verbose_name='Sort')
    class Meta:
        db_table = 'tbl_projectstatus'
    def save(self, *args, **kwargs):
        self.modifiedAt = timezone.now()
        return super(ProjectStatus, self).save(*args, **kwargs)

class ProjectDuplicateStatus(models.Model):
    id = models.AutoField(primary_key=True)
    point = models.IntegerField(db_column='point', blank=True, null=True,  verbose_name='Point')
    project = models.ForeignKey(Project, db_column='projectId', on_delete=models.CASCADE)
    accountId = models.IntegerField(db_column='accountId', blank=True, null=True,  verbose_name='Account Id')
    name = models.CharField(db_column='name', max_length=1000, blank=True, null=True, verbose_name='Name')
    detail = models.CharField(db_column='detail',  max_length=1000, blank=True, null=True, verbose_name='Detail')
    createdAt = models.DateTimeField(db_column='createdAt', blank=True, null=True, default=django.utils.timezone.now, verbose_name='Created At')
    createdBy = models.IntegerField(db_column='createdBy', blank=True, null=True,  verbose_name='Created By')
    modifiedAt = models.DateTimeField(db_column='modifiedAt', blank=True, null=True,  verbose_name='Modified At')
    modifiedBy = models.IntegerField(db_column='modifiedBy', blank=True, null=True,  verbose_name='Modified By')
    color = models.CharField(db_column='color', max_length=1000, blank=True, null=True, verbose_name='Color')
    category = models.ForeignKey(Category, db_column='categoryId', blank=True, null=True, on_delete=models.CASCADE)
    sort = models.IntegerField(db_column='sort', blank=True, null=True,  verbose_name='Sort')
    class Meta:
        db_table = 'tbl_project_duplicatestatus'
    def save(self, *args, **kwargs):
        self.modifiedAt = timezone.now()
        return super(ProjectDuplicateStatus, self).save(*args, **kwargs)

class CustomStatus(models.Model):
    id = models.AutoField(primary_key=True)
    point = models.IntegerField(db_column='point', blank=True, null=True,  verbose_name='Point')
    accountId = models.IntegerField(db_column='accountId', blank=True, null=True,  verbose_name='Account Id')
    name = models.CharField(db_column='name', max_length=1000, blank=True, null=True, verbose_name='Name')
    detail = models.CharField(db_column='detail',  max_length=1000, blank=True, null=True, verbose_name='Detail')
    createdAt = models.DateTimeField(db_column='createdAt', blank=True, null=True, default=django.utils.timezone.now, verbose_name='Created At')
    createdBy = models.IntegerField(db_column='createdBy', blank=True, null=True,  verbose_name='Created By')
    modifiedAt = models.DateTimeField(db_column='modifiedAt', blank=True, null=True,  verbose_name='Modified At')
    modifiedBy = models.IntegerField(db_column='modifiedBy', blank=True, null=True,  verbose_name='Modified By')
    color = models.CharField(db_column='color', max_length=1000, blank=True, null=True, verbose_name='Color')
    category = models.ForeignKey(Category, db_column='categoryId', blank=True, null=True, on_delete=models.CASCADE)
    sort = models.IntegerField(db_column='sort', blank=True, null=True,  verbose_name='Sort')

    class Meta:
        db_table = 'tbl_customstatus'
    def save(self, *args, **kwargs):
        self.modifiedAt = timezone.now()
        return super(CustomStatus, self).save(*args, **kwargs)

class ProjectProduct(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, db_column='projectId', on_delete=models.CASCADE)
    productId = models.IntegerField(db_column='productId', blank=True, null=True,  verbose_name='Product Id')
    createdAt = models.DateTimeField(db_column='createdAt', blank=True, null=True, default=django.utils.timezone.now, verbose_name='Created At')
    createdBy = models.IntegerField(db_column='createdBy', blank=True, null=True,  verbose_name='Created By')
    accountId = models.IntegerField(db_column='accountId', blank=True, null=True,  verbose_name='Account Id')
    class Meta:
        db_table = 'tbl_projectProduct'
    def save(self, *args, **kwargs):
        return super(ProjectProduct, self).save(*args, **kwargs)

class Campaign(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, db_column='projectId', blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(db_column='name', max_length=1000, blank=True, null=True, verbose_name='Name') 
    detail = models.CharField(db_column='detail',  max_length=1000, blank=True, null=True,  verbose_name='Detail') 
    picture = models.CharField(db_column='picture', max_length=1000, blank=True, null=True,  verbose_name='Picture') 
    createdAt = models.DateTimeField(db_column='createdAt', blank=True, null=True, default=django.utils.timezone.now, verbose_name='Created At')
    createdBy = models.IntegerField(db_column='createdBy', blank=True, null=True,  verbose_name='Created By')
    modifiedAt = models.DateTimeField(db_column='modifiedAt', blank=True, null=True,  verbose_name='Modified At')
    modifiedBy = models.IntegerField(db_column='modifiedBy', blank=True, null=True,  verbose_name='Modified By')
    periodEnd = models.DateTimeField(db_column='periodEnd', blank=True, null=True,  verbose_name='Periode End')
    periodStart = models.DateTimeField(db_column='periodStart', blank=True, null=True, verbose_name='Periode Start')
    status = models.CharField(db_column='status', max_length=1000, default="running", blank=True, null=True, verbose_name='Status')
    accountId = models.IntegerField(db_column='accountId', blank=True, null=True,  verbose_name='Account Id')
    totalChannel = models.IntegerField(db_column='totalChannel', default=0, blank=True, null=True,  verbose_name='totalChannel')
    totalLead = models.IntegerField(db_column='totalLead', default=0, blank=True, null=True,  verbose_name='total Lead')

    class Meta:
        db_table = 'tbl_campaign'
    def save(self, *args, **kwargs):
        self.modifiedAt = timezone.now()
        return super(Campaign, self).save(*args, **kwargs)

class Form(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(db_column='name', max_length=1000, blank=True, null=True, verbose_name='Name')
    detail = models.CharField(db_column='detail',  max_length=1000, blank=True, null=True,  verbose_name='Detail')
    type = models.CharField(db_column='type', max_length=1000, blank=True, null=True,  verbose_name='Type')
    pageUrl = models.CharField(db_column='pageUrl', max_length=400, blank=True, null=True,  verbose_name='Page Url')
    createdAt = models.DateTimeField(db_column='createdAt', blank=True, null=True, default=django.utils.timezone.now, verbose_name='Created At')
    createdBy = models.IntegerField(db_column='createdBy', blank=True, null=True,  verbose_name='Created By')
    modifiedAt = models.DateTimeField(db_column='modifiedAt', blank=True, null=True,  verbose_name='Modified At')
    modifiedBy = models.IntegerField(db_column='modifiedBy', blank=True, null=True,  verbose_name='Modified By')
    accountId = models.IntegerField(db_column='accountId', blank=True, null=True,  verbose_name='Account Id')
    class Meta:
        db_table = 'tbl_form'

    def save(self, *args, **kwargs):
        self.modifiedAt = timezone.now()
        return super(Form, self).save(*args, **kwargs)

class Channel(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(db_column='name', max_length=1000, blank=True, null=True, verbose_name='Name')
    detail = models.CharField(db_column='detail',  max_length=1000, blank=True, null=True,  verbose_name='Detail')
    click = models.IntegerField(db_column='click', blank=True, null=True, default=0, verbose_name='Click')
    picture = models.CharField(db_column='picture', max_length=1000, blank=True, null=True,  verbose_name='Picture')
    redirectUrl = models.CharField(db_column='redirectUrl', max_length=400, blank=True, null=True, verbose_name='Redirect URL')
    uniqueCode = models.CharField(db_column="uniqueCode", max_length=1000, null=False, unique=True, editable=False, default=get_uuid)
    channelUrl = models.CharField(db_column='channelUrl', max_length=1000, blank=True, null=True, verbose_name='Channel URL')
    periodStart = models.DateTimeField(db_column='periodStart', blank=True, null=True, verbose_name='Period Start')
    periodEnd = models.DateTimeField(db_column='periodEnd', blank=True, null=True, verbose_name='Period End')
    createdAt = models.DateTimeField(db_column='createdAt', blank=True, null=True, default=django.utils.timezone.now, verbose_name='Created At')
    createdBy = models.IntegerField(db_column='createdBy', blank=True, null=True, verbose_name='Created By')
    modifiedAt = models.DateTimeField(db_column='modifiedAt', blank=True, null=True,  verbose_name='Modified At')
    modifiedBy = models.IntegerField(db_column='modifiedBy', blank=True, null=True,  verbose_name='Modified By')
    status = models.CharField(db_column='status', default="running", max_length=1000, blank=True, null=True, verbose_name='Status')
    accountId = models.IntegerField(db_column='accountId', blank=True, null=True,  verbose_name='Account Id')
    distributionType = models.CharField(db_column='distributionType', max_length=1000, blank=True, null=True, verbose_name='Distribution Type')
    enableRedistribution = models.BooleanField(db_column='enableRedistribution', blank=True, null=True)
    idleDuration = models.CharField(db_column='idleDuration', blank=True, null=True, max_length=100)
    startTime = models.TimeField(db_column='startTime', blank=True, null=True, max_length=100)
    endTime = models.TimeField(db_column='endTime', blank=True, null=True, max_length=100)
    totalLead = models.IntegerField(db_column='totalLead', default=0, blank=True, null=True,  verbose_name='total Lead')
    leadRate = models.IntegerField(db_column='leadRate', default=0, blank=True, null=True, verbose_name='lead_rate')
    campaign  = models.ForeignKey(Campaign, db_column='campaignId', on_delete=models.CASCADE)
    media = models.ForeignKey(Media, db_column='mediaId', blank=True, null=True, on_delete=models.CASCADE)
    form = models.ForeignKey(Form, db_column='formId', blank=True, null=True, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'tbl_channel'
    
    def save(self, *args, **kwargs):
        self.modifiedAt = timezone.now()
        if self.enableRedistribution == False :
            self.startTime = "08:00:00"
            self.endTime = "17:00:00"
        return super(Channel, self).save(*args, **kwargs)

class ChannelGroup(models.Model):
    id = models.AutoField(primary_key=True)
    channel = models.ForeignKey(Channel, db_column='channelId', on_delete=models.CASCADE)
    teamId = models.IntegerField(db_column='teamId', blank=True, null=True,  verbose_name='Team Id')   
    accountId = models.IntegerField(db_column='accountId', blank=True, null=True,  verbose_name='Account Id')
    createdAt = models.DateTimeField(db_column='createdAt', blank=True, null=True, default=django.utils.timezone.now, verbose_name='Created At')
    createdBy = models.IntegerField(db_column='createdBy', blank=True, null=True,  verbose_name='Created By')
    class Meta:
        db_table = 'tbl_channelgroup'
    def save(self, *args, **kwargs):
        return super(ChannelGroup, self).save(*args, **kwargs)

class ChannelClick(models.Model):
    id = models.AutoField(primary_key=True)
    channel = models.ForeignKey(Channel, db_column='channelId', on_delete=models.CASCADE)
    accountId = models.IntegerField(db_column='accountId', blank=True, null=True,  verbose_name='Account Id')
    createdAt = models.DateTimeField(db_column='createdAt', blank=True, null=True, default=django.utils.timezone.now, verbose_name='Created At')
    createdBy = models.IntegerField(db_column='createdBy', blank=True, null=True,  verbose_name='Created By')

    class Meta:
        db_table = 'tbl_channelclick'
    def save(self, *args, **kwargs):
        return super(ChannelClick, self).save(*args, **kwargs)

class FormField(models.Model):
    id = models.AutoField(primary_key=True)
    field = models.ForeignKey(Field, db_column='fieldId', on_delete=models.CASCADE)
    form = models.ForeignKey(Form, db_column='formId', on_delete=models.CASCADE)
    createdAt = models.DateTimeField(db_column='createdAt', blank=True, null=True, default=django.utils.timezone.now, verbose_name='Created At')
    createdBy = models.IntegerField(db_column='createdBy', blank=True, null=True,  verbose_name='Created By')
    accountId = models.IntegerField(db_column='accountId', blank=True, null=True,  verbose_name='Account Id')
    class Meta:
        db_table = 'tbl_formfield'
    def save(self, *args, **kwargs):
        return super(FormField, self).save(*args, **kwargs)

class ProjectAdmin(models.Model):
    id = models.AutoField(primary_key=True)
    createdAt = models.DateTimeField(db_column='createdAt', blank=True, null=True, default=django.utils.timezone.now, verbose_name='Created At')
    createdBy = models.IntegerField(db_column='createdBy', blank=True, null=True,  verbose_name='Created By')
    userId = models.IntegerField(db_column='userId', blank=True, null=True, verbose_name='User Id')
    mask_phone = models.BooleanField(db_column='mask_phone', default=False, verbose_name=' Mask phone')
    project = models.ForeignKey(Project, db_column='projectId', blank=True, null=True, on_delete=models.CASCADE)
    email = models.CharField(db_column='email', blank=True, null=True, max_length=1000)
    status = models.CharField(db_column='status', max_length=1000, default="active", blank=True, null=True, verbose_name='Status')
    ref_id = models.CharField(db_column='ref_id', blank=True, null=True, max_length=1000)
    accountId = models.IntegerField(db_column='accountId', blank=True, null=True, verbose_name='Account Id')
    modifiedAt = models.DateTimeField(db_column='modifiedAt', blank=True, null=True,  verbose_name='Modified At')
    modifiedBy = models.IntegerField(db_column='modifiedBy', blank=True, null=True,  verbose_name='Modified By')
    
    class Meta:
        db_table = 'tbl_projectadmin'
    def save(self, *args, **kwargs):
        self.modifiedAt = timezone.now()
        return super(ProjectAdmin, self).save(*args, **kwargs)

class ChannelSettingMember(models.Model) :
    id = models.AutoField(primary_key=True)
    type = models.CharField(db_column='type', blank=True, null=True, max_length=100)
    status_distribution = models.CharField(db_column='status_distribution', default='enable', blank=True, null=True, max_length=100)
    percentage = models.CharField(db_column='percentage', blank=True, null=True, max_length=100)
    channel = models.ForeignKey(Channel, db_column='channelId', blank=True, null=True, on_delete=models.CASCADE)
    userId = models.IntegerField(db_column='userId', blank=True, null=True,  verbose_name='User Id')
    teamId = models.IntegerField(db_column='teamId', blank=True, null=True,  verbose_name='Team Id')
    accountId = models.IntegerField(db_column='accountId', blank=True, null=True,  verbose_name='Account Id')
    createdAt = models.DateTimeField(db_column='createdAt', blank=True, null=True, default=django.utils.timezone.now, verbose_name='Created At')
    createdBy = models.IntegerField(db_column='createdBy', blank=True, null=True,  verbose_name='Created By')
    modifiedAt = models.DateTimeField(db_column='modifiedAt', blank=True, null=True,  verbose_name='Modified At')
    modifiedBy = models.IntegerField(db_column='modifiedBy', blank=True, null=True,  verbose_name='Modified By')

    class Meta:
        db_table = 'tbl_channelsettingmember'
    def save(self, *args, **kwargs):
        self.modifiedAt = timezone.now()
        return super(ChannelSettingMember, self).save(*args, **kwargs)

class UserDistribution(models.Model) :
    id = models.AutoField(primary_key=True)
    userId = models.IntegerField(db_column='userId', blank=True, null=True,  verbose_name='User Id')
    distribution = models.CharField(db_column='distribution', blank=True, null=True, max_length=1000)
    campaignId = models.CharField(db_column='campaignids', blank=True, null=True, max_length=1000)
    city = models.CharField(db_column='city', blank=True, null=True, max_length=100000)
    accountId = models.IntegerField(db_column='accountId', blank=True, null=True,  verbose_name='Account Id')
    createdAt = models.DateTimeField(db_column='createdAt', blank=True, null=True, default=django.utils.timezone.now, verbose_name='Created At')
    createdBy = models.IntegerField(db_column='createdBy', blank=True, null=True,  verbose_name='Created By')
    modifiedAt = models.DateTimeField(db_column='modifiedAt', blank=True, null=True,  verbose_name='Modified At')
    modifiedBy = models.IntegerField(db_column='modifiedBy', blank=True, null=True,  verbose_name='Modified By')

    class Meta:
        db_table = 'tbl_distribution_usersettings'
    def save(self, *args, **kwargs):
        self.modifiedAt = timezone.now()
        return super(UserDistribution, self).save(*args, **kwargs)