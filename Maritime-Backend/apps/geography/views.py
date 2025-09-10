from rest_framework import viewsets
from rest_framework.schemas.openapi import AutoSchema
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_gis.filters import InBBoxFilter
from rest_framework_gis.pagination import GeoJsonPagination
from . import models, serializers

from maritime.abstract.views import DynamicDepthViewSet, GeoViewSet
from maritime.abstract.models import get_fields

class CountryViewSet(GeoViewSet):

    queryset = models.ADM0.objects.all()
    serializer_class = serializers.CountrySerializer
    filterset_fields = get_fields(models.ADM0, exclude=['geometry'])
    bbox_filter_field = 'geometry'  # Enable bounding box filtering

class ProvinceViewSet(GeoViewSet):

    queryset = models.Province.objects.all()
    serializer_class = serializers.ProvinceSerializer
    filterset_fields = get_fields(models.Province, exclude=['geometry'])

class ParishViewSet(GeoViewSet):

    queryset = models.Parish.objects.all()
    serializer_class = serializers.ParishSerializer
    filterset_fields = get_fields(models.Parish, exclude=['geometry'])

class ADM4ViewSet(GeoViewSet):

    queryset = models.ADM4.objects.all()
    serializer_class = serializers.ADM4Serializer
    filterset_fields = get_fields(models.ADM4, exclude=['geometry'])

    
