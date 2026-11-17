# Carpe Rush

Jeu d'arcade HTML5 gratuit, jouable sur téléphone ou ordinateur. Guidez la carpe, attrapez l'or et évitez les bombes. Les bonus, combos et neuf succès font progresser la partie.

Le jeu existant vient de la branche `main` de ce dépôt, commit `157a948e21e4d6b5482bcf78b34d621fc1715aea`. Cette intégration conserve son moteur, ses graphismes Canvas et ses sons Web Audio ; elle rétablit son export par le générateur du site.

## Jouer

Depuis la racine du dépôt, lancer `python CELESTBIP_MASTER.py serve`, puis ouvrir `/carpe-rush/` dans l'aperçu local. Le jeu n'exige aucune installation, dépendance externe, inscription ou paiement.

Glisser le doigt ou la souris, ou utiliser les flèches pour déplacer la carpe. `P` ou `Échap` met en pause. Le pincement de l'écran reste disponible pour zoomer.

Les 💎 de la boutique sont gagnés en jouant. Ils n'ont aucune valeur réelle et ne s'achètent pas avec de l'argent. Aucun paiement n'est intégré au jeu.

## Sauvegarde et publication

Le record, les améliorations, les succès et le réglage sonore restent dans le stockage local du navigateur, sous la clé `carpe-rush-save-v1`. Le code du jeu n'envoie pas votre progression à un serveur. Effacer le stockage du navigateur efface la progression ; si ce stockage est bloqué, le jeu fonctionne sans sauvegarde. Les valeurs restaurées sont validées et les niveaux d'amélioration restent bornés.

Le générateur copie uniquement `index.html`, `css/style.css`, les six scripts `js/` et `LICENSE` vers `dist/carpe-rush/`. Les captures, outils de simulation, fichiers privés et ce README ne sont pas publiés. Le raccourci d'URL non borné `ff` de l'ancienne version a été retiré.

## Licence

Code sous licence MIT, voir [LICENSE](LICENSE). Les graphismes et sons sont générés localement par le code ; aucun CDN ou fichier audio distant n'est utilisé.
