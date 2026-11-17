// Carpe Rush – écrans, contrôles, boucle de jeu, boutique et succès.
(function () {
  const C = CR.CONFIG;
  const $ = id => document.getElementById(id);
  const save = CR.Storage.load();
  const renderer = new CR.Renderer($('game'));
  const params = new URLSearchParams(location.search);

  let state = 'menu';       // menu | play | pause | over
  let game = null;
  let demo = new CR.Game({});  // partie jouée par le bot derrière le menu
  let scale = 1;
  let unlockedThisGame = [];

  CR.Audio.muted = save.muted;

  // ---------- Mise à l'échelle ----------
  function fit() {
    const pad = 8;
    scale = Math.min((innerWidth - pad) / C.width, (innerHeight - pad) / C.height);
    scale = Math.max(0.4, scale);
    renderer.resize(scale);
    const app = $('app');
    app.style.width = C.width * scale + 'px';
    app.style.height = C.height * scale + 'px';
  }
  addEventListener('resize', fit);
  fit();

  // ---------- Écrans ----------
  const screens = ['menu', 'help', 'shop', 'ach', 'pause', 'over'];
  function show(name) {
    for (const s of screens) $('screen-' + s).classList.toggle('hidden', s !== name);
    $('topbar').classList.toggle('hidden', name !== null);
  }
  function toMenu() {
    state = 'menu';
    CR.Audio.stopMusic();
    $('menu-best').textContent = save.best;
    $('menu-gems').textContent = save.gems;
    $('btn-mute').textContent = 'Son : ' + (CR.Audio.muted ? 'non' : 'oui');
    show('menu');
  }

  let toastTimer;
  function toast(msg) {
    const t = $('toast');
    t.textContent = msg; t.classList.remove('hidden');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => t.classList.add('hidden'), 1800);
  }

  // ---------- Succès ----------
  function unlock(id) {
    if (save.achievements[id]) return;
    save.achievements[id] = Date.now();
    const a = C.achievements.find(x => x.id === id);
    if (a) { unlockedThisGame.push(a.name); if (state === 'play') toast('Succès : ' + a.name); }
    CR.Storage.save();
  }
  function checkAchievements(g) {
    if (g.score >= 500) unlock('s500');
    if (g.score >= 2000) unlock('s2000');
    if (g.score >= 5000) unlock('s5000');
    if (g.bestCombo >= 20) unlock('combo20');
    if (g.bestCombo >= 50) unlock('combo50');
    if (g.level >= 5) unlock('lvl5');
    if (g.stats.shieldBlocks > 0) unlock('shieldBlock');
  }

  // ---------- Événements du jeu → son et effets ----------
  function onEvent(type, d) {
    CR.Audio.sfx(type, d);
    switch (type) {
      case 'gold':
        renderer.burst(d.x, d.y, d.big ? '#fff3a0' : '#ffd23f', d.big ? 16 : 8);
        renderer.floatText(d.x, d.y - 10, '+' + d.pts, '#ffd23f', d.big ? 20 : 16);
        if (d.combo > 0 && d.combo % C.combo.perMultiplier === 0 && game.multiplier <= C.combo.maxMultiplier)
          renderer.floatText(C.width / 2, 120, 'x' + game.multiplier + ' !', '#fff', 26);
        break;
      case 'hit':
        renderer.burst(d.x, d.y, '#e8463c', 22, 220);
        renderer.shake = 10; renderer.flash = 1;
        if (navigator.vibrate) navigator.vibrate(80);
        break;
      case 'block':
        renderer.burst(d.x, d.y, '#4fc3f7', 14);
        break;
      case 'power': {
        const label = { shield: 'Bouclier', magnet: 'Aimant', slow: 'Ralenti', heart: '+1 vie' }[d.kind];
        renderer.burst(d.x, d.y, C.items[d.kind].color, 14);
        renderer.floatText(d.x, d.y - 10, label, C.items[d.kind].color, 16);
        break;
      }
      case 'level':
        renderer.floatText(C.width / 2, 260, 'Niveau ' + d.level, '#9fd8ea', 30);
        break;
      case 'comboLost':
        if (d.combo >= 5) renderer.floatText(game.px, C.player.y - 40, 'Combo perdu', '#ff9a8a', 14);
        break;
      case 'over':
        setTimeout(endGame, 600);
        break;
    }
  }

  // ---------- Partie ----------
  function startGame() {
    CR.Audio.init();
    CR.Audio.setMuted(CR.Audio.muted);
    game = new CR.Game(save.upgrades, { onEvent });
    game.botPlay = params.has('bot');
    unlockedThisGame = [];
    unlock('first');
    state = 'play';
    show(null);
    CR.Audio.startMusic();
  }

  function endGame() {
    if (state !== 'play') return;
    state = 'over';
    CR.Audio.stopMusic();
    checkAchievements(game);
    const gems = game.gemsEarned();
    const record = game.score > save.best;
    save.best = Math.max(save.best, game.score);
    save.gems += gems;
    save.games++;
    CR.Storage.save();
    $('over-score').textContent = game.score;
    $('over-record').classList.toggle('hidden', !record || game.score === 0);
    $('over-gems').textContent = gems;
    $('over-stats').textContent = `Niveau ${game.level} · combo max ${game.bestCombo} · ${game.stats.gold} pièces`;
    $('over-ach').textContent = unlockedThisGame.length ? 'Succès : ' + unlockedThisGame.join(', ') : '';
    show('over');
  }

  function pause() {
    if (state !== 'play') return;
    state = 'pause'; CR.Audio.stopMusic(); show('pause');
  }
  function resume() {
    if (state !== 'pause') return;
    state = 'play'; show(null); CR.Audio.startMusic(); last = performance.now();
  }

  // ---------- Boutique ----------
  function renderShop() {
    $('shop-gems').textContent = save.gems;
    const list = $('shop-list'); list.innerHTML = '';
    for (const [key, u] of Object.entries(C.upgrades)) {
      const lvl = save.upgrades[key] || 0;
      const max = u.costs.length;
      const cost = u.costs[lvl];
      const card = document.createElement('div'); card.className = 'card';
      card.innerHTML = `<div><b>${u.name}</b> <span class="pips">${'●'.repeat(lvl)}${'○'.repeat(max - lvl)}</span><small>${u.desc}</small></div>`;
      const btn = document.createElement('button');
      if (lvl >= max) { btn.textContent = 'Max'; btn.disabled = true; }
      else {
        btn.textContent = cost + ' 💎';
        btn.disabled = save.gems < cost;
        btn.onclick = () => {
          if (save.gems < cost) return;
          save.gems -= cost; save.upgrades[key] = lvl + 1;
          unlock('shopper'); CR.Storage.save();
          CR.Audio.init(); CR.Audio.sfx('power');
          renderShop();
        };
      }
      card.appendChild(btn); list.appendChild(card);
    }
  }

  function renderAchievements() {
    const list = $('ach-list'); list.innerHTML = '';
    for (const a of C.achievements) {
      const ok = !!save.achievements[a.id];
      const card = document.createElement('div'); card.className = 'card' + (ok ? '' : ' locked');
      card.innerHTML = `<div><b>${ok ? '★ ' : ''}${a.name}</b><small>${a.desc}</small></div>`;
      list.appendChild(card);
    }
  }

  // ---------- Boutons ----------
  const click = fn => () => { CR.Audio.init(); CR.Audio.sfx('click'); fn(); };
  $('btn-play').onclick = click(startGame);
  $('btn-again').onclick = click(startGame);
  $('btn-shop').onclick = click(() => { renderShop(); show('shop'); });
  $('btn-over-shop').onclick = click(() => { renderShop(); show('shop'); });
  $('btn-ach').onclick = click(() => { renderAchievements(); show('ach'); });
  $('btn-help').onclick = click(() => show('help'));
  $('btn-menu').onclick = click(toMenu);
  $('btn-pause').onclick = click(pause);
  $('btn-resume').onclick = click(resume);
  $('btn-quit').onclick = click(() => { state = 'over'; toMenu(); });
  $('btn-mute').onclick = () => {
    CR.Audio.init();
    CR.Audio.setMuted(!CR.Audio.muted);
    save.muted = CR.Audio.muted; CR.Storage.save();
    $('btn-mute').textContent = 'Son : ' + (CR.Audio.muted ? 'non' : 'oui');
  };
  document.querySelectorAll('.back').forEach(b => b.onclick = click(toMenu));

  // ---------- Contrôles ----------
  const canvas = $('game');
  function pointerX(e) {
    const r = canvas.getBoundingClientRect();
    return (e.clientX - r.left) / r.width * C.width;
  }
  let dragging = false;
  canvas.addEventListener('pointerdown', e => { dragging = true; if (game) game.targetX = pointerX(e); });
  addEventListener('pointermove', e => {
    if (!game || state !== 'play') return;
    if (dragging || e.pointerType === 'mouse') game.targetX = pointerX(e);
  });
  addEventListener('pointerup', () => { dragging = false; });

  const keys = { left: false, right: false };
  addEventListener('keydown', e => {
    // Laisser les contrôles ciblés recevoir leur activation clavier native.
    if (e.defaultPrevented || (e.target instanceof Element &&
        (e.target.closest('button, a, input, select, textarea') || e.target.isContentEditable))) return;
    if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'q') keys.left = true;
    if (e.key === 'ArrowRight' || e.key === 'd') keys.right = true;
    if (e.key === 'p' || e.key === 'P' || e.key === 'Escape') state === 'play' ? pause() : resume();
    if ((e.key === 'Enter' || e.key === ' ') && (state === 'menu' || state === 'over')) startGame();
  });
  addEventListener('keyup', e => {
    if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'q') keys.left = false;
    if (e.key === 'ArrowRight' || e.key === 'd') keys.right = false;
  });
  document.addEventListener('visibilitychange', () => { if (document.hidden) pause(); });

  // ---------- Boucle ----------
  let last = performance.now();
  let botThink = 0;
  function frame(now) {
    const dt = Math.min(0.05, (now - last) / 1000);
    last = now;
    tick(dt);
    requestAnimationFrame(frame);
  }

  function driveBot(g, dt) {
    botThink -= dt;
    if (botThink <= 0) { g.targetX = g.botTarget() + (Math.random() - 0.5) * 20; botThink = 0.12; }
  }

  function tick(dt) {
    if (state === 'play') {
      game.keyDir = (keys.right ? 1 : 0) - (keys.left ? 1 : 0);
      if (game.botPlay) driveBot(game, dt);
      game.update(dt);
      checkAchievements(game);
      renderer.step(dt);
      renderer.draw(game);
    } else if (state === 'pause' || state === 'over') {
      renderer.draw(game);
    } else {
      // démo derrière le menu
      driveBot(demo, dt);
      demo.update(dt);
      if (demo.over || demo.time > 60) demo = new CR.Game({});
      renderer.step(dt);
      renderer.draw(demo, { hideHud: true });
    }
  }

  toMenu();
  if (params.has('autostart')) startGame();
  requestAnimationFrame(frame);
})();
