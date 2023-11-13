from api_projects.views.internal_check import InternalCheckView
from django.http.response import HttpResponse, JsonResponse
from ..serializers import AllStatusSerializer, ChannelProjectSerializer, MinimalisCatSerializer, MinimalisSerializer, OldStatusCustomSerializer, ProjectDuplicateStatusProjectSerializer, ProjectSerializer, ProjectStatusCustomSerializer, ProjectStatusProjectSerializer, ProjectStatusSerializer, ProjectTeamSerializer, ProjectssSerializer
from ..models import Campaign, Category, Channel, ChannelSettingMember, CustomStatus, Project, ProjectDuplicateStatus, ProjectTeam, ProjectProduct, ProjectStatus, Status, UserDistribution
from rest_framework import mixins, generics
from django.db import transaction, IntegrityError
from ..utils import invalid_handler, succ_resp
from  ..services import BaseParameterMixin, ExternalService 
from django.db.models import CharField, Value

from django.utils.timezone import now
import requests
import os
import rest_framework
import json
from django.db.models import Q

class ProjectListCreateView(BaseParameterMixin,
                    mixins.ListModelMixin, 
                    mixins.CreateModelMixin,
                    generics.GenericAPIView):
    
    serializer_class = ProjectSerializer

    def external(self, accountId, invokerId, since, until):
        external_service = ExternalService()

        if(self.get_since() != None and self.get_until != None):
            param = external_service.get_summary_project(accountId=accountId, invokerId=invokerId, since=since, until = until)
        elif(self.get_since() != None and self.get_until == None):
            param = external_service.get_summary_project(accountId=accountId, invokerId=invokerId, since=since, until = since)
        else :
            param = external_service.get_summary_project(accountId=accountId, invokerId=invokerId)
        
        if(self.get_invoker_id() != None) :
            if(self.get_all() == 'true' or self.get_all() == True):             
                list = param
                if(list != None ):
                    if(list['data'] != None) :
                        return list['data']['getSummary']['buckets']
        return None
    
    def update_team(self, account_id, teams_api):
        team_to_delete = []
        team = []

        project_team = ProjectTeam.objects.filter(accountId=account_id)

        for c in teams_api:
            team.append(c["id"])

        for s in project_team:
            if(s.teamId not in team):
                team_to_delete.append(s.teamId)
        
        if(team_to_delete != []) :
            for id in team_to_delete:
                ProjectTeam.objects.filter(accountId = account_id, teamId=id).delete()

    def limit_query(self, request):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        since = self.get_since()
        until = self.get_until()
        withs = self.get_all()
        size = self.get_size()
        skip = self.get_skip()
        filter_date = self.filter_period()

        self.queryset = Project.objects.filter(accountId=account_id, **filter_date).order_by('-createdAt')[int(skip):int(size)]
        if (invoker_id != None):
            internal = InternalCheckView()
            ow = internal.api_user(account_id=account_id, user_id=invoker_id)
            if(ow["account"] == True) :
                if(ow["role"] == "owner") :
                    self.queryset = Project.objects.filter(accountId=account_id,**filter_date).order_by('-createdAt')[int(skip):int(size)]
                else:
                    check = internal.get(request= request)
                    res = json.loads(check.content)
                    self.queryset = Project.objects.filter(id__in = res['projects'], accountId=account_id, **filter_date).order_by('-createdAt')[int(skip):int(size)]
            else :
                self.queryset = Project.objects.filter(id__in = [], accountId=account_id,**filter_date).order_by('-createdAt')[int(skip):int(size)]

        return self.queryset

    def get(self, request):
        
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        since = self.get_since()
        until = self.get_until()
        withs = self.get_all()
        size = self.get_size()
        skip = self.get_skip()
        skip = int(skip) if skip else 0

        assistant = self.get_assistant()
        external_service = ExternalService()
        
        filter_assistant = {}
        if assistant == 'true':
            filter_assistant = {"status": "running"}

        # filter status
        filter_q = self.filter_status_running()
        filter_date = self.filter_period()
        filter_search = self.filter_search()

        self.queryset = Project.objects.filter(accountId=account_id, **filter_date, **filter_q, **filter_search, **filter_assistant).order_by('-createdAt')
        if (invoker_id != None):
            internal = InternalCheckView()
            ow = internal.api_user(account_id=account_id, user_id=invoker_id)
            if(ow["account"] == True) :
                if(ow["role"] == "owner") :
                    self.queryset = Project.objects.filter(accountId=account_id,**filter_date, **filter_q, **filter_search, **filter_assistant).order_by('-createdAt')
                else:
                    check = internal.get(request= request)
                    res = json.loads(check.content)
                    self.queryset = Project.objects.filter(id__in = res['projects'], accountId=account_id, **filter_date, **filter_q, **filter_search, **filter_assistant).order_by('-createdAt')
            else :
                self.queryset = Project.objects.filter(id__in = [], accountId=account_id,**filter_date, **filter_q, **filter_search,**filter_assistant).order_by('-createdAt')

        if size:
            size = int(size) 
            if size == 10:
                size = 200
            self.queryset = self.queryset[skip:skip+size]

        serializer = ProjectSerializer(self.queryset, many=True)
        js = self.external(account_id, invoker_id, since, until)

        team = None
        product = None
        if(self.get_all() == 'true'):
            product = external_service.get_summary_product(accountId=account_id, invokerId=invoker_id)
            team = external_service.get_team_by_ava(tenant_id=account_id, user_id=invoker_id)
        
        if(serializer.data != None):
                for p in serializer.data:
                    # update total
                    total_channel = 0
                    total_campaign = 0
                    total_group = 0
                    total_sales = 0
                    if(withs == 'true' or withs == True):
                        total_campaign = Campaign.objects.filter(project=p['id']).count()
                        total_group = ProjectTeam.objects.filter(project=p['id']).count()
                        campaigns = Campaign.objects.filter(project=p['id'])
                        total_channel = Channel.objects.filter(campaign__in= campaigns, accountId= account_id).count()
                        listchannel = Channel.objects.filter(campaign__in= campaigns, accountId= account_id).values_list('id', flat=True)
                        total_sales = ChannelSettingMember.objects.filter(channel__in=list(listchannel)).distinct('userId').count()

                     # update groups
                    array_team = []
                    if(team != None):
                        if(p['groups'] != []):
                            for t in p['groups']:
                                chann = next((x for x in team if x['id'] == t['id']), 0)
                                if(chann != 0):
                                    array_team.append(chann)
                    
                    # total product, iki kudu dirapikan
                    if(product != None):
                        chann = next((x for x in product if x['id'] == p['id']), 0)
                        if(chann != 0):
                            p.update({"totalProduct" : chann['totalProducts']})
                        else :
                            p.update({"totalProduct" : 0})
                    else :
                        p.update({"totalProduct" : 0})

                    p.update({"totalChannel" : total_channel, "totalCampaign": total_campaign, "totalGroup" : total_group, "totalSales": total_sales, "groups" : array_team})

                    if(js != None) :
                        chann = next((x for x in js if x['key'] == str(p['id'])), 0)
                        if(chann != 0):
                            p['totalLead'] = chann['value']
                            closing = next((x for x in chann['buckets'] if x['key'] == str(6)), 0)
                            if(closing != 0):
                                p['totalClosingLead'] = closing['value']
                            else :
                                p['totalClosingLead'] = 0
                        else:
                            p['totalLead'] = 0
                            p['totalClosingLead'] = 0
                    
        return succ_resp(data=serializer.data)

    def post(self, request, *args, **kwargs):
        error_message=None
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        cek_name = Project.objects.filter(accountId=account_id).values_list('name', flat=True)
        
        temp_data = request.data
        project_ids = []
        for temp in temp_data:
            body_name = temp.get("name")
            if(body_name.strip() in list(cek_name)):
                return HttpResponse(json.dumps(invalid_handler("Project Name Duplicate"), ensure_ascii=False), content_type="application/json", status=rest_framework.status.HTTP_400_BAD_REQUEST)
            
            #create project
            new_project = Project(
                name=temp.get("name"),
                detail = temp.get("detail"),
                periodStart = temp.get("periodStart"),
                periodEnd = temp.get("periodEnd"),
                duplicate_lead = temp.get("duplicate_lead"),
                accountId = account_id,
                createdBy = invoker_id
            )

            try:
                with transaction.atomic():
                    new_project.save()
                    project_ids.append(new_project.id)

                    #prepare filter valid team id and product id from API
                    external_service = ExternalService()
                    teams_api_list = external_service.get_team_by_tenant_id(tenant_id=account_id, user_id=invoker_id)
                    
                    valid_team_ids = []   
                    if(teams_api_list != []):  
                        for team in teams_api_list:
                            valid_team_ids.append(team['id'])

                    teams = temp.get("groups")
                    if(teams != None) :
                        for team in teams:
                            team_id = team["id"]
                            #check on API team if exist add if not do not add team
                            if (team_id in valid_team_ids):
                                new_projectteam = ProjectTeam(
                                    teamId = team_id,
                                    accountId = account_id,
                                    createdBy = invoker_id,
                                    project = new_project
                                )
                                new_projectteam.save()
                            else:
                                #throw invalid team return
                                error_message = "Team Not Found"
                                raise IntegrityError

                    statuses = temp.get("leadStatuses")
                    if(statuses != None) :
                    
                        for status in statuses:
                            point = status.get("point")
                            detail = status.get("detail")
                            category_id = status["category"]["id"]
                            category = Category.objects.filter(id = category_id).first()
                            color = Category.objects.filter(id = category_id).values('color')
                            if (category!=None):
                                name = status["name"]
                                new_projectstatus=ProjectStatus(
                                    point = point,
                                    name = name,
                                    detail = detail,
                                    category=category,
                                    accountId = account_id,
                                    createdBy = invoker_id,
                                    project = new_project,
                                    color = color
                                )
                                new_projectstatus.save()
                            else:
                                error_message = "Category Not Found"
                                raise IntegrityError
                    
                    status_duplicate = temp.get("leadStatuses_duplicate")
                    if(status_duplicate != None) :
                    
                        point = status_duplicate.get("point")
                        category_id = status_duplicate["category"]["id"]
                        category = Category.objects.filter(id = category_id).first()
                        color = Category.objects.filter(id = category_id).values('color')
                        if (category!=None):
                            names = status_duplicate["name"]
                            new_duplicate = ProjectDuplicateStatus(
                                point = point,
                                name = names,
                                category=category,
                                accountId = account_id,
                                createdBy = invoker_id,
                                project = new_project,
                                color = color
                            )
                            new_duplicate.save()

                        else:
                            error_message = "Category Not Found"
                            raise IntegrityError

            except IntegrityError:
                return HttpResponse(json.dumps(invalid_handler(error_message), ensure_ascii=False), content_type="application/json", status=rest_framework.status.HTTP_400_BAD_REQUEST)   
            else :
                products = temp.get("products")
                if(products != None):
                    proj_id = str(new_project.id)
                    product_id = products
                    base_url_product = os.environ.get('PRODUCT_API')
                    url = base_url_product+"projects/"+proj_id+"/products?account_id="+str(account_id)+"&invoker_id="+str(invoker_id)+"&replace=true"

                    if(product_id != None) : 
                        requests.request("POST", url = url, data=json.dumps(product_id), headers={ 'Content-Type': 'application/json','Accept': 'application/json',})
                        # print(requests.request("POST", url = url, data=json.dumps(product_id), headers={ 'Content-Type': 'application/json','Accept': 'application/json',}).status_code)
                        # print(json.loads(response.text))
                            
        self.queryset = Project.objects.filter(accountId=account_id, id__in=project_ids)
        return self.list(request)

