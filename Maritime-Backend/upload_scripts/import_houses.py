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

def import_houses(data):
    row_names = data.columns
    for index, row in data.iterrows():
        # Handle coordinates
        if not pd.isnull(row.X) and not pd.isnull(row.Y):
            if row.CRS == None:
                point = Point(row.X, row.Y)
            else:
                gdf = gpd.GeoDataFrame([row],geometry=[Point(row.X,row.Y)],crs=int(row.EPSG_Code))
                wgs_gdf=gdf.to_crs(epsg=4326)
                lng,lat=wgs_gdf.geometry.get_coordinates().values[0]
                point = Point(lng,lat)
        else:
            point = None

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
                adm2 = ADM2.objects.get(geometry__contains=point)
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
        if not pd.isnull(row.Farmstead) and not pd.isnull(row.County):        
            site_name = f"{row.Farmstead}, {row.County}"
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

        if not pd.isnull(row.Period):
            periods=row.Period.split(';')
            phases=row.Phase.split(';')
            for period,phase in zip(periods,phases):
                start_date = row.Start_date if pd.notna(row.Start_date) else None
                end_date = row.End_date if pd.notna(row.End_date) else None
                phase_obj, _ = Phase.objects.get_or_create(text=phase)

                period_obj, _ = Period.objects.get_or_create(
                    name=period.strip(),
                    start_date=start_date,
                    end_date=end_date,
                    phase=phase_obj
                )
                periods_obj.append(period_obj)

        dates_obj = []
        if not pd.isnull(row.Uncalibrated_BP):
            dates = row.Uncalibrated_BP.split(';')
            for date in dates:
                lab = None
                sample = date.split(':')[0] if ':' in date else None
                date_str = date.split(':')[1] if ':' in date else date
                date_obj, _ = CalibratedDate.objects.get_or_create(lab=lab,sample=sample,date=date_str
                )
                dates_obj.append(date_obj)

        ext_consts_obj = []
        if not pd.isnull(row.Exterior_construction):
            constructs = row.Exterior_construction.split(';')
            for construct in constructs:
                construct_obj = ExteriorDescriptor.objects.get_or_create(text=construct.strip().capitalize())[0]
                ext_consts_obj.append(construct_obj)

        #Form is the type of structure (e.g. longhouse), variant is the subtype (e.g. two-aisled)
        variant = Variant.objects.get_or_create(name=row.Type.strip().capitalize())[0] if not pd.isnull(row.Type) else None
        # form = Form.objects.get_or_create(name=row.Form)[0] if not pd.isnull(row.Form) else None
        form = Form.objects.get_or_create(name='House')[0]
        orientation = Orientation.objects.get_or_create(text=row.Orientation)[0]
        gable = GableDescriptor.objects.get_or_create(text=row.Gable.strip().capitalize())[0]


        

        # Creating the object
        house_object = LNHouses.objects.update_or_create(
            site=site_obj,
            farmstead = row.Farmstead,
            structure_num = row.Sturcture_number,
            cadastral_num  = row.Cadastral_number if 'Cadastral_number' in row_names else None,
            holding_num = row.Holding_number if 'Holding_number' in row_names else None,
            form = form,
            variant = variant,
            orientation = orientation,
            length = row.Length,
            width = row.Width,
            area = row.Area if 'Area' in row_names else None,
            period_original = row.Dating,
            calibrated = True if 'cal' in row.Uncalibrated_BP else False,
            gable = gable,
            roofbearing_posts = row.Roofbearing_posts if 'Roofbearing_posts' in row_names else None,
            entrance = row.Entrance if 'Entrace' in row_names else None,
            comments = row.Comments,
            references = row.Reference,
            url = row.Heritage_DB_Link if 'Heritage_DB_Link' in row_names else None,
            orig_coords = f"{row.X},{row.Y} (CRS: {row.Projection})"
        )[0]

        # Setting Many-to-Many fields
        if periods_obj:
            house_object.period.set(periods_obj)
        if dates_obj:
            house_object.uncal_dating.set(dates_obj)
        if ext_consts_obj:
            house_object.exterior_construction.set(ext_consts_obj)
        house_object.save()

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
            import_houses(df)

        print(f"{name}: Data imported successfully")
