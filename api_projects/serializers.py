from os import dup
from django.db.models.base import Model
from .services import ExternalService
from django.db.models import fields
from rest_framework import serializers
from .models import Campaign, Category, Channel, ChannelClick, ChannelGroup, ChannelSettingMember, CustomStatus, Field, Form, FormField, Media, Project, ProjectAdmin, ProjectDuplicateStatus, ProjectStatus, ProjectTeam, Status, UserDistribution
import os

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class CategoryStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    statuses = serializers.SerializerMethodField('get_status')
    def get_status(self, category):
        queryset = Status.objects.filter(category=category)
        status_serializer = StatusSerializer(queryset, many=True)
        return status_serializer.data

class StatusCategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=False, required=False)

    class Meta:
        model = Status
        fields = '__all__'

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = '__all__'

class MediaIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['id', 'name', 'type']

class FormIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Form
        fields = ['id'] 

class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = ['id', 'name', 'type', 'mandatory', 'displayedas', 'alias', 'parameters']

class CategoryIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id',]

class StatusIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectStatus
        fields = ['id',]

class ProjectIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name']

class ChannelIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ['id',]

class ProjectStatusSerializer(serializers.ModelSerializer):
    project = ProjectIdSerializer(many=False, required=False)
    category = CategoryIdSerializer(many=False, required=False)

    class Meta:
        model = ProjectStatus
        fields = '__all__'

class ProjectStatusDuplicateSerializer(serializers.ModelSerializer):
    id = StatusIdSerializer(many=False, required=False)

    class Meta:
        model = ProjectDuplicateStatus
        fields = '__all__'
    
    def get_status(self, project):
        queryset = ProjectDuplicateStatus.objects.filter(project=project)
        status_serializer = StatusIdSerializer(queryset, many=True)
        return status_serializer

class OldStatusCustomSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=False, required=False)

    class Meta:
        model = ProjectStatus
        fields = '__all__'

class ProjectStatusCustomSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=False, required=False)

    class Meta:
        model = CustomStatus
        fields = '__all__'

class PTeamSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="teamId")

    class Meta:
        model = ProjectTeam
        fields = ['id']
        
class ProjectSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField('getgroup')
    
    def getgroup(self, project):
        queryset = ProjectTeam.objects.filter(project=project)
        queryset_serializer = PTeamSerializer(queryset, many=True)
        return queryset_serializer.data
        
    class Meta:
        model = Project
        fields = '__all__'

    def to_internal_value(self, data):
        if data.get('periodEnd', None) == '':
            data.pop('periodEnd')
        return super(ProjectSerializer, self).to_internal_value(data)

class ProjectssSerializer(serializers.ModelSerializer):
    totalCampaign = serializers.SerializerMethodField('getcamp')
    totalGroup = serializers.SerializerMethodField('gettot')
    groups  = serializers.SerializerMethodField('get_team')
    leadStatuses = serializers.SerializerMethodField('get_status')
    leadStatuses_duplicate = serializers.SerializerMethodField('get_status_duplicate')

    def getcamp(self, project):
        queryset = Campaign.objects.filter(project=project).count()
        return queryset
    
    def gettot(self, project):
        queryset = ProjectTeam.objects.filter(project=project).count()
        return queryset
        
    def get_team(self, project):
        request_object = self.context['request']
        additional = request_object.query_params.get('without_additional_information')
        user_id = request_object.query_params.get('invoker_id')

        if(additional == None):
            external_service = ExternalService()
            groups = external_service.get_team_by_tenant_id_project_id(tenant_id=project.accountId, projectId=project.id, user_id=user_id)
            return groups
        return None
    
    def get_status(self, project):
        queryset = ProjectStatus.objects.filter(project=project)
        status_serializer = ProjectStatusSerializer(queryset, many=True)
        return status_serializer.data
    
    def get_status_duplicate(self, project):
        duplicate = ProjectDuplicateStatus.objects.filter(project=project)
        if(duplicate != []):
            for n in duplicate:
                queryset = ProjectStatus.objects.filter(project=project, name=n.name)
                status_serializer = ProjectStatusSerializer(queryset, many=True)
                return status_serializer.data
        return []

    class Meta:
        model = Project
        fields = '__all__'
    
    def to_internal_value(self, data):
        if data.get('periodEnd', None) == '':
            data.pop('periodEnd')
        return super(ProjectssSerializer, self).to_internal_value(data)

