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
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.decorators import action
from django.contrib.gis.geos import Polygon
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.middleware.csrf import get_token
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
import logging

logger = logging.getLogger(__name__)

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

@method_decorator(csrf_exempt, name='dispatch')        
class TokenLoginView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to access login
    authentication_classes = []  # Disable authentication for login

    def post(self, request):
        # Debug logging to trace 403 issues (whether view is reached)
        logger.info("TokenLoginView POST reached. Headers=%s", dict(request.headers))
        logger.info("Content-Type=%s", request.content_type)
        logger.info("Body raw=%s", request.body[:500])
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            logger.warning("Missing username or password in request data")
            return Response({'error': 'Missing credentials'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            logger.info("User %s authenticated successfully (token created=%s)", user.username, created)
            return Response({'token': token.key, 'user': user.username})
        logger.warning("Authentication failed for username=%s", username)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class GetTokenView(APIView):
    """
    View to get token for already authenticated users (e.g., from admin login)
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]  # Support both token and session auth

    def get(self, request):
        # If user is authenticated via session, provide them with a token
        token, created = Token.objects.get_or_create(user=request.user)
        return Response({
            'token': token.key,
            'user': request.user.username,
            'created': created
        })

class SessionToTokenView(APIView):
    """
    Convert session authentication to token authentication
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_authenticated:
            token, created = Token.objects.get_or_create(user=request.user)
            return Response({
                'token': token.key,
                'user': request.user.username,
                'is_staff': request.user.is_staff,
                'is_superuser': request.user.is_superuser
            })
        return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

def auth_bridge_view(request):
    """
    Simple HTML page to help users get their API token after admin login
    """
    return render(request, 'auth_bridge.html')

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Simple function-based login view
    """
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)

    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': user.username})
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

def csrf_token_view(request):
    """
    Get CSRF token for frontend
    """
    return JsonResponse({'csrfToken': get_token(request)})

class SiteViewSet(DynamicDepthViewSet):
    serializer_class = serializers.SiteGeoSerializer
    queryset = models.Site.objects.all()

    filterset_fields = get_fields(
        models.Site, exclude=DEFAULT_FIELDS + ['coordinates'])
    search_fields = ['placename']
    bbox_filter_field = 'coordinates'
    bbox_filter_include_overlapping = True
    authentication_classes = [SessionAuthentication, TokenAuthentication]  
    permission_classes = [IsAuthenticated]

class SiteCoordinatesViewSet(GeoViewSet):
    serializer_class = serializers.SiteCoordinatesSerializer
    queryset = models.Site.objects.all().order_by('id')
    filterset_fields = get_fields(
        models.Site, exclude=DEFAULT_FIELDS + ['coordinates'])
    bbox_filter_field = 'coordinates'
    bbox_filter_include_overlapping = True
    authentication_classes = [SessionAuthentication, TokenAuthentication]  
    permission_classes = [IsAuthenticated]  # Explicitly require authentication

class SiteGeoViewSet(GeoViewSet):

    serializer_class = serializers.SiteGeoSerializer
    queryset = models.Site.objects.all()

    filterset_fields = get_fields(
        models.Site, exclude=DEFAULT_FIELDS + ['coordinates'])
    search_fields = ['placename', 'name']
    bbox_filter_field = 'coordinates'
    bbox_filter_include_overlapping = True
    authentication_classes = [SessionAuthentication, TokenAuthentication]  
    permission_classes = [IsAuthenticated]  # Explicitly require authentication

class MetalAnalysisViewSet(DynamicDepthViewSet):
    serializer_class = serializers.MetalAnalysisSerializer
    queryset = models.MetalAnalysis.objects.all()
    filterset_fields = get_fields(models.MetalAnalysis, exclude=DEFAULT_FIELDS)
    search_fields = ['site__name']
    authentication_classes = [SessionAuthentication, TokenAuthentication]  
    permission_classes = [IsAuthenticated]  # Explicitly require authentication

class MetalworkViewSet(DynamicDepthViewSet):
    serializer_class = serializers.MetalworkSerializer
    queryset = models.Metalwork.objects.all()
    filterset_fields = get_fields(models.Metalwork, exclude=DEFAULT_EXCLUDE+DEFAULT_FIELDS+['orig_coords'])
    search_fields = ['site__name', 'entry_number']
    authentication_classes = [SessionAuthentication, TokenAuthentication]  
    permission_classes = [IsAuthenticated]  # Explicitly require authentication

class LandingPointsViewSet(DynamicDepthViewSet):
    serializer_class = serializers.LandingPointsSerializer
    queryset = models.LandingPoints.objects.all()
    filterset_fields = get_fields(models.LandingPoints, exclude=DEFAULT_FIELDS)
    search_fields = ['site__name']
    authentication_classes = [SessionAuthentication, TokenAuthentication]  
    permission_classes = [IsAuthenticated]  # Explicitly require authentication


class HousesViewSet(DynamicDepthViewSet):
    serializer_class = serializers.LNHouseSerializer
    queryset = models.LNHouses.objects.all()
    filterset_fields = get_fields(models.LNHouses, exclude=DEFAULT_FIELDS)
    search_fields = ['site__name']
    authentication_classes = [SessionAuthentication, TokenAuthentication]  
    permission_classes = [IsAuthenticated]  # Explicitly require authentication

class BoatsViewSet(DynamicDepthViewSet):
    serializer_class = BoatSerializer
    queryset = (
        Boat.objects.all()
        .select_related("site", "location", "period")  # ForeignKey relations
        .prefetch_related(
            "components",  # Ensure components are prefetched properly
            "components__component",  # Fetch related BoatComponent objects in one go
        )
    )
    filterset_fields = get_fields(Boat, exclude=DEFAULT_FIELDS)

class SearchPeriodsNames(DynamicDepthViewSet):
    serializer_class = serializers.PeriodSerializer
    queryset = models.Period.objects.all().order_by('name')
    filterset_fields = get_fields(models.Period, exclude=DEFAULT_FIELDS)
    authentication_classes = [SessionAuthentication, TokenAuthentication]  
    permission_classes = [IsAuthenticated]  # Explicitly require authentication

class SiteResourcesViewSet(viewsets.ViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]  # Add TokenAuthentication here
    
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
            'boats': BoatSerializer(Boat.objects.filter(site=site), many=True).data,
            'radiocarbon_dates': RadiocarbonSerializer(Radiocarbon.objects.filter(site=site), many=True).data,
            'individual_samples': IndivdualObjectSerializer(IndividualObjects.objects.filter(site=site), many=True).data,
            'dna_samples': aDNASerializer(aDNA.objects.filter(site=site), many=True).data,
            'metal_analysis': MetalAnalysisSerializer(MetalAnalysis.objects.filter(site=site), many=True).data,
            'landing_points': LandingPointsSerializer(LandingPoints.objects.filter(site=site), many=True).data,
            'new_samples': NewSamplesSerializer(NewSamples.objects.filter(site=site), many=True).data,
            'lnhouses': LNHouseSerializer(LNHouses.objects.filter(site=site), many=True).data,
            # 'metalwork': MetalworkSerializer(Metalwork.objects.filter(location__site=site), many=True).data,
        }

        return Response(data, status=status.HTTP_200_OK)

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
            'boats': models.Boat,
            'radiocarbon_dates': models.Radiocarbon,
            'individual_samples': models.IndividualObjects,
            'dna_samples': models.aDNA,
            'metal_analysis': models.MetalAnalysis,
            'landing_points': models.LandingPoints,
            'new_samples': models.NewSamples,
            'lnhouses': models.LNHouses,
            # 'metalwork': models.Metalwork,
        }

        # If no meaningful filter is provided, return everything
        if not (resource_type and (min_year or max_year) or period_name):
            return sites

        # Special case: fallback condition
        if min_year == -2450 and max_year == 50 and not resource_type:
            return sites

        # Filters for models with start_date/end_date
        date_filter = Q()
        if min_year:
            date_filter &= Q(start_date__gte=min_year)
        if max_year:
            date_filter &= Q(end_date__lte=max_year)
        if period_name:
            date_filter &= Q(period__name=period_name)

        # Filters for models with period field
        date_filter_period = Q()
        if min_year:
            date_filter_period &= Q(period__start_date__gte=min_year)
        if max_year:
            date_filter_period &= Q(period__end_date__lte=max_year)
        if period_name:
            date_filter_period &= Q(period__name=period_name)

        if min_year and max_year:
            date_filter_period = Q()
            Q(period__start_date__isnull=True) | Q(period__end_date__isnull=True)

        site_ids = set()

        def collect_site_ids(model, filter_q):
            return model.objects.filter(filter_q).values_list('site_id', flat=True)

        # Decide if this is the "full range" fallback
        is_full_range = min_year == -2450 and max_year == 50

        models_to_check = (
            [resource_mapping[resource_type]] if resource_type in resource_mapping
            else resource_mapping.values()
        )

        for model in models_to_check:
            model_fields = [field.name for field in model._meta.get_fields()]

            if 'start_date' in model_fields or 'end_date' in model_fields:
                # If full range, include everything; otherwise filter
                if is_full_range:
                    site_ids.update(model.objects.values_list('site_id', flat=True))
                else:
                    site_ids.update(collect_site_ids(model, date_filter))

            elif 'period' in model_fields:
                if is_full_range:
                    # Include all, even if period dates are null
                    site_ids.update(model.objects.values_list('site_id', flat=True))
                else:
                    # Only include those with valid start and end dates
                    filter_with_valid_dates = date_filter_period & Q(period__start_date__isnull=False) & Q(period__end_date__isnull=False)
                    site_ids.update(collect_site_ids(model, filter_with_valid_dates))

            else:
                site_ids.update(model.objects.values_list('site_id', flat=True))

        return sites.filter(id__in=site_ids)

    filterset_fields = get_fields(
        models.Site, exclude=DEFAULT_FIELDS + ['coordinates']
    )
    bbox_filter_field = 'coordinates'
    bbox_filter_include_overlapping = True
    authentication_classes = [SessionAuthentication, TokenAuthentication]  
    permission_classes = [IsAuthenticated]  # Explicitly require authentication

# Viweset to download data for selected area based on parameters and bounding box in search function
# Data should provided in csv and json format
# We can provide a  parameter to select the type of data to downloadfrom io import BytesIO
class DownloadViewSet(viewsets.ViewSet):

    authentication_classes = [SessionAuthentication, TokenAuthentication]  # Add TokenAuthentication here
    
    def get_permissions(self):
        """
        Determine the permissions required for different actions.

        Returns:
            list: A list of permission classes. If the action is 'list' or 'export_csv',
                  it returns a list containing IsAuthenticated permission. For other actions,
                  it returns a list containing AllowAny permission.
        """
        if self.action in ['list', 'export_csv']:
            return [IsAuthenticated()]  # Require authentication for 'list' and 'export_csv' actions
        return [AllowAny()]  # Allow any access for other actions (if any)
    
    def list(self, request):
        resource_type = request.GET.get('type')
        output_format = request.GET.get('download_format', 'json')
        min_year = request.GET.get('min_year')
        max_year = request.GET.get('max_year')
        bbox = request.GET.get('in_bbox')

        min_year = int(min_year) if min_year else None
        max_year = int(max_year) if max_year else None

        resource_mapping = {
            'boats': models.Boat,
            'radiocarbon_dates': models.Radiocarbon,
            'individual_samples': models.IndividualObjects,
            'dna_samples': models.aDNA,
            'metal_analysis': models.MetalAnalysis,
            'landing_points': models.LandingPoints,
            'new_samples': models.NewSamples,
            'lnhouses': models.LNHouses,
            # 'metalwork': models.Metalwork,
        }

        selected_models = [resource_mapping[resource_type]] if resource_type in resource_mapping else resource_mapping.values()
        queryset_list = {}

        is_full_range = (min_year == -2450 and max_year == 50)

        for model in selected_models:
            queryset = model.objects.all()

            # Apply filters
            if bbox:
                min_x, min_y, max_x, max_y = map(float, bbox.split(','))
                bbox_polygon = Polygon.from_bbox((min_x, min_y, max_x, max_y))
                queryset = queryset.filter(site__coordinates__within=bbox_polygon)  # Correct lookup for GeoDjango

            model_fields = [field.name for field in model._meta.get_fields()]
            if not is_full_range:
                if 'start_date' in model_fields or 'end_date' in model_fields:
                    date_filter = Q()
                    if min_year:
                        date_filter &= Q(start_date__gte=min_year)
                    if max_year:
                        date_filter &= Q(end_date__lte=max_year)

                    queryset = queryset.filter(date_filter)

                elif 'period' in model_fields:
                    date_filter_period = Q()
                    if min_year:
                        date_filter_period &= Q(period__start_date__gte=min_year)
                    if max_year:
                        date_filter_period &= Q(period__end_date__lte=max_year)

                    # Only include rows where both period dates are not null
                    queryset = queryset.filter(
                        date_filter_period &
                        Q(period__start_date__isnull=False) &
                        Q(period__end_date__isnull=False)
                    )

            # Otherwise, in full range case: skip filtering
            # (queryset is already all(), possibly filtered by bbox)

            if queryset.exists():
                queryset_list[model.__name__] = list(queryset.values())

        # Return JSON if requested
        if output_format == 'json':
            return JsonResponse(queryset_list, safe=False)

        # Return separate CSV files per model
        if output_format == 'csv':
            return self.export_csv(queryset_list)

        return Response({'error': 'Invalid format'}, status=400)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def export_csv(self, data):

        """
        Exports multiple CSV files for each model in the dataset.
        """
        if not data:
            return Response({}, status=400)

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
    
