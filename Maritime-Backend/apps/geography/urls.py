from django.urls import path, include
from rest_framework import routers
from . import views
import maritime.utils as utils


router = routers.DefaultRouter()
endpoint = utils.build_app_endpoint("geography")
documentation = utils.build_app_api_documentation("geography", endpoint)


router = routers.DefaultRouter()
router.register(f'{endpoint}/country', views.ADM0ViewSet, basename='country')
router.register(f'{endpoint}/province', views.ProvinceViewSet, basename='province')
router.register(f'{endpoint}/parish', views.ParishViewSet, basename='parish')
router.register(f'{endpoint}/lau', views.ADM4ViewSet, basename='lau')

urlpatterns = [
    path('', include(router.urls)),

    *documentation,
]