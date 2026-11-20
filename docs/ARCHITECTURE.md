# Architecture

Le générateur tient dans `CELESTBIP_MASTER.py`, sans dépendance obligatoire.

| Élément | Rôle |
|---|---|
| `CSS`, `HERO_SVG`, `HTML_TEMPLATE` | Page d'accueil, sans ressource externe |
| `OFFERS`, `DONATION_URL` | Offres et liens de paiement ; seuls les préfixes de `PAY_PREFIXES` deviennent des boutons |
| `articles/*.md`, `pages/*.md` | Contenu éditorial converti par `md_to_html` / `page_html` en pages HTML |
| `GUIDE_SECTIONS`, `make_pdf` | Guide PDF gratuit (reportlab si présent, sinon PDF de secours en bibliothèque standard) |
| `assets/` | Image de partage, favicon, dossier partenaires (générés par `tools/make_assets.py`) |
| `carpe-rush/`, `GAME_FILES`, `export_game` | Jeu existant sous MIT, export limité aux huit fichiers runtime et à la licence ; progression locale sans service externe |
| `valid_swiss_iban`, `load_approved_support` | Affichage optionnel d'un IBAN, seulement avec trois validations locales dans `support-approved.json` (non versionné) |
| `build` / `checks` | Génère `dist/` puis vérifie : pages attendues, liens externes autorisés, offres rendues, liens de paiement présents, fichiers non vides |
| `package`, `serve`, `status` | Archive de prévisualisation, aperçu local (127.0.0.1), empreintes SHA-256 |

L'archive inclut les sous-dossiers publics. Le jeu est contrôlé par une liste explicite : les outils, captures, README et fichiers privés ne sont pas exportés. La page `merci.html` ne confirme aucun paiement ; elle invite à vérifier le reçu auprès du prestataire. Les liens de paiement présents dans un manifeste n'établissent pas une vente ni un versement.

## Contrôle facultatif du clavier du jeu

`python tests/browser_game_keyboard.py` sert la construction locale et vérifie les raccourcis dans les sous-vues et les commandes normales. Ajouter `--url https://ceeentreprises-dev.github.io/CelesteBip-starter/carpe-rush/` pour vérifier la version publiée. Ce contrôle utilise Playwright et Chromium lorsqu'ils sont installés ; il ne fait pas partie des dépendances obligatoires ni de la découverte des tests unitaires.

Le contrôle du 20 novembre a reproduit huit échecs avant correction, puis huit sous-vues préservées et deux parcours de lancement, reprise et pause réussis après correction. Un raccourci de démarrage n'est autorisé que si l'écran d'accueil ou de fin de partie est réellement visible, sans intercepter l'activation native des boutons.

## Publication
`.github/workflows/pages.yml` : sur push, installe reportlab, lance les contrôles et les tests unitaires, construit `dist/` puis publie sur la branche `gh-pages` (GitHub Pages). `vercel.json` est conservé comme alternative.

## Choix de conception
- **Un fichier** lisible en entier.
- **Zéro réseau à la génération** : aucun appel sortant.
- **Liste blanche de liens** : un lien externe non prévu fait échouer les contrôles.
- **Refus par défaut** : l'IBAN n'est jamais affiché sans validations explicites.
