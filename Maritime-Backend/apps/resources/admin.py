from .models import *
from django.contrib.gis import admin
from django.utils.translation import gettext_lazy as _
from admin_auto_filters.filters import AutocompleteFilter
import mapwidgets
from django.db.models import Case, When, IntegerField, Q


class SiteFilter(AutocompleteFilter):
    title = _('Site')
    field_name = 'site'


class PeriodFilter(AutocompleteFilter):
    title = _('Period')
    field_name = 'period'


class FormFilter(AutocompleteFilter):
    title = _('Form')
    field_name = 'form'


class VariantFilter(AutocompleteFilter):
    title = _('Variant')
    field_name = 'variant'


class OrientationFilter(AutocompleteFilter):
    title = _('Orientation')
    field_name = 'orientation'


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['location_name', 'location_detail']
    search_fields = ['location_name', 'location_name']
    list_filter = ['location_name']
    ordering = ['location_detail']
    formfield_overrides = {
        models.PointField: {"widget": mapwidgets.LeafletPointFieldWidget}
    }


@admin.register(SiteType)
class SiteTypeAdmin(admin.ModelAdmin):
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

@admin.register(DateRanges)
class DateRangesAdmin(admin.ModelAdmin):
    list_display = ['start_date', 'end_date']
    search_fields = ['start_date', 'end_date']
    list_filter = ['start_date', 'end_date']
    ordering = ['start_date', 'end_date']

@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
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

@admin.register(BoatMaterial)
class BoatMaterialAdmin(admin.ModelAdmin):
    list_display=['common_name','scientific_name']
    search_fields=['common_name','scientific_name']
    list_filter = ['common_name','scientific_name']
    ordering = ['common_name','scientific_name']
    
@admin.register(BoatFeatures)
class BoatFeaturesAdmin(admin.ModelAdmin):
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
    list_display = ['subcategory']
    search_fields = ['category__text', 'subcategory__subcategory']
    list_filter = ['category', 'subcategory']
    ordering = ['category__text', 'subcategory__subcategory']


@admin.register(Cleat)
class CleatAdmin(admin.ModelAdmin):
    list_display = ['cleat_number', 'cleat_length',
                    'cleat_width']
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
class SiteAdmin(admin.ModelAdmin):
    list_display = ['name', 'ADM0', 'placename']
    search_fields = ['name', 'placename', 'ADM0__name', 'ADM1__name']
    autocomplete_fields = ['ADM0', 'ADM1', 'ADM2', 'ADM3', 'ADM4', 'Province', 'Parish']
    list_per_page = 50
    formfield_overrides = {
        models.PointField: {"widget": mapwidgets.LeafletPointFieldWidget}
    }

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Annotate: 1 if both name and placename are empty/null, else 0
        return qs.annotate(
            empty_name=Case(
                When(name__isnull=True, placename__isnull=True, then=1),
                When(name='', placename='', then=1),
                When(name='', placename__isnull=True, then=1),
                When(name__isnull=True, placename='', then=1),
                default=0,
                output_field=IntegerField(),
            ),
            name_is_blank=Case(
                When(Q(name__isnull=True) | Q(name=''), then=1),
                default=0,
                output_field=IntegerField(),
            ),
        ).order_by('empty_name', 'name_is_blank', 'placename', 'name')

@admin.register(Fastening)
class FasteningAdmin(admin.ModelAdmin):
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

@admin.register(BoatComponent)
class BoatComponentAdmin(admin.ModelAdmin):
    list_display = ['part_type']
    search_fields = ['part_type']
    list_filter = ['part_type'] 
    ordering = ['part_type']

class RelBoatComponent(admin.TabularInline):
    model = BoatRelComponent
    extra = 1

@admin.register(CalibratedDate)
class CalibratedDateAdmin(admin.ModelAdmin):
    list_display = ['sample', 'lab', 'dating_method', 'date']
    list_per_page = 50
    search_fields = ['sample', 'lab', 'date']
    autocomplete_fields = ['dating_method']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('dating_method')

