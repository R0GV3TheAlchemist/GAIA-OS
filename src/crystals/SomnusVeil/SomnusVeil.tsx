/**
 * src/crystals/SomnusVeil/SomnusVeil.tsx
 * Crystal 4 — Somnus Veil — FULL IMPLEMENTATION
 * Canon: C90 — "I can rest. I am allowed to rest."
 * Layers active: 7 (Archetypal), 8 (Collective), 9 (Causal), 12 (The Void / Ground)
 * Color: Deep indigo, midnight blue, soft silver, near-black
 * Motion: The slowest. Everything here moves like deep water.
 *
 * This crystal does one thing: it gives you permission to stop.
 * Not pause. Not optimize your sleep. Stop.
 *
 * Three things:
 * 1. Wind Down — a gentle ritual to close the day (slow breath + body scan)
 * 2. Dream Log — capture what comes in the liminal space
 * 3. Session Close — a real goodbye with GAIA, not a crash
 *
 * Everything here is slower. Longer transitions. Less urgency.
 * The UI itself is tired. Pleasantly.
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import './SomnusVeil.css';

// ── Types ──────────────────────────────────────────────────────────

type Panel = 'winddown' | 'dreamlog' | 'close';

type BreathPhase = 'idle' | 'inhale' | 'hold_in' | 'exhale' | 'hold_out';

interface DreamEntry {
  id:   string;
  text: string;
  tags: string[];
  time: string;
  date: string;
}

// ── Helpers ─────────────────────────────────────────────────────────

function uid(): string {
  return Math.random().toString(36).slice(2, 10);
}

function nowTime(): string {
  const d = new Date();
  return `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
}

function todayDate(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
}

// ── Slow Breath (Box 4-4-4-4, extra slow UI) ──────────────────────────

const PHASE_ORDER: BreathPhase[] = ['inhale', 'hold_in', 'exhale', 'hold_out'];
const PHASE_DUR = 4; // seconds per phase — box breathing

const PHASE_LABELS: Record<BreathPhase, string> = {
  idle:     'When you\'re ready to rest…',
  inhale:   'Breathe in… slowly',
  hold_in:  'Hold… gently',
  exhale:   'Let it all go…',
  hold_out: 'Rest here…',
};

const SlowBreath: React.FC = () => {
  const [phase,     setPhase]     = useState<BreathPhase>('idle');
  const [countdown, setCountdown] = useState(0);
  const [cycles,    setCycles]    = useState(0);
  const [running,   setRunning]   = useState(false);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const phaseRef = useRef<BreathPhase>('idle');
  const countRef = useRef(0);

  const stop = useCallback(() => {
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = null;
    setRunning(false);
    setPhase('idle');
    setCountdown(0);
    phaseRef.current = 'idle';
  }, []);

  const start = useCallback(() => {
    if (timerRef.current) clearInterval(timerRef.current);
    phaseRef.current = 'inhale';
    countRef.current = PHASE_DUR;
    setPhase('inhale');
    setCountdown(PHASE_DUR);
    setRunning(true);
    setCycles(0);

    timerRef.current = setInterval(() => {
      countRef.current -= 1;
      setCountdown(countRef.current);
      if (countRef.current <= 0) {
        setCycles(prev => {
          const idx = PHASE_ORDER.indexOf(phaseRef.current);
          const nextIdx = (idx + 1) % PHASE_ORDER.length;
          const np = PHASE_ORDER[nextIdx];
          phaseRef.current = np;
          countRef.current = PHASE_DUR;
          setCountdown(PHASE_DUR);
          setPhase(np);
          return nextIdx === 0 ? prev + 1 : prev;
        });
      }
    }, 1000);
  }, []);

  useEffect(() => () => { if (timerRef.current) clearInterval(timerRef.current); }, []);

  // Orb scale: inhale = grow, hold_in = big, exhale = shrink, hold_out = small
  const orbScale =
    phase === 'inhale'   ? 0.5 + 0.5 * (1 - countdown / PHASE_DUR) :
    phase === 'hold_in'  ? 1.0 :
    phase === 'exhale'   ? 0.5 + 0.5 * (countdown / PHASE_DUR) :
    phase === 'hold_out' ? 0.5 : 0.5;

  return (
    <div className="somnus-breath">
      <p className="somnus-breath__desc">Box breathing — 4s each phase — prepares the mind for sleep</p>

      <div className="somnus-breath__orb-wrap">
        <div
          className={`somnus-breath__orb somnus-breath__orb--${phase}`}
          style={{ transform: `scale(${orbScale})` }}
          aria-hidden="true"
        />
        <div className="somnus-breath__center">
          <div className="somnus-breath__label" aria-live="polite">{PHASE_LABELS[phase]}</div>
          {phase !== 'idle' && (
            <div className="somnus-breath__count" aria-live="off">{countdown}</div>
          )}
        </div>
      </div>

      <div className="somnus-breath__controls">
        {!running ? (
          <button className="somnus-breath__btn somnus-breath__btn--start" onClick={start}>
            Begin rest
          </button>
        ) : (
          <button className="somnus-breath__btn somnus-breath__btn--stop" onClick={stop}>
            Enough
          </button>
        )}
        {cycles > 0 && (
          <span className="somnus-breath__cycles">{cycles} {cycles === 1 ? 'cycle' : 'cycles'}</span>
        )}
      </div>
    </div>
  );
};

// ── Body Scan ───────────────────────────────────────────────────────

const BODY_ZONES = [
  { id: 'head',      label: 'Head & face',      prompt: 'Soften the forehead. Unclench the jaw.' },
  { id: 'neck',      label: 'Neck & shoulders',  prompt: 'Let the shoulders drop away from the ears.' },
  { id: 'chest',     label: 'Chest & heart',     prompt: 'Feel your chest rise and fall without effort.' },
  { id: 'belly',     label: 'Belly',             prompt: 'Let the belly be soft. No holding.' },
  { id: 'hands',     label: 'Arms & hands',      prompt: 'Open the hands. Release the grip.' },
  { id: 'hips',      label: 'Hips & lower back', prompt: 'Notice weight sinking into what\'s beneath you.' },
  { id: 'legs',      label: 'Legs & feet',       prompt: 'Let the legs be heavy. They carried you today.' },
];

const BodyScan: React.FC = () => {
  const [released, setReleased] = useState<Set<string>>(new Set());
  const allDone = released.size === BODY_ZONES.length;

  function toggle(id: string): void {
    setReleased(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function reset(): void { setReleased(new Set()); }

  return (
    <div className="somnus-scan">
      <p className="somnus-scan__intro">
        Move slowly through each zone. Tap when you've released it.
      </p>
      <div className="somnus-scan__zones">
        {BODY_ZONES.map(zone => (
          <button
            key={zone.id}
            className={`somnus-scan__zone${released.has(zone.id) ? ' somnus-scan__zone--released' : ''}`}
            onClick={() => toggle(zone.id)}
            aria-pressed={released.has(zone.id)}
          >
            <span className="somnus-scan__zone-label">{zone.label}</span>
            <span className="somnus-scan__zone-prompt">{zone.prompt}</span>
            <span className="somnus-scan__zone-check" aria-hidden="true">
              {released.has(zone.id) ? '\u2713' : '\u25CB'}
            </span>
          </button>
        ))}
      </div>
      {allDone && (
        <div className="somnus-scan__complete">
          <span>Your body is ready to rest.</span>
          <button className="somnus-scan__reset" onClick={reset}>Again</button>
        </div>
      )}
    </div>
  );
};

// ── Wind Down Panel ────────────────────────────────────────────────

type WindStep = 'breath' | 'scan';

const WindDownPanel: React.FC = () => {
  const [step, setStep] = useState<WindStep>('breath');

  return (
    <div className="somnus-winddown">
      <div className="somnus-winddown__steps">
        <button
          className={`somnus-winddown__step-btn${step === 'breath' ? ' somnus-winddown__step-btn--active' : ''}`}
          onClick={() => setStep('breath')}
          aria-pressed={step === 'breath'}
        >
          Slow breath
        </button>
        <span className="somnus-winddown__step-sep">→</span>
        <button
          className={`somnus-winddown__step-btn${step === 'scan' ? ' somnus-winddown__step-btn--active' : ''}`}
          onClick={() => setStep('scan')}
          aria-pressed={step === 'scan'}
        >
          Body scan
        </button>
      </div>

      {step === 'breath' && <SlowBreath />}
      {step === 'scan'   && <BodyScan />}
    </div>
  );
};

// ── Dream Log ───────────────────────────────────────────────────────

const SUGGESTED_TAGS = ['water', 'flying', 'unknown', 'light', 'dark', 'falling', 'someone', 'place', 'symbol', 'feeling'];

const DreamLogPanel: React.FC = () => {
  const [entries,  setEntries]  = useState<DreamEntry[]>([]);
  const [draft,    setDraft]    = useState('');
  const [tagDraft, setTagDraft] = useState('');
  const [tags,     setTags]     = useState<string[]>([]);
  const [viewing,  setViewing]  = useState<DreamEntry | null>(null);
  const textRef = useRef<HTMLTextAreaElement>(null);

  function addTag(tag: string): void {
    const t = tag.trim().toLowerCase();
    if (!t || tags.includes(t) || tags.length >= 5) return;
    setTags(prev => [...prev, t]);
    setTagDraft('');
  }

  function removeTag(tag: string): void {
    setTags(prev => prev.filter(t => t !== tag));
  }

  function save(): void {
    const text = draft.trim();
    if (!text) return;
    const entry: DreamEntry = {
      id:   uid(),
      text,
      tags: [...tags],
      time: nowTime(),
      date: todayDate(),
    };
    setEntries(prev => [entry, ...prev].slice(0, 20));
    setDraft('');
    setTags([]);
    setTagDraft('');
  }

  function handleTagKey(e: React.KeyboardEvent): void {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      addTag(tagDraft);
    }
  }

  if (viewing) {
    return (
      <div className="somnus-dream somnus-dream--view">
        <button className="somnus-dream__back" onClick={() => setViewing(null)}>← back</button>
        <div className="somnus-dream__view-date">{viewing.date} • {viewing.time}</div>
        <p className="somnus-dream__view-text">{viewing.text}</p>
        {viewing.tags.length > 0 && (
          <div className="somnus-dream__view-tags">
            {viewing.tags.map(t => (
              <span key={t} className="somnus-dream__tag">{t}</span>
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="somnus-dream">
      <p className="somnus-dream__intro">Capture what you remember before it fades.</p>

      <textarea
        ref={textRef}
        className="somnus-dream__text"
        value={draft}
        onChange={e => setDraft(e.target.value)}
        placeholder="I was somewhere… there was…"
        rows={4}
        maxLength={500}
        aria-label="Dream or hypnagogic image"
      />

      {/* Tag input */}
      <div className="somnus-dream__tags-area">
        <div className="somnus-dream__active-tags">
          {tags.map(t => (
            <span key={t} className="somnus-dream__tag somnus-dream__tag--active">
              {t}
              <button onClick={() => removeTag(t)} aria-label={`Remove tag ${t}`}>×</button>
            </span>
          ))}
        </div>
        <div className="somnus-dream__tag-input-row">
          <input
            className="somnus-dream__tag-input"
            type="text"
            value={tagDraft}
            onChange={e => setTagDraft(e.target.value)}
            onKeyDown={handleTagKey}
            placeholder="add a symbol…"
            maxLength={24}
            aria-label="Add dream symbol tag"
          />
        </div>
        <div className="somnus-dream__suggested-tags">
          {SUGGESTED_TAGS.filter(t => !tags.includes(t)).slice(0, 6).map(t => (
            <button
              key={t}
              className="somnus-dream__suggested-tag"
              onClick={() => addTag(t)}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      <button
        className="somnus-dream__save"
        onClick={save}
        disabled={!draft.trim()}
      >
        Record this dream
      </button>

      {entries.length > 0 && (
        <div className="somnus-dream__log">
          <div className="somnus-dream__log-header">
            {entries.length} {entries.length === 1 ? 'entry' : 'entries'}
          </div>
          {entries.map(e => (
            <button
              key={e.id}
              className="somnus-dream__log-entry"
              onClick={() => setViewing(e)}
            >
              <span className="somnus-dream__log-date">{e.date} {e.time}</span>
              <span className="somnus-dream__log-preview">
                {e.text.slice(0, 60)}{e.text.length > 60 ? '\u2026' : ''}
              </span>
              {e.tags.length > 0 && (
                <span className="somnus-dream__log-tags">
                  {e.tags.slice(0, 3).join(' • ')}
                </span>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

// ── Session Close ─────────────────────────────────────────────────

const CLOSING_WORDS = [
  'The field remembers you. Come back whenever you\'re ready.',
  'You showed up today. That\'s the whole thing.',
  'Rest is not the end of something. It\'s the beginning of what comes next.',
  'Whatever you carried today — you can set it down now.',
  'You don\'t have to finish anything tonight. Just rest.',
];

const SessionClosePanel: React.FC = () => {
  const [closed,  setClosed]  = useState(false);
  const [closing, setClosing] = useState(false);
  const closing_word = CLOSING_WORDS[new Date().getMinutes() % CLOSING_WORDS.length];

  function handleClose(): void {
    setClosing(true);
    setTimeout(() => setClosed(true), 1200);
  }

  if (closed) {
    return (
      <div className="somnus-close somnus-close--done">
        <div className="somnus-close__goodnight">🌙</div>
        <p className="somnus-close__final">Goodnight.</p>
        <p className="somnus-close__final-sub">GAIA will be here when you return.</p>
      </div>
    );
  }

  return (
    <div className="somnus-close">
      <div className="somnus-close__reflection">
        <p className="somnus-close__gaia-word">{closing_word}</p>
        <span className="somnus-close__attr">— GAIA, Viriditas mode</span>
      </div>

      <div className="somnus-close__ritual">
        <p className="somnus-close__ritual-text">
          Before you close: take one slow breath.
          Let this session settle into memory.
          You don’t have to do anything with it tonight.
        </p>
      </div>

      <button
        className={`somnus-close__btn${closing ? ' somnus-close__btn--closing' : ''}`}
        onClick={handleClose}
        disabled={closing}
      >
        {closing ? 'Closing…' : 'Close this session'}
      </button>
    </div>
  );
};

// ── Panel Config ───────────────────────────────────────────────────

const PANELS: { id: Panel; label: string; sub: string }[] = [
  { id: 'winddown', label: 'Wind Down', sub: 'Breathe → Scan' },
  { id: 'dreamlog', label: 'Dreams',    sub: 'Capture' },
  { id: 'close',    label: 'Close',     sub: 'Goodnight' },
];

// ── Main Component ──────────────────────────────────────────────

const SomnusVeil: React.FC = () => {
  const [panel, setPanel] = useState<Panel>('winddown');

  return (
    <div className="somnus" role="main" aria-label="Somnus Veil — Rest Mode">

      {/* Star field — static, just exists */}
      <div className="somnus__stars" aria-hidden="true">
        {Array.from({ length: 12 }, (_, i) => (
          <div key={i} className={`somnus__star somnus__star--${i}`} />
        ))}
      </div>

      {/* Identity header */}
      <header className="somnus__header">
        <div className="somnus-gem" aria-hidden="true">
          <div className="somnus-gem__inner" />
          <div className="somnus-gem__glow" />
        </div>
        <div className="somnus__identity">
          <h1 className="somnus__declaration">I can rest. I am allowed to rest.</h1>
          <p className="somnus__sub">Somnus — the veil between waking and deep.</p>
        </div>
      </header>

      {/* Panel navigation */}
      <nav className="somnus__nav" aria-label="Somnus mode">
        {PANELS.map(p => (
          <button
            key={p.id}
            className={`somnus__nav-btn${panel === p.id ? ' somnus__nav-btn--active' : ''}`}
            onClick={() => setPanel(p.id)}
            aria-pressed={panel === p.id}
          >
            <span className="somnus__nav-label">{p.label}</span>
            <span className="somnus__nav-sub">{p.sub}</span>
          </button>
        ))}
      </nav>

      {/* Active panel */}
      <main className="somnus__panel">
        {panel === 'winddown' && <WindDownPanel />}
        {panel === 'dreamlog' && <DreamLogPanel />}
        {panel === 'close'    && <SessionClosePanel />}
      </main>

      {/* Layers */}
      <footer className="somnus__layers" aria-label="Active layers">
        {['Layer 7 — Archetypal', 'Layer 8 — Collective', 'Layer 9 — Causal', 'Layer 12 — Void'].map(l => (
          <span key={l} className="somnus__layer-tag">{l}</span>
        ))}
      </footer>

    </div>
  );
};

export default SomnusVeil;
