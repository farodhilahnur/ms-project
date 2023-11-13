from django.http import JsonResponse
from api_projects.views.internal_check import CheckForm, InternalCheckView
from ..services import BaseParameterMixin
from django.http.response import HttpResponse
from ..serializers import ChannelSerializer, FormChannelSerializer, FormFieldSerializer, FormSerializer, FormforIdSerializer
from ..models import Channel, Field, Form, FormField
from rest_framework import mixins, generics
import rest_framework
import json
from django.db import transaction, IntegrityError
from ..utils import err_resp, invalid_handler, succ_resp
import os

#form lists create
class FormListCreateView(BaseParameterMixin,
                    mixins.ListModelMixin,
                    generics.GenericAPIView):
    
    serializer_class = FormSerializer

    def get(self, request):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        self.queryset = Form.objects.filter(accountId=account_id)

        if(invoker_id != None):
            internal = CheckForm()
            ow = internal.api_user(account_id=account_id, user_id=invoker_id)
            if(ow["account"] == True) :
                if(ow["role"] == "owner") :
                    self.queryset = Form.objects.filter(accountId=account_id).order_by('-createdAt')
                else:
                    check = internal.get(request= request)
                    res = json.loads(check.content)
                    self.queryset = Form.objects.filter(id__in = res['forms'], accountId=account_id).order_by('-createdAt')
            else :
                self.queryset = Form.objects.filter(id__in = [], accountId=account_id).order_by('-createdAt')

        serializer = FormSerializer(self.queryset, many=True)
        base_url_src = os.environ.get('SRC_URL')

        if(serializer.data != None):
                for p in serializer.data:
                    src = str(base_url_src)
                    script = "<script id=\"jalaai-fetch\" data-code=\"-\" src=\""+src+"\"></script>"

                    p.update({"script" : script})

                    if(p['type'] == 'online'):
                        for c in p['channels']:
                            if(c['media']['name'] == 'Organic Website'):
                                script = "<script id=\"jalaai-fetch\" data-code=\""+c['uniqueCode']+"\" src=\""+src+"\"></script>"
                                p.update({"script" : script})

        # return JsonResponse(self.queryset, safe=False)
        return succ_resp(data=serializer.data)
    
    @transaction.atomic
    def post(self, request):
        error_message=None
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        temp_data = request.data
        form_ids = []

        for temp in temp_data:
            type = temp.get("type")
            name = temp.get("name")
            detail = temp.get("detail")
            pageUrl = temp.get("pageUrl")
            # try:
            new_form = Form(
                    name = name,
                    type = type,
                    detail = detail,
                    pageUrl = pageUrl,
                    createdBy = invoker_id,
                    accountId = account_id,
                )
            with transaction.atomic():
                new_form.save()
                form_ids.append(new_form.id)
                fields = temp.get("fields")

                # validasi phone name required
                if({'id': 1} not in fields):
                    fields.append({'id': 1})
                    
                if({'id': 2} not in fields):
                    fields.append({'id': 2})

                for field in fields:
                    field_id = field["id"]
                    
                    valid_field = Field.objects.filter(id = field_id).first()
                    if (valid_field!=None):
                                new_form_field = FormField(
                                    field = valid_field,
                                    form = new_form,
                                    createdBy = invoker_id,
                                    accountId = account_id,
                                )
                                new_form_field.save()
                    else:
                        error_message = "Field Not Found"
                        raise IntegrityError
            # except IntegrityError:
            #     return HttpResponse(json.dumps(invalid_handler(error_message), ensure_ascii=False), content_type="application/json", status=rest_framework.status.HTTP_400_BAD_REQUEST)
            
            self.queryset = Form.objects.filter(accountId=account_id, id__in=form_ids)
            # if (invoker_id!=None):
            #     self.queryset = Form.objects.filter(accountId=account_id, createdBy=invoker_id, id__in=form_ids)
            
            return self.list(request)

