import os
import sys
import django
import pandas as pd
import numpy as np
import argparse
from django.contrib.gis.geos import Point

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maritime.settings')
django.setup()

from apps.geography.models import ADM0, ADM1, ADM2, ADM3, ADM4, Province, Parish
from apps.resources.models import (
    Site, MetalAnalysis, MetalElement, MetalIsotop,
    Element, LeadIsotope, AccessionNum, Context, ObjectDescription,
    ObjectSubcategories, ObjectCategories, Period, Phase,
)

# Element symbol → full name mapping
ELEMENT_NAMES = {
    'S': 'Sulfur', 'Fe': 'Iron', 'Co': 'Cobalt', 'Ni': 'Nickel',
    'Cu': 'Copper', 'Zn': 'Zinc', 'As': 'Arsenic', 'Ag': 'Silver',
    'Sn': 'Tin', 'Sb': 'Antimony', 'Au': 'Gold', 'Pb': 'Lead',
    'Bi': 'Bismuth', 'Hg': 'Mercury',
}

# Lead isotope ratio column names (as they appear in the xlsx, stripped)
LEAD_ISOTOPE_COLS = ['208Pb/206Pb', '207Pb/206Pb', '206Pb/204Pb', '207Pb/204Pb', '208Pb/204Pb', '1/Pb']

# Geographic region columns to skip (use ADM from coordinates instead)
SKIP_COLS = {'Region/County - REPLACE', 'Province/Parish - REPLACE', 'Region - REPLACE',
             'Country', 'Interpretation MM3/MM4', 'MM5'}


def to_float(val):
    try:
        return float(val) if val is not None and not (isinstance(val, float) and np.isnan(val)) else None
    except (ValueError, TypeError):
        return None


def get_adm_from_point(point):
    """Resolve ADM levels from a point geometry."""
    adm0 = adm1 = adm2 = adm3 = adm4 = province = parish = None
    if point is None:
        return adm0, adm1, adm2, adm3, adm4, province, parish
    try:
        adm4 = ADM4.objects.get(geometry__contains=point)
    except Exception:
        pass
    try:
        adm3 = ADM3.objects.get(geometry__contains=point)
    except Exception:
        pass
    try:
        adm2 = ADM2.objects.get(geometry__contains=point)
    except Exception:
        pass
    try:
        adm1 = ADM1.objects.get(geometry__contains=point)
    except Exception:
        pass
    try:
        adm0 = ADM0.objects.get(geometry__contains=point)
    except Exception:
        pass
    try:
        province = Province.objects.get(geometry__contains=point)
    except Exception:
        pass
    try:
        parish = Parish.objects.get(geometry__contains=point)
    except Exception:
        pass

    # Fallback to parent links when direct containment at higher levels fails.
    if adm2 is not None:
        if adm1 is None:
            adm1 = adm2.ADM1
        if adm0 is None and adm1 is not None:
            adm0 = adm1.ADM0
    if adm3 is not None and adm2 is None:
        adm2 = adm3.ADM2
        if adm1 is None:
            adm1 = adm2.ADM1
        if adm0 is None and adm1 is not None:
            adm0 = adm1.ADM0
    if adm4 is not None and adm3 is None:
        adm3 = adm4.ADM3
        if adm2 is None:
            adm2 = adm3.ADM2
        if adm1 is None and adm2 is not None:
            adm1 = adm2.ADM1
        if adm0 is None and adm1 is not None:
            adm0 = adm1.ADM0

    return adm0, adm1, adm2, adm3, adm4, province, parish


