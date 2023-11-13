from datetime import datetime, timedelta
import requests
import json
from .models import Channel, ChannelGroup, ChannelSettingMember, CustomStatus, ProjectTeam, Project
from django.conf import settings
import os
from django.db.models import Q


class BaseParameterMixin():
    def get_account_id(self):
        account_id = self.request.GET.get('account_id')
        return account_id

    def get_invoker_id(self):
        invoker_id = self.request.GET.get('invoker_id')
        return invoker_id
    
    def get_user_id(self):
        user_id = self.request.GET.get('user_id')
        return user_id
    
    def get_invoker_role(self):
        invoker_role = self.request.GET.get('invoker_role')
        return invoker_role
    
    def get_since(self):
        since = self.request.GET.get('since')
        return since
    
    def get_until(self):
        until = self.request.GET.get('until')
        return until
    
    def get_isOnline(self):
        until = self.request.GET.get('isOnline')
        return until
    
    def get_additional(self):
        additional = self.request.GET.get('without_additional_information')
        return additional
    
    def get_all(self):
        additional = self.request.GET.get('with_additional_information')
        return additional
    
    def get_project_param(self):
        additional = self.request.GET.get('project_id')
        return additional
    
    def get_status(self):
        until = self.request.GET.get('status')
        return until
    
    def get_media(self):
        media = self.request.GET.get('media')
        return media

    def get_size(self):
        until = self.request.GET.get('size')
        return until
    
    def get_skip(self):
        until = self.request.GET.get('skip')
        return until
    
    def get_search(self):
        search = self.request.GET.get('search')
        return search
        
    def get_limit_name(self):
        search = self.request.GET.get('limit')
        return search
    
    def get_fields(self):
        search = self.request.GET.get('fields')
        return search

    def get_assistant(self):
        search = self.request.GET.get('assistant_only')
        return search
    
    def get_category(self):
        search = self.request.GET.get('category')
        return search

    def get_projects(self):
        search = self.request.GET.get('projects')
        return search

    def get_existing(self):
        existing = self.request.GET.get('existing')
        return existing

    def get_all_campaign(self):
        all_campaign = self.request.GET.get('all_campaign')
        return all_campaign
    
    def filter_status(self):
        status = self.get_status()

        filter_q = {}
        if(status != None):
            if(status == '[]'):
                filter_q = {}
            else :
                # buat baca array string jadi arrray
                statuses = list(map(lambda x: x.split('/')[-1], json.loads(status)))
                filter_q = {"status__in" : statuses}

        return filter_q
    
    def filter_media(self):
        media = self.get_media()

        filter_m = {}
        if(media != None):
            media = [str(x) for x in self.request.GET.get('media', '').split(',')]

        filter_m = {}
        if(media != None):

            filter_m = {"media__type__in": media}

        return filter_m
    
    def filter_date(self):
        since = self.get_since()
        until = self.get_until()

        filterd = {}
        if(since != None and until != None):
            filterd = {"createdAt__range": [str(since), str(until)]}

        return filterd
    
    def filter_period(self):
        since = self.get_since()
        until = self.get_until()
        # until = datetime.strptime(until, '%Y-%m-%d') + timedelta(days=1)
        filterd = {}
        if(since != None and until != None):
            # filterd = {"periodStart__range": [str(since), str(until)]}
            # filterd = {"periodStart__date__gte" : str(since), "periodStart__date__lte" : str(until)}
            if {"periodStart__isnull" == True}:
                filterd ={"periodStart__date__lte": until}
            else :
                filterd ={"periodStart__date__lte": until, "periodEnd__date__gte": since}

        elif since != None and until == None:
            filterd ={}

        return filterd
    
    def filter_search(self):
        search = self.get_search()

        filter_s = {}
        if(search != None):
            filter_s = {"name__icontains":search}
        
        return filter_s
    
    def filter_status_running(self):
        status = self.get_status()
        if(status != None):
            status = [str(x) for x in self.request.GET.get('status', '').split(',')]
        
        filter_ch = {}
        if(status != None):
            filter_ch = {"status__in": status}
        
        return filter_ch

    def filter_status_active(self):
        status = self.get_status()

        if(status != None):
            status = [str(x) for x in self.request.GET.get('status', '').split(',')]
        
        filter_ch = {}
        if(status != None):
            filter_ch = {"status__in": status}
        
        return filter_ch

    def filter_project_by_admin(self):
        projects = self.get_projects()

        if(projects != None):
            projects = [int(x) for x in projects.split(',')]
        
        filter_ch = {}
        if(projects != None):
            filter_ch = {"project__in": projects}
        
        return filter_ch
    
    def filter_assistant(self):
        ass = self.get_assistant()
        account = self.get_account_id()

        res = False
        if(ass == 'true'):
            coreapi = ExternalService().get_settings_product(account=account)
            if(coreapi != None) :
                apiintegration = coreapi['value']['apiIntegration']

                if(apiintegration == True) :
                    return True
        
        return res
    
    def filter_project_id(self):
        project = self.get_project_param()

        if(project != None):
            project = [int(x) for x in project.split(',')]
        
        filter_ch = {}
        if(project != None):
            filter_ch = {"project__in": project}
        
        return filter_ch

        
    def page_limit(self, size, skip):
        # MyModel.objects.all()[OFFSET:OFFSET+LIMIT]
        total_limit = int(size) + int(skip)

        return total_limit
    
    def _pagination(self, size, skip):
        # paging

        if(size != None):
            if(skip != None) :
                size = self.page_limit(size=size, skip=skip)
                skip = int(skip)
            else :
                size = self.page_limit(size=size, skip=0)
                skip = None
        else :
            skip = None
            size = None
        
        var = []
        var.append(skip)
        var.append(size)

        for i in range(1, var):
            fix = int(i)+':', int[i]
            return list(fix)
    
    def filter_category(self):
        category = self.get_category()
        account_id = self.get_account_id()
        paramcustom = ['Custom', 'custom']
        paramdef = ['Default', 'default']

        filterd = Q()
        if(category != None):
            if category in paramcustom :
                custom = CustomStatus.objects.filter(accountId=account_id).values_list('name', flat=True)
                filterd &= Q(name__in=custom)
            elif category in paramdef :
                custom = CustomStatus.objects.filter(accountId=account_id).values_list('name', flat=True)
                filterd &= ~Q(name__in=custom)
            else :
                cat = 0
                if category == 'New' or category == 'new' :
                    cat = 1
                elif category == 'Hot' or category == 'hot':
                    cat = 2
                elif category == 'Warm' or category == 'warm':
                    cat = 3
                elif category == 'Cold' or category == 'cold':
                    cat = 4
                elif category == 'Unqualified' or category == 'unqualified':
                    cat = 5
                elif category == 'Closed' or category == 'closed':
                    cat = 6

                filterd &= Q(category=cat)

        return filterd
        
