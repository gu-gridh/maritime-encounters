import csv
import io
import zipfile
from django.http import HttpResponse, JsonResponse
from  .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from . import models, serializers
from django.db.models import Q
from maritime.abstract.views import DynamicDepthViewSet, GeoViewSet
from maritime.abstract.models import get_fields, DEFAULT_FIELDS, DEFAULT_EXCLUDE

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from rest_framework.authentication import TokenAuthentication

class ProtectedAPIView(APIView):
    permission_classes = []  # Only authenticated users can access

    def get(self, request):
        token_key = request.headers.get('Authorization').split(' ')[1]  # Extract token
        try:
            token = Token.objects.get(key=token_key)
            print(token.user)  # Check the associated user
            return Response({'message': 'This is a protected API'})
        except Token.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        
class TokenLoginView(APIView):
    permission_classes = []  

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class SiteViewSet(DynamicDepthViewSet):
    serializer_class = serializers.SiteGeoSerializer
    queryset = models.Site.objects.all()

    filterset_fields = get_fields(
        models.Site, exclude=DEFAULT_FIELDS + ['coordinates'])
    search_fields = ['placename']
    bbox_filter_field = 'coordinates'
    bbox_filter_include_overlapping = True
    authentication_classes = [TokenAuthentication]  
    permission_classes = [IsAuthenticated]

class SiteCoordinatesViewSet(GeoViewSet):
    serializer_class = serializers.SiteCoordinatesSerializer
    queryset = models.Site.objects.all().order_by('id')
    filterset_fields = get_fields(
        models.Site, exclude=DEFAULT_FIELDS + ['coordinates'])
    bbox_filter_field = 'coordinates'
    bbox_filter_include_overlapping = True
    authentication_classes = [TokenAuthentication]  
    permission_classes = [IsAuthenticated]  # Explicitly require authentication

class SiteGeoViewSet(GeoViewSet):

    serializer_class = serializers.SiteGeoSerializer
    queryset = models.Site.objects.all()

    filterset_fields = get_fields(
        models.Site, exclude=DEFAULT_FIELDS + ['coordinates'])
    search_fields = ['placename', 'name']
    bbox_filter_field = 'coordinates'
    bbox_filter_include_overlapping = True
    authentication_classes = [TokenAuthentication]  
    permission_classes = [IsAuthenticated]  # Explicitly require authentication

class MetalAnalysisViewSet(DynamicDepthViewSet):
    serializer_class = serializers.MetalAnalysisSerializer
    queryset = models.MetalAnalysis.objects.all()
    filterset_fields = get_fields(models.MetalAnalysis, exclude=DEFAULT_FIELDS)
    search_fields = ['site__name']
    authentication_classes = [TokenAuthentication]  
    permission_classes = [IsAuthenticated]  # Explicitly require authentication

class MetalworkViewSet(DynamicDepthViewSet):
    serializer_class = serializers.MetalworkSerializer
    queryset = models.Metalwork.objects.all()
    filterset_fields = get_fields(models.Metalwork, exclude=DEFAULT_EXCLUDE+DEFAULT_FIELDS+['orig_coords'])
    search_fields = ['site__name', 'entry_number']
    authentication_classes = [TokenAuthentication]  
    permission_classes = [IsAuthenticated]  # Explicitly require authentication

class LandingPointsViewSet(DynamicDepthViewSet):
    serializer_class = serializers.LandingPointsSerializer
    queryset = models.LandingPoints.objects.all()
    filterset_fields = get_fields(models.LandingPoints, exclude=DEFAULT_FIELDS)
    search_fields = ['site__name']
    authentication_classes = [TokenAuthentication]  
    permission_classes = [IsAuthenticated]  # Explicitly require authentication

class SiteResourcesViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]  # Add TokenAuthentication here
    
    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticated()]  # Require authentication for 'list' action
        return [AllowAny()]  # Allow any access for other actions (if any)
    
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
    authentication_classes = [TokenAuthentication]  
    permission_classes = [IsAuthenticated]  # Explicitly require authentication


