import os
import sys
import django
import pandas as pd
import geopandas as gpd
from shapely import geometry
from django.contrib.gis.geos import Point
import numpy as np
import argparse

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maritime.settings')
django.setup()

from apps.geography.models import ADM0, ADM1, ADM2, ADM3, ADM4, Province, Parish
from apps.resources.models import *


def import_individuals(data):
    row_names = data.columns
    for index, row in data.iterrows():
        # Handle coordinates
        lng = row.get('Lng') or row.get('Longitude') or row.get('lng')
        lat = row.get('Lat') or row.get('Latitude') or row.get('lat')

        if pd.notna(lng) and pd.notna(lat):
            try:
                epsg_code = int(row.EPSG_Code)
                temp_df = pd.DataFrame({'geometry': [Point(lng, lat)]}, index=[0])
                gdf = gpd.GeoDataFrame(temp_df, geometry='geometry', crs=epsg_code)
                wgs_gdf = gdf.to_crs(epsg=4326)
                point = Point(wgs_gdf.geometry.x.values[0], wgs_gdf.geometry.y.values[0])
            except Exception as e:
                print(f"CRS transformation failed at index {index}: {e}")
                point = Point(lng, lat)
        else:
            point = None  # or some fallback

        # Ask about County field
        # Administrative division assignments
        adm4 = adm3 = adm2 = adm1 = country = province = parish = None
        if point:
            try:
                adm4 = ADM4.objects.get(geometry__contains=point)
            except:
                pass
            try:
                adm3 = ADM3.objects.get(geometry__contains=point)
            except:
                pass
            try:
                adm2 = ADM2.objects.get(geometry__contains=point, name=row.County)
            except:
                pass
            try:
                adm1 = ADM1.objects.get(geometry__contains=point)
            except:
                pass
            try:
                country = ADM0.objects.get(geometry__contains=point)
            except:
                pass
            try:
                province = Province.objects.get(geometry__contains=point)
            except:
                pass
            try:
                parish = Parish.objects.get(geometry__contains=point)
            except:
                pass
        
        # Site Name determination
        if not pd.isnull(row.Place_name):        
            site_name = row.Place_name
        else:
            site_name = f"{adm2.name}, {adm2.ADM1.name}" if adm2 else None

        site_obj = Site.objects.get_or_create(
            name=site_name,
            coordinates=point,
            ADM0=country,
            ADM1=adm1,
            ADM2=adm2,
            ADM3=adm3,
            ADM4=adm4,
            Province=province,
            Parish=parish
        )[0]

        periods_obj = []
        # if not pd.isnull(row.Period):
        #     periods = row.Period.split("or")
        #     for period in periods:
        #         start_date = row.Start_date if pd.notna(row.Start_date) else None
        #         end_date = row.End_date if pd.notna(row.End_date) else None
        #         phase_obj, _ = Phase.objects.get_or_create(text=row.Phase)

        #         period_obj, _ = Period.objects.get_or_create(
        #             name=period.strip(),
        #             start_date=start_date,
        #             end_date=end_date,
        #             phase=phase_obj
        #         )
        #         periods_obj.append(period_obj)

        if pd.notna(row.Period) and pd.notna(row.Phase):
            periods = row.Period.split(';')
            phases = row.Phase.split(';')
            for period, phase in zip(periods, phases):
                start_date = row.Start_date if pd.notna(row.Start_date) else None
                end_date = row.End_date if pd.notna(row.End_date) else None
                phase_obj, _ = Phase.objects.get_or_create(text=phase.strip())
                period_obj, _ = Period.objects.get_or_create(
                    name=period.strip(),
                    start_date=start_date,
                    end_date=end_date,
                    phase=phase_obj
                )
                periods_obj.append(period_obj)


        # Material
        materials_obj = []
        if not pd.isnull(row.Material):
            materials = row.Material.split(",")
            for material in materials:
                material_obj = ObjectMaterials.objects.get_or_create(text=material.strip())[0]
                materials_obj.append(material_obj)
        
        # Museum and Accession Number
        try: 
            museum = MuseumMeta.objects.get_or_create(museum=row.Museum)[0] if not pd.isnull(row.Museum) else None
            accession_num = AccessionNum.objects.get_or_create(
                accession_number=row.accession_num if 'accession_num' in row_names else None
            )[0]
        except:
            accession_num = None
            museum = None
        # Object Category and Description
        obj_cat = []
        try:
            categories = row.Object_category.split(",") if not pd.isnull(row.Object_category) else []
            for category in categories:
                category_obj = ObjectCategories.objects.get_or_create(text=category.strip().capitalize())[0]
                obj_cat.append(category_obj)
        except:
            pass
            
        
        # try:
        #     object_description = ObjectDescription.objects.get_or_create(
        #         category=obj_cat[0]
        #     )[0]
        #     object_description.category.set(obj_cat)
        # except: 
        #     object_description = None

        try:
            sub_categories = ObjectSubcategories.objects.get_or_create(subcategory=row.Object_subcategory.capitalize())[0] if not pd.isnull(row.Object_subcategory) else None
            categories = ObjectCategories.objects.get_or_create(category=row.Object_category.capitalize())[0] if not pd.isnull(row.Objcet_category) else None
            object_description = ObjectDescription.objects.get_or_create(category=categories,subcategory=sub_categories)[0]
        except:
            object_description = None

        # Variant and Form
        variant = Variant.objects.get_or_create(name=row.Variant)[0] if not pd.isnull(row.Variant) else None
        form = Form.objects.get_or_create(name=row.Form)[0] if not pd.isnull(row.Form) else None
        # Context
        try:
            context = ContextKeywords.objects.get_or_create(text=row.Context.capitalize())[0] if not pd.isnull(row.Context) else None
        except:
            context = None
        

        # Creating the object
        individual_object = IndividualObjects.objects.update_or_create(
            site=site_obj,
            accession_number=accession_num,
            museum=museum ,
            object_type=object_description,
            type_original=row.Object_type if 'Object_type' in row_names else None,
            form=form,
            # form_translation=row.Form_description,
            form_original=row.Form,
            variant=variant,
            variant_original=row.Variant,
            count=1 if 'Count' not in row_names else row.Count,  # Update this if count info is in the data
            context=context,
            orig_coords=f"{row.Lat}, {row.Lng}" if point else None,
            start_date=row.Start_date,
            end_date=row.End_date,
            dating_original=row.Period,
            references = row.References if 'References' in row_names else None,
        )[0]

        # Setting Many-to-Many fields
        if materials_obj:
            individual_object.material.set(materials_obj)
        if periods_obj:
            individual_object.period.set(periods_obj)

        individual_object.save()

commands = argparse.ArgumentParser()
commands.add_argument("--files", nargs="*", type=str)
            
if __name__ == '__main__':
    args = commands.parse_args()
    files = args.files
    for file in files:
        name = file.split('/')[-1]
        data = pd.read_excel(file)
        sheets = pd.ExcelFile(file).sheet_names

        for sheet in sheets:
            print(f"Importing {name} data from {sheet} sheet")
            df = pd.read_excel(file, sheet_name=sheet)
            import_individuals(df)

        print(f"{name}: Data imported successfully")
