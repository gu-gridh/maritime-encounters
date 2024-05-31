from .models import *
from django.utils.html import format_html
from django.contrib.gis import admin
from django.utils.translation import gettext_lazy as _
from maritime.utils import get_fields, DEFAULT_FIELDS, DEFAULT_EXCLUDE
from admin_auto_filters.filters import AutocompleteFilter
from django.contrib.admin import EmptyFieldListFilter
from django.conf import settings

class SiteFilter(AutocompleteFilter):
    title = _('Site') # display title
    field_name = 'site' # name of the foreign key field

@admin.register(Location)
class LocationAdmin(admin.GISModelAdmin):
    list_display = ['location_name', 'site']
    search_fields = ['location_name', 'site']
    list_filter = ['location_name', 'site']
    ordering = ['location_name']

@admin.register(SiteType)
class SiteTypeAdmin(admin.GISModelAdmin):
    list_display = ['text']
    search_fields = ['text']
    list_filter = ['text']
    ordering = ['text']

@admin.register(SampleType)
class SampleTypeAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']
    list_filter = ['text']
    ordering = ['text']

@admin.register(Phase)
class PhaseAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']
    list_filter = ['text']
    ordering = ['text']
@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date']
    search_fields = ['name', 'start_date', 'end_date']
    list_filter = ['name', 'start_date', 'end_date']
    ordering = ['start_date', 'end_date', 'name']
    autocomplete_fields = ['phase']

@admin.register(PeroidActivity)
class PeroidActivityAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']
    list_filter = ['text']
    ordering = ['text']

@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']
    list_filter = ['text']
    ordering = ['text']

@admin.register(Shape)
class ShapeAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']
    list_filter = ['text']
    ordering = ['text']

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']
    list_filter = ['text']
    ordering = ['text']

@admin.register(Context)
class ContextAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']
    list_filter = ['text']
    ordering = ['text']

@admin.register(DrilledLocation)
class DrilledLocationAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']
    list_filter = ['text']
    ordering = ['text']

@admin.register(ObjectDescription)
class ObjectDescriptionAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']
    list_filter = ['text']
    ordering = ['text']

@admin.register(Cleat)
class CleatAdmin(admin.ModelAdmin):
    list_display = ['cleat_number', 'cleat_length', 'cleat_width', 'cleat_heigth']
    search_fields = ['cleat_number']
    list_filter = ['cleat_number']
    ordering = ['cleat_number']

@admin.register(Element)
class ElementAdmin(admin.ModelAdmin):
    list_display = ['element_name', 'element_symbol', 'atomic_number']
    search_fields = ['element_name', 'element_symbol']
    list_filter = ['element_name', 'element_symbol']
    ordering = ['element_name']


class RelMetalElementAdmin(admin.TabularInline):
    model = MetalElement
    extra = 1

class RelMetalIsotopAdmin(admin.TabularInline):
    model = MetalIsotop
    extra = 1

@admin.register(LeadIsotope)
class LeadIsotopeRationAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']
    list_filter = ['text']
    ordering = ['text']

class RelPeriodActivityLandingPoints(admin.TabularInline):
    model = RelPresentActivityLandingPoints
    extra = 1

@admin.register(Carbon_Nitrogen_Ratio)
class Carbon_Nitrogen_RatioAdmin(admin.ModelAdmin):
    list_display = ['carbon_to_nitrogen_ratio']
    search_fields = ['carbon_to_nitrogen_ratio']
    list_filter = ['carbon_to_nitrogen_ratio']
    ordering = ['carbon_to_nitrogen_ratio']

@admin.register(CulturalGroup)
class CulturalGroupAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']
    list_filter = ['text']
    ordering = ['text']

@admin.register(DatingMethod)
class DatingMethodAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']
    list_filter = ['text']
    ordering = ['text']
@admin.register(Site)
class SiteAdmin(admin.GISModelAdmin):
    list_display = ['name', 'ADM0',]
    search_fields = ['name', 'ADM0', 'ADM1',]
    autocomplete_fields = ['ADM0', 'ADM1', 'ADM2', 'ADM3']
    list_filter = ['name', 'ADM1']
    ordering = ['name']

@admin.register(PlankBoats)
class PlankBoatAdmin(admin.GISModelAdmin):
    list_display = ['name', 'location', 'period', 'location']
    search_fields = ['name', 'location', 'period']
    list_filter = ['name', 'location']
    ordering = ['name']

@admin.register(LogBoats)
class LogBoatAdmin(admin.GISModelAdmin):
    list_display = ['name', 'site', 'period']
    search_fields = ['name', 'period']
    list_filter = ['name']
    ordering = ['name']

@admin.register(LandingPoints)
class LandingPointsAdmin(admin.GISModelAdmin):
    list_display = ['site', 'period']
    search_fields = ['site', 'period']
    list_filter = ['site']
    inlines = [
        RelPeriodActivityLandingPoints,
    ]

@admin.register(NewSamples)
class NewSamplesAdmin(admin.GISModelAdmin):
    list_display = ['site']
    search_fields = ['site']
    list_filter = ['site']

@admin.register(Radiocarbon)
class RadiocarbonAdmin(admin.GISModelAdmin):
    list_display = ['site', 'period']
    search_fields = ['site', 'period']
    list_filter = ['site', 'period']

@admin.register(MetalAnalysis)
class MetalAnalysisAdmin(admin.GISModelAdmin):
    list_display = ['site']
    search_fields = ['site']
    list_filter = ['site']
    inlines = [
        RelMetalElementAdmin,
        RelMetalIsotopAdmin,
    ]

@admin.register(aDNA)
class aDNAAdmin(admin.GISModelAdmin):
    list_display = ['site']
    search_fields = ['site']
    list_filter = ['site']

@admin.register(IsotopesBio)
class IsotopesBioAdmin(admin.GISModelAdmin):
    list_display = ['site']
    search_fields = ['site']
    list_filter = ['site']

@admin.register(LNHouses)
class LNHousesAdmin(admin.GISModelAdmin):
    list_display = ['site']
    search_fields = ['site']
    list_filter = ['site']

@admin.register(NorwayDaggers)
class NorwayDaggersAdmin(admin.GISModelAdmin):
    list_display = ['site']
    search_fields = ['site']
    list_filter = ['site']

@admin.register(NorwayShaftHoleAxes)
class NorwayShaftHoleAxesAdmin(admin.GISModelAdmin):
    list_display = ['site', 'museum']
    search_fields = ['site', 'museum']
    list_filter = ['site', 'museum']