class ProjectRetrieveUpdateDeleteView(BaseParameterMixin,
                    mixins.RetrieveModelMixin, 
                    mixins.UpdateModelMixin, 
                    mixins.DestroyModelMixin, 
                    generics.GenericAPIView):

    def get_queryset(self):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        queryset = Project.objects.filter(accountId=account_id)
        return queryset
    
    serializer_class = ProjectssSerializer

    def get(self, request, pk):
        return self.retrieve(request, pk)

    @transaction.atomic
    def put(self, request, pk):

        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        error_message=None
        external = ExternalService()
        cek_name = Project.objects.filter(accountId=account_id).exclude(id=pk).values_list('name', flat=True)
        
        temp = request.data
        name = temp.get("name")
        teams = temp.get("groups")
        products = temp.get("products")
        statuses = temp.get("leadStatuses")
        status_duplicate = temp.get("leadStatuses_duplicate")
        project = Project.objects.filter(id=pk).first()

        if (not project):
            #throw invalid project return
            return HttpResponse(json.dumps(invalid_handler("Project Not Found"), ensure_ascii=False), content_type="application/json")
        
        if(name != None):
            if(name.strip() in list(cek_name)):
                return HttpResponse(json.dumps(invalid_handler("Project Name Duplicate"), ensure_ascii=False), content_type="application/json", status=rest_framework.status.HTTP_400_BAD_REQUEST)

            # update ke event bus
            if(project.name != name):
                external.event_edit_project(accountId=account_id, projectId=pk, projectName=name)
        
        # cek status duplikat
        if(status_duplicate == None or status_duplicate == {}) :
            ProjectDuplicateStatus.objects.filter(project=pk).delete()  

        # ngiawur
        if(teams != None or products != None or statuses != None or status_duplicate != None or status_duplicate != {}) :
            # try:
                with transaction.atomic():

                    #valid team id check
                    #prepare filter valid team id and product id from API
                    external_service = ExternalService()
                    teams_api_list = external_service.get_team_by_tenant_id(tenant_id=account_id, user_id=invoker_id)
                    valid_team_ids = []
                    for team in teams_api_list:
                        valid_team_ids.append(team['id'])
                    
                    if (teams != None) :
                        project_teams =ProjectTeam.objects.filter(project = project)
                        #delete existing project team if not exist in teams parameter
                        for project_team in project_teams:
                            if (project_team.id not in teams):
                                project_team.delete()
                        #add new project teams if not exist in project teams
                        for team in teams:
                            team_id = team["id"]
                            if (team_id not in valid_team_ids):
                                error_message = "Group Not Found"
                                raise IntegrityError
                            #check if project team is exist
                            project_team =ProjectTeam.objects.filter(teamId=team_id, project = project).first()
                            if (project_team==None):
                                new_projectteam = ProjectTeam(
                                    teamId = team_id,
                                    accountId = account_id,
                                    createdBy = invoker_id,
                                    project = project
                                )
                                new_projectteam.save()
                                
                    if(statuses != None) :
                        project_statuses = ProjectStatus.objects.filter(project = project)
                        #delete existing project status if not exist in status parameter

                        statuses_to_create = []
                        status_now = []
                        status_to = []

                        # ambil status yg ada di db
                        for s in project_statuses:
                            status_to.append(s.name)
                        
                        # ambil status yang gaada di db
                        for c in statuses:
                            if(c['point'] != None):
                                ProjectStatus.objects.filter(project = project, name=c['name']).update(point=c['point'])
                            status_now.append(c["name"])
                            if(c["name"] not in status_to):
                                statuses_to_create.append(c)

                        # hapus status yg gaada di body
                        for project_status in project_statuses:
                            if (project_status.name not in status_now):
                                project_status.delete()

                        # create status baru
                        for status in statuses_to_create:
                            point = status.get("point")
                            sort = status.get("sort")
                            category_id = status["category"]["id"]
                            name = status["name"]
                            category = Category.objects.filter(id = category_id).first()
                            color = Category.objects.filter(id = category_id).values('color')
                            if (category!=None):
                                new_projectstatus=ProjectStatus(
                                    point = point,
                                    name = name,
                                    sort= sort,
                                    category=category,
                                    accountId = account_id,
                                    createdBy = invoker_id,
                                    project = project,
                                    color = color
                                )
                                new_projectstatus.save()
                            else:
                                #throw invalid category return
                                return HttpResponse(json.dumps(invalid_handler("Category Not Found"), ensure_ascii=False), content_type="application/json")

                    if (status_duplicate != None) :
                        if(status_duplicate != {}):
                            project_duplicatestatuses = ProjectDuplicateStatus.objects.filter(project = project)

                            # cek udah ada di db belum, kalo belum ada dibuatin dulu
                            cek = ProjectDuplicateStatus.objects.filter(project = project).values_list('name')
                            if not cek:                  
                                    points = status_duplicate.get("point")
                                    names = status_duplicate["name"]
                                    category_ids = status_duplicate["category"]["id"]
                                    categorys = Category.objects.filter(id = category_ids).first()
                                    colors = Category.objects.filter(id = category_ids).values('color')

                                    new_projectstatus_duplicate = ProjectDuplicateStatus(
                                        point = points,
                                        name = names,
                                        category=categorys,
                                        accountId = account_id,
                                        createdBy = invoker_id,
                                        project_id = pk,
                                        color = colors
                                    )
                                    new_projectstatus_duplicate.save()
                            
                            else :
                                # edit duplicate status di db 
                                project_duplicatestatuses.update(name = status_duplicate['name'], point = status_duplicate['point'], category = status_duplicate['category']['id'], modifiedAt=now())  

                    products = temp.get("products")
                    if(products != None):
                        proj_id = str(project.id)
                        product_id = products
                        base_url_product = os.environ.get('PRODUCT_API')
                        url = base_url_product+"projects/"+proj_id+"/products?account_id="+str(account_id)+"&invoker_id="+str(invoker_id)+"&replace=true"

                        if(product_id != None) : 
                            requests.request("POST", url = url, data=json.dumps(product_id), headers={ 'Content-Type': 'application/json','Accept': 'application/json',})
                            # print(requests.request("POST", url = url, data=json.dumps(product_id), headers={ 'Content-Type': 'application/json','Accept': 'application/json',}).status_code)
                            # print(json.loads(response.text))
                
            # except IntegrityError:
            #     return HttpResponse(json.dumps(invalid_handler(error_message), ensure_ascii=False), content_type="application/json", status=rest_framework.status.HTTP_400_BAD_REQUEST)
            
        return self.update(request, pk)

    def delete(self, request, pk):
        self.destroy(request, pk)
        response = "success delete id "+str(pk)
        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

