from api_projects.serializers import ProjectTeamSerializer
from ..models import Campaign, Channel, ChannelGroup, Form, Project, ProjectAdmin, ProjectTeam
from ..services import BaseParameterMixin
from django.http.response import HttpResponse
from rest_framework import mixins, generics
from django.db.models import Q

import json
import os
import requests

class InternalCheckView(mixins.ListModelMixin, 
                    mixins.CreateModelMixin,
                    generics.GenericAPIView):

    serializer_class = ProjectTeamSerializer

    def api_user(self, account_id, user_id):

        base_url_core = os.environ.get('CORE_API_URL')
        url = base_url_core+'internal/check?account_id='+str(account_id)+'&user_id='+str(user_id)
        response = requests.request("GET", url)
        if(response.status_code == 200):
            core = json.loads(response.text)
            return core
        else:
            return None

    def api_groups(self, account_id, user_id):
        base_url_team = os.environ.get('TEAM_API_URL')
        url = base_url_team+'check?accountid='+str(account_id)+'&user_id='+str(user_id)
        response = requests.request("GET", url)
        if(response.status_code == 200):
            team = json.loads(response.text)
            return team
        else:
            return None

    def get(self, request):
        account_id = request.GET.get('account_id')
        user_id = request.GET.get('invoker_id')

        res = {}

        # manggil api core
        api_core = self.api_user(account_id=account_id, user_id=user_id)

        role = None
        allprojects = {'allprojects' : False}
        allcampaigns = {'allcampaigns' : False}
        allchannels = {'allchannels' : False}
        allgroups = {'allgroups' : False}
        projects = {'projects' : []}
        campaigns = {'campaigns' : []}
        channels = {'channels' : []}
        users = {'users' : []}
        groups = {'groups' : []}

        if(user_id != None):
            role = api_core["role"]
            users = {'users' : [int(user_id)]}
            if(api_core["account"] == True ):

                # sales / spv
                if(api_core["role"] == "member") :
                    # manggil api team
                    api_groups = self.api_groups(account_id=account_id, user_id=user_id)
                    
                    # check internal groups kosongan atau nggak
                    if(api_groups.get('groups') != None ):
                        # ambil project by team
                        a = ProjectTeam.objects.filter(accountId=account_id, teamId__in = api_groups["groups"]).distinct('project').values_list("project", flat=True)
                        projects = {'projects' : list(a)}

                        # ambil campaign by project 
                        h = []
                        campaign = Campaign.objects.filter(accountId=account_id, project__in = a).distinct('id').values_list("id", flat=True)
                        h.extend(list(campaign))
                        campaigns = {"campaigns" : h}

                        if account_id == '2891' : 
                            channels = {'channels' : []}
                            allchannels = {'allchannels' : True}

                        else : 
                            # ambil channel by team
                            filter_channel= Channel.objects.filter(campaign__in=h).values_list('id', flat=True)
                            c = ChannelGroup.objects.filter(accountId=account_id, teamId__in = api_groups["groups"], channel__in = list(filter_channel)).distinct('channel').values_list("channel", flat=True)
                            channels = {'channels' : list(c)}

                        # ambil group by project
                        filter_group = ProjectTeam.objects.filter(project__in=list(a)).values_list('teamId', flat=True).distinct('teamId')
                        groups = {'groups' : list(filter_group)}

                # admin
                elif(api_core["role"] == "admin"):
                        # ambil project by admin
                        ap = ProjectAdmin.objects.filter(accountId=account_id, userId = user_id).distinct('project').values_list("project", flat=True)
                        p = Project.objects.filter(Q(id__in = list(ap)) | Q(createdBy=user_id), accountId=account_id).values_list('id', flat=True)
                        projects = {'projects' : list(p)}

                        # ambil campaign by project 
                        h = []
                        campaign = Campaign.objects.filter(accountId=account_id, project__in = p).distinct('id').values_list("id", flat=True)
                        h.extend(list(campaign))
                        campaigns = {"campaigns" : h}

                        if account_id == '2891' : 
                            channels = {'channels' : []}
                            allchannels = {'allchannels' : True}

                        else : 
                            # ambil channel by campaign
                            channel= Channel.objects.filter(accountId=account_id, campaign__in=h).values_list('id', flat=True)
                            channels = {'channels' : list(channel)}

                        # ambil group by project
                        filter_group = ProjectTeam.objects.filter(project__in=list(ap)).values_list('teamId', flat=True).distinct('teamId')
                        groups = {'groups' : list(filter_group)}
                    
                # owner
                elif(api_core["role"] == "owner"):
                    allprojects = {'allprojects' : True}
                    allcampaigns = {'allcampaigns' : True}
                    allchannels = {'allchannels' : True}
                    allgroups = {'allgroups' : True}

        # push ke dictionary respon
        res.update({'role' : role})
        res.update(allprojects)
        res.update(allcampaigns)
        res.update(allchannels)
        res.update(allgroups)
        res.update(projects)
        res.update(campaigns)
        res.update(channels)
        res.update(users)
        res.update(groups)

        return HttpResponse(json.dumps(res, ensure_ascii=False), content_type="application/json")

