from  .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from . import models, serializers
from django.db.models import Q
from maritime.abstract.views import DynamicDepthViewSet, GeoViewSet
from maritime.abstract.models import get_fields, DEFAULT_FIELDS, DEFAULT_EXCLUDE
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
    filterset_fields = get_fields(models.Metalwork, exclude=DEFAULT_EXCLUDE+DEFAULT_FIELDS+['orig_coords'])
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
    

class ResourcesFilteringViewSet(GeoViewSet):
    serializer_class = serializers.SiteCoordinatesSerializer
    
    def dispatch(self, request, *args, **kwargs):
        # Define mapping for resources to models
        mapping = {
            'plank_boats': models.PlankBoats, 
            'log_boats': models.LogBoats, 
            'radiocarbon_dates': models.Radiocarbon, 
            'individual_samples': models.IndividualObjects, 
            'dna_samples': models.aDNA, 
            'metal_analysis': models.MetalAnalysis, 
            'landing_points': models.LandingPoints, 
            'new_samples': models.NewSamples, 
            'metalwork': models.Metalwork
        }
        
        resource_type = request.GET.get('type') 
        
        # Set the queryset based on resource type
        for key, model in mapping.items():
            if resource_type == key:
                queryset = model.objects.all()
                self.queryset = queryset
                break

        return super(ResourcesFilteringViewSet, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        resource_type = self.request.query_params.get('type')
        min_year = self.request.query_params.get('min_year')
        max_year = self.request.query_params.get('max_year')

        # Default queryset for `Site`
        queryset = models.Site.objects.all()

        # Map the resource type to the actual model
        resource_mapping = {
            'plank_boats': models.PlankBoats,
            'log_boats': models.LogBoats,
            'radiocarbon_dates': models.Radiocarbon,
            'individual_samples': models.IndividualObjects,
            'dna_samples': models.aDNA,
            'metal_analysis': models.MetalAnalysis,
            'landing_points': models.LandingPoints,
            'new_samples': models.NewSamples,
            'metalwork': models.Metalwork,
        }

        # If resource_type is provided, filter based on it
        if resource_type and resource_type in resource_mapping:
            resource_model = resource_mapping[resource_type]
            resource_queryset = resource_model.objects.all()

            # Apply period filtering to the resources
            if min_year and max_year:
                resource_queryset = resource_queryset.filter(
                    Q(Q(period__start_date__gte=min_year) | Q(period__end_date__gte=max_year))  
                    & (Q(period__end_date__lte=max_year) | Q(period__start_date__lte=max_year))
                )
            elif min_year:
                resource_queryset = resource_queryset.filter(Q(period__start_date__gte=min_year)
                                                             | Q(period__end_date__gte=min_year))
            elif max_year:
                resource_queryset = resource_queryset.filter(Q(period__end_date__lte=max_year)
                                                             | Q(period__start_date__lte=max_year))

            # Get the related site IDs from the filtered resources
            try:
                site_ids = resource_queryset.values_list('site_id', flat=True)
                queryset = queryset.filter(id__in=site_ids)
            except:
                location_site_ids = resource_queryset.values_list('location__site_id', flat=True)
                queryset = queryset.filter(id__in=location_site_ids)

        return queryset


    filterset_fields = get_fields(
        models.Site, exclude=DEFAULT_FIELDS + ['coordinates']
    )
    bbox_filter_field = 'coordinates'
    bbox_filter_include_overlapping = True
