import os
import django
import pandas as pd
from django.contrib.gis.geos import Point
from django.contrib.gis.geos import GEOSGeometry

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maritime.settings')  # Replace 'your_project' with your project's name
django.setup()

from apps.geography.models import ADM0, ADM1, ADM2, ADM3, ADM4, ADM5, Province, Parish

# Path to your CSV file
csv_file_path = ''

# Load the CSV data
df = pd.read_csv(csv_file_path)

# Import data into ADM levels
def upload_adm0(data):
    for adm0_code, adm0_name, geometry in data[['GID_0', 'COUNTRY' , 'WKT']].drop_duplicates().values:
        ADM0.objects.update_or_create(
            code=adm0_code,
            defaults={
                'name': adm0_name, 
                'geometry': geometry}
        )

def upload_adm1(data):
    for row in data.itertuples(index=False):
        adm0 = ADM0.objects.get(code=row.GID_0, name=row.COUNTRY)
        adm0 = ADM0.objects.get(code=row.GID_0, name=row.COUNTRY)
        ADM1.objects.get_or_create(
            code=row.GID_1,
            defaults={
                'name': row.NAME_1, 
                'name_translation': row.VARNAME_1,
                'geometry': row.WKT, 
                'ADM0': adm0,
                'type': row.TYPE_1,
                'type_translation': row.ENGTYPE_1
                }
        )
        
def upload_adm2(data):
    for row in data.itertuples(index=False):
        adm1 = ADM1.objects.get(code=row.GID_1)
        if adm1:
            ADM2.objects.update_or_create(
                code=row.GID_2,
                defaults={
                    'name': row.NAME_2, 
                    'name_translation': row.VARNAME_2,
                    'geometry': row.WKT, 
                    'ADM1': adm1,
                    'type': row.TYPE_2,
                    'type_translation': row.ENGTYPE_2
                    }
            )

def upload_adm3(data):
    for row in data.itertuples(index=False):
        adm2 = ADM2.objects.get(code=row.GID_2)
        ADM3.objects.update_or_create(
            code=row.GID_3,
            defaults={
                'name': row.NAME_3, 
                'name_translation': row.VARNAME_3,
                'geometry': row.WKT, 
                'ADM2': adm2,
                'type': row.TYPE_3,
                'type_translation': row.ENGTYPE_3
                }
        )

def upload_adm4(data):
    for row in data.itertuples(index=False):
        adm3 = ADM3.objects.get(code=row.GID_3, name=row.NAME_3, ADM2__code=row.GID_2, ADM2__name=row.NAME_2)
        ADM4.objects.update_or_create(
            code=row.GID_4,
            defaults={
                'name': row.NAME_4, 
                'name_translation': row.VARNAME_4,
                'geometry': row.WKT, 
                'ADM3': adm3,
                'type': row.TYPE_4,
                'type_translation': row.ENGTYPE_4
                }
        )

def upload_adm5(data):
    for row in df.itertuples(index=False):
        adm4 = ADM4.objects.get(code=row.GID_4, name=row.NAME_4, ADM3__code=row.GID_3, ADM3__name=row.NAME_3)
        ADM5.objects.update_or_create(
            code=row.GID_5,
            defaults={
                'name': row.NAME_5, 
                'name_translation': row.VARNAME_5,
                'geometry': row.WKT, 
                'ADM4': adm4,
                'type': row.TYPE_5,
                'type_translation': row.ENGTYPE_5
                }
        )

def upload_province(data):
    for row in data.itertuples(index=False):
        adm0 = ADM0.objects.get(code='SWE', name='Sweden')
        Province.objects.update_or_create(
            name=row.LandskapNamn,
            defaults={
                'code':row.LandskapKod,
                'name_translation': row.LandskapNamn,
                'geometry': row.WKT, 
                'type': 'Landskap',
                'type_translation': 'Province',
                'country': adm0,
                }
        )

def upload_parish(data):
    for row in data.itertuples(index=False):
        adm0 = ADM0.objects.get(code='SWE', name='Sweden')
        adm1 = ADM1.objects.get(code=row.GID_1)
        if pd.notna(row.GID_2):
            adm2 = ADM2.objects.get(code=row.GID_2)
        else:
            adm2 = None
        province = Province.objects.get(code=row.LandskapKod, name=row.LandskapNamn, country=adm0)
        Parish.objects.update_or_create(
            name= row.sockenstadnamn, 
            defaults={
                'code':row.omradesnummer,            
                'name_translation': row.sockenstadnamn,
                'geometry': row.WKT, 
                'type': 'Socken',
                'type_translation': 'Parish',
                'country': adm0,
                'county': adm1,
                'municipality': adm2,
                'province': province
                }
        )


# call function based on your need and pass the data as argument
# In case if fields names are different, you can change the field names in the function
# upload_adm0(df)   
print("Data imported successfully")

