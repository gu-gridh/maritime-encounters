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
from apps.resources.models import (
	Boat,
	BoatComponent,
	BoatFeatures,
	BoatMaterial,
	BoatRelComponent,
	CalibratedDate,
	DateRanges,
	Location,
	Period,
	Phase,
	Site,
)


DEFAULT_FILE = os.path.join(
	os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
	"resources",
	"BoatBuildingCombined_ForUpload_BB_8July_2026.xlsx",
)


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
	return text[: max_len - 1].rstrip()


def as_int_or_none(value):
	if value is None or (isinstance(value, float) and np.isnan(value)):
		return None
	try:
		return int(float(value))
	except Exception:
		return None


def as_bool_or_none(value):
	if value is None or (isinstance(value, float) and np.isnan(value)):
		return None
	if isinstance(value, bool):
		return value

	text = str(value).strip().lower()
	if text in {"true", "t", "yes", "y", "1", "present", "x"}:
		return True
	if text in {"false", "f", "no", "n", "0", "absent"}:
		return False
	return None


def split_values(value):
	text = value_or_none(value)
	if not text:
		return []

	parts = [text]
	for delimiter in [";", ",", "|"]:
		new_parts = []
		for part in parts:
			new_parts.extend(part.split(delimiter))
		parts = new_parts
	return [part.strip() for part in parts if part and part.strip()]


def normalize_vessel_type(raw_value):
	text = (value_or_none(raw_value) or "").lower()
	if not text:
		return None

	if "log" in text:
		return "log"
	if "plank" in text:
		return "plank"
	if "bark" in text:
		return "bark"
	return None


def resolve_point(row):
	lat = row.get("Lat")
	lng = row.get("Long")
	if lat is None:
		lat = row.get("Latitude")
	if lng is None:
		lng = row.get("Lng")
	if lng is None:
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


def get_site(row, point):
	site_name = value_or_none(row.get("Site Name"))
	adm4, adm3, adm2, adm1, country, province, parish = resolve_admin_units(point)

	if site_name:
		site_candidates = Site.objects.filter(name=site_name)
		if point:
			site_obj = site_candidates.filter(coordinates=point).first()
			if site_obj is None:
				site_obj = (
					site_candidates.filter(ADM0=country, ADM1=adm1, ADM2=adm2, ADM3=adm3, ADM4=adm4, Province=province, Parish=parish)
					.first()
					or site_candidates.filter(coordinates__isnull=False).first()
					or site_candidates.first()
			)
		else:
			site_obj = site_candidates.first()
		if site_obj is None:
			site_obj = Site.objects.create(name=site_name)
	elif point:
		site_obj = Site.objects.filter(coordinates=point).first()
		if site_obj is None:
			site_obj = Site.objects.create(
				coordinates=point,
				name=f"Boat site ({point.y:.6f}, {point.x:.6f})",
			)
	else:
		site_obj = Site.objects.filter(name="Unknown boat site").first()
		if site_obj is None:
			site_obj = Site.objects.create(name="Unknown boat site")

	# Keep geography and coordinates in sync when they are available.
	changed = False
	if point and not site_obj.coordinates:
		site_obj.coordinates = point
		changed = True
	if country and not site_obj.ADM0:
		site_obj.ADM0 = country
		changed = True
	if adm1 and not site_obj.ADM1:
		site_obj.ADM1 = adm1
		changed = True
	if adm2 and not site_obj.ADM2:
		site_obj.ADM2 = adm2
		changed = True
	if adm3 and not site_obj.ADM3:
		site_obj.ADM3 = adm3
		changed = True
	if adm4 and not site_obj.ADM4:
		site_obj.ADM4 = adm4
		changed = True
	if province and not site_obj.Province:
		site_obj.Province = province
		changed = True
	if parish and not site_obj.Parish:
		site_obj.Parish = parish
		changed = True
	if changed:
		site_obj.save()

	return site_obj


def get_period(row):
	period_name = value_or_none(row.get("Period"))
	if not period_name:
		return None

	phase_obj = None
	phase_text = value_or_none(row.get("Phase"))
	if phase_text:
		# Handle historical duplicates gracefully by reusing the first match.
		phase_obj = Phase.objects.filter(text=phase_text).order_by("id").first()
		if phase_obj is None:
			phase_obj = Phase.objects.create(text=phase_text)

	start_date = as_int_or_none(row.get("Period Start Date"))
	end_date = as_int_or_none(row.get("Period End Date"))

	period_filter = {
		"name": period_name,
		"phase": phase_obj,
		"start_date": start_date,
		"end_date": end_date,
	}
	period_obj = Period.objects.filter(**period_filter).order_by("id").first()
	if period_obj is None:
		period_obj = Period.objects.create(**period_filter)
	return period_obj


def get_date_range(row):
	start_date = as_int_or_none(row.get("Vessel Start Date"))
	end_date = as_int_or_none(row.get("Vessel End Date"))
	if start_date is None and end_date is None:
		return None

	date_range, _ = DateRanges.objects.get_or_create(
		text=f"{start_date} - {end_date}",
		start_date=start_date,
		end_date=end_date,
	)
	return date_range


