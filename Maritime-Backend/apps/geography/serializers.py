from rest_framework_gis.serializers import GeoFeatureModelSerializer
from maritime.utils import get_fields, DEFAULT_FIELDS
from .models import *

class CountrySerializer(GeoFeatureModelSerializer):

    class Meta:
        model = Country
        fields = get_fields(Country, exclude=DEFAULT_FIELDS)
        geo_field = 'geometry'


class LAUSerializer(GeoFeatureModelSerializer):

    class Meta:
        model = LAU
        fields = get_fields(LAU, exclude=DEFAULT_FIELDS)
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