class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

class OngoingProjectSerializer(serializers.ModelSerializer):
    totalCampaign = serializers.SerializerMethodField('getcamp')
    totalGroup = serializers.SerializerMethodField('gettot')

    def getcamp(self, project):
        queryset = Campaign.objects.filter(project=project).count()
        return queryset
    
    def gettot(self, project):
        queryset = ProjectTeam.objects.filter(project=project).count()
        return queryset

    class Meta:
        model = Project
        fields = '__all__'

    def to_internal_value(self, data):
        if data.get('periodEnd', None) == '':
            data.pop('periodEnd')
        return super(ProjectSerializer, self).to_internal_value(data)

class CampaignSerializer(serializers.ModelSerializer):
    # project = ProjectIdSerializer(many = False, required = False)

    class Meta:
        model = Campaign
        fields = '__all__'
    
    def to_internal_value(self, data):
        if data.get('periodEnd', None) == '':
            data.pop('periodEnd')
        return super(CampaignSerializer, self).to_internal_value(data)
    
    def __init__(self, *args, **kwargs):
        request = kwargs.get('context', {}).get('request')
        str_fields = request.GET.get('fields', '') if request else None
        fields = str_fields.split(',') if str_fields else None
        # Instantiate the superclass 
        super(CampaignSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

class CampaignByProjectSerializer(serializers.ModelSerializer):
    # project = ProjectIdSerializer(many = False, required = False)

    class Meta:
        model = Campaign
        fields = '__all__'
    
    def to_internal_value(self, data):
        if data.get('periodEnd', None) == '':
            data.pop('periodEnd')
        return super(CampaignSerializer, self).to_internal_value(data)


class CampaignSingleSerializer(serializers.ModelSerializer):
    project = ProjectIdSerializer(many = False, required = False)
    totalChannel = serializers.SerializerMethodField("getchann")
    totalLead = serializers.SerializerMethodField('getlead')

    def getlead(self, campaign):
        request_object = self.context['request']
        additional = request_object.query_params.get('without_additional_information')
        user_id = request_object.query_params.get('invoker_id')
        since = request_object.query_params.get('since')
        until = request_object.query_params.get('until')

        if(additional == None and user_id != None):
            external_service = ExternalService()
            list = external_service.get_summary_campaign(accountId=campaign.accountId, invokerId=user_id, since=since, until=until)

            if(list != None) :
                if(list['data'] != None):
                    if(list['data']['getSummary']['buckets'] != None):
                        a = list['data']['getSummary']['buckets']
                        chann = next((x for x in a if x['key'] == str(campaign.id)), 0)
                        if (chann != 0) :
                            return chann['value']   
                        else:
                            return 0
        return 0

    def getchann(self, campaign):
        queryset = Channel.objects.filter(campaign=campaign).count()
        return queryset

    class Meta:
        model = Campaign
        fields = '__all__'
    
    def to_internal_value(self, data):
        if data.get('periodEnd', None) == '':
            data.pop('periodEnd')
        return super(CampaignSingleSerializer, self).to_internal_value(data)

class CampaignCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = ['name', 'detail', 'periodeStart', 'periodeEnd', 'status']

class CampaignProjectSerializer(serializers.ModelSerializer):
    project = ProjectIdSerializer(many = False, required = False)
    totalLead = serializers.SerializerMethodField('getlead')
    totalChannel = serializers.SerializerMethodField("getchann")

    def getlead(self, campaign):
        request_object = self.context['request']
        additional = request_object.query_params.get('without_additional_information')
        user_id = request_object.query_params.get('invoker_id')
        since = request_object.query_params.get('since')
        until = request_object.query_params.get('until')

        if(additional == None and user_id != None):
            external_service = ExternalService()
            list = external_service.get_summary_campaign(accountId=campaign.accountId, invokerId=user_id, since=since, until=until)
            
            if(list != None) :
                if(list['data'] != None):
                    if(list['data']['getSummary']['buckets'] != None):
                        a = list['data']['getSummary']['buckets']
                        chann = next((x for x in a if x['key'] == str(campaign.id)), 0)
                        if (chann != 0) :
                            return chann['value']   
                        else:
                            return 0
        return 0
    
    def getchann(self, campaign):
        queryset = Channel.objects.filter(campaign=campaign).count()
        return queryset

    class Meta:
        model = Campaign
        fields = '__all__'

    def to_internal_value(self, data):
        if data.get('periodEnd', None) == '':
            data.pop('periodEnd')
        return super(CampaignProjectSerializer, self).to_internal_value(data)

class CampaignChannelSerializer(serializers.ModelSerializer):
    project = ProjectIdSerializer(many=False, required=False)
    class Meta:
        model = Campaign
        fields = ['id','name','project',]

class ChannelProjectSerializer(serializers.ModelSerializer):
    media = MediaSerializer(many=False, required=False)
    form = serializers.SerializerMethodField('get_channel_form')
    campaign = CampaignChannelSerializer(many=False, required=False)

    def get_channel_form(self, channel):
        queryset = Form.objects.filter(channel=channel).first()
        channel_media_serializer = FormChannelSerializer(queryset, many=False)
        return channel_media_serializer.data
        
    class Meta:
        model = Channel
        fields = '__all__'

class ProjectStatusProjectSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many = False, required = False)
    project = ProjectIdSerializer(many= False, required = False)
    typeStatus = serializers.SerializerMethodField('gettype')

    def gettype(self, project):
        request_object = self.context['request']
        ass = request_object.query_params.get('assistant_only')

        if(ass == 'true'):
            type = CustomStatus.objects.filter(accountId=project.accountId).values_list('name', flat=True)
            if (project.name in type):
                return 'Custom'
            else :
                return 'Default'
        else : 
            return None

    class Meta:
        model = ProjectStatus
        fields = '__all__'

class ProjectDuplicateStatusProjectSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many = False, required = False)
    project = ProjectIdSerializer(many= False, required = False)

    class Meta:
        model = ProjectDuplicateStatus
        fields = '__all__'

class ProjectTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTeam
        fields = '__all__'

class ProjectGroupSerializer(serializers.ModelSerializer):
    totalCampaign = serializers.SerializerMethodField('getcamp')
    totalGroup = serializers.SerializerMethodField('gettot')
    # totalClosingLead = serializers.SerializerMethodField('getclosing')

    def getcamp(self, project):
        queryset = Campaign.objects.filter(project=project).count()
        return queryset
    
    def gettot(self, project):
        queryset = ProjectTeam.objects.filter(project=project).count()
        return queryset
        
    class Meta:
        model = Project
        fields = '__all__'

class ChannelSerializer(serializers.ModelSerializer):
    campaign = CampaignChannelSerializer(many=False, required=False)
    form = serializers.SerializerMethodField('get_channel_form')
    media = serializers.SerializerMethodField('get_channel_media')
    click = serializers.SerializerMethodField('getclick')

    def getclick(self, channel):
        request_object = self.context['request']
        account_id = request_object.query_params.get('account_id')
        since = request_object.query_params.get('since')
        until = request_object.query_params.get('until')
        additional = request_object.query_params.get('with_additional_information')

        if additional == 'true' :
            if(since != None or until != None):
                data = (ChannelClick.objects.filter(accountId=account_id, channel=channel.id, createdAt__gte=since) & ChannelClick.objects.filter(accountId=account_id, channel=channel.id, createdAt__lte=until)).count()
                return data
            else : 
                return ChannelClick.objects.filter(channel=channel.id, accountId = account_id).count() 

    def get_channel_form(self, channel):
        request_object = self.context['request']
        isoffline = request_object.query_params.get('isOffline')
        if isoffline == 'true' :
            return {}
        else :
            queryset = Form.objects.filter(channel=channel).first()
            channel_media_serializer = FormChannelSerializer(queryset, many=False)
            return channel_media_serializer.data

    def get_channel_media(self, channel):      
        queryset = Media.objects.filter(channel=channel).first()
        channel_media_serializer = MediaSerializer(queryset, many=False)
        return channel_media_serializer.data

    class Meta:
        model = Channel
        fields = '__all__'
    
    def to_internal_value(self, data):
        if data.get('periodEnd', None) == '':
            data.pop('periodEnd')
        return super(ChannelSerializer, self).to_internal_value(data)
    
    def __init__(self, *args, **kwargs):
        request = kwargs.get('context', {}).get('request')
        str_fields = request.GET.get('fields', '') if request else None
        fields = str_fields.split(',') if str_fields else None

        # Instantiate the superclass 
        super(ChannelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
    
class ChannelByCampaignSerializer(serializers.ModelSerializer):
    form = serializers.SerializerMethodField('get_channel_form')
    media = serializers.SerializerMethodField('get_channel_media')
    click = serializers.SerializerMethodField('getclick')

    def getclick(self, channel):
        request_object = self.context['request']
        account_id = request_object.query_params.get('account_id')
        since = request_object.query_params.get('since')
        until = request_object.query_params.get('until')

        if(since != None or until != None):
            data = (ChannelClick.objects.filter(accountId=account_id, channel=channel.id, createdAt__gte=since) & ChannelClick.objects.filter(accountId=account_id, channel=channel.id, createdAt__lte=until)).count()
            return data
        else : 
            return ChannelClick.objects.filter(channel=channel.id, accountId = account_id).count() 

    def get_channel_form(self, channel):
        request_object = self.context['request']
        isoffline = request_object.query_params.get('isOffline')
        if isoffline == 'true' :
            return {}
        else :
            queryset = Form.objects.filter(channel=channel).first()
            channel_media_serializer = FormChannelSerializer(queryset, many=False)
            return channel_media_serializer.data

    def get_channel_media(self, channel):      
        queryset = Media.objects.filter(channel=channel).first()
        channel_media_serializer = MediaSerializer(queryset, many=False)
        return channel_media_serializer.data

    class Meta:
        model = Channel
        fields = '__all__'
    
    def to_internal_value(self, data):
        if data.get('periodEnd', None) == '':
            data.pop('periodEnd')
        return super(ChannelSerializer, self).to_internal_value(data)
    
class ChannelssSerializer(serializers.ModelSerializer):
    campaign = CampaignChannelSerializer(many=False, required=False)
    media = serializers.SerializerMethodField('get_channel_media')
    form = serializers.SerializerMethodField('get_channel_form')
    groups  = serializers.SerializerMethodField('get_team')
    x = serializers.SerializerMethodField('getlead')
    click = serializers.SerializerMethodField('getclick')
    channelUrl = serializers.SerializerMethodField('getchannelurl')

    def getchannelurl(self, channel):
        channelcode = Channel.objects.get(id=channel.id)
        if(channelcode.form != None):
            url = ""+channelcode.form.pageUrl+"?jalaic="+channelcode.uniqueCode+"" if channelcode.form.pageUrl else ""

            return url
        else :
            return None

    def getclick(self, channel):
        request_object = self.context['request']
        additional = request_object.query_params.get('without_additional_information')
        account_id = request_object.query_params.get('account_id')
        user_id = request_object.query_params.get('invoker_id')
        since = request_object.query_params.get('since')
        until = request_object.query_params.get('until')
        if(additional == None and user_id != None):
            if(since != None or until != None):
                data = (ChannelClick.objects.filter(accountId=account_id, channel=channel.id, createdAt__gte=since) & ChannelClick.objects.filter(accountId=account_id, channel=channel.id, createdAt__lte=until)).count()
                return data
            else : 
                return ChannelClick.objects.filter(channel=channel.id, accountId = account_id).count()
    
    def getlead(self, channel):
        request_object = self.context['request']
        additional = request_object.query_params.get('without_additional_information')
        user_id = request_object.query_params.get('invoker_id')
        since = request_object.query_params.get('since')
        until = request_object.query_params.get('until')

        if(additional == None and user_id != None):
            external_service = ExternalService()
            list = external_service.get_summary_channel(accountId=channel.accountId, invokerId=user_id, since=since, until=until)

            if(list != None) :
                if(list['data'] != None):
                    if(list['data']['getSummary']['buckets'] != None):
                        a = list['data']['getSummary']['buckets']
                        chann = next((x for x in a if x['key'] == str(channel.id)), 0)
                        if (chann != 0) :
                            click = self.getclick(channel=channel)
                            channel.totalLead = chann['value']
                            channel.leadRate = channel.totalLead / click if click else 0
                            
                        else:
                            return 0
        return 0
    def get_team(self, channel):
        request_object = self.context['request']
        additional = request_object.query_params.get('without_additional_information')
        user_id = request_object.query_params.get('invoker_id')

        if(additional == None):
            external_service = ExternalService()
            groups = external_service.get_team_by_tenant_id_channel_id(tenant_id=channel.accountId, channelId=channel.id, user_id=user_id)
            return groups
        return None
        
    def get_channel_media(self, channel):
        queryset = Media.objects.filter(channel=channel).first()
        channel_media_serializer = MediaSerializer(queryset, many=False)

        return channel_media_serializer.data
    
    def get_channel_form(self, channel):
        queryset = Form.objects.filter(channel=channel).first()
        channel_media_serializer = FormforCSerializer(queryset, many=False)
        return channel_media_serializer.data

    class Meta:
        model = Channel
        fields = '__all__'
    
    def to_internal_value(self, data):
        if data.get('periodEnd', None) == '':
            data.pop('periodEnd')
        return super(ChannelssSerializer, self).to_internal_value(data)

class CampaignIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = ['id'] 

class ChannelFormSerializer(serializers.ModelSerializer):
    campaign = CampaignIdSerializer(many=False, required=False)
    media = MediaIdSerializer(many=False, required=False)
    form = FormIdSerializer(many=False, required=False)
    class Meta:
        model = Channel
        fields = '__all__'

class FormChannelSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Form
        fields = '__all__'

class ChannelSettingMemberSerializer(serializers.ModelSerializer):
    channel = ChannelIdSerializer(many=False, required=False)

    def getcamp(self, channel):
        queryset = '0'
        return queryset
    
    class Meta:
        model = ChannelSettingMember
        fields = '__all__'

class ChannelSetMemberSerializer(serializers.ModelSerializer):
    totalLeadDistribution = serializers.SerializerMethodField('getcamp')
    leadNotFollowUp = serializers.SerializerMethodField('getcamp')
    channel = ChannelIdSerializer(many=False, required=False)
    user = serializers.SerializerMethodField('get_user')

    def getcamp(self, channel):
        queryset = 0
        return queryset
    
    def get_user(self, channel):
        external_service = ExternalService()
        groups = external_service.get_one_member(accountId=channel.accountId, userId= channel.userId)
        return groups

    class Meta:
        model = ChannelSettingMember
        fields = '__all__'

class FieldforformSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Field
        fields = ['id', 'name', 'type', 'mandatory', 'displayedas', 'alias', 'parameters']

class FormSerializer(serializers.ModelSerializer):
    
    channel_used = serializers.SerializerMethodField('get_channels_length')
    channels = serializers.SerializerMethodField('get_channels')
    fields = serializers.SerializerMethodField('get_field')

    def get_channels_length(self, form):
        queryset = Channel.objects.filter(form=form).count()
        return queryset
    
    def get_channels(self, form):
        queryset = Channel.objects.filter(form=form)[:10]
        channel_serializer = ChannelIdFormSerializer(queryset, many=True)
        return channel_serializer.data
    
    def get_field(self, form):
        queryset = Field.objects.filter(form=form)
        field_serializer = FieldIdFormSerializer(queryset, many=True)
        return field_serializer.data

    class Meta:
        model = Form
        fields = '__all__'

class FormforIdSerializer(serializers.ModelSerializer):
    
    channels = serializers.SerializerMethodField('get_channels')
    fields = serializers.SerializerMethodField('get_field')

    def get_channels(self, form):
        queryset = Channel.objects.filter(form=form)[:10]
        channel_serializer = ChannelIdFormSerializer(queryset, many=True)
        return channel_serializer.data
    
    def get_field(self, form):
        queryset = Field.objects.filter(form=form)
        field_serializer = FieldIdFormSerializer(queryset, many=True)
        return field_serializer.data

    class Meta:
        model = Form
        fields = '__all__'

class FieldIdFormSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Field
        fields = ['id', 'name', 'type', 'mandatory', 'displayedas', 'alias', 'parameters']

class ChannelIdFormSerializer(serializers.ModelSerializer):
    media = serializers.SerializerMethodField('get_channel_media')

    def get_channel_media(self, channel):      
        queryset = Media.objects.filter(channel=channel).first()
        channel_media_serializer = MediaSerializer(queryset, many=False)
        return channel_media_serializer.data

    class Meta:
        model = Channel
        fields = ['id', 'name', 'redirectUrl', 'uniqueCode', 'media']

class FormWithoutMediaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Channel
        fields = ['id', 'name', 'redirectUrl', 'uniqueCode']

class FormforCSerializer(serializers.ModelSerializer):

    channels = serializers.SerializerMethodField('get_channels')
    fields = serializers.SerializerMethodField('get_field')

    def get_channels(self, form):
        queryset = Channel.objects.filter(form=form)[:10]
        channel_serializer = FormWithoutMediaSerializer(queryset, many=True)
        return channel_serializer.data
    
    def get_field(self, form):
        queryset = Field.objects.filter(form=form)
        field_serializer = FieldIdFormSerializer(queryset, many=True)
        return field_serializer.data

    class Meta:
        model = Form
        fields = '__all__'

class FormFieldSerializer(serializers.ModelSerializer):
    form = FormIdSerializer(many=False, required=False)
    field = FieldforformSerializer(many=False, required=False)
    
    class Meta :
        model = FormField
        fields = '__all__'

class FormWithFieldSerializer(serializers.ModelSerializer):
    fields = serializers.SerializerMethodField('get_field')
    
    def get_field(self, form):
        queryset = Field.objects.filter(form=form)
        field_serializer = FieldIdFormSerializer(queryset, many=True)
        return field_serializer.data

    class Meta:
        model = Form
        fields = '__all__'

class ChannelClickSerializer(serializers.ModelSerializer):
    campaign = CampaignChannelSerializer(many=False, required=False)
    form = FormWithFieldSerializer(many=False, required=False)

    class Meta:
        model = Channel
        fields = ['id', 'campaign', 'name', 'detail', 'picture', 'status', 'redirectUrl', 'uniqueCode', 'accountId', 'form']

# minimalis
class MinimalisSerializer(serializers.ModelSerializer):
    campaign = serializers.SerializerMethodField("getcamp")
            
    def getcamp(self, project):
        request_object = self.context['request']
        isOffline = request_object.query_params.get('isOffline')
        fields = request_object.query_params.get('fields')

        q = Campaign.objects.filter(project=project, accountId=project.accountId).values('id', 'name')
        data = list(q)

        for dat in data:
            a = Channel.objects.filter(campaign=dat['id'], accountId=project.accountId).values('id', 'name')

            if(isOffline == 'false'):
                a = Channel.objects.filter(campaign=dat['id'], accountId=project.accountId, media__type="online").values('id', 'name')
            elif(isOffline == 'true' and project.accountId != 142):
                a = Channel.objects.filter(campaign=dat['id'], accountId=project.accountId, media__type="offline").values('id', 'name')            

            dat['channel'] = list(a)
        
        return data

    class Meta:
        model = Project
        fields = ['id', 'name', 'campaign']
            
class MinimalisCatSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField('getstat')
    
    def getstat(self, category):
        request_object = self.context['request']
        account_id = request_object.query_params.get('account_id')
        project_id = request_object.query_params.get('project_id')
        if(project_id != None):
            q = ProjectStatus.objects.filter(category=category, accountId = account_id, project=project_id).values('id', 'name', 'accountId', 'project', 'color')
        else :
            q = ProjectStatus.objects.filter(category=category, accountId = account_id).values('id', 'name', 'accountId', 'project', 'color')
        data = list(q)

        return data

    class Meta:
        model = Category
        fields = ['id', 'name', 'status', 'color']

class ProjectAdminSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="userId")
    projects = serializers.SerializerMethodField('get_project')

    def get_project(self, obj):
        queryset = ProjectAdmin.objects.filter(userId=obj.userId).values_list('project', flat=True)
        a = Project.objects.filter(accountId=obj.accountId, id__in=queryset).values('id', 'name', 'picture')
        
        return a
    
    class Meta :
        model = ProjectAdmin
        fields = ['id', "createdAt", "createdBy" ,"userId", "mask_phone", "email", "status", "ref_id", "accountId", "modifiedAt", "modifiedBy", "projects"]

class ProjectAdminListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="userId")

    def get_dateregister(self, obj):
        date = ProjectAdmin.objects.filter(userId=obj.userId).first()

        return date.createdAt
    
    class Meta :
        model = ProjectAdmin
        fields = '__all__'

class ChannelNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ['id', 'name']

class ChannelListnameSerializer(serializers.ModelSerializer):
    campaign = CampaignChannelSerializer(many=False, required=False)
    form = serializers.SerializerMethodField('get_channel_form')
    media = serializers.SerializerMethodField('get_channel_media')

    def get_channel_form(self, channel):
        queryset = Form.objects.filter(channel=channel).first()
        channel_media_serializer = FormChannelSerializer(queryset, many=False)
        return channel_media_serializer.data

    def get_channel_media(self, channel):      
        queryset = Media.objects.filter(channel=channel).first()
        channel_media_serializer = MediaSerializer(queryset, many=False)
        return channel_media_serializer.data

    class Meta:
        model = Channel
        fields = ['id', 'name', 'campaign', 'form', 'media']

class AllStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectStatus
        fields = ['name']

class ProjectCrationSerializer(serializers.ModelSerializer):    

    class Meta:
        model = Campaign
        fields = ['id', 'name']

class ChannelCrationSerializer(serializers.ModelSerializer):    

    class Meta:
        model = Channel
        fields = ['id', 'name', 'uniqueCode']

class GroupChannelSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChannelGroup
        fields = '__all__'

class UserCampaignSerializer(serializers.ModelSerializer):

    class Meta:
        model = Campaign
        fields = ['id', 'name', 'picture', 'status', 'project']

class UserPOSTCampaignSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserDistribution
        fields = '__all__'
