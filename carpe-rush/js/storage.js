// Carpe Rush – sauvegarde locale (navigateur). Ne plante jamais si le stockage est indisponible.
(function (root) {
  const CR = root.CR || (root.CR = {});
  const KEY = 'carpe-rush-save-v1';

  const defaults = () => ({
    best: 0, gems: 0, games: 0, muted: false,
    upgrades: { magnet: 0, shield: 0, slow: 0, life: 0, treasure: 0 },
    achievements: {},
  });

  function boundedInteger(value, max = Number.MAX_SAFE_INTEGER) {
    return typeof value === 'number' && Number.isFinite(value)
      ? Math.max(0, Math.min(max, Math.floor(value))) : 0;
  }

  function restore(value) {
    const data = defaults();
    if (!value || typeof value !== 'object' || Array.isArray(value)) return data;
    for (const key of ['best', 'gems', 'games']) data[key] = boundedInteger(value[key]);
    data.muted = value.muted === true;
    const upgrades = value.upgrades && typeof value.upgrades === 'object' ? value.upgrades : {};
    for (const [key, definition] of Object.entries(CR.CONFIG.upgrades)) {
      data.upgrades[key] = boundedInteger(upgrades[key], definition.costs.length);
    }
    const achievements = value.achievements && typeof value.achievements === 'object'
      ? value.achievements : {};
    for (const definition of CR.CONFIG.achievements) {
      const unlockedAt = boundedInteger(achievements[definition.id]);
      if (unlockedAt > 0) data.achievements[definition.id] = unlockedAt;
    }
    return data;
  }

  CR.Storage = {
    data: defaults(),
    load() {
      this.data = defaults();
      try {
        const raw = root.localStorage && root.localStorage.getItem(KEY);
        if (raw) this.data = restore(JSON.parse(raw));
      } catch (e) { /* stockage bloqué : on joue sans sauvegarde */ }
      return this.data;
    },
    save() {
      try { root.localStorage && root.localStorage.setItem(KEY, JSON.stringify(this.data)); } catch (e) {}
    },
    reset() { this.data = defaults(); this.save(); },
  };
})(typeof window !== 'undefined' ? window : globalThis);