def get_carbon_dates(row):
	date_text = value_or_none(row.get("14C Date"))
	labs = split_values(row.get("14C Lab"))

	if not date_text and not labs:
		return []
	if not labs:
		labs = [None]

	dates = []
	for lab in labs:
		cal_date, _ = CalibratedDate.objects.get_or_create(
			sample=value_or_none(row.get("Vessel Name")),
			lab=lab,
			date=date_text,
		)
		dates.append(cal_date)
	return dates


def get_or_create_component(part_type, material_value, row):
	material_names = split_values(material_value)
	if not material_names:
		return None

	component, _ = BoatComponent.objects.get_or_create(
		part_type=part_type,
		description=value_or_none(row.get("Hull Finish")) if part_type == "hull" else None,
		length_est=value_or_none(row.get("Hull Length Est")) if part_type == "hull" else None,
		width_est=value_or_none(row.get("Hull Width Est")) if part_type == "hull" else None,
		height_est=value_or_none(row.get("Hull Height Est")) if part_type == "hull" else None,
		length_meas=value_or_none(row.get("Hull Length Actual")) if part_type == "hull" else None,
		width_meas=value_or_none(row.get("Hull Width Actual")) if part_type == "hull" else None,
		height_meas=value_or_none(row.get("Hull Height Actual")) if part_type == "hull" else None,
		integral_bool=as_bool_or_none(row.get("Integral Cleat Bool")) if part_type == "hull" else None,
		integral_dist=value_or_none(row.get("Integral Cleats Distance")) if part_type == "hull" else None,
	)

	materials = []
	for name in material_names:
		material, _ = BoatMaterial.objects.get_or_create(common_name=value_limited(name, 256))
		materials.append(material)
	if materials:
		component.material.set(materials)

	return component


def import_boats(data, dry_run=False):
	created_count = 0
	updated_count = 0

	component_map = {
		"hull": "Hull Material",
		"frames": "Frames or Ribs Material",
		"thwarts": "Thwarts Material",
		"bottom_side_strakes": "Bottom Side Strakes Material",
		"outer_bottom_plank": "Outer Bottom Plank Material",
		"keep_plank": "Keel Plank Material",
		"caulking": "Caulking Material",
	}

	for idx, row in data.iterrows():
		with transaction.atomic():
			point = resolve_point(row)
			site = get_site(row, point)

			location = None
			site_description = value_or_none(row.get("Site Description"))
			if site_description:
				location, _ = Location.objects.get_or_create(location_detail=site_description)

			vessel_name = value_or_none(row.get("Vessel Name"))
			vessel_type = normalize_vessel_type(row.get("Vessel Type"))

			boat, created = Boat.objects.update_or_create(
				site=site,
				vessel_name=vessel_name,
				defaults={
					"vessel_type": vessel_type,
					"location": location,
					"description": value_or_none(row.get("Vessel Description")),
					"period": get_period(row),
					"reconstruction": as_bool_or_none(row.get("Reconstruction Boat")),
					"recon_description": value_or_none(row.get("Reconstruction Details")),
					"thickness": value_limited(row.get("Thickness (cm)"), 256),
					"thickness_measured": value_limited(row.get("Thickness Measured"), 256),
					"sealing_lath": value_limited(row.get("CleatHoles SewingHoles Size"), 256),
					"rail_plough": value_limited(row.get("Rail Plough"), 256),
					"tree_nails": value_limited(row.get("Tree Nails"), 256),
					"hewn_out_ridges": as_bool_or_none(row.get("Hewn-out Ridges")),
					"tool_marks": value_limited(row.get("Tool Marks"), 256),
					"potential_tools": value_limited(row.get("Potential Tools"), 256),
					"fastening_method": value_limited(row.get("Fastening Method"), 256),
					"comments": value_or_none(row.get("Comments")),
					"references": value_or_none(row.get("References")),
					"national_id": value_limited(row.get("National Register"), 200),
				},
			)

			date_range = get_date_range(row)
			if date_range:
				boat.date_ranges.set([date_range])

			carbon_dates = get_carbon_dates(row)
			if carbon_dates:
				boat.carbon_date.set(carbon_dates)

			features = []
			for feature in split_values(row.get("Special Features")):
				feature_obj, _ = BoatFeatures.objects.get_or_create(text=value_limited(feature, 256))
				features.append(feature_obj)
			if features:
				boat.special_features.set(features)

			BoatRelComponent.objects.filter(boat=boat).delete()
			for part_type, column in component_map.items():
				component = get_or_create_component(part_type, row.get(column), row)
				if component:
					BoatRelComponent.objects.get_or_create(boat=boat, component=component)

			if dry_run:
				transaction.set_rollback(True)

			if created:
				created_count += 1
			else:
				updated_count += 1

			print(f"[Row {idx}] {'DRY-RUN ' if dry_run else ''}{'created' if created else 'updated'} boat: {vessel_name}")

	return created_count, updated_count


def main():
	parser = argparse.ArgumentParser(description="Import boats from XLSX into Boat model")
	parser.add_argument(
		"--file",
		"--files",
		dest="files",
		nargs="*",
		type=str,
		help="One or more .xlsx files",
	)
	parser.add_argument("--dry-run", action="store_true", help="Parse and validate rows without saving")
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
			created, updated = import_boats(df, dry_run=args.dry_run)
			print(
				f"Finished {sheet} | created={created}, updated={updated}, dry_run={args.dry_run}"
			)


if __name__ == "__main__":
	main()
