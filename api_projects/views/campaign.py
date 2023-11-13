from api_projects.views.internal_check import InternalCheckView
from ..services import ExternalService, BaseParameterMixin
from django.http.response import HttpResponse
from ..serializers import  CampaignByProjectSerializer, CampaignProjectSerializer, CampaignSerializer, CampaignSingleSerializer
from ..models import Campaign, Channel, Project
from rest_framework import mixins, generics
import rest_framework
import json
from django.db import transaction, IntegrityError
from ..utils import invalid_handler, succ_resp

class CampaignListCreateView(BaseParameterMixin,
                    mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    generics.GenericAPIView):
    
    serializer_class = CampaignSerializer

    def external(self, accountId, invokerId, since, until):
        external_service = ExternalService()

        if(self.get_invoker_id() != None) :
            if(self.get_all() == 'true'):
                if(self.get_since() != None and self.get_until!=None):
                    param = external_service.get_summary_campaign(accountId=accountId, invokerId=invokerId, since=since, until = until)
                else :
                    param = external_service.get_summary_campaign(accountId=accountId, invokerId=invokerId)

                list = param
                if(list != None ):
                    if(list['data'] != None) :
                        return list['data']['getSummary']['buckets']
            
        return None
    
    def get(self, request):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        since= self.get_since()
        until = self.get_until()
        assistant = self.get_assistant()
        fields_limit = self.get_fields()
        all_campaign = self.get_all_campaign()
        project = self.filter_project_id()

        # paging
        size = self.get_size()
        skip = self.get_skip()
        skip = int(skip) if skip else 0
        
        filter_assistant = {}
        if assistant == 'true':
            filter_assistant = {"status": "running"}
        # filter status
        filter_q = self.filter_status_running()
        filter_date = self.filter_period()
        filter_search = self.filter_search()

        self.queryset = Campaign.objects.filter(accountId=account_id, **filter_q, **filter_date, **filter_search, **filter_assistant, **project).order_by('-createdAt')
        if all_campaign == None:
            if (invoker_id != None):
                internal = InternalCheckView()
                ow = internal.api_user(account_id=account_id, user_id=invoker_id)
                if(ow["account"] == True) :
                    if(ow["role"] == "owner") :
                        self.queryset = Campaign.objects.filter(accountId=account_id, **filter_q, **filter_date, **filter_search, **filter_assistant, **project).order_by('-createdAt')
                    else:
                        check = internal.get(request= request)
                        res = json.loads(check.content)
                        # print(res['campaigns'])
                        self.queryset = Campaign.objects.filter(id__in = res['campaigns'], accountId=account_id, **filter_q, **filter_date, **filter_search, **filter_assistant, **project).order_by('-createdAt')
                else :
                    self.queryset = Campaign.objects.filter(id__in = [], accountId=account_id, **filter_q, **filter_date, **filter_search, **project)
        elif all_campaign == 'true':
            self.queryset = Campaign.objects.filter(accountId=account_id, **filter_q, **filter_date, **filter_search, **filter_assistant, **project).order_by('-createdAt')

        if size:
            size = int(size) 
            if size == 10:
                size = 200
                if account_id == '2891' :
                    size = 50
            self.queryset = self.queryset[skip:skip+size]

        serializer = CampaignSerializer(self.queryset, context={'request': request}, many=True)
        js = self.external(account_id, invoker_id, since, until)

        if(serializer.data != []):
                for p in serializer.data:
                    if fields_limit == None:
                        idsproject = Project.objects.get(id=p['project'])
                        p['project'] = {
                            "id": idsproject.id,
                            "name": idsproject.name
                        }
                    else :
                        if 'project' in fields_limit if fields_limit else None:
                            idsproject = Project.objects.get(id=p['project'])
                            p['project'] = {
                                "id": idsproject.id,
                                "name": idsproject.name
                            }
                    if(js != None) :
                        chann = next((x for x in js if x['key'] == str(p['id'])), 0)
                        if(chann != 0):
                            p['totalLead'] = chann['value']
                        else:
                            p['totalLead'] = 0

                        totalChannel = 0
                        if not assistant == 'true' :
                            totalChannel = Channel.objects.filter(campaign=p['id']).count()
                        p.update({'totalChannel': totalChannel})
            
        return succ_resp(data=serializer.data)
    
    @transaction.atomic
    def post(self, request):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()

        temp_data = request.data
        for temp in temp_data:
            if(temp.get("project") == None):
                return HttpResponse(json.dumps(invalid_handler("Project Cannot be null"), ensure_ascii=False), content_type="application/json", status=rest_framework.status.HTTP_400_BAD_REQUEST)
            project = temp["project"]["id"]
            
            # cek duplikat name
            cek_name = Campaign.objects.filter(accountId=account_id, project=project).values_list('name', flat=True)
            body_name = temp.get("name")
            if(body_name.strip() in list(cek_name)):
                return HttpResponse(json.dumps(invalid_handler("Campaign Name Duplicate"), ensure_ascii=False), content_type="application/json", status=rest_framework.status.HTTP_400_BAD_REQUEST)

            new_campaign = Campaign(
                name = temp.get("name"),
                detail = temp.get("detail"),
                periodStart = temp.get("periodStart"),
                periodEnd = temp.get("periodEnd"),
                accountId = account_id,
                createdBy = invoker_id,
                picture = temp.get("picture"),
                project_id= project
            )
            new_campaign.save()
        self.queryset = Campaign.objects.filter(accountId=account_id)
        
        return self.list(request)

