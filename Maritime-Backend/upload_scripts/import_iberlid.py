'''
Import the Iberlid lead isotope dataset (Spain ore iberlid_WIP_AG_180926.xlsx).

For every row:
  1. Look for the site in the database (by name, and by proximity when coordinates are valid).
     If it is not found a new Site is created (ADM levels resolved from the coordinates).
  2. A MetalAnalysis is created/updated for the sample (keyed on sample number + site).
  3. The five lead isotope ratios are stored as MetalIsotop records.

Usage:
    python import_iberlid.py --files "../../resources/Spain ore iberlid_WIP_AG_180926.xlsx" [--dry-run]
'''

import os
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

from apps.resources.models import Site, MetalAnalysis, MetalIsotop, LeadIsotope, AccessionNum
from import_metal_isotops import get_adm_from_point, to_float

LEAD_ISOTOPE_COLS = ['208Pb/206Pb', '207Pb/206Pb', '206Pb/204Pb', '207Pb/204Pb', '208Pb/204Pb']

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


def get_or_create_site(name, point, dry_run):
    site = find_site(name, point)
    if site:
        return site, False
    if dry_run:
        return None, True
    adm0, adm1, adm2, adm3, adm4, province, parish = get_adm_from_point(point)
    site = Site.objects.create(
        name=name, coordinates=point,
        ADM0=adm0, ADM1=adm1, ADM2=adm2, ADM3=adm3, ADM4=adm4,
        Province=province, Parish=parish,
    )
    return site, True


def import_iberlid(df, dry_run=False):
    stats = {'sites_created': 0, 'sites_existing': 0, 'created': 0, 'updated': 0, 'skipped': 0}
    site_cache = {}

    for index, row in df.iterrows():
        sample = clean(row.get('Sample'))
        site_name = clean(row.get('SiteName')) or clean(row.get('Outcrop'))
        if not site_name:
            print(f"Row {index}: no site name, skipping")
            stats['skipped'] += 1
            continue

        point = make_point(row.get('latitude'), row.get('longitude'))
        if point is None:
            print(f"Row {index}: no valid coordinates for '{site_name}'")

        cache_key = (site_name.lower(), (round(point.x, 4), round(point.y, 4)) if point else None)
        if cache_key in site_cache:
            site, created = site_cache[cache_key], False
        else:
            site, created = get_or_create_site(site_name, point, dry_run)
            site_cache[cache_key] = site
            stats['sites_created' if created else 'sites_existing'] += 1
            print(f"Row {index}: site '{site_name}' {'CREATED' if created else 'already in db'}")

        ratios = {col: to_float(row.get(col)) for col in LEAD_ISOTOPE_COLS}
        ratios = {k: v for k, v in ratios.items() if v is not None}

        if dry_run:
            continue

        accession = None
        if sample:
            accession = AccessionNum.objects.filter(accession_number=sample).first() \
                or AccessionNum.objects.create(accession_number=sample)

        analysis, was_created = MetalAnalysis.objects.update_or_create(
            museum_entry=accession, site=site,
            defaults={},
        ) if accession else (MetalAnalysis.objects.create(site=site), True)
        stats['created' if was_created else 'updated'] += 1

        for name, value in ratios.items():
            lead_isotope, _ = LeadIsotope.objects.get_or_create(text=name)
            MetalIsotop.objects.update_or_create(
                metal=analysis, lead_isotope=lead_isotope,
                defaults={'lead_isotope_ratio': value},
            )

    print(f"\nDone: {stats}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import Iberlid lead isotope data from xlsx')
    parser.add_argument('--files', nargs='+', required=True, help='Path(s) to xlsx file(s)')
    parser.add_argument('--sheet', default=0, help='Sheet name or index (default: first sheet)')
    parser.add_argument('--dry-run', action='store_true', help='Only report which sites exist, write nothing')
    args = parser.parse_args()

    for file in args.files:
        print(f"Importing {os.path.basename(file)}")
        df = pd.read_excel(file, sheet_name=args.sheet).dropna(how='all').reset_index(drop=True)
        import_iberlid(df, dry_run=args.dry_run)
