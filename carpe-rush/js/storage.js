// Carpe Rush – sauvegarde locale (navigateur). Ne plante jamais si le stockage est indisponible.
(function (root) {
  const CR = root.CR || (root.CR = {});
  const KEY = 'carpe-rush-save-v1';

  const defaults = () => ({
    best: 0, gems: 0, games: 0, muted: false,
    upgrades: { magnet: 0, shield: 0, slow: 0, life: 0, treasure: 0 },
    achievements: {},
  });

  CR.Storage = {
    data: defaults(),
    load() {
      try {
        const raw = root.localStorage && root.localStorage.getItem(KEY);
        if (raw) {
          const d = JSON.parse(raw);
          this.data = Object.assign(defaults(), d);
          this.data.upgrades = Object.assign(defaults().upgrades, d.upgrades || {});
        }
      } catch (e) { /* stockage bloqué : on joue sans sauvegarde */ }
      return this.data;
    },
    save() {
      try { root.localStorage && root.localStorage.setItem(KEY, JSON.stringify(this.data)); } catch (e) {}
    },
    reset() { this.data = defaults(); this.save(); },
  };
})(typeof window !== 'undefined' ? window : globalThis);
