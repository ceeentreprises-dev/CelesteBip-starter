# AGENTS.md — instructions pour les agents de code (Codex, Claude Code, etc.)

Ce fichier est lu automatiquement par les agents de code. Il décrit le projet, les règles à ne jamais enfreindre, les commandes et la liste des tâches prêtes à exécuter. Le dossier complet du projet, de A à Z, est dans [`docs/DOSSIER_COMPLET.md`](docs/DOSSIER_COMPLET.md).

## 1. Le projet en 5 lignes

- **CelestBIP** : initiative indépendante (Suisse romande, depuis novembre 2026) pour rendre l'IA accessible à toute personne, avec méthode et prudence.
- **Site statique** généré par un seul script Python (`CELESTBIP_MASTER.py`), publié sur GitHub Pages : https://ceeentreprises-dev.github.io/CelesteBip-starter/
- **Modèle actuel** : activité 100 % numérique, sans prestation du propriétaire humain. Les offres historiques de séance, d'atelier et d'intervention sur site sont des incompatibilités à traiter, pas des prestations à lui attribuer. Voir `docs/REGLES_EXPLOITATION.md`.
- **Langue** : tout le contenu public est en **français (fr-CH)**, ton clair, sobre, sans jargon.
- **État marchand revérifié au 20 nov. 2026** : site en ligne, 7 articles et 4 produits Gumroad publiés. Leurs compteurs cumulés consultés indiquent 0 vente ; aucun versement ne figure dans la liste retournée. Cela ne valide pas un versement futur ni une prestation livrée. Aucun partenaire signé n'est annoncé.

## 2. Règles absolues (ne jamais enfreindre)

1. **Identité privée.** Aucun nom de personne, adresse, téléphone, e-mail personnel ou IBAN dans le dépôt ou sur le site. Seule identité publique : le profil GitHub `ceeentreprises-dev`. Le fichier `support-approved.json` (IBAN) est ignoré par git et ne doit jamais être versionné.
2. **Aucun fait inventé.** Pas de faux témoignages, faux clients, faux chiffres, faux partenaires, faux labels. Le journal (`docs/JOURNAL.md`) ne contient que des faits vérifiables.
3. **Aucune promesse** de résultat financier, professionnel, juridique ou médical. CelestBIP n'est ni une association reconnue d'utilité publique, ni une offre d'investissement.
4. **Aucun suivi** : pas de cookie, pas de script d'analyse, pas de ressource externe (polices, CDN) sur le site. La CSP de `vercel.json` et les contrôles doivent rester verts.
5. **Liens externes en liste blanche** : seuls les préfixes de `ALLOWED_LINK_PREFIXES` (paiement + GitHub du projet) et `SITE_URL` sont autorisés. Ajouter un nouveau domaine = modifier la liste ET justifier dans le commit.
6. **Aucune dépendance obligatoire** pour `build`/`test` : bibliothèque standard uniquement (reportlab est optionnel).
7. **Ne pas casser la publication** : tout push sur `main` ou sur la branche de travail déclenche `.github/workflows/pages.yml`, qui publie si les tests passent.

8. **Exploitation 100 % numérique, règle permanente du 21 novembre 2026.** Le propriétaire humain ne fournit aucune prestation, ne passe aucun appel ni visioconférence, n'anime aucun atelier en direct ou en personne, ne se déplace dans aucune entreprise ni ailleurs pour l'activité et ne rédige ni n'envoie manuellement aucun e-mail. L'e-mail est le seul canal d'échange externe éventuel, pris en charge par les agents et outils effectivement connectés selon les autorisations applicables. Ne jamais planifier le propriétaire comme formateur, coach, prestataire, intervenant, commercial ou rédacteur. Une dépendance non automatisable est un blocage, jamais une tâche à lui transférer ou une réussite à inventer. Lire `docs/REGLES_EXPLOITATION.md` ; cette règle remplace les anciens plans humains sans modifier les permissions techniques ni donner une autorisation générale de messages, paiements ou dépenses.
9. **Budget sortant nul.** 0 CHF / 0 USD ; aucun achat test, abonnement ni coût inconnu.

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

## 6. Tâches et état d'avancement

Les tâches T1 à T5 ci-dessous décrivent l'historique technique réalisé ; elles ne constituent pas des offres à promouvoir. Les anciens plans de prestation humaine sont supersédés par la règle du 21 novembre 2026. Les dépendances non automatisables restent des blocages, sans travail opérationnel attribué au propriétaire.

T1 à T5 ont été réalisées, testées et publiées le 17 novembre 2026 sur la branche de travail. La suite opérationnelle et ses critères de validation sont dans `docs/PLAN_ACTION.md` ; ne pas recommencer les tâches terminées sans régression constatée.

### T1 — Historique : carte « Atelier PME » (900 CHF), incompatible à traiter
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

### T4 — Article n°7 terminé ; suivants à planifier
- Sujets prévus : « IA et données personnelles au quotidien », « Préparer un rendez-vous administratif avec l'IA », « 10 demandes utiles pour indépendants ».
- Format `articles/NN-slug.md`, 300 à 500 mots, conseils concrets et prudents, aucune affirmation juridique précise sans source officielle.
- Critères : article listé sur l'accueil, page générée, contrôles verts, ligne ajoutée au journal.

### T5 — Accessibilité et performance
- Vérifier contrastes (WCAG AA), focus visible, ordre de tabulation, textes alternatifs.
- Ajouter un contrôle simple dans `checks()` si un défaut récurrent est trouvé.
- Critères : rapport court dans la description du commit, contrôles verts.

### T6 — Version anglaise (plus tard)
- Seulement après les premières ventes. Ne pas commencer sans demande explicite.

### T7 — Blocages et vérifications, sans prestation humaine
- Ne pas réaliser d'achat test : budget sortant nul.
- Consigner les éventuelles exigences d'identité, de versement ou de consentement non automatisables ; ne pas les déclarer résolues et ne pas les transformer en mission opérationnelle du propriétaire.
- Ne pas lui demander d'envoyer, personnaliser ou rédiger des messages, ni d'assurer des échanges, ventes, séances ou ateliers.
- Les agents ne peuvent envoyer un e-mail qu'avec une instruction applicable et un outil réellement connecté ; un brouillon ou une consigne de mémoire ne constitue pas un envoi autorisé.
- Rapprocher les offres historiques de la règle numérique avant toute promotion. Aucun produit marchand n'est modifié par cette mise à jour documentaire.
- Mettre à jour le journal seulement avec des événements vérifiés, sans donnée personnelle ni secret.

## 7. Ce qu'un agent ne doit pas faire

- Envoyer un e-mail sans instruction applicable et sans outil autorisé, ou utiliser un autre canal pour un échange commercial externe. Ne pas demander au propriétaire de rédiger ou d'envoyer à la place de l'agent.
- Créer, modifier ou supprimer des produits de paiement, ou toucher à l'argent.
- Publier une identité, un IBAN ou une donnée personnelle.
- Ajouter des statistiques, traceurs, pop-ups ou newsletters.
- Inventer des preuves sociales.
