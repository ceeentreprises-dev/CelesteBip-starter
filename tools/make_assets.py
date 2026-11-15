#!/usr/bin/env python3
"""Génère les visuels statiques dans assets/ (à relancer seulement si la marque change).

Requiert : reportlab (PDF) et playwright avec Chromium (PNG).
    python tools/make_assets.py
"""
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import CELESTBIP_MASTER as cb  # noqa: E402

OUT = ROOT / "assets"

OG_HTML = f"""<!doctype html><html><head><meta charset="utf-8"><style>
body{{margin:0;width:1200px;height:630px;font-family:'DejaVu Sans',system-ui,sans-serif;color:#f6f9ff;overflow:hidden;position:relative;background:#061323}}
svg{{position:absolute;inset:0;width:100%;height:100%}}
.shade{{position:absolute;inset:0;background:linear-gradient(90deg,rgba(3,14,28,.96),rgba(3,14,28,.8) 45%,rgba(3,14,28,.1))}}
.c{{position:absolute;left:80px;top:90px;width:720px}}
.logo{{font-size:44px;font-weight:800;letter-spacing:-2px}} .logo span,.b{{color:#29b3f3}}
.eye{{margin-top:56px;font-size:20px;letter-spacing:5px;color:#b5ead6;text-transform:uppercase;font-weight:700}}
h1{{font-size:64px;line-height:1.08;letter-spacing:-2.5px;margin:18px 0 26px}}
p{{font-size:26px;color:#d9e7f2;margin:0}}
</style></head><body>{cb.HERO_SVG}<div class="shade"></div><div class="c">
<div class="logo">Celest<span>BIP</span></div><div class="eye">Humain × IA · Suisse romande</div>
<h1>L'humain d'abord.<br><span class="b">L'IA pour apprendre et créer.</span></h1>
<p>Séances, ateliers et guide gratuit pour utiliser l'IA avec méthode.</p></div></body></html>"""


def og_image():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None)
        page = b.new_page(viewport={"width": 1200, "height": 630})
        page.set_content(OG_HTML)
        page.screenshot(path=str(OUT / "og-image.png"))
        b.close()


def partner_pdf():
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    font, bold = "Helvetica", "Helvetica-Bold"
    d = "/usr/share/fonts/truetype/dejavu/"
    if Path(d + "DejaVuSans.ttf").exists():
        pdfmetrics.registerFont(TTFont("S", d + "DejaVuSans.ttf"))
        pdfmetrics.registerFont(TTFont("SB", d + "DejaVuSans-Bold.ttf"))
        font, bold = "S", "SB"
    navy, blue, ink = colors.HexColor("#0a2540"), colors.HexColor("#0675ab"), colors.HexColor("#21334b")
    n = ParagraphStyle("n", fontName=font, fontSize=9.6, leading=14, textColor=ink, spaceAfter=6)
    h = ParagraphStyle("h", parent=n, fontName=bold, fontSize=11.5, textColor=blue, spaceBefore=10, spaceAfter=4)
    t = ParagraphStyle("t", parent=n, fontName=bold, fontSize=24, leading=29, textColor=colors.white)
    sub = ParagraphStyle("s", parent=n, fontSize=11, textColor=colors.HexColor("#b5ead6"))
    cell = ParagraphStyle("c", parent=n, fontSize=9, leading=12.5, spaceAfter=0)
    cellb = ParagraphStyle("cb", parent=cell, fontName=bold, textColor=navy)

    def band(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(navy)
        canvas.rect(0, A4[1] - 128, A4[0], 128, fill=1, stroke=0)
        canvas.setFont(font, 7.5)
        canvas.setFillColor(colors.HexColor("#537184"))
        canvas.drawString(46, 30, f"CelestBIP · Dossier partenaires · {cb.SITE_URL}")
        canvas.restoreState()

    doc = SimpleDocTemplate(str(OUT / "dossier-partenaires.pdf"), pagesize=A4, leftMargin=46,
                            rightMargin=46, topMargin=34, bottomMargin=48,
                            title="CelestBIP - Dossier partenaires", author="CelestBIP")
    P = lambda s, st=n: Paragraph(s, st)  # noqa: E731
    levels = Table([
        [P("Niveau", cellb), P("Contribution", cellb), P("Contreparties", cellb)],
        [P("Soutien matériel", cellb), P("Lieu, équipement, impressions ou expertise", cell),
         P("Remerciement sur le site et lors de l'atelier", cell)],
        [P("Partenaire pilote", cellb), P("500 CHF : 1 atelier de 15 places offertes", cell),
         P("Logo sur la page de l'atelier, bilan chiffré", cell)],
        [P("Partenaire principal", cellb), P("1'500 CHF : cycle de 3 ateliers + guide gratuit", cell),
         P("Mention « avec le soutien de », intervention de 10 min, bilan d'impact", cell)],
    ], colWidths=[110, 180, 213])
    levels.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e6f3fa")),
        ("LINEBELOW", (0, 0), (-1, -1), .5, colors.HexColor("#bdd4e2")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story = [P("CelestBIP · Dossier partenaires", t),
             P("Financer une action précise pour rendre l'IA accessible", sub), Spacer(1, 40),
             P("Le projet", h),
             P("CelestBIP aide les particuliers, indépendants et petites structures de Suisse romande à utiliser "
               "l'intelligence artificielle de façon utile et prudente : séances individuelles, ateliers en petit "
               "groupe et guide gratuit. L'humain d'abord, l'IA comme outil."),
             P("L'action à financer", h),
             P("Des ateliers de 2 heures (max. 15 personnes) offerts à un public qui n'y aurait pas accès : "
               "aînés, demandeurs d'emploi, associations, petits commerces. Contenu : comprendre l'IA, l'essayer "
               "sur des cas concrets, vérifier les réponses, protéger ses données."),
             P("Niveaux de partenariat", h), levels,
             P("Budget type d'un atelier offert (500 CHF)", h),
             P("Préparation et animation 300 CHF · supports imprimés et guide 60 CHF · lieu ou outils en ligne "
               "80 CHF · bilan et suivi 60 CHF. Ajusté aux coûts réels, détaillé avant engagement."),
             P("Résultats mesurables", h),
             P("Nombre de participants, questionnaire avant/après (aisance, confiance), taux de satisfaction, "
               "contenus produits. Bilan écrit transmis dans les 30 jours."),
             P("Nos engagements et limites", h),
             P("Aucune promesse d'audience ou de ventes non vérifiée. Pas d'exclusivité ni de contrôle éditorial. "
               "Contribution encaissée uniquement après accord écrit. CelestBIP n'est ni une association reconnue "
               "d'utilité publique, ni une offre d'investissement."),
             P("Contact", h),
             P(f"Site : {cb.SITE_URL} · Profil : https://github.com/ceeentreprises-dev")]
    doc.build(story, onFirstPage=band, onLaterPages=band)


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#071321"/>
<circle cx="44" cy="22" r="9" fill="#ffce91"/><path d="M6 50L22 30l9 10 9-8 18 18z" fill="#29b3f3"/></svg>"""

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "favicon.svg").write_text(FAVICON, encoding="utf-8")
    og_image()
    partner_pdf()
    print(sorted(p.name for p in OUT.iterdir()))
