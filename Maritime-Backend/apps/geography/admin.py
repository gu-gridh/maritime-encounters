from django.contrib.gis.db import models
from .models import *
from django.utils.html import format_html
from django.contrib.gis import admin
from maritime.utils import get_fields, DEFAULT_EXCLUDE, DEFAULT_FIELDS

@admin.register(Country)
class CountryAdmin(admin.GISModelAdmin):
    fields = get_fields(Country, exclude=DEFAULT_EXCLUDE+["id"])
    readonly_fields = [*DEFAULT_FIELDS]
    list_display = ['name', 'code']
    list_filter = ['name', 'code']
    search_fields = ['name', 'code']


@admin.register(Region)
class RegionAdmin(admin.GISModelAdmin):
    fields = get_fields(Region, exclude=DEFAULT_EXCLUDE+["id"])
    readonly_fields = [*DEFAULT_FIELDS]
    list_display = ['name', 'country']
    list_filter = ['name', 'country']
    search_fields = ['name', 'country']
    autocomplete_fields = ['country']


@admin.register(Counties)
class CountiesAdmin(admin.GISModelAdmin):
    fields = get_fields(Counties, exclude=DEFAULT_EXCLUDE+["id"])
    readonly_fields = [*DEFAULT_FIELDS]
    list_display = ['name', 'region', 'country']
    list_filter = ['name', 'region', 'country']
    search_fields = ['name', 'region', 'country']
    autocomplete_fields = ['region', 'country']


@admin.register(Municipality)
class MunicipalityAdmin(admin.GISModelAdmin):
    fields = get_fields(Municipality, exclude=DEFAULT_EXCLUDE+["id"])
    readonly_fields = [*DEFAULT_FIELDS]
    list_display = ['name', 'counties', 'region', 'country']
    list_filter = ['name', 'counties', 'region', 'country']
    search_fields = ['name', 'counties', 'region', 'country']
    autocomplete_fields = ['counties', 'region', 'country']


@admin.register(LAU)
class LAUAdmin(admin.GISModelAdmin):
    fields = get_fields(LAU, exclude=DEFAULT_EXCLUDE+["id"])
    readonly_fields = [*DEFAULT_FIELDS]
    list_display = ['name', 'municipality', 'counties', 'region', 'country']
    list_filter = ['name', 'municipality', 'counties', 'region', 'country']
    search_fields = ['name', 'municipality', 'counties', 'region', 'country']
    autocomplete_fields = ['municipality', 'counties', 'region', 'country']


@admin.register(Commune)
class CommuneAdmin(admin.GISModelAdmin):
    fields = get_fields(Commune, exclude=DEFAULT_EXCLUDE+["id"])
    readonly_fields = [*DEFAULT_FIELDS]
    list_display = ['name', 'lau', 'municipality', 'counties', 'region', 'country']
    list_filter = ['name', 'lau', 'municipality', 'counties', 'region', 'country']
    search_fields = ['name', 'lau', 'municipality', 'counties', 'region', 'country']
    autocomplete_fields = ['lau', 'municipality', 'counties', 'region', 'country']


@admin.register(Province)
class ProvinceAdmin(admin.GISModelAdmin):
    fields = get_fields(Province, exclude=DEFAULT_EXCLUDE+["id"])
    readonly_fields = [*DEFAULT_FIELDS]
    list_display = ['name', 'country']
    list_filter = ['name', 'country']
    search_fields = ['name', 'country']
    autocomplete_fields = ['country']

@admin.register(Parish)
class ParishAdmin(admin.GISModelAdmin):
    fields = get_fields(Parish, exclude=DEFAULT_EXCLUDE+["id"])
    readonly_fields = [*DEFAULT_FIELDS]
    list_display = ['name', 'code', 'country']
    list_filter = ['name', 'country']
    search_fields = ['name', ]
    autocomplete_fields = ['country']
