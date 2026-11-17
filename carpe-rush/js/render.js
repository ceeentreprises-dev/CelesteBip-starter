// Carpe Rush – dessin sur canvas : décor, objets, carpe, particules, HUD.
(function (root) {
  const CR = root.CR || (root.CR = {});
  const TAU = Math.PI * 2;

  class Renderer {
    constructor(canvas) {
      this.canvas = canvas;
      this.ctx = canvas.getContext('2d');
      this.W = CR.CONFIG.width; this.H = CR.CONFIG.height;
      this.particles = [];
      for (let i = 0; i < 160; i++) this.particles.push({ life: 0 }); // réserve réutilisée
      this.texts = [];
      this.shake = 0;
      this.flash = 0;
      this.bubbles = Array.from({ length: 18 }, () => this.newBubble(true));
      this.bg = this.buildBackground();
    }

    resize(scale) {
      const dpr = Math.min(root.devicePixelRatio || 1, 2);
      this.canvas.width = Math.round(this.W * scale * dpr);
      this.canvas.height = Math.round(this.H * scale * dpr);
      this.canvas.style.width = Math.round(this.W * scale) + 'px';
      this.canvas.style.height = Math.round(this.H * scale) + 'px';
      this.ctx.setTransform(scale * dpr, 0, 0, scale * dpr, 0, 0);
    }

    // Décor dessiné une seule fois dans une image hors écran
    buildBackground() {
      const c = document.createElement('canvas');
      c.width = this.W; c.height = this.H;
      const g = c.getContext('2d');
      const grad = g.createLinearGradient(0, 0, 0, this.H);
      grad.addColorStop(0, '#0b6e8a'); grad.addColorStop(0.55, '#08465f'); grad.addColorStop(1, '#04212f');
      g.fillStyle = grad; g.fillRect(0, 0, this.W, this.H);
      // rayons de lumière
      g.globalCompositeOperation = 'lighter';
      for (let i = 0; i < 5; i++) {
        const x = 30 + i * 75;
        const rg = g.createLinearGradient(0, 0, 0, this.H * 0.8);
        rg.addColorStop(0, 'rgba(160,230,255,0.10)'); rg.addColorStop(1, 'rgba(160,230,255,0)');
        g.fillStyle = rg;
        g.beginPath(); g.moveTo(x, 0); g.lineTo(x + 40, 0); g.lineTo(x + 110, this.H * 0.8); g.lineTo(x + 20, this.H * 0.8); g.fill();
      }
      g.globalCompositeOperation = 'source-over';
      // fond sableux et algues
      g.fillStyle = '#0a2c22';
      g.beginPath(); g.moveTo(0, this.H);
      for (let x = 0; x <= this.W; x += 20) g.lineTo(x, this.H - 22 - Math.sin(x * 0.05) * 6);
      g.lineTo(this.W, this.H); g.fill();
      g.strokeStyle = '#1f7a4d'; g.lineWidth = 4; g.lineCap = 'round';
      for (const sx of [18, 46, 300, 334]) {
        g.beginPath(); g.moveTo(sx, this.H - 15);
        for (let y = 0; y < 90; y += 10) g.lineTo(sx + Math.sin(y * 0.12 + sx) * 8, this.H - 15 - y);
        g.stroke();
      }
      return c;
    }

    newBubble(anyY) {
      return { x: Math.random() * this.W, y: anyY ? Math.random() * this.H : this.H + 10,
        r: 1 + Math.random() * 3, v: 15 + Math.random() * 30 };
    }

    burst(x, y, color, n = 12, speed = 160) {
      for (const p of this.particles) {
        if (n <= 0) break;
        if (p.life > 0) continue;
        const a = Math.random() * TAU, s = speed * (0.3 + Math.random() * 0.7);
        Object.assign(p, { x, y, vx: Math.cos(a) * s, vy: Math.sin(a) * s - 40,
          life: 0.5 + Math.random() * 0.4, max: 0.9, color, size: 2 + Math.random() * 3 });
        n--;
      }
    }

    floatText(x, y, text, color = '#fff', size = 18) {
      this.texts.push({ x, y, text, color, size, life: 0.9 });
    }

    step(dt) {
      for (const p of this.particles) {
        if (p.life <= 0) continue;
        p.life -= dt; p.x += p.vx * dt; p.y += p.vy * dt; p.vy += 300 * dt;
      }
      for (let i = this.texts.length - 1; i >= 0; i--) {
        const t = this.texts[i]; t.life -= dt; t.y -= 40 * dt;
        if (t.life <= 0) this.texts.splice(i, 1);
      }
      for (const b of this.bubbles) {
        b.y -= b.v * dt; b.x += Math.sin(b.y * 0.05) * 0.3;
        if (b.y < -10) Object.assign(b, this.newBubble(false));
      }
      this.shake = Math.max(0, this.shake - dt * 30);
      this.flash = Math.max(0, this.flash - dt * 3);
    }

    draw(game, opts = {}) {
      const g = this.ctx;
      g.save();
      if (this.shake > 0) g.translate((Math.random() - 0.5) * this.shake, (Math.random() - 0.5) * this.shake);
      g.drawImage(this.bg, 0, 0);
      if (game.effects.slow > 0) { g.fillStyle = 'rgba(105,240,174,0.08)'; g.fillRect(0, 0, this.W, this.H); }

      g.fillStyle = 'rgba(200,240,255,0.35)';
      for (const b of this.bubbles) { g.beginPath(); g.arc(b.x, b.y, b.r, 0, TAU); g.fill(); }

      for (const it of game.items) this.drawItem(it);
      this.drawCarp(game);

      for (const p of this.particles) {
        if (p.life <= 0) continue;
        g.globalAlpha = Math.max(0, p.life / p.max);
        g.fillStyle = p.color; g.fillRect(p.x - p.size / 2, p.y - p.size / 2, p.size, p.size);
      }
      g.globalAlpha = 1;
      g.textAlign = 'center'; g.font = 'bold 16px system-ui, sans-serif';
      for (const t of this.texts) {
        g.globalAlpha = Math.min(1, t.life * 2);
        g.font = `bold ${t.size}px system-ui, sans-serif`;
        g.fillStyle = 'rgba(0,0,0,0.5)'; g.fillText(t.text, t.x + 1, t.y + 1);
        g.fillStyle = t.color; g.fillText(t.text, t.x, t.y);
      }
      g.globalAlpha = 1;
      if (this.flash > 0) { g.fillStyle = `rgba(232,70,60,${this.flash * 0.35})`; g.fillRect(0, 0, this.W, this.H); }
      g.restore();
      if (!opts.hideHud) this.drawHud(game);
    }

    drawItem(it) {
      const g = this.ctx, C = CR.CONFIG.items[it.kind];
      const x = it.x + Math.sin(it.wobble) * 1.5, y = it.y;
      g.save();
      if (it.kind === 'gold' || it.kind === 'bigGold') {
        const grad = g.createRadialGradient(x - it.r * 0.3, y - it.r * 0.3, 1, x, y, it.r);
        grad.addColorStop(0, '#fff6c2'); grad.addColorStop(0.4, C.color); grad.addColorStop(1, '#b37400');
        g.fillStyle = grad; g.beginPath(); g.arc(x, y, it.r, 0, TAU); g.fill();
        if (it.kind === 'bigGold') { g.strokeStyle = '#fff3a0'; g.lineWidth = 2; g.stroke(); }
      } else if (it.kind === 'bomb') {
        g.fillStyle = '#2b1416'; g.beginPath(); g.arc(x, y, it.r, 0, TAU); g.fill();
        g.strokeStyle = C.color; g.lineWidth = 3; g.stroke();
        for (let i = 0; i < 6; i++) { // pointes
          const a = i * TAU / 6 + it.wobble * 0.3;
          g.beginPath(); g.moveTo(x + Math.cos(a) * it.r, y + Math.sin(a) * it.r);
          g.lineTo(x + Math.cos(a) * (it.r + 6), y + Math.sin(a) * (it.r + 6)); g.stroke();
        }
        g.fillStyle = C.color; g.beginPath(); g.arc(x, y, 3.5, 0, TAU); g.fill();
      } else {
        g.fillStyle = C.color; g.globalAlpha = 0.25;
        g.beginPath(); g.arc(x, y, it.r + 5, 0, TAU); g.fill();
        g.globalAlpha = 1; g.beginPath(); g.arc(x, y, it.r, 0, TAU); g.fill();
        g.fillStyle = '#0b2a3a'; g.font = 'bold 14px system-ui, sans-serif';
        g.textAlign = 'center'; g.textBaseline = 'middle';
        g.fillText({ shield: '◆', magnet: 'U', slow: '⏱', heart: '♥' }[it.kind], x, y + 1);
      }
      g.restore();
    }

    drawCarp(game) {
      const g = this.ctx, P = CR.CONFIG.player;
      const x = game.px, y = P.y, w = P.width, h = P.height;
      const tilt = Math.max(-0.35, Math.min(0.35, (game.px - game.prevPx) * 0.08));
      const blink = game.invuln > 0 && Math.floor(game.time * 12) % 2 === 0;
      if (blink) return;
      g.save(); g.translate(x, y); g.rotate(tilt);
      if (game.effects.magnet > 0) {
        g.strokeStyle = 'rgba(179,136,255,0.35)'; g.lineWidth = 2;
        g.beginPath(); g.arc(0, 0, 40 + Math.sin(game.time * 6) * 4, 0, TAU); g.stroke();
      }
      // queue
      const sw = Math.sin(game.time * 10) * 4;
      g.fillStyle = '#e8743b';
      g.beginPath(); g.moveTo(-w * 0.38, 0); g.lineTo(-w * 0.62, -h * 0.5 + sw); g.lineTo(-w * 0.62, h * 0.5 + sw); g.fill();
      // corps
      const grad = g.createLinearGradient(0, -h / 2, 0, h / 2);
      grad.addColorStop(0, '#ffb15c'); grad.addColorStop(1, '#e0612a');
      g.fillStyle = grad;
      g.beginPath(); g.ellipse(0, 0, w * 0.42, h * 0.5, 0, 0, TAU); g.fill();
      // écailles
      g.strokeStyle = 'rgba(255,255,255,0.25)'; g.lineWidth = 1;
      for (let i = -1; i <= 1; i++) { g.beginPath(); g.arc(i * 9, 2, 6, Math.PI * 1.1, Math.PI * 1.9); g.stroke(); }
      // nageoire et œil
      g.fillStyle = '#ffd08a';
      g.beginPath(); g.ellipse(-2, -h * 0.45, 9, 4, -0.3, 0, TAU); g.fill();
      g.fillStyle = '#fff'; g.beginPath(); g.arc(w * 0.24, -4, 5, 0, TAU); g.fill();
      g.fillStyle = '#111'; g.beginPath(); g.arc(w * 0.26, -4, 2.5, 0, TAU); g.fill();
      // bouche ouverte vers le haut
      g.fillStyle = '#7a2412'; g.beginPath(); g.ellipse(w * 0.36, -6, 4, 3, 0, 0, TAU); g.fill();
      g.restore();
      if (game.effects.shield > 0) {
        g.save();
        g.strokeStyle = 'rgba(79,195,247,0.85)'; g.fillStyle = 'rgba(79,195,247,0.15)'; g.lineWidth = 3;
        g.beginPath(); g.ellipse(x, y, w * 0.62, h * 0.95, 0, 0, TAU); g.fill(); g.stroke();
        g.restore();
      }
    }

    drawHud(game) {
      const g = this.ctx;
      g.save();
      g.fillStyle = 'rgba(0,20,30,0.45)'; g.fillRect(0, 0, this.W, 46);
      g.textBaseline = 'middle';
      g.fillStyle = '#fff'; g.font = 'bold 22px system-ui, sans-serif'; g.textAlign = 'left';
      g.fillText(game.score, 12, 23);
      const sw = g.measureText(String(game.score)).width;
      g.font = '12px system-ui, sans-serif'; g.fillStyle = '#9fd8ea';
      g.fillText('Niv. ' + game.level, 12 + sw + 10, 25);
      g.textAlign = 'right'; g.font = '18px system-ui, sans-serif'; g.fillStyle = '#ff6f91';
      g.fillText('♥'.repeat(Math.max(0, game.lives)), this.W - 48, 23);
      if (game.multiplier > 1) {
        g.textAlign = 'center'; g.font = 'bold 16px system-ui, sans-serif'; g.fillStyle = '#ffd23f';
        g.fillText(`x${game.multiplier}  ·  combo ${game.combo}`, this.W / 2, 64);
      }
      // jauges des bonus actifs
      let yy = 80;
      for (const k of ['shield', 'magnet', 'slow']) {
        const t = game.effects[k]; if (t <= 0) continue;
        const max = game.duration(k);
        g.fillStyle = 'rgba(0,0,0,0.35)'; g.fillRect(this.W / 2 - 50, yy, 100, 6);
        g.fillStyle = CR.CONFIG.items[k].color; g.fillRect(this.W / 2 - 50, yy, 100 * t / max, 6);
        yy += 10;
      }
      g.restore();
    }
  }

  CR.Renderer = Renderer;
})(typeof window !== 'undefined' ? window : globalThis);
