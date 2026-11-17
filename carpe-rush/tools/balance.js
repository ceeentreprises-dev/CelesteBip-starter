// Outil d'équilibrage : simule des parties jouées par le pilote automatique.
// Usage : node tools/balance.js [nombre_de_parties]
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const dir = path.join(__dirname, '..', 'js');
for (const f of ['config.js', 'game.js']) {
  vm.runInThisContext(fs.readFileSync(path.join(dir, f), 'utf8'), { filename: f });
}
const CR = globalThis.CR;
const runs = Number(process.argv[2]) || 150;

function rng(seed) { // mulberry32, résultats reproductibles
  return function () {
    seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// Le bot a un temps de réaction et une imprécision, comme un humain moyen.
function play(upgrades, seed) {
  const r = rng(seed);
  const g = new CR.Game(upgrades, { random: r });
  const dt = 1 / 60;
  let think = 0;
  while (!g.over && g.time < 600) {
    think -= dt;
    if (think <= 0) { g.targetX = g.botTarget() + (r() - 0.5) * 30; think = 0.12; }
    g.update(dt);
  }
  return { score: g.score, level: g.level, time: g.time, combo: g.bestCombo, gems: g.gemsEarned() };
}

const profiles = {
  'sans amélioration': {},
  'moyen': { magnet: 1, shield: 1, slow: 1, treasure: 1 },
  'maximum': { magnet: 3, shield: 3, slow: 3, life: 2, treasure: 3 },
};

const med = a => { const s = [...a].sort((x, y) => x - y); return s[Math.floor(s.length / 2)]; };
for (const [name, up] of Object.entries(profiles)) {
  const res = [];
  for (let i = 0; i < runs; i++) res.push(play(up, 1000 + i));
  console.log(`${name.padEnd(18)} score médian ${String(med(res.map(x => x.score))).padStart(6)}`
    + ` | niveau ${med(res.map(x => x.level))} | durée ${med(res.map(x => x.time)).toFixed(0)} s`
    + ` | combo max ${med(res.map(x => x.combo))} | 💎 ${med(res.map(x => x.gems))}`);
}
