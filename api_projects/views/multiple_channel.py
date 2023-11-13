from api_projects.views.internal_check import InternalCheckView
from django.http.response import HttpResponse
from django.db.models import F, Q
from django.db import transaction, IntegrityError
from rest_framework import mixins, generics, exceptions
from rest_framework.views import APIView, Response
from django.http import Http404

from ..serializers import ChannelListnameSerializer, ChannelNameSerializer, ChannelSerializer, ChannelClickSerializer, ChannelSetMemberSerializer, ChannelSettingMemberSerializer, ChannelssSerializer
from ..models import Campaign, Channel, ChannelGroup, Form, Media, ProjectTeam, ChannelClick, ChannelSettingMember
from ..services import ExternalService, BaseParameterMixin
from ..utils import err_resp, get_uuid, invalid_handler, not_found_exception_handler, succ_resp

import os
import rest_framework
import json

class CreateMultipleChannel(BaseParameterMixin,
                    mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    generics.GenericAPIView):

    serializer_class = ChannelSerializer    
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        error_message=None
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()

        temp = request.data

        name = temp.get("channel_names")
        redirectUrl = temp.get("redirectUrl")
        periodStart = temp.get("periodStart")
        periodEnd = temp.get("periodEnd")
        picture = temp.get("picture")
        distr= temp.get("distributionType")
        redis = temp.get("enableRedistribution")
        idle= temp.get("idleDuration")
        startTime = temp.get("startTime")
        endTime = temp.get("endTime")

        media_id = temp.get("media_id")
        campaign_ids = temp.get("campaign_ids")
        form_id = temp.get("form_id")
        teams = temp.get("group_ids")

        channel_ids = []
        if distr == None or distr == '':
            distr = 'roundRobin'
            
        for c in campaign_ids :
            for ch_name in name:
                new_channel = Channel(
                    name= ch_name,
                    redirectUrl = redirectUrl,
                    periodStart = periodStart,
                    periodEnd = periodEnd,
                    picture = picture,
                    createdBy = invoker_id,
                    accountId = account_id,
                    media_id = media_id,
                    campaign_id = c,
                    form_id = form_id,
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
                    
                    # validasi team nya udah ada di projectteam ??
                    valid_team_id = []
                    for team in teams:
                        # ini buat dapet project id nya
                        ch = Channel.objects.filter(id=new_channel.id).values_list('campaign', flat=True)                         
                        campaigns = Campaign.objects.filter(id__in=ch).values_list('project', flat=True)

                        project_team = ProjectTeam.objects.filter(teamId = team, project__in = campaigns).first()
                        if (project_team != None):
                            valid_team_id.append(project_team.teamId)
                        else:
                            return err_resp(status=400, message="Project Groups Not Found or Not include Project Groups")
                    
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
        self.queryset = Channel.objects.filter(accountId=account_id)
        res = 'succes create channel id' + str(channel_ids)

        return succ_resp(data=res)