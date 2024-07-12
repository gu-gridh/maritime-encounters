import os
import sys
import django
import pandas as pd
from django.contrib.gis.geos import Point
from django.contrib.gis.geos import GEOSGeometry
import geopandas as gpd
import fiona

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maritime.settings')  # Replace 'your_project' with your project's name
django.setup()

from apps.geography.models import ADM0, ADM1, ADM2, ADM3, ADM4, ADM5, Province, Parish

#Download geopackage from https://gadm.org/download_world.html (file link: https://geodata.ucdavis.edu/gadm/gadm4.1/gadm_410-gpkg.zip)

#Path to geopackage file - you may need to do some preprocessing to fix Cork (Ireland) and NA values
gpkg = ''

#Generate a list of the layers in the geopackage
layers = fiona.listlayers(gpkg)


ADM0.objects.all().delete()
ADM1.objects.all().delete()
ADM2.objects.all().delete()
ADM3.objects.all().delete()
ADM4.objects.all().delete()
ADM5.objects.all().delete()

# Import data into ADM levels
def upload_adm0(data):
    for adm0_code, adm0_name, geometry in data[['GID_0', 'COUNTRY' , 'geometry']].drop_duplicates().values:
        ADM0.objects.update_or_create(
            code=adm0_code,
            defaults={
                'name': adm0_name, 
                'geometry': geometry}
        )

def upload_adm1(data):
    for row in data.itertuples(index=False):
        try:
            adm0 = ADM0.objects.get(name = row.COUNTRY)
            ADM1.objects.update_or_create(
                code=row.GID_1,
                name = row.NAME_1, 
                defaults={
                    'name_translation': row.VARNAME_1,
                    'geometry': row.geometry, 
                    'ADM0': adm0,
                    'type': row.TYPE_1,
                    'type_translation': row.ENGTYPE_1
                    }
            )
        except:
            pass

        
def upload_adm2(data):
    for row in data.itertuples(index=False):
        try:
            adm1 = ADM1.objects.get(code=row.GID_1, name=row.NAME_1)
            ADM2.objects.update_or_create(
                code=row.GID_2,
                name = row.NAME_2, 
                defaults={
                    'name_translation': row.VARNAME_2,
                    'geometry': row.geometry, 
                    'ADM1': adm1,
                    'type': row.TYPE_2,
                    'type_translation': row.ENGTYPE_2
                    }
            )
        except:
            pass
                

def upload_adm3(data):
    for row in data.itertuples(index=False):
        try:
            adm2 = ADM2.objects.get(name=row.NAME_2,code=row.GID_2)
            ADM3.objects.update_or_create(
                code=row.GID_3,
                name = row.NAME_3, 
                defaults={
                    'name_translation': row.VARNAME_3,
                    'geometry': row.geometry, 
                    'ADM2': adm2,
                    'type': row.TYPE_3,
                    'type_translation': row.ENGTYPE_3
                    }
            )
        except:
            pass

def upload_adm4(data):
    for row in data.itertuples(index=False):
        try:
            adm3 = ADM3.objects.get(code=row.GID_3, name=row.NAME_3, ADM2__code=row.GID_2, ADM2__name=row.NAME_2)
            ADM4.objects.update_or_create(
                code=row.GID_4,
                defaults={
                    'name': row.NAME_4, 
                    'name_translation': row.VARNAME_4,
                    'geometry': row.geometry, 
                    'ADM3': adm3,
                    'type': row.TYPE_4,
                    'type_translation': row.ENGTYPE_4
                    }
        )
        except:
            pass


def upload_adm5(data):
    for row in data.itertuples(index=False):
        try:
            adm4 = ADM4.objects.get(code=row.GID_4, name=row.NAME_4, ADM3__code=row.GID_3, ADM3__name=row.NAME_3)
            ADM5.objects.update_or_create(
                code=row.GID_5,
                defaults={
                    'name': row.NAME_5, 
                    'name_translation': row.VARNAME_5,
                    'geometry': row.geometry, 
                    'ADM4': adm4,
                    'type': row.TYPE_5,
                    'type_translation': row.ENGTYPE_5
                    }
            )
        except:
            pass

# call function based on your need and pass the data as argument
# loops through all layers in geopackage to create a dataframe with wkt geometry fields
# layers are named using ADM levels, change statements based on your dataset

for layer in layers:
    data = gpd.read_file(gpkg, layer=layer).to_wkt()
    if '0' in layer:
        upload_adm0(data[data.COUNTRY.isin(['Germany','Denmark','Sweden','Norway','France','United Kingdom','Ireland','Poland','NA'])])
    elif '1' in layer:
        upload_adm1(data[data.COUNTRY.isin(['Germany','Denmark','Sweden','Norway','France','United Kingdom','Ireland','Poland','NA'])])
    elif '2' in layer:
        upload_adm2(data[data.COUNTRY.isin(['Germany','Denmark','Sweden','Norway','France','United Kingdom','Ireland','Poland','NA'])])
    elif '3' in layer:
        upload_adm3(data[data.COUNTRY.isin(['Germany','Denmark','Sweden','Norway','France','United Kingdom','Ireland','Poland','NA'])])
    elif '4' in layer:
        upload_adm4(data[data.COUNTRY.isin(['Germany','Denmark','Sweden','Norway','France','United Kingdom','Ireland','Poland'])])
    # elif '5' in layer:
    #     upload_adm5(data[data.COUNTRY.isin(['Germany','Denmark','Sweden','Norway','France','United Kingdom','Ireland','Poland'])])


print("Data imported successfully")

