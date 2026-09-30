"""Tag every Site with a Site Type for each kind of data it has in resources.

For each resource table that points at a site (Radiocarbon, Individual finds,
Metalwork, ...) the sites with at least one row get the matching Site Type, e.g.
Radiocarbon, Findspot. The labels live in apps/resources/site_data_types.py.

Additive and idempotent: it only ever adds missing (site, site type) pairs, never
removes or edits anything, and creates a SiteType only if it does not exist yet -
so it is safe to re-run after each import. Hand-tagged types (mining) are untouched.
"""

import argparse
import os
import sys

import django
from django.db import transaction


# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "maritime.settings")
django.setup()

from apps.resources import models
from apps.resources.models import Site, SiteType
from apps.resources.site_data_types import DATA_TYPE_LABELS


def fill_data_site_types(dry_run=False, verbose=False):
	through = Site.site_type.through
	existing = set(through.objects.values_list("site_id", "sitetype_id"))

	with transaction.atomic():
		to_add = []
		print(f"{'model':<20}{'site type':<24}{'sites':>8}{'to add':>8}")
		for model_name, label in DATA_TYPE_LABELS.items():
			model = getattr(models, model_name)
			site_ids = set(
				model.objects.filter(site__isnull=False).values_list("site_id", flat=True).distinct()
			)

			# A dry run still creates the SiteType inside the transaction so the
			# counts are accurate; it is rolled back below.
			site_type, created = SiteType.objects.get_or_create(text=label)
			new = {(s, site_type.id) for s in site_ids} - existing
			to_add.extend(sorted(new))

			print(f"{model_name:<20}{label + (' (new)' if created else ''):<24}{len(site_ids):>8}{len(new):>8}")
			if verbose and new:
				names = dict(Site.objects.filter(id__in=[s for s, _ in new]).values_list("id", "name"))
				for site_id, _ in sorted(new):
					print(f"    {site_id}: {names.get(site_id)!r}")

		through.objects.bulk_create(
			[through(site_id=s, sitetype_id=t) for s, t in to_add],
			ignore_conflicts=True,
			batch_size=1000,
		)

		untagged = Site.objects.filter(site_type__isnull=True).count()

		if dry_run:
			transaction.set_rollback(True)

	print(f"\n{'DRY-RUN - rolled back. Would have added' if dry_run else 'Added'} {len(to_add)} pairs.")
	if not dry_run:
		print(f"Sites still without any site type: {untagged} (no resource rows and not hand-tagged)")
	return len(to_add)


def main():
	parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
	parser.add_argument("--dry-run", action="store_true", help="Report what would change without saving")
	parser.add_argument("--verbose", action="store_true", help="List every site that will get a new type")
	args = parser.parse_args()

	fill_data_site_types(dry_run=args.dry_run, verbose=args.verbose)


if __name__ == "__main__":
	main()
