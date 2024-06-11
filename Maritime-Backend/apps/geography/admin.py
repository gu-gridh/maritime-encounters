from django.contrib.gis.db import models
from .models import *
from django.utils.html import format_html
from django.contrib.gis import admin
from maritime.utils import get_fields, DEFAULT_EXCLUDE, DEFAULT_FIELDS

@admin.register(ADM0)
class ADM0Admin(admin.GISModelAdmin):
    fields = get_fields(ADM0, exclude=DEFAULT_EXCLUDE+["id"])
    readonly_fields = [*DEFAULT_FIELDS]
    list_display = ['name', 'code']
    list_filter = ['name', 'code']
    search_fields = ['name', 'code']


@admin.register(ADM1)
class ADM1Admin(admin.GISModelAdmin):
    fields = get_fields(ADM1, exclude=DEFAULT_EXCLUDE+["id"])
    readonly_fields = [*DEFAULT_FIELDS]
    list_display = ['name', 'ADM0']
    # list_filter = ['name', 'ADM0']
    search_fields = ['name', 'ADM0__name']
    autocomplete_fields = ['ADM0']
    list_per_page = 30  # Adjust the number to your needs



@admin.register(ADM2)
class ADM2Admin(admin.GISModelAdmin):
    fields = get_fields(ADM2, exclude=DEFAULT_EXCLUDE+["id"])
    readonly_fields = [*DEFAULT_FIELDS]
    list_display = ['name', 'ADM1']
    # list_filter = ['name', 'ADM1']
    search_fields = ['name', 'ADM1__name', 'ADM1__ADM0__name']
    autocomplete_fields = ['ADM1']
    list_per_page = 30  # Adjust the number to your needs



@admin.register(ADM3)
class ADM3Admin(admin.GISModelAdmin):
    fields = get_fields(ADM3, exclude=DEFAULT_EXCLUDE+["id"])
    readonly_fields = [*DEFAULT_FIELDS]
    list_display = ['name', 'ADM2']
    # list_filter = ['name', 'ADM2']
    search_fields = ['name', 'ADM2__name', 'ADM2__ADM1__name', 'ADM2__ADM1__ADM0__name']
    autocomplete_fields = ['ADM2']
    list_per_page = 30  # Adjust the number to your needs



@admin.register(ADM4)
class ADM4dmin(admin.GISModelAdmin):
    fields = get_fields(ADM4, exclude=DEFAULT_EXCLUDE+["id"])
    readonly_fields = [*DEFAULT_FIELDS]
    list_display = ['name', 'ADM3']
    # list_filter = ['name', 'ADM3']
    search_fields = ['name','ADM3__name', 'ADM3__ADM2__name', 'ADM3__ADM2__ADM1__name', 'ADM3__ADM2__ADM1__ADM0__name']
    autocomplete_fields = ['ADM3']
    list_per_page = 30  # Adjust the number to your needs



@admin.register(ADM5)
class ADM5Admin(admin.GISModelAdmin):
    fields = get_fields(ADM5, exclude=DEFAULT_EXCLUDE+["id"])
    readonly_fields = [*DEFAULT_FIELDS]
    list_display = ['name', 'ADM4']
    # list_filter = ['name', 'ADM4']
    search_fields = ['name', 'ADM4__name', 'ADM4__ADM3__ADM2__name', 'ADM4__ADM3__ADM2__ADM1__name', 'ADM4__ADM3__ADM2__ADM1__ADM0__name']
    autocomplete_fields = ['ADM4']
    list_per_page = 30  # Adjust the number to your needs


@admin.register(Province)
class ProvinceAdmin(admin.GISModelAdmin):
    fields = get_fields(Province, exclude=DEFAULT_EXCLUDE+["id"])
    readonly_fields = [*DEFAULT_FIELDS]
    list_display = ['name', 'country']
    # list_filter = ['name', 'country']
    search_fields = ['name', 'country']
    autocomplete_fields = ['country']

@admin.register(Parish)
class ParishAdmin(admin.GISModelAdmin):
    fields = get_fields(Parish, exclude=DEFAULT_EXCLUDE+["id"])
    readonly_fields = [*DEFAULT_FIELDS]
    list_display = ['name', 'code', 'country']
    # list_filter = ['name', 'country']
    search_fields = ['name', ]
    autocomplete_fields = ['country']
