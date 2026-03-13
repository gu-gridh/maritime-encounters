# This is a script to delete empty sites from the database.
# Those sites aren't included in any of resources needs to be removed
# from the database to avoid confusion and to keep the database clean.

import os
import sys
import django

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maritime.settings')
django.setup()

from django.db.models import Q
from apps.resources.models import (
    Site, Boat, LandingPoints, NewSamples, Radiocarbon,
    MetalAnalysis, aDNA, IsotopesBio, LNHouses, Metalwork, IndividualObjects
)

# All resource models that have a ForeignKey to Site
RESOURCE_MODELS = {
    'Boat': Boat,
    'LandingPoints': LandingPoints,
    'NewSamples': NewSamples,
    'Radiocarbon': Radiocarbon,
    'MetalAnalysis': MetalAnalysis,
    'aDNA': aDNA,
    'IsotopesBio': IsotopesBio,
    'LNHouses': LNHouses,
    'Metalwork': Metalwork,
    'IndividualObjects': IndividualObjects,
}


def check_site(site_id):
    """Check which resources reference a specific site."""
    try:
        site = Site.objects.get(id=site_id)
    except Site.DoesNotExist:
        print(f"Site {site_id} does not exist.")
        return

    print(f"Site {site_id}: {site}")
    print(f"  Coordinates: {site.coordinates}")
    print(f"  ADM0: {site.ADM0}")
    print()

    has_any = False
    for name, model in RESOURCE_MODELS.items():
        count = model.objects.filter(site=site).count()
        if count > 0:
            has_any = True
            print(f"  {name}: {count} record(s)")

    if not has_any:
        print("  ** No resources reference this site — safe to delete **")


def delete_empty_sites(dry_run=True):
    """
    Delete sites that are not referenced by any resource model.
    Set dry_run=False to actually delete.
    """
    total_sites = Site.objects.count()
    print(f"Total sites in database: {total_sites}")

    # Collect site IDs referenced by each resource
    referenced_site_ids = set()
    for name, model in RESOURCE_MODELS.items():
        ids = set(model.objects.filter(site__isnull=False).values_list('site_id', flat=True))
        print(f"  {name}: references {len(ids)} sites")
        referenced_site_ids.update(ids)

    print(f"\nTotal unique referenced sites: {len(referenced_site_ids)}")

    # Find sites not referenced by any resource
    empty_sites = Site.objects.exclude(id__in=referenced_site_ids)
    count = empty_sites.count()
    print(f"Sites to delete (unreferenced): {count}")

    if count > 0:
        # Show a few examples
        sample = empty_sites[:10]
        print("\nExample sites to delete:")
        for s in sample:
            print(f"  id={s.id}  name={s.name}  placename={s.placename}")

    if dry_run:
        print("\n[DRY RUN] No sites were deleted. Run with --execute to delete.")
    else:
        empty_sites.delete()
        print(f"\nDeleted {count} empty sites.")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Delete sites not referenced by any resource.')
    parser.add_argument('--execute', action='store_true',
                        help='Actually delete the sites. Without this flag, runs in dry-run mode.')
    parser.add_argument('--check', type=int, metavar='SITE_ID',
                        help='Check which resources reference a specific site ID.')
    args = parser.parse_args()

    if args.check:
        check_site(args.check)
    else:
        delete_empty_sites(dry_run=not args.execute)