import os
import sys
import django
import pandas as pd
from django.contrib.gis.geos import Point
import numpy as np
from ast import literal_eval
from django.db import transaction

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maritime.settings')

# Set up Django
django.setup()

# Replace 'your_app' with the name of your Django app
from apps.resources.models import *
from apps.geography.models import ADM0, ADM1, ADM2, ADM3, ADM4, ADM5, Province, Parish

csv_file_path = '../../resources/c_horn_metalwork_v2.csv'

# Load the CSV data
df = pd.read_csv(csv_file_path).replace(np.nan, None).replace('[]', None)

# Function to get or create objects
def get_or_create_object(model, **kwargs):
    obj, created = model.objects.get_or_create(**kwargs)
    return obj

# Clear current data in database
# Uncomment these lines if you need to clear the existing data
# Site.objects.all().delete()
# Location.objects.all().delete()
# Metalwork.objects.all().delete()
# ContextKeywords.objects.all().delete()
# Period.objects.all().delete()
# ObjectCount.objects.all().delete()
# ObjectMaterials.objects.all().delete()
# ObjectDescription.objects.all().delete()
# ObjectSubcategories.objects.all().delete()
# ObjectCategories.objects.all().delete()
# ContextDetail.objects.all().delete()
# ContextFindsCategories.objects.all().delete()
# ContextFindsSubcategories.objects.all().delete()

# Create sites and add administrative data
with transaction.atomic():
    for place, adm0n, adm1n, adm2n, adm3n, adm4n, provincen, parishn, x, y in df[['place', 'ADM_0', 'ADM_1', 'ADM_2', 'ADM_3', 'ADM_4', 'province', 'parish', 'x', 'y']].drop_duplicates(['x', 'y', 'place']).values:
        site_name = place or f"{parishn}: {y}, {x}" or f"{provincen}: {y}, {x}" or f"{adm4n}: {y}, {x}" or f"{adm3n}: {y}, {x}" or f"{adm2n}: {y}, {x}"
        adm0 = ADM0.objects.filter(name=adm0n).first() if adm0n else None
        adm1 = ADM1.objects.filter(name=adm1n).first() if adm1n else None
        adm2 = ADM2.objects.filter(name=adm2n, ADM1__name=adm1n).first() if adm2n else None
        adm3 = ADM3.objects.filter(name=adm3n, ADM2__name=adm2n).first() if adm3n else None
        adm4 = ADM4.objects.filter(name=adm4n, ADM3__name=adm3n, ADM3__ADM2__name=adm2n).first() if adm4n else None
        province = Province.objects.filter(name=provincen).first() if provincen else None
        parish = Parish.objects.filter(name=parishn).first() if parishn else None
        point = Point(x, y) if not pd.isnull(y) and not pd.isnull(x) else None
        
        Site.objects.get_or_create(
            name=site_name,
            ADM0=adm0,
            ADM1=adm1,
            ADM2=adm2,
            ADM3=adm3,
            ADM4=adm4,
            Province=province,
            Parish=parish,
            coordinates=point
        )

# Add finds categories to database
desc_df = pd.json_normalize(literal_eval(df['certainContextDescriptors'][0]))
for category in desc_df.columns:
    ContextFindsCategories.objects.get_or_create(text=category.capitalize())

