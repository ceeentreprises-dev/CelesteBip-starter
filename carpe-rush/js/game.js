// Carpe Rush – logique du jeu, sans dessin ni DOM.
// Fonctionne aussi dans Node (outil d'équilibrage tools/balance.js).
(function (root) {
  const CR = root.CR || (root.CR = {});

  class Game {
    // upgrades : { magnet, shield, slow, life, treasure } (niveaux achetés)
    // opts.random : générateur aléatoire (pour des simulations reproductibles)
    // opts.onEvent : callback(type, data) pour le son et les effets
    constructor(upgrades, opts = {}) {
      this.C = CR.CONFIG;
      this.up = Object.assign({ magnet: 0, shield: 0, slow: 0, life: 0, treasure: 0 }, upgrades || {});
      this.random = opts.random || Math.random;
      this.onEvent = opts.onEvent || (() => {});
      this.reset();
    }

    reset() {
      const C = this.C;
      this.time = 0;
      this.score = 0;
      this.lives = Math.min(C.maxLives, C.startLives + this.up.life);
      this.level = 1;
      this.combo = 0;
      this.bestCombo = 0;
      this.items = [];
      this.spawnTimer = 0.6;
      this.px = C.width / 2;           // position de la carpe
      this.prevPx = this.px;
      this.targetX = this.px;
      this.keyDir = 0;
      this.effects = { shield: 0, magnet: 0, slow: 0 };
      this.invuln = 0;
      this.over = false;
      this.stats = { gold: 0, bombsHit: 0, shieldBlocks: 0, powerups: 0 };
    }

    get multiplier() {
      const c = this.C.combo;
      return Math.min(c.maxMultiplier, 1 + Math.floor(this.combo / c.perMultiplier));
    }

    duration(kind) {
      return this.C.items[kind].duration + 1.5 * (this.up[kind] || 0);
    }

    fallSpeed() {
      const f = this.C.fallSpeed;
      return Math.min(f.max, f.base + f.perLevel * (this.level - 1));
    }

    spawnInterval() {
      const s = this.C.spawnEvery;
      return Math.max(s.min, s.base - s.perLevel * (this.level - 1));
    }

    pickKind() {
      const items = this.C.items;
      let total = 0;
      const w = {};
      for (const k in items) {
        w[k] = items[k].weight + (k === 'bomb' ? items.bomb.bombPerLevel * (this.level - 1) : 0);
        if (k === 'heart' && this.lives >= this.C.maxLives) w[k] = 0;
        total += w[k];
      }
      let r = this.random() * total;
      for (const k in w) { r -= w[k]; if (r <= 0) return k; }
      return 'gold';
    }

    spawn() {
      const kind = this.pickKind();
      const def = this.C.items[kind];
      const m = def.radius + 8;
      this.items.push({
        kind, r: def.radius,
        x: m + this.random() * (this.C.width - 2 * m),
        y: -def.radius,
        vy: this.fallSpeed() * (0.85 + this.random() * 0.3),
        wobble: this.random() * Math.PI * 2,
        prevY: -def.radius,
      });
    }

    update(dt) {
      if (this.over) return;
      const C = this.C;
      this.time += dt;
      for (const k in this.effects) this.effects[k] = Math.max(0, this.effects[k] - dt);
      this.invuln = Math.max(0, this.invuln - dt);
      const slow = this.effects.slow > 0 ? C.slowFactor : 1;

      // Déplacement de la carpe (doigt/souris : suit la cible ; clavier : vitesse fixe)
      this.prevPx = this.px;
      if (this.keyDir !== 0) {
        this.px += this.keyDir * C.player.speed * dt;
        this.targetX = this.px;
      } else {
        this.px += (this.targetX - this.px) * Math.min(1, C.player.follow * dt);
      }
      const half = C.player.width / 2;
      this.px = Math.max(half, Math.min(C.width - half, this.px));

      // Apparition
      this.spawnTimer -= dt * slow;
      if (this.spawnTimer <= 0) {
        this.spawn();
        this.spawnTimer = this.spawnInterval();
      }

      // Chute, aimant, collisions
      const py = C.player.y;
      const hw = half + 2, hh = C.player.height / 2;
      for (let i = this.items.length - 1; i >= 0; i--) {
        const it = this.items[i];
        it.prevY = it.y;
        it.y += it.vy * slow * dt;
        it.wobble += dt * 3;
        if (this.effects.magnet > 0 && (it.kind === 'gold' || it.kind === 'bigGold')) {
          const dx = this.px - it.x, dy = py - it.y;
          const d = Math.hypot(dx, dy);
          if (d < C.magnetRange && d > 1) {
            it.x += (dx / d) * C.magnetPull * dt;
            it.y += (dy / d) * C.magnetPull * 0.5 * dt;
          }
        }
        // Collision « balayée » : l'objet a traversé la bande de la carpe pendant cette frame
        const top = py - hh - it.r, bottom = py + hh + it.r;
        const crossed = it.prevY <= bottom && it.y >= top;
        const minX = Math.min(this.px, this.prevPx) - hw - it.r;
        const maxX = Math.max(this.px, this.prevPx) + hw + it.r;
        if (crossed && it.x >= minX && it.x <= maxX) {
          this.items.splice(i, 1);
          this.collect(it);
          continue;
        }
        if (it.y - it.r > C.height) {
          this.items.splice(i, 1);
          if (it.kind === 'gold' || it.kind === 'bigGold') {
            if (this.combo > 0) this.onEvent('comboLost', { combo: this.combo });
            this.combo = 0;
          }
        }
      }
    }

    collect(it) {
      const C = this.C;
      switch (it.kind) {
        case 'gold':
        case 'bigGold': {
          this.combo++;
          this.bestCombo = Math.max(this.bestCombo, this.combo);
          const pts = C.items[it.kind].points * this.multiplier;
          this.addScore(pts);
          this.stats.gold++;
          this.onEvent('gold', { x: it.x, y: it.y, pts, big: it.kind === 'bigGold', combo: this.combo });
          break;
        }
        case 'bomb':
          if (this.effects.shield > 0) {
            this.stats.shieldBlocks++;
            this.onEvent('block', { x: it.x, y: it.y });
          } else if (this.invuln <= 0) {
            this.lives--;
            this.combo = 0;
            this.invuln = 1.0;
            this.stats.bombsHit++;
            this.onEvent('hit', { x: it.x, y: it.y, lives: this.lives });
            if (this.lives <= 0) { this.over = true; this.onEvent('over', {}); }
          }
          break;
        case 'heart':
          this.lives = Math.min(C.maxLives, this.lives + 1);
          this.stats.powerups++;
          this.onEvent('power', { x: it.x, y: it.y, kind: 'heart' });
          break;
        default:
          this.effects[it.kind] = this.duration(it.kind);
          this.stats.powerups++;
          this.onEvent('power', { x: it.x, y: it.y, kind: it.kind });
      }
    }

    addScore(pts) {
      this.score += pts;
      const lvl = 1 + Math.floor(this.score / this.C.pointsPerLevel);
      if (lvl > this.level) {
        this.level = lvl;
        this.onEvent('level', { level: lvl });
      }
    }

    gemsEarned() {
      const base = Math.floor(this.score / this.C.gemsPerPoints);
      return Math.floor(base * (1 + 0.15 * this.up.treasure));
    }

    // Pilote automatique : sert aux tests d'équilibrage et à la démo du menu.
    botTarget() {
      const C = this.C;
      const py = C.player.y;
      let best = null, bestScore = -Infinity;
      for (const it of this.items) {
        if (it.kind === 'bomb' || it.y > py) continue;
        const t = (py - it.y) / Math.max(1, it.vy);
        if (t > 2.2) continue;
        const reach = Math.abs(it.x - this.px) / C.player.speed;
        if (reach > t + 0.05) continue;
        let value = it.kind === 'bigGold' ? 4 : it.kind === 'gold' ? 2 : 3;
        let s = value - t * 1.2 - reach;
        // pénalité si une bombe tombe près de la trajectoire
        for (const b of this.items) {
          if (b.kind !== 'bomb' || b.y > py) continue;
          const tb = (py - b.y) / Math.max(1, b.vy);
          if (tb < t + 0.3 && Math.abs(b.x - it.x) < C.player.width) s -= 3;
        }
        if (s > bestScore) { bestScore = s; best = it; }
      }
      let target = best ? best.x : this.px;
      // esquive : bombe imminente au-dessus de la cible
      for (const b of this.items) {
        if (b.kind !== 'bomb' || b.y > py) continue;
        const tb = (py - b.y) / Math.max(1, b.vy);
        if (tb < 0.45 && Math.abs(b.x - target) < C.player.width / 2 + b.r + 6) {
          target = b.x < C.width / 2 ? b.x + C.player.width + b.r : b.x - C.player.width - b.r;
        }
      }
      return target;
    }
  }

  CR.Game = Game;
})(typeof window !== 'undefined' ? window : globalThis);
