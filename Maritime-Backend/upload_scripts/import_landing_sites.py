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

from apps.geography.models import ADM0, ADM1, ADM2, ADM3, ADM4
from apps.resources.models import *

# LandingPoints.objects.all().delete()

def upload_sites_noADM(data):
    for row in data.itertuples(index=False):
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
                
        site_name = row.Place
        Site.objects.update_or_create(
            name=site_name,
            defaults={
                'coordinates':point,
                'ADM0': adm2.ADM1.ADM0 if adm2 != None else None,
                'ADM1': adm2.ADM1 if adm2 != None else None,
                'ADM2': adm2,
                'ADM3': adm3,
                'ADM4': adm4,
            }
        )

def calc_date(start,end,period):
    if 'Iron Age' not in period:
        start_date = (int(start)*-1)
        end_date = (int(end)*-1)
    else:
        start_date = (int(start)*-1)
        end_date = int(end)
    return start_date, end_date
            
def upload_data(data):
    for row in df.itertuples(index=False):
        if '-' not in [row.Date_start,row.Date_end]:
            start_date, end_date = calc_date(row.Date_start,row.Date_end,row.Period)
        else:
            start_date=None
            end_date=None
        db_object = LandingPoints.objects.get_or_create(
                site = Site.objects.get_or_create(name=row.Place, coordinates=Point(row.Lng,row.Lat))[0],
                related_finds = row.Material_site if row.Material_site != 'None in particular' else None,
                reason = row.Reason,
                geographic = row.Geographic_significance if row.Geographic_significance != '-' else None,
                start_date = start_date,
                end_date = end_date,
            )[0]
        
        if row.Period not in [None,'Multiple']:
            datings = []
            date_string = row.Period
            if '-' in date_string:
                periods = date_string.split('-')
            elif ' and ' in date_string:
                periods = date_string.split(' and ')
            elif ' or ' in date_string:
                periods = date_string.split(' or ')
            elif '/' in date_string:
                periods = date_string.split('/')
            elif ' ̶ ' in date_string:
                periods = date_string.split(' ̶ ')
            else:
                periods=date_string
            print(periods)
            
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
        upload_sites_noADM(df)
        upload_data(df)
        print(f"{name}: Data imported successfully")