@admin.register(Boat)
class BoatsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'vessel_name', 'vessel_type']
    list_per_page = 50

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('site', 'period', 'location')

    def site_name(self, obj):
        return obj.site.name if obj.site else ''
    site_name.admin_order_field = 'site'
    site_name.short_description = 'Site Name'

    search_fields = ['site__name', 'vessel_name', 'vessel_type']
    list_filter = [SiteFilter, 'vessel_type']
    ordering = ['site']
    autocomplete_fields = ['site', 'period', 'location']
    filter_horizontal = ['carbon_date']
    inlines = [
        RelBoatComponent
    ]

@admin.register(LandingPoints)
class LandingPointsAdmin(admin.ModelAdmin):
    list_display = ['site']
    list_per_page = 50
    search_fields = ['site__name', 'period__name']
    list_filter = [SiteFilter]
    autocomplete_fields = ['site']
    inlines = [
        RelPeriodActivityLandingPoints,
    ]
    filter_horizontal = ['period', 'related_finds']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('site')
@admin.register(NewSamples)
class NewSamplesAdmin(admin.ModelAdmin):
    list_display = ['site', 'sampler', 'metal']
    list_per_page = 50
    search_fields = ['site__name']
    list_filter = [SiteFilter]
    autocomplete_fields = ['site']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('site', 'sampler', 'metal')


@admin.register(Radiocarbon)
class RadiocarbonAdmin(admin.ModelAdmin):
    list_display = ['site', 'period']
    list_per_page = 50
    search_fields = ['site__name', 'period__name', 'lab_id']
    list_filter = [SiteFilter, PeriodFilter]
    autocomplete_fields = ['site', 'period', 'sample', 'material', 'species']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('site', 'period', 'sample', 'material', 'species')



@admin.register(LISource)
class LISourceAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    list_filter = ['name']
    ordering = ['name']


@admin.register(MetalAnalysis)
class MetalAnalysisAdmin(admin.ModelAdmin):
    list_display = ['site', 'museum_entry', 'context']
    list_per_page = 50
    search_fields = ['site__name']
    list_filter = [SiteFilter]
    inlines = [
        RelMetalElementAdmin,
        RelMetalIsotopAdmin,
    ]
    filter_horizontal = ['LIconsistency']
    autocomplete_fields = ['context', 'object_description',
                           'site', 'museum_entry', 'sample', 'period']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'site', 'museum_entry', 'context', 'object_description', 'sample', 'period'
        )


@admin.register(aDNA)
class aDNAAdmin(admin.ModelAdmin):
    list_display = ['site']
    list_per_page = 50
    search_fields = ['site__name']
    list_filter = [SiteFilter]
    autocomplete_fields = ['site']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('site')


@admin.register(IsotopesBio)
class IsotopesBioAdmin(admin.ModelAdmin):
    list_display = ['site']
    list_per_page = 50
    search_fields = ['site__name']
    list_filter = [SiteFilter]
    autocomplete_fields = ['site']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('site', 'sample', 'smple_type', 'species', 'period')

@admin.register(Orientation)
class OrientationAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']
    list_filter = ['text']
    ordering = ['text']

@admin.register(GableDescriptor)
class GableDescriptorAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']
    list_filter = ['text']
    ordering = ['text']

@admin.register(ExteriorDescriptor)
class ExteriorDescriptorAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']
    list_filter = ['text']
    ordering = ['text']

@admin.register(LNHouses)
class LNHousesAdmin(admin.ModelAdmin):
    list_display = ['site']
    list_per_page = 50
    search_fields = ['site__name', 'form__name', 'variant__name', 'orientation__text']
    list_filter = [SiteFilter, FormFilter, VariantFilter, OrientationFilter]
    autocomplete_fields = ['site', 'form', 'variant', 'orientation']
    filter_horizontal = ['period', 'dating', 'gable', 'exterior_construction']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('site', 'form', 'variant', 'orientation')

