#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Registre de risque CelestBIP : la partie saine du cadre ISO 31000, lancée à la main.

Identifier -> analyser (proba x gravité) -> évaluer -> traiter (éviter/réduire/transférer/accepter).
Volontairement SANS autonomie : aucun déclenchement automatique, aucun relais entre agents, aucun réseau.
C'est vous qui le relancez quand une décision change.

Copyright (c) 2026 ceeentreprises-dev. Tous droits réservés : voir LICENCE-MOTEUR.md (pas la licence MIT du dépôt).

USAGE:
    python registre_risques.py                 # lit registre_risques.json, trie, montre les urgents d'abord
    python registre_risques.py autre.json      # un autre fichier
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
DEFAUT = ROOT / "registre_risques.json"
TRAITEMENTS = ("éviter", "réduire", "transférer", "accepter")
MAX_ACTIFS = 7   # garde-fou anti-bureaucratie : le cadre d'origine le demandait, on l'impose


def valider(r: dict, i: int, vus: set) -> list:
    """Frontière de confiance : un risque mal formé ne passe pas en silence."""
    e = []
    rid = str(r.get("id", "")).strip()
    if not rid or rid in vus:
        e.append(f"risque #{i} : id manquant ou en double")
    vus.add(rid)
    if not str(r.get("titre", "")).strip():
        e.append(f"{rid or i} : titre manquant")
    for champ in ("proba", "gravite"):
        v = r.get(champ)
        if not isinstance(v, int) or isinstance(v, bool) or not 1 <= v <= 5:
            e.append(f"{rid or i} : {champ} doit être un entier de 1 à 5")
    f = r.get("fenetre_jours")
    if not isinstance(f, int) or isinstance(f, bool) or f < 0:
        e.append(f"{rid or i} : fenetre_jours doit être un entier >= 0")
    if r.get("traitement") not in TRAITEMENTS:
        e.append(f"{rid or i} : traitement doit être l'un de {', '.join(TRAITEMENTS)}")
    if not str(r.get("action_0chf", "")).strip():
        e.append(f"{rid or i} : action_0chf manquante (que faire, à 0 CHF)")
    if r.get("statut") not in ("actif", "clos"):
        e.append(f"{rid or i} : statut doit être actif ou clos")
    return e


def analyser(fichier: Path) -> dict:
    risques = json.loads(fichier.read_text(encoding="utf-8"))
    bloquants, vus = [], set()
    for i, r in enumerate(risques, 1):
        bloquants += valider(r, i, vus)
    if bloquants:
        return {"bloquants": bloquants, "lignes": []}
    actifs = [r for r in risques if r["statut"] == "actif"]
    if len(actifs) > MAX_ACTIFS:
        bloquants.append(f"{len(actifs)} risques actifs : maximum {MAX_ACTIFS}. Clôturez ou fusionnez avant d'en ajouter.")
    for r in actifs:
        r["score"] = r["proba"] * r["gravite"]              # 1 à 25, classique ISO
        r["urgent"] = r["fenetre_jours"] <= 30               # peut freiner l'encaissement sous 30 j
    actifs.sort(key=lambda r: (not r["urgent"], -r["score"], r["fenetre_jours"]))
    return {"bloquants": bloquants, "lignes": actifs}


def rendu(res: dict) -> str:
    out = []
    for r in res["lignes"]:
        marque = "URGENT" if r["urgent"] else "      "
        out.append(f"[{marque}] {r['id']} score {r['score']:2}/25  <{r['fenetre_jours']}j>  "
                   f"[{r['categorie']}] {r['titre']}")
        out.append(f"           -> {r['traitement']} : {r['action_0chf']}")
    for b in res["bloquants"]:
        out.append(f"BLOQUANT : {b}")
    return "\n".join(out) or "Aucun risque actif. Registre vide ou tout est clos."


def main():
    ap = argparse.ArgumentParser(description="Registre de risque CelestBIP (ISO 31000 sans autonomie)")
    ap.add_argument("fichier", nargs="?", default=str(DEFAUT))
    a = ap.parse_args()
    res = analyser(Path(a.fichier))
    texte = rendu(res)
    print(texte)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write("# Registre de risque\n\n```\n" + texte + "\n```\n")
    sys.exit(1 if res["bloquants"] else 0)


if __name__ == "__main__":
    main()
