from api_projects.views.internal_check import InternalCheckView
from ..services import ExternalService, BaseParameterMixin
from django.http.response import HttpResponse, JsonResponse
from ..serializers import  CampaignByProjectSerializer, CampaignProjectSerializer, CampaignSerializer, CampaignSingleSerializer, UserCampaignSerializer, UserPOSTCampaignSerializer
from ..models import Campaign, Channel, ChannelSettingMember, Project, UserDistribution
from rest_framework import mixins, generics
import rest_framework
import json
from django.db import transaction, IntegrityError
from ..utils import invalid_handler, succ_resp
from django.db.models import Q, F
import re

# campaign retrieve create by user id
class UserCampaignListCreateView(BaseParameterMixin,
                    mixins.ListModelMixin,
                    generics.GenericAPIView, mixins.UpdateModelMixin):
    
    serializer_class = UserPOSTCampaignSerializer

    def get(self, request, pk):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        status = self.filter_status_running()
        project = self.filter_project_id()
        if pk == 0 :
            pk = invoker_id

        campaign = UserDistribution.objects.filter(userId = pk, accountId=account_id, distribution='campaign').first()
        if campaign != None :
            if campaign.campaignId is not None and campaign.campaignId.strip() != "":
                campaignids = tuple(campaign.campaignId.split(','))
                self.queryset = Campaign.objects.filter(accountId=account_id, id__in=campaignids, **status, **project)
                serializer = UserCampaignSerializer(self.queryset, many=True)

                if(serializer.data != []):
                    for p in serializer.data :
                        idsproject = Project.objects.get(id=p['project'])
                        p['project'] = {
                            "id": idsproject.id,
                            "name": idsproject.name
                        }
            else :
                return succ_resp(data=[])
        else :
            return succ_resp(data=[])
            
        return succ_resp(data=serializer.data)
    
    @transaction.atomic
    def post(self, request, pk):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        temp = request.data
        campaign_ids = temp.get("campaign")
        campaignids = ','.join(str(e) for e in campaign_ids)

        if pk == 0 :
            pk = invoker_id

        max_allowed = 3
        # validasi max
        if len(campaign_ids) > max_allowed:
            error_message = f"Campaigns cannot exceed {max_allowed} campaigns."
            response_data = {"message": error_message}
            return JsonResponse(response_data, status=400)

        if UserDistribution.objects.filter(accountId=account_id, userId=pk, distribution='campaign').exists() == True :
            pkid = UserDistribution.objects.filter(userId=pk, distribution='campaign', accountId=account_id).first()

            # dhannel id to keep
            channel_ids_to_keep = Channel.objects.filter(accountId=account_id, campaign__in=campaign_ids).values_list("id", flat=True)
            # existing channel
            existing_channels = ChannelSettingMember.objects.filter(userId=pkid.userId, type='preferential_campaign').values_list('channel', flat=True)

            # campaign id list to delete
            channels_to_add = []
            channels_to_remove = []
            
            for ch_id in channel_ids_to_keep:
                if ch_id not in existing_channels:
                    channels_to_add.append(ch_id)
            
            for ex_ch in existing_channels:
                if ex_ch not in channel_ids_to_keep:
                    channels_to_remove.append(ex_ch)

            channel_group_objects = []
            # add
            for ch_id_to_add in channels_to_add:
                channel_group_objects.append(
                        ChannelSettingMember(teamId=None, userId=pk, createdBy=invoker_id, accountId=account_id, channel_id=ch_id_to_add, type='preferential_campaign')
                    )
                
            # delete
            ChannelSettingMember.objects.filter(userId=pkid.userId, channel__in=channels_to_remove).delete()

            # Update campaignId pada UserDistribution
            UserDistribution.objects.filter(id=pkid.id).update(campaignId=campaignids)

            self.queryset = UserDistribution.objects.filter(id=pkid.id)
            batch_size = 10000
            for i in range(0, len(channel_group_objects), batch_size):
                batch = channel_group_objects[i:i + batch_size]
                ChannelSettingMember.objects.bulk_create(batch)
        
        else :                        
            channel_ids_from_database = Channel.objects.filter(accountId=account_id, campaign__in=campaign_ids).values_list("id", flat=True)
            channel_group_objects = []

            for ch_id in channel_ids_from_database:
                    channel_group_objects.append(
                        ChannelSettingMember(teamId=None, userId=pk, createdBy=invoker_id, accountId=account_id, channel_id=ch_id, type='preferential_campaign')
                    )

            new_campaign = UserDistribution(
                accountId = account_id,
                createdBy = invoker_id,
                campaignId = campaignids,
                userId=pk,
                distribution='campaign'
            )
            new_campaign.save()

            batch_size = 10000
            for i in range(0, len(channel_group_objects), batch_size):
                batch = channel_group_objects[i:i + batch_size]
                ChannelSettingMember.objects.bulk_create(batch)
            self.queryset = UserDistribution.objects.filter(accountId=account_id, userId=pk)

        return self.list(request, pk)

    @transaction.atomic
    def put(self, request, pk):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        if pk == 0 :
            pk = invoker_id
        
        pkid = UserDistribution.objects.filter(userId=pk, distribution='campaign').first()
        temp = request.data
        campaign_ids = temp.get("campaign")
        campaignids = ','.join(str(e) for e in campaign_ids)

        max_allowed = 3
        # validasi max
        if len(campaign_ids) > max_allowed:
            error_message = f"Campaigns cannot exceed {max_allowed} campaigns."
            response_data = {"message": error_message}
            return JsonResponse(response_data, status=400)
        
        # dhannel id to keep
        channel_ids_to_keep = Channel.objects.filter(accountId=account_id, campaign__in=campaign_ids).values_list("id", flat=True)
        # existing channel
        existing_channels = ChannelSettingMember.objects.filter(userId=pkid.userId, type='preferential_campaign').values_list('channel', flat=True)

        # campaign id list to delete
        channels_to_add = []
        channels_to_remove = []
        
        for ch_id in channel_ids_to_keep:
            if ch_id not in existing_channels:
                channels_to_add.append(ch_id)
        
        for ex_ch in existing_channels:
            if ex_ch not in channel_ids_to_keep:
                channels_to_remove.append(ex_ch)

        channel_group_objects = []
        # add
        for ch_id_to_add in channels_to_add:
            channel_group_objects.append(
                    ChannelSettingMember(teamId=None, userId=pk, createdBy=invoker_id, accountId=account_id, channel_id=ch_id_to_add, type='preferential_campaign')
                )
            
        # delete
        ChannelSettingMember.objects.filter(userId=pkid.userId, channel__in=channels_to_remove).delete()

        # Update campaignId pada UserDistribution
        UserDistribution.objects.filter(id=pkid.id).update(campaignId=campaignids)

        self.queryset = UserDistribution.objects.filter(id=pkid.id)
        batch_size = 10000
        for i in range(0, len(channel_group_objects), batch_size):
            batch = channel_group_objects[i:i + batch_size]
            ChannelSettingMember.objects.bulk_create(batch)

        return self.list(request, pkid.id)

  
