# AGENTS.md — instructions pour les agents de code (Codex, Claude Code, etc.)

Ce fichier est lu automatiquement par les agents de code. Il décrit le projet, les règles à ne jamais enfreindre, les commandes et la liste des tâches prêtes à exécuter. Le dossier complet du projet, de A à Z, est dans [`docs/DOSSIER_COMPLET.md`](docs/DOSSIER_COMPLET.md).

## 1. Le projet en 5 lignes

- **CelestBIP** : initiative indépendante (Suisse romande, depuis novembre 2026) pour rendre l'IA accessible à toute personne, avec méthode et prudence.
- **Site statique** généré par un seul script Python (`CELESTBIP_MASTER.py`), publié sur GitHub Pages : https://ceeentreprises-dev.github.io/CelesteBip-starter/
- **Revenus** : séances (150 CHF), ateliers (20 CHF/place), adhésion (10 CHF/mois), soutien libre ; paiements via liens Gumroad. Sponsoring d'ateliers offerts.
- **Langue** : tout le contenu public est en **français (fr-CH)**, ton clair, sobre, sans jargon.
- **État au 17 nov. 2026** : site et paiements en ligne, 6 articles, 0 vente, 0 partenaire signé.

## 2. Règles absolues (ne jamais enfreindre)

1. **Identité privée.** Aucun nom de personne, adresse, téléphone, e-mail personnel ou IBAN dans le dépôt ou sur le site. Seule identité publique : le profil GitHub `ceeentreprises-dev`. Le fichier `support-approved.json` (IBAN) est ignoré par git et ne doit jamais être versionné.
2. **Aucun fait inventé.** Pas de faux témoignages, faux clients, faux chiffres, faux partenaires, faux labels. Le journal (`docs/JOURNAL.md`) ne contient que des faits vérifiables.
3. **Aucune promesse** de résultat financier, professionnel, juridique ou médical. CelestBIP n'est ni une association reconnue d'utilité publique, ni une offre d'investissement.
4. **Aucun suivi** : pas de cookie, pas de script d'analyse, pas de ressource externe (polices, CDN) sur le site. La CSP de `vercel.json` et les contrôles doivent rester verts.
5. **Liens externes en liste blanche** : seuls les préfixes de `ALLOWED_LINK_PREFIXES` (paiement + GitHub du projet) et `SITE_URL` sont autorisés. Ajouter un nouveau domaine = modifier la liste ET justifier dans le commit.
6. **Aucune dépendance obligatoire** pour `build`/`test` : bibliothèque standard uniquement (reportlab est optionnel).
7. **Ne pas casser la publication** : tout push sur `main` ou sur la branche de travail déclenche `.github/workflows/pages.yml`, qui publie si les tests passent.

## 3. Commandes

```bash
python CELESTBIP_MASTER.py build        # génère dist/
python CELESTBIP_MASTER.py test         # contrôles sur dist/ (doit afficher "TESTS : OK")
python -m unittest discover -s tests -v # tests unitaires
python CELESTBIP_MASTER.py serve        # aperçu http://127.0.0.1:8787
python tools/make_assets.py             # régénère assets/ (reportlab + playwright requis)
```

**Définition de « terminé »** : `python CELESTBIP_MASTER.py test` affiche `TESTS : OK` **et** `python -m unittest discover -s tests` affiche `OK`.

## 4. Carte du code

| Emplacement | Rôle |
|---|---|
| `CELESTBIP_MASTER.py` | Générateur unique : constantes (offres, liens, URL), CSS, HTML, PDF, build, contrôles |
| `OFFERS` | Liste des offres `(titre, prix affiché, description, URL de paiement)` ; URL vide = « bientôt disponible » |
| `DONATION_URL`, `SPONSORS_URL` | Boutons de soutien |
| `articles/NN-slug.md` | Un article = un fichier. Ligne 1 `# Titre`, ligne 2 `AAAA-MM-JJ · résumé`, puis `## sous-titres`, paragraphes, listes `- ` |
| `pages/*.md` | Pages fixes (même format), ex. `a-propos.md` → `a-propos.html` |
| `assets/` | `og-image.png`, `favicon.svg`, `dossier-partenaires.pdf` (copiés tels quels) |
| `tools/make_assets.py` | Génère les visuels |
| `tests/test_celestbip.py` | Tests unitaires |
| `docs/` | Dossier d'entreprise (voir `DOSSIER_COMPLET.md`) |

