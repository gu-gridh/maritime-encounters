from maritime.abstract.serializers import DynamicDepthSerializer, GenericSerializer
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from . import models
from maritime.utils import get_fields, DEFAULT_FIELDS
from .models import *