class UserCityListCreateView(BaseParameterMixin,
                    mixins.ListModelMixin,
                    generics.GenericAPIView, mixins.UpdateModelMixin):
    
    serializer_class = UserPOSTCampaignSerializer

    def get(self, request, pk):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        if pk == 0:
            pk = invoker_id
        try:
            user = UserDistribution.objects.get(userId=pk, accountId=account_id, distribution='city')
              
            cities = user.city.split(',')
            listcities = []
            if cities != None and cities != "" and cities != '' and cities != ['']:
        
                location = ExternalService().get_location()
                if location != None:
                    for c in cities :
                        city = next((x for x in location if x['name'] == str(c)), 0)
                        if (city != 0) :
                            citi = {'id' : city['id'], 'name': city['name'] }  
                        else:
                            citi = {'id' : 0, 'name': str(c) } 
                        listcities.append(citi)

            data = {'city' : listcities }
            data["city"] = sorted(data["city"], key=lambda x: x["id"])

            # Tindakan yang akan diambil jika user ditemukan
        except UserDistribution.DoesNotExist:
            data = {'city' : []}
            cities = []

        if self.request.GET.get('summary') == 'true':
            campaign = UserDistribution.objects.filter(userId=pk, accountId=account_id, distribution='campaign').values_list('campaignId', flat=True)
            if campaign.exists():
                campaigns = str(campaign[0]).split(',')
                totalcampaign = len(campaigns)
            else : 
                totalcampaign = 0
            data.update({
                'total_campaign' : totalcampaign,
                'total_city' : len(cities)
            })

        return succ_resp(data=data)
    
    @transaction.atomic
    def post(self, request, pk):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()

        temp = request.data
        citys = temp.get("city")
        city = ','.join(str(e) for e in citys)
        if pk == 0:
            pk = invoker_id
        
        max_allowed = 1
        # validasi max
        if len(citys) > max_allowed:
            error_message = f"Cities cannot exceed {max_allowed} cities."
            response_data = {"message": error_message}
            return JsonResponse(response_data, status=400)

        list_all_city = ExternalService().get_location()

        if UserDistribution.objects.filter(accountId=account_id, userId=pk, distribution='city').exists() == True :
            pkid = UserDistribution.objects.filter(userId=pk, distribution='city').first()

            # Existing keep cities
            query = Q()
            for c in citys:
                query |= Q(campaign__name__icontains=c)
                aliases = [alias for city in list_all_city if city['alias'] and city['name'] == c for alias in city['alias'].split(', ')]
                for c in aliases:
                    query |= Q(campaign__name__icontains=c)

            channel_ids_to_keep = Channel.objects.filter(query, accountId=account_id).values_list("id", flat=True)
            existing_channels = ChannelSettingMember.objects.filter(userId=pkid.userId, type='preferential_city').values_list('channel', flat=True)

            # list id delete
            channels_to_add = []
            channels_to_remove = []
            
            for ch_id in channel_ids_to_keep:
                if ch_id not in existing_channels:
                    channels_to_add.append(ch_id)
            
            for ex_ch in existing_channels:
                if ex_ch not in channel_ids_to_keep:
                    channels_to_remove.append(ex_ch)

            channel_group_objects = []
            # add
            for ch_id_to_add in channels_to_add:
                channel_group_objects.append(
                        ChannelSettingMember(teamId=None, userId=pk, createdBy=invoker_id, accountId=account_id, channel_id=ch_id_to_add, type='preferential_city')
                    )
                
            # delete
            ChannelSettingMember.objects.filter(userId=pkid.userId, channel__in=channels_to_remove).delete()

            batch_size = 10000
            for i in range(0, len(channel_group_objects), batch_size):
                batch = channel_group_objects[i:i + batch_size]
                ChannelSettingMember.objects.bulk_create(batch)

        
            UserDistribution.objects.filter(id=pkid.id).update(city=city)

        else :
            channel_ids_from_database = []
            query = Q()
            for ch in citys:
                query |= Q(campaign__name__icontains=ch)
                aliases = [alias for city in list_all_city if city['alias'] and city['name'] == ch for alias in city['alias'].split(', ')]
                for c in aliases:
                    query |= Q(campaign__name__icontains=c)
            ids = Channel.objects.filter(query, accountId=account_id).values_list("id", flat=True)
            channel_ids_from_database.extend(ids)
            
            channel_group_objects = []
            for ch_id in channel_ids_from_database:
                    channel_group_objects.append(
                        ChannelSettingMember(teamId=None, userId=pk, createdBy=invoker_id, accountId=account_id, channel_id=ch_id, type='preferential_city')
                    )

            new_city = UserDistribution(
                accountId = account_id,
                createdBy = invoker_id,
                city = city,
                userId=pk,
                distribution='city'
            )
            new_city.save()

            batch_size = 10000
            for i in range(0, len(channel_group_objects), batch_size):
                batch = channel_group_objects[i:i + batch_size]
                ChannelSettingMember.objects.bulk_create(batch)

        self.queryset = UserDistribution.objects.filter(accountId=account_id, userId=pk)

        return self.list(request, pk)

    @transaction.atomic
    def put(self, request, pk):
        account_id = self.get_account_id()
        invoker_id = self.get_invoker_id()
        if pk == 0:
            pk = invoker_id
        pkid = UserDistribution.objects.filter(userId=pk, distribution='city').first()
        temp = request.data
        city = temp.get("city")
        cities = ','.join(str(e) for e in city)

        max_allowed = 1
        # validasi max
        if len(city) > max_allowed:
            error_message = f"Cities cannot exceed {max_allowed} cities."
            response_data = {"message": error_message}
            return JsonResponse(response_data, status=400)
        
        list_all_city = ExternalService().get_location()

        # Existing keep cities
        query = Q()
        for c in city:
            query |= Q(campaign__name__icontains=c)
            aliases = [alias for city in list_all_city if city['alias'] and city['name'] == c for alias in city['alias'].split(', ')]
            for c in aliases:
                query |= Q(campaign__name__icontains=c)

        channel_ids_to_keep = Channel.objects.filter(query, accountId=account_id).values_list("id", flat=True)
        existing_channels = ChannelSettingMember.objects.filter(userId=pkid.userId, type='preferential_city').values_list('channel', flat=True)

        # list id delete
        channels_to_add = []
        channels_to_remove = []
        
        for ch_id in channel_ids_to_keep:
            if ch_id not in existing_channels:
                channels_to_add.append(ch_id)
        
        for ex_ch in existing_channels:
            if ex_ch not in channel_ids_to_keep:
                channels_to_remove.append(ex_ch)

        channel_group_objects = []
        # add
        for ch_id_to_add in channels_to_add:
            channel_group_objects.append(
                    ChannelSettingMember(teamId=None, userId=pk, createdBy=invoker_id, accountId=account_id, channel_id=ch_id_to_add, type='preferential_city')
                )
            
        # delete
        ChannelSettingMember.objects.filter(userId=pkid.userId, channel__in=channels_to_remove).delete()

        batch_size = 10000
        for i in range(0, len(channel_group_objects), batch_size):
            batch = channel_group_objects[i:i + batch_size]
            ChannelSettingMember.objects.bulk_create(batch)

    
        UserDistribution.objects.filter(id=pkid.id).update(city=cities)

        self.queryset = UserDistribution.objects.filter(id=pkid.id)

        return self.list(request, pkid.id)
   
