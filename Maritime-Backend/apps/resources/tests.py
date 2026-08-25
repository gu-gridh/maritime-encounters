from pathlib import Path
import importlib.util

from django.contrib.gis.geos import Point
from django.test import TestCase

from apps.resources.models import Site


module_path = Path(__file__).resolve().parents[1] / "upload_scripts" / "import_boats.py"
spec = importlib.util.spec_from_file_location("import_boats_script", module_path)
import_boats_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(import_boats_module)
get_site = import_boats_module.get_site


class SiteLookupTests(TestCase):
    def test_get_site_handles_duplicate_site_names(self):
        point_a = Point(12.3456, 56.7890)
        point_b = Point(12.4567, 56.8901)

        Site.objects.create(name="Pesse", coordinates=point_a)
        Site.objects.create(name="Pesse", coordinates=point_b)

        site = get_site({"Site Name": "Pesse"}, point_a)

        self.assertEqual(site.coordinates, point_a)
        self.assertEqual(Site.objects.filter(name="Pesse").count(), 2)
