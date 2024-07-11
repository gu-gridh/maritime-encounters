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
        if not pd.isnull(row.GID_0):
            adm0 = ADM0.objects.get(code=row.GID_0)
        else:
            adm0 = None
        if not pd.isnull(row.GID_1):    
            adm1 = ADM1.objects.get(code=row.GID_1)
        else:
            adm1 = None
        if not pd.isnull(row.GID_2):
            adm2 = ADM2.objects.get(code=row.GID_2)
        else:
            adm2 = None
        if not pd.isnull(row.GID_3):
            adm3 = ADM3.objects.get(code=row.GID_3)
        else:
            adm3 = None
        if not pd.isnull(row.GID_4):
            adm4 = ADM4.objects.get(code=row.GID_4)
        else:
            adm4 = None

        if not pd.isnull(row.lat) or pd.isnull(row.lng):
            point = Point(row.lng, row.lat)  # Note that Point takes (longitude, latitude) order
        else:
            point = None

        Site.objects.update_or_create(
            name=row.site,
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
upload_sites(df)
print("Data imported successfully")

