from django.urls import path, include
from rest_framework import routers
from . import views
import maritime.utils as utils

router = routers.DefaultRouter()
endpoint = utils.build_app_endpoint("resources")
documentation = utils.build_app_api_documentation("resources", endpoint)

urlpatterns = [
    path('', include(router.urls)),

    # Automatically generated views
    *utils.get_model_urls('resources', endpoint, 
        exclude=[]),

    *utils.get_model_urls('resources', f'{endpoint}', exclude=[]),
    *documentation
]