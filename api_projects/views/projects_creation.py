from api_projects.models import Campaign, Channel, UserDistribution
from api_projects.views.internal_check import InternalCheckView
from ..serializers import ChannelCrationSerializer, ProjectCrationSerializer
from rest_framework import mixins, generics
from  ..services import BaseParameterMixin, ExternalService 

import json
from django.db.models import Q

class ProjectCreationView(BaseParameterMixin,
                    mixins.ListModelMixin, 
                    mixins.CreateModelMixin,
                    generics.GenericAPIView):
    
    serializer_class = ProjectCrationSerializer

    def get(self, request):

        self.queryset = Campaign.objects.filter(accountId=2891, status='running').order_by('-createdAt')
        return self.list(request)
    

class ProjectChannelsCreationView(BaseParameterMixin,
                    mixins.ListModelMixin, 
                    mixins.CreateModelMixin,
                    generics.GenericAPIView):
    
    serializer_class = ChannelCrationSerializer

    def get(self, request, pk):
        exclude_condition = {}
        lis = UserDistribution.objects.filter(distribution='channel_exclude_juragen').values_list('city', flat=True)[0]
        if lis != None :
            print(lis)
            list_ch = [item.strip() for item in lis.split(',')]
            exclude_condition = {"name__in":list_ch}

        self.queryset = Channel.objects.filter(accountId=2891, status='running', campaign__id=pk).exclude(**exclude_condition).order_by('-createdAt')
        return self.list(request)