# status retreive by project id
class ProjectStatusListView(BaseParameterMixin,
                    mixins.ListModelMixin,
                    generics.GenericAPIView):


    serializer_class = ProjectStatusProjectSerializer

    def get(self, request, pk):
        account_id = self.get_account_id()
        filter_assistant = self.filter_assistant()
        filter_search = self.filter_search()
        filter_category = self.filter_category()

        projects = Project.objects.filter(id = pk).first()
        self.queryset = ProjectStatus.objects.filter(filter_category, project = projects, accountId=account_id, **filter_search).order_by('createdAt')

        # buat filter di assistant
        if(filter_assistant == True) :
            self.queryset = ProjectStatus.objects.filter(filter_category, project = projects, accountId=account_id, **filter_search).exclude(Q(name__icontains="book") | Q(name__icontains="pesan") | Q(name__icontains="clos") | Q(name__icontains="sold")).order_by('createdAt')

        return self.list(request, pk)
    
    @transaction.atomic
    def post(self, request, pk):
        error_message=None
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        project = Project.objects.filter(id = pk).first()
        if (not project):
            return HttpResponse(json.dumps(invalid_handler("Project Not Found"), ensure_ascii=False), content_type="application/json", status=rest_framework.status.HTTP_400_BAD_REQUEST)
        #TODO add parareter for payload if available

        temp_data = request.data
        with transaction.atomic():
            for temp in temp_data :
                point = temp.get("point")
                category = temp.get("category")
                name = temp.get("name")
                detail = temp.get("detail")
                color = Category.objects.filter(id = category['id']).values('color')
                new_userproject = ProjectStatus(
                    accountId = account_id,
                    createdBy = invoker_id,
                    point = point,
                    category_id = category['id'],
                    name = name,
                    detail = detail,
                    color = color,
                    project= project
                )
                new_userproject.save()
        projects = Project.objects.filter(id = pk)
        self.queryset = ProjectStatus.objects.filter(project__in = projects, accountId=account_id)
        # if (invoker_id!=None):
        #     self.queryset = UserProject.objects.filter(project__in = projects, accountId=account_id, userId=invoker_id)
        return self.list(request, pk)