@admin.register(MuseumMeta)
class MuseumMetaAdmin(admin.ModelAdmin):
    list_display = ['museum','museum_number']
    search_fields = ['museum','museum_number']
    list_filter = ['museum','museum_number']


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
    list_display = ['subcategory']
    search_fields = ['subcategory']
    list_filter = ['subcategory']
    ordering = ['subcategory']


@admin.register(ObjectMaterials)
class ObjectMaterialsAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']
    list_filter = ['text']
    ordering = ['text']


# @admin.register(ObjectDescriptions)
# class ObjectDescriptionsAdmin(admin.ModelAdmin):
#     list_display = ['subcategory', 'subcategory']
#     search_fields = ['subcategory__category__text', 'subcategory', 'material']
#     list_filter = ['subcategory__category__text', 'subcategory', 'material']
#     ordering = ['subcategory']

@admin.register(ObjectCount)
class ObjectCountAdmin(admin.ModelAdmin):
    list_display = ['metal', 'object', 'material_list', 'count']
    list_per_page = 50
    search_fields = ['metal__entry_num__entry_number',
                     'metal__literature_num__literature_number']
    ordering = ['metal']
    filter_horizontal = ['material']
    autocomplete_fields = ['metal', 'object']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'metal', 'object'
        ).prefetch_related('material')

    def material_list(self, obj):
        return [material.text for material in obj.material.all()]


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


class RelObjectCountAdmin(admin.TabularInline):
    model = ObjectCount
    extra = 1
    filter_horizontal = ['material']
    autocomplete_fields = ['object']
    list_display=['materials_list']


@admin.register(Metalwork)
class MetalworkAdmin(admin.ModelAdmin):
    list_display = ['entry_num', 'literature_num', 'accession_num',
                    'location', 'main_context', 'find_context', 'context_detail', 'site']
    list_per_page = 50
    search_fields = ['entry_num__entry_number', 'literature_num__literature_number', 'accession_num__accession_number', 'collection__collection',
                     'location__location_name', 'main_context__text', 'find_context__text', 'context_detail__text', 'period__name', 'period__phase__text']
    list_filter = [SiteFilter]
    ordering = ['entry_num']
    inlines = [
        RelObjectCountAdmin
    ]
    filter_horizontal = ['context_keywords', 'period', 'context_keywords',
                         'certain_context_descriptors', 'uncertain_context_descriptors', 'museum', 'collection']
    autocomplete_fields = ['entry_num', 'literature_num', 'accession_num', 'location', 'main_context', 'find_context', 'context_detail', 'site']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'entry_num', 'literature_num', 'accession_num',
            'location', 'main_context', 'find_context', 'context_detail', 'site'
        )


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    list_filter = ['name']
    ordering = ['name']


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    list_filter = ['name']
    ordering = ['name']


@admin.register(ObjectIds)
class ObjectIdsAdmin(admin.ModelAdmin):
    list_display = ['art_id', 'systemnr',
                    'stednr', 'loknr', 'frednr', 'other_id']
    search_fields = ['art_id', 'systemnr',
                     'stednr', 'loknr', 'frednr', 'other_id']
    list_filter = ['art_id', 'systemnr',
                   'stednr', 'loknr', 'frednr', 'other_id']
    ordering = ['art_id', 'systemnr', 'stednr', 'loknr', 'frednr', 'other_id']


@admin.register(IndividualObjects)
class IndividualObjectsAdmin(admin.ModelAdmin):
    list_display = ['site', 'accession_number']
    list_per_page = 50
    search_fields = ['site__name', 'id_national_database__art_id',
                     'form__name', 'variant__name', 'period__name', 'start_date', 'end_date']
    list_filter = [SiteFilter]
    ordering = ['site']
    filter_horizontal = ['material', 'period']
    autocomplete_fields = ['site', 'accession_number',
                           'object_type', 'form', 'variant', 'museum', 'context']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'site', 'accession_number', 'museum', 'object_type', 'form', 'variant', 'context'
        )
