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
    if not pd.isnull(row.y) or pd.isnull(row.x):
        point = Point(row.Lat,row.Lng) # Note that Point takes (longitude, latitude) order
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
            
        adm0 = ADM0.objects.get(name=row.ADM_0) if row.ADM_0 != None else None
        adm1 = ADM1.objects.get(name=row.ADM_1) if row.ADM_1 != None else None
            
        site_name = row.Site or f"{parish}, {province}: {row.y}, {row.x}" or f"{province}: {row.y}, {row.x}" or f"{adm4}: {row.y}, {row.x}" or f"{adm3}: {row.y}, {row.x}" or f"{adm2}: {row.y}, {row.x}"
        
        try:
            site = Site.objects.get_or_create(
                name=site_name,
                ADM0=adm0,
                ADM1=adm1,
                ADM2=adm2,
                ADM3=adm3,
                ADM4=adm4,
                Province=province,
                Parish=parish,
                coordinates=point
            )[0]
        
        except:
            site = Site.objects.get_or_create(
                name=row.Site if row.Site != None else None,
            )[0]



    site_type =SiteType.objects.get_or_create(
        text= row.site_type
    )


    metal = Material.objects.get_or_create(
                text= row.Material,     
        )

    species = Species.objects.get_or_create(
                text= row.Species,     
        )

    period = Period.objects.update_or_create(
        start_date= row.start,
        end_date= row.end,
        name= row.Period,
        phase= row.period_2
    )


    Radiocarbon.objects.get_or_create(
        site= site,
        site_type= site_type,
        lab_id=row.labnr,
        period= period,

        c14_age= row.C14AGE,
        c14_std= row.C14STD,
        density= row.dens,

        material= metal,
        species= species,

        d13c= row.DELTA13C,

        feature= row.feature,
        
        note=row.notes,
        refrence=row.Refrence,
        source_database=row.source_database,


    )

print("Data imported successfully")

