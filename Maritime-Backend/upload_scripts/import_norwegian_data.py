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

from apps.geography.models import *
from apps.resources.models import *

# Define common coordinate system codes
utm_32_n = 'EPSG:25832'
utm_33_n = 'EPSG:25833'
ngo1948 = 'EPSG:4817'

def upload_sites_noADM(data):
    for row in data.itertuples(index=False):
        if not pd.isnull(row.y) or pd.isnull(row.x):
            point = Point(row.x,row.y)
        else:
            point = None
        if point is not None:
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
                
        site_name = row.Art_Id
        Site.objects.update_or_create(
            name=site_name,
            defaults={
                'coordinates': point,
                'ADM0': adm2.ADM1.ADM0 if adm2 else None,
                'ADM1': adm2.ADM1 if adm2 else None,
                'ADM2': adm2,
                'ADM3': adm3,
                'ADM4': adm4,
            }
        )


def clean_data(file_path, utm_32_n, utm_33_n, ngo1948):
    # Load the CSV data
    df = pd.read_excel(file_path).replace(np.nan, None).replace('[]', None)

    # Clean coordinates so they're correctly interpreted as float
    geom_df = df.dropna(subset=['Kart_Nord', 'Kart_aust'])
    other_df = df[df['Kart_Nord'].isnull()]

    # Split dataframe by coordinate system
    utm32 = df[df['Kart_Projeksjon'] == 'EU89-UTM; Sone 32']
    utm33 = df[df['Kart_Projeksjon'] == 'EU89-UTM; Sone 33']
    ngo = df[df['Kart_Projeksjon'] == 'NGO1948 Gauss-K; Akse 1']

    # Create a dataframe for each coordinate system and convert to WGS84
    utm_32_n_df = gpd.GeoDataFrame(utm32, geometry=gpd.points_from_xy(utm32['Kart_aust'], utm32['Kart_Nord'], crs=utm_32_n).to_crs('EPSG:4326'))
    utm_33_n_df = gpd.GeoDataFrame(utm33, geometry=gpd.points_from_xy(utm33['Kart_aust'], utm33['Kart_Nord'], crs=utm_33_n).to_crs('EPSG:4326'))
    ngo1948_df = gpd.GeoDataFrame(ngo, geometry=gpd.points_from_xy(ngo['Kart_aust'], ngo['Kart_Nord'], crs=ngo1948).to_crs('EPSG:4326'))

    # Concatenate the converted geodataframes and extract the x and y coordinates expected by the site import function
    geo_df = pd.concat([utm_32_n_df, utm_33_n_df, ngo1948_df, other_df])
    geo_df['x'] = geo_df.get_coordinates()['x']
    geo_df['y'] = geo_df.get_coordinates()['y']

    return geo_df


