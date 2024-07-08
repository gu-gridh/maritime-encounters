from .models import *
from django.utils.html import format_html
from django.contrib.gis import admin
from django.utils.translation import gettext_lazy as _
from maritime.utils import get_fields, DEFAULT_FIELDS, DEFAULT_EXCLUDE
from admin_auto_filters.filters import AutocompleteFilter
from django.contrib.admin import EmptyFieldListFilter
from django.conf import settings


class SiteFilter(AutocompleteFilter):
    title = _('Site')  # display title
    field_name = 'site'  # name of the foreign key field


@admin.register(Location)
class LocationAdmin(admin.GISModelAdmin):
    list_display = ['location_name', 'site']
    search_fields = ['location_name', 'site__name']
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
    list_display = ['name', 'phase', 'start_date', 'end_date']
    search_fields = ['name', 'phase', 'start_date', 'end_date']
    list_filter = ['name', 'start_date', 'end_date']
    ordering = ['start_date', 'end_date', 'name']
    autocomplete_fields = ['phase']


@admin.register(PeriodActivity)
class PeriodActivityAdmin(admin.ModelAdmin):
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


@admin.register(Sampler)
class SamplerAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    list_filter = ['name']
    ordering = ['name']


@admin.register(ObjectDescription)
class ObjectDescriptionAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']
    list_filter = ['text']
    ordering = ['text']


@admin.register(Cleat)
class CleatAdmin(admin.ModelAdmin):
    list_display = ['cleat_number', 'cleat_length',
                    'cleat_width', 'cleat_heigth']
    search_fields = ['cleat_number']
    list_filter = ['cleat_number']
    ordering = ['cleat_number']


@admin.register(Element)
class ElementAdmin(admin.ModelAdmin):
    list_display = ['name', 'symbol', 'atomic_number']
    search_fields = ['name', 'symbol']
    list_filter = ['name', 'symbol']
    ordering = ['name']


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
    search_fields = ['name', 'ADM0__name', 'ADM1__name',]
    autocomplete_fields = ['ADM0', 'ADM1', 'ADM2', 'ADM3', 'ADM4']
    # list_filter = ['name', 'ADM1']
    ordering = ['name']


@admin.register(PlankBoats)
class PlankBoatAdmin(admin.GISModelAdmin):
    list_display = ['name', 'location', 'period', 'location']
    search_fields = ['name', 'location__location_name', 'period__name']
    list_filter = ['name', 'location']
    ordering = ['name']


@admin.register(LogBoats)
class LogBoatAdmin(admin.GISModelAdmin):
    list_display = ['name', 'site', 'period']
    search_fields = ['name', 'period__name', 'site__name']
    list_filter = ['name']
    ordering = ['name']


@admin.register(LandingPoints)
class LandingPointsAdmin(admin.GISModelAdmin):
    list_display = ['site', 'period']
    search_fields = ['site__name', 'period__name']
    list_filter = ['site']
    inlines = [
        RelPeriodActivityLandingPoints,
    ]


@admin.register(NewSamples)
class NewSamplesAdmin(admin.GISModelAdmin):
    list_display = ['site', 'sampler', 'metal']
    search_fields = ['site__name']
    list_filter = ['site']


@admin.register(Radiocarbon)
class RadiocarbonAdmin(admin.GISModelAdmin):
    list_display = ['site', 'period']
    search_fields = ['site__name', 'period__name']
    list_filter = ['site', 'period']


@admin.register(MetalAnalysis)
class MetalAnalysisAdmin(admin.GISModelAdmin):
    list_display = ['site', 'museum_entry', 'context']
    search_fields = ['site__name']
    list_filter = ['site']
    inlines = [
        RelMetalElementAdmin,
        RelMetalIsotopAdmin,
    ]


@admin.register(aDNA)
class aDNAAdmin(admin.GISModelAdmin):
    list_display = ['site']
    search_fields = ['site__name']
    list_filter = ['site']


@admin.register(IsotopesBio)
class IsotopesBioAdmin(admin.GISModelAdmin):
    list_display = ['site']
    search_fields = ['site__name']
    list_filter = ['site']


