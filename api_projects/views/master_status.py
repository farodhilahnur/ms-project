from django.http.response import HttpResponse
from ..serializers import StatusCategorySerializer
from ..models import Category, Status
from rest_framework import mixins, generics
import rest_framework
import json
from ..utils import invalid_handler

# status list, create
class StatusListCreateView(mixins.ListModelMixin,
                    mixins.CreateModelMixin, 
                    generics.GenericAPIView):
    
    queryset = Status.objects.all()
    serializer_class = StatusCategorySerializer

    def get(self, request):
        return self.list(request)
    
    def post(self, request, *args, **kwargs):
        temp_data = request.data
        for temp in temp_data:
            name = temp.get("name")
            point = temp.get("point")
            detail = temp.get("detail")
            sort = temp.get("sort")
            color = temp.get("color")
            tenantCategory = temp.get("tenantCategory")

            category_id = temp["category"]["id"]
            category = Category.objects.filter(id = category_id).first()
            if (category==None):
                return HttpResponse(json.dumps(invalid_handler("Category Not Found"), ensure_ascii=False), content_type="application/json", status=rest_framework.status.HTTP_400_BAD_REQUEST)
            else:
                new_status = Status(
                    category = category,
                    name = name,
                    point = point,
                    detail = detail,
                    sort = sort,
                    color= color,
                    tenantCategory = tenantCategory
                )
                new_status.save()

        return HttpResponse(json.dumps(temp_data, ensure_ascii=False), content_type="application/json")

# status retreive, update, delete  by status id
class StatusRetrieveUpdateDeleteView(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin, 
                    mixins.DestroyModelMixin, 
                    generics.GenericAPIView):
    queryset = Status.objects.all()
    serializer_class = StatusCategorySerializer
    
    def get(self, request, pk):
        return self.retrieve(request, pk)

    def put(self, request, pk):
        return self.update(request, pk)
    
    def delete(self, request, pk):
        self.destroy(request, pk)
        response = "success delete id "+str(pk)
        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")
