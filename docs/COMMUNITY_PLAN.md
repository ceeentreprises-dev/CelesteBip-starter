# Programme communautaire — CelestBIP Starter

**Statut : propositions à développer, non fonctionnalités livrées.** Aucun revenu ni sponsor n'est présumé.

## Principes
- Budget de développement : 0 CHF par défaut.
- Respect de la licence MIT, des auteurs et de la confidentialité.
- Aucun appel réseau, aucune collecte, aucun paiement actif par défaut.
- Une amélioration par PR, tests reproductibles, pas de fusion automatique.
- Ne jamais publier de données privées, secrets, IBAN ou identités personnelles.

## Ordre de travail

### Lot A — qualité et communauté
1. Modèles d'issues : demande de fonctionnalité et bug.
2. Modèle de PR et critères de vérification.
3. Revue des tests et de l'accessibilité.
**Acceptation :** modèles visibles dans GitHub, commandes de tests exécutées avec résultats conservés.

### Lot B — personnalisation (proposition)
1. Exemple de fichier JSON local pour titre, sous-titre, sections et palette.
2. Validation stricte des valeurs et échappement HTML.
3. Valeurs par défaut identiques au comportement actuel.
4. Tests sur configuration valide, absente et malformée.
**Acceptation :** deux pages distinctes générées hors ligne, aucun changement sans configuration.

### Lot C — langue et pédagogie (proposition)
1. Variante anglaise, sans traduction automatique externe.
2. Guide gratuit : vérifier les réponses d'une IA.
3. Relecture humaine des textes et contrôle de lisibilité.
**Acceptation :** tests et vérification des deux langues, PDF ouvrables.

### Lot D — publication (proposition)
1. Changelog et version sémantique.
2. Archive ZIP vérifiée, instructions d'installation et captures sans données privées.
3. Publication seulement après validation des tests et du contenu.
**Acceptation :** URL de release, hash SHA-256, procédure reproductible.

## Communication — règles de preuve
- « Proposé » : idée ou issue.
- « Préparé » : branche ou PR.
- « Testé » : résultats locaux datés.
- « Publié » : fusion/release et URL vérifiées.
- « Sponsorisé » : preuve GitHub Sponsors.
Ne jamais convertir un statut en un autre sans preuve.

## Messages prêts à adapter après publication vérifiée

### Français
« CelestBIP Starter est un générateur open source gratuit qui prépare une page web et un guide PDF hors ligne. Le dépôt contient les instructions d'utilisation et de contribution. Vos retours sur la simplicité, l'accessibilité et les besoins de personnalisation sont les bienvenus. Projet : https://github.com/ceeentreprises-dev/CelesteBip-starter »

### English
« CelestBIP Starter is a free, open-source offline generator for a web page and a PDF guide. The repository includes usage and contribution instructions. Feedback on usability, accessibility and customization needs is welcome. Project: https://github.com/ceeentreprises-dev/CelesteBip-starter »

Ces messages décrivent le projet existant; ne pas annoncer les lots B à D comme disponibles avant livraison.

## Suivi minimal
À chaque évolution : date, issue/PR, auteur, changement, commande de test, résultat, URL de preuve, statut, prochaine action. Éviter les métriques inventées et les publications répétitives.
