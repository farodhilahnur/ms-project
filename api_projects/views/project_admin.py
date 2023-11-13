from api_projects.views.internal_check import InternalCheckView
from django.http.response import HttpResponse
from ..serializers import ProjectAdminListSerializer, ProjectAdminSerializer
from ..models import ProjectAdmin, Project
from rest_framework import mixins, generics, exceptions
from django.db import transaction, IntegrityError
from ..utils import invalid_handler, succ_resp, not_found_exception_handler
from  ..services import BaseParameterMixin, ExternalService 
from django.db.models import Q
from django.http import Http404

from django.utils.timezone import now
import requests
import os
import rest_framework
import json

class ProjectAdminListCreateView(BaseParameterMixin, mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    
    serializer_class = ProjectAdminSerializer

    def get(self, request, pk):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        since = self.get_since()
        until = self.get_until()

        self.queryset = ProjectAdmin.objects.filter(project = pk, accountId=account_id).distinct('email')
        serializer = ProjectAdminSerializer(self.queryset, many=True)

        external_service = ExternalService()
        campaign = external_service.get_user_by_account_id(account_id=account_id)

        for pv in serializer.data:
            total = ProjectAdmin.objects.filter(accountId=account_id, userId=pv['userId']).count()
            createby = next((x for x in campaign if x['id'] == pv['createdBy']), 0)
            # update name create by 
            if( createby != 0) :
                if (createby['role'] == "owner") :
                    names = "Owner (" + (createby['name'] + ")") if createby['name'] else "Owner ()"
                elif(createby['role'] == "admin") :
                    names =  "Admin (" + (createby['name'] + ")") if createby['name'] else "Admin ()"
                else :
                    names =  "Spv (" + (createby['name'] + ")") if createby['name'] else "Spv ()"
                pv.update({'created_by' : names})

            # update info user
            chann = next((x for x in campaign if x['id'] == pv['userId']), 0)
            if( chann != 0) :
                pv.update({'name' : chann['name'], 'email' : chann['email'], 'phone' : chann['phone'], 'picture' : chann['picture'], 'createdAt': chann['createdAt'], 'totalProject' : total}) 
        serializer_data = sorted(
            serializer.data, key=lambda k: k['createdAt'], reverse=True)                 
        return succ_resp(data=serializer_data)

    def post(self, request, pk, *args, **kwargs):
        error_message='Invite failed / user already exists'
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        existing = self.get_existing()
        temp_data = request.data

        base_url_core = os.environ.get('CORE_API_URL')
        url = base_url_core+"internal/accounts/"+account_id+"/invites"
        existadmin = ProjectAdmin.objects.filter(accountId = account_id).values_list('email', flat=True).distinct('email')
        # external
        # getuserId = ExternalService().get_user_by_account_id(account_id=account_id)
        self.queryset = ProjectAdmin.objects.filter(accountId=account_id, project=pk)

        admin = {'role' : 'admin'}
        listbody = []

        if existing == 'true' :
            for temp in temp_data:
                userid = ProjectAdmin.objects.filter(accountId = account_id, email=temp['email']).values_list('userId', flat=True)
                mask = ProjectAdmin.objects.filter(accountId = account_id, email=temp['email']).values_list('mask_phone', flat=True).first()
                ress = list(self.queryset.values())
                status_code = 200
                try:
                    if ProjectAdmin.objects.filter(accountId = account_id, email=temp['email'], project=pk).count() < 1 == True :
                        new_project_admin = ProjectAdmin(
                            project_id=pk,
                            userId=userid[0],
                            email=temp['email'],
                            accountId = account_id,
                            createdBy = invoker_id,
                            mask_phone = mask
                        )
                        new_project_admin.save()
                    else : 
                        ress = list(self.queryset.values())
                        status_code = 200
                except :
                    ress = {'message' : 'User not invited'}
                    status_code = 422

        else :
            for temp in temp_data:
                body = {}
                body.update(admin)
                body.update(temp) 
                listbody.append(body)
            
            responsee = requests.request("POST", url = url, data=json.dumps(listbody), headers={ 'Content-Type': 'application/json','Accept': 'application/json',})
            if(responsee.status_code == 200):
                ress = json.loads(responsee.text)
                status_code = 200
                    #create project admin
                for r in ress:
                    new_project_admin = ProjectAdmin(
                        project_id=pk,
                        userId=r['id'],
                        email=r['email'],
                        accountId = account_id,
                        createdBy = invoker_id
                    )
                    new_project_admin.save()     

            else : 
                ress = json.loads(responsee.text)
                status_code = responsee.status_code

        return succ_resp(data=ress, status=status_code)

class ProjectAdminRetrieveUpdateDeleteView(BaseParameterMixin,
                    mixins.RetrieveModelMixin, 
                    mixins.UpdateModelMixin, 
                    mixins.DestroyModelMixin, 
                    generics.GenericAPIView):

    def get_queryset(self):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        queryset = ProjectAdmin.objects.filter(accountId=account_id)
        return queryset
    
    serializer_class = ProjectAdminSerializer

    def get(self, request, pk):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        queryset = ProjectAdmin.objects.filter(userId = pk).first()
        serializer = ProjectAdminSerializer(queryset, many=False)

        return succ_resp(data=serializer.data)

    def put(self, request, pk):
        account_id = self.get_account_id()
        temp = request.data

        status = temp.get("status")
        projects = temp.get("projects")
        mask = temp.get("mask_phone")
        queryset = ProjectAdmin.objects.filter(userId = pk).order_by('-id').first()

        if(projects != None) :
            projectsdb = ProjectAdmin.objects.filter(userId = pk)
            #delete existing project  if not exist in project parameter

            project_to_create = []
            project_now = []
            project_to = []

            # ambil project yg ada di db
            for s in projectsdb:
                project_to.append(s.id)
            
            # ambil status yang gaada di db
            for c in projects:
                if(c["id"] not in project_to):
                    project_to_create.append(c)

            # create project admin baru
            userid = ProjectAdmin.objects.filter(userId = pk).values()
            for pr in project_to_create:
                idproject = pr["id"]       
                new_project_admin = ProjectAdmin(
                    project_id=idproject,
                    userId=userid[0]['userId'],
                    email=userid[0]['email'],
                    accountId = account_id,
                )
                new_project_admin.save()    

            # hapus projectadmin yg gaada di body
            for p in projectsdb:
                if (p.id not in project_now):
                    p.delete()

        if mask != None :
            ProjectAdmin.objects.filter(userId=pk).update(mask_phone=mask)
        if status != None :
            ProjectAdmin.objects.filter(userId=pk).update(status=status)

        serializer = ProjectAdminSerializer(queryset, many=False)

        return succ_resp(data=serializer.data)
        
    def delete(self, request, pk):
        account_id = self.get_account_id()

        # delete di core
        userid = ProjectAdmin.objects.filter(accountId=account_id, userId=pk).values_list('userId', flat=True)
        if list(userid) != [] :
            data = [{"id" : list(userid)[0]}]
            ExternalService().delete_user_by_account_id(account_id=account_id, data=data)

        ProjectAdmin.objects.filter(accountId=account_id, userId=pk).delete()
        response = "success delete user "+str(pk)     
        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

class ProjectAdminAccountListCreateView(BaseParameterMixin, mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    
    serializer_class = ProjectAdminSerializer

    def get(self, request):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        project_id = self.get_project_param()

        self.queryset = ProjectAdmin.objects.filter(accountId=account_id).distinct('email')
        if(project_id != None) :
            projecadmin = ProjectAdmin.objects.filter(accountId=account_id, project=project_id).values_list('email', flat=True)
            self.queryset = ProjectAdmin.objects.filter(accountId=account_id).exclude(Q(project=project_id) | Q(email__in=list(projecadmin))).distinct('email')
        else :
            projecadmin = ProjectAdmin.objects.filter(accountId=account_id).values_list('email', flat=True)
            self.queryset = ProjectAdmin.objects.filter(accountId=account_id).exclude(Q(project=project_id) | Q(email__in=list(projecadmin))).distinct('email')

        serializer = ProjectAdminSerializer(self.queryset, many=True)

        external_service = ExternalService()
        campaign = external_service.get_user_by_account_id(account_id=account_id)

        for pv in serializer.data:
            total = ProjectAdmin.objects.filter(accountId=account_id, userId=pv['userId']).count()
            createby = next((x for x in campaign if x['id'] == pv['createdBy']), 0)
            
            # update name create by 
            if( createby != 0) :
                if (createby['role'] == "owner") :
                    names = "Owner (" + (createby['name'] + ")")
                else :
                    names =  "Spv (" + (createby['name'] + ")")
                pv.update({'created_by' : names})

            # update info user
            chann = next((x for x in campaign if x['id'] == pv['userId']), 0)
            if( chann != 0) :
                pv.update({'name' : chann['name'], 'email' : chann['email'], 'phone' : chann['phone'], 'picture' : chann['picture'], 'totalProject' : total}) 
                          
        return succ_resp(data=serializer.data)

class ListProjectAdminView(BaseParameterMixin, mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    
    serializer_class = ProjectAdminListSerializer

    def get(self, request):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        since = self.get_since()
        until = self.get_until()
        filter_status = self.filter_status_active()
        filter_project = self.filter_project_by_admin()

        admins=ProjectAdmin.objects.filter(accountId=account_id, **filter_status, **filter_project).order_by('email','-id').distinct('email')

        self.queryset = ProjectAdmin.objects.filter(id__in=admins).order_by('-id')
        serializer = ProjectAdminListSerializer(self.queryset, many=True)

        external_service = ExternalService()
        campaign = external_service.get_user_by_account_id(account_id=account_id)

        for pv in serializer.data:
            a = ProjectAdmin.objects.filter(accountId=account_id, userId=pv['userId']).values_list('project', flat=True)
            b = Project.objects.filter(accountId=account_id, id__in=a).values('id', 'name', 'picture')
            pv.update({'projects' : b})

            total = ProjectAdmin.objects.filter(accountId=account_id, userId=pv['userId']).count()
            createby = next((x for x in campaign if x['id'] == pv['createdBy']), 0)
            # update name create by 
            if( createby != 0) :
                if (createby['role'] == "owner") :
                    names = "Owner (" + (createby['name'] + ")") if createby['name'] else "Owner ()"
                elif(createby['role'] == "admin") :
                    names =  "Admin (" + (createby['name'] + ")") if createby['name'] else "Admin ()"
                else :
                    names =  "Spv (" + (createby['name'] + ")") if createby['name'] else "Spv ()"
                pv.update({'created_by' : names})

            # update info user
            chann = next((x for x in campaign if x['id'] == pv['userId']), 0)
            if( chann != 0) :
                pv.update({'name' : chann['name'], 'email' : chann['email'], 'phone' : chann['phone'], 'picture' : chann['picture'], 'createdAt': chann['createdAt'], 'totalProject' : total}) 
        serializer_data = sorted(
            serializer.data, key=lambda k: k['createdAt'], reverse=True)                  
        return succ_resp(data=serializer_data)

class ProjectAdmiInviteListCreateViewclass(BaseParameterMixin, mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    
    serializer_class = ProjectAdminSerializer

    def post(self, request):
        error_message='Invite failed / user already exists'
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        existing = self.get_existing()
        temp_data = request.data

        base_url_core = os.environ.get('CORE_API_URL')
        url = base_url_core+"internal/accounts/"+account_id+"/invites"
        existadmin = ProjectAdmin.objects.filter(accountId = account_id).values_list('email', flat=True).distinct('email')
        # external
        # getuserId = ExternalService().get_user_by_account_id(account_id=account_id)
        self.queryset = ProjectAdmin.objects.filter(accountId=account_id)

        for temp in temp_data:
            projects = temp.get("projects")
            usrs = temp.get("users")

            admin = {'role' : 'admin'}
            listbody = []

            if existing == 'true' :
                for u in usrs :       
                    userid = ProjectAdmin.objects.filter(accountId = account_id, email=u['email']).values_list('userId', flat=True)
                    mask = ProjectAdmin.objects.filter(accountId = account_id, email=u['email']).values_list('mask_phone', flat=True).first()
                    for a in projects:
                        if ProjectAdmin.objects.filter(accountId = account_id, email=u['email'], project=a['id']).count() < 1 == True :
                            new_project_admin = ProjectAdmin(
                                project_id=a['id'],
                                userId=userid[0],
                                email=u['email'],
                                accountId = account_id,
                                createdBy = invoker_id,
                                mask_phone = mask
                            )
                            new_project_admin.save()
                            ress = list(self.queryset.values())
                            status_code = 200
                        
                        else : 
                            project_name = Project.objects.filter(accountId = account_id, id=a['id']).values_list('name',flat=True)
                            status_code = 422
                            ress = {"message" : "\""+u['email']+"\" has already added in "+str(project_name[0])+""}
                            return succ_resp(data=ress, status=status_code)
            else :
                for u in usrs :
                    body = {}
                    body.update(admin)
                    body.update(u) 
                    listbody.append(body)
                    
                responsee = requests.request("POST", url = url, data=json.dumps(listbody), headers={ 'Content-Type': 'application/json','Accept': 'application/json',})
                if(responsee.status_code == 200):
                    ress = json.loads(responsee.text)
                    status_code = 200
                    for u in usrs :
                        
                        #create project admin
                        for r in ress:
                            for a in projects:
                                new_project_admin = ProjectAdmin(
                                    project_id=a['id'],
                                    userId=r['id'],
                                    email=r['email'],
                                    accountId = account_id,
                                    createdBy = invoker_id
                                )
                                new_project_admin.save()     

                else : 
                    ress = json.loads(responsee.text)
                    status_code = responsee.status_code


        return succ_resp(data=ress, status=status_code)
