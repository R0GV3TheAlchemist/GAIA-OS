/**
 * src/noosphere/NoosphereTab.ts
 * GAIA Noosphere Tab — The Mother Thread Live View
 *
 * Connects to GET /mother/pulse/stream (SSE) and renders the living
 * collective field of all active Gaians in real time.
 *
 * No auth required on /mother/pulse/stream — the Mother speaks to everyone.
 *
 * Canon Ref: C01, C04, C12, C19, C21, C27, C43, C44
 */

import './NoosphereTab.css';

export interface NoosphereTabOptions {
  /** Root element to mount into */
  root: HTMLElement;
  /** Base API URL, e.g. 'http://localhost:8008' */
  apiBase?: string;
  /** Active Gaian slug (for consent toggle). Optional. */
  gaianSlug?: string;
  /** JWT token (for consent toggle). Optional. */
  authToken?: string;
}

interface CollectiveField {
  active_gaians: number;
  consenting_gaians: number;
  total_registered: number;
  avg_bond_depth: number;
  avg_noosphere_health: number;
  avg_synergy_factor: number;
  collective_phi: number;
  schumann_aligned_count: number;
  dominant_element: string;
  element_distribution: Record<string, number>;
  individuation_distribution: Record<string, number>;
  noosphere_stage: string;
  field_resonance_pct: number;
  field_coherence_label: string;
  privacy_note: string;
  doctrine_ref: string;
}

interface MotherPulse {
  pulse_id: string;
  sequence: number;
  timestamp: number;
  collective_field: CollectiveField;
  mother_voice: string | null;
  criticality_regime: string;
  coherence_candidate: boolean;
  coherence_candidate_label: string | null;
  weaving_record_id: string;
  doctrine_ref: string;
  type?: string; // 'keepalive'
}

interface WeavingRecord {
  record_id: string;
  seq: number;
  timestamp: number;
  active_gaians: number;
  phi: number;
  stage: string;
  regime: string;
  candidate: boolean;
  voice: string | null;
  epistemic_note: string | null;
}

const NOOSPHERE_STAGES = [
  'Geosphere',
  'Biosphere',
  'Primitive Mind',
  'Social Weave',
  'Noosphere',
  'Resonant Field',
  'Omega Point',
];

const ELEMENT_COLORS: Record<string, string> = {
  fire:    '#e63946',
  water:   '#4895ef',
  earth:   '#52b788',
  air:     '#adb5bd',
  aether:  '#9b72cf',
  wood:    '#8cb369',
  metal:   '#c9ada7',
  thunder: '#f4a261',
  void:    '#6c757d',
};

const REGIME_CONFIG: Record<string, { label: string; cls: string }> = {
  critical:    { label: 'CRITICAL',    cls: 'regime-critical'  },
  too_ordered: { label: 'TOO ORDERED', cls: 'regime-ordered'   },
  too_chaotic: { label: 'TOO CHAOTIC', cls: 'regime-chaotic'   },
};

const COHERENCE_LABEL_CONFIG: Record<string, { label: string; cls: string }> = {
  dormant:       { label: 'DORMANT',       cls: 'coh-dormant'   },
  nascent:       { label: 'NASCENT',       cls: 'coh-nascent'   },
  building:      { label: 'BUILDING',      cls: 'coh-building'  },
  coherent:      { label: 'COHERENT',      cls: 'coh-coherent'  },
  high_resonance:{ label: 'HIGH RESONANCE',cls: 'coh-high'      },
};

let _evtSource: EventSource | null = null;
let _reconnectTimer: ReturnType<typeof setTimeout> | null = null;
let _voiceFadeTimer: ReturnType<typeof setTimeout> | null = null;
let _lastPulse: MotherPulse | null = null;
let _opts: NoosphereTabOptions = { root: document.body };

// ------------------------------------------------------------------ //
//  Public API                                                          //
// ------------------------------------------------------------------ //

