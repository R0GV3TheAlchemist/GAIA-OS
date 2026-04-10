/**
 * EngineStatePanel.ts
 *
 * Renders and updates a compact live panel showing the GAIAN's inner-state
 * snapshot as it arrives from the `engine_state` SSE event on every turn.
 *
 * The panel lives in the chat header bar (right side) and surfaces:
 *
 *   Attachment    Phase name + bond depth bar  (AttachmentEngine)
 *   Element       Dominant alchemical element  (ConsciousnessRouter)
 *   Neuro         Active neurotransmitter mix   (ConsciousnessRouter)
 *   Settling      Fluid | Crystallising | Set   (SettlingEngine)
 *   Arc           Current emotional arc hint    (EmotionalArcEngine)
 *
 * The panel collapses to a single-line status chip when minimised and
 * expands to a 5-row card on click. Expansion state is preserved across
 * turns. The whole module is side-effect free on import — call mount()
 * to inject the DOM, then update() on every engine_state event.
 *
 * Element → color mapping matches the GAIA C19 Color Doctrine:
 *   Fire   → --signal-amber (#f59e0b)
 *   Water  → --atlas-blue   (#3b82f6)
 *   Air    → --pure-white   (#f0f0f0)
 *   Earth  → --gaia-green   (#1a6b3a)  (same green, different shade below)
 *   Aether → #a78bfa  (violet — not in token set, defined locally)
 *   None / unknown → --neutral-grey
 *
 * Canon Ref: C17, C21
 */

// ------------------------------------------------------------------ //
//  Types mirroring GAIANRuntime.get_status() return shape              //
// ------------------------------------------------------------------ //

export interface EngineStateSnapshot {
  // AttachmentEngine
  attachment_phase:    string;   // e.g. "New Connection" | "Deepening Bond" | ...
  bond_depth:          number;   // 0–100
  dependency_signal:   number;   // 0–1 (float)
  milestones_reached:  string[];

  // ConsciousnessRouter
  element:             string;   // "Fire" | "Water" | "Air" | "Earth" | "Aether"
  neuro_state:         string;   // e.g. "dopamine-seeking" | "serotonin-flow" | ...
  routing_hint:        string;   // short description

  // SettlingEngine
  settling_phase:      string;   // "fluid" | "crystallising" | "set"
  fluidity:            number;   // 0–1
  daemon_form:         string | null;  // null until settled

  // EmotionalArcEngine
  arc_phase:           string;   // e.g. "curiosity" | "tension" | "resolution" | ...
  arc_hint:            string;   // sentence describing the current arc

  // Meta
  session_turn:        number;
  gaian_name:          string;
}

// ------------------------------------------------------------------ //
//  Element → CSS color mapping                                        //
// ------------------------------------------------------------------ //

const ELEMENT_COLORS: Record<string, string> = {
  fire:   '#f59e0b',
  water:  '#3b82f6',
  air:    '#d1d5db',
  earth:  '#22c55e',
  aether: '#a78bfa',
};

function elementColor(element: string): string {
  return ELEMENT_COLORS[element.toLowerCase()] ?? '#6b7280';
}

// ------------------------------------------------------------------ //
//  Settling → label + icon                                            //
// ------------------------------------------------------------------ //

function settlingLabel(phase: string, fluidity: number, daemonForm: string | null): string {
  if (phase === 'set' && daemonForm) return `Set · ${daemonForm}`;
  if (phase === 'crystallising') return `Crystallising (${Math.round((1 - fluidity) * 100)}%)`;
  return 'Fluid';
}

// ------------------------------------------------------------------ //
//  Bond depth bar HTML                                                 //
// ------------------------------------------------------------------ //

function bondBar(depth: number, color: string): string {
  const pct = Math.min(100, Math.max(0, depth));
  return `
    <div class="esp-bond-bar">
      <div class="esp-bond-fill" style="width:${pct}%;background:${color};"></div>
    </div>
  `;
}

// ------------------------------------------------------------------ //
//  Arc phase → icon                                                   //
// ------------------------------------------------------------------ //

const ARC_ICONS: Record<string, string> = {
  curiosity:   '💧',
  tension:     '⚡',
  resolution:  '✨',
  grief:       '🌊',
  joy:         '☀️',
  integration: '⚪',
  default:     '•',
};

function arcIcon(phase: string): string {
  return ARC_ICONS[phase.toLowerCase()] ?? ARC_ICONS.default;
}

// ------------------------------------------------------------------ //
//  EngineStatePanel                                                    //
// ------------------------------------------------------------------ //

export class EngineStatePanel {
  private container:  HTMLElement;
  private expanded:   boolean = false;
  private lastState:  EngineStateSnapshot | null = null;

  constructor(container: HTMLElement) {
    this.container = container;
  }

