from api_projects.views.internal_check import InternalCheckView
from django.http.response import HttpResponse
from django.db.models import F, Q
from django.db import transaction, IntegrityError
from rest_framework import mixins, generics, exceptions
from rest_framework.views import APIView, Response
from django.http import Http404
from django.core.paginator import Paginator

from ..serializers import ChannelListnameSerializer, ChannelNameSerializer, ChannelSerializer, ChannelClickSerializer, ChannelSetMemberSerializer, ChannelSettingMemberSerializer, ChannelssSerializer
from ..models import Campaign, Channel, ChannelGroup, Form, Media, ProjectTeam, ChannelClick, ChannelSettingMember, UserDistribution
from ..services import ExternalService, BaseParameterMixin
from ..utils import get_uuid, invalid_handler, not_found_exception_handler, succ_resp

import os
import rest_framework
import json

#channel list, create
class ChannelListCreateView(BaseParameterMixin,
                    mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    generics.GenericAPIView):

    serializer_class = ChannelSerializer

    def external(self, accountId, invokerId, since, until):
        external_service = ExternalService()
        
        if(self.get_invoker_id() != None) :
            if(self.get_all() == 'true'):
                if(self.get_since() != None and self.get_until!=None):
                    param = external_service.get_summary_channel(accountId=accountId, invokerId=invokerId, since=since, until = until)
                else :
                    param = external_service.get_summary_channel(accountId=accountId, invokerId=invokerId)
                list = param
                if(list != None ):
                    if(list['data'] != None) :
                        return list['data']['getSummary']['buckets']
        return None
               
    def get(self, request):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        since = self.get_since()
        until = self.get_until()
        additional = self.get_additional()
        limit = self.get_fields()
        base_url_src = os.environ.get('SRC_URL')
        isOffline = self.request.GET.get('isOffline')
        channelGroup = self.request.GET.get('channel_group_only')
        assistant = self.get_assistant()

        # Paging
        size = self.get_size()
        skip = self.get_skip()
        total_channels = 0  # Inisialisasi total_channels

        skip = int(skip) if skip else 0

        if size:
            size = int(size)
            if size == 10:
                size = 200
                if account_id == '2891' :
                    size = 50
        else:
            size = 100
            current_page = 1

        filter_assistant = {}
        exclude_condition = {}
        if assistant == 'true':
            filter_assistant = {"status": "running"}
            if account_id == '2891' :
                lis = UserDistribution.objects.filter(distribution='channel_exclude').values_list('city', flat=True)[0]
                list_ch = [item.strip() for item in lis.split(',')]
                exclude_condition = {"name__in":list_ch}

        # Filter status
        filter_q = self.filter_status_running()
        filter_m = self.filter_media()
        filter_search = self.filter_search()

        filters = {"accountId": account_id}
        if isOffline == 'true' and account_id != 142:
            filters["media__type"] = "offline"

        queryset = Channel.objects.filter(**filters, **filter_q, **filter_m, **filter_search, **filter_assistant).exclude(**exclude_condition).order_by('-createdAt')[skip:skip+size]

        if invoker_id:
            internal = InternalCheckView()
            ow = internal.api_user(account_id=account_id, user_id=invoker_id)
            if ow.get("account"):
                if ow.get("role") == "owner":
                    queryset = Channel.objects.filter(**filters, **filter_q, **filter_m, **filter_search).exclude(**exclude_condition).order_by('-createdAt')[skip:skip+size]

                else:
                    if account_id == '2891' : 
                        queryset = Channel.objects.filter(**filters, **filter_q, **filter_m, **filter_search).exclude(**exclude_condition).order_by('-createdAt')[skip:skip+size]
                    else : 
                        check = internal.get(request=request)
                        res = json.loads(check.content)
                        queryset = Channel.objects.filter(id__in=res['channels'], **filters, **filter_q, **filter_m, **filter_search).exclude(**exclude_condition)[skip:skip+size]

        serializer = ChannelSerializer(queryset, context={'request': request}, many=True)

        if serializer.data:
            if not limit or 'form' in limit:
                js = self.external(account_id, invoker_id, since=since, until=until)
                for p in serializer.data:
                    # ... (code Anda tetap sama)

                    # Update total sales
                    totalSales = ChannelSettingMember.objects.filter(accountId=account_id, channel=p['id']).count()
                    p.update({'totalSales': totalSales})

                    # Update total lead
                    if additional is None:
                        if js:
                            chann = next((x for x in js if x['key'] == str(p['id'])), 0)
                            if chann != 0:
                                p['totalLead'] = chann['value']
                                p['leadRate'] = p['totalLead'] / p['click'] if p['click'] else 0
                            else:
                                p['totalLead'] = 0
                        else:
                            p['totalLead'] = 0


        if channelGroup == 'true':
            total_channels = Channel.objects.filter(**filters, **filter_q, **filter_m, **filter_search).count()
            current_page = (skip // size) + 1 if skip else 1  # Gunakan 1 jika skip tidak ada

            # Menghitung total_pages
            total_pages = (total_channels + size - 1) // size

            # Memperbaiki respon
            res = {
                "total_channels": total_channels,
                "total_pages": total_pages,
                "current_page": current_page,
                "channels": serializer.data
            }
            return succ_resp(data=res)

        return succ_resp(data=serializer.data)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        error_message=None
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()

        temp_data = request.data
        channel_ids = []
        for temp in temp_data:
            name=temp.get("name")
            detail = temp.get("detail")
            redirectUrl = temp.get("redirectUrl")
            periodStart = temp.get("periodStart")
            periodEnd = temp.get("periodEnd")
            picture = temp.get("picture")
            teams= temp.get("groups")
            distr= temp.get("distributionType")
            redis = temp.get("enableRedistribution")
            idle= temp.get("idleDuration")
            startTime = temp.get("startTime")
            endTime = temp.get("endTime")

            media_id = temp["media"]["id"]
            media = Media.objects.filter(id=media_id).first()
            campaign_id = temp["campaign"]["id"]
            campaign = Campaign.objects.filter(id = campaign_id).first()
            form_id = temp.get("form")["id"]
            form = Form.objects.filter(id = form_id).first()
            
            cek_name = Channel.objects.filter(accountId=account_id, campaign=campaign).values_list('name', flat=True)

            if (not campaign):
                return HttpResponse(json.dumps(invalid_handler("Campaign Not Found"), ensure_ascii=False), content_type="application/json", status=rest_framework.status.HTTP_400_BAD_REQUEST)
            if (not form):
                return HttpResponse(json.dumps(invalid_handler("Form Not Found"), ensure_ascii=False), content_type="application/json", status=rest_framework.status.HTTP_400_BAD_REQUEST)
            if (not media):
                return HttpResponse(json.dumps(invalid_handler("Media Not Found"), ensure_ascii=False), content_type="application/json", status=rest_framework.status.HTTP_400_BAD_REQUEST)
            if(name.strip() in list(cek_name)):
                return HttpResponse(json.dumps(invalid_handler("Channel Name Duplicate"), ensure_ascii=False), content_type="application/json", status=rest_framework.status.HTTP_400_BAD_REQUEST)
            # try:
            new_channel = Channel(
                name= name,
                detail = detail,
                redirectUrl = redirectUrl,
                periodStart = periodStart,
                periodEnd = periodEnd,
                picture = picture,
                createdBy = invoker_id,
                accountId = account_id,
                media = media,
                campaign = campaign,
                form = form,
                distributionType = distr,
                enableRedistribution = redis,
                idleDuration = idle,
                startTime = startTime,
                endTime = endTime          
            )
            with transaction.atomic():
                new_channel.save()
                channel_ids.append(new_channel.id)
                
                # buat channelurl
                channelcode = Channel.objects.get(id=new_channel.id)
                if(channelcode.form != None):
                    url = ""+channelcode.form.pageUrl+"?jalaic="+channelcode.uniqueCode+"" if channelcode.form.pageUrl else ""
                    Channel.objects.filter(id=new_channel.id).update(channelUrl = url)
                channel_ids.append(new_channel.id)
                
                # validasi team nya udah ada di projectteam ??
                valid_team_id = []
                for team in teams:
                    # ini buat dapet project id nya
                    ch = Channel.objects.filter(id=new_channel.id).values_list('campaign', flat=True)                         
                    campaigns = Campaign.objects.filter(id__in=ch).values_list('project', flat=True)

                    project_team = ProjectTeam.objects.filter(teamId = team["id"], project__in = campaigns).first()
                    if (project_team!=None):
                        valid_team_id.append(project_team.teamId)
                    else:
                        error_message = "Project Groups Not Found"
                        raise IntegrityError
                # print(valid_team_id)
                for team_id in valid_team_id:
                    new_channel_team = ChannelGroup(
                        teamId = team_id,
                        createdBy = invoker_id,
                        accountId = account_id,
                        channel = new_channel
                    )
                    new_channel_team.save()
                
                # kalo distributionnya percentage
                if(valid_team_id != []) :
                    #store percentage member id
                    valid_member_id = []
                    external_service = ExternalService()
                    teams_api_list = external_service.get_team_by_tenant_id(tenant_id=account_id, user_id=invoker_id)

                    for team in teams_api_list:
                        project_team = ChannelGroup.objects.filter(teamId = team["id"], channel=new_channel).first()
                        # print(valid_team_id)
                        if (project_team != None):
                            team_members = team["member"]
                            if(team_members != None) :
                                for member in team_members:  
                                    if(member["status"] == "active"):
                                        valid_member_id.append(member["id"])

                    totalM = len(valid_member_id)
                    percentage = 1/totalM if totalM else 0
                    
                    for team in teams_api_list:
                        project_team = ChannelGroup.objects.filter(teamId = team["id"], channel=new_channel).first()
                        if (project_team != None):
                            team_members = team["member"]
                            if(team_members != None) :
                                for member in team_members:  
                                    if(member["status"] == "active"):
                                        valid_member_id.append(member["id"])
                                    new_channelmember = ChannelSettingMember(
                                        channel = new_channel,
                                        userId = member["id"],
                                        teamId = team["id"],
                                        percentage = percentage,
                                        accountId = account_id,
                                        createdBy = invoker_id
                                        )
                                    new_channelmember.save()

            # except IntegrityError:
            #     return HttpResponse(json.dumps(invalid_handler(error_message), ensure_ascii=False), content_type="application/json", status=rest_framework.status.HTTP_400_BAD_REQUEST)
        self.queryset = Channel.objects.filter(accountId=account_id, id__in=channel_ids)
        
        return self.list(request)

# field retreive, update, delete
class ChannelRetreiveUpdateDeleteView(BaseParameterMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, 
                    mixins.DestroyModelMixin, 
                    generics.GenericAPIView):
    
    serializer_class = ChannelssSerializer

    def get_queryset(self):
        account_id = self.get_account_id()

        queryset = Channel.objects.filter(accountId=account_id)
        return queryset

    def update_member(self, channel, teams, team_api_list, account_id, invoker_id):
        team_to_delete = []
        team = []
        team_member_del = []
        channel_teams = ChannelGroup.objects.filter(channel = channel)

        for c in teams:
            team.append(c["id"])

        for s in channel_teams:
            if(s.teamId not in team):
                team_to_delete.append(s.teamId)
        
        # ambil team member yang dihapus
        for teamid in team_to_delete:
            member = next((x for x in team_api_list if x['id'] == teamid), 0)
            if(member != 0):
                for m in member['member']:
                    aing = (m['id'])
                    if(m['status']== "inactive"):
                        team_member_del.append({'teamId' : member['id'], 'userId' : aing})
        
        # menghapus member
        if(team_member_del != []):
            for member in team_member_del:
                ChannelSettingMember.objects.filter(channel = channel, accountId=account_id, teamId=member['teamId'], userId=member['userId']).delete()
        
        team_db = []
        member_to_create = []
        for s in channel_teams:
            team_db.append(s.teamId)

        new_id_team = []
        for id in teams:
            if(id['id'] not in team_db):
                new_id_team.append(id)

        # get member from new team
        for teamid in new_id_team:
            member = next((x for x in team_api_list if x['id'] == teamid['id']), 0)
            if(member != 0):
                for m in member['member']:
                    aing = (m['id'])
                    if(m['status']== "active"):
                        member_to_create.append({'teamId' : member['id'], 'userId' : aing})
        
        # create new member team
        if(member_to_create != []):
            for c in member_to_create:
                new_channelmember = ChannelSettingMember(
                                    channel = channel,
                                    userId = c['userId'],
                                    teamId = c['teamId'],
                                    accountId = account_id,
                                    createdBy = invoker_id
                                    )
                new_channelmember.save()  

    def update_percentage(self, dist, channel, teams):
        member_id = ChannelSettingMember.objects.filter(channel=channel)

        member = []
        for a in member_id:
            member.append(a.id)

        if(dist == "percentage"):
            totalM = len(member_id.distinct('userId'))
            percentage = 1/totalM if totalM else 0
            ChannelSettingMember.objects.filter(channel = channel, id__in = [s for s in member]).update(percentage = percentage)
        else : 
            ChannelSettingMember.objects.filter(channel = channel, id__in = [s for s in member]).update(percentage = None)

    def get(self, request, pk):
        account_id = self.get_account_id()
        
        self.queryset = Channel.objects.filter(accountId=account_id)
        return self.retrieve(request, pk)

    @transaction.atomic
    def put(self, request, pk):

        error_message=None
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        external = ExternalService()
        camp_id= Channel.objects.filter(accountId=account_id, id=pk).values_list('campaign', flat=True)
        cek_name = Channel.objects.filter(accountId=account_id, campaign=list(camp_id)[0]).exclude(id=pk).values_list('name', flat=True)

        temp = request.data
        name = temp.get("name")
        teams = temp.get("groups")
        form = temp.get("form")
        media = temp.get("media")
        distr = temp.get("distributionType")
        periodEnd = temp.get("periodEnd")
        startTime = temp.get("startTime")
        endTime = temp.get("endTime")
        idleDuration = temp.get("idleDuration")
        enableRedistribution = temp.get("enableRedistribution")
        distributionType = temp.get("distributionType")

        if (periodEnd == ""):
            periodEnd = None
        
        channel = Channel.objects.filter(id=pk).first()
        if (not channel):
            #throw invalid channel return
            return HttpResponse(json.dumps(invalid_handler("Channel Not Found"), ensure_ascii=False), content_type="application/json")
        
        if(teams != None or form != None or media != None):
            # try:
                with transaction.atomic():
                    
                    if(form != None) :
                        project_team = Form.objects.filter(id = form['id']).first()
                        if (project_team!=None):
                            Channel.objects.filter(id=pk, accountId = account_id).update(form_id = form['id'])
                        else:
                            error_message = "Form Not Found"
                            raise IntegrityError

                    if(media != None) :
                        project_team = Media.objects.filter(id = media['id']).first()
                        if (project_team!=None):
                           Channel.objects.filter(id=pk, accountId = account_id).update(media_id = media['id'])
                        else:
                            error_message = "Media Not Found"
                            raise IntegrityError
                        
                    if(teams != None) :
                        channel_teams = ChannelGroup.objects.filter(channel = channel)
                        valid_team_id = []
                        
                        for team in teams:
                            project_team = ProjectTeam.objects.filter(teamId = team["id"]).first()
                            if (project_team!=None):
                                valid_team_id.append(project_team.teamId)
                            else:
                                error_message = "Project Team Not Found"
                                raise IntegrityError

                        external_service = ExternalService()
                        teams_api_list = external_service.get_team_by_tenant_id(tenant_id=account_id, user_id=invoker_id)

                        self.update_member(channel=channel, teams=teams, team_api_list=teams_api_list, account_id=account_id, invoker_id=invoker_id)
                        # self.update_percentage(dist=distr, channel=channel, teams=teams)
                        #delete existing channel team if not exist in teams parameter
                        for channel_team in channel_teams:
                            if (channel_team.id not in teams):
                                channel_team.delete()

                        #add new channel teams if not exist in channel teams
                        for team in teams:
                            team_id = team["id"]
                            #check if channel team is exist
                            channel_team = ChannelGroup.objects.filter(teamId=team_id, channel = channel).first()
                            if (channel_team == None):
                                new_channelteam = ChannelGroup(
                                    teamId = team_id,
                                    accountId = account_id,
                                    createdBy = invoker_id,
                                    channel = channel
                                )
                                new_channelteam.save()
        if(name != None) :
            if(enableRedistribution == None) : 
                return HttpResponse(json.dumps(invalid_handler("Please fill the 'enableRedistribution true or false' property"), ensure_ascii=False), content_type="application/json")

            if(enableRedistribution == True and startTime == None):
                return HttpResponse(json.dumps(invalid_handler("Please fill the 'startTime, endTime and idleDuration' property"), ensure_ascii=False), content_type="application/json")

            if(name.strip() in list(cek_name)):
                return HttpResponse(json.dumps(invalid_handler("Channel Name Duplicate"), ensure_ascii=False), content_type="application/json", status=rest_framework.status.HTTP_400_BAD_REQUEST)        
            
            if(enableRedistribution != None and enableRedistribution == False):
                external.event_edit_channel(accountId=account_id, channelId=pk, channelName=name, startTime=None, endTime=None, idleDuration=0, enableRedistribution=enableRedistribution, distributionType=distributionType)
            
            if(enableRedistribution != None and enableRedistribution == True):
                # update ke eventbus
                external.event_edit_channel(accountId=account_id, channelId=pk, channelName=name, startTime=startTime, endTime=endTime, idleDuration=idleDuration, enableRedistribution=enableRedistribution, distributionType=distributionType)

        self.queryset = Channel.objects.filter(accountId=account_id)
       
        return self.update(request, pk)
    
    
    def delete(self, request, pk):
        self.destroy(request, pk)
        response = "success delete id "+str(pk)
        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

# channel team retreive by channel id
class ChannelGroupListView(BaseParameterMixin, 
                    generics.GenericAPIView):

    def get(self, request, pk):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        
        channel = Channel.objects.filter(id=pk).first()
        channel_teams = ChannelGroup.objects.filter(channel = channel, accountId=account_id)
        external_service = ExternalService()
        team = external_service.get_teams(tenant_id=account_id)

        response = []
        for channel_team in channel_teams: 
            chann = next((x for x in team if x['id'] == channel_team.teamId), 0)

            if(chann != 0):
                response.append(chann)

        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

# channel retreive & create by campaign id
class CampaignChannelListCreateView(BaseParameterMixin, 
                    mixins.ListModelMixin, 
                    mixins.CreateModelMixin,
                    generics.GenericAPIView):
    
    serializer_class = ChannelSerializer
    
    def list_cities(self):
        lis = ExternalService().get_location()
        name_list = []
        if lis != None:
            cities = [item["name"] for item in lis]
            name_list = [city.lower() for city in cities]

        return name_list
    
    def get(self, request, pk):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        since= self.get_since()
        until = self.get_until()
        base_url_src = os.environ.get('SRC_URL')
        additional = self.get_all()
        assistant = self.get_assistant()
        isOffline = self.request.GET.get('isOffline')

        campaigns = Campaign.objects.filter(id=pk)
        
        # paging
        size = self.get_size()
        skip = self.get_skip()
        skip = int(skip) if skip else 0

        # filter status
        filter_q = self.filter_status_running()
        filter_m = self.filter_media()
        filter_search = self.filter_search()

        # filter assistant
        filter_assistant = {}
        filters = {"campaign__in": campaigns, "accountId":account_id}

        filter_assistant = {}
        exclude_condition = {}
        if assistant == 'true':
            filter_assistant = {"status": "running"}
            if account_id == '2891' :
                lis = UserDistribution.objects.filter(distribution='channel_exclude', accountId=account_id).values_list('city', flat=True)[0]
                if lis != None :
                    list_ch = [item.strip() for item in lis.split(',')]
                    exclude_condition = {"name__in":list_ch}

        # filter channel offline
            if (isOffline == 'true' and account_id != 142):
                filters = {"campaign__in": campaigns, "accountId":account_id, "media__type": "offline"}
            elif (isOffline == 'false'):
                filters = {"campaign__in": campaigns, "accountId":account_id, "media__type": "online"}

        self.queryset = Channel.objects.filter(**filters, **filter_q, **filter_m, **filter_search, **filter_assistant).exclude(**exclude_condition).order_by('-createdAt')
        if (invoker_id != None):
            internal = InternalCheckView()
            ow = internal.api_user(account_id=account_id, user_id=invoker_id)
            if(ow["account"] == True) :
                if(ow["role"] == "owner") :
                    self.queryset = Channel.objects.filter(**filters, **filter_q, **filter_m, **filter_search, **filter_assistant).exclude(**exclude_condition).order_by('-createdAt')
                else:
                    if account_id == '2891' : 
                        self.queryset = Channel.objects.filter( **filters, **filter_q, **filter_m, **filter_search, **filter_assistant).exclude(**exclude_condition).order_by('-createdAt')
                    else : 
                        check = internal.get(request= request)
                        res = json.loads(check.content)
                        self.queryset = Channel.objects.filter(id__in = res['channels'], **filters, **filter_q, **filter_m, **filter_search, **filter_assistant).exclude(**exclude_condition).order_by('-createdAt')
            else :
                self.queryset = Channel.objects.filter(id__in = [], **filters, **filter_q, **filter_m, **filter_search, **filter_assistant).exclude(**exclude_condition).order_by('-createdAt')
        
        if size:
            size = int(size) 
            if assistant == 'true':
                size = 200
            self.queryset = self.queryset[skip:skip+size]

        serializer = ChannelSerializer(self.queryset, context={'request': request}, many=True)

        if(serializer.data != []):
                js = ChannelListCreateView.external(self, account_id, invoker_id, since=since, until=until)

                if additional == 'true':
                    for p in serializer.data:
                        # update channelUrl 
                        p.update({'totalSales' : 0})
                        if isOffline != 'true':
                            # update script form
                            src = str(base_url_src)
                            script = "<script id=\"jalaai-fetch\" data-code=\"-\" src=\""+src+"\"></script>"

                            p['form'].update({"script" : script})

                            if(p['form'] != None and p['media']['name'] == 'Organic Website'):
                                script = "<script id=\"jalaai-fetch\" data-code=\""+p['uniqueCode']+"\" src=\""+src+"\"></script>"
                                p['form'].update({"script" : script})
                            
                            # update total sales
                            totalSales = ChannelSettingMember.objects.filter(accountId=account_id, channel=p['id']).distinct('userId').count()
                            p.update({'totalSales' : totalSales})

                        if(js != None) :
                            chann = next((x for x in js if x['key'] == str(p['id'])), 0)
                            if(chann != 0):
                                p['totalLead'] = chann['value']
                                p['leadRate'] = p['totalLead'] / p['click'] if p['click'] else 0

                            else:
                                p['totalLead'] = 0
                    
        return succ_resp(data=serializer.data)

    #create channel with campaign and other nested object
    @transaction.atomic
    def post(self, request, pk):
        error_message=None
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        temp_data = request.data
        cek_name = Channel.objects.filter(accountId=account_id, campaign=pk).values_list('name', flat=True)

        channel_ids = []
        for temp in temp_data:
            name=temp.get("name")
            detail = temp.get("detail")
            redirectUrl = temp.get("redirectUrl")
            periodStart = temp.get("periodStart")
            periodEnd = temp.get("periodEnd")
            picture = temp.get("picture")
            teams= temp.get("groups")
            distr= temp.get("distributionType")
            redis = temp.get("enableRedistribution")
            idle= temp.get("idleDuration")
            startTime = temp.get("startTime")
            endTime = temp.get("endTime")

            media_id = temp["media"]["id"]
            media = Media.objects.filter(id=media_id).first()

            campaign = Campaign.objects.filter(id = pk).first()
            
            form_id = temp.get("form")["id"]
            form = Form.objects.filter(id = form_id).first()
            
            if (not campaign):
                return HttpResponse(json.dumps(invalid_handler("Campaign Not Found"), ensure_ascii=False), content_type="application/json", status=rest_framework.status.HTTP_400_BAD_REQUEST)
            if (not form):
                return HttpResponse(json.dumps(invalid_handler("Form Not Found"), ensure_ascii=False), content_type="application/json", status=rest_framework.status.HTTP_400_BAD_REQUEST)
            if (not media):
                return HttpResponse(json.dumps(invalid_handler("Media Not Found"), ensure_ascii=False), content_type="application/json", status=rest_framework.status.HTTP_400_BAD_REQUEST)
            if(name.strip() in list(cek_name)):
                return HttpResponse(json.dumps(invalid_handler("Channel Name Duplicate"), ensure_ascii=False), content_type="application/json", status=rest_framework.status.HTTP_400_BAD_REQUEST)        
            if UserDistribution.objects.filter(accountId=account_id, distribution='create_campaign_preferential').exists() == True :
                distr = 'preferentialSales'
            # try:
            new_channel = Channel(
                name= name,
                detail = detail,
                redirectUrl = redirectUrl,
                periodStart = periodStart,
                periodEnd = periodEnd,
                picture = picture,
                createdBy = invoker_id,
                accountId = account_id,
                media = media,
                campaign = campaign,
                form = form,
                distributionType = distr,
                enableRedistribution = redis,
                idleDuration = idle,
                startTime = startTime,
                endTime = endTime
            )

            with transaction.atomic():
                new_channel.save()

                # buat channelurl
                channelcode = Channel.objects.get(id=new_channel.id)
                if(channelcode.form != None):
                    url = ""+channelcode.form.pageUrl+"?jalaic="+channelcode.uniqueCode+"" if channelcode.form.pageUrl else ""
                    Channel.objects.filter(id=new_channel.id).update(channelUrl = url)
                channel_ids.append(new_channel.id)
                
                # validasi team nya udah ada di projectteam ??
                valid_team_id = []
                for team in teams:
                    # ini buat dapet project id nya
                    ch = Channel.objects.filter(id=new_channel.id).values_list('campaign', flat=True)
                    campaigns = Campaign.objects.filter(id__in=ch).values_list('project', flat=True)

                    project_team = ProjectTeam.objects.filter(teamId = team["id"], project__in = campaigns).first()
                    if (project_team!=None):
                        valid_team_id.append(project_team.teamId)
                    # else:
                    #     error_message = "Project Groups Not Found"
                    #     raise IntegrityError

                # print(valid_team_id)
                for team_id in valid_team_id:
                    new_channel_team = ChannelGroup(
                        teamId = team_id,
                        createdBy = invoker_id,
                        accountId = account_id,
                        channel = new_channel
                    )
                    new_channel_team.save()
                
                # kalo distributionnya percentage
                if(valid_team_id != []) :
                    #store percentage member id
                    valid_member_id = []
                    external_service = ExternalService()
                    teams_api_list = external_service.get_team_by_tenant_id(tenant_id=account_id, user_id=invoker_id)

                    for team in teams_api_list:
                        project_team = ChannelGroup.objects.filter(teamId = team["id"], channel=new_channel).first()
                        # print(valid_team_id)
                        if (project_team != None):
                            team_members = team["member"]
                            if(team_members != None) :
                                for member in team_members:
                                    if(member["status"] == "active"):
                                        valid_member_id.append(member["id"])

                    percentage = None
                    if(distr == "percentage"):
                        totalM = len(valid_member_id)
                        percentage = 1/totalM if totalM else 0

                    for team in teams_api_list:
                        project_team = ChannelGroup.objects.filter(teamId = team["id"], channel=new_channel).first()
                        if (project_team != None):
                            team_members = team["member"]
                            if(team_members != None) :
                                for member in team_members:
                                    if(member["status"] == "active"):
                                        valid_member_id.append(member["id"])
                                    new_channelmember = ChannelSettingMember(
                                        channel = new_channel,
                                        userId = member["id"],
                                        teamId = team["id"],
                                        percentage = percentage,
                                        accountId = account_id,
                                        createdBy = invoker_id
                                        )
                                    new_channelmember.save()

                if distr == 'preferentialSales':
                        campaign_name = Campaign.objects.filter(id=pk).values_list('name', flat=True)[0]
                        incity = next((x for x in self.list_cities() if x in str(campaign_name).lower()), 0)
                        if incity != 0:
                            userids = UserDistribution.objects.filter(distribution='city', accountId=account_id, city__icontains=str(incity)).values_list('userId', flat=True)
                            channeluser = []
                            for userid in userids:
                                channeluser.append(
                                        ChannelSettingMember(teamId=None, userId=userid, createdBy=invoker_id, accountId=account_id, channel_id=new_channel.id, type='preferential_city')
                                    )
                            batch_size = 10000
                            for i in range(0, len(channeluser), batch_size):
                                batch = channeluser[i:i + batch_size]
                                ChannelSettingMember.objects.bulk_create(batch)

            if(account_id == '166'):
                ExternalService().update_validator(accountId=account_id, channelId=new_channel.id)
            # except IntegrityError:
            #     return HttpResponse(json.dumps(invalid_handler(error_message), ensure_ascii=False), content_type="application/json", status=rest_framework.status.HTTP_400_BAD_REQUEST)
        self.queryset = Channel.objects.filter(accountId=account_id, id__in=channel_ids)
        
        return self.list(request)

# channel click
class ChannelByCodeView(BaseParameterMixin,
                    mixins.ListModelMixin,
                    generics.GenericAPIView):
    
    serializer_class = ChannelClickSerializer
  
    def get(self, request):
    
        code = self.request.GET.get('code')
        hit = self.request.GET.get('hit')
        if (code != None):
            self.queryset = (Channel.objects.filter(uniqueCode=code))

        try:
            channel = Channel.objects.get(uniqueCode=code)

            with transaction.atomic():
                if(hit == 'true') :
                    Channel.objects.filter(id=channel.id).update(click = F('click')+1)
                    account = self.queryset.values_list('accountId', flat=True)
                    new = ChannelClick(
                        accountId = account,
                        channel = Channel.objects.get(id = channel.id)
                    )
                    new.save()

        except:
            return not_found_exception_handler(exceptions.NotFound(), Http404)

        return self.list(request)

# edit percentage member
class MemberView(BaseParameterMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
                    
    serializer_class = ChannelSettingMemberSerializer

    def get_queryset(self):
        account_id = self.get_account_id()

        queryset = ChannelSettingMember.objects.filter(accountId=account_id)
        return queryset
    
    def get_user(self, accountId):
        external_service = ExternalService()
        groups = external_service.get_member(accountId=accountId)
        return groups

    def get_info_lead(self, accountId, invokerId, channelId, since, until, get_additional):
        external_service = ExternalService()
        if(since != None and until !=None):
            param = external_service.get_leads(accountId=accountId, invokerId=invokerId, channel_id=channelId, since=since, until = until)
        else :
            param = external_service.get_leads(accountId=accountId, invokerId=invokerId, channel_id=channelId)

        if(invokerId != None) :
            if(get_additional == None):
                
                list = param
                if(list != None ):
                    if(list['data'] != None) :
                        if(list['data']['getSummary']['buckets'] != None) :
                            return list['data']['getSummary']['buckets']

        return None

    def update_member(self, channel, team_api_list, account_id, invoker_id):
        
        channel_team = ChannelGroup.objects.filter(channel = channel)
        channel_member = ChannelSettingMember.objects.filter(channel=channel).values('teamId', 'userId').order_by('teamId', 'userId')
        teams = []
        
        for teamid in channel_team:
            member = next((x for x in team_api_list if x['id'] == teamid.teamId), 0)
            if(member != 0):
                for m in member['member']:
                    aing = (m['id'])
                    if(m['status']== "active"):
                        teams.append({'teamId' : member['id'], 'userId' : aing})

        for i in teams:
            if i not in list(channel_member):
                new_channelmember = ChannelSettingMember(
                                    channel = channel,
                                    userId = i['userId'],
                                    teamId = i['teamId'],
                                    accountId = account_id,
                                    createdBy = invoker_id
                                    )
                new_channelmember.save()
        
        for chan_team in list(channel_member):
            if chan_team not in teams:
                ChannelSettingMember.objects.filter(channel = channel, accountId=account_id, teamId=chan_team['teamId'], userId=chan_team['userId']).delete()
    
    def get(self, request, pk):
        account_id = request.GET.get('account_id')
        invoker_id = request.GET.get('invoker_id')
        since= request.GET.get('since')
        until = request.GET.get('until')
        isOnline = request.GET.get('isOnline')
        additional = request.GET.get('without_additional_information')

        channel = Channel.objects.filter(id=pk).first()
        self.queryset = ChannelSettingMember.objects.filter(channel = channel, accountId=account_id).distinct('userId')
        serializer = ChannelSettingMemberSerializer(self.queryset, many= True)
        js = self.get_user(accountId=account_id)

        # update percentage
        external_service = ExternalService()
        teams_api_list = external_service.get_team_by_tenant_id(tenant_id=account_id, user_id=invoker_id)
        campaignid = Channel.objects.filter(id=pk).values_list('campaign', flat=True).first()
        self.queryset = UserDistribution.objects.filter(campaignId = campaignid, accountId=account_id).distinct('userId')

        self.queryset = ChannelSettingMember.objects.filter(channel = channel, accountId=account_id).distinct('userId')
        if channel.distributionType != 'preferentialSales':
            # check member yang dihapus / ditambah
            self.update_member(channel=channel, team_api_list=teams_api_list, account_id=account_id, invoker_id=invoker_id)
            self.queryset = ChannelSettingMember.objects.filter(channel = channel, accountId=account_id).distinct('userId')
        else :
            self.queryset = ChannelSettingMember.objects.filter(
                channel=channel, accountId=account_id, status_distribution='enable', type='preferential_campaign')
            # Jika data dengan type='preferential_campaign' kosong, maka mengambil data dengan type='preferential_city'
            if not self.queryset.exists():
                self.queryset = ChannelSettingMember.objects.filter(
                    channel=channel, accountId=account_id, status_distribution='enable', type='preferential_city')


        # disable jika user kpi 0
        ChannelSettingMember.objects.filter(Q(percentage=0) | Q(percentage__isnull=True), channel = channel, accountId=account_id, channel__distributionType='percentage').update(status_distribution='disable')
        
        serializer = ChannelSettingMemberSerializer(self.queryset, many= True)
        if(serializer.data != []):
            if(js != None) :
                for p in serializer.data:
                    chann = next((x for x in js if x['id'] == p['userId']), 0)
                    if(chann != 0):
                        p.update({"user" : {"id": chann["id"],"name" : chann['name'], "email" : chann['email'], "role" : chann['role'], "isOnline" : chann['isOnline'],"picture" : chann['picture'], "status" : chann['status'], "phone" : chann['phone'], "registered" : None}, "leadNotFollowUp" : 0, "totalLeadDistribution" : 0})     
                        if chann['isOnline'] == False:
                            p.update({'status_distribution' : 'disable'})

            api_total = self.get_info_lead(accountId=account_id, invokerId=invoker_id, channelId=pk, since=since, until=until, get_additional=additional)
            if(api_total != None):
                for s in serializer.data:
                    lead = next((x for x in api_total if x['key'] == str(s['userId'])), 0)
                    if(lead != 0):
                        new_lead = next((x for x in lead['buckets'] if x['key'] == '1'), 0)
                        s.update({"leadNotFollowUp" : new_lead['value'], "totalLeadDistribution" : lead['value']})   

        if(isOnline == 'true'):
            response_validator = []
            for s in serializer.data:
                if(s['user']['status'] == 'active' and s['user']['isOnline'] == True):
                    response_validator.append(s)
            return succ_resp(data=response_validator)

        return succ_resp(data=serializer.data)

    def put(self, request, *args, **kwargs):
        account_id = self.get_account_id()
        error_message = None
        data = request.data 
        channel = Channel.objects.filter(id=self.kwargs['pk']).first()
        instances = []
        # try:
        with transaction.atomic():
            for temp_dict in data:
                id = temp_dict["id"]
                percentage = temp_dict['percentage']
                obj = ChannelSettingMember.objects.get(id=id, channel=channel, accountId=account_id)

                obj.percentage = percentage
                obj.save()
                instances.append(obj)
            serializer = ChannelSettingMemberSerializer(instances, many=True)
        # except IntegrityError:
        #     return HttpResponse(json.dumps(invalid_handler(error_message), ensure_ascii=False), content_type="application/json", status=rest_framework.status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data)
    
    def delete(self, request, pk):
        self.destroy(request, pk)
        response = "success delete id "+str(pk)
        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

class StatusMemberView(BaseParameterMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):

    serializer_class = ChannelSetMemberSerializer

    def get_queryset(self):
        account_id = self.get_account_id()

        queryset = ChannelSettingMember.objects.filter(accountId=account_id)
        return queryset

    def get(self, request, **kwargs):
        account_id = self.get_account_id()
        
        channel = Channel.objects.filter(id=self.kwargs["channel_pk"], accountId = account_id).first()
        self.queryset = ChannelSettingMember.objects.filter(id=self.kwargs['pk'], channel=channel, accountId = account_id)

        return self.retrieve(request, **kwargs)
    
    def put(self, request, **kwargs):
        account_id = self.get_account_id()
        
        channel = Channel.objects.filter(id=self.kwargs["channel_pk"], accountId = account_id).first()
        self.queryset = ChannelSettingMember.objects.filter(id=self.kwargs['pk'], channel=channel, accountId = account_id)

        return self.update(request, **kwargs)


class ChannelNameCreateView(BaseParameterMixin,
                    mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    generics.GenericAPIView):

    serializer_class = ChannelNameSerializer

    def get(self, request):
        account_id = self.get_account_id()
        self.queryset = Channel.objects.filter(accountId=account_id)
        if(account_id != None) : 
            self.queryset = Media.objects.filter(accountId = account_id)

        return self.list(request)

class ChannelNameView(BaseParameterMixin,
                    mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    generics.GenericAPIView):

    serializer_class = ChannelListnameSerializer


    def get(self, request):
        account_id = self.get_account_id()

        self.queryset = Channel.objects.filter(accountId=account_id)

        return self.list(request)