class ProjectDuplicateStatusListView(BaseParameterMixin,
                    mixins.ListModelMixin,
                    generics.GenericAPIView):


    serializer_class = ProjectDuplicateStatusProjectSerializer

    def get(self, request, pk):
        account_id = self.get_account_id()
        projects = Project.objects.filter(id = pk).first()
        cek = ProjectDuplicateStatus.objects.filter(project = projects, accountId=account_id).count()
        duplicate_status = ProjectDuplicateStatus.objects.filter(project = projects, accountId=account_id)

        self.queryset = ProjectStatus.objects.none()

        if(cek > 0) :
            for a in duplicate_status:
                self.queryset = ProjectStatus.objects.filter(project = projects, accountId=account_id, name = a.name)

        return self.list(request, pk)
 
# custom status yang lama
class OldCustomStatus():

    serializer_class = OldStatusCustomSerializer

    def get(self, account_id):     
        stat = Status.objects.values('name')
        status = ProjectStatus.objects.filter(accountId=account_id).exclude(name__in = stat).distinct('name')
        res = OldStatusCustomSerializer(status, many=True).data

        return JsonResponse(res, safe=False)

# custom status
class ProjectMetadataView(BaseParameterMixin, mixins.ListModelMixin, generics.GenericAPIView):
    
    serializer_class = ProjectStatusCustomSerializer

    def get(self, request):
        account_id = self.get_account_id()

        old = OldCustomStatus().get(account_id= account_id)
        json_status = json.loads(old.content)
        self.queryset = CustomStatus.objects.filter(accountId=account_id)

        # if(json_status != None) :
        #     self.queryset = list(chain(self.queryset, json_status))

        return self.list(request)
    
    @transaction.atomic
    def post(self, request):
        error_message=None
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()

        # list status buat validasi duplikat name e
        master_status = Status.objects.all().values_list('name', flat=True)
        cust_status = CustomStatus.objects.filter(accountId=account_id).values_list('name', flat=True)
        list_status = list(master_status) + list(cust_status)

        temp_data = request.data
        with transaction.atomic():
            
            for temp in temp_data :
                point = temp.get("point")
                category = temp.get("category")
                name = temp.get("name")
                detail = temp.get("detail")
                color = Category.objects.filter(id = category['id']).values('color')

                if (name.strip() in list_status):
                    return HttpResponse(json.dumps(invalid_handler("Status Name Duplicate"), ensure_ascii=False), content_type="application/json", status=rest_framework.status.HTTP_400_BAD_REQUEST)
                
                new_userproject = CustomStatus(
                    accountId = account_id,
                    createdBy = invoker_id,
                    point = point,
                    category_id = category['id'],
                    name = name,
                    detail = detail,
                    color = color,
                )
                new_userproject.save()
        self.queryset = CustomStatus.objects.filter(accountId=account_id)
       
        return self.list(request)

