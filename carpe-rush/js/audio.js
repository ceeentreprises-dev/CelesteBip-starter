// Carpe Rush – sons et musique générés par le navigateur (aucun fichier audio).
(function (root) {
  const CR = root.CR || (root.CR = {});

  CR.Audio = {
    ctx: null, master: null, musicGain: null, muted: false, musicTimer: null, step: 0,

    init() {
      if (this.ctx) { if (this.ctx.state === 'suspended') this.ctx.resume(); return; }
      const AC = root.AudioContext || root.webkitAudioContext;
      if (!AC) return;
      this.ctx = new AC();
      // Bus principal avec compresseur : évite la saturation quand les sons s'empilent
      const comp = this.ctx.createDynamicsCompressor();
      comp.threshold.value = -14; comp.ratio.value = 6;
      this.master = this.ctx.createGain();
      this.master.gain.value = this.muted ? 0 : 0.6;
      this.master.connect(comp); comp.connect(this.ctx.destination);
      this.musicGain = this.ctx.createGain();
      this.musicGain.gain.value = 0.18;
      this.musicGain.connect(this.master);
    },

    setMuted(m) {
      this.muted = m;
      if (this.master) this.master.gain.value = m ? 0 : 0.6;
    },

    tone(freq, dur, type = 'sine', vol = 0.3, slide = 0, dest) {
      if (!this.ctx) return;
      const t = this.ctx.currentTime;
      const o = this.ctx.createOscillator(), g = this.ctx.createGain();
      o.type = type;
      o.frequency.setValueAtTime(freq, t);
      if (slide) o.frequency.exponentialRampToValueAtTime(Math.max(30, freq + slide), t + dur);
      g.gain.setValueAtTime(vol, t);
      g.gain.exponentialRampToValueAtTime(0.001, t + dur);
      o.connect(g); g.connect(dest || this.master);
      o.start(t); o.stop(t + dur + 0.02);
    },

    noise(dur, vol = 0.4) {
      if (!this.ctx) return;
      const len = Math.floor(this.ctx.sampleRate * dur);
      const buf = this.ctx.createBuffer(1, len, this.ctx.sampleRate);
      const d = buf.getChannelData(0);
      for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * (1 - i / len);
      const s = this.ctx.createBufferSource(), g = this.ctx.createGain();
      const f = this.ctx.createBiquadFilter(); f.type = 'lowpass'; f.frequency.value = 900;
      s.buffer = buf; g.gain.value = vol;
      s.connect(f); f.connect(g); g.connect(this.master); s.start();
    },

    sfx(type, data = {}) {
      switch (type) {
        case 'gold': {
          const n = Math.min(data.combo || 0, 24);
          this.tone(660 * Math.pow(2, n / 24), 0.12, 'triangle', 0.25);
          if (data.big) this.tone(990, 0.2, 'sine', 0.2, 300);
          break;
        }
        case 'hit': this.noise(0.35, 0.5); this.tone(180, 0.3, 'sawtooth', 0.2, -120); break;
        case 'block': this.tone(400, 0.15, 'square', 0.15, 400); break;
        case 'power': this.tone(520, 0.1, 'sine', 0.25); setTimeout(() => this.tone(780, 0.18, 'sine', 0.25), 90); break;
        case 'level': [523, 659, 784, 1046].forEach((f, i) => setTimeout(() => this.tone(f, 0.15, 'triangle', 0.22), i * 80)); break;
        case 'over': [392, 330, 262].forEach((f, i) => setTimeout(() => this.tone(f, 0.3, 'triangle', 0.25), i * 160)); break;
        case 'click': this.tone(880, 0.05, 'square', 0.1); break;
      }
    },

    startMusic() {
      if (!this.ctx || this.musicTimer) return;
      const bass = [130.8, 130.8, 174.6, 196, 146.8, 146.8, 196, 174.6];
      const lead = [523, 0, 659, 0, 784, 659, 0, 587, 523, 0, 440, 0, 494, 0, 587, 0];
      this.step = 0;
      this.musicTimer = setInterval(() => {
        const s = this.step++;
        if (s % 2 === 0) this.tone(bass[(s / 2 | 0) % bass.length], 0.25, 'triangle', 0.5, 0, this.musicGain);
        const l = lead[s % lead.length];
        if (l) this.tone(l, 0.12, 'sine', 0.25, 0, this.musicGain);
      }, 180);
    },

    stopMusic() { clearInterval(this.musicTimer); this.musicTimer = null; },
  };
})(typeof window !== 'undefined' ? window : globalThis);
