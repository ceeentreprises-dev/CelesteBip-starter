#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Moteur de publication CelestBIP : vérifie chaque produit, calcule son score de préparation (sur 100),
classe les améliorations par points gagnés et prépare un kit de distribution reproductible.

USAGE:
    python MOTEUR_PUBLICATION.py verifier                  # tous les produits de produits/
    python MOTEUR_PUBLICATION.py preparer                  # kits prêts dans release/publication/
    python MOTEUR_PUBLICATION.py verifier produits/<nom>   # un seul produit

Un produit = un dossier produits/<nom>/ avec un produit.json (voir README).
AUCUN appel réseau, aucune mise en vente automatique : publier reste un geste humain.
Licence du code : MIT.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import sys
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

from CELESTBIP_MASTER import valid_swiss_iban

ROOT = Path(__file__).resolve().parent
PRODUITS = ROOT / "produits"
SORTIE = ROOT / "release" / "publication"

SECRETS = {   # ce qui ne doit jamais partir dans un produit vendu
    "clé privée": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "clé d'API": re.compile(r"\b(?:sk-(?:ant-)?[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_\w{30,}|AKIA[0-9A-Z]{16})"),
    "mot de passe": re.compile(r"(?i)\b(?:password|mot de passe)\s*[:=]\s*\S+"),
}
IBAN_CH = re.compile(r"\bCH\d{2}(?:\s?[0-9A-Z]){17}\b")


def chemin(dossier: Path, nom: str):
    """Frontière de confiance : un manifeste ne peut pas désigner un fichier hors du dépôt."""
    p = (dossier / nom).resolve()
    return p if p.is_relative_to(ROOT.resolve()) else None


