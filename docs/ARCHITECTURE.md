# Architecture

Tout tient dans `CELESTBIP_MASTER.py`.

| Bloc | Rôle |
|---|---|
| `CSS`, `HERO_SVG`, `HTML_TEMPLATE` | Contenu de la page unique, sans dépendance externe |
| `GUIDE_SECTIONS`, `STARTER_PROMPT` | Texte du guide PDF et instructions à copier dans un assistant IA |
| `make_pdf` | Génère le PDF avec `reportlab` si présent, sinon avec un générateur de secours (bibliothèque standard) |
| `valid_swiss_iban` | Contrôle de somme de contrôle uniquement (aucun accès bancaire) |
| `load_approved_support` | Active l'affichage d'un soutien seulement si trois validations explicites sont présentes dans `support-approved.json` |
| `build` / `checks` | Génère `dist/` puis vérifie 17 règles (une page, un PDF, pas de newsletter, pas de fournisseur de paiement, `noindex`, etc.) |
| `package` | Archive de prévisualisation, produite uniquement si les contrôles passent |
| `serve` | Aperçu local lié à 127.0.0.1 |

## Choix de conception

- **Un fichier** pour que n'importe qui puisse tout relire.
- **Zéro réseau** pour garantir la confidentialité.
- **Refus par défaut** : tant que les validations ne sont pas données, aucun paiement n'est affiché.