# project channel
class ProjectChannelListCreateView(BaseParameterMixin,
                    mixins.ListModelMixin,
                    generics.GenericAPIView):
     
    serializer_class = ChannelProjectSerializer

    def external(self, accountId, invokerId, since, until):
        external_service = ExternalService()
        if(self.get_since() != None and self.get_until!=None):
            param = external_service.get_summary_channel(accountId=accountId, invokerId=invokerId, since=since, until = until)
        else :
            param = external_service.get_summary_channel(accountId=accountId, invokerId=invokerId)

        if(self.get_invoker_id() != None) :
            if(self.get_additional() == None):
                
                list = param
                if(list != None ):
                    if(list['data'] != None) :
                        return list['data']['getSummary']['buckets']
        return None

    def get(self, request, pk):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        since= self.get_since()
        until = self.get_until()
        isOffline = self.request.GET.get('isOffline')
        assistant = self.get_assistant()
        projects = Project.objects.filter(id = pk)
        campaigns = Campaign.objects.filter(project__in=projects)
        size = self.get_size()
        skip = self.get_skip()
        skip = int(skip) if skip else 0

        filter_assistant = {}
        exclude_condition = {}
        if assistant == 'true':
            filter_assistant = {"status": "running"}
            if account_id == '2891' :
                lis = UserDistribution.objects.filter(distribution='channel_exclude').values_list('city', flat=True)[0]
                list_ch = [item.strip() for item in lis.split(',')]
                exclude_condition = {"name__in":list_ch}

        filters = {"campaign__in" : campaigns, "accountId":account_id}
        if (isOffline == 'true' and account_id != 142):
            filters = {"campaign__in" : campaigns, "accountId":account_id, "media__type": "offline"}
        
        self.queryset = Channel.objects.filter(**filters, **filter_assistant).exclude(**exclude_condition).order_by('-createdAt')

        if (invoker_id != None):
            internal = InternalCheckView()
            ow = internal.api_user(account_id=account_id, user_id=invoker_id)
            if(ow["account"] == True) :
                if(ow["role"] == "owner") :
                    self.queryset = Channel.objects.filter(**filters,**filter_assistant).exclude(**exclude_condition).order_by('-createdAt')
                else:
                    check = internal.get(request= request)
                    res = json.loads(check.content)
                    self.queryset = Channel.objects.filter(id__in = res['channels'], **filters,**filter_assistant).exclude(**exclude_condition).order_by('-createdAt')
            else :
                self.queryset = Channel.objects.filter(id__in = [], **filters, **filter_assistant).exclude(**exclude_condition).order_by('-createdAt')
        
        if size:
            size = int(size) 
            if assistant == 'true':
                size = 200
            self.queryset = self.queryset[skip:skip+size]

        serializer = ChannelProjectSerializer(self.queryset, context={'request': request}, many=True)
        js = ProjectChannelListCreateView.external(self, account_id, invoker_id, since=since, until=until)
        
        if(serializer.data != None):
                for p in serializer.data:
                    # total sales
                    totalSales = ChannelSettingMember.objects.filter(accountId=account_id, channel=p['id']).count()
                    p.update({'totalSales' : totalSales})
                    
                    if(js != None) :
                        chann = next((x for x in js if x['key'] == str(p['id'])), 0)
                        if(chann != 0):
                            p['totalLead'] = chann['value']
                            p['leadRate'] = p['totalLead'] / p['click'] if p['click'] else 0

                        else:
                            p['totalLead'] = 0
            
        return succ_resp(data=serializer.data)
 
