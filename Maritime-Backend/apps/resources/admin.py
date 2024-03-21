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

@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ['text', 'start_date', 'end_date']
    search_fields = ['text', 'start_date', 'end_date']
    list_filter = ['text', 'start_date', 'end_date']
    ordering = ['start_date', 'end_date', 'text']

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

@admin.register(Cleat)
class CleatAdmin(admin.ModelAdmin):
    list_display = ['cleat_number', 'cleat_length', 'cleat_width', 'cleat_heigth']
    search_fields = ['cleat_number']
    list_filter = ['cleat_number']
    ordering = ['cleat_number']

@admin.register(Element)
class ElementAdmin(admin.ModelAdmin):
    list_display = ['elemant_name', 'element_symbol', 'element_number']
    search_fields = ['elemant_name', 'element_symbol']
    list_filter = ['elemant_name', 'element_symbol']
    ordering = ['elemant_name']

@admin.register(LeadIsotopeRation)
class LeadIsotopeRationAdmin(admin.ModelAdmin):
    list_display = ['lead_isotop', 'isotop_ratio']
    search_fields = ['lead_isotop', 'isotop_ratio']
    list_filter = ['lead_isotop', 'isotop_ratio']
    ordering = ['lead_isotop']

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
    list_display = ['site_name']
    search_fields = ['site_name', 'ADM1', 'ADM2', 'ADM3']
    list_filter = ['site_name', 'ADM1', 'ADM2', 'ADM3']
    # fieldsets = (
    #     (None, {
    #         'fields': ('site_name')
    #     }),
    # )
    ordering = ['site_name']

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
    list_display = ['landing_id', 'site', 'period']
    search_fields = ['landing_id', 'site', 'period']
    list_filter = ['landing_id', 'site']
    ordering = ['landing_id']

@admin.register(NewSamples)
class NewSamplesAdmin(admin.GISModelAdmin):
    list_display = ['sample_id', 'site']
    search_fields = ['sample_id', 'site']
    list_filter = ['sample_id', 'site']
    ordering = ['sample_id']

@admin.register(Radiocarbon)
class RadiocarbonAdmin(admin.GISModelAdmin):
    list_display = ['date_id', 'site', 'period']
    search_fields = ['date_id', 'site', 'period']
    list_filter = ['date_id', 'site', 'period']
    ordering = ['date_id']

@admin.register(MetalAnalysis)
class MetalAnalysisAdmin(admin.GISModelAdmin):
    list_display = ['metal_id', 'site']
    search_fields = ['metal_id', 'site']
    list_filter = ['metal_id', 'site']
    ordering = ['metal_id']

@admin.register(aDNA)
class aDNAAdmin(admin.GISModelAdmin):
    list_display = ['aDNA_id', 'site']
    search_fields = ['aDNA_id', 'site']
    list_filter = ['aDNA_id', 'site']
    ordering = ['aDNA_id']

@admin.register(IsotopesBio)
class IsotopesBioAdmin(admin.GISModelAdmin):
    list_display = ['bio_id', 'site']
    search_fields = ['bio_id', 'site']
    list_filter = ['bio_id', 'site']
    ordering = ['bio_id']

@admin.register(LNHouses)
class LNHousesAdmin(admin.GISModelAdmin):
    list_display = ['house_id', 'site']
    search_fields = ['house_id', 'site']
    list_filter = ['house_id', 'site']
    ordering = ['house_id']

@admin.register(NorwayDaggers)
class NorwayDaggersAdmin(admin.GISModelAdmin):
    list_display = ['dagger_id', 'site']
    search_fields = ['dagger_id', 'site']
    list_filter = ['dagger_id', 'site']
    ordering = ['dagger_id']

@admin.register(NorwayShaftHoleAxes)
class NorwayShaftHoleAxesAdmin(admin.GISModelAdmin):
    list_display = ['shaft_hole_axe_id', 'site', 'museum']
    search_fields = ['shaft_hole_axe_id', 'site', 'museum']
    list_filter = ['shaft_hole_axe_id', 'site', 'museum']
    ordering = ['shaft_hole_axe_id']