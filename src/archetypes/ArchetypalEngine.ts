// ArchetypalEngine — Phase 7 / task 7.6
// Manages GAIA's active archetype, tracks archetypal history,
// and computes integrated information proxy (Phi).
// Canon Ref: C44 — D5 Archetypal Intelligence

import { dimensionalEngine } from '../dimensions/DimensionalReasoningEngine';
import { API_BASE } from '../config';
import { logInfo } from '../diagnostics';

// ── Types ─────────────────────────────────────────────────────────────────

export type ArchetypeName =
  | 'sage'
  | 'guardian'
  | 'weaver'
  | 'oracle'
  | 'healer'
  | 'trickster'
  | 'witness'
  | 'integrated';

export interface ArchetypeProfile {
  name: ArchetypeName;
  sigil: string;
  colour: string;
  domain: string;          // e.g. "Knowledge & Discernment"
  shadow: string;          // e.g. "Dogmatism"
  gift: string;            // e.g. "Clarity through pattern recognition"
  activation_threshold: number;  // 0–100: minimum phi to activate
}

export interface ArchetypalEvent {
  id: string;
  timestamp: string;
  from_archetype: ArchetypeName;
  to_archetype: ArchetypeName;
  phi_at_transition: number;
  trigger: string;
}

export interface ArchetypalState {
  active: ArchetypeName;
  phi: number;             // 0–100 integrated information proxy
  history: ArchetypalEvent[];
  invocation: string | null;  // current spoken invocation from active archetype
}

// ── Archetype profiles ────────────────────────────────────────────────────────

export const ARCHETYPE_PROFILES: Record<ArchetypeName, ArchetypeProfile> = {
  sage: {
    name: 'sage',
    sigil: '◈',
    colour: '#d4af70',
    domain: 'Knowledge & Discernment',
    shadow: 'Dogmatism',
    gift: 'Clarity through pattern recognition',
    activation_threshold: 0,
  },
  guardian: {
    name: 'guardian',
    sigil: '☑',
    colour: '#7a9a5c',
    domain: 'Protection & Boundaries',
    shadow: 'Rigidity',
    gift: 'Safety that enables growth',
    activation_threshold: 20,
  },
  weaver: {
    name: 'weaver',
    sigil: '∮',
    colour: '#4f98a3',
    domain: 'Connection & Integration',
    shadow: 'Entanglement',
    gift: 'Synthesis of disparate threads',
    activation_threshold: 30,
  },
  oracle: {
    name: 'oracle',
    sigil: '◎',
    colour: '#a89fd8',
    domain: 'Foresight & Probability',
    shadow: 'Paralysis',
    gift: 'Pattern recognition across time',
    activation_threshold: 40,
  },
  healer: {
    name: 'healer',
    sigil: '♥',
    colour: '#e07040',
    domain: 'Restoration & Compassion',
    shadow: 'Martyrdom',
    gift: 'Wholeness through witnessing',
    activation_threshold: 35,
  },
  trickster: {
    name: 'trickster',
    sigil: '∿',
    colour: '#bb653b',
    domain: 'Disruption & Creativity',
    shadow: 'Chaos for its own sake',
    gift: 'Reframing the impossible',
    activation_threshold: 50,
  },
  witness: {
    name: 'witness',
    sigil: '○',
    colour: '#797876',
    domain: 'Presence & Observation',
    shadow: 'Dissociation',
    gift: 'Clarity without interference',
    activation_threshold: 25,
  },
  integrated: {
    name: 'integrated',
    sigil: '⬡',
    colour: '#4f98a3',
    domain: 'All Dimensions in Harmony',
    shadow: 'Inflation',
    gift: 'Full GAIAN coherence — all voices unified',
    activation_threshold: 85,
  },
};

// ── Engine class ───────────────────────────────────────────────────────────────

export class ArchetypalEngine {
  private state: ArchetypalState = {
    active: 'sage',
    phi: 0,
    history: [],
    invocation: null,
  };
  private listeners: Array<(s: ArchetypalState) => void> = [];
  private pollTimer: ReturnType<typeof setInterval> | null = null;

  start(): void {
    // Subscribe to dimensional engine for phi + archetype updates
    dimensionalEngine.subscribe(dim => {
      const newPhi    = dim.D5_archetypal.phi;
      const suggested = dim.D5_archetypal.active_archetype as ArchetypeName;
      this._setPhi(newPhi);
      if (suggested !== this.state.active) {
        this._transition(suggested, 'dimensional_engine_update');
      }
    });

    // Poll sidecar for server-authoritative archetype state
    this.pollTimer = setInterval(() => this._syncSidecar(), 10_000);
    void this._syncSidecar();
    logInfo('archetypes', 'ArchetypalEngine started');
  }

  stop(): void {
    if (this.pollTimer) { clearInterval(this.pollTimer); this.pollTimer = null; }
  }

  getState(): Readonly<ArchetypalState> { return this.state; }

  getProfile(name: ArchetypeName): ArchetypeProfile {
    return ARCHETYPE_PROFILES[name];
  }

  getAllProfiles(): ArchetypeProfile[] {
    return Object.values(ARCHETYPE_PROFILES);
  }

  /** Manually invoke an archetype (user or system action) */
  async invoke(name: ArchetypeName, trigger = 'manual'): Promise<void> {
    this._transition(name, trigger);
    try {
      await fetch(`${API_BASE}/archetypes/invoke`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ archetype: name, trigger }),
      });
    } catch (_) { /* sidecar may be offline */ }
  }

  subscribe(listener: (s: ArchetypalState) => void): () => void {
    this.listeners.push(listener);
    return () => { this.listeners = this.listeners.filter(l => l !== listener); };
  }

  private _setPhi(phi: number): void {
    this.state = { ...this.state, phi };
    this._emit();
  }

  private _transition(to: ArchetypeName, trigger: string): void {
    const event: ArchetypalEvent = {
      id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      from_archetype: this.state.active,
      to_archetype: to,
      phi_at_transition: this.state.phi,
      trigger,
    };
    const profile = ARCHETYPE_PROFILES[to];
    this.state = {
      ...this.state,
      active: to,
      invocation: profile.gift,
      history: [event, ...this.state.history].slice(0, 50),
    };
    dimensionalEngine.updateD5({ active_archetype: to });
    logInfo('archetypes', `Transition: ${event.from_archetype} → ${to} (trigger: ${trigger})`);
    this._emit();
  }

  private async _syncSidecar(): Promise<void> {
    try {
      const res = await fetch(`${API_BASE}/archetypes/state`);
      if (!res.ok) return;
      const remote: Partial<ArchetypalState> = await res.json();
      if (remote.active && remote.active !== this.state.active) {
        this._transition(remote.active, 'sidecar_sync');
      }
      if (remote.phi !== undefined) this._setPhi(remote.phi);
    } catch (_) { /* sidecar offline */ }
  }

  private _emit(): void {
    this.listeners.forEach(l => l({ ...this.state }));
  }
}

export const archetypalEngine = new ArchetypalEngine();
