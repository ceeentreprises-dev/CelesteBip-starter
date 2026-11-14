"""Tests du moteur de publication (bibliothèque standard uniquement).

Lancer : python -m unittest discover -s tests -v
"""
import json
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import MOTEUR_PUBLICATION as mp  # noqa: E402


def png(w, h):
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + ihdr + struct.pack(">I", zlib.crc32(b"IHDR" + ihdr))


class MoteurTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self._old = mp.ROOT
        mp.ROOT = self.root
        self.d = self.root / "produits" / "carnet-test"
        self.d.mkdir(parents=True)
        (self.d / "carnet.txt").write_text("Contenu du produit.", encoding="utf-8")
        (self.d / "couverture.png").write_bytes(png(630, 500))
        self.m = {"titre": "Carnet de test complet", "version": "1.0.0", "prix_chf": 4.5, "licence": "Usage personnel",
                  "description": "x" * 300, "fichiers": ["carnet.txt"], "couverture": "couverture.png",
                  "mots_cles": ["a", "b", "c"]}
        self.ecrire()

    def ecrire(self):
        (self.d / "produit.json").write_text(json.dumps(self.m), encoding="utf-8")

    def tearDown(self):
        mp.ROOT = self._old
        self._tmp.cleanup()

    def test_produit_complet_vaut_100(self):
        r = mp.evaluer(self.d)
        self.assertEqual((r["score"], r["bloquants"]), (100, []))

    def test_conseil_le_plus_rentable_en_premier(self):
        del self.m["couverture"]
        self.m["mots_cles"] = []
        self.ecrire()
        r = mp.evaluer(self.d)
        self.assertEqual(r["score"], 75)
        self.assertEqual(r["conseils"][0][0], 15)

    def test_iban_bloque_la_preparation(self):
        (self.d / "carnet.txt").write_text("IBAN CH93 0076 2011 6238 5295 7", encoding="utf-8")
        with self.assertRaises(RuntimeError):
            mp.preparer(self.d, self.root / "out")

    def test_fichier_hors_depot_refuse(self):
        self.m["fichiers"] = ["../../../etc/hostname"]
        self.ecrire()
        self.assertTrue(mp.evaluer(self.d)["bloquants"])

    def test_kit_reproductible(self):
        a = (mp.preparer(self.d, self.root / "out") / "SHA256SUMS").read_text()
        b = (mp.preparer(self.d, self.root / "out") / "SHA256SUMS").read_text()
        self.assertEqual(a, b)
        self.assertIn("carnet-test-1.0.0.zip", a)


if __name__ == "__main__":
    unittest.main()
