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
        point = None  # ✅ Define default first

        # Handle coordinates safely
        try:
            x = float(row.X)
            y = float(row.Y)
            if not np.isnan(x) and not np.isnan(y):
                pt = Point(x, y)
                if pd.notna(row.EPSG_Code):
                    gdf = gpd.GeoDataFrame(geometry=[geometry.Point(x, y)], crs=int(row.EPSG_Code))
                    wgs_gdf = gdf.to_crs(epsg=4326)
                    lng, lat = wgs_gdf.geometry.get_coordinates().values[0]
                    point = Point(lng, lat)
                else:
                    point = pt
        except Exception as e:
            print(f"[Row {index}] Invalid coordinates (X={row.X}, Y={row.Y}): {e}")


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
            if pd.isna(row.Phase):
                print(f"[Index {index}] Missing 'Phase' value, skipping.")
                phases = []
            else:
                phases = str(row.Phase).split(';')

            for period,phase in zip(periods,phases):
                try:
                    start_date = row.Start_date if pd.notna(row.Start_date) else None
                except:
                    start_date = None
                try:
                    end_date = row.End_date if pd.notna(row.End_date) else None
                except:
                    end_date = None
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
        gable_text = row.Gable.strip().capitalize() if pd.notnull(row.Gable) else None
        gable = GableDescriptor.objects.get_or_create(text=gable_text)[0] if gable_text else None
        

        # Temporarily remove gable
        house_object, created = LNHouses.objects.get_or_create(
            site=site_obj,
            farmstead=row.Farmstead,
            structure_num=row.Structure_number,
            cadastral_num=row.Cadastral_number if 'Cadastral_number' in row_names else None,
            holding_num=row.Holding_number if 'Holding_number' in row_names else None,
            form=form,
            variant=variant,
            orientation=orientation,
            length=row.Length,
            width=row.Width,
            area=row.Area if 'Area' in row_names else None,
            period_original=row.Dating,
            calibrated=True if isinstance(row.Uncalibrated_BP, str) and 'cal' in row.Uncalibrated_BP.lower() else False,
            roofbearing_posts=row.Roofbearing_posts if 'Roofbearing_posts' in row_names else None,
            entrance=row.Entrance if 'Entrance' in row_names else None,
            comments=f"Size descr: {row.Size}; {row.Comments}",
            references=row.Reference,
            url=row.Heritage_DB_Link if 'Heritage_DB_Link' in row_names else None,
            orig_coords = f"{row.X},{row.Y} (CRS: {row.Projection})",
        )

        # Now set the M2M gable if exists
        if gable:
            house_object.gable.set([gable])

        # Then set other M2M fields
        if periods_obj:
            house_object.period.set(periods_obj)
        if dates_obj:
            house_object.dating.set(dates_obj)
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
