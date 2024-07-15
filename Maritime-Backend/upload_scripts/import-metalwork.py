import os
import sys
import django
import json
import pandas as pd
from datetime import datetime
from django.contrib.gis.geos import Point
import numpy as np
from ast import literal_eval

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maritime.settings')

# Set up Django
django.setup()

# Replace 'your_app' with the name of your Django app
from apps.resources.models import *
from apps.geography.models import ADM0, ADM1, ADM2, ADM3, ADM4, ADM5, Province, Parish


# Clear current data in database
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


csv_file_path = '../../resources/c_horn_metalwork_v2.csv'

# Load the CSV data
df = pd.read_csv(csv_file_path).replace(np.nan, None).replace('[]',None)

# Import data into caches
site_cache = {}


#Add administrative data to sites and create site objects
for place, adm0n, adm1n, adm2n, adm3n, adm4n, provincen, parishn, x, y in df[['place', 'ADM_0', 'ADM_1', 'ADM_2', 'ADM_3', 'ADM_4', 'province', 'parish', 'x', 'y']].drop_duplicates(['x','y','place']).values:
    site_name = place or f"{parish}: {y}, {x}" or f"{province}: {y}, {x}" or f"{adm4n}: {y}, {x}" or f"{adm3n}: {y}, {x}" or f"{adm2n}: {y}, {x}"
    adm0 = ADM0.objects.get(name=adm0n) if adm0n != None else None
    adm1 = ADM1.objects.get(name=adm1n) if adm1n != None else None
    adm2 = ADM2.objects.get(name=adm2n, ADM1__name=adm1n) if adm2n != None else None
    adm3 = ADM3.objects.get(name=adm3n, ADM2__name=adm2n) if adm3n != None else None
    adm4 = ADM4.objects.get(name=adm4n, ADM3__name=adm3n, ADM3__ADM2__name=adm2n) if adm4n != None else None
    province = Province.objects.get(name=provincen) if provincen != None else None
    parish= Parish.objects.get(name=parishn) if parishn != None else None
    point = Point(x, y) if not pd.isnull(y) or pd.isnull(x) else None # Note that Point takes (longitude, latitude) order

    site = Site.objects.get_or_create(
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
    site_cache[x] = site
    
#Add finds categories to database
desc_df = pd.json_normalize(literal_eval(df['certainContextDescriptors'][0]))
for category in desc_df.columns:
    ContextFindsCategories.objects.get_or_create(text=category.capitalize())

# Import data by row
for row in df.itertuples(index=False):
    site_name = row.place or f"{row.parish}: {row.y}, {row.x}" or f"{row.province}: {row.y}, {row.x}" or f"{row.ADM_4}: {row.y}, {row.x}" or f"{row.ADM_3}: {row.y}, {row.x}" or f"{row.ADM_2}: {row.y}, {row.x}" or "NAME IS MISSING"
    
    # Add data to boolean, character/text, and some foreignkey fields
    db_object=Metalwork.objects.update_or_create(
        entry_num=EntryNum.objects.get_or_create(entry_number=row.entryNo)[0], 
        literature_num=LiteratureNum.objects.get_or_create(literature_number = row.literatureNo)[0],
        accession_num=AccessionNum.objects.get_or_create(accession_number = row.accessionNo)[0],
        accession_certain=row.accessionCertain,
        collection=MuseumCollection.objects.get_or_create(collection=row.museumCollection.strip().title())[0] if not pd.isnull(row.museumCollection) else None,
        museum_certain=row.museumCertain,
        location=Location.objects.get_or_create(
        site=Site.objects.get_or_create(coordinates=Point(row.x,row.y), name=site_name)[0], location_detail=row.placeDetail)[0],
        location_certain=row.locationCertain,
        coord_system=row.origCoordSys,
        orig_coords=[row.xOrig, row.yOrig] if row.xOrig or row.yOrig else None,
        main_context=Context.objects.get_or_create(text=row.mainContext)[0],
        main_context_certain=row.mainContextCertain,
        find_context=FindContext.objects.get_or_create(text=row.findContext)[0],
        find_context_certain=row.findContextCertain,
        context_detail=ContextDetail.objects.get_or_create(text=row.detailContext if row.detailContext != None else 'Unknown')[0]  ,
        context_detail_certain=row.detailContextCertain,
        multiperiod=row.multiperiod,
        date_string=row.datingString, 
        dating_certain=row.datingCertain,
        dendro_date=row.dendroDate, 
        radiocarbon_date=row.radioCarbonDate,
        radiocarbon_years=row.radioCarbonYear, 
        radiocarbon_std=row.stdDeviation, 
        comments=row.comments
    )[0]
    
    # Add data to remaining fields with more complex data structure
    keywords=[]
    datings = []
    objects_list = []
    cert_context_desc =[]
    poss_context_desc =[]
    
    # Add objects for all keywords to list
    if row.contextKeywords != None:
        for desc in literal_eval(row.contextKeywords):
            desc_text = ContextKeywords.objects.get_or_create(text=desc)[0]
            keywords.append(desc_text)
    
    # Separate phase values from periods and add objects to list    
    if row.dating != None:
        for dating in literal_eval(row.dating):
            if 'PI' or 'PV' or 'BA' in dating:
                phase_text = Phase.objects.get_or_create(text=dating)[0]
                dating_text=Period.objects.get_or_create(name='Bronze Age', phase=phase_text)[0]
                datings.append(dating_text)
            elif 'IA' in dating:
                phase_text = Phase.objects.get_or_create(text=dating)[0]
                dating_text=Period.objects.get_or_create(name = 'Iron Age', phase=phase_text)[0]
                datings.append(dating_text)
            elif ('Early' or 'Late' or 'Middle' in dating) and 'Neolithic' in dating:
                phase_text = Phase.objects.get_or_create(text=dating)[0]
                dating_text=Period.objects.get_or_create(name = 'Neolithic', phase=phase_text)[0]
                datings.append(dating_text)
            else:
                dating_text=Period.objects.get_or_create(name = dating)[0]
                datings.append(dating_text)
                
    # Create finds categories and subcategories, edit material values for normalisation, generate a list of material objects, add the object and count data to the current metalwork object
    if row.findsOverview !=None:
        data = pd.json_normalize(literal_eval(row.findsOverview))
        data.rename(columns={'count':'obj_count'}, inplace=True)
        for finds in data.itertuples():
            category_text = ObjectCategories.objects.get_or_create(text=finds.category.capitalize())[0]
            subcategory_text = ObjectSubcategories.objects.get_or_create(subcategory=finds.subcategory.capitalize())[0]
            materials = []
            for material in finds.material:
                if material.capitalize().strip() == 'Au':
                    material = 'Gold'
                if material.capitalize().strip() == 'Cu':
                    material = 'Copper'
                if material.capitalize().strip() == 'Fe':
                    material = 'Iron'
                if material.capitalize().strip() == 'Sn':
                    material = 'Tin'
                if material.capitalize().strip() == 'Ag':
                    material = 'Silver'
                if material.capitalize().strip() == 'Bz':
                    material = 'Bronze'
                if material.capitalize().strip() == 'Kn':
                    material = 'Bone'
                material_text = ObjectMaterials.objects.get_or_create(text=material.capitalize())[0]
                materials.append(material_text)
            object_desc=ObjectDescription.objects.get_or_create(subcategory=subcategory_text,category=category_text)[0]
            
            # db_object = Metalwork.objects.get(entry_num__entry_number=row.entryNo, literature_num__literature_number=row.literatureNo)
            object_counts = ObjectCount.objects.get_or_create(metal=db_object, object = object_desc, count = finds.obj_count, certainty = finds.certain)[0]
            object_counts.material.set(materials)
            objects_list.append(object_counts)
    
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

    # Set ManyToMany fields using the lists
    # db_object = Metalwork.objects.get(entry_num__entry_number=row.entryNo, literature_num__literature_number=row.literatureNo)
    db_object.context_keywords.set(keywords)
    db_object.dating.set(datings)
    db_object.certain_context_descriptors.set(cert_context_desc)
    db_object.uncertain_context_descriptors.set(poss_context_desc)
        
    
print("Data imported successfully")
