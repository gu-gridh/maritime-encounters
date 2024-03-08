from .models import *
from django.utils.html import format_html
from django.contrib.gis import admin
from django.utils.translation import gettext_lazy as _
from maritime.utils import get_fields, DEFAULT_FIELDS, DEFAULT_EXCLUDE
from admin_auto_filters.filters import AutocompleteFilter
from django.contrib.admin import EmptyFieldListFilter
from django.conf import settings


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
    ordering = ('site_name',)

@admin.register(PlankBoats)
class PlankBoatAdmin(admin.GISModelAdmin):
    list_display = ['plankboat_name', 'location']
    search_fields = ['plankboat_name', 'location']
    list_filter = ['plankboat_name', 'location']
    ordering = ('plankboat_name',)

@admin.register(LogBoats)
class LogBoatAdmin(admin.GISModelAdmin):
    list_display = ['logboat_name', ]
    search_fields = ['logboat_name']
    list_filter = ['logboat_name']
    ordering = ('logboat_name',)

@admin.register(LandingPints)
class LandingPintsAdmin(admin.GISModelAdmin):
    list_display = ['landing_id', 'site']
    search_fields = ['landing_id', 'site']
    list_filter = ['landing_id', 'site']
    ordering = ('landing_id',)

@admin.register(NewSamples)
class NewSamplesAdmin(admin.GISModelAdmin):
    list_display = ['sample_id', 'site']
    search_fields = ['sample_id', 'site']
    list_filter = ['sample_id', 'site']
    ordering = ('sample_id',)

@admin.register(Radiocarbon)
class RadiocarbonAdmin(admin.GISModelAdmin):
    list_display = ['date_id', 'site', 'period']
    search_fields = ['date_id', 'site', 'period']
    list_filter = ['date_id', 'site', 'period']
    ordering = ('date_id',)

@admin.register(MetalAnalysis)
class MetalAnalysisAdmin(admin.GISModelAdmin):
    list_display = ['metal_id', 'site']
    search_fields = ['metal_id', 'site']
    list_filter = ['metal_id', 'site']
    ordering = ('metal_id',)

@admin.register(aDNA)
class aDNAAdmin(admin.GISModelAdmin):
    list_display = ['aDNA_id', 'site']
    search_fields = ['aDNA_id', 'site']
    list_filter = ['aDNA_id', 'site']
    ordering = ('aDNA_id',)

@admin.register(IsotopesBio)
class IsotopesBioAdmin(admin.GISModelAdmin):
    list_display = ['bio_id', 'site']
    search_fields = ['bio_id', 'site']
    list_filter = ['bio_id', 'site']
    ordering = ('bio_id',)

@admin.register(LNHouses)
class LNHousesAdmin(admin.GISModelAdmin):
    list_display = ['house_id', 'site']
    search_fields = ['house_id', 'site']
    list_filter = ['house_id', 'site']
    ordering = ('house_id',)

@admin.register(NorwayDaggers)
class NorwayDaggersAdmin(admin.GISModelAdmin):
    list_display = ['dagger_id', 'site']
    search_fields = ['dagger_id', 'site']
    list_filter = ['dagger_id', 'site']
    ordering = ('dagger_id',)

@admin.register(NorwayShaftHoleAxes)
class NorwayShaftHoleAxesAdmin(admin.GISModelAdmin):
    list_display = ['shaft_hole_axe_id', 'site', 'museum']
    search_fields = ['shaft_hole_axe_id', 'site', 'museum']
    list_filter = ['shaft_hole_axe_id', 'site', 'museum']
    ordering = ('shaft_hole_axe_id',)