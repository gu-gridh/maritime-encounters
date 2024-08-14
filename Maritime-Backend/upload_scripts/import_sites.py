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
df = pd.read_csv(csv_file_path, encoding='utf-8')

# Import data into ADM levels
   
def upload_sites_withADM(data):
    for row in data.itertuples(index=False):
        if not pd.isnull(row.GID_0):
            try:
                adm0 = ADM0.objects.get(code=row.GID_0)
            except:
                adm0 = None
        else:
            adm0 = None
        if not pd.isnull(row.GID_1):
            try:    
                adm1 = ADM1.objects.get(code=row.GID_1)
            except:
                adm1 = None
        else:
            adm1 = None
        if not pd.isnull(row.GID_2):
            try:
                adm2 = ADM2.objects.get(code=row.GID_2)
            except:
                adm2 = None
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

        if not pd.isnull(row.y) or pd.isnull(row.x):
            point = Point(row.x, row.y)  # Note that Point takes (longitude, latitude) order
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


def upload_sites_noADM(data):
    for row in data.itertuples(index=False):
        if not pd.isnull(row.y) or pd.isnull(row.x):
            point = Point(row.x,row.y)
        else:
            point=None
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
                
        site_name = row.place or f"{row.parish}: {row.y}, {row.x}" or f"{row.province}: {row.y}, {row.x}" or f"{row.ADM_4}: {row.y}, {row.x}" or f"{row.ADM_3}: {row.y}, {row.x}" or f"{row.ADM_2}: {row.y}, {row.x}"
        Site.objects.update_or_create(
            name=site_name,
            defaults={
                'coordinates':point,
                'ADM0': adm2.ADM1.ADM0 if adm2 != None else None,
                'ADM1': adm2.ADM1 if adm2 != None else None,
                'ADM2': adm2,
                'ADM3': adm3,
                'ADM4': adm4,
                'Province':province,
                'Parish':parish,
            }
        )
# Call the function and pass the data
# In case of different name of columns in the CSV file, replace the column names accordingly
# If ADMS are not in the database then you need first to import them through import ADMs script

# If dataset already has geography data run this function
upload_sites_withADM(df)

# If dataset doesn't have any fields with ADM data, run this function
upload_sites_noADM(df)
print("Data imported successfully")