def upload_data(data):
    for row in data.itertuples(index=False):
        # Check if any required field is missing or empty, log the missing fields
        missing_fields = []
        
        # Check for required fields
        if not row.Art_Id:
            missing_fields.append('Art_Id')
        if not row.x or not row.y:
            missing_fields.append('Coordinates (x, y)')
        if not row.Gjenstand:
            missing_fields.append('Gjenstand (Object Type)')
        if not row.Form:
            missing_fields.append('Form')
        if not row.Variant:
            missing_fields.append('Variant')
        if not row.Materiale:
            missing_fields.append('Materiale')
        if not row.Periode:
            missing_fields.append('Period')
        
        # If there are missing fields, log them and skip this entry
        if missing_fields:
            print(f"Skipping row {row.Index} due to missing fields: {', '.join(missing_fields)}")
            continue

        # Translate the Norwegian text to English
        type_translated = GoogleTranslator(source='norwegian', target='en').translate(text=row.Gjenstand.strip().capitalize()) if row.Gjenstand else None
        form_translated = GoogleTranslator(source='norwegian', target='en').translate(text=row.Form.strip().capitalize()) if row.Form else None
        variant_translated = GoogleTranslator(source='norwegian', target='en').translate(text=row.Variant.strip().title()) if row.Variant else None
        material_translated = GoogleTranslator(source='norwegian', target='en').translate(text=row.Materiale.strip().capitalize()) if row.Materiale else None
        materials = [material.capitalize() for material in material_translated.split('/')] if material_translated else None
        period_translated = GoogleTranslator(source='norwegian', target='en').translate(text=row.Periode.strip().capitalize()) if row.Periode else None
        periods = [period.capitalize() for period in period_translated.split('/')] if period_translated else None
        
        # Add data to the non-ManyToMany fields
        db_object = LNHouses.objects.get_or_create(
            site=Site.objects.get_or_create(name=row.Art_Id, coordinates=Point(row.x, row.y))[0],
            accession_number=AccessionNum.objects.get_or_create(accession_number=row.Museumsnr)[0],
            object_type=ObjectDescription.objects.get_or_create(subcategory=ObjectSubcategories.objects.get_or_create(subcategory=type_translated)[0])[0],
            type_original=row.Gjenstand,
            form_translation=form_translated,
            form_original=row.Form,
            variant=Variant.objects.get_or_create(name=variant_translated)[0],
            variant_original=row.Variant,
            count=row.Antall_gjenstander,
            material_original=row.Materiale,
            period_original=row.Periode,
            orig_coords=f"[{row.Kart_aust},{row.Kart_Nord}]",
            orig_crs=row.Kart_Projeksjon,
            dating_original=row.Datering,
            object_id=ObjectIds.objects.get_or_create(art_id=row.Art_Id)[0]
        )[0]
        
        # Loop through lists for ManyToMany fields
        datings_list = []
        category_list = []
        materials_list = []
        
        if periods:
            for item in periods:
                if 'Earl' in item or 'Late' in item or 'Old' in item or 'Younger' in item or 'Middle' in item:
                    dating_text = Period.objects.get_or_create(name=item.title().replace('Older', '').replace('Younger', '').replace('Early', '').replace('Late', '').replace('Earlier', '').replace('Old', '').replace('Eolithic', 'Neolithic').replace('Middle', '').strip(), phase=Phase.objects.get_or_create(text=item.title().replace('Older', 'Early').replace('Younger', 'Late').replace('Eolithic', 'Neolithic').strip())[0])[0]
                else:
                    dating_text = Period.objects.get_or_create(
                        name=item.title(), phase=None)[0]
                datings_list.append(dating_text)
        db_object.period.set(datings_list)
        
        if type_translated == 'Dagger':
            category_text = ObjectCategories.objects.get_or_create(text='Weapons')[0]
            category_list.append(category_text)
        elif type_translated == 'Shaft hole Axe':
            categories = ['Tools', 'Weapons']
            for category in categories:
                category_text = ObjectCategories.objects.get_or_create(text=category)[0]
                category_list.append(category_text)
        elif type_translated == 'Sickle':
            category_text = ObjectCategories.objects.get_or_create(text='Tools')[0]
            category_list.append(category_text)
        else:
            category_text = ObjectCategories.objects.get_or_create(text='Needs Review')[0]
            category_list.append(category_text)
        db_object.object_type.category.set(category_list)
        
        if materials:
            for item in materials:
                material = ObjectMaterials.objects.get_or_create(text=item.strip().title())[0]
                materials_list.append(material)
        db_object.material.set(materials_list)



if __name__ == '__main__':
    file = sys.argv[1]
    geo_df = clean_data(file, utm_32_n, utm_33_n, ngo1948)
    upload_sites_noADM(geo_df)
    if "Museumsnr." in geo_df.columns:
        geo_df.rename(columns={'Museumsnr.': 'Museumsnr'}, inplace=True)
    if "Antall gjenstander" in geo_df.columns:
        geo_df.rename(columns={"Antall gjenstander": "Antall_gjenstander"}, inplace=True)
    upload_data(geo_df)