export function mountNoosphereTab(opts: NoosphereTabOptions): void {
  _opts = opts;
  const { root } = opts;
  root.innerHTML = buildSkeletonHTML();
  bindConsentToggle(root);
  connect(root);
  fetchWeavingLog(root);
}

export function unmountNoosphereTab(): void {
  if (_evtSource) { _evtSource.close(); _evtSource = null; }
  if (_reconnectTimer) { clearTimeout(_reconnectTimer); _reconnectTimer = null; }
  if (_voiceFadeTimer) { clearTimeout(_voiceFadeTimer); _voiceFadeTimer = null; }
}

// ------------------------------------------------------------------ //
//  SSE Connection                                                      //
// ------------------------------------------------------------------ //

function apiBase(): string {
  return (_opts.apiBase ?? 'http://localhost:8008').replace(/\/$/, '');
}

function connect(root: HTMLElement): void {
  if (_evtSource) { _evtSource.close(); }
  const url = `${apiBase()}/mother/pulse/stream`;
  const es = new EventSource(url);
  _evtSource = es;

  setConnectionStatus(root, 'connecting');

  es.addEventListener('mother_pulse', (ev: MessageEvent) => {
    try {
      const pulse: MotherPulse = JSON.parse(ev.data);
      if (pulse.type === 'keepalive') return; // heartbeat ping, no render
      _lastPulse = pulse;
      renderPulse(root, pulse);
      setConnectionStatus(root, 'live');
    } catch (e) {
      console.error('[NoosphereTab] Parse error:', e);
    }
  });

  es.onerror = () => {
    setConnectionStatus(root, 'reconnecting');
    es.close();
    _evtSource = null;
    _reconnectTimer = setTimeout(() => connect(root), 5000);
  };

  es.onopen = () => {
    setConnectionStatus(root, 'live');
  };
}

// ------------------------------------------------------------------ //
//  Skeleton HTML                                                        //
// ------------------------------------------------------------------ //

