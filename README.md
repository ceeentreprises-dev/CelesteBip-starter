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
- une activité **100 % numérique**, sans prestation du propriétaire humain ; les offres historiques de séance, d’atelier et d’intervention sur site sont des incompatibilités à traiter, pas des services à lui attribuer.
- un **jeu d'arcade gratuit**, [Carpe Rush](https://ceeentreprises-dev.github.io/CelesteBip-starter/carpe-rush/), avec progression sauvegardée dans le navigateur et monnaie virtuelle sans valeur réelle.

Le dépôt contient tout le site et son générateur : on peut le lire en entier, le copier et le réutiliser (licence MIT).

La [règle permanente d’exploitation du 21 novembre 2026](docs/REGLES_EXPLOITATION.md) s’applique à tous les agents : aucun appel, aucune visioconférence, animation, visite, prestation ou rédaction/envoi manuel d’e-mail du propriétaire. L’e-mail est le seul canal d’échange externe éventuel, traité par les agents et outils autorisés. Une dépendance non automatisable est un blocage.

## Où nous en sommes (consigne du 21, contrôle marchand du 20 novembre 2026)

| | |
|---|---|
| Site en ligne, publication automatique | ✅ |
| Catalogue Gumroad | Au 20 novembre : 4 produits publiés, compteurs à 0 vente ; offres de séance et d’atelier incompatibles avec la règle actuelle ; aucun produit modifié par cette consigne |
| Atelier PME | Carte historique à 900 CHF, sans lien de paiement ; intervention sur site incompatible à traiter |
| Articles publiés | 7 |
| Partenaires signés | 0 — anciens modèles d’animation archivés, voir [PARTENARIATS](docs/PARTENARIATS.md) |

Le détail daté est dans le [journal d'activité](docs/JOURNAL.md). Nous n'affichons que des faits vérifiables.

Une publication ou une page de retour ne prouve pas un encaissement. Une commande, un paiement, une livraison et un versement restent des états distincts. Aucune séance n’est confirmée par les supports préparés.

## Documentation

| Document | Contenu |
|---|---|
| [REGLES_EXPLOITATION](docs/REGLES_EXPLOITATION.md) | Consigne permanente 100 % numérique, rôles et incompatibilités |
| [BUSINESS_PLAN](docs/BUSINESS_PLAN.md) | Archive du modèle historique avec prestations humaines, supersédée |
| [PLAN_ACTION](docs/PLAN_ACTION.md) | Plan numérique actuel, preuves disponibles et blocages |
| [SEANCE_PILOTE](docs/SEANCE_PILOTE.md) | Archive pédagogique ; aucune séance à animer ou confirmée |
| [MARCHE](docs/MARCHE.md) | Analyse de marché, concurrence, alternatives |
| [PARTENARIATS](docs/PARTENARIATS.md) | Modèles historiques archivés, non prêts à envoyer |
| [KIT_DIFFUSION](docs/KIT_DIFFUSION.md) | Textes historiques archivés, non prêts à publier ou envoyer |
| [JOURNAL](docs/JOURNAL.md) | Historique d'activité |
| [DOSSIER_COMPLET](docs/DOSSIER_COMPLET.md) | Dossier historique, subordonné aux règles actuelles |
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
- **Transparence** : code ouvert, journal daté et faits vérifiables ; aucune prestation ni livraison supposée.

## Contribuer et collaborer

Corrections de texte, accessibilité et idées sont les bienvenues : voir [CONTRIBUTING](CONTRIBUTING.md). Les anciennes propositions de partenariat avec animation sont archivées ; tout échange commercial externe éventuel suit la règle de l’e-mail uniquement, sans travail manuel du propriétaire.

## Soutenir

Le soutien volontaire est présenté via [GitHub Sponsors](https://github.com/sponsors/ceeentreprises-dev) et le lien de soutien existant. Les offres historiques incompatibles ne doivent pas être promues. Le soutien volontaire ne promet aucune prestation humaine, aucun avantage privé ni rendement.

## Licence

[MIT](LICENSE) — fourni « tel quel », sans garantie.
