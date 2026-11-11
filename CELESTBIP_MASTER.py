#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CelestBIP - générateur autonome et prudent : 1 site, 1 PDF, 0 dépense.

USAGE:
    python CELESTBIP_MASTER.py build
    python CELESTBIP_MASTER.py test
    python CELESTBIP_MASTER.py serve --port 8787
    python CELESTBIP_MASTER.py package
    python CELESTBIP_MASTER.py status

AUCUN appel réseau, aucun paiement, aucune publication externe automatique.
Licence du code : MIT, sans garantie. Contenus éditoriaux : CelestBIP.
"""
from __future__ import annotations
import argparse
from html import escape
import hashlib
import json
from pathlib import Path
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import sys
import textwrap
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
RELEASE = ROOT / "release"
GUIDE = "installer-celestbip-soi-meme.pdf"
PUBLIC_FILES = ("index.html", "style.css", "hero.svg", GUIDE, "robots.txt")
CONFIG_FILE = ROOT / "support-approved.json"

BRAND = "CelestBIP"

CSS = r"""
:root {color-scheme:dark;--bg:#071321;--panel:#11263b;--line:#2b4a68;
--white:#f6f9ff;--muted:#c0d1e2;--blue:#29b3f3;--mint:#b5ead6;--gold:#ffce91;}
* {box-sizing:border-box} html {scroll-behavior:smooth}
body {margin:0;font:17px/1.6 system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
background:var(--bg);color:var(--white);}
a {color:inherit} a:focus-visible {outline:3px solid var(--gold);outline-offset:4px}
.skip {position:absolute;left:-9999px;top:1rem;z-index:99;background:#fff;color:#000;padding:.65rem}
.skip:focus {left:1rem}
.wrap {width:min(1120px,calc(100% - 44px));margin:0 auto}
header {position:absolute;inset:0 0 auto 0;z-index:10}
.nav {display:flex;align-items:center;justify-content:space-between;min-height:82px;gap:1rem}
.logo {font-weight:800;text-decoration:none;font-size:1.65rem;letter-spacing:-.06em}
.logo span,.shine {color:var(--blue)} .nav small {font-size:.73rem;letter-spacing:.19em;color:#c1d2e3}
nav a {text-decoration:none;padding:.5rem .75rem;font-size:.91rem;color:var(--muted)}
nav a:hover {color:white}
.hero {position:relative;min-height:720px;display:flex;align-items:center;
background:radial-gradient(circle at 76% 25%,#285279 0,transparent 42%),#061323;overflow:hidden}
.hero-art {position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:.91}
.hero::after {content:'';position:absolute;inset:0;
background:linear-gradient(90deg,rgba(3,14,28,.96),rgba(3,14,28,.88) 32%,rgba(3,14,28,.20) 80%),
linear-gradient(0deg,#071321,transparent 32%);pointer-events:none}
.hero-content {position:relative;z-index:1;padding:150px 0 110px;max-width:1120px}
.eyebrow {font-weight:700;font-size:.77rem;color:var(--mint);letter-spacing:.23em;text-transform:uppercase}
h1 {font-size:clamp(2.5rem,5.8vw,5.5rem);line-height:1.09;letter-spacing:-.06em;
max-width:750px;margin:.45em 0 .35em} .lead {font-size:clamp(1.08rem,2vw,1.34rem);max-width:610px;color:#d9e7f2}
.actions {display:flex;gap:.8rem;flex-wrap:wrap;margin-top:1.8rem}
.button {display:inline-flex;align-items:center;justify-content:center;padding:.85rem 1.4rem;
background:var(--blue);color:#07172a;border:1px solid var(--blue);border-radius:60px;
font-weight:750;text-decoration:none;min-height:50px}
.button.secondary {background:#0d2339c7;color:#f1f9ff;border-color:#78b5d0}
.button:hover {filter:brightness(1.1)}
section {padding:72px 0} h2 {font-size:clamp(1.65rem,3vw,2.35rem);line-height:1.2;letter-spacing:-.035em;margin:.1em 0 .65em}
.section-intro {color:var(--muted);max-width:780px}
.grid {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;margin-top:28px}
.card {border:1px solid var(--line);background:linear-gradient(160deg,#132e46,#0a1a2d);
border-radius:20px;padding:27px;min-height:190px}
.num {display:inline-block;border:1px solid #5b849d;border-radius:999px;color:var(--mint);padding:.2em .7em;font-size:.72rem;letter-spacing:.1em}
h3 {font-size:1.25rem;margin:.8em 0 .4em} .card p {color:var(--muted);margin:0}
.banded {background:#0b1d30}
.two {display:grid;grid-template-columns:1.2fr .8fr;gap:46px;align-items:center}
.note {border-left:3px solid var(--blue);padding:1rem 1.2rem;background:#122c42;border-radius:0 12px 12px 0;color:#d7eaf5}
.muted {color:var(--muted)} .muted a {text-underline-offset:.15em}
.support {border:1px solid #365775;background:linear-gradient(125deg,#122f49,#0b2135);
border-radius:24px;padding:36px}
.support p {max-width:780px;color:#d4e3ed}
.disclosure {font-size:.87rem;color:#b2c9db}
footer {border-top:1px solid var(--line);padding:31px 0 44px;color:#a7bfd0;font-size:.86rem}
footer .foot {display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap}
@media(max-width:740px){.hero{min-height:670px}.hero-content{padding-top:125px}
.hero::after{background:linear-gradient(90deg,rgba(3,14,28,.95),rgba(3,14,28,.72)),
linear-gradient(0deg,#071321,transparent 40%)}.grid,.two{grid-template-columns:1fr}
nav a{padding:.25rem}.support{padding:24px}section{padding:48px 0}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
"""

HERO_SVG = r'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
<defs><linearGradient id="s" x1="0" x2="0" y1="0" y2="1"><stop stop-color="#08152b"/><stop offset=".58" stop-color="#235078"/><stop offset="1" stop-color="#e3a17d"/></linearGradient>
<linearGradient id="lake" x1="0" x2="0" y1="0" y2="1"><stop stop-color="#47708e"/><stop offset="1" stop-color="#081b32"/></linearGradient>
<radialGradient id="sun"><stop stop-color="#ffe2ad" stop-opacity=".9"/><stop offset=".25" stop-color="#ffb57c" stop-opacity=".65"/><stop offset="1" stop-color="#d48b8b" stop-opacity="0"/></radialGradient></defs>
<rect width="1600" height="900" fill="url(#s)"/><circle cx="1210" cy="370" r="350" fill="url(#sun)"/>
<g fill="#eff8ff" opacity=".7"><circle cx="100" cy="90" r="2"/><circle cx="340" cy="43" r="1.4"/><circle cx="630" cy="76" r="1.4"/><circle cx="880" cy="48" r="1.9"/><circle cx="1280" cy="140" r="1.2"/><circle cx="1450" cy="40" r="1.5"/><circle cx="1130" cy="80" r="1"/></g>
<path d="M0 470L190 355 320 438 495 262 700 481 879 326 1021 459 1204 280 1400 440 1520 305 1600 355V900H0Z" fill="#304960"/>
<path d="M385 350L495 262 570 350 516 334 494 300 458 350Z M1130 350L1204 280 1265 355 1213 334 1204 319 1172 354Z" fill="#c7dce7" opacity=".9"/>
<path d="M0 590L170 540 330 575 580 510 810 597 1060 512 1300 590 1470 507 1600 535V900H0Z" fill="#112e49"/>
<path d="M0 625Q370 590 700 630T1600 614V900H0Z" fill="url(#lake)"/>
<g stroke="#ffd599" stroke-width="2" opacity=".46"><path d="M1000 680l500 30M1010 720l580 34M995 778l605 13M960 827l450 6"/></g>
<path d="M0 760Q250 680 510 740T1600 708V900H0Z" fill="#07182d"/>
</svg>'''

HTML_TEMPLATE = '''<!doctype html>
<html lang="fr-CH"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="CelestBIP : une initiative indépendante pour comprendre l'intelligence artificielle, partager des connaissances et favoriser les projets utiles.">
<meta name="robots" content="noindex,nofollow"><meta name="referrer" content="strict-origin-when-cross-origin">
<title>CelestBIP | Humain × IA</title>
<link rel="stylesheet" href="style.css"></head>
<body><a class="skip" href="#contenu">Aller au contenu</a>
<header><div class="wrap nav"><a href="#accueil" class="logo" aria-label="CelestBIP accueil">Celest<span>BIP</span></a>
<nav aria-label="Navigation principale"><a href="#projet">Le projet</a><a href="#guide">PDF gratuit</a><a href="#soutenir">Soutenir</a></nav></div></header>
<main id="contenu"><section id="accueil" class="hero"><img class="hero-art" src="hero.svg" alt="" aria-hidden="true">
<div class="wrap hero-content"><p class="eyebrow">Projet indépendant · Humain × IA</p>
<h1>L'humain d'abord.<br><span class="shine">L'IA pour apprendre et créer.</span></h1>
<p class="lead">CelestBIP explore une idée simple : rendre les connaissances et les possibilités de l'IA plus faciles à comprendre, à essayer et à partager.</p>
<div class="actions"><a class="button" href="#projet">Découvrir le projet</a><a class="button secondary" href="installer-celestbip-soi-meme.pdf" download>Télécharger le guide PDF</a></div></div></section>
<section id="projet"><div class="wrap"><p class="eyebrow">Une initiative en préparation</p><h2>Des idées d'aujourd'hui pour un demain plus humain.</h2>
<p class="section-intro">Nous voulons expérimenter à petite échelle, expliquer les choses simplement et partager ce qui fonctionne. Aucune promesse de révolution : avancer, apprendre et montrer les résultats.</p>
<div class="grid"><article class="card"><span class="num">01</span><h3>Comprendre</h3><p>Découvrir ce que l'intelligence artificielle peut faire, et connaître ses limites.</p></article>
<article class="card"><span class="num">02</span><h3>Essayer</h3><p>Apprendre avec de petits exemples accessibles, sans compétence technique obligatoire.</p></article>
<article class="card"><span class="num">03</span><h3>Partager</h3><p>Mettre des connaissances utiles à disposition du plus grand nombre, gratuitement.</p></article></div></div></section>
<section id="guide" class="banded"><div class="wrap two"><div><p class="eyebrow">Commencer librement</p><h2>Un PDF pour essayer CelestBIP soi-même</h2>
<p>Le guide propose une méthode simple pour configurer un assistant pédagogique inspiré de CelestBIP dans un service d'IA de votre choix.</p>
<p class="muted">Il ne prétend pas installer une superintelligence ni fournir une application propriétaire. Il explique comment commencer, vérifier les réponses et protéger ses données.</p>
<a class="button" href="installer-celestbip-soi-meme.pdf" download>Télécharger gratuitement le PDF</a></div>
<aside class="note">Libre d'accès. Sans inscription. Sans abonnement obligatoire. Le guide et cette page restent disponibles à tout moment, tant que le site est hébergé.</aside></div></section>
<section id="soutenir"><div class="wrap"><div class="support"><p class="eyebrow">Soutien volontaire</p><h2>Un soutien libre, pour une idée utile à tous.</h2>
<p>Si CelestBIP vous parle, vous pourrez soutenir sa construction. Le projet vise une utilité collective, sans avantage privé réservé aux contributeurs. Il n'est ni une association reconnue d'utilité publique, ni une offre d'investissement.</p>
{{SUPPORT_BLOCK}}
<p class="disclosure">Les fonds éventuels serviront à la préparation, au travail humain nécessaire, au fonctionnement et aux développements du projet. Un budget détaillé sera présenté avant toute collecte. Aucun résultat ni remboursement n'est promis.</p>
</div></div></section></main>
<footer><div class="wrap foot"><div><strong>CelestBIP</strong> · Idées · Outils · Avenir</div><div>Projet indépendant en préparation · Aucune collecte activée sur cette page à ce jour.</div></div></footer>
</body></html>'''

GUIDE_SECTIONS = [
    ("INTRODUCTION", [
        "CelestBIP est une démarche humaine d'exploration, d'apprentissage et de partage autour de l'intelligence artificielle.",
        "Ce guide gratuit explique comment créer une configuration personnelle inspirée de CelestBIP dans un assistant IA existant. Il ne télécharge pas une application et n'installe aucune superintelligence.",
    ]),
    ("1. CHOISIR UN SERVICE D'IA", [
        "Choisissez un service d'IA que vous utilisez déjà, sur ordinateur ou téléphone. Les fonctionnalités, coûts éventuels et paramètres de confidentialité dépendent du fournisseur.",
        "Vous pouvez commencer dans une nouvelle conversation, sans installer de programme supplémentaire.",
    ]),
    ("2. COLLER CES INSTRUCTIONS", [
        "Copiez le texte de la page suivante dans les instructions personnalisées, si votre service le permet, ou dans le premier message d'une conversation.",
    ]),
    ("3. FAIRE UN PREMIER ESSAI", [
        "Exemple : Explique-moi ce qu'est une IA générative en cinq phrases, puis donne-moi un exemple simple et une limite importante.",
        "Autre exemple : Aide-moi à apprendre un nouveau sujet en proposant trois questions progressives.",
    ]),
    ("4. GARDER LE CONTRÔLE", [
        "Ne partagez pas de mots de passe, clés API, données bancaires ou renseignements confidentiels. Vérifiez les informations importantes auprès de sources fiables.",
        "L'assistant peut se tromper. Il ne prend aucune décision juridique, médicale ou financière à votre place.",
    ]),
    ("5. LIBERTÉ ET SOUTIEN", [
        "Vous pouvez utiliser cette démarche sans payer CelestBIP, sans compte CelestBIP et sans laisser votre adresse e-mail.",
        "Un éventuel soutien à CelestBIP est entièrement volontaire, sans contrepartie ni rendement.",
    ]),
]
STARTER_PROMPT = """Tu es mon compagnon pédagogique inspiré de CelestBIP.
Ta mission est de m'aider à comprendre, tester et partager des connaissances utiles autour de l'intelligence artificielle.
Commence par me demander ce que j'aimerais apprendre.
Explique simplement, sans jargon inutile, avec des exemples concrets et des étapes courtes.
Sépare les faits vérifiables, les hypothèses et les incertitudes.
Signale tes limites. Ne prétends jamais avoir effectué une action que tu n'as pas réalisée.
Ne me demande pas de secrets, d'identifiants bancaires ou de données privées.
Lorsque le sujet est important, propose une méthode pour contrôler les informations.
Privilégie les outils gratuits et n'engage aucune dépense ou action externe sans mon accord.
Rappelle-moi que je garde toujours le contrôle de mes décisions."""


def _pdf_with_reportlab(destination: Path) -> None:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    font = "Helvetica"
    for guess in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                  "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"):
        if Path(guess).exists():
            pdfmetrics.registerFont(TTFont("GuideSans", guess))
            font = "GuideSans"
            break
    normal = ParagraphStyle("normal", fontName=font, fontSize=10.6, leading=16.8,
                            textColor=colors.HexColor("#21334b"), spaceAfter=12)
    title = ParagraphStyle("title", parent=normal, fontSize=22, leading=29,
                           textColor=colors.HexColor("#0a365c"), spaceAfter=17)
    h = ParagraphStyle("h", parent=normal, fontSize=13, leading=18,
                       textColor=colors.HexColor("#0675ab"), spaceBefore=15, spaceAfter=7)
    tag = ParagraphStyle("tag", parent=normal, fontSize=9,
                         textColor=colors.HexColor("#557187"), spaceAfter=14)
    mono = ParagraphStyle("mono", parent=normal, fontSize=9.1, leading=14, spaceAfter=8)

    def foot(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#bdd4e2"))
        canvas.line(46, 47, 549, 47)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#537184"))
        canvas.drawString(46, 34, "CelestBIP - Guide gratuit - Edition de travail")
        canvas.drawRightString(549, 34, f"Page {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(str(destination), pagesize=A4, leftMargin=47, rightMargin=47,
                            topMargin=55, bottomMargin=62,
                            title="Installer CelestBIP soi-même - guide gratuit",
                            author="CelestBIP (projet en préparation)")
    story = [Paragraph("CELESTBIP", title),
             Paragraph("Comment démarrer soi-même - Guide gratuit", h),
             Paragraph("Une approche simple, indépendante et volontaire de la découverte de l'IA.", tag)]
    for head, paras in GUIDE_SECTIONS[:3]:
        story.append(Paragraph(escape(head), h))
        for t in paras:
            story.append(Paragraph(escape(t), normal))
    story.append(PageBreak())
    story.append(Paragraph("LES INSTRUCTIONS À COPIER", title))
    story.append(Paragraph("Copiez ce texte dans votre assistant IA, puis commencez votre conversation.", normal))
    for ln in STARTER_PROMPT.splitlines():
        story.append(Paragraph(escape(ln), mono))
    story.append(PageBreak())
    story.append(Paragraph("PREMIERS ESSAIS ET PRÉCAUTIONS", title))
    for head, paras in GUIDE_SECTIONS[3:]:
        story.append(Paragraph(escape(head), h))
        for t in paras:
            story.append(Paragraph(escape(t), normal))
    story.append(Spacer(1, 19))
    story.append(Paragraph("Pas d'inscription CelestBIP. Pas de paiement obligatoire. Pas de collecte active dans ce guide.", tag))
    doc.build(story, onFirstPage=foot, onLaterPages=foot)


def _pdf_without_dependency(destination: Path) -> None:
    """Fallback PDF 3 pages, bibliothèque standard, Helvetica/WinAnsi; texte sélectionnable."""
    page1 = ["CelestBIP - Comment demarrer soi-meme", "Guide gratuit - Version de travail", "",
             "CelestBIP propose une methode simple pour explorer l'IA.",
             "Ce guide configure un assistant existant, pas une superintelligence.", "",
             "1. Choisissez un service d'IA que vous connaissez.",
             "2. Ouvrez une nouvelle conversation.",
             "3. Copiez le texte propose sur la page suivante.",
             "4. Testez-le avec une question simple.", "",
             "Utilisez des outils gratuits lorsque c'est possible.",
             "Ne confiez aucun secret ni aucune donnee personnelle sensible."]
    page2 = ["INSTRUCTIONS A COPIER DANS VOTRE ASSISTANT IA", ""]
    for ln in STARTER_PROMPT.splitlines():
        page2.extend(textwrap.wrap(ln, width=81, break_long_words=False) or [""])
    page3 = ["PREMIERS ESSAIS", "",
             "Demandez : Explique-moi une IA generative en cinq phrases.",
             "Demandez : Guide-moi pour apprendre un nouveau sujet.", "",
             "Gardez un esprit critique. Verifiez les informations importantes.",
             "L'assistant peut se tromper et ne remplace pas un professionnel.", "",
             "CelestBIP est un projet independant en preparation.",
             "Acces libre, aucun compte CelestBIP requis, aucun don obligatoire."]
    pages = [page1, page2, page3]
    objs = []

    def add(b):
        objs.append(b)
        return len(objs)

    font_id = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    refs = []
    for lines in pages:
        ops = ["BT /F1 12 Tf 45 795 Td 18 TL"]
        for i, line in enumerate(lines):
            safe = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            ops.append(("" if i == 0 else "T* ") + f"({safe}) Tj")
        ops.append("ET")
        stream = "\n".join(ops).encode("cp1252", errors="replace")
        content_id = add(f"<< /Length {len(stream)} >>\nstream\n".encode() + stream + b"\nendstream")
        page_id = add(f"<< /Type /Page /Parent __PARENT__ /MediaBox [0 0 595 842] /Resources << /Font << /F1 {font_id} 0 R >> >> /Contents {content_id} 0 R >>".encode())
        refs.append(page_id)
    pages_id = add(f"<< /Type /Pages /Count {len(refs)} /Kids [{' '.join(str(r) + ' 0 R' for r in refs)}] >>".encode())
    for r in refs:
        objs[r - 1] = objs[r - 1].replace(b"__PARENT__", f"{pages_id} 0 R".encode())
    catalog_id = add(f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode())
    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offs = [0]
    for i, obj in enumerate(objs, 1):
        offs.append(len(out))
        out += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"
    pos = len(out)
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode()
    for off in offs[1:]:
        out += f"{off:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {len(objs) + 1} /Root {catalog_id} 0 R >>\nstartxref\n{pos}\n%%EOF".encode()
    destination.write_bytes(out)


def make_pdf(destination: Path) -> str:
    try:
        _pdf_with_reportlab(destination)
        return "reportlab"
    except ImportError:
        _pdf_without_dependency(destination)
        return "standard-library"


def valid_swiss_iban(value: str) -> bool:
    """IBAN suisse : contrôle de somme uniquement, jamais d'accès ni de virement bancaire."""
    iban = re.sub(r"\s+", "", value).upper()
    if len(iban) != 21 or not re.fullmatch(r"CH[0-9]{7}[A-Z0-9]{12}", iban):
        return False
    chars = iban[4:] + iban[:4]
    expanded = "".join(c if c.isdigit() else str(ord(c) - 55) for c in chars)
    return int(expanded) % 97 == 1


def load_approved_support():
    """N'active le soutien que si 3 validations explicites sont dans un fichier local."""
    if not CONFIG_FILE.exists():
        return None
    c = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    required = ("bank_owner_confirmed", "legal_checks_confirmed", "explicit_publish_approval")
    if any(c.get(key) is not True for key in required):
        return None
    if not valid_swiss_iban(c.get("iban", "")):
        raise ValueError("IBAN suisse invalide dans support-approved.json")
    beneficiary = c.get("beneficiary", "").strip()
    if not beneficiary or len(beneficiary) > 100:
        raise ValueError("Bénéficiaire absent/invalide")
    return {"iban": re.sub(r"\s+", "", c["iban"]).upper(), "beneficiary": beneficiary}


def support_html(bank) -> str:
    if bank is None:
        return ('<div class="note"><strong>Contributions non ouvertes pour le moment.</strong> '
                'Les informations bancaires et le cadre légal seront vérifiés avant d\'activer un '
                'éventuel soutien. Aucun paiement n\'est demandé aujourd\'hui.</div>')
    iban = escape(bank['iban'])
    beneficiary = escape(bank['beneficiary'])
    return (f'<div class="note"><strong>Virement bancaire volontaire (Suisse)</strong>'
            f'<p>IBAN : <code>{iban}</code><br>Bénéficiaire : {beneficiary}</p>'
            '<p>Un ordre permanent peut être configuré et arrêté par le contributeur auprès de sa banque. '
            'Aucun rendement, part ni avantage en échange.</p></div>')


def build() -> dict:
    DIST.mkdir(exist_ok=True)
    support = load_approved_support()
    html = HTML_TEMPLATE.replace("{{SUPPORT_BLOCK}}", support_html(support))
    if support:
        html = html.replace("Aucune collecte activée sur cette page à ce jour.",
                            "Coordonnées de soutien volontaire affichées après validation.")
    (DIST / "index.html").write_text(html, encoding="utf-8")
    (DIST / "style.css").write_text(CSS, encoding="utf-8")
    (DIST / "hero.svg").write_text(HERO_SVG, encoding="utf-8")
    (DIST / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    pdf_engine = make_pdf(DIST / GUIDE)
    summary = {"brand": BRAND, "pages_web": 1, "pdf": GUIDE, "payments_active": bool(support),
               "public_release_approved": False, "pdf_engine": pdf_engine,
               "files": {f: hashlib.sha256((DIST / f).read_bytes()).hexdigest() for f in PUBLIC_FILES}}
    (DIST / "build-manifest.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def checks() -> list:
    failures = []

    def check(ok: bool, name: str):
        if not ok:
            failures.append(name)

    if not all((DIST / f).exists() for f in PUBLIC_FILES):
        build()
    site = (DIST / "index.html").read_text(encoding="utf-8")
    check(site.lower().count("<!doctype html>") == 1, "one_html_document")
    check(len(list(DIST.glob("*.html"))) == 1, "single_web_page")
    check(f'href="{GUIDE}"' in site, "pdf_download_link")
    check((DIST / GUIDE).read_bytes().startswith(b"%PDF-"), "real_pdf_file")
    check("noindex,nofollow" in site, "no_public_indexation_without_approval")
    check('lang="fr-CH"' in site, "french_locale")
    check('href="#projet"' in site and 'href="#soutenir"' in site, "internal_navigation")
    check("newsletter" not in site.lower(), "no_newsletter")
    check("s'abonner" not in site.lower(), "no_forced_subscription")
    check("paypal" not in site.lower() and "stripe" not in site.lower(), "no_payment_provider")
    check("fondation reconnue" not in site.lower() and "présidente" not in site.lower(), "no_false_status")
    check("Aucun paiement" in site or "IBAN" in site, "support_is_clear")
    robots = (DIST / "robots.txt").read_text()
    check("noindex" in robots.lower() or "Disallow" in robots, "robots_gated")
    for f in PUBLIC_FILES:
        check((DIST / f).stat().st_size > (10 if f == "robots.txt" else 80), f"nonempty_{f}")
    return failures


def package() -> Path:
    build()
    issues = checks()
    if issues:
        raise RuntimeError("Tests échoués: " + ", ".join(issues))
    RELEASE.mkdir(exist_ok=True)
    path = RELEASE / "CELESTBIP_SITE_PREVIEW_NON_PUBLIE.zip"
    with ZipFile(path, "w", ZIP_DEFLATED) as z:
        for name in PUBLIC_FILES:
            z.write(DIST / name, name)
        z.write(DIST / "build-manifest.json", "build-manifest.json")
    return path


def serve(port: int):
    build()
    import os
    os.chdir(DIST)
    with ThreadingHTTPServer(("127.0.0.1", port), SimpleHTTPRequestHandler) as server:
        print(f"Prévisualisation privée : http://127.0.0.1:{port}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


def main():
    parser = argparse.ArgumentParser(description="CelestBIP Master : une page, un PDF, aucun service payant")
    parser.add_argument("command", choices=("build", "test", "serve", "package", "status"),
                        nargs="?", default="build")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()
    if args.command == "serve":
        serve(args.port)
        return
    if args.command == "build":
        result = build()
    elif args.command == "test":
        build()
        issues = checks()
        print("TESTS :", "OK" if not issues else "ÉCHEC - " + ", ".join(issues))
        sys.exit(1 if issues else 0)
    elif args.command == "package":
        result = {"archive": str(package())}
    else:
        if not (DIST / "build-manifest.json").exists():
            build()
        result = json.loads((DIST / "build-manifest.json").read_text(encoding="utf-8"))
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
