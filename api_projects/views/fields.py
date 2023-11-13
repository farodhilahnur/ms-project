from django.http.response import HttpResponse
from ..serializers import FieldSerializer
from ..models import Field
from rest_framework import mixins, generics
import json

# field list, create
class FieldListCreateView(mixins.ListModelMixin,
                    mixins.CreateModelMixin, 
                    generics.GenericAPIView):
    queryset = Field.objects.all()
    serializer_class = FieldSerializer

    def get(self, request):
        return self.list(request)
    
    def post(self, request, *args, **kwargs):
        serializer_list = self.get_serializer(data=request.data, many=isinstance(request.data, list))
        serializer_list.is_valid(raise_exception=True)
        self.perform_create(serializer_list)
        return HttpResponse(json.dumps(serializer_list.data, ensure_ascii=False), content_type="application/json")

# field retreive, update, delete
class FieldRetrieveUpdateDeleteView(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin, 
                    mixins.DestroyModelMixin, 
                    generics.GenericAPIView):
    queryset = Field.objects.all()
    serializer_class = FieldSerializer
    
    def get(self, request, pk):
        return self.retrieve(request, pk)

    def put(self, request, pk):
        return self.update(request, pk)
    
    def delete(self, request, pk):
        self.destroy(request, pk)
        response = "success delete id "+str(pk)
        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")