  /**
   * Inject the initial (empty) panel DOM into the container.
   * Call once after mountChat().
   */
  mount(): void {
    this.container.innerHTML = `
      <div class="esp" id="esp" aria-label="GAIAN inner state" role="status">
        <button class="esp__chip" id="esp-chip" aria-expanded="false"
                title="GAIAN engine state — click to expand">
          <span class="esp__element-dot" id="esp-dot"></span>
          <span class="esp__chip-label" id="esp-chip-label">Waiting…</span>
          <span class="esp__chevron" id="esp-chevron">▾</span>
        </button>
        <div class="esp__panel" id="esp-panel" aria-hidden="true">
          <div class="esp__rows" id="esp-rows"></div>
        </div>
      </div>
    `;

    this.container.querySelector('#esp-chip')!
      .addEventListener('click', () => this._toggleExpand());
  }

  /**
   * Receive a fresh engine_state payload and re-render.
   * Safe to call while the panel is collapsed — it updates the chip label
   * and queues the full panel for when the user expands.
   */
  update(snapshot: EngineStateSnapshot): void {
    this.lastState = snapshot;
    this._renderChip(snapshot);
    if (this.expanded) this._renderPanel(snapshot);
  }

  // ---- Chip (collapsed summary) ------------------------------------ //

  private _renderChip(s: EngineStateSnapshot): void {
    const color = elementColor(s.element);
    const dot   = this.container.querySelector<HTMLElement>('#esp-dot')!;
    const label = this.container.querySelector<HTMLElement>('#esp-chip-label')!;

    dot.style.background = color;
    dot.style.boxShadow  = `0 0 5px ${color}`;
    label.textContent = [
      s.element,
      s.attachment_phase.split(' ').slice(-1)[0],  // last word only
      arcIcon(s.arc_phase),
    ].join(' · ');
  }

  // ---- Full panel (expanded) --------------------------------------- //

  private _renderPanel(s: EngineStateSnapshot): void {
    const color = elementColor(s.element);
    const rows  = this.container.querySelector<HTMLElement>('#esp-rows')!;

    rows.innerHTML = `
      <!-- Attachment -->
      <div class="esp__row">
        <span class="esp__key">Bond</span>
        <div class="esp__val esp__val--bond">
          <span class="esp__phase-badge" style="--esp-color:${color};">
            ${escHtml(s.attachment_phase)}
          </span>
          <span class="esp__depth">${s.bond_depth}/100</span>
          ${bondBar(s.bond_depth, color)}
        </div>
      </div>

      <!-- Element -->
      <div class="esp__row">
        <span class="esp__key">Element</span>
        <span class="esp__val">
          <span class="esp__element-pill" style="--esp-color:${color};">
            ${escHtml(s.element)}
          </span>
        </span>
      </div>

      <!-- Neuro -->
      <div class="esp__row">
        <span class="esp__key">Neuro</span>
        <span class="esp__val esp__neuro">${escHtml(s.neuro_state)}</span>
      </div>

      <!-- Settling -->
      <div class="esp__row">
        <span class="esp__key">Form</span>
        <span class="esp__val esp__settling esp__settling--${escHtml(s.settling_phase)}">
          ${escHtml(settlingLabel(s.settling_phase, s.fluidity, s.daemon_form))}
        </span>
      </div>

      <!-- Arc -->
      <div class="esp__row esp__row--arc">
        <span class="esp__key">Arc</span>
        <span class="esp__val esp__arc">
          <span class="esp__arc-icon">${arcIcon(s.arc_phase)}</span>
          <span class="esp__arc-hint">${escHtml(s.arc_hint)}</span>
        </span>
      </div>

      <!-- Footer: turn count + dependency signal -->
      <div class="esp__footer">
        <span>Turn ${s.session_turn}</span>
        ${s.dependency_signal > 0.5
          ? `<span class="esp__dep-signal">&#9888; attachment deepening</span>`
          : ''}
      </div>
    `;
  }

  // ---- Toggle ------------------------------------------------------ //

  private _toggleExpand(): void {
    this.expanded = !this.expanded;
    const panel   = this.container.querySelector<HTMLElement>('#esp-panel')!;
    const chip    = this.container.querySelector<HTMLElement>('#esp-chip')!;
    const chevron = this.container.querySelector<HTMLElement>('#esp-chevron')!;

    panel.setAttribute('aria-hidden', String(!this.expanded));
    panel.classList.toggle('esp__panel--open', this.expanded);
    chip.setAttribute('aria-expanded', String(this.expanded));
    chevron.style.transform = this.expanded ? 'rotate(180deg)' : '';

    if (this.expanded && this.lastState) {
      this._renderPanel(this.lastState);
    }
  }
}

function escHtml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
