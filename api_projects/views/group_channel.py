import json
from django.http.response import HttpResponse

from api_projects.utils import succ_resp
from ..serializers import GroupChannelSerializer
from ..models import Channel, ChannelGroup, Project, ProjectTeam
from rest_framework import mixins, generics
from  ..services import BaseParameterMixin, ExternalService 
from api_projects.views.internal_check import InternalCheckView
from django.db import transaction, IntegrityError

class AssignGroupChannelsListView(BaseParameterMixin, 
                    generics.GenericAPIView):

    serializer_class = GroupChannelSerializer
    
    def get(self, request, pk):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        since = self.get_since()
        until = self.get_until()
        
        channels = ChannelGroup.objects.filter(teamId = pk, accountId=account_id).values_list('channel', flat=True)

        ch = Channel.objects.filter(id__in=channels).values('id', 'name').order_by('-id')

        return succ_resp(data=ch)

    @transaction.atomic
    def post(self, request, pk):
        error_message=None
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()

        temp = request.data
        channel_ids = temp.get("channel_ids")
        all_channel = temp.get("all_channel")
        filters_payload = temp.get("filters")

        new_channel_team_list = []

        if all_channel == True or all_channel == 'true' :
            filter_project = {}
            filter_campaign = {}
            filter_media = {}
            filter_search = {}

            if filters_payload:
                if "project_ids" in filters_payload:
                    filter_project = {"campaign__project_id__in": filters_payload['project_ids']}
                if "campaign_ids" in filters_payload:
                    filter_campaign = {"campaign__id__in": filters_payload['campaign_ids']}
                if "media" in filters_payload:
                    filter_media = {"media__type__in": filters_payload['media']}
                if "search" in filters_payload:
                    filter_search = {"name__icontains": filters_payload['search']}


            channel_ids_from_database = Channel.objects.filter(accountId=account_id, **filter_project, **filter_campaign, **filter_media, **filter_search).values_list("id", flat=True)
            existing = ChannelGroup.objects.filter(teamId=pk).values_list("channel", flat= True)
            channel_group_objects = []

            for ch_id in channel_ids_from_database:
                if ch_id not in existing:
                    channel_group_objects.append(
                        ChannelGroup(teamId=pk, createdBy=invoker_id, accountId=account_id, channel_id=ch_id)
                    )
        else:
            existing = ChannelGroup.objects.filter(teamId=pk).values_list("channel", flat= True)
            channel_group_objects = []

            for ch_id in channel_ids:
                if ch_id not in existing:
                    channel_group_objects.append(
                        ChannelGroup(teamId=pk, createdBy=invoker_id, accountId=account_id, channel_id=ch_id)
                    )

        # Pisahkan objek-objek ke dalam batch size 100 dan buat ke database
        batch_size = 10000
        for i in range(0, len(channel_group_objects), batch_size):
            batch = channel_group_objects[i:i + batch_size]
            ChannelGroup.objects.bulk_create(batch)

        self.queryset = Channel.objects.filter(accountId=account_id)
        res = {'message' : 'Success assign group to channel'}

        return succ_resp(data=res)