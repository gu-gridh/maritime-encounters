import os
import sys
import django
import json
import pandas as pd
from datetime import datetime
from django.contrib.gis.geos import Point
import numpy as np
import argparse

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maritime.settings')  # Replace 'your_project' with your project's name
django.setup()

from apps.geography.models import ADM0, ADM1, ADM2, ADM3, ADM4, Province,Parish
from apps.resources.models import *

# LandingPoints.objects.all().delete()

# def upload_sites_noADM(data):
#     for row in data.itertuples(index=False):
#         if not pd.isnull(row.Lng) or pd.isnull(row.Lat):
#             point = Point(row.Lng,row.Lat)
#         else:
#             point=None
#         if point != None:
#             try:
#                 adm4 = ADM4.objects.get(geometry__contains=point)
#             except:
#                 adm4 = None
#             try:
#                 adm3 = ADM3.objects.get(geometry__contains=point)
#             except:
#                 adm3 = None
#             try:
#                 adm2 = ADM2.objects.get(geometry__contains=point)
#             except:
#                 adm2 = None
#         if row.Place != None:        
#             site_name = row.Place
#         elif row.Site != None:
#             site_name = row.Site
#         else:
#             site_name = f"{adm2.name}, {adm2.ADM1.name}"
#         Site.objects.update_or_create(
#             name=site_name,
#             defaults={
#                 'coordinates':point,
#                 'ADM0': adm2.ADM1.ADM0 if adm2 != None else None,
#                 'ADM1': adm2.ADM1 if adm2 != None else None,
#                 'ADM2': adm2,
#                 'ADM3': adm3,
#                 'ADM4': adm4,
#             }
#         )

# def calc_date(start,end,period):
#     if 'Iron Age' not in period:
#         start_date = (int(start)*-1)
#         end_date = (int(end)*-1)
#     else:
#         start_date = (int(start)*-1)
#         end_date = int(end)
#     return start_date, end_date
            
def upload_data(data):
    for row in df.itertuples(index=False):
        # if '-' not in [row.Date_start,row.Date_end]:
        #     start_date, end_date = calc_date(row.Date_start,row.Date_end,row.Period)
        # else:
        #     start_date=None
        #     end_date=None
        if not pd.isnull(row.Lng) or pd.isnull(row.Lat):
            point = Point(row.Lng,row.Lat)
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
                
        if row.Place != None:        
            site_name = row.Place
        elif row.Site != None:
            site_name = row.Site
        else:
            site_name = f"{adm2.name}, {adm2.ADM1.name}"
        site_obj=Site.objects.get_or_create(
            name=site_name,
            coordinates=point,
            ADM0 = adm2.ADM1.ADM0 if adm2 != None else None,
            ADM1 = adm2.ADM1 if adm2 != None else None,
            ADM2 = adm2,
            ADM3 = adm3,
            ADM4 = adm4,
            Province=province,
            Parish=parish
        )[0]
        db_object = LandingPoints.objects.get_or_create(
                site = site_obj,
                # related_finds = row.Material_site if row.Material_site != 'None in particular' else None,
                reason = row.Rationale,
                geographic = row.Geographic if row.Geographic != '-' else None,
                start_date = row.start_date,
                end_date = row.end_date,
                source = row.Source
            )[0]
        
        if row.Period not in [None,'Multiple']:
            datings=[]
            periods = str(row.Period).split(',')
            for dating in periods:
                if 'EBA' or 'MBA' or 'LBA':
                    phase_text = Phase.objects.get_or_create(text=dating)[0]
                    dating_text = Period.objects.get_or_create(
                        name='Bronze Age', phase=phase_text)[0]
                    datings.append(dating_text)
                else:
                    dating_text = Period.objects.get_or_create(
                        name=dating)[0]
                    datings.append(dating_text)       
            db_object.period.set(datings)
            
        if row.Subproject != None:
            sps = []
            subprojects = str(row.Subproject).split(',')
            for sp in subprojects:
                sp_text = Subprojects.objects.get_or_create(text=sp)[0]
                sps.append(sp_text)
            db_object.subproject.set(sps)
            
        date_ranges = []    
        for range in ['F3400_3000','F3000_2700','F2700_2300','F2300_2000', 'F2000_1700','F1700_1500','F1500_1400','F1400_1000','F1000_600']:
            if row[range] == 1:
                dates = str(range).replace('F','').split('_')
                range_text = DateRanges.objects.get_or_create(start_date=f"-{dates[0]}", end_date=f"-{dates[1]}")[0]
                date_ranges.append(range_text)
        db_object.active_dates.set(date_ranges)
        
            
            
commands = argparse.ArgumentParser()
commands.add_argument("--files", nargs="*", type=str)
            
if __name__ == '__main__':
    args = commands.parse_args()
    files = args.files
    print(files)
    for file in files:
        name=file.split('/')[-1]
        df = pd.read_excel(file).replace(np.nan, None).replace('[]', None)
        for col in df.columns:
            if ' ' in col:
                new_col = col.replace(' ','_')
                df.rename(columns={col:new_col}, inplace=True)
        # upload_sites_noADM(df)
        upload_data(df)
        print(f"{name}: Data imported successfully")
