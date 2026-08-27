import argparse
import os
import sys

import django
import numpy as np
import pandas as pd
from django.contrib.gis.geos import Point
from django.db import transaction


# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "maritime.settings")
django.setup()

from apps.geography.models import ADM0, ADM1, ADM2, ADM3, ADM4, Parish, Province
from apps.resources.models import Site, SiteType


DEFAULT_FILE = os.path.join(
	os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
	"resources",
	"Bronze_Age_Mining_Sites_240826.xlsx",
)

# Every row in these tables is a mining site. The SiteType is created by the
# import itself rather than assumed to exist, so running this against a fresh
# database (the server) adds the vocabulary entry as well as the sites.
DEFAULT_SITE_TYPE = "Mining site"

# Columns the spreadsheet carries that the Site model has nowhere to store.
# Site has no period, date or reference field - see the note in --report.
UNMAPPED_COLUMNS = [
	"Start Date",
	"End Date",
	"BCE Year(s) of Exploitation",
	"Approximate Age of Exploitation",
	"Period",
	"Rationale_Associated Finds",
	"Full References (Harvard Style)",
]


def value_or_none(value):
	if value is None:
		return None
	if isinstance(value, float) and np.isnan(value):
		return None
	text = str(value).strip()
	return text if text else None


def value_limited(value, max_len):
	text = value_or_none(value)
	if not text:
		return None
	if len(text) <= max_len:
		return text
	return text[:max_len].rstrip()


def resolve_point(row):
	lat = row.get("Latitude")
	lng = row.get("Longitude")

	try:
		if pd.notna(lat) and pd.notna(lng):
			return Point(float(lng), float(lat))
	except Exception:
		return None
	return None


def resolve_admin_units(point):
	adm4 = adm3 = adm2 = adm1 = country = province = parish = None
	if not point:
		return adm4, adm3, adm2, adm1, country, province, parish

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
		country = ADM0.objects.get(geometry__contains=point)
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

	return adm4, adm3, adm2, adm1, country, province, parish


def get_site(name, point):
	"""Find the Site this row describes, or create it.

	Localities are unique within the mining tables, but the name alone can
	collide with an unrelated site already in the database, so an existing row
	only counts as a match when its coordinates agree (or it has none yet).
	"""
	if name:
		candidates = Site.objects.filter(name=name)
		if point:
			site_obj = (
				candidates.filter(coordinates=point).first()
				or candidates.filter(coordinates__isnull=True).first()
			)
		else:
			site_obj = candidates.first()
		if site_obj is None:
			return Site.objects.create(name=name), True
		return site_obj, False

	site_obj = Site.objects.filter(coordinates=point).first()
	if site_obj is None:
		return Site.objects.create(
			coordinates=point,
			name=f"Mining site ({point.y:.6f}, {point.x:.6f})",
		), True
	return site_obj, False


def import_mining_sites(data, site_type_text=DEFAULT_SITE_TYPE, dry_run=False):
	created_count = 0
	updated_count = 0
	skipped_count = 0

	for idx, row in data.iterrows():
		name = value_limited(row.get("Locality"), 256)
		point = resolve_point(row)

		if not name and not point:
			print(f"[Row {idx}] skipped: no locality and no coordinates")
			skipped_count += 1
			continue

		with transaction.atomic():
			# Resolved inside the transaction so a --dry-run leaves no new
			# vocabulary entry behind.
			site_type, _ = SiteType.objects.get_or_create(text=site_type_text)
			site, created = get_site(name, point)
			adm4, adm3, adm2, adm1, country, province, parish = resolve_admin_units(point)

			# Coordinates and geography are the authoritative values from this
			# table, so they overwrite whatever an earlier import guessed - but
			# a resolved unit is never replaced with a null.
			if point:
				site.coordinates = point
			if country:
				site.ADM0 = country
			if adm1:
				site.ADM1 = adm1
			if adm2:
				site.ADM2 = adm2
			if adm3:
				site.ADM3 = adm3
			if adm4:
				site.ADM4 = adm4
			if province:
				site.Province = province
			if parish:
				site.Parish = parish

			region = value_limited(row.get("Region"), 256)
			if region and not site.placename:
				site.placename = region

			site.save()
			site.site_type.add(site_type)

			if dry_run:
				transaction.set_rollback(True)

			if created:
				created_count += 1
			else:
				updated_count += 1

			resolved = country.name if country else "no ADM0"
			print(
				f"[Row {idx}] {'DRY-RUN ' if dry_run else ''}"
				f"{'created' if created else 'updated'} site: {name} ({resolved})"
			)

	return created_count, updated_count, skipped_count


