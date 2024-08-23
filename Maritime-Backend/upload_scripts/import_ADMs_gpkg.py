import os
import sys
import django
import pandas as pd
from django.contrib.gis.geos import Point
from django.contrib.gis.geos import GEOSGeometry
import geopandas as gpd
import fiona
import argparse

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maritime.settings')  # Replace 'your_project' with your project's name
django.setup()

from apps.geography.models import ADM0, ADM1, ADM2, ADM3, ADM4, Province, Parish

#Download geopackage from https://gadm.org/download_world.html (file link: https://geodata.ucdavis.edu/gadm/gadm4.1/gadm_410-gpkg.zip)

#Path to geopackage file - you may need to do some preprocessing to fix Cork (Ireland) and NA values
# gpkg = ''

#Generate a list of the layers in the geopackage
# layers = fiona.listlayers(gpkg)


# ADM0.objects.all().delete()
# ADM1.objects.all().delete()
# ADM2.objects.all().delete()
# ADM3.objects.all().delete()
# ADM4.objects.all().delete()

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
        
def upload_province(data):
    for row in data.itertuples(index=False):
        adm0 = ADM0.objects.get(code='SWE', name='Sweden')
        Province.objects.get_or_create(
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
        Parish.objects.get_or_create(
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

# Add arguments for the CLI
commands = argparse.ArgumentParser()
commands.add_argument("file", type=str) #use a single file
commands.add_argument("data_format", type=str, choices=['adm','province','parish'], help="The level of data being uploaded, e.g. GADM data, Swedish provinces, etc. Choice are adm, province, or parish")
commands.add_argument("--selection", nargs="*", type=str, help="Add preferred country names separated by a space to limit the data uploaded") #converts the country selection to a list
commands.add_argument("--adm_levels", nargs="*", type=int, help="Add preferred GADM levels as integers. If wanting to upload all layers, use 0 1 2 3 4") #converts adm level integers to a list

# call function based on your need and pass the data as argument
# loops through all layers in geopackage to create a dataframe with wkt geometry fields
# layers are named using ADM levels, change statements based on your dataset

if __name__ == '__main__':
    args = commands.parse_args()
    file = args.file
    countries = args.selection
    adm_list = args.adm_levels
    data_format = args.data_format
    
    
    if data_format == 'adm':
        layers = fiona.listlayers(file)
        
        for layer in adm_list:
            data = gpd.read_file(file, layer=layers[layer]).to_wkt()
            if layer==0:
                upload_adm0(data[data.COUNTRY.isin(countries)]) if countries != None else upload_adm0(data)
            if layer==1:
                upload_adm1(data[data.COUNTRY.isin(countries)]) if countries != None else upload_adm0(data)
            if layer==2:
                upload_adm2(data[data.COUNTRY.isin(countries)]) if countries != None else upload_adm0(data)
            if layer==3:
                upload_adm3(data[data.COUNTRY.isin(countries)]) if countries != None else upload_adm0(data)
            if layer==4:
                upload_adm4(data[data.COUNTRY.isin(countries)]) if countries != None else upload_adm0(data)
            else:
                pass
    if data_format == 'province':
        df = pd.read_csv(file)
        upload_province(df)
        
    if data_format == 'parish':
        df = pd.read_csv(file)
        upload_parish(df)
    
    else:
        print("No data to import, check the data format is correct")
   


print("Data imported successfully")