class ResourcesFilteringViewSet(GeoViewSet):
    serializer_class = serializers.SiteCoordinatesSerializer

    def get_queryset(self):
        sites = models.Site.objects.all()

        resource_type = self.request.query_params.get('type')
        min_year = self.request.query_params.get('min_year')
        max_year = self.request.query_params.get('max_year')
        period_name = self.request.query_params.get('period_name')

        min_year = int(min_year) if min_year else None
        max_year = int(max_year) if max_year else None

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

        if not (resource_type or min_year or max_year or period_name):
            return sites

        if min_year == -2450 and max_year == 50 and not resource_type:
            return sites

        date_filter = Q()
        if min_year:
            date_filter &= Q(start_date__gte=min_year)
        if max_year:
            date_filter &= Q(end_date__lte=max_year)
        if period_name:
            date_filter &= Q(period__name=period_name)

        date_filter_period = Q()
        if min_year:
            date_filter_period &= Q(period__start_date__gte=min_year)
        if max_year:
            date_filter_period &= Q(period__end_date__lte=max_year)
        if period_name:
            date_filter_period &= Q(period__name=period_name)

        # Use a set to collect site IDs
        site_ids = set()

        def collect_site_ids(model, filter_q):
            return model.objects.filter(filter_q).values_list('site_id', flat=True)

        # Filter by specific resource type
        if resource_type in resource_mapping:
            resource_model = resource_mapping[resource_type]
            model_fields = [field.name for field in resource_model._meta.get_fields()]

            if 'start_date' in model_fields or 'end_date' in model_fields:
                site_ids.update(collect_site_ids(resource_model, date_filter))
            elif 'period' in model_fields:
                site_ids.update(collect_site_ids(resource_model, date_filter_period))
            else:
                site_ids.update(resource_model.objects.values_list('site_id', flat=True))

        # Filter across all resources if no type is specified
        else:
            for resource_model in resource_mapping.values():
                model_fields = [field.name for field in resource_model._meta.get_fields()]

                if 'start_date' in model_fields or 'end_date' in model_fields:
                    site_ids.update(collect_site_ids(resource_model, date_filter))
                elif 'period' in model_fields:
                    site_ids.update(collect_site_ids(resource_model, date_filter_period))
                else:
                    site_ids.update(resource_model.objects.values_list('site_id', flat=True))

        # Final filter with no union or filter chaining
        return sites.filter(id__in=site_ids)
        # Fields and filters
        
    filterset_fields = get_fields(
        models.Site, exclude=DEFAULT_FIELDS + ['coordinates']
    )
    bbox_filter_field = 'coordinates'
    bbox_filter_include_overlapping = True
    authentication_classes = [TokenAuthentication]  
    permission_classes = [IsAuthenticated]  # Explicitly require authentication

# Viweset to download data for selected area based on parameters and bounding box in search function
# Data should provided in csv and json format
# We can provide a  parameter to select the type of data to downloadfrom io import BytesIO
class DownloadViewSet(viewsets.ViewSet):
    # authentication_classes = [TokenAuthentication]  # Add TokenAuthentication here
    
    # def get_permissions(self):
    #     if self.action == 'list':
    #         return [IsAuthenticated()]  # Require authentication for 'list' action
    #     return [AllowAny()]  # Allow any access for other actions (if any)

    def list(self, request):
        resource_type = request.GET.get('type')
        output_format = request.GET.get('download_format', 'json')
        min_year = request.GET.get('min_year')
        max_year = request.GET.get('max_year')
        bbox = request.GET.get('bbox')

        min_year = int(min_year) if min_year else None
        max_year = int(max_year) if max_year else None

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

        selected_models = [resource_mapping[resource_type]] if resource_type in resource_mapping else resource_mapping.values()
        queryset_list = {}

        for model in selected_models:
            queryset = model.objects.all()

            # Apply filters
            if bbox:
                try:
                    min_x, min_y, max_x, max_y = map(float, bbox.split(','))
                    queryset = queryset.filter(coordinates__contained_in=((min_x, min_y), (max_x, max_y)))
                except ValueError:
                    return Response({'error': 'Invalid bbox format. Use min_x,min_y,max_x,max_y'}, status=400)

            date_filter = Q()
            if min_year:
                date_filter &= Q(start_date__gte=min_year)
            if max_year:
                date_filter &= Q(end_date__lte=max_year)

            date_filter_period = Q()
            if min_year:
                date_filter_period &= Q(period__start_date__gte=min_year)
            if max_year:
                date_filter_period &= Q(period__end_date__lte=max_year)

            model_fields = [field.name for field in model._meta.get_fields()]
            if 'start_date' in model_fields or 'end_date' in model_fields:
                queryset = queryset.filter(date_filter)
            elif 'period' in model_fields:
                queryset = queryset.filter(date_filter_period)

            if queryset.exists():
                queryset_list[model.__name__] = list(queryset.values())

        # Return JSON if requested
        if output_format == 'json':
            return JsonResponse(queryset_list, safe=False)

        # Return separate CSV files per model
        if output_format == 'csv':
            return self.export_csv(queryset_list)

        return Response({'error': 'Invalid format'}, status=400)

    def export_csv(self, data):
        """
        Exports multiple CSV files for each model in the dataset.
        """
        if not data:
            return Response({'error': 'No data available for export'}, status=400)

        # Create a ZIP file in memory
        zip_buffer = io.BytesIO()

        # Creating the zip file
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for model_name, rows in data.items():
                if not rows:
                    continue

                # Create an in-memory CSV file (in UTF-8 encoding)
                csv_buffer = io.StringIO()
                csv_writer = csv.DictWriter(csv_buffer, fieldnames=rows[0].keys())
                csv_writer.writeheader()

                for row in rows:
                    # Write each row to the CSV
                    csv_writer.writerow({key: str(value) if value is not None else "" for key, value in row.items()})

                # Move to the start of the StringIO buffer before writing it to the ZIP file
                zip_file.writestr(f"{model_name}.csv", csv_buffer.getvalue())

        # Prepare response as a ZIP file
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.read(), content_type="application/zip")
        response['Content-Disposition'] = 'attachment; filename="exported_data.zip"'
        return response