from api_projects.services import BaseParameterMixin
from django.db import transaction, IntegrityError
from django.shortcuts import render
from django.http.response import HttpResponse
from ..serializers import MediaSerializer
from ..models import Media
from django.db.models import Q
from rest_framework import mixins, generics
import rest_framework
import json

# media list, create
class MediaListCreateView(BaseParameterMixin, mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    
    queryset = Media.objects.all()
    serializer_class = MediaSerializer

    def get(self, request):
        account_id = self.get_account_id()
        self.queryset = Media.objects.filter(accountId=None)
        if(account_id != None) : 
            self.queryset = Media.objects.filter(Q(accountId = account_id) | Q(accountId = None))

        return self.list(request)
    
    def post(self, request, *args, **kwargs):
        error_message=None
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        temp_data = request.data

        for temp in temp_data:
            name=temp.get("name")
            type = temp.get("type")
            picture = temp.get("picture")
            
            if (account_id != None) :
                new_channel = Media(
                    name= name,
                    type = type,
                    picture = picture,
                    accountId = account_id    
                )
                new_channel.save()
            else:
                new_channel = Media(
                    name= name,
                    type = type,
                    picture = picture
                )
                new_channel.save()
        
        return self.list(request)

# media retreive, update, delete by media id
class MediaRetrieveUpdateDeleteView(
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin, 
                    mixins.DestroyModelMixin, 
                    generics.GenericAPIView):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    
    def get(self, request, pk):
        return self.retrieve(request, pk)

    def put(self, request, pk):
        return self.update(request, pk)
    
    def delete(self, request, pk):
        self.destroy(request, pk)
        response = "success delete id "+str(pk)
        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

# channel media
class ChannelMediaView(BaseParameterMixin, mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    
    queryset = Media.objects.all()
    serializer_class = MediaSerializer

    def get(self, request):
        account_id = self.get_account_id()
        self.queryset = Media.objects.filter(accountId=None)
        if(account_id != None) : 
            self.queryset = Media.objects.filter(Q(accountId = account_id) | Q(accountId = None))

        return self.list(request)
    
    def post(self, request, *args, **kwargs):
        error_message=None
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        temp_data = request.data

        for temp in temp_data:
            name=temp.get("name")
            type = temp.get("type")
            picture = temp.get("picture")
            
            if (account_id != None) :
                new_channel = Media(
                    name= name,
                    type = type,
                    picture = picture,
                    accountId = account_id    
                )
                new_channel.save()
            else:
                new_channel = Media(
                    name= name,
                    type = type,
                    picture = picture
                )
                new_channel.save()
        
        return self.list(request)
