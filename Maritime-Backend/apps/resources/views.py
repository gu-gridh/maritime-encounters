from . import models, serializers
from django.db.models import Q
from maritime.abstract.views import DynamicDepthViewSet, GeoViewSet
from maritime.abstract.models import get_fields, DEFAULT_FIELDS
from django.views.decorators.csrf import csrf_exempt
from django.contrib.gis.geos import Polygon
from django.contrib.gis.gdal.envelope import Envelope 

class SiteViewSet(DynamicDepthViewSet):
    serializer_class = serializers.SiteGeoSerializer
    queryset = models.Site.objects.all()
                                    

    filterset_fields = get_fields(models.Site, exclude=DEFAULT_FIELDS + ['coordinates'])
    search_fields = ['placename']
    bbox_filter_field = 'coordinates'
    bbox_filter_include_overlapping = True


class SiteGeoViewSet(GeoViewSet):

    serializer_class = serializers.SiteGeoSerializer
    queryset = models.Site.objects.all()

    filterset_fields = get_fields(models.Site, exclude=DEFAULT_FIELDS + ['coordinates'])
    search_fields = ['placename', 'name']
    bbox_filter_field = 'coordinates'
    bbox_filter_include_overlapping = True


class MetalAnalysisViewSet(DynamicDepthViewSet):
    serializer_class = serializers.MetalAnalysisSerializer
    queryset = models.MetalAnalysis.objects.all()
    filterset_fields = get_fields(models.MetalAnalysis, exclude=DEFAULT_FIELDS)
    search_fields = ['site__name']


