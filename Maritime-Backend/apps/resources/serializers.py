from maritime.abstract.serializers import DynamicDepthSerializer, GenericSerializer
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from . import models
from maritime.utils import get_fields, DEFAULT_FIELDS
from .models import *
from apps.geography.models import *

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


# class ExcludePloygonFieldADM5Serializer(DynamicDepthSerializer):
#     class Meta:
#         model = ADM5
#         fields = ['id']+get_fields(ADM5, exclude=DEFAULT_FIELDS+['geometry'])


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
    # ADM5 = ExcludePloygonFieldADM5Serializer()

    class Meta:
        model = Site
        fields = ['id'] + \
            get_fields(Site, exclude=DEFAULT_FIELDS+['coordinates'])
        # geo_field = 'coordinates'


class ExcludeSitePloygonSampleSerializer(DynamicDepthSerializer):
    site = ExcludePlolygonSiteGeoSerializer()

    class Meta:
        model = NewSamples
        fields = ['id']+get_fields(NewSamples, exclude=DEFAULT_FIELDS)


class MetalAnalysisSerializer(DynamicDepthSerializer):
    site = ExcludePlolygonSiteGeoSerializer()
    sample = ExcludeSitePloygonSampleSerializer()

    class Meta:
        model = MetalAnalysis
        fields = ['id']+get_fields(MetalAnalysis, exclude=DEFAULT_FIELDS)


class MetalworkSerializer(DynamicDepthSerializer):
    # site = ExcludePlolygonSiteGeoSerializer()
    # sample = ExcludeSitePloygonSampleSerializer()

    class Meta:
        model = Metalwork
        fields = ['id']+get_fields(Metalwork, exclude=DEFAULT_FIELDS)


class RadioCarbonSerializer(DynamicDepthSerializer):
    site = ExcludePlolygonSiteGeoSerializer()
    sample = ExcludeSitePloygonSampleSerializer()

    class Meta:
        model = Radiocarbon
        fields = ['id']+get_fields(Radiocarbon, exclude=DEFAULT_FIELDS)


class PlankBoatsSerializer(DynamicDepthSerializer):
    site = ExcludePlolygonSiteGeoSerializer()

    class Meta:
        model = PlankBoats
        fields = ['id']+get_fields(PlankBoats, exclude=DEFAULT_FIELDS)

class LogBoatsSerializer(DynamicDepthSerializer):
    site = ExcludePlolygonSiteGeoSerializer()

    class Meta:
        model = LogBoats
        fields = ['id']+get_fields(LogBoats, exclude=DEFAULT_FIELDS)

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


class RadiocarbonSerializer(DynamicDepthSerializer):
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