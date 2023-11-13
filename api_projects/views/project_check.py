from api_projects.services import ExternalService
from ..models import Campaign, Category, Channel, ChannelSettingMember, CustomStatus, Project, ProjectDuplicateStatus, ProjectTeam, ProjectProduct, ProjectStatus, Status
from rest_framework.response import Response

from rest_framework.views import APIView
from datetime import datetime, timedelta
import pytz
import json
import os
import requests
import logging


class ProjectCheckCreateView(APIView):
    def sendto_notif(self, data):
        logger = logging.getLogger(__name__)
        url = os.environ.get('NOTIF_API_URL')+"notif/send?type=dashboard"

        response = requests.request("POST", url = url, json=data, headers={ 'Content-Type': 'application/json','Accept': 'application/json',})
        if(response.status_code == 200):
            logger.error(url +" => " + str(response.status_code) + str(response.text))
        else:
            logger.error(url +" => " + str(response.status_code) + str(response.text))

        
    def bodys(self, userid, accountid, info, info_id, name, dateend):
        body = {
                "userId": userid,
                "message": {
                    "title": "Opss, your "+str(info)+" duration will end 😮",
                    "body": " "+str(info).capitalize()+" '"+str(name)+"' will end soon on "+str(dateend)+". Immediately check and renew duration so as not to miss."
                },
                "data": {
                    "accountId": ""+str(accountid)+"",
                    "page": ""+str(info)+"_detail",
                    "sub_type": "info",
                    ""+str(info)+"_id": ""+str(info_id)+""
                }
            }

        return body

    def get(self, request):
        allproject = Project.objects.filter(status='running').exclude(periodEnd=None).values('id', 'accountId', 'periodEnd', 'status', 'name').order_by('id')
        allcampaign = Campaign.objects.filter(status='running').exclude(periodEnd=None).values('id', 'accountId', 'periodEnd', 'status', 'name').order_by('id')
        allchannel = Channel.objects.filter(status='running').exclude(periodEnd=None).values('id', 'accountId', 'periodEnd', 'status', 'name').order_by('id')
        datalist = []
        external = ExternalService()
        daybefore = 1
        if self.request.GET.get('day_before') != None:
            daybefore = self.request.GET.get('day_before')

        datenow = datetime.now(tz=pytz.timezone('Asia/Jakarta')).strftime("%Y-%m-%d")
        for j in allproject:
            b = str(j['periodEnd'].year)+"-"+str(j['periodEnd'].month)+"-"+str(j['periodEnd'].day)
            c = datetime.strptime(b, "%Y-%m-%d") - timedelta(days=int(daybefore))
            stopnow = datetime.strptime(b, "%Y-%m-%d") + timedelta(days=1)

            dataproject = []
            if datetime.strftime(c, "%Y-%m-%d") == datenow:
                userid = external.get_owner_id(account=j['accountId'])
                if(userid != None):
                    dataproject.append(self.bodys(userid=userid, accountid=j['accountId'], info='project', info_id=j['id'], name=j['name'], dateend=str(b)))
                    if dataproject != [] :
                        self.sendto_notif(data=dataproject)
                        datalist.append(dataproject)
            
            if datetime.strftime(stopnow, "%Y-%m-%d") <= datenow:
                Project.objects.filter(id=j['id']).update(status='stop')

        for k in allcampaign:
            d = str(k['periodEnd'].year)+"-"+str(k['periodEnd'].month)+"-"+str(k['periodEnd'].day)
            e = datetime.strptime(d, "%Y-%m-%d")
            stopnow = datetime.strptime(d, "%Y-%m-%d") + timedelta(days=1)

            datacampaign = []
            if datetime.strftime(e, "%Y-%m-%d") == datenow:
                userid = external.get_owner_id(account=k['accountId'])
                if(userid != None):
                    datacampaign.append(self.bodys(userid=userid, accountid=k['accountId'], info='campaign', info_id=k['id'], name=k['name'], dateend=str(stopnow)))
                    if datacampaign != [] :
                        self.sendto_notif(data=datacampaign)
                        datalist.append(datacampaign)

            if datetime.strftime(stopnow, "%Y-%m-%d") <= datenow:
                Campaign.objects.filter(id=k['id']).update(status='stop')

        for l in allchannel:
            f = str(l['periodEnd'].year)+"-"+str(l['periodEnd'].month)+"-"+str(l['periodEnd'].day)
            g =  datetime.strptime(f, "%Y-%m-%d")
            stopnow = datetime.strptime(f, "%Y-%m-%d") + timedelta(days=1)

            datachannel = []
            if datetime.strftime(g, "%Y-%m-%d") == datenow:
                userid = external.get_owner_id(account=l['accountId'])
                if(userid != None):
                    datachannel.append(self.bodys(userid=userid, accountid=l['accountId'], info='channel', info_id=l['id'], name=l['name'], dateend=str(stopnow)))
                    if datachannel != [] :
                        self.sendto_notif(data=datachannel)
                        datalist.append(datachannel)
            
            if datetime.strftime(stopnow, "%Y-%m-%d") <= datenow:
                Channel.objects.filter(id=l['id']).update(status='stop')

        return Response(status=200, data=datalist)