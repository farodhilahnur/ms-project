import json
from django.http.response import HttpResponse

from api_projects.utils import succ_resp
from ..serializers import OngoingProjectSerializer, ProjectGroupSerializer, ProjectSerializer, ProjectTeamSerializer
from ..models import Project, ProjectTeam
from rest_framework import mixins, generics
from  ..services import BaseParameterMixin, ExternalService 
from api_projects.views.internal_check import InternalCheckView

# project team retreive by project id
class ProjectGroupListView(BaseParameterMixin, 
                    generics.GenericAPIView):

    serializer_class = ProjectTeamSerializer
    
    def get(self, request, pk):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        since = self.get_since()
        until = self.get_until()
        
        project = Project.objects.filter(id=pk).first()
        project_teams = ProjectTeam.objects.filter(project = project, accountId=account_id)
        external_service = ExternalService()
        team = external_service.get_teams(tenant_id=account_id)

        response = []
        for project_team in project_teams:
            chann = next((x for x in team if x['id'] == project_team.teamId), 0)

            if(chann != 0):
                response.append(chann)
                
        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")


# project retreive by group id
class GroupProjectListView(BaseParameterMixin, mixins.ListModelMixin, generics.GenericAPIView):
    
    serializer_class = ProjectGroupSerializer

    def external(self, accountId, invokerId, since, until):
        external_service = ExternalService()
        if(self.get_since() != None and self.get_until!=None):
            param = external_service.get_closing_leads(accountId=accountId, invokerId=invokerId, since=since, until = until)
        else :
            param = external_service.get_closing_leads(accountId=accountId, invokerId=invokerId)

        if(self.get_invoker_id() != None) :
            if(self.get_additional() == None):
                list = param
                if(list != None ):
                    if(list['data'] != None) :
                        return list['data']['getSummary']

        return None

    def get(self, request, pk):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        since= self.get_since()
        until = self.get_until()
        
        query_project = ProjectTeam.objects.filter(teamId = 0, accountId=account_id)

        if (invoker_id != None):
            internal = InternalCheckView()
            ow = internal.api_user(account_id=account_id, user_id=invoker_id)
            if(ow["account"] == True) :
                if(ow["role"] == "owner") :
                    query_project = ProjectTeam.objects.filter(teamId = pk, accountId=account_id)
                else:
                    check = internal.api_groups(account_id=account_id, user_id=invoker_id)
                    if(check.get('groups') != None ):
                        if(pk in check["groups"]):
                            query_project = ProjectTeam.objects.filter(teamId = pk, accountId=account_id)
                        else :
                            query_project = ProjectTeam.objects.filter(teamId = 0, accountId=account_id)
            else :
                query_project = ProjectTeam.objects.filter(teamId = 0, accountId=account_id)
        else :
            query_project = ProjectTeam.objects.filter(teamId = pk, accountId=account_id)
       
        project_id = list(query_project.values_list('project', flat= True))
        self.queryset = Project.objects.filter(id__in = project_id, accountId=account_id)
        
        serializer = ProjectGroupSerializer(self.queryset, many=True)
        js = self.external(account_id, invoker_id, since=since, until=until)

        if(serializer.data != None):
            if(js != None) :
                for p in serializer.data:
                    if(js['buckets'] != None) :
                        chann = next((x for x in js['buckets'] if x['key'] == str(p['id'])), 0)

                        if(chann != 0):
                            # total lead project
                            p['totalLead'] = chann['value']

                            # total closing lead project
                            closing = next((x for x in chann['buckets'] if x['key'] == str(6)), 0)
                            if(closing != 0):
                                p['totalClosingLead'] = closing['value']
                            else :
                                p['totalClosingLead'] = 0
                        else:
                            p['totalLead'] = 0
            
        return succ_resp(data=serializer.data)

# sales retrive by project ruwett
class ProjectSalesListView(BaseParameterMixin, mixins.ListModelMixin, generics.GenericAPIView):
    
    serializer_class = ProjectTeamSerializer
    
    def get(self, request, pk):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        since = self.get_since()
        until = self.get_until()
        
        project = Project.objects.filter(id=pk).first()
        project_teams = ProjectTeam.objects.filter(project = project, accountId=account_id)


        external_service = ExternalService()
        sales = external_service.summary_sales_name(accountId=account_id, invokerId=invoker_id, project_id=pk, since=since, until=until)

        return HttpResponse(json.dumps(sales, ensure_ascii=False), content_type="application/json")

# ongoing project by account
class OngoingProjectListView(BaseParameterMixin, mixins.ListModelMixin, generics.GenericAPIView):
    
    serializer_class = OngoingProjectSerializer

    def external(self, accountId, invokerId, since, until):
        external_service = ExternalService()
        if(self.get_since() != None and self.get_until!=None):
            param = external_service.get_closing_leads(accountId=accountId, invokerId=invokerId, since=since, until = until)
        else :
            param = external_service.get_closing_leads(accountId=accountId, invokerId=invokerId)

        if(self.get_invoker_id() != None) :
            if(self.get_additional() == None):
                external_service = ExternalService()
                list = param
                if(list != None ):
                    if(list['data'] != None) :
                        return list['data']['getSummary']

        return None

    def get(self, request):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        since= self.get_since()
        until = self.get_until()
        self.queryset = Project.objects.filter(accountId=account_id).order_by('-createdAt')[0:5]

        if (invoker_id != None):
            internal = InternalCheckView()
            ow = internal.api_user(account_id=account_id, user_id=invoker_id)
            if(ow["account"] == True) :
                if(ow["role"] == "owner") :
                    self.queryset = Project.objects.filter(accountId=account_id).order_by('-createdAt')[0:5]
                else:
                    check = internal.get(request= request)
                    res = json.loads(check.content)
                    self.queryset = Project.objects.filter(id__in = res['projects'], accountId=account_id).order_by('-createdAt')[0:5]
            else :
                self.queryset = Project.objects.filter(id__in = [], accountId=account_id).order_by('-createdAt')[0:5]

        serializer = OngoingProjectSerializer(self.queryset, many=True)
        js = self.external(account_id, invoker_id, since=since, until=until)

        if(serializer.data != None):
            if(js != None) :
                for p in serializer.data:
                    if(js['buckets'] != None) :
                        chann = next((x for x in js['buckets'] if x['key'] == str(p['id'])), 0)

                        if(chann != 0):
                            # total lead project
                            p['totalLead'] = chann['value']

                            # total closing lead project
                            closing = next((x for x in chann['buckets'] if x['key'] == str(6)), 0)
                            if(closing != 0):
                                p['totalClosingLead'] = closing['value']
                            else :
                                p['totalClosingLead'] = 0
                        else:
                            p['totalLead'] = 0
            
        return succ_resp(data=serializer.data)
