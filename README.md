# CelestBIP

> **L'humain d'abord. L'IA pour apprendre et créer.**
> Rendre l'IA accessible à toute personne, avec méthode et prudence — Suisse romande.

[![Site](https://img.shields.io/badge/site-en%20ligne-29b3f3.svg)](https://ceeentreprises-dev.github.io/CelesteBip-starter/)
[![Licence MIT](https://img.shields.io/badge/licence-MIT-blue.svg)](LICENSE)
![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Dépendances](https://img.shields.io/badge/d%C3%A9pendances-aucune%20obligatoire-brightgreen.svg)

**Site : https://ceeentreprises-dev.github.io/CelesteBip-starter/**

## Le projet

CelestBIP est une initiative indépendante, née en novembre 2026. Elle propose :
- un **guide PDF gratuit** pour démarrer avec un assistant IA ;
- des **articles** pratiques (vérifier une réponse, protéger ses données, bien formuler une demande…) ;
- des **séances et ateliers** à tarif pilote, et des ateliers offerts financés par des partenaires.

Le dépôt contient tout le site et son générateur : on peut le lire en entier, le copier et le réutiliser (licence MIT).

## Où nous en sommes (17 nov. 2026)

| | |
|---|---|
| Site en ligne, publication automatique | ✅ |
| Offres et paiements (Gumroad) | ✅ ouverts, 0 vente à ce jour |
| Articles publiés | 6 |
| Partenaires signés | 0 — plan prêt, voir [PARTENARIATS](docs/PARTENARIATS.md) |

Le détail daté est dans le [journal d'activité](docs/JOURNAL.md). Nous n'affichons que des faits vérifiables.

## Documentation

| Document | Contenu |
|---|---|
| [BUSINESS_PLAN](docs/BUSINESS_PLAN.md) | Offres, prix, validation, sponsoring |
| [PLAN_ACTION](docs/PLAN_ACTION.md) | Financement et calendrier sur 90 jours |
| [MARCHE](docs/MARCHE.md) | Analyse de marché, concurrence, alternatives |
| [PARTENARIATS](docs/PARTENARIATS.md) | Modèles de collaboration, cibles, messages |
| [KIT_DIFFUSION](docs/KIT_DIFFUSION.md) | Textes prêts à publier |
| [JOURNAL](docs/JOURNAL.md) | Historique d'activité |
| [DOSSIER_COMPLET](docs/DOSSIER_COMPLET.md) | Tout le projet de A à Z, procédures comprises |
| [AGENTS](AGENTS.md) | Instructions et tâches pour les agents de code (Codex, Claude Code) |
| [ARCHITECTURE](docs/ARCHITECTURE.md) | Fonctionnement du code |

## Développement

```bash
python CELESTBIP_MASTER.py build      # génère dist/
python CELESTBIP_MASTER.py test       # contrôles automatiques sur le résultat
python -m unittest discover -s tests  # tests unitaires
python CELESTBIP_MASTER.py serve      # aperçu local sur http://127.0.0.1:8787
```

Contenu éditorial : `articles/*.md` (un fichier = un article, ligne 1 `# Titre`, ligne 2 `date · résumé`) et `pages/*.md` (pages fixes). Un push publie le site automatiquement (GitHub Actions, après réussite des tests).

Visuels : `assets/` ; régénération avec `python tools/make_assets.py` (nécessite reportlab et Playwright).

## Principes

- **Aucun suivi** : pas de cookie, pas de statistiques, pas d'inscription.
- **Paiements via des prestataires tiers** (liens externes) : aucune donnée bancaire n'est traitée ici. Les liens autorisés sont limités par les contrôles du générateur.
- **Aucune promesse de résultat.** Pas une association d'utilité publique, pas une offre d'investissement.
- **Transparence** : code ouvert, journal daté, bilans publiés après chaque atelier.

## Contribuer et collaborer

Corrections de texte, accessibilité et idées sont les bienvenues : voir [CONTRIBUTING](CONTRIBUTING.md). Pour un partenariat : [ouvrir une proposition](https://github.com/ceeentreprises-dev/CelesteBip-starter/issues/new?template=partenariat.md).

## Soutenir

[GitHub Sponsors](https://github.com/sponsors/ceeentreprises-dev) ou les offres du site. Les contributions financent le temps de travail, la maintenance et des places d'atelier offertes. Aucun avantage privé, aucun rendement.

## Licence

[MIT](LICENSE) — fourni « tel quel », sans garantie.