class FormRetreiveUpdateDeleteView(BaseParameterMixin,
                    mixins.RetrieveModelMixin, 
                    mixins.UpdateModelMixin, 
                    mixins.DestroyModelMixin, 
                    generics.GenericAPIView):

    def get_queryset(self):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        # if (invoker_id!=None):
        #     queryset = Form.objects.filter(accountId=account_id, createdBy=invoker_id)
        # else:
        queryset = Form.objects.filter(accountId=account_id)
        return queryset
    
    serializer_class = FormforIdSerializer

    def get(self, request, pk):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        self.queryset = Form.objects.get(accountId=account_id, id=pk)

        serializer = FormforIdSerializer(self.queryset, many=False)
        base_url_src = os.environ.get('SRC_URL')

        src = str(base_url_src)
        script = "<script id=\"jalaai-fetch\" data-code=\"-\" src=\""+src+"\"></script>"

        data = serializer.data
        data.update({"script" : script})

        if(data['type'] == 'online'):
            for c in data['channels']:
                if(c['media']['name'] == 'Organic Website'):
                    script = "<script id=\"jalaai-fetch\" data-code=\""+c['uniqueCode']+"\" src=\""+src+"\"></script>"
                    data.update({"script" : script})

        return succ_resp(data=data)

    def put(self, request, pk):
        error_message = None
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()

        temp = request.data
        #retreive project
        form = Form.objects.get(id=pk)
        if (not form):
            #throw invalid project return
            return HttpResponse(json.dumps(invalid_handler("Form Not Found"), ensure_ascii=False), content_type="application/json")

        name=temp.get("name")
        detail = temp.get("detail")
        type = temp.get("type")
        pageUrl = temp.get("pageUrl")

        if (form!=None):
            form.name = name
            form.detail = detail
            form.type = type
            form.pageUrl = pageUrl

        fields = temp.get("fields")

        if(fields != None):
            # validasi phone name required
                try:
                    with transaction.atomic():
                        if({'id': 1} not in fields):
                            fields.append({'id': 1})
                        
                        if({'id': 2} not in fields):
                            fields.append({'id': 2})

                        form_fields = FormField.objects.filter(form = form)
                        #delete existing field if not exist in field parameter
                        for form_field in form_fields:
                            if (form_field.id not in fields):
                                form_field.delete()
                        for field in fields:
                            field_id = field["id"]
                            # print(field_id)
                            form_field = FormField.objects.filter(field=field_id, form = form, accountId=account_id).first()
                            # print(form_field)
                            if (form_field == None):
                                new_formfield = FormField(
                                    field_id = field_id,
                                    accountId = account_id,
                                    createdBy = invoker_id,
                                    form = form
                                )
                                new_formfield.save()
                except IntegrityError:
                    return HttpResponse(json.dumps(invalid_handler(error_message), ensure_ascii=False), content_type="application/json", status=rest_framework.status.HTTP_400_BAD_REQUEST)
                
        return self.update(request, pk)
    
    def delete(self, request, pk):
        self.destroy(request, pk)
        response = "success delete id "+str(pk)
        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

class FormFieldView(BaseParameterMixin,
                    mixins.ListModelMixin,
                    generics.GenericAPIView):
    
    serializer_class = FormFieldSerializer

    def get(self, request, pk):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        form = Form.objects.filter(id=pk).first()
        self.queryset = FormField.objects.filter(form = form, accountId=account_id)
        # if (invoker_id!=None):
        #     channel_teams = ChannelGroup.objects.filter(channel = channel, accountId=account_id, createdBy=invoker_id,)

        return self.list(request)

class FormChannelView(BaseParameterMixin,
                    mixins.ListModelMixin,
                    generics.GenericAPIView):
    
    serializer_class = ChannelSerializer

    def get(self, request, pk):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        self.queryset = Channel.objects.filter(form=pk, accountId=account_id)
        # if (invoker_id!=None):
        #     self.queryset = Form.objects.filter(accountId=account_id, createdBy=invoker_id)
            
        return self.list(request)
