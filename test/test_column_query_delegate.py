import os
import sys
import unittest
from django.conf import settings

# Ensure the project root is on the path so the locally built extension is imported
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

SETTINGS = {
    "INSTALLED_APPS": ["columntestapp"],
    "DATABASES": {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "daffodil_hstore_test",
            "USER": "postgres",
            "PASSWORD": "postgres",
            "HOST": "127.0.0.1",
            "PORT": 5432,
        }
    },
    "MIDDLEWARE": [],
}

if not settings.configured:
    settings.configure(**SETTINGS)

import django
try:
    django.setup()
except AttributeError:
    pass

from django.core import management
from daffodil import Daffodil, ColumnQueryDelegate
from columntestapp.models import BasicColumnData
from test.data.nyc_sat_scores import NYC_SAT_SCORES


class ColumnDelegateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        management.call_command("migrate", verbosity=0)
        BasicColumnData.objects.all().delete()
        for record in NYC_SAT_SCORES:
            data = record.copy()
            if "$calculated_pct" in data:
                data["cc_calculated_pct"] = int(data.pop("$calculated_pct"))
            if "zip_code" in data:
                data["zip_code"] = int(data["zip_code"])
            if "total_score" in data:
                try:
                    data["total_score"] = float(data["total_score"])
                except (TypeError, ValueError):
                    data["total_score"] = None
            BasicColumnData.objects.create(**data)
        BasicColumnData.objects.create(cc_amount___total=5, foo_bar=1)

    def setUp(self):
        self.qs = BasicColumnData.objects.all()
        self.delegate = ColumnQueryDelegate()

    def _count(self, fltr):
        daff = Daffodil(fltr, delegate=self.delegate)
        return daff(self.qs).count()

    def test_basic(self):
        self.assertEqual(self._count("zip_code = 8002"), 1)

    def test_key_transforms(self):
        self.assertEqual(self._count('"$amount - total" = 5'), 1)
        self.assertEqual(self._count('"foo-bar" = 1'), 1)

    def test_in_operators(self):
        self.assertEqual(self._count("zip_code in (10004, 10002)"), 1)
        self.assertEqual(self._count("zip_code !in (10004, 10002)"), self.qs.count() - 1)

    def test_existence_and_not_equal(self):
        self.assertEqual(self._count("zip_code ?= true"), 7)
        self.assertEqual(self._count("zip_code ?= false"), self.qs.count() - 7)
        self.assertEqual(self._count("zip_code != 10004"), self.qs.count() - 1)


if __name__ == "__main__":
    unittest.main()
