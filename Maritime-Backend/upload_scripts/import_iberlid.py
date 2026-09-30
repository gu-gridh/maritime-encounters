'''
Import the Iberlid lead isotope dataset (Spain ore iberlid_WIP_AG_180926.xlsx).

For every row:
  1. Look for the site in the database by SiteName (and by proximity when coordinates are valid).
     If it is not found the row is skipped: this script never creates sites.
  2. A MetalAnalysis is created/updated for the sample (keyed on sample number + site).
  3. The five lead isotope ratios are stored as MetalIsotop records.

Usage:
    python import_iberlid.py --files "../../resources/Spain ore iberlid_WIP_AG_180926.xlsx" [--dry-run]
'''

import os
import re
import sys
import argparse
import django
import pandas as pd
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import Q

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maritime.settings')
django.setup()

from apps.resources.models import Site, MetalAnalysis, MetalIsotop, LeadIsotope, NewSamples, Element
from import_metal_isotops import to_float

LEAD_ISOTOPE_COLS = ['208Pb/206Pb', '207Pb/206Pb', '206Pb/204Pb', '207Pb/204Pb', '208Pb/204Pb']

# 'Analysed material' sometimes holds object codes (e.g. PA29130) instead of a material: not a metal
CODE_RE = re.compile(r'[A-Za-z]{1,3}\d+')

# A site with the same name closer than this is considered the same site
MATCH_RADIUS_KM = 5


def clean(val):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    val = str(val).strip()
    return val or None


def make_point(lat, lon):
    """Some rows are shifted in the sheet (text in the coordinate columns), so be tolerant."""
    lat, lon = to_float(lat), to_float(lon)
    if lat is None or lon is None or not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return None
    return Point(lon, lat, srid=4326)


def find_site(name, point):
    """Return an existing Site matching the name (and location when available), or None."""
    candidates = Site.objects.filter(name__iexact=name)
    if not candidates.exists():
        return None
    if point is None:
        return candidates.first()
    near = candidates.filter(coordinates__distance_lte=(point, D(km=MATCH_RADIUS_KM))).first()
    if near:
        return near
    # Same name but no coordinates stored: assume the same site
    return candidates.filter(Q(coordinates__isnull=True)).first()


def import_iberlid(df, dry_run=False):
    stats = {'matched': 0, 'created': 0, 'updated': 0, 'skipped_no_name': 0, 'skipped_site_not_in_db': 0}
    site_cache = {}
    skipped_sites = set()

    for index, row in df.iterrows():
        sample = clean(row.get('Sample'))
        site_name = clean(row.get('SiteName'))
        if not site_name:
            print(f"Row {index}: no SiteName, skipping")
            stats['skipped_no_name'] += 1
            continue

        point = make_point(row.get('latitude'), row.get('longitude'))

        cache_key = (site_name.lower(), (round(point.x, 4), round(point.y, 4)) if point else None)
        if cache_key not in site_cache:
            site_cache[cache_key] = find_site(site_name, point)
        site = site_cache[cache_key]
        if site is None:
            stats['skipped_site_not_in_db'] += 1
            skipped_sites.add(site_name)
            continue
        stats['matched'] += 1

        ratios = {col: to_float(row.get(col)) for col in LEAD_ISOTOPE_COLS}
        ratios = {k: v for k, v in ratios.items() if v is not None}

        if dry_run:
            continue

        # Analysed material -> Sample > Metal (Element), first letter capitalised
        material = clean(row.get('Analysed material'))
        metal = None
        if material and not CODE_RE.fullmatch(material):
            material = material[0].upper() + material[1:]
            metal = Element.objects.filter(name__iexact=material).first() \
                or Element.objects.create(name=material)

        # The sample number goes on the Sample record (NewSamples has no id field, so it is kept in note)
        sample_obj = None
        if sample or metal:
            note = f"Sample: {sample}" if sample else None
            sample_obj = NewSamples.objects.filter(site=site, note=note).first() \
                or NewSamples.objects.create(site=site, note=note)
            if sample_obj.metal_id != (metal.pk if metal else None):
                sample_obj.metal = metal
                sample_obj.save()

        extra = {'geology': clean(row.get('geol.zone')), 'reference': clean(row.get('Reference'))}
        analysis, was_created = MetalAnalysis.objects.update_or_create(
            sample=sample_obj, site=site,
            defaults=extra,
        ) if sample_obj else (MetalAnalysis.objects.create(site=site, **extra), True)
        stats['created' if was_created else 'updated'] += 1

        for name, value in ratios.items():
            lead_isotope, _ = LeadIsotope.objects.get_or_create(text=name)
            MetalIsotop.objects.update_or_create(
                metal=analysis, lead_isotope=lead_isotope,
                defaults={'lead_isotope_ratio': value},
            )

    print(f"\nSites not found in the database ({len(skipped_sites)}): {sorted(skipped_sites)}")
    print(f"\nDone{' (dry run, nothing written)' if dry_run else ''}: {stats}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import Iberlid lead isotope data from xlsx')
    parser.add_argument('--files', nargs='+', required=True, help='Path(s) to xlsx file(s)')
    parser.add_argument('--sheet', default=0, help='Sheet name or index (default: first sheet)')
    parser.add_argument('--dry-run', action='store_true', help='Only report which rows match an existing site, write nothing')
    args = parser.parse_args()

    for file in args.files:
        print(f"Importing {os.path.basename(file)}")
        df = pd.read_excel(file, sheet_name=args.sheet).dropna(how='all').reset_index(drop=True)
        import_iberlid(df, dry_run=args.dry_run)