def taille_image(p: Path):
    """(largeur, hauteur) d'un PNG ou d'un JPEG, lue dans l'en-tête ; None sinon."""
    b = p.read_bytes()
    if b[:8] == b"\x89PNG\r\n\x1a\n" and b[12:16] == b"IHDR":
        return struct.unpack(">II", b[16:24])
    if b[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(b):
            if b[i] != 0xFF or b[i + 1] == 0xFF:
                i += 1
                continue
            m = b[i + 1]
            if 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
                h, w = struct.unpack(">HH", b[i + 5:i + 9])
                return w, h
            i += 2 + struct.unpack(">H", b[i + 2:i + 4])[0]
    return None


def secrets_trouves(fichiers) -> list:
    trouves = []
    for f in fichiers:
        b = f.read_bytes()
        if b"\0" in b[:4096] or len(b) > 5_000_000:   # shortcut: binaires (PDF, images) non lus, à revoir si un produit livre du texte dans un binaire
            continue
        texte = b.decode("utf-8", "ignore")
        trouves += [f"{nom} dans {f.name}" for nom, motif in SECRETS.items() if motif.search(texte)]
        trouves += [f"IBAN dans {f.name}" for m in IBAN_CH.findall(texte) if valid_swiss_iban(m)][:1]
    return trouves


def evaluer(dossier: Path) -> dict:
    dossier = Path(dossier)
    try:
        m = json.loads((dossier / "produit.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return {"slug": dossier.name, "score": 0, "bloquants": [f"produit.json illisible : {e}"], "conseils": []}
    titre, desc = str(m.get("titre", "")).strip(), str(m.get("description", "")).strip()
    fichiers = [chemin(dossier, str(f)) for f in m.get("fichiers", [])]
    ok_fichiers = (bool(fichiers) and all(f and f.is_file() and f.stat().st_size > 0 for f in fichiers)
                   and len({f.name for f in fichiers}) == len(fichiers))
    couv = chemin(dossier, str(m["couverture"])) if m.get("couverture") else None
    dims = taille_image(couv) if couv and couv.is_file() else None
    fuites = secrets_trouves([dossier / "produit.json"] + [f for f in fichiers if f and f.is_file()])
    prix = m.get("prix_chf")
    regles = [   # (points, bloquant si raté, réussi, conseil) : total 100
        (20, True, ok_fichiers, "fichiers : chaque fichier listé existe dans le dépôt, n'est pas vide, noms tous différents"),
        (15, True, not fuites, "secrets à retirer avant toute publication : " + ", ".join(fuites)),
        (10, True, 10 <= len(titre) <= 80, "titre : entre 10 et 80 caractères"),
        (15, not desc, len(desc) >= 300, "description : au moins 300 caractères, dire à qui sert le produit et ce qu'il apporte"),
        (5, True, isinstance(prix, (int, float)) and not isinstance(prix, bool) and prix >= 0, "prix_chf : un nombre, 0 si gratuit"),
        (5, True, bool(str(m.get("licence", "")).strip()), "licence : dire ce que l'acheteur a le droit de faire"),
        (5, True, bool(re.fullmatch(r"\d+\.\d+\.\d+", str(m.get("version", "")))), "version : au format 1.0.0"),
        (15, False, dims is not None, "couverture : ajouter une image PNG ou JPG, c'est elle qui fait cliquer"),
        (5, False, bool(dims) and dims[0] >= 630 and dims[1] >= 500, "couverture : au moins 630 × 500 px (format itch.io)"),
        (5, False, 3 <= len(m.get("mots_cles", [])) <= 10, "mots_cles : entre 3 et 10 (itch.io en accepte 10)"),
    ]
    return {"slug": dossier.name, "score": sum(p for p, _, ok, _ in regles if ok),
            "bloquants": [c for _, b, ok, c in regles if b and not ok],
            "conseils": sorted(((p, c) for p, b, ok, c in regles if not ok and not b), reverse=True),
            "manifeste": m, "fichiers": fichiers, "couverture": couv}


def fiche(m: dict, score: int, archive: str, sha: str) -> str:
    prix = "gratuit (0 CHF, prix libre possible)" if m["prix_chf"] == 0 else f"{m['prix_chf']:.2f} CHF"
    tags = ", ".join(m.get("mots_cles", [])) or "(aucun)"
    return f"""# {m['titre']} : fiche de publication {m['version']}

Score de préparation : {score}/100
Archive à téléverser : {archive}
SHA-256 : {sha}
Prix : {prix}
Licence : {m['licence']}
Mots-clés : {tags}

## Texte de vente (le même partout)
{m['description']}

## Où le coller
- Gumroad : nom, prix, description, fichier = l'archive, couverture = couverture.*
- itch.io : titre, prix, description, tags (10 au plus), fichier téléchargeable = l'archive, couverture 630 × 500
- TinyPages : produit numérique, nom, prix, description, fichier = l'archive

Ce moteur n'envoie rien : la mise en ligne se fait par vous, sur chaque plateforme.
"""


def preparer(dossier: Path, sortie: Path | None = None) -> Path:
    r = evaluer(dossier)
    if r["bloquants"]:
        raise RuntimeError(f"{r['slug']} : " + " ; ".join(r["bloquants"]))
    m = r["manifeste"]
    nom = f"{r['slug']}-{m['version']}"
    out = (sortie or SORTIE) / nom
    out.mkdir(parents=True, exist_ok=True)
    archive = out / f"{nom}.zip"
    with ZipFile(archive, "w", ZIP_DEFLATED) as z:
        for f in sorted(r["fichiers"]):
            info = ZipInfo(f.name, date_time=(1980, 1, 1, 0, 0, 0))   # date fixe : mêmes fichiers, même SHA-256
            info.compress_type, info.external_attr = ZIP_DEFLATED, 0o644 << 16
            z.writestr(info, f.read_bytes())
    if r["couverture"] and r["couverture"].is_file():
        shutil.copyfile(r["couverture"], out / f"couverture{r['couverture'].suffix.lower()}")
    sha = hashlib.sha256(archive.read_bytes()).hexdigest()
    (out / "SHA256SUMS").write_text(f"{sha}  {archive.name}\n", encoding="utf-8")
    (out / "fiche.md").write_text(fiche(m, r["score"], archive.name, sha), encoding="utf-8")
    return out


def main():
    ap = argparse.ArgumentParser(description="Moteur de publication CelestBIP : score, conseils, kit de distribution")
    ap.add_argument("commande", choices=("verifier", "preparer"))
    ap.add_argument("produits", nargs="*", help="dossiers de produits (par défaut : tous ceux de produits/)")
    a = ap.parse_args()
    dossiers = [Path(p) for p in a.produits] or sorted(p.parent for p in PRODUITS.glob("*/produit.json"))
    lignes, bloque = [], False
    for d in dossiers:
        r = evaluer(d)
        lignes.append(f"## {r['slug']} : {r['score']}/100")
        lignes += [f"- BLOQUANT : {c}" for c in r["bloquants"]]
        lignes += [f"- +{p} pts : {c}" for p, c in r["conseils"]]
        bloque |= bool(r["bloquants"])
        if a.commande == "preparer" and not r["bloquants"]:
            lignes.append(f"- kit prêt : {preparer(d).relative_to(ROOT)}")
    texte = "\n".join(lignes) or "Aucun produit : créez produits/<nom>/produit.json"
    print(texte)
    if os.environ.get("GITHUB_STEP_SUMMARY"):   # résumé visible sur GitHub à chaque modification
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write("# Publication\n\n" + texte + "\n")
    sys.exit(1 if bloque else 0)


if __name__ == "__main__":
    main()
