import os
import sys
import django
import pandas as pd
from datetime import datetime

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maritime.settings')  # Replace 'your_project' with your project's name
django.setup()

from apps.geography.models import *
from apps.resources.models import *  # Replace 'your_app' with the name of your Django app

# Path to your CSV file
csv_file_path = ''

# Load the CSV data
df = pd.read_csv(csv_file_path)

# Import data into ADM levels
site_cache = {}
metal_cache = {}
sampler_cache = {}

for sampler_name in df[['Sampler']].drop_duplicates().values:
    sampler_name = sampler_name[0]
    sampler, created = Sampler.objects.get_or_create(
        name= sampler_name
    )
    sampler_cache[sampler_name] = sampler

for metal_name in df[['Metal']].drop_duplicates().values:
    metal_name = metal_name[0]
    metal, created = Element.objects.get_or_create(
                name= metal_name,     
        )
    metal_cache[metal_name] = metal

for site_name, adm0, adm1, adm2 in df[['site_name', 'COUNTRY', 'NAME_1', 'NAME_2']].drop_duplicates().values:
    site = Site.objects.get(
                name= site_name,
                ADM0__name= adm0,
                ADM1__name= adm1,
                ADM2__name=adm2,
        )
    site_cache[site_name] = site


for row in df.itertuples(index=False):
    site_sample = site_cache.get(row.site_name)
    metal_name = metal_cache.get(row.Metal)
    sampler_name = sampler_cache.get(row.Sampler)
    date_format = "%d/%m/%Y %H:%M"
    if pd.notna(row.Date):
        parsed_date = datetime.strptime(row.Date, date_format)
    else:
        parsed_date = None
    NewSamples.objects.update_or_create(
        site=site_sample,

        defaults={
            # 'site': site_sample,
            'metal': metal_name,
            'drilled_location': row.Drilled_location,
            'weight': row.Weight,
            'pictures': row.Pictures,
            'sampler': sampler_name,
            'date': parsed_date,
            'note': row.Note
        }
    )

print("Data imported successfully")