class ExternalService():

    def __init__(self):
        return

    base_url_team = os.environ.get('TEAM_API_URL')
    base_url_product = os.environ.get('PRODUCT_API')
    base_url_report = os.environ.get('REPORT_API')
    base_url_bus = os.environ.get('EVENT_BUS')
    base_url_core = os.environ.get('CORE_API_URL')
    base_url_validator = os.environ.get('VALIDATOR_API_URL')

    def get_member(self, accountId):
        url = self.base_url_team+"members?accountid="+str(accountId)
        # print(url)
        response = requests.request("GET", url)
        if(response.status_code == 200):
            teams = json.loads(response.text)
            
            return teams
        else:
            return None

    def get_one_member(self, accountId, userId):
        url = self.base_url_team+"members?accountid="+str(accountId)
        # print(url)
        response = requests.request("GET", url)
        if(response.status_code == 200):
            teams = json.loads(response.text)        
            for team in teams:
                if (team.get("id") == userId):
                    return ({"name" : team.get("name"), "email" : team.get("email"), "role" : team.get("role"), "picture" : team.get("picture"), "status" : team.get("status")})
            return None
        else:
            return None

    def get_team_by_tenant_id(self, tenant_id, user_id):
        url = self.base_url_team+"groups?accountid="+str(tenant_id)
        response = requests.request("GET", url)
        if(response.status_code == 200):
            team = json.loads(response.text)
            return team
        else:
            return None
    
    def get_team_by_ava(self, tenant_id, user_id):
        url = self.base_url_team+"groups?accountid="+str(tenant_id)
        response = requests.request("GET", url)
        if(response.status_code == 200):
            teams = []
            res = json.loads(response.text)
            # print(res)

            for team in res:              
                like = ({"id" : team.get("id"), "name" : team.get("name"), "avatar" : team.get("avatar")})
                teams.append(like)
            
            return teams
        else:
            return None
    
    def get_team_by_tenant_id_project_id(self, tenant_id, projectId, user_id):
        project = Project.objects.get(id = projectId)
        if (project):
            project_teams = ProjectTeam.objects.filter(project=project)
            project_team_ids=[]
            for project_team in project_teams:
                project_team_ids.append(project_team.teamId)
            url = self.base_url_team+"groups?accountid="+str(tenant_id)
            response = requests.request("GET", url)
            project_team_return=[]
            if(response.status_code == 200):
                project_team_tenants= json.loads(response.text)
                for project_team_tenant in  project_team_tenants:
                    if (project_team_tenant["id"] in project_team_ids):
                        project_team_return.append(project_team_tenant)
                return project_team_return
            else:
                return None
        else:
            return None
    
    # get channel team
    def get_team_by_tenant_id_channel_id(self, tenant_id, channelId, user_id):
        channel = Channel.objects.get(id = channelId)
        if (channel):
            project_teams = ChannelGroup.objects.filter(channel=channel)
            project_team_ids=[]
            for project_team in project_teams:
                project_team_ids.append(project_team.teamId)
            url = self.base_url_team+"groups?accountid="+str(tenant_id)
            response = requests.request("GET", url)
            project_team_return=[]
            if(response.status_code == 200):
                project_team_tenants= json.loads(response.text)
                for project_team_tenant in  project_team_tenants:
                    if (project_team_tenant["id"] in project_team_ids):
                        project_team_return.append(project_team_tenant)
                return project_team_return
            else:
                return None
        else:
            return None

    #get team, single return
    def get_team_by_tenant_id_team_id(self, tenant_id, team_id, user_id):
        url = self.base_url_team+"groups?accountid="+str(tenant_id)
        response = requests.request("GET", url)
        if(response.status_code == 200):
            teams= json.loads(response.text)
            for team in teams:
                if (team.get("id")==team_id):
                    return team
            return None
        else:
            return None
    
    def get_teams(self, tenant_id):
        url = self.base_url_team+"groups?accountid="+str(tenant_id)

        response = requests.request("GET", url)
        if(response.status_code == 200):
            teams= json.loads(response.text)
            return teams
        else:
            return None

    def get_product_by_tenant_id(self, product_id, tenant_id):
        url = self.base_url_product+"products/"+str(product_id)+"projects?account_id="+str(tenant_id)
        response = requests.request("GET", url)
        if(response.text):
            return json.loads(response.text)
        else:
            return None
    
    def get_summary_product(self, project_id, tenant_id):
        url = self.base_url_product+"projects/"+str(project_id)+"/products?account_id="+str(tenant_id)
        response = requests.request("GET", url)
        if(response.status_code == 200):
            product = len(json.loads(response.text))
            return product
        else:
            return 0

    def get_summary_project(self, accountId, invokerId, since=None, until=None):
        url = self.base_url_report+"?account_id="+str(accountId)+"&invoker_id="+str(invokerId)

        if(since != None and until != None):
            # sementara (kudu ganti biar gak bar bar)
            since = datetime.fromisoformat(since) - timedelta(1)
            until = datetime.fromisoformat(until) + timedelta(days=1)
            
            since = since.strftime('%Y-%m-%dT%H:%M:%S.%f%z')+"Z"
            until = until.strftime('%Y-%m-%dT%H:%M:%S.%f%z')+"Z"

            since = json.dumps(str(since))
            until = json.dumps(str(until))
            filters =  "filters: {createdAt: {since: " + since +", until: " + until + "}}"
            
        elif(since != None and until == None):
            since = datetime.fromisoformat(since) 
            until = since + timedelta(1)
            
            since = since.strftime('%Y-%m-%dT%H:%M:%S.%f%z')+"Z"
            until = until.strftime('%Y-%m-%dT%H:%M:%S.%f%z')+"Z"

            since = json.dumps(str(since))
            until = json.dumps(str(until))
            filters =  "filters: {createdAt: {since: " + since +", until: " + until + "}}"

        else:
            filters = ''

        data = {"query": "{ getSummary( grouping:[ {by:project}, {by:category, fillGap: true} ] "+filters+" values:[count] ){ value(type: count) buckets{ key alias value(type:count) buckets{key alias value(type: count)} } }}"}

        response = requests.request("POST", url = url, json=data, headers={ 'Content-Type': 'application/json','Accept': 'application/json',})

        if(response.status_code == 200):
            return json.loads(response.text)
        else:
            return None
    
    def get_summary_campaign(self, accountId, invokerId, since=None, until=None):
        url = self.base_url_report+"?account_id="+str(accountId)+"&invoker_id="+str(invokerId)

        if(since !=None and until != None):
            since = json.dumps(since)
            until = json.dumps(until)
            filters =  "filters: {createdAt: {since: " + since +", until: " + until + "}}"
        else:
            filters = ''

        data = {"query": "{ getSummary( grouping:[ {by:campaign} ] "+filters+" values:[count] ){ buckets{ key alias value(type:count) } }}"}

        response = requests.request("POST", url = url, json=data, headers={ 'Content-Type': 'application/json','Accept': 'application/json',})

        if(response.status_code == 200):
            return json.loads(response.text)
        else:
            return None
    
    def get_summary_channel(self, accountId, invokerId, since=None, until=None):
        url = self.base_url_report+"?account_id="+str(accountId)+"&invoker_id="+str(invokerId)

        if(since !=None and until != None):
            since = json.dumps(since)
            until = json.dumps(until)
            filters =  "filters: {createdAt: {since: " + since +", until: " + until + "}}"
        else:
            filters = ''

        data = {"query": "{ getSummary( grouping:[ {by:channel} ] "+filters+" values:[count] ){ buckets{ key alias value(type:count) } }}"}

        response = requests.request("POST", url = url, json=data, headers={ 'Content-Type': 'application/json','Accept': 'application/json',})

        if(response.status_code == 200):
            return json.loads(response.text)
        else:
            return None

    def get_closing_leads(self, accountId, invokerId, since=None, until=None):
        url = self.base_url_report+"?account_id="+str(accountId)+"&invoker_id="+str(invokerId)

        if(since !=None and until != None):
            since = json.dumps(since)
            until = json.dumps(until)
            filters =  "filters: {createdAt: {since: " + since +", until: " + until + "}}"
        else:
            filters = ''

        data = {"query": "{ getSummary( grouping:[ {by:project}, {by:category, fillGap: true} ] "+filters+" values:[count] ){ value(type: count) buckets{ key alias value(type:count) buckets{key alias value(type: count)} } }}"}

        response = requests.request("POST", url = url, json=data, headers={ 'Content-Type': 'application/json','Accept': 'application/json',})

        if(response.status_code == 200):
            return json.loads(response.text)
        else:
            return None
    
    def get_leads(self, accountId, invokerId, channel_id, since=None, until=None):
        url = self.base_url_report+"?account_id="+str(accountId)+"&invoker_id="+str(invokerId)

        if(since !=None and until != None):
            since = json.dumps(since)
            until = json.dumps(until)
            filters =  "filters: [{channelIds: "+ str(channel_id)+"}{createdAt: {since: " + since +", until: " + until + "}}]"   
        else:
            filters = "filters: {channelIds: "+ str(channel_id)+"}"

        data = {"query": "{getSummary( values: count grouping: [{ by: user }, { by: category, fillGap: true }] "+filters+") { buckets { key alias value(type: count) buckets {key value(type: count) }}}}"}
        response = requests.request("POST", url = url, json=data, headers={ 'Content-Type': 'application/json','Accept': 'application/json',})

        if(response.status_code == 200) :
            return json.loads(response.text)
        else:
            return None

    def get_summary_product(self, accountId, invokerId):
        url = self.base_url_product+"products/summary?account_id="+str(accountId)+"&invoker_id="+str(invokerId)

        response = requests.request("GET", url)
        if(response.status_code == 200):
            teams = json.loads(response.text)
            if(teams.get("projects") != []):
                return teams.get("projects")
        else:
            return None
    
    def summary_sales_name(self, accountId, invokerId, project_id, since, until):
        url = self.base_url_report+"?account_id="+str(accountId)+"&invoker_id="+str(invokerId)

        if(since !=None and until != None):
            since = json.dumps(since)
            until = json.dumps(until)
            filters =  "filters: [{projectIds: "+ str(project_id)+"}{createdAt: {since: " + since +", until: " + until + "}}]"   
        else:
            filters = "filters: {projectIds: "+ str(project_id)+"}"

        data = {"query": "{getSummary("+filters+", grouping: {by: user}, values: count){buckets{ key alias }}}"}
        response = requests.request("POST", url = url, json=data, headers={ 'Content-Type': 'application/json','Accept': 'application/json',})

        if(response.status_code == 200):
            teams = []
            res = json.loads(response.text)
            
            if(res['data']['getSummary']['buckets'] != None):
                for team in res['data']['getSummary']['buckets']:              
                    like = ({"id" : team.get("key"), "name" : team.get("alias")})
                    teams.append(like)
                
                return teams
            else :
                return []
        else:
            return []
    
    def summary_group_name(self, accountId, invokerId, project_id, since, until):
        url = self.base_url_report+"?account_id="+str(accountId)+"&invoker_id="+str(invokerId)

        if(since !=None and until != None):
            since = json.dumps(since)
            until = json.dumps(until)
            filters =  "filters: [{projectIds: "+ str(project_id)+"}{createdAt: {since: " + since +", until: " + until + "}}]"   
        else:
            filters = "filters: {projectIds: "+ str(project_id)+"}"

        data = {"query": "{getSummary("+filters+", grouping: {by: group}, values: count){buckets{ key alias }}}"}
        response = requests.request("POST", url = url, json=data, headers={ 'Content-Type': 'application/json','Accept': 'application/json',})

        if(response.status_code == 200):
            teams = []
            res = json.loads(response.text)
            if(res['data']['getSummary']['buckets'] != None):
                for team in res['data']['getSummary']['buckets']:              
                    like = ({"id" : team.get("key"), "name" : team.get("alias")})
                    teams.append(like)
                
                return teams
            else :
                return []
        else:
            return []
    
    def event_edit_project(self, accountId, projectId, projectName):
        url = self.base_url_bus+"events"

        data = {
            "activity": "project;project;edit",
            "metadata": {
                "microserviceId": "ms-project",
                "accountId": int(accountId)
            },
            "payload": [
                {
                    "accountId": int(accountId),
                    "id": int(projectId),
                    "name": str(projectName)
                }
            ]
        }
        response = requests.request("POST", url = url, json=data, headers={ 'Content-Type': 'application/json','Accept': 'application/json',})
        # print(response.text)

        if(response.status_code == 200):
  
            return 'success'
    
    def event_edit_campaign(self, accountId, campaignId, campaignName):
        url = self.base_url_bus+"events"

        data = {
            "activity": "project;campaign;edit",
            "metadata": {
                "microserviceId": "ms-project",
                "accountId": int(accountId)
            },
            "payload": [
                {
                    "accountId": int(accountId),
                    "id": int(campaignId),
                    "name": str(campaignName)
                }
            ]
        }
        response = requests.request("POST", url = url, json=data, headers={ 'Content-Type': 'application/json','Accept': 'application/json',})
        # print(response.text)

        if(response.status_code == 200):
  
            return 'success'
    
    def event_edit_channel(self, accountId, channelId, channelName, startTime, endTime, enableRedistribution, idleDuration, distributionType):
        url = self.base_url_bus+"events"

        data = {
            "activity": "project;channel;edit",
            "metadata": {
                "microserviceId": "ms-project",
                "accountId": int(accountId)
            },
            "payload": [
                {
                    "accountId": int(accountId),
                    "id": int(channelId),
                    "name": str(channelName),
                    "enableRedistribution": bool(enableRedistribution),
                    "distributionType": str(distributionType),
                    "startTime": str(startTime),
                    "endTime" : str(endTime),
                    "idleDuration": int(idleDuration),
                }
            ]
        }
        response = requests.request("POST", url = url, json=data, headers={ 'Content-Type': 'application/json','Accept': 'application/json',})
        # print(response.text)

        if(response.status_code == 200):
            return 'success'
    
    def get_user_by_account_id(self, account_id):
        url = self.base_url_core+"internal/accounts/"+str(account_id)+"/users?account_id="+str(account_id)
        response = requests.request("GET", url)
        if(response.status_code == 200):
            teams = json.loads(response.text)
           
            return teams
        else:
            return None
    
    def delete_user_by_account_id(self, account_id, data):
        url = self.base_url_core+"internal/accounts/"+str(account_id)+"/users?account_id="+str(account_id)

        response = requests.request("DELETE", url = url, json=data, headers={ 'Content-Type': 'application/json','Accept': 'application/json',})
        
        if(response.status_code == 200):
            teams = json.loads(response.text)
           
            return teams
        else:
            return None
    
    def get_settings_product(self, account):
        url = self.base_url_core+"settings/product_catalog?account_id="+str(account)

        response = requests.request("GET", url)
        if(response.status_code == 200):
            teams= json.loads(response.text)
            return teams
        else:
            return None
    
    def get_location(self, ):
        url = self.base_url_core+"internal/locations"

        response = requests.request("GET", url)
        if(response.status_code == 200):
            teams= json.loads(response.text)
            return teams
        else:
            return None
    
    def get_owner_id(self, account):
        url = self.base_url_core+"internal/accounts/"+str(account)+"/users?role=owner"
        response = requests.request("GET", url)

        if(response.status_code == 200):
            teams= json.loads(response.text)
            if(teams != []):
                return teams[0]['id']
        else:
            return None
    
    def update_validator(self, accountId, channelId):
        url = self.base_url_validator+"validation/3/channel?account_id="+str(accountId)

        data = [
            {
                "id": channelId
            }
        ]
        response = requests.request("POST", url = url, json=data, headers={ 'Content-Type': 'application/json','Accept': 'application/json',})
        # print(response.text)

        if(response.status_code == 200):
            return 'success'