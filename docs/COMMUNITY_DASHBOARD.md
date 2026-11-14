# CelestBIP Control — tableau communautaire (prototype)

Fichier : [community/index.html](../community/index.html)

## Fonctions préparées
- Vue responsive en français, filtres texte/type/statut.
- Consultation en lecture seule des issues et pull requests publiques de ce dépôt.
- Compteurs sur les éléments récupérés et nombre de commentaires déclaré par GitHub.
- Liens directs pour ouvrir une issue, proposer une amélioration, lire et commenter une PR.
- Aucun jeton GitHub, cookie, stockage local, formulaire d'envoi ou paiement.
- Rafraîchissement manuel, erreurs API affichées explicitement.

## Lancer pour vérifier
Ouvrir `community/index.html` dans un navigateur ou lancer un serveur statique local :
```bash
python -m http.server 8788 --directory community --bind 127.0.0.1
```
Puis ouvrir http://127.0.0.1:8788 .

**Attention :** le tableau effectue deux requêtes HTTPS à l'API publique GitHub. Contrairement au générateur Python principal, ce module nécessite une connexion réseau pour récupérer les informations. Il ne transmet aucun secret et n'écrit rien sur GitHub.

## Limites
- Seuls les 100 premiers résultats récents de chaque type sont chargés; pas de pagination.
- Le nombre de commentaires de PR peut différer des commentaires de revue; aucun contenu de commentaire n'est récupéré.
- Pas de permissions d'administration ni de réponses directement depuis la page.
- Les erreurs réseau et les limites d'API peuvent bloquer le chargement.
- Pas de preuve de déploiement public, de tests multi-navigateurs ni de conformité complète d'accessibilité.
- Le code est préparé sur branche de travail, pas fusionné.

## Validation avant fusion
1. Inspecter la page dans un navigateur mobile et desktop.
2. Vérifier le chargement, les filtres, les liens et les états vides.
3. Tester l'erreur réseau et les limites API.
4. Vérifier l'absence de secrets et de données privées.
5. Vérifier que le générateur principal fonctionne toujours avec ses tests.
6. Décider séparément si et où héberger la page; ne pas activer automatiquement GitHub Pages.

## Pistes futures
- Pagination et indicateurs de retard.
- Vues « besoin d'une réponse », « en attente de revue », « prochaine action ».
- Lecture des commentaires publics à la demande (attention aux limites API).
- Fichier de configuration pour suivre plusieurs dépôts explicitement publics.
- Journal de versions vérifiées et preuves de tests.
