# Politique de sécurité / Security policy

Ce document concerne **CelestBIP Starter**, un générateur Python destiné à fonctionner localement. Il ne constitue pas une certification de sécurité.

## Signaler une vulnérabilité / Report a vulnerability

Privilégiez la fonctionnalité **Private vulnerability reporting** de GitHub si elle est activée pour ce dépôt. Sinon, ouvrez une issue publique **sans détail sensible** pour demander un canal de communication privé.

Please use GitHub **Private vulnerability reporting** if enabled. Otherwise, open a public issue **without sensitive details** to request a private contact channel.

Ne publiez jamais de clés API, mots de passe, coordonnées bancaires, données personnelles, journaux confidentiels ni instructions d'exploitation d'une vulnérabilité dans une issue ou pull request publique.

## Principes

- L'exécution normale ne doit pas nécessiter de secrets, compte externe ni paiement.
- Le fichier `support-approved.json` doit rester privé et exclu de Git.
- Les modifications externes passent par une revue et les tests documentés, avant fusion.
- Les contributions non fiables ne doivent pas déclencher d'exécution automatique.
- Les incidents doivent être traités à partir de preuves vérifiables.

## Versions

La branche `main` est la seule branche visée par la maintenance actuelle. Aucun délai contractuel de correction n'est garanti.

## Portée des vérifications

La présence de ce fichier ne signifie pas qu'une analyse complète des dépendances, de l'historique Git, des secrets ou des vulnérabilités a déjà été menée.
