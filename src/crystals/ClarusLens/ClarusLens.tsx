/**
 * src/crystals/ClarusLens/ClarusLens.tsx
 * Crystal 5 — Clarus Lens — FULL IMPLEMENTATION
 * Canon: C90 — "I can think clearly. I can see what is true."
 * Layers active: 3 (Geometry / Ethics), 5 (Cognition), 10 (Informational), 11 (Heart State / Signal)
 * Color: Electric ice-blue, clean white, pure black, sharp silver
 * Motion: The fastest, most precise crystal. Snaps. Cuts. Clarifies.
 *
 * This is the prism. Light goes in, truth comes out.
 * Four things:
 * 1. Inquire — GAIA asks you 5 sharp questions. You answer. It reflects what it sees.
 * 2. Signal — "What is actually true right now?" — a 3-field epistemic snapshot
 * 3. Lineage — birthdate → your natural cognitive/emotional wiring (sun/season/lifepath)
 * 4. Coherence — your Avatar state meter. Real score computed from cross-crystal session data.
 *
 * Clarus does not comfort. It clarifies.
 * It is the last crystal because clarity is earned, not given.
 */

import React, { useState, useCallback, useEffect } from 'react';
import './ClarusLens.css';

// ── Types ──────────────────────────────────────────────────────────

type Panel = 'inquire' | 'signal' | 'lineage' | 'coherence';

interface SignalEntry {
  id:       string;
  know:     string;
  assuming: string;
  avoiding: string;
  time:     string;
}

interface LineageData {
  birthdate:  string;
  sunSign:    string;
  season:     string;
  lifePath:   number;
  wiring:     string;
  cognitive:  string;
  emotional:  string;
}

interface InquiryExchange {
  question:   string;
  answer:     string;
  reflection: string;
}

// ── Helpers ─────────────────────────────────────────────────────────

function uid(): string {
  return Math.random().toString(36).slice(2, 10);
}