# minimalis
class MinimalisView(BaseParameterMixin,
                    mixins.ListModelMixin, 
                    mixins.CreateModelMixin,
                    generics.GenericAPIView):
    serializer_class = MinimalisSerializer

    def get(self, request):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        project_id = self.get_project_param()

        # filter by project
        filters = {"accountId": account_id}
        if (project_id != None):
            filters = {"id": project_id, "accountId":account_id}

        self.queryset = Project.objects.filter(**filters)

        if (invoker_id != None):
            internal = InternalCheckView()
            ow = internal.api_user(account_id=account_id, user_id=invoker_id)
            if(ow["account"] == True) :
                if(ow["role"] == "owner") :
                    self.queryset = Project.objects.filter(**filters)
                else:
                    check = internal.get(request= request)
                    res = json.loads(check.content)
                    self.queryset = Project.objects.filter(id__in = res['projects'], **filters)
            else :
                self.queryset = Project.objects.filter(id__in = [],**filters)

        return self.list(request)

class MinimalisCatView(BaseParameterMixin,
                    mixins.ListModelMixin, 
                    mixins.CreateModelMixin,
                    generics.GenericAPIView):

    serializer_class = MinimalisCatSerializer

    def get(self, request):
        self.queryset = Category.objects.all()
       
        return self.list(request)

class AllStatusListCreateView(BaseParameterMixin, mixins.ListModelMixin,
                    mixins.CreateModelMixin, 
                    generics.GenericAPIView):
    
    queryset = ProjectStatus.objects.all()
    serializer_class = AllStatusSerializer

    def get(self, request):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        self.queryset = ProjectStatus.objects.filter(accountId=account_id).distinct('name')
        if (invoker_id != None):
            internal = InternalCheckView()
            ow = internal.api_user(account_id=account_id, user_id=invoker_id)
            if(ow["account"] == True) :
                if(ow["role"] == "owner") :
                    self.queryset = ProjectStatus.objects.filter(accountId=account_id).distinct('name')
                else:
                    check = internal.get(request= request)
                    res = json.loads(check.content)
                    self.queryset = ProjectStatus.objects.filter(project__in = res['projects'], accountId=account_id).distinct('name')
            else :
                self.queryset = ProjectStatus.objects.filter(project__in = [], accountId=account_id).distinct('name')
        
        serializer = AllStatusSerializer(self.queryset, many=True)

        return succ_resp(data=serializer.data)