def import_metal_analyses(df):
    # Build a mapping of stripped column name → original column name for element columns
    stripped_cols = {col.strip(): col for col in df.columns}

    for index, row in df.iterrows():
        row = row.where(pd.notna(row), None)  # replace NaN with None

        # --- Coordinates (x = longitude, y = latitude) ---
        x_val = row.get('x')
        y_val = row.get('y')
        point = None
        if x_val is not None and y_val is not None:
            try:
                point = Point(float(x_val), float(y_val), srid=4326)
            except (ValueError, TypeError):
                print(f"Row {index}: invalid coordinates x={x_val} y={y_val}, skipping point")

        # --- ADM from geometry (skip geographic region sheet columns) ---
        adm0, adm1, adm2, adm3, adm4, province, parish = get_adm_from_point(point)

        # --- Site ---
        site_name = row.get('Placename')
        if not site_name and adm2:
            site_name = f"{adm2.name}, {adm2.ADM1.name}"

        site_defaults = {
            'ADM0': adm0,
            'ADM1': adm1,
            'ADM2': adm2,
            'ADM3': adm3,
            'ADM4': adm4,
            'Province': province,
            'Parish': parish,
        }
        try:
            site_obj, _ = Site.objects.update_or_create(
                name=site_name,
                coordinates=point,
                defaults=site_defaults,
            )
        except Site.MultipleObjectsReturned:
            site_qs = Site.objects.filter(name=site_name, coordinates=point)
            site_qs.update(**site_defaults)
            site_obj = site_qs.first()

        # --- Accession / museum number ---
        # Use Sample/Analytical No. as the primary lookup key; museum number as supplementary
        sample_no = row.get('Sample/Analytical No.')
        museum_nr = row.get('Museum Nr.')
        accession_val = str(sample_no).strip() if sample_no else (str(museum_nr).strip() if museum_nr else None)
        accession_obj = None
        if accession_val:
            accession_obj, _ = AccessionNum.objects.get_or_create(accession_number=accession_val)

        # --- Context ---
        context_val = row.get('Context')
        context_obj = None
        if context_val:
            context_obj, _ = Context.objects.get_or_create(text=str(context_val).strip().capitalize())

        # --- Object description ---
        obj_group = row.get('Object group')
        obj_type = row.get('Type')
        object_desc_obj = None
        if obj_type:
            subcategory_obj, _ = ObjectSubcategories.objects.get_or_create(
                subcategory=str(obj_type).strip().capitalize()
            )
            object_desc_obj, _ = ObjectDescription.objects.get_or_create(
                subcategory=subcategory_obj
            )
            if obj_group:
                category_obj, _ = ObjectCategories.objects.get_or_create(
                    text=str(obj_group).strip().capitalize()
                )
                object_desc_obj.category.add(category_obj)

        # --- Period ---
        period_obj = None
        period_val = row.get('Period')
        phase_val = row.get('Phase')
        start_date_val = row.get('Start date')
        end_date_val = row.get('End date')
        if period_val:
            phase_obj = None
            if phase_val:
                phase_obj, _ = Phase.objects.get_or_create(text=str(phase_val).strip())
            start_int = int(start_date_val) if start_date_val is not None else None
            end_int = int(end_date_val) if end_date_val is not None else None
            # Filter on all discriminating fields to avoid MultipleObjectsReturned
            period_qs = Period.objects.filter(
                name=str(period_val).strip(),
                phase=phase_obj,
                start_date=start_int,
                end_date=end_int,
            )
            if period_qs.exists():
                period_obj = period_qs.first()
            else:
                period_obj = Period.objects.create(
                    name=str(period_val).strip(),
                    phase=phase_obj,
                    start_date=start_int,
                    end_date=end_int,
                )

        # --- MetalAnalysis ---
        # Key on accession number (Sample/Analytical No.) for idempotent re-runs
        metal_analysis_obj, created = MetalAnalysis.objects.update_or_create(
            museum_entry=accession_obj,
            defaults={
                'site': site_obj,
                'context': context_obj,
                'object_description': object_desc_obj,
                'general_typology': str(row.get('General typology')).strip() if row.get('General typology') else None,
                'typology': str(row.get('Typology')).strip() if row.get('Typology') else None,
                'period': period_obj,
                # Interpretation columns (MM3/MM4, MM5) are intentionally skipped
            }
        )
        action = 'Created' if created else 'Updated'
        print(f"Row {index}: {action} MetalAnalysis id={metal_analysis_obj.id}  sample={accession_val}  site={site_name}")

        # --- MetalElement records (one per element column) ---
        for symbol, full_name in ELEMENT_NAMES.items():
            orig_col = stripped_cols.get(symbol)
            if orig_col is None:
                continue
            ratio_val = to_float(row.get(orig_col))
            if ratio_val is None:
                continue
            element_obj, _ = Element.objects.get_or_create(
                symbol=symbol,
                defaults={'name': full_name}
            )
            MetalElement.objects.update_or_create(
                metal=metal_analysis_obj,
                elemnt=element_obj,
                defaults={'element_ratio': ratio_val}
            )

        # --- MetalIsotop records (one per lead isotope column) ---
        for isotope_name in LEAD_ISOTOPE_COLS:
            ratio_val = to_float(row.get(isotope_name))
            if ratio_val is None:
                continue
            lead_isotope_obj, _ = LeadIsotope.objects.get_or_create(text=isotope_name)
            MetalIsotop.objects.update_or_create(
                metal=metal_analysis_obj,
                lead_isotope=lead_isotope_obj,
                defaults={'lead_isotope_ratio': ratio_val}
            )


commands = argparse.ArgumentParser(description='Import metal analysis + lead isotope data from xlsx')
commands.add_argument('--files', nargs='*', type=str, help='Path(s) to xlsx file(s)')
commands.add_argument('--sheet', type=str, default=None, help='Sheet name (default: all sheets)')

if __name__ == '__main__':
    args = commands.parse_args()
    if not args.files:
        print("Usage: python import_isotops.py --files path/to/file.xlsx")
        sys.exit(1)

    for file in args.files:
        name = os.path.basename(file)
        xl = pd.ExcelFile(file)
        sheets = [args.sheet] if args.sheet else xl.sheet_names

        for sheet in sheets:
            print(f"\nImporting '{name}' — sheet: '{sheet}'")
            df = pd.read_excel(file, sheet_name=sheet)
            df = df.dropna(how='all').reset_index(drop=True)
            import_metal_analyses(df)

        print(f"\n{name}: import complete.")
