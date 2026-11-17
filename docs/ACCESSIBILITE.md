# T5 — Accessibilité et performance

Vérification locale sur le site généré, avec Chromium, sans ressource extérieure ni modification des paiements. L’audit navigateur reste facultatif : la construction et les contrôles du projet utilisent la bibliothèque standard.

Deux défauts corrigés : le lien « Aller au contenu » des pages éditoriales quittait la page ; la navigation mobile fragmentait certains liens et coupait le haut du contour de focus. Le lien d’évitement cible désormais le `main` de la page courante et lui transfère le focus. La navigation utilise des liens d’un seul bloc, hauts d’au moins 44 px ; le header mobile reste dans le flux, sur fond sombre.

Vérification finale sur l’accueil et l’article 07, à **320, 390, 1024 et 1920 px** :

- Aucun débordement horizontal ni chevauchement du header avec le contenu.
- Lien d’évitement local, focus sur `main`, puis poursuite de la tabulation dans le contenu.
- Ordre clavier cohérent, contours visibles et entièrement dans le viewport ; liens de navigation non fragmentés, hauteur ≥ 44 px.
- Attributs `alt` présents ; l’unique illustration du hero est décorative (`alt=""`, `aria-hidden="true"`).
- Aucune erreur JavaScript.

Contrastes ponctuels calculés en sRGB linéarisé : bouton principal **7,58:1**, texte secondaire des cartes **≥8,93:1**, texte principal **17,71:1**. Sur le rendu du hero, texte bleu **≥3,31:1 à 1024 px** (grand texte, seuil AA 3:1) et ≥ 5,29:1 à 1440 px. Les alertes obtenues sur des rectangles contenant des étoiles lumineuses ont été contrôlées sur les glyphes : elles ne prouvaient pas un défaut de contraste. Palette et illustration conservées. Ces mesures ciblées ne constituent pas une certification exhaustive WCAG.

Le site n’ajoute aucun JavaScript, traceur, CDN ni police externe. L’accueil généré comprend 9839 octets de HTML, 4647 octets de CSS et 1681 octets de SVG ; les PDF sont téléchargés à la demande. Aucun outil supplémentaire obligatoire n’est nécessaire.
