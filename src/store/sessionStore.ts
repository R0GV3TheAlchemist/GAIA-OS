/**
 * src/store/sessionStore.ts
 * GAIA-OS Session Store — Cross-Crystal Coherence Data Bus.
 * Canon: C90 — Phase 4a
 *
 * All five crystals write here. Clarus reads from here.
 * This is the nervous system connecting the field.
 *
 * Coherence Score formula:
 *   - Sovereign check-ins  × 8  (max 40)
 *   - Anchor breath cycles × 6  (max 30)
 *   - Viriditas entries    × 5  (max 25)
 *   - Somnus dream logs    × 4  (max 20)
 *   - Clarus inquiries     × 7  (max 35)
 *   Total possible raw: 150 → normalized to 0–100
 */

export interface SessionState {
  /** Session open timestamp (ISO 8601) */
  sessionStart: string;

  /** Breath/grounding cycles completed in Anchor Prism */
  anchorCycles: number;

  /** Gratitude / growth journal entries saved in Viriditas Heart */
  viriditasEntries: number;

  /** Dream entries saved in Somnus Veil */
  somnusLogs: number;

  /** Full inquiry conversations completed in Clarus Lens */
  clarusInquiries: number;

  /** Sovereign Core check-ins / declarations confirmed */
  sovereignCheckins: number;

  /** Computed — sum of all meaningful interactions */
  totalInteractions: number;

  /** Computed — 0 to 100 coherence score */
  coherenceScore: number;

  /** Computed — human-readable coherence level */
  coherenceLevel: CoherenceLevel;
}

export type CoherenceLevel =
  | 'Scattered'
  | 'Settling'
  | 'Present'
  | 'Coherent'
  | 'Avatar';

export interface SessionActions {
  recordAnchorCycle:      () => void;
  recordViriditasEntry:   () => void;
  recordSomnusLog:        () => void;
  recordClarusInquiry:    () => void;
  recordSovereignCheckin: () => void;
  resetSession:           () => void;
  subscribe:              (listener: (state: SessionState) => void) => () => void;
  getSnapshot:            () => SessionState;
}

export type SessionStore = SessionState & SessionActions;

// ── Coherence weights ────────────────────────────────────────────────────

const WEIGHTS = {
  sovereign: 8,
  anchor:    6,
  viriditas: 5,
  somnus:    4,
  clarus:    7,
} as const;

const MAX_RAW = 150; // 5×sovereign + 5×anchor + 5×viriditas + 5×somnus + 5×clarus

function computeCoherence(state: Omit<SessionState, 'coherenceScore' | 'coherenceLevel' | 'totalInteractions'>): {
  coherenceScore: number;
  coherenceLevel: CoherenceLevel;
  totalInteractions: number;
} {
  const raw =
    Math.min(state.sovereignCheckins, 5) * WEIGHTS.sovereign +
    Math.min(state.anchorCycles,      5) * WEIGHTS.anchor    +
    Math.min(state.viriditasEntries,  5) * WEIGHTS.viriditas +
    Math.min(state.somnusLogs,        5) * WEIGHTS.somnus    +
    Math.min(state.clarusInquiries,   5) * WEIGHTS.clarus;

  const coherenceScore = Math.round((raw / MAX_RAW) * 100);
  const totalInteractions =
    state.sovereignCheckins +
    state.anchorCycles      +
    state.viriditasEntries  +
    state.somnusLogs        +
    state.clarusInquiries;

  let coherenceLevel: CoherenceLevel;
  if      (coherenceScore >= 85) coherenceLevel = 'Avatar';
  else if (coherenceScore >= 65) coherenceLevel = 'Coherent';
  else if (coherenceScore >= 40) coherenceLevel = 'Present';
  else if (coherenceScore >= 20) coherenceLevel = 'Settling';
  else                           coherenceLevel = 'Scattered';

  return { coherenceScore, coherenceLevel, totalInteractions };
}

// ── Store factory ────────────────────────────────────────────────────────

type Listener = (state: SessionState) => void;

function createSessionStore(): SessionStore {
  const baseState = {
    sessionStart:     new Date().toISOString(),
    anchorCycles:     0,
    viriditasEntries: 0,
    somnusLogs:       0,
    clarusInquiries:  0,
    sovereignCheckins: 0,
  };

  let state: SessionState = {
    ...baseState,
    ...computeCoherence(baseState),
  };

  const listeners = new Set<Listener>();

  function notify(): void {
    listeners.forEach(l => l({ ...state }));
  }

  function increment(
    field: 'anchorCycles' | 'viriditasEntries' | 'somnusLogs' | 'clarusInquiries' | 'sovereignCheckins'
  ): void {
    const next = { ...state, [field]: state[field] + 1 };
    state = { ...next, ...computeCoherence(next) };
    notify();
  }

  return {
    // Getters
    get sessionStart()      { return state.sessionStart; },
    get anchorCycles()      { return state.anchorCycles; },
    get viriditasEntries()  { return state.viriditasEntries; },
    get somnusLogs()        { return state.somnusLogs; },
    get clarusInquiries()   { return state.clarusInquiries; },
    get sovereignCheckins() { return state.sovereignCheckins; },
    get totalInteractions() { return state.totalInteractions; },
    get coherenceScore()    { return state.coherenceScore; },
    get coherenceLevel()    { return state.coherenceLevel; },

    // Actions
    recordAnchorCycle():      void { increment('anchorCycles'); },
    recordViriditasEntry():   void { increment('viriditasEntries'); },
    recordSomnusLog():        void { increment('somnusLogs'); },
    recordClarusInquiry():    void { increment('clarusInquiries'); },
    recordSovereignCheckin(): void { increment('sovereignCheckins'); },

    resetSession(): void {
      const base = {
        sessionStart:      new Date().toISOString(),
        anchorCycles:      0,
        viriditasEntries:  0,
        somnusLogs:        0,
        clarusInquiries:   0,
        sovereignCheckins: 0,
      };
      state = { ...base, ...computeCoherence(base) };
      notify();
    },

    // React useSyncExternalStore interface
    subscribe(listener: Listener): () => void {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
    getSnapshot(): SessionState {
      return { ...state };
    },
  };
}

/** Singleton session store — shared across all crystals. */
export const sessionStore = createSessionStore();
