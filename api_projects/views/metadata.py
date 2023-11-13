from rest_framework.views import APIView
from rest_framework.response import Response
import json

class ChannelMetadata(APIView):
    def get(self, request):
        res = {
            'statuses' : {'running', 'hold', 'stop'},
            'lead_distribution': {'manual', 'roundRobin', 'percentage'},
            'media' : {'offline','online'}
            }
        return Response(status=200, data=res)