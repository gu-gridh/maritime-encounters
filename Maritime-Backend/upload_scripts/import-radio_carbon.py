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
csv_file_path = ''

# # Load the CSV data

def load_data(path):
    # Import data into ADM levels
    df = pd.read_csv()

    for row in df.itertuples(index=False):
        if not pd.isnull(row.lat) or pd.isnull(row.lng):
            point = Point(row.lat,row.lng) # Note that Point takes (longitude, latitude) order
        else:
            point=None
            
        # Add administrative data to sites and create site objects
        if point != None:
            try:
                adm0 = ADM0.objects.get(geometry__contains=point)
            except:
                adm0 = None
            try:
                adm4 = ADM4.objects.get(geometry__contains=point)
            except:
                adm4 = None
            try:
                adm3 = ADM3.objects.get(geometry__contains=point)
            except:
                adm3 = None
            try:
                adm2 = ADM2.objects.get(geometry__contains=point)
            except:
                adm2 = None
            try:
                province = Province.objects.get(geometry__contains=point)
            except:
                province = None
            try:
                parish = Parish.objects.get(geometry__contains=point)
            except:
                parish = None

            # adm0 = ADM0.objects.get(code=row.country) if row.country != None else None    
            site_name = row.site 
            
            try:
                obj_site = Site.objects.get_or_create(
                    name=site_name,
                    ADM2=adm2,
                    ADM3=adm3,
                    ADM4=adm4,
                    Province=province,
                    Parish=parish,
                    coordinates=point
                )[0]
            
            except:
                obj_site = Site.objects.get_or_create(
                    name=row.Site if row.Site != None else None,
                )[0]


        context_details = []
        if not pd.isnull(row.site_type):
            types = row.site_type.split("/")
            # There should be a for loop here to iterate over the site types, this is many to many relationship
            for i in types:
                context_details.append(Context.objects.get_or_create(
                    text=i.strip().capitalize()
                )[0])
        else:
            context_details = None

        r_metal = Material.objects.get_or_create(
                    text= row.material,     
            )[0]

        r_species = Species.objects.get_or_create(
                    text= row.species,     
            )[0]
        
        if not pd.isnull(row.periods_2):
            period_phase = Phase.objects.get_or_create(
                text= row.periods_2.strip().capitalize(),
            )[0]
        else:
            period_phase = None
            
        if not pd.isnull(row.periods_1):
            periods = Period.objects.get_or_create(
                name= row.periods_1.strip().capitalize(),
                phase= period_phase
            )[0]
        else:
            periods = None

        radio_carbon,_ = Radiocarbon.objects.update_or_create(
            site= obj_site,
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
        if context_details:
            radio_carbon.context.set(context_details)

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

delete_empty_sites()