class CampaignRetrieveUpdateDeleteView(BaseParameterMixin,
                    mixins.RetrieveModelMixin, 
                    mixins.UpdateModelMixin, 
                    mixins.DestroyModelMixin, 
                    generics.GenericAPIView):

    def get_queryset(self):
        account_id = self.get_account_id()
        
        queryset = Campaign.objects.filter(accountId=account_id)
        return queryset
    
    serializer_class = CampaignSingleSerializer

    def get(self, request, pk):
        return self.retrieve(request, pk)

    def put(self, request, pk):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        external = ExternalService()

        # cek duplikat name
        camp = Campaign.objects.filter(accountId=account_id, id=pk).values_list('project', flat=True)
        cek_name = Campaign.objects.filter(accountId=account_id, project=list(camp)[0]).exclude(id=pk).values_list('name', flat=True)
        body_name = request.data.get("name")
        if(body_name.strip() in list(cek_name)):
            return HttpResponse(json.dumps(invalid_handler("Campaign Name Duplicate"), ensure_ascii=False), content_type="application/json", status=rest_framework.status.HTTP_400_BAD_REQUEST)
            
        # update ke event bus
        campaign = Campaign.objects.get(id = pk, accountId=account_id)
        name = request.data.get("name")
        if(campaign.name != name):
            external.event_edit_campaign(accountId=account_id, campaignId=pk, campaignName=name)

        return self.update(request, pk)
    
    def delete(self, request, pk):
        self.destroy(request, pk)
        response = "success delete id "+str(pk)
        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

# campaign retreive by project id
# campaign create by project id
class ProjectCampaignListCreateView(BaseParameterMixin,
                    mixins.ListModelMixin,
                    generics.GenericAPIView):
    
    serializer_class = CampaignProjectSerializer

    def get(self, request, pk):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        since= self.get_since()
        until = self.get_until()
        projects = Project.objects.filter(id = pk)
        assistant = self.get_assistant()
        
        # paging
        size = self.get_size()
        skip = self.get_skip()

        skip = int(skip) if skip else 0

        filter_assistant = {}
        if assistant == 'true':
            filter_assistant = {"status": "running"}
            
        # filter status
        filter_q = self.filter_status_running()
        filter_date = self.filter_period()
        filter_search = self.filter_search()

        self.queryset = Campaign.objects.filter(project__in = projects, accountId=account_id, **filter_q, **filter_date, **filter_search, **filter_assistant).order_by('-periodStart')
        if (invoker_id != None):
            internal = InternalCheckView()
            ow = internal.api_user(account_id=account_id, user_id=invoker_id)
            if(ow["account"] == True) :
                if(ow["role"] == "owner") :
                    self.queryset = Campaign.objects.filter(project__in = projects, accountId=account_id, **filter_q, **filter_date, **filter_search, **filter_assistant).order_by('-periodStart')
                else:
                    check = internal.get(request= request)
                    res = json.loads(check.content)
                    self.queryset = Campaign.objects.filter(id__in = res['campaigns'], project__in = projects, accountId=account_id, **filter_q, **filter_date, **filter_search, **filter_assistant).order_by('-periodStart')
            else :
                self.queryset = Campaign.objects.filter(id__in = [],project__in = projects, accountId=account_id, **filter_q, **filter_date, **filter_search, **filter_assistant).order_by('-periodStart')
        
        if size:
            size = int(size) 
            if assistant == 'true':
                size = 200
            self.queryset = self.queryset[skip:skip+size]
        print(skip)
        serializer = CampaignByProjectSerializer(self.queryset, many=True)
        js = CampaignListCreateView.external(self, account_id, invoker_id, since=since, until=until)

        if(serializer.data != []):
            projectids = Project.objects.filter(id=serializer.data[0]['project']).values_list('name', flat=True)
            pname = str(projectids[0])
            for p in serializer.data:
                p.update({'project': {
                    'id': pk,
                    'name' : pname
                }})
                if(js != None) :
                    totalchannel = Channel.objects.filter(campaign=p['id']).count()
                    p['totalChannel'] = totalchannel
                    chann = next((x for x in js if x['key'] == str(p['id'])), 0)
                    if(chann != 0):
                        p['totalLead'] = chann['value']
                    else:
                        p['totalLead'] = 0
            
        return succ_resp(data=serializer.data)
    
    @transaction.atomic
    def post(self, request, pk):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        project = Project.objects.filter(id = pk).first()
        if (not project):
            return HttpResponse(json.dumps(invalid_handler("Project Not Found"), ensure_ascii=False), content_type="application/json", status=rest_framework.status.HTTP_400_BAD_REQUEST)
        temp_data = request.data
        campaign_ids = []
        for temp in temp_data:

            # cek duplikat name
            cek_name = Campaign.objects.filter(accountId=account_id, project=pk).values_list('name', flat=True)
            body_name = temp.get("name")
            if(body_name.strip() in list(cek_name)):
                return HttpResponse(json.dumps(invalid_handler("Campaign Name Duplicate"), ensure_ascii=False), content_type="application/json", status=rest_framework.status.HTTP_400_BAD_REQUEST)

            new_campaign = Campaign(
                name = temp.get("name"),
                detail = temp.get("detail"),
                periodStart = temp.get("periodStart"),
                periodEnd = temp.get("periodEnd"),
                accountId = account_id,
                createdBy = invoker_id,
                picture = temp.get("picture"),
                project= project
            )
            new_campaign.save()
            campaign_ids.append(new_campaign.id)
        projects = Project.objects.filter(id = pk)
        self.queryset = Campaign.objects.filter(project__in = projects, accountId=account_id, id__in=campaign_ids)
        
        return self.list(request, pk)

