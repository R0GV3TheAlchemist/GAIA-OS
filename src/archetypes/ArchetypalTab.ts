// ArchetypalTab — Phase 7 / task 7.6
// UI panel: active archetype, invocation, phi meter, history, manual invoke.
// Canon Ref: C44 — D5 Archetypal Intelligence

import './ArchetypalTab.css';
import {
  archetypalEngine,
  ArchetypalState,
  ArchetypalEvent,
  ArchetypeName,
  ARCHETYPE_PROFILES,
} from './ArchetypalEngine';

export function mountArchetypalTab(container: HTMLElement): () => void {
  container.innerHTML = buildShell();
  renderState(container, archetypalEngine.getState());
  renderGlyphs(container);

  if (!archetypalEngine.getState().invocation) {
    archetypalEngine.start();
  }

  const unsub = archetypalEngine.subscribe(state => renderState(container, state));
  bindInvokeButtons(container);

  return () => {
    unsub();
    archetypalEngine.stop();
  };
}

// ── Shell ─────────────────────────────────────────────────────────────────

function buildShell(): string {
  return `
  <div class="at-root">
    <div class="at-header">
      <span class="at-sigil" id="at-active-sigil">◈</span>
      <div class="at-header-text">
        <h2 class="at-title">Archetypal Engine</h2>
        <p class="at-subtitle">D5 — Integrated Archetypal Intelligence</p>
      </div>
    </div>

    <!-- Active archetype hero -->
    <div class="at-hero" id="at-hero">
      <div class="at-hero-name" id="at-hero-name">sage</div>
      <div class="at-hero-domain" id="at-hero-domain">&mdash;</div>
      <div class="at-phi-row">
        <span class="at-phi-label">Φ</span>
        <div class="at-phi-track">
          <div class="at-phi-fill" id="at-phi-fill" style="width:0%"></div>
        </div>
        <span class="at-phi-value" id="at-phi-value">0.00</span>
      </div>
      <div class="at-invocation" id="at-invocation"></div>
    </div>

    <!-- Glyph wheel: all 8 archetypes -->
    <div class="at-glyph-section">
      <div class="at-section-label">Invoke Archetype</div>
      <div class="at-glyph-grid" id="at-glyph-grid"></div>
    </div>

    <!-- Stats row -->
    <div class="at-stats-row">
      <div class="at-stat">
        <span class="at-stat-label">Shadow</span>
        <span class="at-stat-value" id="at-shadow">&mdash;</span>
      </div>
      <div class="at-stat">
        <span class="at-stat-label">Threshold</span>
        <span class="at-stat-value" id="at-threshold">&mdash;</span>
      </div>
      <div class="at-stat">
        <span class="at-stat-label">Transitions</span>
        <span class="at-stat-value" id="at-transitions">0</span>
      </div>
    </div>

    <!-- Transition history -->
    <div class="at-section-label" style="margin-top:1rem">Transition History</div>
    <div class="at-history" id="at-history">
      <div class="at-history-empty">No transitions yet.</div>
    </div>
  </div>
  `;
}

// ── Render ────────────────────────────────────────────────────────────────

function renderState(container: HTMLElement, state: ArchetypalState): void {
  const profile = ARCHETYPE_PROFILES[state.active];

  // Hero
  setText(container, 'at-active-sigil', profile.sigil);
  setText(container, 'at-hero-name',    state.active);
  setText(container, 'at-hero-domain',  profile.domain);
  setText(container, 'at-invocation',   state.invocation ?? profile.gift);

  const hero = container.querySelector<HTMLElement>('#at-hero');
  if (hero) hero.style.setProperty('--archetype-colour', profile.colour);

  const sigil = container.querySelector<HTMLElement>('#at-active-sigil');
  if (sigil) sigil.style.color = profile.colour;

  // Phi meter
  const phiPct = Math.min(100, Math.max(0, state.phi));
  const fill    = container.querySelector<HTMLElement>('#at-phi-fill');
  const val     = container.querySelector<HTMLElement>('#at-phi-value');
  if (fill) fill.style.width = `${phiPct}%`;
  if (val)  val.textContent  = state.phi.toFixed(2);

  // Stats
  setText(container, 'at-shadow',    profile.shadow);
  setText(container, 'at-threshold', `Φ ≥ ${profile.activation_threshold}`);
  setText(container, 'at-transitions', String(state.history.length));

  // Glyph active state
  container.querySelectorAll<HTMLElement>('.at-glyph-btn').forEach(btn => {
    btn.classList.toggle('at-glyph-btn--active', btn.dataset.archetype === state.active);
  });

  // History
  renderHistory(container, state.history);
}

function renderGlyphs(container: HTMLElement): void {
  const grid = container.querySelector<HTMLElement>('#at-glyph-grid');
  if (!grid) return;
  grid.innerHTML = Object.values(ARCHETYPE_PROFILES).map(p => `
    <button
      class="at-glyph-btn"
      data-archetype="${p.name}"
      style="--glyph-colour:${p.colour}"
      title="${p.name} — ${p.domain}"
    >
      <span class="at-glyph-sigil">${p.sigil}</span>
      <span class="at-glyph-name">${p.name}</span>
    </button>
  `).join('');
}

function renderHistory(container: HTMLElement, history: ArchetypalEvent[]): void {
  const el = container.querySelector<HTMLElement>('#at-history');
  if (!el) return;
  if (!history.length) {
    el.innerHTML = '<div class="at-history-empty">No transitions yet.</div>';
    return;
  }
  el.innerHTML = history.slice(0, 20).map(e => {
    const from = ARCHETYPE_PROFILES[e.from_archetype];
    const to   = ARCHETYPE_PROFILES[e.to_archetype];
    const time = new Date(e.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    return `
      <div class="at-history-entry">
        <span class="at-history-from" style="color:${from.colour}">${from.sigil} ${e.from_archetype}</span>
        <span class="at-history-arrow">→</span>
        <span class="at-history-to"   style="color:${to.colour}">${to.sigil} ${e.to_archetype}</span>
        <span class="at-history-phi">  Φ${e.phi_at_transition.toFixed(1)}</span>
        <span class="at-history-time">${time}</span>
        <span class="at-history-trigger">${e.trigger}</span>
      </div>`;
  }).join('');
}

// ── Bind invoke buttons ─────────────────────────────────────────────────────────

function bindInvokeButtons(container: HTMLElement): void {
  container.addEventListener('click', async e => {
    const btn = (e.target as HTMLElement).closest<HTMLButtonElement>('.at-glyph-btn');
    if (!btn) return;
    const name = btn.dataset.archetype as ArchetypeName;
    if (!name) return;
    btn.classList.add('at-glyph-btn--invoking');
    await archetypalEngine.invoke(name, 'user_manual');
    setTimeout(() => btn.classList.remove('at-glyph-btn--invoking'), 600);
  });
}

// ── Helpers ────────────────────────────────────────────────────────────────

function setText(c: HTMLElement, id: string, text: string): void {
  const el = c.querySelector<HTMLElement>(`#${id}`);
  if (el) el.textContent = text;
}
