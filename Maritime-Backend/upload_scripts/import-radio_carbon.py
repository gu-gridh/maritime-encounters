import os
import sys
import django
import pandas as pd
from datetime import datetime

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maritime.settings')

# Set up Django
django.setup()

from apps.geography.models import ADM0, ADM1, ADM2, ADM3, ADM4, ADM5
from apps.resources.models import *  # Replace 'your_app' with the name of your Django app

# Path to your CSV file
csv_file_path = '../../resources/maritime_enc_14C_062424_v2.csv'

# Load the CSV data
df = pd.read_csv(csv_file_path)

# Import data into ADM levels

for sampler_type in df[['site_type']].drop_duplicates().values:
    type = sampler_type[0]
    SiteType.objects.get_or_create(
        text= type
    )

for material in df[['Material']].drop_duplicates().values:
    material_name = material
    metal = Material.objects.get_or_create(
                text= material_name,     
        )

for species in df[['Species']].drop_duplicates().values:
    species_name = species
    Species.objects.get_or_create(
                text= species_name,     
        )

for period_name, start_date, end_date, period_phase in df[['Period', 'start', 'end', 'period_2']].values:
    Period.objects.update_or_create(
        start_date= start_date,
        end_date= end_date,
        name= period_name,
        phase= period_phase
    )

# For sites if there is no match you should be able to use import_sites.py script
for site_name, adm0, adm1, adm2 in df[['Site', 'COUNTRY', 'NAME_1', 'NAME_2']].drop_duplicates().values:
    site = Site.objects.get(
                name= site_name,
                ADM0__name= adm0,
                ADM1__name= adm1,
                ADM2__name=adm2,
        )

# Empty fields and NA values should be ignored
# These columns names are based on the CSV file and in your case, it may be different
# Make sure to change the column names to match your CSV file


for row in df.itertuples(index=False):

    material = Material.objects.get(
                text= row.Material,
        )
    species = Species.objects.get(
                text= row.Species,
        )
    period = Period.objects.get(
                name= row.Period,
        )
    site_type = SiteType.objects.get(
                text= row.site_type,
        )
    Radiocarbon.objects.get_or_create(
        site= site,
        site_type= site_type,
        lab_id=row.labnr,
        period= period,

        c14_age= row.C14AGE,
        c14_std= row.C14STD,
        density= row.dens,

        material= material,
        species= species,

        d13c= row.DELTA13C,

        feature= row.feature,
        
        note=row.notes,
        refrence=row.Refrence,
        source_database=row.source_database,


    )

print("Data imported successfully")

