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

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maritime.settings')  # Replace 'your_project' with your project's name
django.setup()

from apps.geography.models import ADM0, ADM1, ADM2, ADM3, ADM4, Province, Parish
from apps.resources.models import *


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


# Load the CSV data

def import_metalwork(csv_file_path):
    df = pd.read_csv(csv_file_path).replace(np.nan, None).replace('[]', None)
        # Add finds categories to database
    desc_df = pd.json_normalize(literal_eval(df['certainContextDescriptors'][0]))
    for category in desc_df.columns:
        ContextFindsCategories.objects.get_or_create(text=category.capitalize())
    for row in df.itertuples(index=False):
        if not pd.isnull(row.y) or pd.isnull(row.x):
            point = Point(row.x,row.y) # Note that Point takes (longitude, latitude) order
        else:
            point=None
            
        # Add administrative data to sites and create site objects
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
                
            adm0 = ADM0.objects.get(name=row.ADM_0) if row.ADM_0 != None else None
            adm1 = ADM1.objects.get(name=row.ADM_1) if row.ADM_1 != None else None
                
            site_name = row.place or f"{parish}, {province}: {row.y}, {row.x}" or f"{province}: {row.y}, {row.x}" or f"{adm4}: {row.y}, {row.x}" or f"{adm3}: {row.y}, {row.x}" or f"{adm2}: {row.y}, {row.x}"
            
            try:
                site_obj = Site.objects.get_or_create(
                    name=site_name,
                    ADM0=adm0,
                    ADM1=adm1,
                    ADM2=adm2,
                    ADM3=adm3,
                    ADM4=adm4,
                    Province=province,
                    Parish=parish,
                    coordinates=point
                )[0]
            
            except:
                site_obj = Site.objects.get_or_create(
                    name=row.place if row.place != None else None,
                    ADM0=row.ADM_0 if row.ADM_0 != None else None,
                    ADM1=row.ADM_1 if row.ADM_1 != None else None,
                )[0]

            if row.dating != None:
                multiperiod_bool = False if len(literal_eval(row.dating)) <1 else True
            else:
                multiperiod_bool = False

            # Add data to boolean, character/text, and some foreignkey fields
            db_object = Metalwork.objects.update_or_create(
                entry_num=EntryNum.objects.get_or_create(entry_number=row.entryNo)[0],
                literature_num=LiteratureNum.objects.get_or_create(
                    literature_number=row.literatureNo)[0],
                accession_num=AccessionNum.objects.get_or_create(
                    accession_number=row.accessionNo)[0],
                accession_certain=row.accessionCertain,
                museum_certain=row.museumCertain,
                location=Location.objects.get_or_create(
                    site=site_obj, location_detail=row.placeDetail)[0],
                location_certain=row.locationCertain,
                coord_system=row.origCoordSys,
                orig_coords=[row.xOrig, row.yOrig] if row.xOrig or row.yOrig else None,
                main_context=Context.objects.get_or_create(
                    text=row.mainContext if row.mainContext != None else 'Uncertain')[0],
                main_context_certain=row.mainContextCertain,
                find_context=FindContext.objects.get_or_create(
                    text=row.findContext)[0],
                find_context_certain=row.findContextCertain,
                context_detail=ContextDetail.objects.get_or_create(
                    text=row.detailContext if row.detailContext != None else 'Unknown')[0],
                context_detail_certain=row.detailContextCertain,
                # Inverted boolean value to handle mixup during data export
                multiperiod=multiperiod_bool,
                date_string=row.datingString,
                dating_certain=row.datingCertain,
                dendro_date=row.dendroDate,
                radiocarbon_date=row.radioCarbonDate,
                radiocarbon_years=row.radioCarbonYear,
                radiocarbon_std=row.stdDeviation,
                comments=row.comments
            )[0]

            # Add data to remaining fields with more complex data structure
            keywords = []
            datings = []
            objects_list = []
            cert_context_desc = []
            poss_context_desc = []

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
                        dating_text = Period.objects.get_or_create(
                            name='Bronze Age', phase=phase_text)[0]
                        datings.append(dating_text)
                    elif 'IA' in dating:
                        phase_text = Phase.objects.get_or_create(text=dating)[0]
                        dating_text = Period.objects.get_or_create(
                            name='Iron Age', phase=phase_text)[0]
                        datings.append(dating_text)
                    elif ('Early' or 'Late' or 'Middle' in dating) and 'Neolithic' in dating:
                        phase_text = Phase.objects.get_or_create(text=dating)[0]
                        dating_text = Period.objects.get_or_create(
                            name='Neolithic', phase=phase_text)[0]
                        datings.append(dating_text)
                    elif ('ERT' or 'RT' in dating):
                        phase_text = Phase.objects.get_or_create(text=dating)[0]
                        dating_text = Period.objects.get_or_create(name='Iron Age', phase = phase_text)
                        datings.append(dating_text)
                    elif 'EGK' in dating:
                        phase_text = Phase.objects.get_or_create(text=dating)[0]
                        dating_text = Period.objects.get_or_create(name='Neolithic', phase = phase_text)
                        datings.append(dating_text)
                    else:
                        dating_text = Period.objects.get_or_create(name=dating)[0]
                        datings.append(dating_text)

            # Create finds categories and subcategories, edit material values for normalisation, generate a list of material objects, add the object and count data to the current metalwork object
            if row.findsOverview != None:
                data = pd.json_normalize(literal_eval(row.findsOverview))
                data.rename(columns={'count': 'obj_count'}, inplace=True)
                for finds in data.itertuples():
                    category_text = ObjectCategories.objects.get_or_create(
                        text=finds.category.capitalize())[0]
                    subcategory_text = ObjectSubcategories.objects.get_or_create(
                        subcategory=finds.subcategory.capitalize())[0]
                    materials = []
                    category_list = []
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
                        material_text = ObjectMaterials.objects.get_or_create(
                            text=material.capitalize())[0]
                        materials.append(material_text)

                    category_text = ObjectCategories.objects.get_or_create(text='Weapons')[0]
                    category_list.append(category_text)
        
                    object_desc = ObjectDescription.objects.get_or_create(
                        subcategory=subcategory_text)[0]
                    object_desc.category.set(category_list) 
                    

                    # db_object = Metalwork.objects.get(entry_num__entry_number=row.entryNo, literature_num__literature_number=row.literatureNo)
                    object_counts = ObjectCount.objects.create(
                        metal=db_object, object=object_desc, count=finds.obj_count, certainty=finds.certain)
                    object_counts.material.set(materials)
                    objects_list.append(object_counts)

            # Assign categories to the subcategories using keys in the dictionary, append the subcategory objects to a list, add the list to the current db object
            data = pd.json_normalize(literal_eval(row.certainContextDescriptors))
            for category in data.columns:
                category_obj = ContextFindsCategories.objects.get(
                    text=category.capitalize())
                for subcat in data[category].values[0]:
                    context_subcat = ContextFindsSubcategories.objects.get_or_create(
                        text=subcat.capitalize(), category=category_obj)[0]
                    cert_context_desc.append(context_subcat)

            data = pd.json_normalize(literal_eval(row.uncertainContextDescriptors))
            for category in data.columns:
                category_obj = ContextFindsCategories.objects.get(
                    text=category.capitalize())
                for subcat in data[category].values[0]:
                    context_subcat = ContextFindsSubcategories.objects.get_or_create(
                        text=subcat.capitalize(), category=category_obj)[0]
                    poss_context_desc.append(context_subcat)
                    
            if row.museumCollection != None:
                collections_list=[]
                for collection in row.museumCollection.title().split(';'):        
                    mus_collect=MuseumCollection.objects.get_or_create(collection=collection.strip())[
                            0]
                    collections_list.append(mus_collect)

            # Set ManyToMany fields using the lists
            # db_object = Metalwork.objects.get(entry_num__entry_number=row.entryNo, literature_num__literature_number=row.literatureNo)
            db_object.context_keywords.set(keywords)
            db_object.dating.set(datings)
            db_object.certain_context_descriptors.set(cert_context_desc)
            db_object.uncertain_context_descriptors.set(poss_context_desc)
            db_object.collection.set(collections_list)


    print("Data imported successfully")
    
if __name__ == '__main__':
    file = sys.argv[1]
    import_metalwork(file)