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

# Load the CSV data
def import_metalwork(csv_file_path):
    df = pd.read_csv(csv_file_path).replace(np.nan, None).replace('[]', None)

    # Normalize descriptors to avoid multiple evaluations in the loop
    desc_df = pd.json_normalize(literal_eval(df['certainContextDescriptors'][0]))
    for category in desc_df.columns:
        ContextFindsCategories.objects.get_or_create(text=category.capitalize())

    for row in df.itertuples(index=False):
        # Handle site creation
        x, y = row.x, row.y
        point = Point(x, y) if not pd.isnull(y) or pd.isnull(x) else None
        site_name = row.place or f"{row.parish}: {y}, {x}" or f"{row.province}: {y}, {x}" or f"{row.ADM_4}: {y}, {x}" or f"{row.ADM_3}: {y}, {x}" or f"{row.ADM_2}: {y}, {x}"
        print(site_name)
        # adm0 = ADM0.objects.get(name=row.ADM_0) if row.ADM_0 else None
        # adm1 = ADM1.objects.get(name=row.ADM_1) if row.ADM_1 else None
        # adm2 = ADM2.objects.get(name=row.ADM_2, ADM1__name=row.ADM_1) if row.ADM_2 else None
        # adm3 = ADM3.objects.get(name=row.ADM_3, ADM2__name=row.ADM_2) if row.ADM_3 else None
        # adm4 = ADM4.objects.get(name=row.ADM_4, ADM3__name=row.ADM_3, ADM3__ADM2__name=row.ADM_2) if row.ADM_4 else None
        # province, parish = None, None

        # try:
        #     province = Province.objects.get(geometry__contains=point)
        # except:
        #     pass
        # try:
        #     parish = Parish.objects.get(geometry__contains=point)
        # except:
        #     pass

        # site_obj, _ = Site.objects.get_or_create(
        #     name=site_name,
        #     ADM0=adm0,
        #     ADM1=adm1,
        #     ADM2=adm2,
        #     ADM3=adm3,
        #     ADM4=adm4,
        #     Province=province,
        #     Parish=parish,
        #     coordinates=point
        # )

        # # Process Metalwork data for each row
        # multiperiod_bool = bool(row.dating) and len(literal_eval(row.dating)) > 1

        # db_object, _ = Metalwork.objects.update_or_create(
        #     entry_num=EntryNum.objects.get_or_create(entry_number=row.entryNo)[0],
        #     literature_num=LiteratureNum.objects.get_or_create(
        #         literature_number=row.literatureNo)[0],
        #     accession_num=AccessionNum.objects.get_or_create(
        #         accession_number=row.accessionNo)[0],
        #     accession_certain=row.accessionCertain,
        #     museum_certain=row.museumCertain,
        #     location=Location.objects.get_or_create(
        #         site=site_name, location_detail=row.placeDetail)[0],
        #     location_certain=row.locationCertain,
        #     coord_system=row.origCoordSys,
        #     orig_coords=[row.xOrig, row.yOrig] if row.xOrig or row.yOrig else None,
        #     main_context=Context.objects.get_or_create(
        #         text=row.mainContext if row.mainContext != None else 'Uncertain')[0],
        #     main_context_certain=row.mainContextCertain,
        #     find_context=FindContext.objects.get_or_create(
        #         text=row.findContext)[0],
        #     find_context_certain=row.findContextCertain,
        #     context_detail=ContextDetail.objects.get_or_create(
        #         text=row.detailContext if row.detailContext != None else 'Unknown')[0],
        #     context_detail_certain=row.detailContextCertain,
        #     # Inverted boolean value to handle mixup during data export
        #     multiperiod=multiperiod_bool,
        #     date_string=row.datingString,
        #     dating_certain=row.datingCertain,
        #     dendro_date=row.dendroDate,
        #     radiocarbon_date=row.radioCarbonDate,
        #     radiocarbon_years=row.radioCarbonYear,
        #     radiocarbon_std=row.stdDeviation,
        #     comments=row.comments
        # )[0]    

        # # Process complex fields
        # keywords, datings, objects_list = [], [], []
        # cert_context_desc, poss_context_desc = [], []

        # if row.contextKeywords:
        #     for desc in literal_eval(row.contextKeywords):
        #         keywords.append(ContextKeywords.objects.get_or_create(text=desc)[0])

        # if row.dating:
        #     for dating in literal_eval(row.dating):
        #         if 'PI' or 'PV' or 'BA' in dating:
        #             phase = Phase.objects.get_or_create(text=dating)[0]
        #             datings.append(Period.objects.get_or_create(name='Bronze Age', phase=phase)[0])
        #         elif 'IA' in dating:
        #             phase = Phase.objects.get_or_create(text=dating)[0]
        #             datings.append(Period.objects.get_or_create(name='Iron Age', phase=phase)[0])
        #         elif 'Neolithic' in dating:
        #             phase = Phase.objects.get_or_create(text=dating)[0]
        #             datings.append(Period.objects.get_or_create(name='Neolithic', phase=phase)[0])
        #         elif 'ERT' or 'RT' in dating:
        #             phase = Phase.objects.get_or_create(text=dating)[0]
        #             datings.append(Period.objects.get_or_create(name='Iron Age', phase=phase)[0])
        #         elif 'EGK' in dating:
        #             phase = Phase.objects.get_or_create(text=dating)[0]
        #             datings.append(Period.objects.get_or_create(name='Neolithic', phase=phase)[0])
        #         else:
        #             datings.append(Period.objects.get_or_create(name=dating)[0])

        # if row.findsOverview:
        #     data = pd.json_normalize(literal_eval(row.findsOverview))
        #     data.rename(columns={'count': 'obj_count'}, inplace=True)
        #     for finds in data.itertuples():
        #         category = ObjectCategories.objects.get_or_create(text=finds.category.capitalize())[0]
        #         subcategory = ObjectSubcategories.objects.get_or_create(subcategory=finds.subcategory.capitalize())[0]
        #         materials = [
        #             ObjectMaterials.objects.get_or_create(
        #                 text=material.capitalize().strip()
        #                 .replace('Au', 'Gold')
        #                 .replace('Cu', 'Copper')
        #                 .replace('Fe', 'Iron')
        #                 .replace('Sn', 'Tin')
        #                 .replace('Ag', 'Silver')
        #                 .replace('Bz', 'Bronze')
        #                 .replace('Kn', 'Bone')
        #             )[0]
        #             for material in finds.material
        #         ]

        #         object_desc = ObjectDescription.objects.get_or_create(subcategory=subcategory)[0]
        #         object_desc.category.set([category])
        #         object_counts = ObjectCount.objects.create(
        #             metal=db_object, object=object_desc, count=finds.obj_count, certainty=finds.certain)
        #         object_counts.material.set(materials)
        #         objects_list.append(object_counts)

        # if row.certainContextDescriptors:
        #     data = pd.json_normalize(literal_eval(row.certainContextDescriptors))
        #     for category in data.columns:
        #         category_obj = ContextFindsCategories.objects.get(text=category.capitalize())
        #         for subcat in data[category].values[0]:
        #             cert_context_desc.append(ContextFindsSubcategories.objects.get_or_create(
        #                 text=subcat.capitalize(), category=category_obj)[0])

        # if row.uncertainContextDescriptors:
        #     data = pd.json_normalize(literal_eval(row.uncertainContextDescriptors))
        #     for category in data.columns:
        #         category_obj = ContextFindsCategories.objects.get(text=category.capitalize())
        #         for subcat in data[category].values[0]:
        #             poss_context_desc.append(ContextFindsSubcategories.objects.get_or_create(
        #                 text=subcat.capitalize(), category=category_obj)[0])

        # if row.museumCollection:
        #     collections_list = [MuseumCollection.objects.get_or_create(collection=collection.strip())[0]
        #                         for collection in row.museumCollection.title().split(';')]

        # # Set ManyToMany fields
        # db_object.context_keywords.set(keywords)
        # db_object.dating.set(datings)
        # db_object.certain_context_descriptors.set(cert_context_desc)
        # db_object.uncertain_context_descriptors.set(poss_context_desc)
        # db_object.collection.set(collections_list)

    print("Data imported successfully")
    
if __name__ == '__main__':
    file = sys.argv[1]
    import_metalwork(file)