@admin.register(LNHouses)
class LNHousesAdmin(admin.GISModelAdmin):
    list_display = ['site']
    search_fields = ['site__name']
    list_filter = ['site']


@admin.register(NorwayDaggers)
class NorwayDaggersAdmin(admin.GISModelAdmin):
    list_display = ['site']
    search_fields = ['site__name']
    list_filter = ['site']


@admin.register(NorwayShaftHoleAxes)
class NorwayShaftHoleAxesAdmin(admin.GISModelAdmin):
    list_display = ['site', 'museum']
    search_fields = ['site__name', 'museum']
    list_filter = ['site', 'museum']


@admin.register(MuseumMeta)
class MuseumMetaAdmin(admin.ModelAdmin):
    list_display = ['museum']
    search_fields = ['museum']
    list_filter = ['museum']


@admin.register(MuseumCollection)
class MuseumCollectionAdmin(admin.ModelAdmin):
    list_display = ['museum', 'collection']
    search_fields = ['museum', 'collection']
    list_filter = ['museum', 'collection']


@admin.register(EntryNum)
class EntryNumAdmin(admin.ModelAdmin):
    list_display = ['entry_number']
    search_fields = ['entry_number']
    list_filter = ['entry_number']
    ordering = ['entry_number']


@admin.register(LiteratureNum)
class LiteratureNumAdmin(admin.ModelAdmin):
    list_display = ['literature_number']
    search_fields = ['literature_number']
    list_filter = ['literature_number']
    ordering = ['literature_number']


@admin.register(AccessionNum)
class AccessionNumAdmin(admin.ModelAdmin):
    list_display = ['accession_number']
    search_fields = ['accession_number']
    list_filter = ['accession_number']
    ordering = ['accession_number']


@admin.register(FindContext)
class FindContextAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']
    list_filter = ['text']
    ordering = ['text']


@admin.register(ContextDetail)
class ContextDetailAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']
    list_filter = ['text']
    ordering = ['text']


@admin.register(ContextKeywords)
class ContextKeywordsAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']
    list_filter = ['text']
    ordering = ['text']


@admin.register(ObjectCategories)
class ObjectCategoriesAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']
    list_filter = ['text']
    ordering = ['text']


@admin.register(ObjectSubcategories)
class ObjectSubcategoriesAdmin(admin.ModelAdmin):
    list_display = ['category', 'subcategory']
    search_fields = ['category', 'subcategory']
    list_filter = ['category', 'subcategory']
    ordering = ['category', 'subcategory']


@admin.register(ObjectMaterials)
class ObjectMaterialsAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']
    list_filter = ['text']
    ordering = ['text']


@admin.register(ObjectDescriptions)
class ObjectDescriptionsAdmin(admin.ModelAdmin):
    list_display = ['subcategory__category', 'subcategory', 'material']
    search_fields = ['subcategory__category', 'subcategory', 'material']
    list_filter = ['subcategory__category', 'subcategory', 'material']
    ordering = ['subcategory']


@admin.register(ContextFindsCategories)
class ContextFindsCategoriesAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']
    list_filter = ['text']
    ordering = ['text']


@admin.register(ContextFindsSubcategories)
class ContextFindsSubcategoriesAdmin(admin.ModelAdmin):
    list_display = ['category', 'text']
    search_fields = ['category', 'text']
    list_filter = ['category', 'text']
    ordering = ['category', 'text']


@admin.register(Metalwork)
class MetalworkAdmin(admin.ModelAdmin):
    list_display = ['entry_num', 'literature_num', 'accession_num', 'collection',
                    'location', 'primary_context', 'find_context', 'context_detail', 'dating']
    search_fields = ['entry_num', 'literature_num', 'accession_num', 'collection',
                     'location', 'primary_context', 'find_context', 'context_detail', 'dating']
    list_filter = ['entry_num', 'literature_num', 'accession_num', 'collection',
                   'location', 'primary_context', 'find_context', 'context_detail', 'dating']
    ordering = ['entry_num']