class CheckForm(mixins.ListModelMixin, 
                    mixins.CreateModelMixin,
                    generics.GenericAPIView):

    serializer_class = ProjectTeamSerializer

    def api_user(self, account_id, user_id):

        base_url_core = os.environ.get('CORE_API_URL')
        url = base_url_core+'internal/check?account_id='+str(account_id)+'&user_id='+str(user_id)
        response = requests.request("GET", url)
        if(response.status_code == 200):
            core = json.loads(response.text)
            return core
        else:
            return None

    def api_groups(self, account_id, user_id):
        base_url_team = os.environ.get('TEAM_API_URL')
        url = base_url_team+'check?accountid='+str(account_id)+'&user_id='+str(user_id)
        response = requests.request("GET", url)
        if(response.status_code == 200):
            team = json.loads(response.text)
            return team
        else:
            return None

    def get(self, request):
        account_id = request.GET.get('account_id')
        user_id = request.GET.get('invoker_id')

        res = {}

        # manggil api core & groups
        api_core = self.api_user(account_id=account_id, user_id=user_id)
        api_groups = self.api_groups(account_id=account_id, user_id=user_id)
        allforms = {'allforms' : False}
        form_json = {'forms' : []}

        if(api_core["account"] == True ):
            if(api_core["role"] == "member") :
                
                # check internal groups kosongan atau nggak
                if(api_groups.get('groups') != None ):
                    # ambil project by team
                    a = ChannelGroup.objects.filter(accountId=account_id, teamId__in = api_groups["groups"]).distinct('channel')
                    p = a.values_list("channel", flat=True)
                    
                    # ambil form by channel
                    f = Channel.objects.filter(accountId=account_id, id__in = list(p))
                    form_id = f.values_list("form", flat=True)

                    form_list = Form.objects.filter(Q(id__in = form_id) | Q(createdBy=user_id), accountId=account_id)
                    form_queryset = form_list.values_list("id", flat=True)
                    form_json =  {"forms" : list(form_queryset)}
            
            # nambah filter get form buat admin
            elif(api_core["role"] == "admin") :
                padmin = ProjectAdmin.objects.filter(accountId = account_id, userId=user_id).values_list('project', flat=True)
                listpadmin = list(padmin)
                channeladmin = Channel.objects.filter(accountId=account_id, campaign__project__in = listpadmin).values_list('form', flat=True)

                formadmin = Form.objects.filter(Q(id__in = channeladmin) | Q(createdBy=user_id), accountId=account_id).values_list('id', flat=True)
                form_json = {"forms" : list(formadmin)}

            elif(api_core["role"] == "owner"):
                allforms = {'allforms' : True}

        # push ke dictionary respon
        res.update(allforms)
        res.update(form_json)

        return HttpResponse(json.dumps(res, ensure_ascii=False), content_type="application/json")