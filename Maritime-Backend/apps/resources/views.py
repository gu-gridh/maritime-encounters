from  .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from . import models, serializers
from django.db.models import Q
from maritime.abstract.views import DynamicDepthViewSet, GeoViewSet
from maritime.abstract.models import get_fields, DEFAULT_FIELDS
from django.views.decorators.csrf import csrf_exempt
from django.contrib.gis.geos import Polygon
from django.contrib.gis.gdal.envelope import Envelope
from rest_framework.views import APIView


class SiteViewSet(DynamicDepthViewSet):
    serializer_class = serializers.SiteGeoSerializer
    queryset = models.Site.objects.all()

    filterset_fields = get_fields(
        models.Site, exclude=DEFAULT_FIELDS + ['coordinates'])
    search_fields = ['placename']
    bbox_filter_field = 'coordinates'
    bbox_filter_include_overlapping = True


class SiteCoordinatesViewSet(GeoViewSet):
    serializer_class = serializers.SiteCoordinatesSerializer
    queryset = models.Site.objects.all().order_by('id')
    filterset_fields = get_fields(
        models.Site, exclude=DEFAULT_FIELDS + ['coordinates'])
    bbox_filter_field = 'coordinates'
    bbox_filter_include_overlapping = True
    


class SiteGeoViewSet(GeoViewSet):

    serializer_class = serializers.SiteGeoSerializer
    queryset = models.Site.objects.all()

    filterset_fields = get_fields(
        models.Site, exclude=DEFAULT_FIELDS + ['coordinates'])
    search_fields = ['placename', 'name']
    bbox_filter_field = 'coordinates'
    bbox_filter_include_overlapping = True


class MetalAnalysisViewSet(DynamicDepthViewSet):
    serializer_class = serializers.MetalAnalysisSerializer
    queryset = models.MetalAnalysis.objects.all()
    filterset_fields = get_fields(models.MetalAnalysis, exclude=DEFAULT_FIELDS)
    search_fields = ['site__name']


class MetalworkViewSet(DynamicDepthViewSet):
    serializer_class = serializers.MetalworkSerializer
    queryset = models.Metalwork.objects.all()
    filterset_fields = get_fields(models.Metalwork, exclude=DEFAULT_FIELDS+['orig_coords'])
    search_fields = ['site__name', 'entry_number']


class SiteResourcesViewSet(viewsets.ViewSet):
    
    def list(self, request):
        site_id = request.GET.get("site_id")
        
        if not site_id:
            return Response({"error": "site_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            site = Site.objects.get(id=site_id)
        except Site.DoesNotExist:
            return Response({"error": "Site not found."}, status=status.HTTP_404_NOT_FOUND)
        
        data = {
            'plank_boats': PlankBoatsSerializer(PlankBoats.objects.filter(site=site), many=True).data,
            'log_boats': LogBoatsSerializer(LogBoats.objects.filter(site=site), many=True).data,
            'radiocarbon_dates': RadiocarbonSerializer(Radiocarbon.objects.filter(site=site), many=True).data,
            'individual_samples': IndivdualObjectSerializer(IndividualObjects.objects.filter(site=site), many=True).data,
            'dna_samples': aDNASerializer(aDNA.objects.filter(site=site), many=True).data,
            'metal_analysis': MetalAnalysisSerializer(MetalAnalysis.objects.filter(site=site), many=True).data,
            'landing_points': LandingPointsSerializer(LandingPoints.objects.filter(site=site), many=True).data,
            'new_samples': NewSamplesSerializer(NewSamples.objects.filter(site=site), many=True).data,
            'metalwork': MetalworkSerializer(Metalwork.objects.filter(location__site=site), many=True).data,
        }

        return Response(data, status=status.HTTP_200_OK)
    