/**
 * src/crystals/SovereignCore/SovereignCore.tsx
 * Crystal 1 — Sovereign Core — FULL IMPLEMENTATION
 * Canon: C90 — "Nothing happens unless I allow it."
 * Layers active: 1 (Physical), 2 (Energy), 3 (Coherence/Love Filter), Human Element (9)
 * Color: Bright white, silver, clear crystal geometry
 * Motion: Slow stable rotation — commanding, centered, unhurried
 *
 * This is the first face of GAIA.
 * It is the crystal that greets the wielder when the app opens.
 * It communicates: you are safe, you are in control, nothing happens without you.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useCrystal } from '../../hooks/useCrystal';
import { useKernel, type SovereignStatus } from '../../hooks/useKernel';
import {
  CrystalMode,
  CRYSTAL_LABELS,
  CRYSTAL_DECLARATIONS,
  CRYSTAL_ORDER,
} from '../../store/crystalStore';
import './SovereignCore.css';

// ── Sub-components ──────────────────────────────────────────────────

const SovereignGem: React.FC = () => (
  <div className="sovereign-gem" aria-hidden="true">
    <div className="sovereign-gem__outer" />
    <div className="sovereign-gem__middle" />
    <div className="sovereign-gem__inner">◆</div>
    <div className="sovereign-gem__glow" />
  </div>
);

interface LiveClockProps { compact?: boolean }

const LiveClock: React.FC<LiveClockProps> = ({ compact = false }) => {
  const [now, setNow] = useState(new Date());

  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  const pad = (n: number) => String(n).padStart(2, '0');
  const h = pad(now.getHours());
  const m = pad(now.getMinutes());
  const s = pad(now.getSeconds());
  const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  const monthNames = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

  if (compact) {
    return (
      <div className="sovereign-clock sovereign-clock--compact">
        <span className="sovereign-clock__time">{h}:{m}</span>
      </div>
    );
  }

  return (
    <div className="sovereign-clock" role="timer" aria-label={`Current time: ${h}:${m}:${s}`}>
      <div className="sovereign-clock__time">
        <span className="sovereign-clock__h">{h}</span>
        <span className="sovereign-clock__sep">:</span>
        <span className="sovereign-clock__m">{m}</span>
        <span className="sovereign-clock__sep sovereign-clock__sep--dim">:</span>
        <span className="sovereign-clock__s">{s}</span>
      </div>
      <div className="sovereign-clock__date">
        {dayNames[now.getDay()]} — {monthNames[now.getMonth()]} {now.getDate()}, {now.getFullYear()}
      </div>
    </div>
  );
};

interface StatusPanelProps { status: SovereignStatus | null; loading: boolean }

const StatusPanel: React.FC<StatusPanelProps> = ({ status, loading }) => {
  if (loading || !status) {
    return (
      <div className="sovereign-status sovereign-status--loading">
        <span className="sovereign-status__dot" />
        <span className="sovereign-status__text">Connecting to kernel…</span>
      </div>
    );
  }

  const loveScore = Math.round(status.love_filter_score * 100);
  const entDepth  = Math.round(status.entanglement_depth * 100);
  const layerStr  = status.layers_active.length > 0
    ? status.layers_active.join(', ')
    : 'Layers 1, 2, 3, HE';

  return (
    <div className="sovereign-status" role="status" aria-label="System status">
      <div className="sovereign-status__row">
        <span className="sovereign-status__label">Layers</span>
        <span className="sovereign-status__value">{layerStr}</span>
      </div>
      <div className="sovereign-status__row">
        <span className="sovereign-status__label">Love Filter</span>
        <span className="sovereign-status__value sovereign-status__value--love">{loveScore}%</span>
      </div>
      <div className="sovereign-status__row">
        <span className="sovereign-status__label">Entanglement</span>
        <span className="sovereign-status__value">{entDepth}%</span>
      </div>
      <div className="sovereign-status__row">
        <span className="sovereign-status__label">Sessions</span>
        <span className="sovereign-status__value">{status.session_count}</span>
      </div>
    </div>
  );
};

const AXIOMS = [
  { number: 'I',   text: 'The Human Element controls with love and authority.' },
  { number: 'II',  text: 'Every intention is filtered through love.' },
  { number: 'III', text: 'Every action is declared before it is taken.' },
];

const AxiomPanel: React.FC = () => (
  <div className="sovereign-axioms" role="list" aria-label="The three axioms">
    {AXIOMS.map(a => (
      <div key={a.number} className="sovereign-axioms__item" role="listitem">
        <span className="sovereign-axioms__num">Axiom {a.number}</span>
        <span className="sovereign-axioms__text">{a.text}</span>
      </div>
    ))}
  </div>
);

interface IntentionLoggerProps {
  onLog: (intention: string) => void;
  log:   { intention: string; time: string; stamp: string }[];
}

const IntentionLogger: React.FC<IntentionLoggerProps> = ({ onLog, log }) => {
  const [draft, setDraft] = useState('');

  function handleSubmit(e: React.FormEvent): void {
    e.preventDefault();
    const trimmed = draft.trim();
    if (!trimmed) return;
    onLog(trimmed);
    setDraft('');
  }

  return (
    <div className="sovereign-intentions">
      <form className="sovereign-intentions__form" onSubmit={handleSubmit}>
        <input
          className="sovereign-intentions__input"
          type="text"
          value={draft}
          onChange={e => setDraft(e.target.value)}
          placeholder="Declare your intention…"
          maxLength={280}
          aria-label="Declare your intention (Axiom III)"
        />
        <button
          className="sovereign-intentions__submit"
          type="submit"
          disabled={!draft.trim()}
          aria-label="Log intention"
        >
          ◆
        </button>
      </form>

      {log.length > 0 && (
        <div className="sovereign-intentions__log" role="log" aria-label="Intention log">
          {log.map((entry, i) => (
            <div key={i} className="sovereign-intentions__entry">
              <span className="sovereign-intentions__entry-time">{entry.time}</span>
              <span className="sovereign-intentions__entry-text">{entry.intention}</span>
              <span className="sovereign-intentions__entry-stamp">{entry.stamp}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

interface CrystalNavProps {
  activeCrystal: CrystalMode;
  setCrystal:    (mode: CrystalMode) => void;
}

const OTHER_CRYSTALS = CRYSTAL_ORDER.filter(m => m !== CrystalMode.SOVEREIGN_CORE);

const CrystalNav: React.FC<CrystalNavProps> = ({ activeCrystal, setCrystal }) => (
  <nav className="sovereign-nav" aria-label="Navigate to another crystal">
    <div className="sovereign-nav__label">Open a crystal</div>
    <div className="sovereign-nav__crystals">
      {OTHER_CRYSTALS.map(mode => (
        <button
          key={mode}
          className={`sovereign-nav__btn sovereign-nav__btn--${mode.replace(/_/g, '-')}${activeCrystal === mode ? ' sovereign-nav__btn--active' : ''}`}
          onClick={() => setCrystal(mode)}
          aria-label={`${CRYSTAL_LABELS[mode]} — ${CRYSTAL_DECLARATIONS[mode]}`}
          title={CRYSTAL_DECLARATIONS[mode]}
        >
          <span className="sovereign-nav__btn-gem" aria-hidden="true">◆</span>
          <span className="sovereign-nav__btn-label">{CRYSTAL_LABELS[mode]}</span>
          <span className="sovereign-nav__btn-declaration">{CRYSTAL_DECLARATIONS[mode]}</span>
        </button>
      ))}
    </div>
  </nav>
);

// ── Main Component ──────────────────────────────────────────────

interface IntentionEntry {
  intention: string;
  time:      string;
  stamp:     string;
}

export const SovereignCore: React.FC = () => {
  const { activeCrystal, setCrystal, loveFilterScore } = useCrystal();
  const { sovereign } = useKernel();

  const [status,   setStatus]   = useState<SovereignStatus | null>(null);
  const [loading,  setLoading]  = useState(true);
  const [intentionLog, setIntentionLog] = useState<IntentionEntry[]>([]);

  // Poll kernel status every 10s
  useEffect(() => {
    let mounted = true;
    async function fetchStatus(): Promise<void> {
      try {
        const s = await sovereign.getStatus();
        if (mounted) { setStatus(s); setLoading(false); }
      } catch {
        if (mounted) setLoading(false);
      }
    }
    void fetchStatus();
    const id = setInterval(() => { void fetchStatus(); }, 10_000);
    return () => { mounted = false; clearInterval(id); };
  }, [sovereign]);

  const handleLogIntention = useCallback((intention: string): void => {
    const now   = new Date();
    const time  = `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`;
    const stamp = loveFilterScore >= 0.8 ? '♥ Aligned' :
                  loveFilterScore >= 0.5 ? '◆ Coherent' : '○ Neutral';
    setIntentionLog(prev => [{ intention, time, stamp }, ...prev].slice(0, 20));
  }, [loveFilterScore]);

  return (
    <div className="sovereign-core" role="main" aria-label="Sovereign Core">

      {/* Header — Identity */}
      <header className="sovereign-core__header">
        <SovereignGem />
        <div className="sovereign-core__identity">
          <h1 className="sovereign-core__declaration">Nothing happens unless I allow it.</h1>
          <p className="sovereign-core__sub">You are safe. You are strong. You are not alone.</p>
        </div>
      </header>

      {/* Main dashboard grid */}
      <div className="sovereign-core__grid">

        {/* Clock */}
        <section className="sovereign-core__section sovereign-core__section--clock" aria-label="Time">
          <LiveClock />
        </section>

        {/* Kernel status */}
        <section className="sovereign-core__section sovereign-core__section--status" aria-label="System status">
          <div className="sovereign-core__section-label">System</div>
          <StatusPanel status={status} loading={loading} />
        </section>

        {/* Axioms */}
        <section className="sovereign-core__section sovereign-core__section--axioms" aria-label="The three axioms">
          <div className="sovereign-core__section-label">Axioms</div>
          <AxiomPanel />
        </section>

        {/* Intention logger — Axiom III */}
        <section className="sovereign-core__section sovereign-core__section--intentions" aria-label="Intention log (Axiom III)">
          <div className="sovereign-core__section-label">Declare (Axiom III)</div>
          <IntentionLogger onLog={handleLogIntention} log={intentionLog} />
        </section>

        {/* Crystal navigation */}
        <section className="sovereign-core__section sovereign-core__section--nav" aria-label="Crystal navigation">
          <CrystalNav activeCrystal={activeCrystal} setCrystal={setCrystal} />
        </section>

      </div>
    </div>
  );
};

export default SovereignCore;
