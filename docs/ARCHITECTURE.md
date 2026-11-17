# Architecture

Le générateur tient dans `CELESTBIP_MASTER.py`, sans dépendance obligatoire.

| Élément | Rôle |
|---|---|
| `CSS`, `HERO_SVG`, `HTML_TEMPLATE` | Page d'accueil, sans ressource externe |
| `OFFERS`, `DONATION_URL` | Offres et liens de paiement ; seuls les préfixes de `PAY_PREFIXES` deviennent des boutons |
| `articles/*.md`, `pages/*.md` | Contenu éditorial converti par `md_to_html` / `page_html` en pages HTML |
| `GUIDE_SECTIONS`, `make_pdf` | Guide PDF gratuit (reportlab si présent, sinon PDF de secours en bibliothèque standard) |
| `assets/` | Image de partage, favicon, dossier partenaires (générés par `tools/make_assets.py`) |
| `valid_swiss_iban`, `load_approved_support` | Affichage optionnel d'un IBAN, seulement avec trois validations locales dans `support-approved.json` (non versionné) |
| `build` / `checks` | Génère `dist/` puis vérifie : pages attendues, liens externes autorisés, offres rendues, liens de paiement présents, fichiers non vides |
| `package`, `serve`, `status` | Archive de prévisualisation, aperçu local (127.0.0.1), empreintes SHA-256 |

## Publication
`.github/workflows/pages.yml` : sur push, installe reportlab, lance les contrôles et les tests unitaires, construit `dist/` puis publie sur la branche `gh-pages` (GitHub Pages). `vercel.json` est conservé comme alternative.

## Choix de conception
- **Un fichier** lisible en entier.
- **Zéro réseau à la génération** : aucun appel sortant.
- **Liste blanche de liens** : un lien externe non prévu fait échouer les contrôles.
- **Refus par défaut** : l'IBAN n'est jamais affiché sans validations explicites.
