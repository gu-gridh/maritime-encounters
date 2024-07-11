import os
import sys
import django
import json
import pandas as pd
from datetime import datetime
from django.contrib.gis.geos import Point


# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maritime.settings')

# Set up Django
django.setup()

# Replace 'your_app' with the name of your Django app
from apps.resources.models import *
from apps.geography.models import ADM0, ADM1, ADM2, ADM3, ADM4, ADM5

csv_file_path = ''

# Load the CSV data
df = pd.read_csv(csv_file_path)

# Import data into caches
site_cache = {}
entry_num_cache = {}
lit_num_cache = {}
accession_num_cache = {}
locations_cache = {}
context_cache = {}
museum_collection_cache = {}
finds_cache = {}
context_detail_cache = {}


for place, entry_num, adm0, adm1, adm2, adm3, adm4, province, parish, x, y in df[['place', 'entryNo', 'ADM_0', 'ADM_1', 'ADM_2', 'ADM_3', 'ADM_4', 'province', 'parish', 'x', 'y']].values:
    site = Site.objects.get_or_create(
        name=f"{entry_num}, {place}",
        ADM0__name=adm0,
        ADM1__name=adm1,
        ADM2__name=adm2,
        ADM3__name=adm3,
        ADM4__name=adm4,
        Province__name=province,
        Parish__name=parish,
        coordinates=Point(y, x)
    )
    site_cache[entry_num] = site

for entry_num, lit_num, accession_num in df[['entryNo', 'literatureNo', 'accessionNo']].drop_duplicates().values:
    entryNo, created = EntryNum.objects.get_or_create(
        entry_number=entry_num)
    entry_num_cache[entry_num] = entryNo
    litNo, created = LiteratureNum.objects.get_or_create(
        literature_number=lit_num)
    lit_num_cache[lit_num] = litNo
    accessionNo, created = AccessionNum.objects.get_or_create(
        accession_number=accession_num)
    accession_num_cache[accession_num] = accessionNo


for location_name, place, entry_num in df[['placeDetail', 'place', 'entryNo']].drop_duplicates().values:
    location_name = location_name[0]
    location, created = Location.objects.get_or_create(
        site__name=', '.join(entry_num, place),
        location_detail=location_name
    )
    locations_cache[location_name] = location

for context_name in df[['mainContext']].drop_duplicates().values:
    context_name = context_name[0]
    context, created = Context.objects.get_or_create(
        text=context_name.capitalize()
    )
    context_cache[context_name] = context

for museum_collection in df[['museumCollection']].drop_duplicates().values:
    museum_collection = museum_collection[0]
    collection, created = MuseumCollection.objects.get_or_create(
        collection=museum_collection,
    )
    museum_collection_cache[museum_collection] = collection

for context_name in df[['findContext']].drop_duplicates().values:
    context_name = context_name[0]
    context, created = FindContext.objects.get_or_create(
        text=context_name.capitalize()
    )
    finds_cache[context_name] = context

for context_name in df[['detailContext']].drop_duplicates().values:
    context_name = context_name[0]
    context, created = ContextDetail.objects.get_or_create(
        text=context_name.capitalize()
    )
    context_detail_cache[context_name] = context


for row in df.itertuples(index=False):
    site_sample = site_cache.get(row.site_name)
    entry_sample = entry_num_cache.get(row.entryNo)
    lit_sample = lit_num_cache.get(row.literatureNo)
    accession_sample = accession_num_cache.get(row.accessionNo)
    location_sample = locations_cache.get(row.placeDetail)
    context_sample = context_cache.get(row.mainContext)
    museum_sample = museum_collection_cache.get(row.museumCollection)
    finds_sample = finds_cache.get(row.findContext)
    context_detail_sample = context_detail_cache.get(row.detailContext)

    Metalwork.objects.update_or_create(
        entry_num=entry_sample,
        literature_num=lit_sample,
        accession_num=accession_sample,
        accession_certain=row.accessionCertain,
        museum=None,
        museum_collection=museum_sample,
        museum_certain=row.museumCertain,
        location=location_sample,
        location_certain=row.locationCertain,
        coord_system=row.origCoordSys,
        orig_coords=[row.xOrig, row.yOrig],
        primary_context=context_sample,
        primary_context_certain=row.mainContextCertain,
        find_context=finds_sample,
        find_context_certain=row.findContextCertain,
        context_detail=context_detail_sample,
        context_detail_certain=row.detailContextCertain,
        # context_keywords=
        multiperiod=row.multiPeriod,
        # dating=
        date_string=row.datingString,
        dating_certain=row.datingCertain,
        dendro_date=row.dendroDate,
        radiocarbon_date=row.radioCarbonDate,
        radiocarbon_years=row.radioCarbonYear,
        radiocarbon_std=row.stdDeviation,
        comments=row.comments,
        # certain_context_descriptors=
        # uncertain_context_descriptors=

    )
json_file_path = ''

# Load the CSV data
df = pd.json_normalize(json.load(open(json_file_path)))
# Import data into ADM levels

for row in df.rows(index=False):
    ()


print("Data imported successfully")
