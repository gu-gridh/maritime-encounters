import os
import sys
import django
import pandas as pd
from datetime import datetime
from ast import literal_eval

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
# Replace 'your_project' with your project's name
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maritime.settings')
django.setup()

# Replace 'your_app' with the name of your Django app
from apps.resources.models import *
from apps.geography.models import ADM0, ADM1, ADM2, ADM3, ADM4, ADM5


# Path to your CSV file
csv_file_path = ''

# Load the CSV data
df = pd.read_csv(csv_file_path)

# Import data into ADM levels
site_cache = {}
metal_cache = {}
sampler_cache = {}
new_sample_cache = {}
context_cache = {}
categories_cache = {}
object_subcategories = {}
object_material_cache = {}
object_description_cache = {}
period_cache = {}
phase_cache = {}
assocation_cache = {}

for sampler_name in df[['Sampler']].drop_duplicates().values:
    sampler_name = sampler_name[0].strip()
    sampler, created = Sampler.objects.get_or_create(
        name=sampler_name
    )
    sampler_cache[sampler_name] = sampler

for metal_name in df[['Metal']].drop_duplicates().values:
    metal_name = metal_name[0].strip()
    metal, created = Element.objects.get_or_create(
        name=metal_name,
    )
    metal_cache[metal_name] = metal

# you can upload sites using imort-sites.py
for site_name, adm0, adm1, adm2 in df[['site_name', 'COUNTRY', 'NAME_1', 'NAME_2']].drop_duplicates().values:
    site = Site.objects.get(
        name=site_name.strip(),
        ADM0__name=adm0,
        ADM1__name=adm1,
        ADM2__name=adm2,
    )
    site_cache[site_name] = site

for site_name, metal_name, drilled_location, weight, pictures, sampler_names, date, note in df[['site_name', 'Metal', 'Drilled_location', 'Weight', 'Pictures', 'Sampler', 'Date', 'Note']].values:

    date_format = "%d/%m/%Y %H:%M"
    if pd.notna(date):
        parsed_date = datetime.strptime(date, date_format)
    else:
        parsed_date = None

    new_sample, created = NewSamples.objects.get_or_create(
        site=site_cache.get(site_name),
        metal=metal_cache.get(metal_name),
        drilled_location=drilled_location,
        weight=weight,
        pictures=pictures,
        sampler=sampler_cache.get(sampler_names[0]),
        date=parsed_date,
        note=note
    )
    new_sample_cache[(site_name, metal_name, drilled_location)] = new_sample

for context_name in df[['context']].drop_duplicates().values:
    context_name = context_name[0].strip()
    context, created = Context.objects.get_or_create(
        text=context_name
    )
    context_cache[context_name] = context

# for category in df[['object_category']].drop_duplicates().values:
#     category = category[0].strip()
#     object_type, created = ObjectCategories.objects.get_or_create(
#         text=category.capitalize()
#     )
#     categories_cache[category] = object_type

# for sub_category, category in df[['object_description', 'object_category']].drop_duplicates().values:
#     sub_category = sub_category.strip()
#     object_type, created = ObjectSubcategories.objects.get_or_create(
#         category=categories_cache.get(category.capitalize()),
#         subcategory=sub_category.capitalize()
#     )
#     object_subcategories[sub_category] = object_type

# for object_material in df[['Metal']].drop_duplicates().values:
#     obj_material = object_material[0].strip()
#     object, created = ObjectMaterials.objects.get_or_create(
#         text=obj_material,
#     )
#     object_material_cache[obj_material] = object

# for object_description, mat in df[['object_description', 'Metal']].drop_duplicates().values:
#     object = object_subcategories.get(object_description)
#     material = object_material_cache.get(mat)
#     object_desc, created = ObjectDescription.objects.get_or_create(
#         type=object
#     )
#     object_desc.material.add(material)
#     object_description_cache[object_description] = object_desc

for phase_n in df[['phase']].drop_duplicates().values:
    phase_n = phase_n[0]
    phase, created = Phase.objects.get_or_create(
        text=phase_n
    )
    phase_cache[phase_n] = phase

for start_date, end_date, period_name, period_phase in df[['start_date', 'end_date', 'period', 'phase']].values:

    if pd.isna(period_phase):
        period_phase = None
    else:
        period_phase = phase_cache.get(period_phase)

    period, created = Period.objects.get_or_create(
        start_date=start_date,
        end_date=end_date,
        name=period_name,
        phase=period_phase
    )
    period_cache[(period_name, period_phase, start_date, end_date)] = period

for ass_num in df[['Catalogue_no_']].values:
    assoc_number= ass_num[0]
    ass_number, created = AccessionNum.objects.get_or_create(
        accession_number=assoc_number
    )
    assocation_cache[assoc_number] = ass_number

for row in df.itertuples(index=False):
    site_sample = site_cache.get(row.site_name)
    if not pd.isna(row.typology):
        typology_row = row.typology.strip()
    else:
        typology_row = None

    phase = phase_cache.get(row.phase)
    
    category_text = ObjectCategories.objects.get_or_create(text=row.object_category.capitalize().strip())[0]
    subcategory_text = ObjectSubcategories.objects.get_or_create(subcategory=row.object_description.capitalize().strip())[0]

    obj=MetalAnalysis.objects.update_or_create(
        site=site_sample,
        sample=new_sample_cache.get((row.site_name, row.Metal, row.Drilled_location)),
        museum_entry=assocation_cache.get(row.Catalogue_no_),
        context=context_cache.get(row.context),
        object_description=ObjectDescription.objects.get_or_create(subcategory=subcategory_text, category=category_text)[0],
        general_typology=row.general_typology,
        typology=typology_row,
        period=period_cache.get((row.period, phase, row.start_date, row.end_date)),
    )[0]




print("Data imported successfully")