"""Tests unitaires de CelestBIP Starter (bibliothèque standard uniquement).

Lancer : python -m unittest discover -s tests -v
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import CELESTBIP_MASTER as cb  # noqa: E402


class IbanTests(unittest.TestCase):
    def test_valid_example(self):
        self.assertTrue(cb.valid_swiss_iban("CH93 0076 2011 6238 5295 7"))

    def test_wrong_checksum(self):
        self.assertFalse(cb.valid_swiss_iban("CH94 0076 2011 6238 5295 7"))

    def test_wrong_country_or_length(self):
        self.assertFalse(cb.valid_swiss_iban("FR7630006000011234567890189"))
        self.assertFalse(cb.valid_swiss_iban("CH93"))


class BuildTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        tmp = Path(self._tmp.name)
        self._old = (cb.DIST, cb.RELEASE, cb.CONFIG_FILE)
        cb.DIST, cb.RELEASE, cb.CONFIG_FILE = tmp / "dist", tmp / "release", tmp / "support-approved.json"

    def tearDown(self):
        cb.DIST, cb.RELEASE, cb.CONFIG_FILE = self._old
        self._tmp.cleanup()

    def test_build_has_no_payment_by_default(self):
        summary = cb.build()
        self.assertFalse(summary["payments_active"])
        self.assertEqual(cb.checks(), [])

    def test_support_needs_three_approvals(self):
        cb.CONFIG_FILE.write_text(json.dumps({
            "iban": "CH93 0076 2011 6238 5295 7", "beneficiary": "Test",
            "bank_owner_confirmed": True, "legal_checks_confirmed": True,
            "explicit_publish_approval": False}), encoding="utf-8")
        self.assertIsNone(cb.load_approved_support())

    def test_invalid_iban_is_rejected(self):
        cb.CONFIG_FILE.write_text(json.dumps({
            "iban": "CH00 0000 0000 0000 0000 0", "beneficiary": "Test",
            "bank_owner_confirmed": True, "legal_checks_confirmed": True,
            "explicit_publish_approval": True}), encoding="utf-8")
        with self.assertRaises(ValueError):
            cb.load_approved_support()

    def test_package_creates_archive(self):
        path = cb.package()
        self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()