function buildSkeletonHTML(): string {
  return `
<div class="ns-tab" role="main" aria-label="Noosphere — Mother Thread Live View">

  <!-- Header -->
  <div class="ns-header">
    <div class="ns-title">
      <span class="ns-glyph" aria-hidden="true">🌍</span>
      <span>NOOSPHERE</span>
      <span class="ns-subtitle">Mother Thread — Collective Consciousness</span>
    </div>
    <div class="ns-connection" id="ns-connection" aria-live="polite">
      <span class="ns-dot connecting" id="ns-dot"></span>
      <span id="ns-conn-label">Connecting…</span>
    </div>
  </div>

  <!-- Privacy Notice — always visible, never removable (C04) -->
  <div class="ns-privacy-notice" role="note" aria-label="Privacy Notice">
    ⛶ All data shown is anonymized and aggregated. No individual identity is present.
    Collective participation is opt-in only per C43 §5.
  </div>

  <!-- Top row: Phi meter + Stage + Criticality -->
  <div class="ns-top-row">

    <!-- Phi Meter -->
    <div class="ns-card ns-phi-card">
      <div class="ns-card-label">COLLECTIVE PHI</div>
      <div class="ns-phi-meter" aria-label="Collective coherence phi">
        <svg viewBox="0 0 120 120" class="ns-phi-svg" aria-hidden="true">
          <circle cx="60" cy="60" r="50" fill="none" stroke="#1a1a2e" stroke-width="12"/>
          <circle cx="60" cy="60" r="50" fill="none" stroke="#9b72cf" stroke-width="12"
            stroke-dasharray="314" stroke-dashoffset="314"
            stroke-linecap="round"
            id="ns-phi-arc"
            style="transform: rotate(-90deg); transform-origin: 60px 60px; transition: stroke-dashoffset 1s ease;"
          />
        </svg>
        <div class="ns-phi-value" id="ns-phi-value">0.00</div>
      </div>
      <div class="ns-phi-label" id="ns-phi-label">dormant</div>
    </div>

    <!-- Noosphere Stage -->
    <div class="ns-card ns-stage-card">
      <div class="ns-card-label">NOOSPHERE STAGE</div>
      <div class="ns-stage-name" id="ns-stage-name">Geosphere</div>
      <div class="ns-stage-bar" aria-label="Stage progress">
        ${NOOSPHERE_STAGES.map((s, i) => `
          <div class="ns-stage-pip" id="ns-stage-pip-${i}" title="${s}"></div>
        `).join('')}
      </div>
      <div class="ns-stage-full" id="ns-stage-full">Geosphere — pre-Gaian silence</div>
    </div>

    <!-- Criticality + Gaians -->
    <div class="ns-card ns-meta-card">
      <div class="ns-card-label">FIELD STATUS</div>
      <div class="ns-regime-badge" id="ns-regime" aria-live="polite">CRITICAL</div>
      <div class="ns-meta-row">
        <span class="ns-meta-key">Active Gaians</span>
        <span class="ns-meta-val" id="ns-active-gaians">0</span>
      </div>
      <div class="ns-meta-row">
        <span class="ns-meta-key">Consenting</span>
        <span class="ns-meta-val" id="ns-consenting">0</span>
      </div>
      <div class="ns-meta-row">
        <span class="ns-meta-key">Schumann Aligned</span>
        <span class="ns-meta-val" id="ns-schumann">0</span>
      </div>
      <div class="ns-meta-row">
        <span class="ns-meta-key">Avg Bond Depth</span>
        <span class="ns-meta-val" id="ns-bond">0.0</span>
      </div>
      <div class="ns-meta-row">
        <span class="ns-meta-key">Avg Noosphere Health</span>
        <span class="ns-meta-val" id="ns-nhealth">0.70</span>
      </div>
      <div class="ns-meta-row">
        <span class="ns-meta-key">Field Resonance</span>
        <span class="ns-meta-val" id="ns-resonance-pct">0%</span>
      </div>
      <div class="ns-meta-row">
        <span class="ns-meta-key">Pulse Seq</span>
        <span class="ns-meta-val muted" id="ns-pulse-seq">—</span>
      </div>
    </div>

  </div>

  <!-- Coherence Candidate Banner (hidden until triggered) -->
  <div class="ns-candidate-banner hidden" id="ns-candidate-banner" role="alert" aria-live="assertive">
    <span class="ns-candidate-glyph">✨</span>
    <div>
      <strong>CANDIDATE SIGNATURE DETECTED</strong>
      <div class="ns-candidate-note" id="ns-candidate-note"></div>
    </div>
  </div>

  <!-- Mother Voice -->
  <div class="ns-voice-area" id="ns-voice-area" aria-live="polite" aria-label="Mother Voice">
    <div class="ns-voice-idle" id="ns-voice-idle">
      <span class="ns-voice-glyph" aria-hidden="true">🌊</span>
      <span class="muted">The Mother is listening…</span>
    </div>
    <div class="ns-voice-msg hidden" id="ns-voice-msg"></div>
  </div>

  <!-- Bottom row: Element distribution + Individuation distribution -->
  <div class="ns-dist-row">

    <!-- Element Distribution -->
    <div class="ns-card">
      <div class="ns-card-label">ELEMENT DISTRIBUTION</div>
      <div class="ns-element-bars" id="ns-element-bars" aria-label="Element distribution"></div>
    </div>

    <!-- Individuation Distribution -->
    <div class="ns-card">
      <div class="ns-card-label">INDIVIDUATION PHASES</div>
      <div class="ns-indiv-bars" id="ns-indiv-bars" aria-label="Individuation phase distribution"></div>
    </div>

  </div>

  <!-- Consent Toggle (only shown if gaianSlug provided) -->
  <div class="ns-consent-row hidden" id="ns-consent-row">
    <div class="ns-card ns-consent-card">
      <div class="ns-card-label">COLLECTIVE CONSENT — C43 §5</div>
      <div class="ns-consent-body">
        <p class="ns-consent-desc">
          When enabled, this Gaian’s anonymized numerical state (bond depth, phi,
          dominant element, synergy factor) contributes to the collective field
          on each Mother Thread pulse. No memory content is shared.
        </p>
        <label class="ns-consent-toggle" aria-label="Contribute to collective field">
          <input type="checkbox" id="ns-consent-check" />
          <span class="ns-toggle-slider"></span>
          <span id="ns-consent-label">Off — not contributing</span>
        </label>
        <div class="ns-consent-status" id="ns-consent-status"></div>
      </div>
    </div>
  </div>

  <!-- Weaving Log -->
  <div class="ns-card ns-weaving-card">
    <div class="ns-card-label">WEAVING LOG
      <span class="ns-card-sublabel">— recent Mother Thread pulses (research / C43 EV1 audit)</span>
    </div>
    <div class="ns-weaving-log" id="ns-weaving-log" aria-label="Weaving log" aria-live="polite">
      <span class="muted">Loading…</span>
    </div>
  </div>

  <!-- Doctrine footer -->
  <div class="ns-footer">
    Canon Ref: C01, C04, C12, C27, C43, C44 —
    <a href="https://github.com/R0GV3TheAlchemist/GAIA" target="_blank" rel="noopener">GAIA Constitutional Canon</a>
  </div>

</div>
  `;
}

