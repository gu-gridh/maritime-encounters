import os
import sys
import django
import pandas as pd
from django.contrib.gis.geos import Point
from datetime import datetime

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maritime.settings')

# Set up Django
django.setup()

from apps.geography.models import *
from apps.resources.models import *  # Replace 'your_app' with the name of your Django app

# Path to your CSV file
csv_file_path = '../../resources/maritime_enc_14C_062424_v2.csv'

# Load the CSV data
df = pd.read_csv(csv_file_path)

# Import data into ADM levels
for row in df.itertuples(index=False):
    if not pd.isnull(row.lat) or pd.isnull(row.lng):
        point = Point(row.lat,row.lng) # Note that Point takes (longitude, latitude) order
    else:
        point=None
        
    # Add administrative data to sites and create site objects
    if point != None:
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


    site_types = []
    # There should be a for loop here to iterate over the site types, this is many to many relationship
    site_type =SiteType.objects.get_or_create(
        text= row.site_type
    )[0]


    r_metal = Material.objects.get_or_create(
                text= row.material,     
        )[0]

    r_species = Species.objects.get_or_create(
                text= row.species,     
        )[0]

    period_phase = Phase.objects.get_or_create(
        text= row.periods_2
    )[0]
    periods = Period.objects.get_or_create(
        start_date= row.start,
        end_date= row.end,
        name= row.periods_1,
        phase= period_phase
    )[0]


    radio_carbon = Radiocarbon.objects.get_or_create(
        site= obj_site,
        # site_type= site_type,
        lab_id=row.labnr,
        period= periods,

        c14_age= row.c14age,
        c14_std= row.c14std,
        density= row.dens,

        material= r_metal,
        species= r_species,

        d13c= row.delta_c13,

        feature= row.feature,
        
        notes=row.notes,
        reference=row.reference_1,
        source_database=row.source_database,

    )
    # radio_carbon.site_type.set(site_types)

print("Data imported successfully")

