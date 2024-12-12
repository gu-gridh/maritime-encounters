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


class LandingPointsViewSet(DynamicDepthViewSet):
    serializer_class = serializers.LandingPointsSerializer
    queryset = models.LandingPoints.objects.all()
    filterset_fields = get_fields(models.LandingPoints, exclude=DEFAULT_FIELDS)
    search_fields = ['site__name']

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


class SearchPeriodsNames(DynamicDepthViewSet):
    serializer_class = serializers.PeriodSerializer
    queryset = models.Period.objects.all().order_by('name')
    filterset_fields = get_fields(models.Period, exclude=DEFAULT_FIELDS)


class ResourcesFilteringViewSet(GeoViewSet):
    serializer_class = serializers.SiteCoordinatesSerializer

    def get_queryset(self):
        sites = models.Site.objects.all()

        # Retrieve query parameters
        resource_type = self.request.query_params.get('type')
        min_year = self.request.query_params.get('min_year')
        max_year = self.request.query_params.get('max_year')
        period_name = self.request.query_params.get('period_name')

        # Convert years to integers if provided
        min_year = int(min_year) if min_year else None
        max_year = int(max_year) if max_year else None
        
        # Map the resource type to the actual model
        resource_mapping = {
            'plank_boats': models.PlankBoats,
            'log_boats': models.LogBoats,
            'radiocarbon_dates': models.Radiocarbon,
            'individual_samples': models.IndividualObjects,
            'dna_samples': models.aDNA,
            'metal_analysis': models.MetalAnalysis,
            'landing_points': models.LandingPoints,
            # 'new_samples': models.NewSamples,
            'metalwork': models.Metalwork,
        }

        # If no filters are provided, return all sites
        if not (resource_type or min_year or max_year or period_name):
            return sites

        # If the date filter is the default, return all sites
        if min_year == -2450 and max_year == 50 and not resource_type:
            return sites
        
        # Construct the date filter
        date_filter = Q()
        if min_year:
            date_filter &= Q(Q(period__start_date__gte=min_year)  | Q(start_date__gte=min_year))
        if max_year:
            date_filter &= Q(Q(period__end_date__lte=max_year) | Q(end_date__lte=max_year))
        if period_name:
            date_filter &= Q(period__name=period_name)
        
        # Initialize an empty queryset for filtering
        filtered_sites = models.Site.objects.none() 

        # Handle filtering for a specific resource type
        if resource_type in resource_mapping:
            resource_model = resource_mapping[resource_type]
            resource_queryset = resource_model.objects.filter(date_filter)
            filtered_sites = sites.filter(id__in=resource_queryset.values_list('site_id', flat=True))

        # Handle filtering for all resource types when no specific type is given
        else:
            for resource_model in resource_mapping.values():
                resource_queryset = resource_model.objects.filter(date_filter)
                filtered_sites = filtered_sites.union(
                    sites.filter(id__in=resource_queryset.values_list('site_id', flat=True))
                )

        # Return the filtered queryset
        return filtered_sites

    # Fields and filters
    filterset_fields = get_fields(
        models.Site, exclude=DEFAULT_FIELDS + ['coordinates']
    )
    bbox_filter_field = 'coordinates'
    bbox_filter_include_overlapping = True