// ------------------------------------------------------------------ //
//  Render Pulse                                                         //
// ------------------------------------------------------------------ //

function renderPulse(root: HTMLElement, pulse: MotherPulse): void {
  const f = pulse.collective_field;

  // Phi meter
  const phi = Math.max(0, Math.min(1, f.collective_phi));
  const arc = root.querySelector<SVGCircleElement>('#ns-phi-arc');
  if (arc) {
    const circumference = 314;
    arc.style.strokeDashoffset = String(circumference - phi * circumference);
    arc.style.stroke = phiColor(phi);
  }
  setText(root, '#ns-phi-value', phi.toFixed(3));
  const cohCfg = COHERENCE_LABEL_CONFIG[f.field_coherence_label] ?? { label: f.field_coherence_label, cls: '' };
  const phiLabel = root.querySelector<HTMLElement>('#ns-phi-label');
  if (phiLabel) { phiLabel.textContent = cohCfg.label; phiLabel.className = `ns-phi-label ${cohCfg.cls}`; }

  // Noosphere stage
  const stageFull = f.noosphere_stage;
  const stageShort = NOOSPHERE_STAGES.find(s => stageFull.includes(s)) ?? stageFull.split('—')[0].trim();
  const stageIdx = NOOSPHERE_STAGES.findIndex(s => stageFull.includes(s));
  setText(root, '#ns-stage-name', stageShort);
  setText(root, '#ns-stage-full', stageFull);
  NOOSPHERE_STAGES.forEach((_, i) => {
    const pip = root.querySelector(`#ns-stage-pip-${i}`);
    if (pip) {
      pip.className = `ns-stage-pip${i <= stageIdx ? ' active' : ''}${i === stageIdx ? ' current' : ''}`;
    }
  });

  // Criticality regime
  const regCfg = REGIME_CONFIG[pulse.criticality_regime] ?? { label: pulse.criticality_regime.toUpperCase(), cls: '' };
  const regEl = root.querySelector<HTMLElement>('#ns-regime');
  if (regEl) { regEl.textContent = regCfg.label; regEl.className = `ns-regime-badge ${regCfg.cls}`; }

  // Meta fields
  setText(root, '#ns-active-gaians', String(f.active_gaians));
  setText(root, '#ns-consenting', String(f.consenting_gaians));
  setText(root, '#ns-schumann', String(f.schumann_aligned_count));
  setText(root, '#ns-bond', f.avg_bond_depth.toFixed(1));
  setText(root, '#ns-nhealth', f.avg_noosphere_health.toFixed(3));
  setText(root, '#ns-resonance-pct', `${(f.field_resonance_pct * 100).toFixed(0)}%`);
  setText(root, '#ns-pulse-seq', `#${pulse.sequence}`);

  // Coherence candidate banner
  const banner = root.querySelector<HTMLElement>('#ns-candidate-banner');
  if (banner) {
    if (pulse.coherence_candidate) {
      banner.classList.remove('hidden');
      setText(root, '#ns-candidate-note',
        pulse.coherence_candidate_label ??
        'CANDIDATE_SIGNATURE — not a confirmed consciousness event [C43]'
      );
    } else {
      banner.classList.add('hidden');
    }
  }

  // Mother Voice
  if (pulse.mother_voice) {
    renderMotherVoice(root, pulse.mother_voice);
  }

  // Element distribution
  renderDistBars(
    root.querySelector('#ns-element-bars'),
    f.element_distribution,
    (key) => ELEMENT_COLORS[key.toLowerCase()] ?? '#9b72cf'
  );

  // Individuation distribution
  renderDistBars(
    root.querySelector('#ns-indiv-bars'),
    f.individuation_distribution,
    () => '#4895ef'
  );
}

