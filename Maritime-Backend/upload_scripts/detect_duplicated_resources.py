# Script to detect and optionally delete duplicated resource records.
# Duplicates are identified by matching key fields (site + identifying fields).
# Run in dry-run mode by default; use --execute to actually delete duplicates.

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maritime.settings')
django.setup()

from django.db.models import Count, Min
from apps.resources.models import (
    Site, Boat, LandingPoints, NewSamples, Radiocarbon,
    MetalAnalysis, aDNA, IsotopesBio, LNHouses, Metalwork, IndividualObjects
)

# For each model, define the fields that together identify a unique record.
# Records sharing ALL these field values are considered duplicates.
DUPLICATE_KEYS = {
    'Radiocarbon': {
        'model': Radiocarbon,
        'fields': ['site', 'lab_id', 'c14_age', 'c14_std'],
    },
    'MetalAnalysis': {
        'model': MetalAnalysis,
        'fields': ['site', 'museum_entry', 'object_description', 'general_typology', 'typology'],
    },
    'aDNA': {
        'model': aDNA,
        'fields': ['site', 'genetic_id', 'master_id', 'skeletal_code'],
    },
    'IsotopesBio': {
        'model': IsotopesBio,
        'fields': ['site', 'individual_id', 'sample_number'],
    },
    'LNHouses': {
        'model': LNHouses,
        'fields': ['site', 'farmstead', 'structure_num', 'cadastral_num'],
    },
    'Metalwork': {
        'model': Metalwork,
        'fields': ['site', 'entry_num', 'literature_num', 'accession_num'],
    },
    'IndividualObjects': {
        'model': IndividualObjects,
        'fields': ['site', 'accession_number', 'museum', 'object_type', 'form', 'variant'],
    },
    'Boat': {
        'model': Boat,
        'fields': ['site', 'vessel_name', 'vessel_type'],
    },
    'LandingPoints': {
        'model': LandingPoints,
        'fields': ['site', 'start_date', 'end_date'],
    },
    'NewSamples': {
        'model': NewSamples,
        'fields': ['site', 'metal', 'sampler', 'drilled_location', 'date'],
    },
}


def detect_duplicates(resource_name, config, verbose=False):
    """
    Detect duplicate records for a given resource model.
    Returns a list of IDs to delete (keeps the oldest record per duplicate group).
    """
    model = config['model']
    fields = config['fields']

    # Group by the key fields, find groups with count > 1
    dupes = (
        model.objects.values(*fields)
        .annotate(cnt=Count('id'), min_id=Min('id'))
        .filter(cnt__gt=1)
    )

    ids_to_delete = []
    for group in dupes:
        # Build filter to find all records in this group
        filter_kwargs = {f: group[f] for f in fields}
        group_qs = model.objects.filter(**filter_kwargs).order_by('id')
        group_ids = list(group_qs.values_list('id', flat=True))

        # Keep the first (oldest) record, mark the rest for deletion
        keep_id = group_ids[0]
        delete_ids = group_ids[1:]
        ids_to_delete.extend(delete_ids)

        if verbose:
            print(f"  Group {filter_kwargs}: {len(group_ids)} records, keeping id={keep_id}, deleting {delete_ids}")

    return ids_to_delete


def run(dry_run=True, resource_filter=None, verbose=False):
    total_deleted = 0

    for name, config in DUPLICATE_KEYS.items():
        if resource_filter and name.lower() != resource_filter.lower():
            continue

        model = config['model']
        total = model.objects.count()
        ids_to_delete = detect_duplicates(name, config, verbose=verbose)
        count = len(ids_to_delete)
        total_deleted += count

        print(f"{name}: {total} total records, {count} duplicates found")

        if count > 0 and not dry_run:
            # Delete in batches to avoid memory issues
            batch_size = 500
            for i in range(0, len(ids_to_delete), batch_size):
                batch = ids_to_delete[i:i + batch_size]
                model.objects.filter(id__in=batch).delete()
            print(f"  -> Deleted {count} duplicate records")

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Total duplicates: {total_deleted}")
    if dry_run and total_deleted > 0:
        print("Run with --execute to delete them.")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Detect and delete duplicate resource records.')
    parser.add_argument('--execute', action='store_true',
                        help='Actually delete duplicates. Without this flag, runs in dry-run mode.')
    parser.add_argument('--resource', type=str, default=None,
                        help='Only check a specific resource (e.g. Radiocarbon, Boat, MetalAnalysis).')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show details for each duplicate group.')
    args = parser.parse_args()

    run(dry_run=not args.execute, resource_filter=args.resource, verbose=args.verbose)
