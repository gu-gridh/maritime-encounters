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
from django.db.models import Q, Exists, OuterRef
from maritime.abstract.views import DynamicDepthViewSet, GeoViewSet
from maritime.abstract.models import get_fields, DEFAULT_FIELDS, DEFAULT_EXCLUDE

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.decorators import action
from rest_framework.negotiation import DefaultContentNegotiation
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


class RadioCarbonViewSet(DynamicDepthViewSet):
    serializer_class = serializers.RadioCarbonSerializer
    queryset = models.Radiocarbon.objects.all()
    filterset_fields = get_fields(models.Radiocarbon, exclude=DEFAULT_FIELDS)
    search_fields = ['site__name', 'lab_code']
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
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def _get_safe_prefetch_fields(self, model):
        """Get safe prefetch fields - manually defined for each model"""
        prefetch_map = {
            'Boat': ['components'],
            'IndividualObjects': ['material', 'period'],
            'Radiocarbon': [],  # No prefetch needed
            'aDNA': [],
            'MetalAnalysis': [],  # Skip problematic prefetch
            'LandingPoints': [],
            'NewSamples': [],
            'LNHouses': [],
        }
        return prefetch_map.get(model.__name__, [])
    
    def _get_safe_select_fields(self, model):
        """Get safe select_related fields - manually defined for each model"""
        select_map = {
            'Boat': ['site', 'period', 'location'],
            'IndividualObjects': ['site', 'museum', 'accession_number', 'object_type', 'form', 'variant', 'context'],
            'Radiocarbon': ['site', 'period', 'dating_method'],
            'aDNA': ['site'],
            'MetalAnalysis': ['site'],
            'LandingPoints': ['site'],
            'NewSamples': ['site'],
            'LNHouses': ['site'],
        }
        return select_map.get(model.__name__, ['site'])
    
    def list(self, request):
        site_id = request.GET.get("site_id")
        
        if not site_id:
            return Response({"error": "site_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            site = Site.objects.get(id=site_id)
        except Site.DoesNotExist:
            return Response({"error": "Site not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Model configurations with their serializers
        model_configs = [
            (Boat, BoatSerializer, 'boats'),
            (Radiocarbon, RadioCarbonSerializer, 'radiocarbon_dates'),
            (IndividualObjects, IndivdualObjectSerializer, 'individual_samples'),
            (aDNA, aDNASerializer, 'dna_samples'),
            (MetalAnalysis, MetalAnalysisSerializer, 'metal_analysis'),
            (LandingPoints, LandingPointsSerializer, 'landing_points'),
            (NewSamples, NewSamplesSerializer, 'new_samples'),
            (LNHouses, LNHouseSerializer, 'lnhouses'),
        ]
        
        data = {}
        
        for model, serializer_class, key in model_configs:
            try:
                # Get safe fields for this specific model
                select_fields = self._get_safe_select_fields(model)
                prefetch_fields = self._get_safe_prefetch_fields(model)
                
                # Build queryset with optimization
                queryset = model.objects.filter(site=site)
                
                if select_fields:
                    queryset = queryset.select_related(*select_fields)
                
                if prefetch_fields:
                    queryset = queryset.prefetch_related(*prefetch_fields)
                
                # Serialize data
                data[key] = serializer_class(queryset, many=True).data
                
            except Exception as e:
                # Log the error but continue with other models
                print(f"Error processing {model.__name__}: {e}")
                data[key] = []
        
        return Response(data, status=status.HTTP_200_OK)

class ResourcesFilteringViewSet(GeoViewSet):
    serializer_class = serializers.SiteCoordinatesSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]  
    permission_classes = [IsAuthenticated]

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
        }

        # Early return for no filters
        if not (resource_type or min_year or max_year or period_name):
            # If no filters are applied, return all sites that have at least one resource attached to them
            sites = sites.filter(
                Q(boat__isnull=False) |
                Q(radiocarbon__isnull=False) |
                Q(individualobjects__isnull=False) |
                Q(adna__isnull=False) |
                Q(metalanalysis__isnull=False) |
                Q(landingpoints__isnull=False) |
                Q(newsamples__isnull=False) |
                Q(lnhouses__isnull=False)
            ).distinct()

            return sites

        # Special case: fallback condition
        is_full_range = min_year == -2450 and max_year == 50
        if is_full_range and not resource_type:
            return sites

        # Determine models to check - supports comma-separated resource types
        models_to_check = []
        
        if resource_type:
            # Split by comma and clean up whitespace
            resource_types = [rt.strip() for rt in resource_type.split(',') if rt.strip()]
            
            # Get models for valid resource types
            for rt in resource_types:
                if rt in resource_mapping:
                    models_to_check.append(resource_mapping[rt])
                else:
                    # Log warning for invalid resource type
                    print(f"Warning: Unknown resource type '{rt}' ignored")
            
            # If no valid resource types found, use all models as fallback
            if not models_to_check:
                print(f"Warning: No valid resource types in '{resource_type}', using all models")
                models_to_check = list(resource_mapping.values())
        else:
            # No resource type specified, use all models
            models_to_check = list(resource_mapping.values())

        # **Key Optimization: Use database-level filtering with EXISTS subqueries**
        site_filter = Q()
        
        for model in models_to_check:
            model_fields = [field.name for field in model._meta.get_fields()]
            model_filter = Q()
            
            # Build filter for this specific model
            if 'start_date' in model_fields or 'end_date' in model_fields:
                if not is_full_range:
                    if min_year:
                        model_filter &= Q(start_date__gte=min_year)
                    if max_year:
                        model_filter &= Q(end_date__lte=max_year)
                    if period_name:
                        model_filter &= Q(period__name=period_name)
                
            elif 'period' in model_fields:
                if not is_full_range:
                    # Build period-based filter
                    period_filter = Q()
                    if min_year:
                        period_filter &= Q(period__start_date__gte=min_year)
                    if max_year:
                        period_filter &= Q(period__end_date__lte=max_year)
                    if period_name:
                        period_filter &= Q(period__name=period_name)
                    
                    # Only include records with valid period dates
                    model_filter &= (
                        period_filter & 
                        Q(period__start_date__isnull=False) & 
                        Q(period__end_date__isnull=False)
                    )
            
            # **FIXED: Use imported OuterRef and Exists instead of models.OuterRef/models.Exists**
            if model_filter or is_full_range:
                subquery = model.objects.filter(site=OuterRef('pk'))  # Changed from models.OuterRef
                if not is_full_range and model_filter:
                    subquery = subquery.filter(model_filter)
                
                site_filter |= Exists(subquery)  # Changed from models.Exists

        # Apply the combined filter
        if site_filter:
            sites = sites.filter(site_filter)

        return sites

    filterset_fields = get_fields(
        models.Site, exclude=DEFAULT_FIELDS + ['coordinates']
    )
    bbox_filter_field = 'coordinates'
    bbox_filter_include_overlapping = True

# Viweset to download data for selected area based on parameters and bounding box in search function
# Data should provided in csv and json format
# We can provide a  parameter to select the type of data to downloadfrom io import BytesIO
class DownloadViewSet(viewsets.ViewSet):
    # Allow token via header, session cookie, or ?token= query parameter (for file downloads via <a> tags)
    class QueryParamTokenAuthentication(TokenAuthentication):
        def authenticate(self, request):
            q_token = request.query_params.get('token')
            if q_token:
                try:
                    return self.authenticate_credentials(q_token)
                except Exception:
                    return None  # Fall through to other authenticators
            return super().authenticate(request)

    class IgnoreClientContentNegotiation(DefaultContentNegotiation):
        """Always select the first renderer (ignore Accept header to prevent 406)."""
        def select_renderer(self, request, renderers, format_suffix):
            return renderers[0], renderers[0].media_type

    authentication_classes = [QueryParamTokenAuthentication, SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    content_negotiation_class = IgnoreClientContentNegotiation
    
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
            return self._export_csv_zip(queryset_list)

        return Response({'error': 'Invalid format'}, status=400)
    
    def _export_csv_zip(self, data):
        """Internal helper to generate ZIP of CSVs."""
        if not data:
            return Response({}, status=400)
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for model_name, rows in data.items():
                if not rows:
                    continue
                csv_buffer = io.StringIO()
                csv_writer = csv.DictWriter(csv_buffer, fieldnames=rows[0].keys())
                csv_writer.writeheader()
                for row in rows:
                    csv_writer.writerow({key: str(value) if value is not None else "" for key, value in row.items()})
                zip_file.writestr(f"{model_name}.csv", csv_buffer.getvalue())
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.read(), content_type="application/zip")
        response['Content-Disposition'] = 'attachment; filename="exported_data.zip"'
        return response

    @action(detail=False, methods=['get'])
    def export_csv(self, request, *args, **kwargs):
        """Action endpoint to export CSV (same filtering as list). Accepts ?token=TOKEN."""
        # Reuse logic by replicating core of list (could be further refactored)
        resource_type = request.GET.get('type')
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
        }
        selected_models = [resource_mapping[resource_type]] if resource_type in resource_mapping else resource_mapping.values()
        queryset_list = {}
        is_full_range = (min_year == -2450 and max_year == 50)
        for model in selected_models:
            queryset = model.objects.all()
            if bbox:
                try:
                    min_x, min_y, max_x, max_y = map(float, bbox.split(','))
                    bbox_polygon = Polygon.from_bbox((min_x, min_y, max_x, max_y))
                    queryset = queryset.filter(site__coordinates__within=bbox_polygon)
                except Exception:
                    pass
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
                    queryset = queryset.filter(
                        date_filter_period & Q(period__start_date__isnull=False) & Q(period__end_date__isnull=False)
                    )
            if queryset.exists():
                queryset_list[model.__name__] = list(queryset.values())
        return self._export_csv_zip(queryset_list)
    

# Add new viewset when you select multiple resources, it resturns common sites have the same resources
# We can filter them also based on period  
class CommonSitesViewSet(GeoViewSet):
    serializer_class = serializers.SiteCoordinatesSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]  
    permission_classes = [IsAuthenticated]  

    def get_queryset(self):
        # Use 'type' instead of 'types' to match your URL
        resources = self.request.query_params.get('type')
        min_year = self.request.query_params.get('min_year')
        max_year = self.request.query_params.get('max_year')


        min_year = int(min_year) if min_year else None
        max_year = int(max_year) if max_year else None
        
        # Handle empty resources parameter
        if not resources:
            return models.Site.objects.none()
            
        resource_list = [r.strip() for r in resources.split(',') if r.strip()]

        resource_mapping = {
            'boats': models.Boat,
            'radiocarbon_dates': models.Radiocarbon,
            'individual_samples': models.IndividualObjects,
            'dna_samples': models.aDNA,
            'metal_analysis': models.MetalAnalysis,
            'landing_points': models.LandingPoints,
            'new_samples': models.NewSamples,
            'lnhouses': models.LNHouses,
        }

        selected_models = [resource_mapping[r] for r in resource_list if r in resource_mapping]
        
        if not selected_models:
            return models.Site.objects.none()
        
        field_mapping = {
            'Boat': 'boat',
            'Radiocarbon': 'radiocarbon', 
            'IndividualObjects': 'individualobjects',
            'aDNA': 'adna',
            'MetalAnalysis': 'metalanalysis',
            'LandingPoints': 'landingpoints',
            'NewSamples': 'newsamples',
            'LNHouses': 'lnhouses',
        }

        # Start with all sites
        sites = models.Site.objects.all()
        
        # Apply AND filter: site must have ALL selected resource types
        for model in selected_models:
            field_name = field_mapping.get(model.__name__)
            if field_name:
                sites = sites.filter(**{f"{field_name}__isnull": False})

        sites = sites.distinct()

        return sites
    
    filterset_fields = get_fields(
        models.Site, exclude=DEFAULT_FIELDS + ['coordinates']
    )
    bbox_filter_field = 'coordinates'
    bbox_filter_include_overlapping = True
