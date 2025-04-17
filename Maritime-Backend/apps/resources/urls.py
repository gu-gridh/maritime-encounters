from django.urls import path, include
from rest_framework import routers
from . import views
import maritime.utils as utils

router = routers.DefaultRouter()
endpoint = utils.build_app_endpoint("resources")
documentation = utils.build_app_api_documentation("resources", endpoint)


router.register(rf'{endpoint}/site', views.SiteViewSet, basename='site')
router.register(rf'{endpoint}/geojson/site', views.SiteGeoViewSet, basename='site as geojson')
router.register(rf'{endpoint}/site_coordinates', views.SiteCoordinatesViewSet, basename='sites coordinates')
router.register(rf'{endpoint}/metal_analysis', views.MetalAnalysisViewSet, basename='metal analsyis')
# router.register(rf'{endpoint}/metalwork', views.MetalworkViewSet, basename='metalwork')
router.register(rf'{endpoint}/landing_points', views.LandingPointsViewSet, basename='landing points')
router.register(rf'{endpoint}/boat', views.BoatsViewSet, basename='boats')
router.register(rf'{endpoint}/lnhouses', views.HousesViewSet, basename='houses')

router.register(rf'{endpoint}/site_resources', views.SiteResourcesViewSet, basename='site resources')
router.register(rf'{endpoint}/order_periods', views.SearchPeriodsNames, basename='sort periods by their name')

# Api urls to download data both in csv and json format
router.register(rf'{endpoint}/data', views.DownloadViewSet, basename='Download data in csv and json format')

# Api urls to filter resources based on different criteria
router.register(rf'{endpoint}/search', views.ResourcesFilteringViewSet, basename='Filtering resources based on different criteria')


urlpatterns = [
    path('login/', views.TokenLoginView.as_view(), name='user-login'),
    path('', include(router.urls)),

    # Automatically generated views
    *utils.get_model_urls('resources', endpoint, 
        exclude=['site', 'metal_analysis', 'metalwork', 'boat', 'lnhouses']),

    *utils.get_model_urls('resources', f'{endpoint}', exclude=['site', 'metal_analysis', 'metalwork', 'boat', 'lnhouses']),
    *documentation
]