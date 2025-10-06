from maritime.abstract.serializers import DynamicDepthSerializer, GenericSerializer
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from . import models
from maritime.utils import get_fields, DEFAULT_FIELDS
from .models import *
from apps.geography.models import *
import math

# ADMs serializers: We need to exclude PolygonField from the serializer to make it faster
class ExcludePloygonFieldADM0Serializer(DynamicDepthSerializer):
    class Meta:
        model = ADM0
        fields = ['id']+get_fields(ADM0, exclude=DEFAULT_FIELDS+['geometry'])


class ExcludePloygonFieldADM1Serializer(DynamicDepthSerializer):
    class Meta:
        model = ADM1
        fields = ['id']+get_fields(ADM1, exclude=DEFAULT_FIELDS+['geometry'])


class ExcludePloygonFieldADM2Serializer(DynamicDepthSerializer):
    class Meta:
        model = ADM2
        fields = ['id']+get_fields(ADM2, exclude=DEFAULT_FIELDS+['geometry'])


class ExcludePloygonFieldADM3Serializer(DynamicDepthSerializer):
    class Meta:
        model = ADM3
        fields = ['id']+get_fields(ADM3, exclude=DEFAULT_FIELDS+['geometry'])


class ExcludePloygonFieldADM4Serializer(DynamicDepthSerializer):
    class Meta:
        model = ADM4
        fields = ['id']+get_fields(ADM4, exclude=DEFAULT_FIELDS+['geometry'])


class ExcludePloygonFieldProvinceSerializer(DynamicDepthSerializer):
    class Meta:
        model = Province
        fields = ['id']+get_fields(Province, exclude=DEFAULT_FIELDS+['geometry'])


class ExcludePolygonFieldParishSerializer(DynamicDepthSerializer):
    class Meta:
        model = Parish
        fields = ['id']+get_fields(Parish, exclude=DEFAULT_FIELDS+['geometry'])

class SiteSerializer(DynamicDepthSerializer):

    class Meta:
        model = Site
        fields = ['id']+get_fields(Site, exclude=DEFAULT_FIELDS)


class SiteGeoSerializer(GeoFeatureModelSerializer):

    class Meta:
        model = Site
        fields = ['id'] + \
            get_fields(Site, exclude=DEFAULT_FIELDS+['coordinates'])
        geo_field = 'coordinates'


class SiteCoordinatesSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Site
        fields = ['id', 'name']
        geo_field = 'coordinates'
        # depth = 1


class ExcludePlolygonSiteGeoSerializer(DynamicDepthSerializer):
    ADM0 = ExcludePloygonFieldADM0Serializer()
    ADM1 = ExcludePloygonFieldADM1Serializer()
    ADM2 = ExcludePloygonFieldADM2Serializer()
    ADM3 = ExcludePloygonFieldADM3Serializer()
    ADM4 = ExcludePloygonFieldADM4Serializer()
    Province = ExcludePloygonFieldProvinceSerializer()
    Parish = ExcludePolygonFieldParishSerializer()


    # ADM5 = ExcludePloygonFieldADM5Serializer()

    class Meta:
        model = Site
        fields = ['id'] + \
            get_fields(Site, exclude=DEFAULT_FIELDS+['coordinates']) + ['ADM0', 'ADM1', 'ADM2', 'ADM3', 'ADM4', 'Province', 'Parish']
        # geo_field = 'coordinates'


class ExcludeSitePloygonSampleSerializer(DynamicDepthSerializer):
    site = ExcludePlolygonSiteGeoSerializer()

    class Meta:
        model = NewSamples
        fields = ['id']+get_fields(NewSamples, exclude=DEFAULT_FIELDS)


class ExcludePlolygonLocationGeoSerializer(DynamicDepthSerializer):
    site = ExcludePlolygonSiteGeoSerializer()

    class Meta:
        model = Location
        fields = ['id'] + get_fields(Location, exclude=DEFAULT_FIELDS)


class PeriodSerializer(DynamicDepthSerializer):

    class Meta:
        model = Period
        fields = ['id']+get_fields(Period, exclude=DEFAULT_FIELDS)

