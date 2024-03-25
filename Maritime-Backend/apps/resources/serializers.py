from maritime.abstract.serializers import DynamicDepthSerializer, GenericSerializer
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from . import models
from maritime.utils import get_fields, DEFAULT_FIELDS
from .models import *



class SiteSerializer(DynamicDepthSerializer):

    class Meta:
        model = Site
        fields = ['id']+get_fields(Site, exclude=DEFAULT_FIELDS)

class SiteGeoSerializer(GeoFeatureModelSerializer):

    class Meta:
        model = Site
        fields = ['id']+get_fields(Site, exclude=DEFAULT_FIELDS)
        geo_field = 'coordinates'


class MetalAnalysisSerializer(DynamicDepthSerializer):

    class Meta:
        model = MetalAnalysis
        fields = ['id']+get_fields(MetalAnalysis, exclude=DEFAULT_FIELDS)