def report(data):
	"""Print how each row resolves, without writing anything."""
	print("\n== Admin units resolved from the coordinates ==")
	unresolved = 0
	for idx, row in data.iterrows():
		point = resolve_point(row)
		name = value_or_none(row.get("Locality"))
		if not point:
			print(f"[Row {idx}] {name}: no coordinates")
			unresolved += 1
			continue

		adm4, adm3, adm2, adm1, country, province, parish = resolve_admin_units(point)
		levels = [
			("ADM0", country),
			("ADM1", adm1),
			("ADM2", adm2),
			("ADM3", adm3),
			("ADM4", adm4),
			("Province", province),
			("Parish", parish),
		]
		found = ", ".join(f"{label}={unit.name}" for label, unit in levels if unit)
		if not found:
			found = "nothing - point falls outside every imported ADM layer"
			unresolved += 1
		print(f"[Row {idx}] {name} ({row.get('Country')}): {found}")

	print(f"\n    {unresolved} of {len(data)} rows resolve to no admin unit at all")

	# Most misses are simply countries whose ADM layers were never imported.
	# A miss inside a country that *is* loaded points at bad coordinates instead.
	loaded = set(ADM0.objects.values_list("name", flat=True))
	print(f"    ADM0 layers currently loaded: {', '.join(sorted(loaded))}")

	suspect = []
	for idx, row in data.iterrows():
		point = resolve_point(row)
		country = value_or_none(row.get("Country"))
		if not point or not country or country not in loaded:
			continue
		if ADM0.objects.filter(geometry__contains=point).exists():
			continue
		suspect.append((idx, value_or_none(row.get("Locality")), country, point))

	if suspect:
		print("\n== Coordinates that look wrong ==")
		print("    The Country column names a country whose ADM layers ARE loaded,")
		print("    yet the point falls outside it - check the sign of the longitude.")
		for idx, name, country, point in suspect:
			print(f"[Row {idx}] {name} ({country}): lat={point.y}, lon={point.x}")

	print("\n== Columns present in the file but not imported ==")
	print("    The Site model has no period, date or reference field.")
	for column in UNMAPPED_COLUMNS:
		if column in data.columns:
			print(f"    {column}: {int(data[column].notna().sum())} non-empty rows")


def main():
	parser = argparse.ArgumentParser(
		description="Import mining sites from XLSX into the Site model"
	)
	parser.add_argument(
		"--file",
		"--files",
		dest="files",
		nargs="*",
		type=str,
		help="One or more .xlsx files",
	)
	parser.add_argument(
		"--site-type",
		default=DEFAULT_SITE_TYPE,
		help=f"SiteType to tag every imported site with (default: {DEFAULT_SITE_TYPE})",
	)
	parser.add_argument("--dry-run", action="store_true", help="Parse and validate rows without saving")
	parser.add_argument(
		"--report",
		action="store_true",
		help="Print how each row resolves (read-only, writes nothing)",
	)
	args = parser.parse_args()

	files = args.files or [DEFAULT_FILE]
	for file in files:
		if not os.path.exists(file):
			print(f"File not found: {file}")
			continue

		workbook = pd.ExcelFile(file)
		for sheet in workbook.sheet_names:
			print(f"Importing {os.path.basename(file)} :: {sheet}")
			df = pd.read_excel(file, sheet_name=sheet).replace({np.nan: None})
			if args.report:
				report(df)
				continue
			created, updated, skipped = import_mining_sites(
				df, site_type_text=args.site_type, dry_run=args.dry_run
			)
			print(
				f"Finished {sheet} | created={created}, updated={updated}, "
				f"skipped={skipped}, dry_run={args.dry_run}"
			)


if __name__ == "__main__":
	main()