class MetalAnalysisSerializer(DynamicDepthSerializer):
    site = ExcludePlolygonSiteGeoSerializer()
    sample = ExcludeSitePloygonSampleSerializer()

    class Meta:
        model = MetalAnalysis
        fields = ['id']+get_fields(MetalAnalysis, exclude=DEFAULT_FIELDS)


class MetalworkSerializer(DynamicDepthSerializer):
    site = ExcludePlolygonSiteGeoSerializer()
    # sample = ExcludeSitePloygonSampleSerializer()

    class Meta:
        model = Metalwork
        fields = ['id']+get_fields(Metalwork, exclude=DEFAULT_FIELDS)


class LNHouseSerializer(DynamicDepthSerializer):
    site = ExcludePlolygonSiteGeoSerializer()

    class Meta:
        model = LNHouses
        fields = ['id']+get_fields(LNHouses, exclude=DEFAULT_FIELDS)
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        for key, value in data.items():
            if isinstance(value, float) and math.isnan(value):
                data[key] = None  # Replace NaN with null in JSON
        return data

class RadioCarbonSerializer(DynamicDepthSerializer):
    site = ExcludePlolygonSiteGeoSerializer()
    sample = ExcludeSitePloygonSampleSerializer()

    class Meta:
        model = Radiocarbon
        fields = ['id']+get_fields(Radiocarbon, exclude=DEFAULT_FIELDS)


class aDNASerializer(DynamicDepthSerializer):
    site = ExcludePlolygonSiteGeoSerializer()

    class Meta:
        model = aDNA
        fields = ['id']+get_fields(aDNA, exclude=DEFAULT_FIELDS)

class IndivdualObjectSerializer(DynamicDepthSerializer):
    site = ExcludePlolygonSiteGeoSerializer()

    class Meta:
        model = IndividualObjects
        fields = ['id']+get_fields(IndividualObjects, exclude=DEFAULT_FIELDS)


class RadioCarbonSerializer(DynamicDepthSerializer):
    site = ExcludePlolygonSiteGeoSerializer()

    class Meta:
        model = Radiocarbon
        fields = ['id']+get_fields(Radiocarbon, exclude=DEFAULT_FIELDS)


class LandingPointsSerializer(DynamicDepthSerializer):
    site = ExcludePlolygonSiteGeoSerializer()

    class Meta:
        model = LandingPoints
        fields = ['id']+get_fields(LandingPoints, exclude=DEFAULT_FIELDS)

class NewSamplesSerializer(DynamicDepthSerializer):
    site = ExcludePlolygonSiteGeoSerializer()

    class Meta:
        model = NewSamples
        fields = ['id']+get_fields(NewSamples, exclude=DEFAULT_FIELDS)


class CalibratedDateSerializer(DynamicDepthSerializer):
    class Meta:
        model = CalibratedDate
        fields = ["id", "sample", "lab", "dating_method", "date"]

class BoatFeatureSerializer(DynamicDepthSerializer):
    class Meta:
        model = BoatFeatures
        fields = get_fields(BoatFeatures, exclude=DEFAULT_FIELDS)

class BoatComponentSerializer(DynamicDepthSerializer):
    class Meta:
        model = BoatComponent
        fields = ["id"] + get_fields(BoatComponent, exclude=DEFAULT_FIELDS)

class BoatRelComponentSerializer(DynamicDepthSerializer):
    component = BoatComponentSerializer()

    class Meta:
        model = BoatRelComponent
        fields = ['id'] + get_fields(BoatRelComponent, exclude=DEFAULT_FIELDS) + ['component']

class BoatSerializer(DynamicDepthSerializer):
    site = ExcludePlolygonSiteGeoSerializer()
    # location = ExcludePlolygonLocationGeoSerializer()
    components = BoatRelComponentSerializer(many=True, read_only=True)  
    class Meta:
        model = Boat
        fields = ['id'] + get_fields(Boat, exclude=DEFAULT_FIELDS+['location']) + ['components', 'site', 'location']

