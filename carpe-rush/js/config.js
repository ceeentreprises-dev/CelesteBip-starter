// Carpe Rush – réglages du jeu. Tout l'équilibrage se fait ici.
(function (root) {
  const CR = root.CR || (root.CR = {});

  CR.CONFIG = {
    width: 360,
    height: 640,
    startLives: 3,
    maxLives: 5,

    player: { y: 575, width: 64, height: 30, speed: 520, follow: 14 },

    // Vitesse de chute et fréquence d'apparition selon le niveau
    fallSpeed: { base: 150, perLevel: 18, max: 430 },
    spawnEvery: { base: 0.85, perLevel: 0.05, min: 0.32 },
    pointsPerLevel: 400,

    // Objets qui tombent : weight = probabilité relative
    items: {
      gold:   { weight: 60, radius: 11, points: 10, color: '#ffd23f' },
      bigGold:{ weight: 8,  radius: 15, points: 40, color: '#ffb000' },
      bomb:   { weight: 20, radius: 13, color: '#e8463c', bombPerLevel: 2.5 },
      shield: { weight: 3,  radius: 13, color: '#4fc3f7', duration: 6 },
      magnet: { weight: 3,  radius: 13, color: '#b388ff', duration: 6 },
      slow:   { weight: 2,  radius: 13, color: '#69f0ae', duration: 5 },
      heart:  { weight: 0.8,radius: 13, color: '#ff6f91' },
    },

    combo: { perMultiplier: 8, maxMultiplier: 5 },
    magnetRange: 150,
    magnetPull: 520,
    slowFactor: 0.5,
    gemsPerPoints: 60,   // 1 💎 tous les 60 points

    // Améliorations de la boutique (coût par niveau, en 💎)
    upgrades: {
      magnet:  { name: 'Aimant',      desc: '+1,5 s de durée par niveau',      costs: [20, 45, 90] },
      shield:  { name: 'Bouclier',    desc: '+1,5 s de durée par niveau',      costs: [20, 45, 90] },
      slow:    { name: 'Ralenti',     desc: '+1,5 s de durée par niveau',      costs: [15, 35, 70] },
      life:    { name: 'Vie bonus',   desc: '+1 vie au départ',                costs: [60, 150] },
      treasure:{ name: 'Trésor',      desc: '+15 % de 💎 gagnés par niveau',   costs: [30, 70, 140] },
    },

    achievements: [
      { id: 'first',    name: 'Premier plongeon', desc: 'Jouer une partie' },
      { id: 's500',     name: 'Bonne pêche',      desc: 'Atteindre 500 points' },
      { id: 's2000',    name: 'Carpe dorée',      desc: 'Atteindre 2000 points' },
      { id: 's5000',    name: 'Légende du lac',   desc: 'Atteindre 5000 points' },
      { id: 'combo20',  name: 'En rythme',        desc: 'Combo de 20' },
      { id: 'combo50',  name: 'Inarrêtable',      desc: 'Combo de 50' },
      { id: 'lvl5',     name: 'Courant fort',     desc: 'Atteindre le niveau 5' },
      { id: 'shieldBlock', name: 'Intouchable',   desc: 'Bloquer une bombe avec le bouclier' },
      { id: 'shopper',  name: 'Investisseur',     desc: 'Acheter une amélioration' },
    ],
  };
})(typeof window !== 'undefined' ? window : globalThis);