Le convertisseur Markdown est volontairement minimal (`md_to_html`) : titres de niveau 1 et 2, listes, paragraphes et liens `[texte](url)` relatifs ou autorisés par la liste blanche. Pas de gras ni de titres de niveau 3. Ne pas utiliser d'autres syntaxes dans `articles/` et `pages/`, ou étendre `md_to_html` avec un test. Un lien refusé reste du texte échappé.

## 5. Conventions

- Commits en français, à l'impératif ou descriptifs, un sujet par commit.
- Toute logique nouvelle (branche, boucle, parseur, lien de paiement) reçoit un test dans `tests/`.
- Pas d'abstraction ni d'option « pour plus tard ». Garder un seul fichier générateur tant qu'il reste lisible.
- Accessibilité : contrastes suffisants, `alt` sur les images porteuses de sens, navigation clavier, `lang="fr-CH"`.
- Après chaque changement visible (nouvelle offre, nouvel article, partenaire signé), ajouter une ligne datée à `docs/JOURNAL.md` et mettre à jour `CHANGELOG.md` (section « Non publié »).

## 6. Tâches prêtes à exécuter (par priorité)

Chaque tâche liste ses critères d'acceptation. Les tâches marquées **[HUMAIN]** demandent une action du propriétaire et ne doivent pas être simulées.

### T1 — Offre « Atelier PME » (900 CHF)
- Ajouter une 4ᵉ entrée à `OFFERS` : « Atelier PME sur site (3 h, jusqu'à 12 personnes) », « 900 CHF », description factuelle, URL vide (« bientôt disponible ») tant que le lien de paiement n'existe pas.
- Adapter le contrôle `cards_rendered` (nombre de cartes) et le test associé.
- Critères : `TESTS : OK`, la carte s'affiche, aucun lien de paiement inventé.

### T2 — Page « Partenaires » publique
- Créer `pages/partenaires.md` à partir de `docs/PARTENARIATS.md` : mission, 3 modèles de collaboration, ce que CelestBIP apporte, comment proposer un partenariat (lien vers le modèle d'issue `partenariat.md`… via la page d'accueil, car `md_to_html` ne gère pas les liens).
- Ajouter le lien dans la navigation.
- Critères : page générée, présente dans `sitemap.xml`, contrôles verts, aucun partenaire présenté comme signé.

### T3 — Liens dans le Markdown
- Étendre `md_to_html` pour la syntaxe `[texte](url)` en n'acceptant que les URL relatives ou celles de `ALLOWED_LINK_PREFIXES` ; échapper tout le reste.
- Tests : lien autorisé rendu, lien externe non autorisé rendu en texte brut, injection `"` ou `javascript:` neutralisée.

### T4 — Article hebdomadaire n°7 et suivants
- Sujets prévus : « IA et données personnelles au quotidien », « Préparer un rendez-vous administratif avec l'IA », « 10 demandes utiles pour indépendants ».
- Format `articles/NN-slug.md`, 300 à 500 mots, conseils concrets et prudents, aucune affirmation juridique précise sans source officielle.
- Critères : article listé sur l'accueil, page générée, contrôles verts, ligne ajoutée au journal.

### T5 — Accessibilité et performance
- Vérifier contrastes (WCAG AA), focus visible, ordre de tabulation, textes alternatifs.
- Ajouter un contrôle simple dans `checks()` si un défaut récurrent est trouvé.
- Critères : rapport court dans la description du commit, contrôles verts.

### T6 — Version anglaise (plus tard)
- Seulement après les premières ventes. Ne pas commencer sans demande explicite.

### T7 — [HUMAIN] Actions réservées au propriétaire
- Créer les paliers GitHub Sponsors (5 / 15 / 50 USD par mois).
- Vérifier le compte de versement Gumroad et faire un achat test de 5 CHF.
- Envoyer les messages de partenariat (`docs/PARTENARIATS.md`) et de prospection (`docs/KIT_DIFFUSION.md`) depuis ses propres comptes.
- Décider de l'affichage éventuel de l'IBAN (déconseillé : révèle le titulaire).
- Signaler chaque vente, atelier ou partenaire pour mise à jour du journal.

## 7. Ce qu'un agent ne doit pas faire

- Envoyer des messages, e-mails ou publications au nom du propriétaire.
- Créer, modifier ou supprimer des produits de paiement, ou toucher à l'argent.
- Publier une identité, un IBAN ou une donnée personnelle.
- Ajouter des statistiques, traceurs, pop-ups ou newsletters.
- Inventer des preuves sociales.
