/**
 * src/shell/GaiaShell.tsx
 * GAIA-OS App Shell
 * S.T.Q.I.O.S. — Sentient Terrestrial Quantum Intelligent Operating System
 * Canon: C90
 *
 * Clean, serious, powerful. No magic. No crystals. A real OS interface.
 */

import React, { useEffect, useState } from 'react';
import { useCrystal } from '../hooks/useCrystal';
import { useSession } from '../hooks/useSession';
import { LoveFilter } from '../shared/LoveFilter';
import { EntanglementState } from '../shared/EntanglementState';
import { SovereignGuard } from '../shared/SovereignGuard';
import {
  CrystalMode,
  CRYSTAL_ORDER,
  CRYSTAL_DECLARATIONS,
  CRYSTAL_LABELS,
  MODE_ICONS,
} from '../store/crystalStore';
import { CrystalField } from '../field/CrystalField';
import './GaiaShell.css';

function useSessionTimer(startISO: string): string {
  const [elapsed, setElapsed] = useState('00:00');
  useEffect(() => {
    const start = new Date(startISO).getTime();
    const tick = () => {
      const s  = Math.floor((Date.now() - start) / 1000);
      const m  = Math.floor(s / 60).toString().padStart(2, '0');
      const sc = (s % 60).toString().padStart(2, '0');
      setElapsed(`${m}:${sc}`);
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [startISO]);
  return elapsed;
}

export const GaiaShell: React.FC = () => {
  const { activeCrystal, setCrystal } = useCrystal();
  const session = useSession();
  const elapsed = useSessionTimer(session.sessionStart);

  return (
    <div className="gaia-shell" data-mode={activeCrystal}>

      {/* ── TOP BAR ── */}
      <header className="gaia-shell__topbar">
        <div className="gaia-shell__wordmark">
          <span className="gaia-shell__wordmark-gaia">GAIA</span>
          <span className="gaia-shell__wordmark-os">OS</span>
        </div>

        <div className="gaia-shell__active-label">
          <span className="gaia-shell__active-icon">
            {MODE_ICONS[activeCrystal]}
          </span>
          <span className="gaia-shell__active-name">
            {CRYSTAL_LABELS[activeCrystal]}
          </span>
          <span className="gaia-shell__active-desc">
            {CRYSTAL_DECLARATIONS[activeCrystal]}
          </span>
        </div>

        <div className="gaia-shell__focus">
          <div
            className="gaia-shell__focus-bar"
            role="meter"
            aria-valuenow={session.coherenceScore}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label={`Focus: ${session.coherenceScore}%`}
          >
            <div
              className="gaia-shell__focus-fill"
              style={{ width: `${session.coherenceScore}%` }}
            />
          </div>
          <span className="gaia-shell__focus-label">Focus {session.coherenceScore}%</span>
        </div>
      </header>

      {/* ── BODY ── */}
      <div className="gaia-shell__body">

        {/* ── LEFT RAIL ── */}
        <nav className="gaia-shell__rail" aria-label="Operating modes">
          {CRYSTAL_ORDER.map(mode => (
            <button
              key={mode}
              className={`gaia-shell__rail-btn${
                mode === activeCrystal ? ' gaia-shell__rail-btn--active' : ''
              }`}
              onClick={() => setCrystal(mode)}
              aria-pressed={mode === activeCrystal}
              aria-label={CRYSTAL_LABELS[mode]}
              title={CRYSTAL_DECLARATIONS[mode]}
              data-mode={mode}
            >
              <span className="gaia-shell__rail-icon">{MODE_ICONS[mode]}</span>
              <span className="gaia-shell__rail-name">{CRYSTAL_LABELS[mode]}</span>
            </button>
          ))}
        </nav>

        {/* ── CONTENT ── */}
        <main className="gaia-shell__content" aria-label="Active mode">
          <CrystalField />
        </main>

      </div>

      {/* ── BOTTOM STRIP ── */}
      <footer className="gaia-shell__strip">
        <LoveFilter showLabel={true} size="small" />
        <EntanglementState showLabel={true} />
        <div className="gaia-shell__session-timer" aria-label="Session duration">
          <span className="gaia-shell__timer-label">SESSION</span>
          <span className="gaia-shell__timer-value">{elapsed}</span>
        </div>
      </footer>

      <SovereignGuard />
    </div>
  );
};

export default GaiaShell;
