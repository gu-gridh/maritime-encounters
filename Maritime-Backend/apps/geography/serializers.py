from rest_framework_gis.serializers import GeoFeatureModelSerializer
from maritime.utils import get_fields, DEFAULT_FIELDS
from .models import *

class ADM0Serializer(GeoFeatureModelSerializer):

    class Meta:
        model = ADM0
        fields = get_fields(ADM0, exclude=DEFAULT_FIELDS)
        geo_field = 'geometry'


class ADM4Serializer(GeoFeatureModelSerializer):

    class Meta:
        model = ADM4
        fields = get_fields(ADM4, exclude=DEFAULT_FIELDS)
        geo_field = 'geometry'


class ProvinceSerializer(GeoFeatureModelSerializer):

    class Meta:
        model = Province
        fields = get_fields(Province, exclude=DEFAULT_FIELDS)
        geo_field = 'geometry'

class ParishSerializer(GeoFeatureModelSerializer):

    class Meta:
        model = Parish
        fields = get_fields(Parish, exclude=DEFAULT_FIELDS)
        geo_field = 'geometry'

