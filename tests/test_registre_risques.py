"""Tests du registre de risque (bibliothèque standard uniquement).
Copyright (c) 2026 ceeentreprises-dev. Tous droits réservés : voir LICENCE-MOTEUR.md.

Lancer : python -m unittest discover -s tests -v
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import registre_risques as rr  # noqa: E402


def risque(**kw):
    base = {"id": "R1", "titre": "x", "categorie": "securite", "proba": 3, "gravite": 3,
            "fenetre_jours": 10, "traitement": "réduire", "action_0chf": "faire x", "statut": "actif"}
    base.update(kw)
    return base


class RegistreTests(unittest.TestCase):
    def analyser(self, risques):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(risques, f)
            p = Path(f.name)
        try:
            return rr.analyser(p)
        finally:
            p.unlink()

    def test_fichier_valide_le_registre_sème(self):
        res = rr.analyser(rr.DEFAUT)
        self.assertEqual(res["bloquants"], [])
        self.assertTrue(res["lignes"])

    def test_urgent_avant_fort_score(self):
        res = self.analyser([
            risque(id="A", proba=5, gravite=5, fenetre_jours=60),   # score 25 mais lointain
            risque(id="B", proba=2, gravite=2, fenetre_jours=5),    # score 4 mais urgent
        ])
        self.assertEqual([l["id"] for l in res["lignes"]], ["B", "A"])

    def test_proba_hors_bornes_bloque(self):
        self.assertTrue(self.analyser([risque(proba=6)])["bloquants"])

    def test_traitement_inconnu_bloque(self):
        self.assertTrue(self.analyser([risque(traitement="ignorer")])["bloquants"])

    def test_id_en_double_bloque(self):
        self.assertTrue(self.analyser([risque(id="R1"), risque(id="R1")])["bloquants"])

    def test_plus_de_sept_actifs_bloque(self):
        res = self.analyser([risque(id=f"R{i}") for i in range(8)])
        self.assertTrue(any("maximum 7" in b for b in res["bloquants"]))

    def test_clos_non_compte(self):
        res = self.analyser([risque(id=f"R{i}") for i in range(7)] + [risque(id="R7", statut="clos")])
        self.assertEqual(res["bloquants"], [])
        self.assertEqual(len(res["lignes"]), 7)


if __name__ == "__main__":
    unittest.main()
