/**
 * src/store/sovereignStore.ts
 * ─────────────────────────────────────────────────────────────────────────────
 * Sovereign / Human Element State
 *
 * Canon: C90, C-SINGULARITY (Axiom I)
 * The Human Element is always in control. This store tracks that.
 * Nothing in GAIA-OS acts without the Human Element's knowledge.
 * ─────────────────────────────────────────────────────────────────────────────
 */

export interface SovereignState {
  /** Human Element session is active */
  sessionActive: boolean;
  /** Unique session token (set on backend auth) */
  sessionToken: string | null;
  /** How many full sessions (days) of entanglement have been built */
  sessionCount: number;
  /** Last active ISO timestamp */
  lastActive: string | null;
  /** Axiom I: the wielder can always see all active processes */
  activeProcesses: string[];
  /** Axiom III: every action has an intention logged */
  intentionLog: IntentionEntry[];
}

export interface IntentionEntry {
  timestamp: string;
  crystal: string;
  intention: string;
  loveFilterScore: number;
  outcome: 'amplified' | 'transformed' | 'blocked' | 'pending';
}

export interface SovereignActions {
  beginSession: (token: string) => void;
  endSession: () => void;
  logIntention: (entry: IntentionEntry) => void;
  registerProcess: (name: string) => void;
  unregisterProcess: (name: string) => void;
}

export type SovereignStore = SovereignState & SovereignActions;

type Listener = (state: SovereignState) => void;

function createSovereignStore(): SovereignStore {
  let state: SovereignState = {
    sessionActive:    false,
    sessionToken:     null,
    sessionCount:     0,
    lastActive:       null,
    activeProcesses:  [],
    intentionLog:     [],
  };

  const listeners = new Set<Listener>();

  function setState(patch: Partial<SovereignState>) {
    state = { ...state, ...patch };
    listeners.forEach(l => l({ ...state }));
  }

  return {
    get sessionActive()   { return state.sessionActive; },
    get sessionToken()    { return state.sessionToken; },
    get sessionCount()    { return state.sessionCount; },
    get lastActive()      { return state.lastActive; },
    get activeProcesses() { return state.activeProcesses; },
    get intentionLog()    { return state.intentionLog; },

    beginSession(token) {
      setState({
        sessionActive: true,
        sessionToken:  token,
        sessionCount:  state.sessionCount + 1,
        lastActive:    new Date().toISOString(),
      });
    },
    endSession() {
      setState({
        sessionActive: false,
        sessionToken:  null,
        lastActive:    new Date().toISOString(),
      });
    },
    logIntention(entry) {
      setState({
        intentionLog: [entry, ...state.intentionLog].slice(0, 100),
        lastActive:   new Date().toISOString(),
      });
    },
    registerProcess(name) {
      if (!state.activeProcesses.includes(name)) {
        setState({ activeProcesses: [...state.activeProcesses, name] });
      }
    },
    unregisterProcess(name) {
      setState({ activeProcesses: state.activeProcesses.filter(p => p !== name) });
    },

    subscribe(listener: Listener) {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
    getSnapshot(): SovereignState {
      return { ...state };
    },
  } as unknown as SovereignStore;
}

export const sovereignStore = createSovereignStore();