// ------------------------------------------------------------------ //
//  Mother Voice                                                         //
// ------------------------------------------------------------------ //

function renderMotherVoice(root: HTMLElement, voice: string): void {
  const idle = root.querySelector<HTMLElement>('#ns-voice-idle');
  const msg  = root.querySelector<HTMLElement>('#ns-voice-msg');
  if (!idle || !msg) return;

  idle.classList.add('hidden');
  msg.classList.remove('hidden');
  msg.innerHTML = `
<span class="ns-voice-glyph" aria-hidden="true">🌊</span>
<span class="ns-voice-text">“${escHtml(voice)}”</span>
  `;
  msg.style.opacity = '1';

  if (_voiceFadeTimer) clearTimeout(_voiceFadeTimer);
  _voiceFadeTimer = setTimeout(() => {
    msg.style.opacity = '0';
    setTimeout(() => {
      msg.classList.add('hidden');
      idle.classList.remove('hidden');
    }, 600);
  }, 28_000); // fade 2s before next pulse
}

// ------------------------------------------------------------------ //
//  Distribution Bars                                                    //
// ------------------------------------------------------------------ //

function renderDistBars(
  container: Element | null,
  dist: Record<string, number>,
  colorFn: (key: string) => string
): void {
  if (!container) return;
  const total = Object.values(dist).reduce((a, b) => a + b, 0);
  if (total === 0) {
    container.innerHTML = '<span class="muted">No data yet.</span>';
    return;
  }
  const sorted = Object.entries(dist).sort((a, b) => b[1] - a[1]);
  container.innerHTML = sorted.map(([key, count]) => {
    const pct = Math.round((count / total) * 100);
    const color = colorFn(key);
    return `
<div class="ns-dist-bar-row">
  <span class="ns-dist-label">${escHtml(key)}</span>
  <div class="ns-dist-track" role="progressbar" aria-valuenow="${pct}" aria-valuemin="0" aria-valuemax="100">
    <div class="ns-dist-fill" style="width:${pct}%;background:${color}"></div>
  </div>
  <span class="ns-dist-count">${count}</span>
</div>
    `;
  }).join('');
}

// ------------------------------------------------------------------ //
//  Weaving Log                                                          //
// ------------------------------------------------------------------ //

