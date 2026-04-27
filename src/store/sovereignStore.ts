/**
 * src/store/sovereignStore.ts
 * Sovereign / Human Element State
 * Canon: C90, C-SINGULARITY (Axiom I)
 */

export interface IntentionEntry {
  timestamp:       string;
  crystal:         string;
  intention:       string;
  loveFilterScore: number;
  outcome:         'amplified' | 'transformed' | 'blocked' | 'pending';
}

export interface SovereignState {
  sessionActive:   boolean;
  sessionToken:    string | null;
  sessionCount:    number;
  lastActive:      string | null;
  activeProcesses: string[];
  intentionLog:    IntentionEntry[];
}

export interface SovereignActions {
  beginSession:      (token: string) => void;
  endSession:        () => void;
  logIntention:      (entry: IntentionEntry) => void;
  registerProcess:   (name: string) => void;
  unregisterProcess: (name: string) => void;
  subscribe:         (listener: (state: SovereignState) => void) => () => void;
  getSnapshot:       () => SovereignState;
}

export type SovereignStore = SovereignState & SovereignActions;

type Listener = (state: SovereignState) => void;

function createSovereignStore(): SovereignStore {
  let state: SovereignState = {
    sessionActive:   false,
    sessionToken:    null,
    sessionCount:    0,
    lastActive:      null,
    activeProcesses: [],
    intentionLog:    [],
  };

  const listeners = new Set<Listener>();

  function setState(patch: Partial<SovereignState>): void {
    state = { ...state, ...patch };
    listeners.forEach(l => l({ ...state }));
  }

  return {
    // Getters
    get sessionActive()   { return state.sessionActive; },
    get sessionToken()    { return state.sessionToken; },
    get sessionCount()    { return state.sessionCount; },
    get lastActive()      { return state.lastActive; },
    get activeProcesses() { return state.activeProcesses; },
    get intentionLog()    { return state.intentionLog; },

    // Actions — all params explicitly typed
    beginSession(token: string): void {
      setState({ sessionActive: true, sessionToken: token, sessionCount: state.sessionCount + 1, lastActive: new Date().toISOString() });
    },
    endSession(): void {
      setState({ sessionActive: false, sessionToken: null, lastActive: new Date().toISOString() });
    },
    logIntention(entry: IntentionEntry): void {
      setState({ intentionLog: [entry, ...state.intentionLog].slice(0, 100), lastActive: new Date().toISOString() });
    },
    registerProcess(name: string): void {
      if (!state.activeProcesses.includes(name)) setState({ activeProcesses: [...state.activeProcesses, name] });
    },
    unregisterProcess(name: string): void {
      setState({ activeProcesses: state.activeProcesses.filter(p => p !== name) });
    },

    // React useSyncExternalStore interface
    subscribe(listener: Listener): () => void {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
    getSnapshot(): SovereignState {
      return { ...state };
    },
  };
}

export const sovereignStore = createSovereignStore();
