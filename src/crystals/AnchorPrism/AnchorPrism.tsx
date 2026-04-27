/**
 * src/crystals/AnchorPrism/AnchorPrism.tsx
 * Crystal 2 — Anchor Prism — FULL IMPLEMENTATION
 * Canon: C90 — "I am here. I am stable."
 * Layers active: 1 (Physical), 2 (Energy), 3 (Coherence), 12 (The Field / Ground)
 * Color: Warm white, stone grey, earth brown, golden morning light
 * Motion: Perfectly still — it does not move. It holds.
 *
 * This crystal does one thing: it brings you back to your body.
 * Breathwork. Grounding. The present moment. Nothing else.
 * No tasks. No urgency. Just: you are here. That is enough.
 *
 * Real mechanics:
 * - 4-7-8 breathwork (clinically validated for nervous system regulation)
 * - Box breathing (4-4-4-4) — used by Navy SEALs, therapists, athletes
 * - 5-4-3-2-1 grounding (sensory anchoring for anxiety/dissociation)
 * - Presence log (micro-journaling — "I notice...")
 * All timers are real setInterval — no fake animation.
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import './AnchorPrism.css';

// ── Breath State Machine ────────────────────────────────────────────────

type BreathPhase = 'idle' | 'inhale' | 'hold' | 'exhale' | 'rest';
type BreathMode  = '478' | 'box';

interface BreathProfile {
  label:   string;
  desc:    string;
  inhale:  number; // seconds
  hold:    number;
  exhale:  number;
  rest:    number;
}

const BREATH_PROFILES: Record<BreathMode, BreathProfile> = {
  '478': {
    label:  '4-7-8',
    desc:   'Inhale 4s • Hold 7s • Exhale 8s — calms the nervous system',
    inhale: 4, hold: 7, exhale: 8, rest: 2,
  },
  'box': {
    label:  'Box',
    desc:   'Inhale 4s • Hold 4s • Exhale 4s • Rest 4s — builds focus',
    inhale: 4, hold: 4, exhale: 4, rest: 4,
  },
};

const PHASE_LABELS: Record<BreathPhase, string> = {
  idle:   'When you\'re ready…',
  inhale: 'Breathe in…',
  hold:   'Hold…',
  exhale: 'Let it go…',
  rest:   'Rest…',
};

const PHASE_ORDER: BreathPhase[] = ['inhale', 'hold', 'exhale', 'rest'];

function phaseDuration(phase: BreathPhase, profile: BreathProfile): number {
  if (phase === 'inhale') return profile.inhale;
  if (phase === 'hold')   return profile.hold;
  if (phase === 'exhale') return profile.exhale;
  if (phase === 'rest')   return profile.rest;
  return 0;
}

// ── Breathwork Component ─────────────────────────────────────────────

const BreathworkTimer: React.FC = () => {
  const [mode,       setMode]       = useState<BreathMode>('478');
  const [phase,      setPhase]      = useState<BreathPhase>('idle');
  const [countdown,  setCountdown]  = useState(0);
  const [cycles,     setCycles]     = useState(0);
  const [running,    setRunning]    = useState(false);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const phaseRef = useRef<BreathPhase>('idle');
  const countRef = useRef(0);

  const profile = BREATH_PROFILES[mode];

  const stop = useCallback(() => {
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = null;
    setRunning(false);
    setPhase('idle');
    setCountdown(0);
    phaseRef.current = 'idle';
  }, []);

  const nextPhase = useCallback((currentPhase: BreathPhase, currentCycles: number): { phase: BreathPhase; cycles: number } => {
    const idx = PHASE_ORDER.indexOf(currentPhase);
    if (idx === PHASE_ORDER.length - 1) {
      return { phase: PHASE_ORDER[0], cycles: currentCycles + 1 };
    }
    return { phase: PHASE_ORDER[idx + 1], cycles: currentCycles };
  }, []);

  const start = useCallback(() => {
    if (timerRef.current) clearInterval(timerRef.current);
    const firstPhase: BreathPhase = 'inhale';
    const firstDur = phaseDuration(firstPhase, profile);
    phaseRef.current = firstPhase;
    countRef.current = firstDur;
    setPhase(firstPhase);
    setCountdown(firstDur);
    setRunning(true);
    setCycles(0);

    timerRef.current = setInterval(() => {
      countRef.current -= 1;
      setCountdown(countRef.current);

      if (countRef.current <= 0) {
        setCycles(prev => {
          const { phase: np, cycles: nc } = nextPhase(phaseRef.current, prev);
          phaseRef.current = np;
          const dur = phaseDuration(np, profile);
          countRef.current = dur;
          setCountdown(dur);
          setPhase(np);
          return nc;
        });
      }
    }, 1000);
  }, [profile, nextPhase]);

  useEffect(() => () => { if (timerRef.current) clearInterval(timerRef.current); }, []);

  const ringScale =
    phase === 'inhale' ? 0.5 + 0.5 * (1 - countdown / profile.inhale) :
    phase === 'hold'   ? 1.0 :
    phase === 'exhale' ? 0.5 + 0.5 * (countdown / profile.exhale) :
    phase === 'rest'   ? 0.5 : 0.5;

  return (
    <div className="anchor-breath">
      <div className="anchor-breath__modes">
        {(Object.entries(BREATH_PROFILES) as [BreathMode, BreathProfile][]).map(([key, p]) => (
          <button
            key={key}
            className={`anchor-breath__mode-btn${mode === key ? ' anchor-breath__mode-btn--active' : ''}`}
            onClick={() => { stop(); setMode(key); }}
            aria-pressed={mode === key}
          >
            {p.label}
          </button>
        ))}
      </div>

      <p className="anchor-breath__desc">{profile.desc}</p>

      <div className="anchor-breath__ring-wrap">
        <div
          className={`anchor-breath__ring anchor-breath__ring--${phase}`}
          style={{ transform: `scale(${ringScale})` }}
          aria-hidden="true"
        />
        <div className="anchor-breath__ring-inner">
          <div className="anchor-breath__phase-label" aria-live="polite">
            {PHASE_LABELS[phase]}
          </div>
          {phase !== 'idle' && (
            <div className="anchor-breath__countdown" aria-live="off">
              {countdown}
            </div>
          )}
        </div>
      </div>

      <div className="anchor-breath__controls">
        {!running ? (
          <button className="anchor-breath__btn anchor-breath__btn--start" onClick={start}>
            Begin
          </button>
        ) : (
          <button className="anchor-breath__btn anchor-breath__btn--stop" onClick={stop}>
            Stop
          </button>
        )}
        {cycles > 0 && (
          <span className="anchor-breath__cycles">{cycles} {cycles === 1 ? 'cycle' : 'cycles'}</span>
        )}
      </div>
    </div>
  );
};

// ── 5-4-3-2-1 Grounding ─────────────────────────────────────────────

const GROUNDING_STEPS = [
  { count: 5, sense: 'see',   prompt: 'Name 5 things you can see right now.' },
  { count: 4, sense: 'touch', prompt: 'Notice 4 things you can physically feel.' },
  { count: 3, sense: 'hear',  prompt: 'Listen for 3 sounds around you.' },
  { count: 2, sense: 'smell', prompt: 'Find 2 things you can smell.' },
  { count: 1, sense: 'taste', prompt: 'Notice 1 thing you can taste.' },
];

const GroundingExercise: React.FC = () => {
  const [stepIdx, setStepIdx] = useState(0);
  const [done,    setDone]    = useState(false);
  const [entries, setEntries] = useState<string[][]>(GROUNDING_STEPS.map(() => []));
  const [draft,   setDraft]   = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const step = GROUNDING_STEPS[stepIdx];
  const stepEntries = entries[stepIdx] ?? [];
  const remaining = step.count - stepEntries.length;

  function addEntry(): void {
    const trimmed = draft.trim();
    if (!trimmed) return;
    const next = entries.map((e, i) => i === stepIdx ? [...e, trimmed] : e);
    setEntries(next);
    setDraft('');
    inputRef.current?.focus();
    if (next[stepIdx].length >= step.count) {
      if (stepIdx < GROUNDING_STEPS.length - 1) {
        setTimeout(() => setStepIdx(i => i + 1), 400);
      } else {
        setTimeout(() => setDone(true), 400);
      }
    }
  }

  function handleKey(e: React.KeyboardEvent): void {
    if (e.key === 'Enter') addEntry();
  }

  function reset(): void {
    setStepIdx(0);
    setDone(false);
    setEntries(GROUNDING_STEPS.map(() => []));
    setDraft('');
  }

  if (done) {
    return (
      <div className="anchor-grounding anchor-grounding--done">
        <div className="anchor-grounding__complete">✓ Grounded.</div>
        <p className="anchor-grounding__done-text">
          You named what is real. You are here. That is enough.
        </p>
        <button className="anchor-grounding__reset" onClick={reset}>Again</button>
      </div>
    );
  }

  return (
    <div className="anchor-grounding">
      <div className="anchor-grounding__step-header">
        <span className="anchor-grounding__sense">{step.count} things you can {step.sense}</span>
        <span className="anchor-grounding__remaining">{remaining} remaining</span>
      </div>
      <p className="anchor-grounding__prompt">{step.prompt}</p>

      <div className="anchor-grounding__entries">
        {stepEntries.map((e, i) => (
          <div key={i} className="anchor-grounding__entry">
            <span className="anchor-grounding__entry-num">{i + 1}</span>
            <span className="anchor-grounding__entry-text">{e}</span>
          </div>
        ))}
      </div>

      <div className="anchor-grounding__input-row">
        <input
          ref={inputRef}
          className="anchor-grounding__input"
          type="text"
          value={draft}
          onChange={e => setDraft(e.target.value)}
          onKeyDown={handleKey}
          placeholder={`I ${step.sense}…`}
          maxLength={120}
          autoFocus
          aria-label={`Enter something you can ${step.sense}`}
        />
        <button
          className="anchor-grounding__add"
          onClick={addEntry}
          disabled={!draft.trim()}
          aria-label="Add"
        >
          +
        </button>
      </div>

      <div className="anchor-grounding__progress">
        {GROUNDING_STEPS.map((_, i) => (
          <div
            key={i}
            className={`anchor-grounding__pip${
              i < stepIdx ? ' anchor-grounding__pip--done' :
              i === stepIdx ? ' anchor-grounding__pip--active' : ''
            }`}
            aria-hidden="true"
          />
        ))}
      </div>
    </div>
  );
};

// ── Presence Log ───────────────────────────────────────────────────

interface PresenceEntry {
  text: string;
  time: string;
}

const PresenceLog: React.FC = () => {
  const [entries, setEntries] = useState<PresenceEntry[]>([]);
  const [draft,   setDraft]   = useState('');

  function addEntry(): void {
    const trimmed = draft.trim();
    if (!trimmed) return;
    const now  = new Date();
    const time = `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`;
    setEntries(prev => [{ text: trimmed, time }, ...prev].slice(0, 12));
    setDraft('');
  }

  function handleKey(e: React.KeyboardEvent): void {
    if (e.key === 'Enter') addEntry();
  }

  return (
    <div className="anchor-presence">
      <div className="anchor-presence__input-row">
        <span className="anchor-presence__prefix">I notice…</span>
        <input
          className="anchor-presence__input"
          type="text"
          value={draft}
          onChange={e => setDraft(e.target.value)}
          onKeyDown={handleKey}
          placeholder="something real, right now"
          maxLength={200}
          aria-label="I notice… (presence moment)"
        />
        <button
          className="anchor-presence__submit"
          onClick={addEntry}
          disabled={!draft.trim()}
          aria-label="Log presence moment"
        >
          ■
        </button>
      </div>

      {entries.length > 0 && (
        <div className="anchor-presence__log" role="log">
          {entries.map((e, i) => (
            <div key={i} className="anchor-presence__entry">
              <span className="anchor-presence__entry-time">{e.time}</span>
              <span className="anchor-presence__entry-text">I notice {e.text}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// ── Panel toggle ────────────────────────────────────────────────────

type Panel = 'breath' | 'grounding' | 'presence';

const PANELS: { id: Panel; label: string; sub: string }[] = [
  { id: 'breath',    label: 'Breathe',  sub: 'Regulate' },
  { id: 'grounding', label: 'Ground',   sub: '5-4-3-2-1' },
  { id: 'presence',  label: 'Notice',   sub: 'I notice…' },
];

// ── Main Component ──────────────────────────────────────────────

const AnchorPrism: React.FC = () => {
  const [panel, setPanel] = useState<Panel>('breath');
  const [now,   setNow]   = useState(new Date());

  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 60_000);
    return () => clearInterval(id);
  }, []);

  const pad = (n: number) => String(n).padStart(2, '0');
  const timeStr = `${pad(now.getHours())}:${pad(now.getMinutes())}`;
  const dayNames    = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
  const monthNames  = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  const dateStr = `${dayNames[now.getDay()]}, ${monthNames[now.getMonth()]} ${now.getDate()}`;

  return (
    <div className="anchor-prism" role="main" aria-label="Anchor Prism — Grounding Mode">

      {/* Identity header */}
      <header className="anchor-prism__header">
        <div className="anchor-gem" aria-hidden="true">
          <div className="anchor-gem__stone" />
          <div className="anchor-gem__glow" />
        </div>
        <div className="anchor-prism__identity">
          <h1 className="anchor-prism__declaration">I am here. I am stable.</h1>
          <p className="anchor-prism__sub">You don't have to go anywhere. You're already where you need to be.</p>
        </div>
        <div className="anchor-prism__clock" aria-label={`Current time: ${timeStr}`}>
          <div className="anchor-prism__time">{timeStr}</div>
          <div className="anchor-prism__date">{dateStr}</div>
        </div>
      </header>

      {/* Panel navigation */}
      <nav className="anchor-prism__nav" aria-label="Anchor mode">
        {PANELS.map(p => (
          <button
            key={p.id}
            className={`anchor-prism__nav-btn${panel === p.id ? ' anchor-prism__nav-btn--active' : ''}`}
            onClick={() => setPanel(p.id)}
            aria-pressed={panel === p.id}
          >
            <span className="anchor-prism__nav-label">{p.label}</span>
            <span className="anchor-prism__nav-sub">{p.sub}</span>
          </button>
        ))}
      </nav>

      {/* Active panel */}
      <main className="anchor-prism__panel">
        {panel === 'breath'    && <BreathworkTimer />}
        {panel === 'grounding' && <GroundingExercise />}
        {panel === 'presence'  && <PresenceLog />}
      </main>

      {/* Layers */}
      <footer className="anchor-prism__layers" aria-label="Active layers">
        {['Layer 1 — Physical', 'Layer 2 — Energy', 'Layer 3 — Coherence', 'Layer 12 — Ground'].map(l => (
          <span key={l} className="anchor-prism__layer-tag">{l}</span>
        ))}
      </footer>

    </div>
  );
};

export default AnchorPrism;
