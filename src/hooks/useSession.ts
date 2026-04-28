/**
 * src/hooks/useSession.ts
 * React hook for the GAIA-OS Session Store.
 * Canon: C90 — Phase 4a
 *
 * Usage (read):
 *   const { coherenceScore, coherenceLevel, anchorCycles } = useSession();
 *
 * Usage (write):
 *   const { recordAnchorCycle } = useSession();
 *   recordAnchorCycle();
 */

import { useSyncExternalStore } from 'react';
import { sessionStore, SessionState, SessionActions } from '../store/sessionStore';

type UseSessionReturn = SessionState & Pick<SessionActions,
  | 'recordAnchorCycle'
  | 'recordViriditasEntry'
  | 'recordSomnusLog'
  | 'recordClarusInquiry'
  | 'recordSovereignCheckin'
  | 'resetSession'
>;

export function useSession(): UseSessionReturn {
  const state = useSyncExternalStore(
    sessionStore.subscribe.bind(sessionStore),
    sessionStore.getSnapshot.bind(sessionStore),
    sessionStore.getSnapshot.bind(sessionStore),
  );

  return {
    ...state,
    recordAnchorCycle:      () => sessionStore.recordAnchorCycle(),
    recordViriditasEntry:   () => sessionStore.recordViriditasEntry(),
    recordSomnusLog:        () => sessionStore.recordSomnusLog(),
    recordClarusInquiry:    () => sessionStore.recordClarusInquiry(),
    recordSovereignCheckin: () => sessionStore.recordSovereignCheckin(),
    resetSession:           () => sessionStore.resetSession(),
  };
}
