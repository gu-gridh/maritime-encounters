import os
import sys
import django
import pandas as pd
from django.contrib.gis.geos import Point
from datetime import datetime
from django.db.models import Q


# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maritime.settings')

# Set up Django
django.setup()

from apps.geography.models import *
from apps.resources.models import *  # Replace 'your_app' with the name of your Django app

# # Path to your CSV file
csv_file_path =  ''

# Load the CSV data

def load_data(path):
    df = pd.read_csv(path)
    for row in df.itertuples(index=False):
        # Validate latitude and longitude
        if not pd.isnull(row.lat) and not pd.isnull(row.lng):
            point = Point(row.lng, row.lat)
        else:
            point = None
        # Assign administrative levels
        adm4, adm3, adm2, province, parish = None, None, None, None, None
        if point:
            try:
                adm4 = ADM4.objects.get(geometry__contains=point)
            except ADM4.DoesNotExist:
                pass
            try:
                adm3 = ADM3.objects.get(geometry__contains=point)
            except ADM3.DoesNotExist:
                pass
            try:
                adm2 = ADM2.objects.get(geometry__contains=point)
            except ADM2.DoesNotExist:
                pass
            try:
                province = Province.objects.get(geometry__contains=point)
            except Province.DoesNotExist:
                pass
            try:
                parish = Parish.objects.get(geometry__contains=point)
            except Parish.DoesNotExist:
                pass
        # Determine site name
        site_name = f"{adm2.name}, {adm2.ADM1.name}" if adm2 else 'Unknown Site'
        # Create or get site object
        site_obj, _ = Site.objects.get_or_create(
            name=site_name,
            defaults={
                'coordinates': point,
                'ADM0': adm2.ADM1.ADM0 if adm2 else None,
                'ADM1': adm2.ADM1 if adm2 else None,
                'ADM2': adm2,
                'ADM3': adm3,
                'ADM4': adm4,
                'Province': province,
                'Parish': parish,
            }
        )
        # Process site types (Many-to-Many)
        site_types_list = []
        if not pd.isnull(row.site_type):
            for site_type in row.site_type.split(','):
                site_type_text = site_type.strip().capitalize()  # Clean input
                types = SiteType.objects.get_or_create(text=site_type_text)[0]  # Ensure Context instance
                site_types_list.append(types)  # Append valid object
        # Get or create materials and species
        r_metal = Material.objects.get_or_create(text=row.material)[0]
        r_species = Species.objects.get_or_create(text=row.species)[0]
        # Process periods and phases
        period_phase = Phase.objects.get_or_create(
            text=row.periods_2.strip().capitalize()
        )[0] if not pd.isnull(row.periods_2) else None
        periods = Period.objects.get_or_create(
            name=row.periods_1.strip().capitalize(),
            phase=period_phase
        )[0] if not pd.isnull(row.periods_1) else None
        # Create or update Radiocarbon object
        radio_carbon, _ = Radiocarbon.objects.update_or_create(
        site= site_obj,
            lab_id= row.labnr if not pd.isnull(row.labnr) else None,
            period= periods,
            c14_age= row.c14age if not pd.isnull(row.c14age) else None,
            c14_std= row.c14std if not pd.isnull(row.c14std) else None,
            density= row.dens if not pd.isnull(row.dens) else None,
            start_date= row.start if not pd.isnull(row.start) else None,
            end_date= row.end if not pd.isnull(row.end) else None,
            material= r_metal if not pd.isnull(row.material) else None,
            species= r_species if not pd.isnull(row.species) else None,
            d13c= row.delta_c13 if not pd.isnull(row.delta_c13) else None,
            feature= row.feature if not pd.isnull(row.feature) else None,
            notes=row.notes if not pd.isnull(row.notes) else None,
            reference=row.reference_1 if not pd.isnull(row.reference_1) else None,
            source_database=row.source_database if not pd.isnull(row.source_database) else None,
        )
        if site_types_list:
            radio_carbon.site_type.set(site_types_list)

    print("Data imported successfully")

def delete_data():

    # Find all related sites before deleting Radiocarbon objects
    related_sites = Site.objects.filter(
        id__in=Radiocarbon.objects.values_list('site_id', flat=True)
    )

    # Find duplicate sites by name in the related sites
    duplicate_sites = Site.objects.filter(name__in=related_sites.values_list('name', flat=True))

    # Delete Radiocarbon objects
    Radiocarbon.objects.all().delete()

    # Delete the related and duplicate sites
    related_sites.delete()
    duplicate_sites.delete()


    print("Data and related sites deleted successfully")


def delete_empty_sites():
    # Define models referencing `Site`
    resource_mapping = {
        'plank_boats': PlankBoats,
        'log_boats': LogBoats,
        'radiocarbon_dates': Radiocarbon,
        'individual_samples': IndividualObjects,
        'dna_samples': aDNA,
        'metal_analysis': MetalAnalysis,
        'landing_points': LandingPoints,
        'metalwork': Metalwork,
    } 

    # Identify sites referenced in any model
    referenced_sites_query = Q()
    for model in resource_mapping.values():
        referenced_sites_query |= Q(id__in=model.objects.values_list('site_id', flat=True))

    # Delete sites not referenced in any model
    unreferenced_sites = Site.objects.filter(~referenced_sites_query)
    unreferenced_sites.delete()

    print("Empty sites deleted successfully")

# Load data
load_data(csv_file_path)