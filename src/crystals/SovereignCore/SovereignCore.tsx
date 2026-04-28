/**
 * src/crystals/SovereignCore/SovereignCore.tsx
 * GAIA-OS — Control Mode
 * S.T.Q.I.O.S. — Canon: C90
 *
 * This is the default operating mode.
 * Full oversight. You are at the helm.
 * Clean, precise, no ceremony.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useCrystal } from '../../hooks/useCrystal';
import { useKernel, type SovereignStatus } from '../../hooks/useKernel';
import {
  CrystalMode,
  CRYSTAL_LABELS,
  CRYSTAL_DECLARATIONS,
  CRYSTAL_ORDER,
  MODE_ICONS,
} from '../../store/crystalStore';
import './SovereignCore.css';

// ── Live Clock ──────────────────────────────────────────────────────

const LiveClock: React.FC = () => {
  const [now, setNow] = useState(new Date());
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  const pad = (n: number) => String(n).padStart(2, '0');
  const h = pad(now.getHours());
  const m = pad(now.getMinutes());
  const s = pad(now.getSeconds());
  const days   = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

  return (
    <div className="sc-clock" role="timer" aria-label={`${h}:${m}:${s}`}>
      <div className="sc-clock__time">
        <span>{h}</span>
        <span className="sc-clock__sep">:</span>
        <span>{m}</span>
        <span className="sc-clock__sep sc-clock__sep--dim">:</span>
        <span className="sc-clock__s">{s}</span>
      </div>
      <div className="sc-clock__date">
        {days[now.getDay()]} {monthNames[now.getMonth()]} {now.getDate()}, {now.getFullYear()}
      </div>
    </div>
  );
};

const monthNames = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

// ── System Status ───────────────────────────────────────────────────

const StatusPanel: React.FC<{ status: SovereignStatus | null; loading: boolean }> = ({ status, loading }) => {
  if (loading || !status) {
    return (
      <div className="sc-status sc-status--loading">
        <span className="sc-status__dot" />
        <span>Connecting to kernel…</span>
      </div>
    );
  }

  return (
    <div className="sc-status" role="status">
      <div className="sc-status__row">
        <span className="sc-status__label">Active layers</span>
        <span className="sc-status__value">
          {status.layers_active.length > 0 ? status.layers_active.join(', ') : '1, 2, 3, HE'}
        </span>
      </div>
      <div className="sc-status__row">
        <span className="sc-status__label">Tone</span>
        <span className="sc-status__value">{Math.round(status.love_filter_score * 100)}%</span>
      </div>
      <div className="sc-status__row">
        <span className="sc-status__label">Focus depth</span>
        <span className="sc-status__value">{Math.round(status.entanglement_depth * 100)}%</span>
      </div>
      <div className="sc-status__row">
        <span className="sc-status__label">Sessions</span>
        <span className="sc-status__value">{status.session_count}</span>
      </div>
    </div>
  );
};

// ── Note Logger ─────────────────────────────────────────────────────

interface NoteEntry { text: string; time: string; }

const NoteLogger: React.FC<{
  onLog: (text: string) => void;
  log:   NoteEntry[];
}> = ({ onLog, log }) => {
  const [draft, setDraft] = useState('');

  function handleSubmit(e: React.FormEvent): void {
    e.preventDefault();
    const t = draft.trim();
    if (!t) return;
    onLog(t);
    setDraft('');
  }

  return (
    <div className="sc-notes">
      <form className="sc-notes__form" onSubmit={handleSubmit}>
        <input
          className="sc-notes__input"
          type="text"
          value={draft}
          onChange={e => setDraft(e.target.value)}
          placeholder="What's on your mind?"
          maxLength={280}
          aria-label="Add a note"
        />
        <button
          className="sc-notes__submit"
          type="submit"
          disabled={!draft.trim()}
          aria-label="Log note"
        >
          ↵
        </button>
      </form>

      {log.length > 0 && (
        <div className="sc-notes__log" role="log">
          {log.map((entry, i) => (
            <div key={i} className="sc-notes__entry">
              <span className="sc-notes__entry-time">{entry.time}</span>
              <span className="sc-notes__entry-text">{entry.text}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// ── Mode Nav ────────────────────────────────────────────────────────

const ModeNav: React.FC<{
  activeCrystal: CrystalMode;
  setCrystal:    (mode: CrystalMode) => void;
}> = ({ activeCrystal, setCrystal }) => (
  <nav className="sc-modenav" aria-label="Switch operating mode">
    <div className="sc-modenav__label">Operating modes</div>
    <div className="sc-modenav__list">
      {CRYSTAL_ORDER.filter(m => m !== CrystalMode.SOVEREIGN_CORE).map(mode => (
        <button
          key={mode}
          className={`sc-modenav__btn${activeCrystal === mode ? ' sc-modenav__btn--active' : ''}`}
          onClick={() => setCrystal(mode)}
          aria-label={CRYSTAL_LABELS[mode]}
          title={CRYSTAL_DECLARATIONS[mode]}
        >
          <span className="sc-modenav__icon">{MODE_ICONS[mode]}</span>
          <div className="sc-modenav__text">
            <span className="sc-modenav__name">{CRYSTAL_LABELS[mode]}</span>
            <span className="sc-modenav__desc">{CRYSTAL_DECLARATIONS[mode]}</span>
          </div>
        </button>
      ))}
    </div>
  </nav>
);

// ── Main ────────────────────────────────────────────────────────────

export const SovereignCore: React.FC = () => {
  const { activeCrystal, setCrystal } = useCrystal();
  const { sovereign } = useKernel();

  const [status,  setStatus]  = useState<SovereignStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [notes,   setNotes]   = useState<NoteEntry[]>([]);

  useEffect(() => {
    let mounted = true;
    async function fetch(): Promise<void> {
      try {
        const s = await sovereign.getStatus();
        if (mounted) { setStatus(s); setLoading(false); }
      } catch {
        if (mounted) setLoading(false);
      }
    }
    void fetch();
    const id = setInterval(() => { void fetch(); }, 10_000);
    return () => { mounted = false; clearInterval(id); };
  }, [sovereign]);

  const handleLog = useCallback((text: string): void => {
    const now  = new Date();
    const time = `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`;
    setNotes(prev => [{ text, time }, ...prev].slice(0, 20));
  }, []);

  return (
    <div className="sovereign-core">

      <header className="sc-header">
        <div className="sc-header__title">GAIA-OS</div>
        <div className="sc-header__sub">Control Mode — full oversight active</div>
      </header>

      <div className="sc-grid">

        <section className="sc-section" aria-label="Time">
          <div className="sc-section__label">System time</div>
          <LiveClock />
        </section>

        <section className="sc-section" aria-label="System status">
          <div className="sc-section__label">System status</div>
          <StatusPanel status={status} loading={loading} />
        </section>

        <section className="sc-section sc-section--notes" aria-label="Notes">
          <div className="sc-section__label">Notes</div>
          <NoteLogger onLog={handleLog} log={notes} />
        </section>

        <section className="sc-section sc-section--modes" aria-label="Mode navigation">
          <ModeNav activeCrystal={activeCrystal} setCrystal={setCrystal} />
        </section>

      </div>
    </div>
  );
};

export default SovereignCore;
