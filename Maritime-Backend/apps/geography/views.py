from tkinter import N
from rest_framework import viewsets
from rest_framework.schemas.openapi import AutoSchema
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_gis.filters import InBBoxFilter
from rest_framework_gis.pagination import GeoJsonPagination
from . import models, serializers

from maritime.abstract.views import DynamicDepthViewSet, GeoViewSet
from maritime.abstract.models import get_fields

class ProvinceViewSet(GeoViewSet):

    queryset = models.Province.objects.all()
    serializer_class = serializers.ProvinceSerializer
    filterset_fields = get_fields(models.Province, exclude=['geometry'])

class ParishViewSet(GeoViewSet):

    queryset = models.Parish.objects.all()
    serializer_class = serializers.ParishSerializer
    filterset_fields = get_fields(models.Parish, exclude=['geometry'])


class CountryViewSet(GeoViewSet):

    queryset = models.Country.objects.all()
    serializer_class = serializers.CountrySerializer
    filterset_fields = get_fields(models.Country, exclude=['geometry'])


class LAUViewSet(GeoViewSet):

    queryset = models.LAU.objects.all()
    serializer_class = serializers.LAUSerializer
    filterset_fields = get_fields(models.LAU, exclude=['geometry'])

    