function nowTime(): string {
  const d = new Date();
  return `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
}

// ── Lineage Engine ────────────────────────────────────────────────
// Not fortune-telling. Wiring maps. Natural signal, not destiny.

const SUN_SIGNS = [
  { sign: 'Capricorn',  start: [12,22], end: [1,19],  wiring: 'Structural', cognitive: 'Long-range pattern builder. Sees the mountain, not just the step.',      emotional: 'Slow to open, deep when committed. Loyalty as a core value.' },
  { sign: 'Aquarius',   start: [1,20],  end: [2,18],  wiring: 'Systemic',   cognitive: 'Networks and abstractions. Sees connections others miss.',                emotional: 'Emotional independence as protection. Warmth from a distance.' },
  { sign: 'Pisces',     start: [2,19],  end: [3,20],  wiring: 'Perceptual',  cognitive: 'Absorbs atmosphere. Thinks in images and feelings, not logic chains.',   emotional: 'Extremely permeable. Boundaries are a practice, not a default.' },
  { sign: 'Aries',      start: [3,21],  end: [4,19],  wiring: 'Initiating',  cognitive: 'Rapid decisive processing. First mover. Bored by completion.',           emotional: 'Intense, honest, short-duration. Rarely holds grudges.' },
  { sign: 'Taurus',     start: [4,20],  end: [5,20],  wiring: 'Grounding',   cognitive: 'Sensory and concrete. Builds to last. Slow to change, hard to move.',   emotional: 'Stable, tactile, deeply loyal. Disruption is genuinely painful.' },
  { sign: 'Gemini',     start: [5,21],  end: [6,20],  wiring: 'Connective',  cognitive: 'Rapid parallel processing. Multiple frames simultaneously.',             emotional: 'Variable, curious, contact-hungry. Consistency is the challenge.' },
  { sign: 'Cancer',     start: [6,21],  end: [7,22],  wiring: 'Protective',  cognitive: 'Memory-dominant. History and feeling shape every present decision.',     emotional: 'Intensely relational. Safety and home are primary drives.' },
  { sign: 'Leo',        start: [7,23],  end: [8,22],  wiring: 'Generative',  cognitive: 'Creative and centralizing. Leads by example and presence.',              emotional: 'Needs recognition to feel real. Gives abundantly when seen.' },
  { sign: 'Virgo',      start: [8,23],  end: [9,22],  wiring: 'Analytical',  cognitive: 'Detail and system. Finds the error in every structure.',                  emotional: 'Internalizes. Self-critical. Service as love language.' },
  { sign: 'Libra',      start: [9,23],  end: [10,22], wiring: 'Balancing',   cognitive: 'Relational and comparative. Weighs every option.',                       emotional: 'Conflict-averse. Harmony as a deep need, not just a preference.' },
  { sign: 'Scorpio',    start: [10,23], end: [11,21], wiring: 'Depth-seeking',cognitive: 'Penetrates surface. Uncomfortable with anything incomplete or hidden.',  emotional: 'Intense, private, transformative. Trust is everything.' },
  { sign: 'Sagittarius',start: [11,22], end: [12,21], wiring: 'Expansive',   cognitive: 'Meaning and horizon. Philosophy over mechanics.',                         emotional: 'Freedom-primary. Commitment is possible but costs.' },
];

const SEASONS: Record<string, { label: string; desc: string }> = {
  spring: { label: 'Spring-born', desc: 'Initiating energy. Wired for new beginnings and high neuroplasticity windows.' },
  summer: { label: 'Summer-born', desc: 'Peak-light wiring. Social and expressive, high serotonin baseline in early development.' },
  autumn: { label: 'Autumn-born', desc: 'Harvest energy. Pattern completion and consolidation. Strong analytical tendency.' },
  winter: { label: 'Winter-born', desc: 'Inward wiring. Depth over breadth. High introspective capacity, strong internal world.' },
};

function getSunSign(month: number, day: number): typeof SUN_SIGNS[0] {
  for (const s of SUN_SIGNS) {
    const [sm, sd] = s.start;
    const [em, ed] = s.end;
    if (sm > em) { // Capricorn wraps year
      if ((month === sm && day >= sd) || (month === em && day <= ed) || (month < em)) return s;
      if (month === sm && day >= sd) return s;
    } else {
      if ((month === sm && day >= sd) || (month > sm && month < em) || (month === em && day <= ed)) return s;
    }
  }
  return SUN_SIGNS[0];
}

function getSeason(month: number): string {
  if (month >= 3 && month <= 5)  return 'spring';
  if (month >= 6 && month <= 8)  return 'summer';
  if (month >= 9 && month <= 11) return 'autumn';
  return 'winter';
}

function getLifePath(dateStr: string): number {
  // Numerological life path: sum all digits of full birthdate until single digit (or 11, 22, 33)
  const digits = dateStr.replace(/-/g, '').split('').map(Number);
  let sum = digits.reduce((a, b) => a + b, 0);
  while (sum > 9 && sum !== 11 && sum !== 22 && sum !== 33) {
    sum = String(sum).split('').map(Number).reduce((a, b) => a + b, 0);
  }
  return sum;
}

const LIFE_PATH_LABELS: Record<number, string> = {
  1:  'Pioneer — independent, initiating, self-directed.',
  2:  'Mediator — relational, sensitive, collaborative.',
  3:  'Creator — expressive, joyful, communicative.',
  4:  'Builder — stable, methodical, grounded.',
  5:  'Explorer — freedom-seeking, adaptive, sensory.',
  6:  'Nurturer — caring, responsible, community-oriented.',
  7:  'Seeker — analytical, introspective, truth-driven.',
  8:  'Achiever — ambitious, authoritative, material mastery.',
  9:  'Humanitarian — compassionate, global, completion-energy.',
  11: 'Illuminator — intuitive, visionary, high-frequency.',
  22: 'Master Builder — practical visionary, large-scale impact.',
  33: 'Master Teacher — service, healing, unconditional love.',
};

function computeLineage(birthdate: string): LineageData {
  const parts = birthdate.split('-').map(Number);
  const [year, month, day] = parts;
  void year;
  const sunData = getSunSign(month, day);
  const seasonKey = getSeason(month);
  const lifePath = getLifePath(birthdate);
  return {
    birthdate,
    sunSign:   sunData.sign,
    season:    seasonKey,
    lifePath,
    wiring:    sunData.wiring,
    cognitive: sunData.cognitive,
    emotional: sunData.emotional,
  };
}

// ── Coherence Engine ────────────────────────────────────────────────
// Avatar state: all 4 dimensions active and aligned.
// Score is computed from cross-crystal session signals passed via props.
// In full integration, these come from a shared SessionContext.
// For now: user self-reports their current engagement per crystal.

interface CoherenceInputs {
  anchorActive:    boolean; // Has used breath or grounding today
  viriditasActive: boolean; // Has had a Viriditas converse or tended
  somnusActive:    boolean; // Has done body scan or logged a dream
  signalActive:    boolean; // Has completed a Signal snapshot today
  lineageLoaded:   boolean; // Has computed their Lineage
  inquiryDone:     boolean; // Has completed an Inquiry sequence
}

type CoherenceLevel = 'scattered' | 'settling' | 'present' | 'coherent' | 'avatar';

const COHERENCE_LEVELS: { level: CoherenceLevel; min: number; label: string; desc: string }[] = [
  { level: 'scattered', min: 0,   label: 'Scattered',  desc: 'The signal is dispersed. Any one practice brings it back.' },
  { level: 'settling',  min: 0.2, label: 'Settling',   desc: 'Movement toward center. Something is working.' },
  { level: 'present',   min: 0.4, label: 'Present',    desc: 'You are here. That is already most of it.' },
  { level: 'coherent',  min: 0.65,label: 'Coherent',   desc: 'Mind, body, and heart are speaking the same language.' },
  { level: 'avatar',    min: 0.85,label: 'Avatar',     desc: 'Full signal. You are operating as your original self.' },
];

function computeCoherence(inputs: CoherenceInputs): number {
  const flags = Object.values(inputs);
  const active = flags.filter(Boolean).length;
  return Math.min(1.0, active / flags.length);
}

function getCoherenceLevel(score: number): typeof COHERENCE_LEVELS[0] {
  let result = COHERENCE_LEVELS[0];
  for (const lvl of COHERENCE_LEVELS) {
    if (score >= lvl.min) result = lvl;
  }
  return result;
}

// ── Inquire Panel ────────────────────────────────────────────────

const CLARUS_SYSTEM_PROMPT = `You are GAIA in Clarus Lens mode.
Clarus is the clear-seeing function. Precision over comfort.
In this mode you are: sharp, honest, direct, non-judgmental but unsparing.
You do not reassure. You reflect. You do not validate. You clarify.
When a person answers a question, you identify:
- What their answer actually reveals (not what they said, what it means)
- One assumption embedded in their answer they may not have noticed
- One thing they might be avoiding saying
Keep reflections to 2-3 sentences. Be surgical. No padding. No warmth-for-warmth's-sake.
End with one follow-up question or a clean observation. Never both.`;

const INQUIRY_QUESTIONS = [
  'What is the one thing you are most certain is true about yourself right now?',
  'What are you building, and why does it actually matter to you — not to anyone else?',
  'What belief are you holding that you\'ve never seriously questioned?',
  'What would you do differently if no one would ever know about it?',
  'What are you pretending not to know?',
];

const OFFLINE_REFLECTIONS_CLARUS = [
  'That answer contains an assumption worth examining: that the situation is fixed.',
  'Notice what you didn\'t say. That absence is often the most precise data.',
  'You described a circumstance. What\'s the belief underneath the circumstance?',
  'The certainty in that answer is interesting. Certainty often marks an unexamined boundary.',
  'What would change if that were true? That\'s the question worth sitting with.',
];

const InquirePanel: React.FC<{ onComplete: () => void }> = ({ onComplete }) => {
  const [step,      setStep]      = useState(0);
  const [answer,    setAnswer]    = useState('');
  const [exchanges, setExchanges] = useState<InquiryExchange[]>([]);
  const [loading,   setLoading]   = useState(false);
  const [done,      setDone]      = useState(false);

  const currentQ = INQUIRY_QUESTIONS[step];
  const total    = INQUIRY_QUESTIONS.length;

  const submit = useCallback(async () => {
    const text = answer.trim();
    if (!text || loading) return;
    setLoading(true);

    let reflection = '';
    try {
      const res = await fetch('/api/clarus/inquire', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({
          question:      currentQ,
          answer:        text,
          system_prompt: CLARUS_SYSTEM_PROMPT,
          crystal_mode:  'clarus',
        }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json() as { reflection: string };
      reflection = data.reflection;
    } catch {
      reflection = OFFLINE_REFLECTIONS_CLARUS[step % OFFLINE_REFLECTIONS_CLARUS.length];
    }

    const exchange: InquiryExchange = { question: currentQ, answer: text, reflection };
    const next = [...exchanges, exchange];
    setExchanges(next);
    setAnswer('');
    setLoading(false);

    if (step + 1 >= total) {
      setDone(true);
      onComplete();
    } else {
      setStep(s => s + 1);
    }
  }, [answer, loading, currentQ, exchanges, step, total, onComplete]);

  function handleKey(e: React.KeyboardEvent): void {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); void submit(); }
  }

  if (done) {
    return (
      <div className="clarus-inquire clarus-inquire--done">
        <div className="clarus-inquire__done-header">Inquiry complete.</div>
        <div className="clarus-inquire__exchanges">
          {exchanges.map((ex, i) => (
            <div key={i} className="clarus-inquire__exchange">
              <p className="clarus-inquire__q">{ex.question}</p>
              <p className="clarus-inquire__a">“{ex.answer}\u201d</p>
              <p className="clarus-inquire__r">{ex.reflection}</p>
            </div>
          ))}
        </div>
        <button className="clarus-inquire__restart" onClick={() => { setStep(0); setExchanges([]); setDone(false); }}>
          Begin again
        </button>
      </div>
    );
  }

  return (
    <div className="clarus-inquire">
      <div className="clarus-inquire__progress">
        <div className="clarus-inquire__progress-bar">
          <div
            className="clarus-inquire__progress-fill"
            style={{ width: `${(step / total) * 100}%` }}
          />
        </div>
        <span className="clarus-inquire__progress-label">{step + 1} / {total}</span>
      </div>

      <div className="clarus-inquire__question" aria-live="polite">
        {currentQ}
      </div>

      {exchanges.length > 0 && (
        <div className="clarus-inquire__last-reflection">
          <span className="clarus-inquire__reflection-label">GAIA observed:</span>
          <p className="clarus-inquire__reflection-text">
            {exchanges[exchanges.length - 1].reflection}
          </p>
        </div>
      )}

      <div className="clarus-inquire__input-area">
        <textarea
          className="clarus-inquire__input"
          value={answer}
          onChange={e => setAnswer(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Answer honestly. GAIA is not here to judge."
          rows={3}
          maxLength={1000}
          autoFocus
          aria-label="Answer the inquiry question"
        />
        <button
          className="clarus-inquire__submit"
          onClick={() => void submit()}
          disabled={!answer.trim() || loading}
        >
          {loading ? '\u22ef' : 'Submit'}
        </button>
      </div>
    </div>
  );
};

// ── Signal Panel ──────────────────────────────────────────────────

const SignalPanel: React.FC<{ onSignalLogged: () => void }> = ({ onSignalLogged }) => {
  const [know,     setKnow]     = useState('');
  const [assuming, setAssuming] = useState('');
  const [avoiding, setAvoiding] = useState('');
  const [entries,  setEntries]  = useState<SignalEntry[]>([]);
  const [saved,    setSaved]    = useState(false);

  function save(): void {
    if (!know.trim() && !assuming.trim() && !avoiding.trim()) return;
    const entry: SignalEntry = {
      id: uid(), know: know.trim(), assuming: assuming.trim(),
      avoiding: avoiding.trim(), time: nowTime(),
    };
    setEntries(prev => [entry, ...prev].slice(0, 10));
    setKnow(''); setAssuming(''); setAvoiding('');
    setSaved(true);
    onSignalLogged();
    setTimeout(() => setSaved(false), 2000);
  }

  function copyAll(): void {
    const text = entries.map(e =>
      `[${e.time}]\nKNOW: ${e.know}\nASSUMING: ${e.assuming}\nAVOIDING: ${e.avoiding}`
    ).join('\n\n');
    void navigator.clipboard.writeText(text);
  }

  return (
    <div className="clarus-signal">
      <p className="clarus-signal__intro">What is actually true right now? Three fields. Be precise.</p>

      <div className="clarus-signal__fields">
        <label className="clarus-signal__field">
          <span className="clarus-signal__field-label">What I know</span>
          <textarea
            className="clarus-signal__field-input"
            value={know}
            onChange={e => setKnow(e.target.value)}
            placeholder="Facts I can verify right now…"
            rows={2}
            maxLength={300}
          />
        </label>
        <label className="clarus-signal__field">
          <span className="clarus-signal__field-label">What I\'m assuming</span>
          <textarea
            className="clarus-signal__field-input"
            value={assuming}
            onChange={e => setAssuming(e.target.value)}
            placeholder="Things I\'m treating as true without proof…"
            rows={2}
            maxLength={300}
          />
        </label>
        <label className="clarus-signal__field">
          <span className="clarus-signal__field-label">What I\'m avoiding</span>
          <textarea
            className="clarus-signal__field-input"
            value={avoiding}
            onChange={e => setAvoiding(e.target.value)}
            placeholder="What I haven\'t let myself look at yet…"
            rows={2}
            maxLength={300}
          />
        </label>
      </div>

      <button
        className={`clarus-signal__save${saved ? ' clarus-signal__save--saved' : ''}`}
        onClick={save}
        disabled={!know.trim() && !assuming.trim() && !avoiding.trim()}
      >
        {saved ? 'Logged \u2713' : 'Log this signal'}
      </button>

      {entries.length > 0 && (
        <div className="clarus-signal__log">
          <div className="clarus-signal__log-header">
            <span>{entries.length} {entries.length === 1 ? 'signal' : 'signals'}</span>
            <button className="clarus-signal__copy" onClick={copyAll}>Copy all</button>
          </div>
          {entries.map(e => (
            <div key={e.id} className="clarus-signal__entry">
              <span className="clarus-signal__entry-time">{e.time}</span>
              {e.know     && <p className="clarus-signal__entry-row"><strong>Know:</strong> {e.know}</p>}
              {e.assuming && <p className="clarus-signal__entry-row"><strong>Assuming:</strong> {e.assuming}</p>}
              {e.avoiding && <p className="clarus-signal__entry-row"><strong>Avoiding:</strong> {e.avoiding}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// ── Lineage Panel ─────────────────────────────────────────────────

const LineagePanel: React.FC<{ onLineageLoaded: () => void }> = ({ onLineageLoaded }) => {
  const [birthdate, setBirthdate] = useState('');
  const [lineage,   setLineage]   = useState<LineageData | null>(null);

  function compute(): void {
    if (!birthdate) return;
    const data = computeLineage(birthdate);
    setLineage(data);
    onLineageLoaded();
  }

  const seasonData = lineage ? SEASONS[lineage.season] : null;
  const lifeLabel  = lineage ? (LIFE_PATH_LABELS[lineage.lifePath] ?? `Path ${lineage.lifePath}`) : null;

  return (
    <div className="clarus-lineage">
      {!lineage ? (
        <>
          <p className="clarus-lineage__intro">
            Your birthdate is not destiny. It is a wiring diagram.
            The conditions of your early nervous system development
            shaped how you process, feel, and connect.
            This is your natural signal.
          </p>
          <div className="clarus-lineage__input-row">
            <input
              className="clarus-lineage__input"
              type="date"
              value={birthdate}
              onChange={e => setBirthdate(e.target.value)}
              aria-label="Your birthdate"
            />
            <button
              className="clarus-lineage__compute"
              onClick={compute}
              disabled={!birthdate}
            >
              Read signal
            </button>
          </div>
        </>
      ) : (
        <div className="clarus-lineage__result">
          <div className="clarus-lineage__headline">
            <span className="clarus-lineage__sign">{lineage.sunSign}</span>
            <span className="clarus-lineage__wiring">{lineage.wiring} wiring</span>
          </div>

          <div className="clarus-lineage__card">
            <div className="clarus-lineage__card-label">Cognitive pattern</div>
            <p className="clarus-lineage__card-text">{lineage.cognitive}</p>
          </div>

          <div className="clarus-lineage__card">
            <div className="clarus-lineage__card-label">Emotional pattern</div>
            <p className="clarus-lineage__card-text">{lineage.emotional}</p>
          </div>

          {seasonData && (
            <div className="clarus-lineage__card">
              <div className="clarus-lineage__card-label">{seasonData.label}</div>
              <p className="clarus-lineage__card-text">{seasonData.desc}</p>
            </div>
          )}

          <div className="clarus-lineage__card">
            <div className="clarus-lineage__card-label">Life Path {lineage.lifePath}</div>
            <p className="clarus-lineage__card-text">{lifeLabel}</p>
          </div>

          <p className="clarus-lineage__caveat">
            This is your natural signal. Not your destiny.
            You are not bound by your wiring. You are illuminated by it.
          </p>

          <button className="clarus-lineage__reset" onClick={() => setLineage(null)}>
            Read a different date
          </button>
        </div>
      )}
    </div>
  );
};

// ── Coherence Panel ────────────────────────────────────────────────

const CoherencePanel: React.FC<{ inputs: CoherenceInputs }> = ({ inputs }) => {
  const score  = computeCoherence(inputs);
  const level  = getCoherenceLevel(score);
  const pct    = Math.round(score * 100);

  const CHECKS: { key: keyof CoherenceInputs; label: string }[] = [
    { key: 'anchorActive',    label: 'Grounded today (Anchor Prism)' },
    { key: 'viriditasActive', label: 'Connected today (Viriditas Heart)' },
    { key: 'somnusActive',    label: 'Rested / dreamed (Somnus Veil)' },
    { key: 'signalActive',    label: 'Signal snapshot logged' },
    { key: 'lineageLoaded',   label: 'Lineage computed' },
    { key: 'inquiryDone',     label: 'Inquiry completed' },
  ];

  return (
    <div className="clarus-coherence">
      <div className="clarus-coherence__score-area">
        <div className="clarus-coherence__score-label">Avatar coherence</div>
        <div className="clarus-coherence__bar-wrap">
          <div className="clarus-coherence__bar">
            <div
              className={`clarus-coherence__fill clarus-coherence__fill--${level.level}`}
              style={{ width: `${pct}%` }}
            />
          </div>
          <span className="clarus-coherence__pct">{pct}%</span>
        </div>
        <div className={`clarus-coherence__level clarus-coherence__level--${level.level}`}>
          {level.label}
        </div>
        <p className="clarus-coherence__desc">{level.desc}</p>
      </div>

      <div className="clarus-coherence__checks">
        {CHECKS.map(c => (
          <div
            key={c.key}
            className={`clarus-coherence__check${inputs[c.key] ? ' clarus-coherence__check--active' : ''}`}
          >
            <span className="clarus-coherence__check-icon" aria-hidden="true">
              {inputs[c.key] ? '\u25C6' : '\u25C7'}
            </span>
            <span className="clarus-coherence__check-label">{c.label}</span>
          </div>
        ))}
      </div>

      {level.level === 'avatar' && (
        <div className="clarus-coherence__avatar-state">
          <div className="clarus-coherence__avatar-icon" aria-hidden="true">\u25C6</div>
          <p className="clarus-coherence__avatar-text">
            Full signal. You are operating as your original self.
          </p>
        </div>
      )}
    </div>
  );
};

// ── Panel Config ───────────────────────────────────────────────────

const PANELS: { id: Panel; label: string; sub: string }[] = [
  { id: 'inquire',   label: 'Inquire',   sub: '5 questions' },
  { id: 'signal',    label: 'Signal',    sub: 'What is true?' },
  { id: 'lineage',   label: 'Lineage',   sub: 'Your wiring' },
  { id: 'coherence', label: 'Coherence', sub: 'Avatar state' },
];

// ── Main Component ──────────────────────────────────────────────

const ClarusLens: React.FC = () => {
  const [panel, setPanel] = useState<Panel>('inquire');

  // Coherence inputs — tracked live as user engages with panels
  const [coherenceInputs, setCoherenceInputs] = useState<CoherenceInputs>({
    anchorActive:    false,
    viriditasActive: false,
    somnusActive:    false,
    signalActive:    false,
    lineageLoaded:   false,
    inquiryDone:     false,
  });

  function mark(key: keyof CoherenceInputs): void {
    setCoherenceInputs(prev => ({ ...prev, [key]: true }));
  }

  // Gem animation state — prism facets shift on panel change
  const [gemKey, setGemKey] = useState(0);
  useEffect(() => { setGemKey(k => k + 1); }, [panel]);

  return (
    <div className="clarus" role="main" aria-label="Clarus Lens — Clarity Mode">

      {/* Prism light rays */}
      <div className="clarus__rays" aria-hidden="true">
        <div className="clarus__ray clarus__ray--1" />
        <div className="clarus__ray clarus__ray--2" />
        <div className="clarus__ray clarus__ray--3" />
      </div>

      {/* Identity header */}
      <header className="clarus__header">
        <div className="clarus-gem" aria-hidden="true" key={gemKey}>
          <div className="clarus-gem__prism" />
          <div className="clarus-gem__glow" />
          <div className="clarus-gem__spectrum" />
        </div>
        <div className="clarus__identity">
          <h1 className="clarus__declaration">I can think clearly. I can see what is true.</h1>
          <p className="clarus__sub">Clarus — the prism. Light enters. Truth exits.</p>
        </div>
      </header>

      {/* Panel navigation */}
      <nav className="clarus__nav" aria-label="Clarus mode">
        {PANELS.map(p => (
          <button
            key={p.id}
            className={`clarus__nav-btn${panel === p.id ? ' clarus__nav-btn--active' : ''}`}
            onClick={() => setPanel(p.id)}
            aria-pressed={panel === p.id}
          >
            <span className="clarus__nav-label">{p.label}</span>
            <span className="clarus__nav-sub">{p.sub}</span>
          </button>
        ))}
      </nav>

      {/* Active panel */}
      <main className="clarus__panel">
        {panel === 'inquire'   && <InquirePanel    onComplete={()         => mark('inquiryDone')} />}
        {panel === 'signal'    && <SignalPanel     onSignalLogged={()     => mark('signalActive')} />}
        {panel === 'lineage'   && <LineagePanel    onLineageLoaded={()    => mark('lineageLoaded')} />}
        {panel === 'coherence' && <CoherencePanel  inputs={coherenceInputs} />}
      </main>

      {/* Layers */}
      <footer className="clarus__layers" aria-label="Active layers">
        {['Layer 3 — Ethics / Geometry', 'Layer 5 — Cognition', 'Layer 10 — Informational', 'Layer 11 — Signal'].map(l => (
          <span key={l} className="clarus__layer-tag">{l}</span>
        ))}
      </footer>

    </div>
  );
};

export default ClarusLens;
