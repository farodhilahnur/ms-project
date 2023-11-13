from django.shortcuts import render
from ..services import ExternalService
from django.http.response import HttpResponse
from ..serializers import CategoryStatusSerializer, StatusCategorySerializer
from ..models import Category, Status
from rest_framework import mixins, generics
import rest_framework
import json
from ..utils import invalid_handler

# Create your views here.

# category list, create
class CategoryListCreateView(mixins.ListModelMixin,
                    mixins.CreateModelMixin, 
                    generics.GenericAPIView
                    ):
    queryset = Category.objects.all()
    serializer_class = CategoryStatusSerializer

    def get(self, request):
        return self.list(request)
    
    def post(self, request, *args, **kwargs):
        serializer_list = self.get_serializer(data=request.data, many=isinstance(request.data, list))
        serializer_list.is_valid(raise_exception=True)
        self.perform_create(serializer_list)
        return HttpResponse(json.dumps(serializer_list.data, ensure_ascii=False), content_type="application/json")

# category retreive, update, delete by category id
class CategoryRetrieveUpdateDeleteView(
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin, 
                    mixins.DestroyModelMixin, 
                    generics.GenericAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryStatusSerializer
    
    def get(self, request, pk):
        return self.retrieve(request, pk)

    def put(self, request, pk):
        return self.update(request, pk)
    
    def delete(self, request, pk):
        self.destroy(request, pk)
        response = "success delete id "+str(pk)
        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

# category retreive by status id
class CategoryStatusListCreateView(mixins.ListModelMixin,
                    mixins.CreateModelMixin, 
                    generics.GenericAPIView
                    ):
    serializer_class = StatusCategorySerializer

    def get(self, request, pk):
        self.queryset = Status.objects.filter(id=pk)
        return self.list(request, pk)
    
    def post(self, request, pk):
        category_id = pk
        category = Category.objects.filter(id = category_id).first()
        if (category==None):
            return HttpResponse(json.dumps(invalid_handler("Category Not Found"), ensure_ascii=False), content_type="application/json", status=rest_framework.status.HTTP_400_BAD_REQUEST)
        else:    
            temp_data = request.data
            for temp in temp_data:
                name = temp.get("name")
                point = temp.get("point")
                detail = temp.get("detail")
                sort = temp.get("sort")
                color = temp.get("color")
                enableReminder = temp.get("enableReminder")
                new_status = Status(
                    category = category,
                    name = name,
                    point = point,
                    detail = detail,
                    sort = sort,
                    color= color,
                    enableReminder = enableReminder  
                )
                new_status.save()
            self.queryset = Status.objects.filter(id=pk)
            return self.list(request, pk)