# Function to process row data
def process_row(row):
    site_name = row.place or f"{row.parish}: {row.y}, {row.x}" or f"{row.province}: {row.y}, {row.x}" or f"{row.ADM_4}: {row.y}, {row.x}" or f"{row.ADM_3}: {row.y}, {row.x}" or f"{row.ADM_2}: {row.y}, {row.x}" or "NAME IS MISSING"

    site = Site.objects.filter(coordinates=Point(row.x, row.y), name=site_name).first()
    
    entry_num = get_or_create_object(EntryNum, entry_number=row.entryNo)
    literature_num = get_or_create_object(LiteratureNum, literature_number=row.literatureNo)
    accession_num = get_or_create_object(AccessionNum, accession_number=row.accessionNo)
    
    collection = get_or_create_object(MuseumCollection, collection=row.museumCollection.strip().title()) if row.museumCollection else None
    location = get_or_create_object(Location, site=site, location_detail=row.placeDetail)
    
    main_context = get_or_create_object(Context, text=row.mainContext)
    find_context = get_or_create_object(FindContext, text=row.findContext)
    context_detail = get_or_create_object(ContextDetail, text=row.detailContext if row.detailContext else 'Unknown')

    metalwork, created = Metalwork.objects.update_or_create(
        entry_num=entry_num,
        literature_num=literature_num,
        accession_num=accession_num,
        defaults={
            'accession_certain': row.accessionCertain,
            'collection': collection,
            'museum_certain': row.museumCertain,
            'location': location,
            'location_certain': row.locationCertain,
            'coord_system': row.origCoordSys,
            'orig_coords': [row.xOrig, row.yOrig] if row.xOrig or row.yOrig else None,
            'main_context': main_context,
            'main_context_certain': row.mainContextCertain,
            'find_context': find_context,
            'find_context_certain': row.findContextCertain,
            'context_detail': context_detail,
            'context_detail_certain': row.detailContextCertain,
            'multiperiod': row.multiperiod,
            'date_string': row.datingString,
            'dating_certain': row.datingCertain,
            'dendro_date': row.dendroDate,
            'radiocarbon_date': row.radioCarbonDate,
            'radiocarbon_years': row.radioCarbonYear,
            'radiocarbon_std': row.stdDeviation,
            'comments': row.comments
        }
    )
    
    keywords = []
    datings = []
    objects_list = []
    cert_context_desc =[]
    poss_context_desc =[]
    
    if row.contextKeywords:
        for desc in literal_eval(row.contextKeywords):
            desc_text = get_or_create_object(ContextKeywords, text=desc)
            keywords.append(desc_text)
    
    if row.dating:
        for dating in literal_eval(row.dating):
            phase_text = get_or_create_object(Phase, text=dating)
            if 'PI' in dating or 'PV' in dating or 'BA' in dating:
                dating_text = get_or_create_object(Period, name='Bronze Age', phase=phase_text)
            elif 'IA' in dating:
                dating_text = get_or_create_object(Period, name='Iron Age', phase=phase_text)
            elif ('Early' in dating or 'Late' in dating or 'Middle' in dating) and 'Neolithic' in dating:
                dating_text = get_or_create_object(Period, name='Neolithic', phase=phase_text)
            else:
                dating_text = get_or_create_object(Period, name=dating)
            datings.append(dating_text)
    
    if row.findsOverview:
        data = pd.json_normalize(literal_eval(row.findsOverview))
        data.rename(columns={'count': 'obj_count'}, inplace=True)
        for finds in data.itertuples():
            category_text = get_or_create_object(ObjectCategories, text=finds.category.capitalize())
            subcategory_text = get_or_create_object(ObjectSubcategories, subcategory=finds.subcategory.capitalize())
            materials = []
            for material in finds.material:
                material = material.capitalize().strip()
                material_mapping = {
                    'Au': 'Gold',
                    'Cu': 'Copper',
                    'Fe': 'Iron',
                    'Sn': 'Tin',
                    'Ag': 'Silver',
                    'Bz': 'Bronze',
                    'Kn': 'Bone'
                }
                material = material_mapping.get(material, material)
                material_text = get_or_create_object(ObjectMaterials, text=material)
                materials.append(material_text)
            object_desc = get_or_create_object(ObjectDescription, subcategory=subcategory_text, category=category_text)
            object_count = get_or_create_object(ObjectCount, metal=metalwork, object=object_desc, count=finds.obj_count, certainty=finds.certain)
            object_count.material.set(materials)
            objects_list.append(object_count)
    
    # Assign categories to the subcategories using keys in the dictionary, append the subcategory objects to a list, add the list to the current db object        
    data = pd.json_normalize(literal_eval(row.certainContextDescriptors))
    for category in data.columns:
            category_obj = ContextFindsCategories.objects.get(text=category.capitalize())
            for subcat in data[category].values[0]:
                    context_subcat=ContextFindsSubcategories.objects.get_or_create(text=subcat.capitalize(), category=category_obj)[0]
                    cert_context_desc.append(context_subcat)
                    
    data = pd.json_normalize(literal_eval(row.uncertainContextDescriptors))
    for category in data.columns:
            category_obj = ContextFindsCategories.objects.get(text=category.capitalize())
            for subcat in data[category].values[0]:
                    context_subcat=ContextFindsSubcategories.objects.get_or_create(text=subcat.capitalize(), category=category_obj)[0]
                    poss_context_desc.append(context_subcat)

print("Data imported successfully")