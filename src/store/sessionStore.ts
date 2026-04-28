/**
 * src/store/sessionStore.ts
 * GAIA-OS Session Store — Cross-Crystal Coherence Data Bus.
 * Canon: C90 — Phase 4a
 */

export interface SessionState {
  sessionStart:      string;
  anchorCycles:      number;
  viriditasEntries:  number;
  somnusLogs:        number;
  clarusInquiries:   number;
  sovereignCheckins: number;
  totalInteractions: number;
  coherenceScore:    number;
  coherenceLevel:    CoherenceLevel;
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
  subscribe:              (listener: () => void) => () => void;
  getSnapshot:            () => SessionState;
}

export type SessionStore = SessionState & SessionActions;

// ── Coherence weights ────────────────────────────────────────────

const WEIGHTS = { sovereign: 8, anchor: 6, viriditas: 5, somnus: 4, clarus: 7 } as const;
const MAX_RAW = 150;

function computeCoherence(s: Omit<SessionState, 'coherenceScore' | 'coherenceLevel' | 'totalInteractions'>) {
  const raw =
    Math.min(s.sovereignCheckins, 5) * WEIGHTS.sovereign +
    Math.min(s.anchorCycles,      5) * WEIGHTS.anchor    +
    Math.min(s.viriditasEntries,  5) * WEIGHTS.viriditas +
    Math.min(s.somnusLogs,        5) * WEIGHTS.somnus    +
    Math.min(s.clarusInquiries,   5) * WEIGHTS.clarus;
  const coherenceScore = Math.round((raw / MAX_RAW) * 100);
  const totalInteractions = s.sovereignCheckins + s.anchorCycles + s.viriditasEntries + s.somnusLogs + s.clarusInquiries;
  let coherenceLevel: CoherenceLevel;
  if      (coherenceScore >= 85) coherenceLevel = 'Avatar';
  else if (coherenceScore >= 65) coherenceLevel = 'Coherent';
  else if (coherenceScore >= 40) coherenceLevel = 'Present';
  else if (coherenceScore >= 20) coherenceLevel = 'Settling';
  else                           coherenceLevel = 'Scattered';
  return { coherenceScore, coherenceLevel, totalInteractions };
}

// ── Store factory ──────────────────────────────────────────────

function createSessionStore(): SessionStore {
  const base = {
    sessionStart:      new Date().toISOString(),
    anchorCycles:      0,
    viriditasEntries:  0,
    somnusLogs:        0,
    clarusInquiries:   0,
    sovereignCheckins: 0,
  };

  let state: SessionState = { ...base, ...computeCoherence(base) };

  // Stable snapshot — same ref until state changes
  let cachedSnapshot: SessionState = { ...state };

  // useSyncExternalStore listeners are () => void
  const listeners = new Set<() => void>();

  function notify(): void {
    listeners.forEach(l => l());
  }

  function increment(
    field: 'anchorCycles' | 'viriditasEntries' | 'somnusLogs' | 'clarusInquiries' | 'sovereignCheckins'
  ): void {
    const next = { ...state, [field]: state[field] + 1 };
    state = { ...next, ...computeCoherence(next) };
    cachedSnapshot = { ...state };
    notify();
  }

  return {
    get sessionStart()      { return state.sessionStart; },
    get anchorCycles()      { return state.anchorCycles; },
    get viriditasEntries()  { return state.viriditasEntries; },
    get somnusLogs()        { return state.somnusLogs; },
    get clarusInquiries()   { return state.clarusInquiries; },
    get sovereignCheckins() { return state.sovereignCheckins; },
    get totalInteractions() { return state.totalInteractions; },
    get coherenceScore()    { return state.coherenceScore; },
    get coherenceLevel()    { return state.coherenceLevel; },

    recordAnchorCycle():      void { increment('anchorCycles'); },
    recordViriditasEntry():   void { increment('viriditasEntries'); },
    recordSomnusLog():        void { increment('somnusLogs'); },
    recordClarusInquiry():    void { increment('clarusInquiries'); },
    recordSovereignCheckin(): void { increment('sovereignCheckins'); },

    resetSession(): void {
      const b = {
        sessionStart:      new Date().toISOString(),
        anchorCycles:      0,
        viriditasEntries:  0,
        somnusLogs:        0,
        clarusInquiries:   0,
        sovereignCheckins: 0,
      };
      state = { ...b, ...computeCoherence(b) };
      cachedSnapshot = { ...state };
      notify();
    },

    subscribe(listener: () => void): () => void {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
    getSnapshot(): SessionState {
      return cachedSnapshot;
    },
  };
}

export const sessionStore = createSessionStore();