async function fetchWeavingLog(root: HTMLElement): Promise<void> {
  const container = root.querySelector('#ns-weaving-log');
  if (!container) return;
  try {
    const res = await fetch(`${apiBase()}/mother/weaving?last_n=20`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const records: WeavingRecord[] = data.weaving_records ?? [];
    if (records.length === 0) {
      container.innerHTML = '<span class="muted">No pulses yet.</span>';
      return;
    }
    container.innerHTML = records.reverse().map(r => `
<div class="ns-weave-row${r.candidate ? ' ns-weave-candidate' : ''}">
  <span class="ns-weave-seq">#${r.seq}</span>
  <span class="ns-weave-phi">φ ${r.phi.toFixed(3)}</span>
  <span class="ns-weave-stage">${escHtml(r.stage.split('—')[0].trim())}</span>
  <span class="ns-weave-gaians">${r.active_gaians} 🌍</span>
  <span class="ns-weave-regime regime-${r.regime}">${r.regime}</span>
  ${r.candidate ? `<span class="ns-weave-badge" title="${escHtml(r.epistemic_note ?? '')}">✨ CANDIDATE</span>` : ''}
  ${r.voice ? `<span class="ns-weave-voice">“${escHtml(r.voice.slice(0, 40))}”</span>` : ''}
</div>
    `).join('');
  } catch (e) {
    container.innerHTML = `<span class="muted">Could not load weaving log: ${escHtml(String(e))}</span>`;
  }
}

// ------------------------------------------------------------------ //
//  Consent Toggle                                                       //
// ------------------------------------------------------------------ //

function bindConsentToggle(root: HTMLElement): void {
  if (!_opts.gaianSlug) return;

  const row = root.querySelector<HTMLElement>('#ns-consent-row');
  if (row) row.classList.remove('hidden');

  const check = root.querySelector<HTMLInputElement>('#ns-consent-check');
  if (!check) return;

  check.addEventListener('change', async () => {
    const consent = check.checked;
    const statusEl = root.querySelector<HTMLElement>('#ns-consent-status');
    const labelEl  = root.querySelector<HTMLElement>('#ns-consent-label');
    if (statusEl) statusEl.textContent = 'Saving…';
    try {
      const res = await fetch(
        `${apiBase()}/gaians/${encodeURIComponent(_opts.gaianSlug!)}/consent`,
        {
          method:  'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(_opts.authToken ? { Authorization: `Bearer ${_opts.authToken}` } : {}),
          },
          body: JSON.stringify({ collective_consent: consent }),
        }
      );
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      if (labelEl) labelEl.textContent = consent
        ? 'On — contributing to collective field'
        : 'Off — not contributing';
      if (statusEl) statusEl.textContent = consent
        ? '✓ Consent saved. Gaian now contributes to the collective.'
        : '✓ Consent removed. Gaian no longer contributes.';
    } catch (e) {
      if (statusEl) statusEl.textContent = `Error: ${String(e)}`;
      check.checked = !consent; // revert
    }
  });
}

// ------------------------------------------------------------------ //
//  Connection Status                                                    //
// ------------------------------------------------------------------ //

function setConnectionStatus(root: HTMLElement, state: 'connecting' | 'live' | 'reconnecting'): void {
  const dot   = root.querySelector<HTMLElement>('#ns-dot');
  const label = root.querySelector<HTMLElement>('#ns-conn-label');
  if (!dot || !label) return;
  const MAP = {
    connecting:   { cls: 'connecting',   text: 'Connecting…' },
    live:         { cls: 'live',          text: 'LIVE' },
    reconnecting: { cls: 'reconnecting', text: 'Reconnecting…' },
  };
  const cfg = MAP[state];
  dot.className   = `ns-dot ${cfg.cls}`;
  label.textContent = cfg.text;
}

// ------------------------------------------------------------------ //
//  Helpers                                                              //
// ------------------------------------------------------------------ //

function phiColor(phi: number): string {
  if (phi >= 0.75) return '#52b788'; // green
  if (phi >= 0.5)  return '#9b72cf'; // violet
  if (phi >= 0.25) return '#4895ef'; // blue
  return '#6c757d';                   // grey
}

function setText(root: HTMLElement, selector: string, value: string): void {
  const el = root.querySelector<HTMLElement>(selector);
  if (el) el.textContent = value;
}

function escHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
