


import os
import sys
import django
import json
import pandas as pd
from datetime import datetime
from django.contrib.gis.geos import Point
import numpy as np
from ast import literal_eval
import geopandas as gpd
from deep_translator import GoogleTranslator

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maritime.settings')  # Replace 'your_project' with your project's name
django.setup()

from apps.geography.models import ADM0, ADM1, ADM2, ADM3, ADM4
from apps.resources.models import *

Site.objects.all().delete()
IndividualObjects.objects.all().delete()
AccessionNum.objects.all().delete()


# Define common coordinate system codes
utm_32_n = 'EPSG:25832'
utm_33_n = 'EPSG:25833'
ngo1948 = 'EPSG:4817'

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
            # try:
            #     province = Province.objects.get(geometry__contains=point)
            # except:
            #     province = None
            # try:
            #     parish = Parish.objects.get(geometry__contains=point)
            # except:
            #     parish = None
                
        site_name = row.Art_Id
        Site.objects.update_or_create(
            name=site_name,
            defaults={
                'coordinates':point,
                'ADM0': adm2.ADM1.ADM0 if adm2 != None else None,
                'ADM1': adm2.ADM1 if adm2 != None else None,
                'ADM2': adm2,
                'ADM3': adm3,
                'ADM4': adm4,
                # 'Province':province,
                # 'Parish':parish,
            }
        )



def clean_data(file_path,utm_32_n,utm_33_n,ngo1948):
    # Load the CSV data
    df = pd.read_excel(file_path).replace(np.nan, None).replace('[]', None)

    # Clean coordinates so they're correctly interpreted as float
    df['Kart_Nord'] = df['Kart_Nord'].str.replace(',', '.')
    df['Kart_aust'] = df['Kart_aust'].str.replace(',', '.')

    # print(df['Kart_Nord'].value_counts)

    geom_df = df.dropna(subset=['Kart_Nord','Kart_aust'])
    other_df = df[df['Kart_Nord'].isnull()]

    # Split dataframe by coordinate system
    utm32 = df[df['Kart_Projeksjon'] == 'EU89-UTM; Sone 32']
    utm33 = df[df['Kart_Projeksjon'] == 'EU89-UTM; Sone 33']
    ngo = df[df['Kart_Projeksjon'] == 'NGO1948 Gauss-K; Akse 1']

    # Create a dataframe for each coordinate system and convert to WGS84
    utm_32_n_df = gpd.GeoDataFrame(utm32,geometry=gpd.points_from_xy(utm32['Kart_aust'], utm32['Kart_Nord'], crs=utm_32_n).to_crs('EPSG:4326'))

    utm_33_n_df = gpd.GeoDataFrame(utm33,geometry=gpd.points_from_xy(utm33['Kart_aust'], utm33['Kart_Nord'], crs=utm_33_n).to_crs('EPSG:4326'))

    ngo1948_df = gpd.GeoDataFrame(ngo, geometry=gpd.points_from_xy(ngo['Kart_aust'], ngo['Kart_Nord'], crs=ngo1948).to_crs('EPSG:4326'))

    # Concatenate the converted geodataframes and extract the x and y coordinates expected by the site import function
    geo_df = pd.concat([utm_32_n_df, utm_33_n_df, ngo1948_df, other_df])
    geo_df['x'] = geo_df.get_coordinates()['x']
    geo_df['y'] = geo_df.get_coordinates()['y']

    return geo_df

def upload_data(data):
    for row in data.itertuples(index=False):
        
        # Translate the Norwegian text to English
        type_translated=GoogleTranslator(source='auto',target='en').translate(text=row.Gjenstand).strip().capitalize() if row.Gjenstand != None else None
        form_translated=GoogleTranslator(source='auto',target='en').translate(text=row.Form).strip().capitalize() if row.Form != None else None    
        variant_translated=GoogleTranslator(source='auto',target='en').translate(text=row.Variant).strip().capitalize() if row.Variant != None else None
        material_translated=GoogleTranslator(source='auto',target='en').translate(text=row.Materiale).strip().capitalize() if row.Materiale != None else None
        period_translated=GoogleTranslator(source='auto',target='en').translate(text=row.Periode).strip().capitalize() if row.Periode != None else None
        periods=period_translated.split('/')
        
        # Clean and split text for Dating data that contains specific years
        if row.Datering != None and 'f.kr.' in row.Datering.lower():
            dates_string = row.Datering.lower().replace('f.kr.','').split('-')
            dates = [(date*-1) for date in dates_string] #Make BC years negative for compatibility with Danish data
        elif row.Datering != None and ('e.kr.' in row.Datering.lower() or 'e. kr.' in row.Datering.lower()):
            dates = row.Datering.lower().replace('e.kr.','').replace('e. kr.','').split('-')
        else:
            dates=[None,None]
            
        # Add data to the non-ManyToMany fields    
        db_object = IndividualObjects.objects.get_or_create(
            site = Site.objects.get_or_create(name=row.Art_Id, coordinates=Point(row.x,row.y))[0],
            accession_number = AccessionNum.objects.get_or_create(accession_number=row.Museumsnr)[0],
            # museum = MuseumMeta.objects.get_or_create(museum_number=row.Museumsnr)[0],
            object_type = ObjectDescription.objects.get_or_create(category=ObjectCategories.objects.get_or_create(text='NEEDS REVIEW')[0], subcategory=ObjectSubcategories.objects.get_or_create(subcategory=type_translated)[0])[0],
            type_original = row.Gjenstand,
            form = Form.objects.get_or_create(name=form_translated)[0],
            form_original = row.Form,
            variant = Variant.objects.get_or_create(name=variant_translated)[0],
            variant_original = row.Variant,
            count = row.Antall_gjenstander,
            material = ObjectMaterials.objects.get_or_create(text=material_translated)[0] if material_translated != None else None,
            material_original = row.Materiale,
            period_original = row.Periode,
            orig_coords = f"[{row.Kart_aust},{row.Kart_Nord}]",
            orig_crs = row.Kart_Projeksjon,
            start_date = dates[0] if len(dates)>1 else None,
            end_date = dates[1] if len(dates)>1 else None,
            dating_original= row.Datering,
            object_id = ObjectIds.objects.get_or_create(art_id=row.Art_Id)[0]
        )[0]
        
        # Loop through lists for ManyToMany fields
        datings_list=[]
        if len(periods)>0:
            for item in periods:
                dating_text = Period.objects.get_or_create(
                        name=item)[0]
                datings_list.append(dating_text)
        db_object.period.set(datings_list)
            
        
if __name__ == '__main__':
    file = sys.argv[1]
    geo_df = clean_data(file,utm_32_n,utm_33_n,ngo1948)
    upload_sites_noADM(geo_df)
    if "Museumsnr." in geo_df.columns:
        geo_df.rename(columns={'Museumsnr.':'Museumsnr'},inplace=True)
    if "Antall gjenstander" in geo_df.columns:
        geo_df.rename(columns={"Antall gjenstander":"Antall_gjenstander"},inplace=True)
    upload_data(geo_df)
    
    

