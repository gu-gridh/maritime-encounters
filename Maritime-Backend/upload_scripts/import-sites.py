import os
import sys
import django
import pandas as pd
from django.contrib.gis.geos import Point

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maritime.settings')  # Replace 'your_project' with your project's name
django.setup()

from apps.geography.models import *
from apps.resources.models import Site  # Replace 'your_app' with the name of your Django app

# Path to your CSV file
csv_file_path = ''

# Load the CSV data
df = pd.read_csv(csv_file_path)

# Import data into ADM levels
   
def upload_sites(data):
    for row in data.itertuples(index=False):
        adm0 = ADM0.objects.get(row.GID_0)
        adm1 = ADM1.objects.get(row.GID_1)
        adm2 = ADM2.objects.get(row.GID_2)
        adm3 = ADM3.objects.get(row.GID_3)
        adm4 = ADM4.objects.get(row.GID_4)

        point = Point(row.lat, row.lon)  # Note that Point takes (longitude, latitude) order

        Site.objects.update_or_create(
            name=row.site_name,
            defaults={
                'coordinates':point,
                'ADM0': adm0,
                'ADM1': adm1,
                'ADM2': adm2,
                'ADM3': adm3,
                'ADM4': adm4
            }
        )
# Call the function and pass the data
# In case of different name of columns in the CSV file, replace the column names accordingly
# If ADMS are not in the database then you need first to import them through import ADMs script
print("Data imported successfully")

