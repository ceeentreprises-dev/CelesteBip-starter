# CelestBIP Starter

> **L'humain d'abord. L'IA pour apprendre et créer.**
> Un générateur minimaliste : une page web et un guide PDF gratuit, en une commande.

[![Licence MIT](https://img.shields.io/badge/licence-MIT-blue.svg)](LICENSE)
![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Dépendances](https://img.shields.io/badge/d%C3%A9pendances-aucune%20obligatoire-brightgreen.svg)

## À quoi ça sert ?

Vous voulez présenter une idée ou un projet avec **une seule page propre** et **un PDF à offrir**, sans compte, sans hébergement payant, sans outil compliqué ? CelestBIP Starter génère les deux fichiers pour vous, sur votre ordinateur, en quelques secondes.

Le guide PDF inclus explique, en français simple, comment configurer un **assistant d'IA pédagogique** dans le service que vous utilisez déjà, comment vérifier ses réponses et comment protéger vos données.

## Démarrage rapide

```bash
git clone https://github.com/ceeentreprises-dev/CelesteBip-starter.git
cd CelesteBip-starter
python CELESTBIP_MASTER.py build      # crée le dossier dist/
python CELESTBIP_MASTER.py serve      # aperçu privé sur http://127.0.0.1:8787
```

| Commande | Effet |
|---|---|
| `build` | Génère `dist/` : `index.html`, `style.css`, `hero.svg`, le guide PDF, `robots.txt` |
| `test` | Lance 17 contrôles automatiques sur le résultat |
| `serve` | Aperçu local uniquement (127.0.0.1), jamais exposé sur Internet |
| `package` | Crée une archive ZIP de prévisualisation (après réussite des tests) |
| `status` | Affiche l'empreinte SHA-256 de chaque fichier généré |

Tests unitaires : `python -m unittest discover -s tests -v`

## Moteur de publication

`MOTEUR_PUBLICATION.py` pousse chaque produit vers la vente. Il donne un score de préparation sur 100, classe les améliorations par points gagnés, puis prépare un kit prêt à téléverser : une archive ZIP reproductible, son empreinte SHA-256, une fiche à copier pour Gumroad, itch.io et TinyPages, et la couverture.

```bash
python CELESTBIP_MASTER.py build                 # construit le guide (premier produit)
python MOTEUR_PUBLICATION.py verifier            # score et conseils de chaque produit
python MOTEUR_PUBLICATION.py preparer            # kits dans release/publication/
```

Un produit est un dossier `produits/<nom>/` avec un `produit.json` :

```json
{
  "titre": "Nom du produit (10 à 80 caractères)",
  "version": "1.0.0",
  "prix_chf": 0,
  "licence": "Ce que l'acheteur a le droit de faire",
  "description": "Au moins 300 caractères : à qui il sert, ce qu'il apporte.",
  "fichiers": ["mon-produit.pdf"],
  "couverture": "couverture.png",
  "mots_cles": ["trois", "à", "dix"]
}
```

Ce qui bloque la préparation : un fichier manquant ou hors du dépôt, un secret dans un fichier texte (IBAN suisse valide, clé privée, clé d'API, mot de passe), un titre, un prix, une licence ou une version absents. À chaque modification poussée sur GitHub, le flux `.github/workflows/publication.yml` relance les tests et le moteur, puis met les kits en téléchargement. Le moteur ne publie rien lui-même : la mise en vente reste votre décision.

**Licence du moteur : tous droits réservés.** Le moteur n'est pas sous licence MIT : sa copie, sa modification et sa réutilisation sont interdites sans autorisation écrite (voir [LICENCE-MOTEUR.md](LICENCE-MOTEUR.md)).

## Registre de risque

`registre_risques.py` est la partie saine du cadre ISO 31000, lancée à la main : identifier → analyser (proba × gravité, de 1 à 5) → évaluer → traiter (éviter / réduire / transférer / accepter), avec une action à 0 CHF par risque. **Pas d'autonomie** : aucun déclenchement automatique, aucun relais entre agents, aucun réseau. Vous le relancez quand une décision change.

```bash
python registre_risques.py        # trie les risques actifs, les urgents (< 30 j) d'abord
```

Les risques sont dans `registre_risques.json`. Règles : au plus 7 risques actifs (garde-fou anti-bureaucratie), chaque risque a un `traitement` et une `action_0chf`. Le registre est semé avec les risques de sécurité issus du cadre multi-agents lui-même (mail pris pour un ordre, agent qui agit seul, compte unique). Licence « tous droits réservés » (voir [LICENCE-MOTEUR.md](LICENCE-MOTEUR.md)).

## Ce qui est garanti

- **Aucun appel réseau.** Le script ne contacte aucun serveur.
- **Aucune collecte de données**, aucun cookie, aucune newsletter, aucun compte.
- **Aucun paiement** n'est affiché par défaut. Les coordonnées de soutien n'apparaissent que si un fichier local `support-approved.json` (jamais publié, voir `.gitignore`) contient trois validations explicites et un IBAN suisse à la somme de contrôle valide.
- **Page en `noindex`** : rien n'est indexé par les moteurs de recherche tant que vous ne l'avez pas décidé.
- **Aucune dépendance obligatoire.** Si `reportlab` est installé, le PDF est plus soigné ; sinon un PDF de secours est produit avec la bibliothèque standard Python.

## Ce que ce projet n'est pas

Pas une application, pas une « superintelligence », pas un service. C'est un outil simple et honnête, que vous pouvez lire en entier en dix minutes.

## Pour qui ?

- Les personnes qui découvrent l'IA et veulent un premier guide clair.
- Les indépendants et petits projets qui veulent une page de présentation sobre, sans dépenses.
- Les enseignants et formateurs qui cherchent un modèle de départ à adapter.

## Structure

```
CELESTBIP_MASTER.py      le générateur (un seul fichier)
tests/                   tests unitaires
docs/                    architecture et feuille de route
LICENSE                  MIT
```

## Contribuer

Les suggestions, corrections de texte et améliorations d'accessibilité sont les bienvenues. Voir [CONTRIBUTING.md](CONTRIBUTING.md) et la [feuille de route](docs/ROADMAP.md).

## Soutenir le projet

Le projet est libre et gratuit, et le restera. Si vous le trouvez utile, un soutien volontaire via **GitHub Sponsors** est possible dès que le profil est validé par GitHub. Il n'y a aucun avantage privé, aucun rendement et aucune promesse de résultat. Les contributions servent au temps de travail, à la maintenance et aux améliorations de la feuille de route.

## Licence

[MIT](LICENSE) : vous pouvez utiliser, copier, modifier et redistribuer ce code, y compris commercialement, en conservant la mention de licence. Fourni « tel quel », sans garantie.

**Exception :** le moteur de publication (`MOTEUR_PUBLICATION.py`, `tests/test_publication.py`, `.github/workflows/publication.yml`) n'est pas sous MIT. Il est sous licence « tous droits réservés » : voir [LICENCE-MOTEUR.md](LICENCE-MOTEUR.md).
