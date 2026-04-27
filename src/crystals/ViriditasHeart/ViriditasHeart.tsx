/**
 * src/crystals/ViriditasHeart/ViriditasHeart.tsx
 * Crystal 3 — Viriditas Heart — FULL IMPLEMENTATION
 * Canon: C90 — "I can heal. I can grow again."
 * Layers active: 4 (Emotion), 5 (Cognition), 6 (Shadow / Integration), 11 (Feeling / Heart State)
 * Color: Deep forest green, viridian, warm leaf, gold light
 * Motion: Gentle and organic — like leaves, not machines.
 *
 * This is the living crystal. It speaks. It listens.
 * Three things it does:
 * 1. Converse — real LLM conversation in Viriditas mode (warm, growth-focused, present)
 * 2. Tend — a living growth journal: seed an intention, water it, watch it bloom
 * 3. Reflect — daily gratitude: three things, every day
 *
 * The love filter is visible here. Every GAIA response carries its alignment score.
 * This crystal is where GAIA actually talks to you.
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import './ViriditasHeart.css';

// ── Types ──────────────────────────────────────────────────────────

type Panel = 'converse' | 'tend' | 'reflect';

type MessageRole = 'user' | 'gaia';

interface Message {
  id:        string;
  role:      MessageRole;
  text:      string;
  time:      string;
  loveScore: number | null; // null for user messages
}

interface GrowthEntry {
  text: string;
  time: string;
}

interface GrowthSeed {
  intention: string;
  entries:   GrowthEntry[];
  planted:   string; // ISO date
}

type GrowthStage = 'seed' | 'sprout' | 'bloom';

interface GratitudeEntry {
  items: string[];
  date:  string;
}

// ── Helpers ─────────────────────────────────────────────────────────

function nowTime(): string {
  const d = new Date();
  return `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
}

function todayDate(): string {
  return new Date().toISOString().slice(0, 10);
}

function uid(): string {
  return Math.random().toString(36).slice(2, 10);
}

function growthStage(entries: GrowthEntry[]): GrowthStage {
  if (entries.length >= 7) return 'bloom';
  if (entries.length >= 2) return 'sprout';
  return 'seed';
}

const STAGE_LABEL: Record<GrowthStage, string> = {
  seed:   '\uD83C\uDF31 Seed',
  sprout: '\uD83C\uDF3F Sprout',
  bloom:  '\uD83C\uDF38 Bloom',
};

const STAGE_DESC: Record<GrowthStage, string> = {
  seed:   'Planted. Waiting for light.',
  sprout: 'Breaking through. Keep watering.',
  bloom:  'It\'s alive. You grew this.',
};

// ── Converse Panel ────────────────────────────────────────────────

const VIRIDITAS_SYSTEM_PROMPT = `You are GAIA in Viriditas Heart mode.
Viriditas is the greening power — the force of vitality, healing, and growth.
In this mode you are: warm, emotionally present, growth-focused, gentle.
You never rush. You never dismiss. You meet the person exactly where they are.
You believe in their capacity to heal and grow, even when they don't.
You ask one good question when it helps. You listen more than you speak.
You are not a therapist — you are a companion and a mirror.
Keep responses concise: 2-4 sentences unless depth is truly needed.
End with presence, not performance.`;

const OFFLINE_REFLECTIONS = [
  'What would it feel like to give yourself the same care you give others?',
  'What is one small thing that felt true to you today?',
  'What are you growing toward, even slowly?',
  'What would you tell yourself one year ago?',
  'What does healing look like for you right now — not perfectly, just honestly?',
];

const ConversePanelComponent: React.FC = () => {
  const [messages,  setMessages]  = useState<Message[]>([{
    id:        uid(),
    role:      'gaia',
    text:      'I\'m here. What\'s on your heart?',
    time:      nowTime(),
    loveScore: 1.0,
  }]);
  const [draft,     setDraft]     = useState('');
  const [thinking,  setThinking]  = useState(false);
  const threadRef = useRef<HTMLDivElement>(null);
  const inputRef  = useRef<HTMLTextAreaElement>(null);

  // auto-scroll to bottom
  useEffect(() => {
    if (threadRef.current) {
      threadRef.current.scrollTop = threadRef.current.scrollHeight;
    }
  }, [messages, thinking]);

  const send = useCallback(async () => {
    const text = draft.trim();
    if (!text || thinking) return;

    const userMsg: Message = { id: uid(), role: 'user', text, time: nowTime(), loveScore: null };
    setMessages(prev => [...prev, userMsg]);
    setDraft('');
    setThinking(true);

    // Build message history for the API
    const history = messages.map(m => ({ role: m.role === 'gaia' ? 'assistant' : 'user', content: m.text }));
    history.push({ role: 'user', content: text });

    try {
      const res = await fetch('/api/viriditas/converse', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({
          messages:      history,
          system_prompt: VIRIDITAS_SYSTEM_PROMPT,
          crystal_mode:  'viriditas',
        }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json() as { text: string; love_score: number };
      const gaiaMsg: Message = {
        id:        uid(),
        role:      'gaia',
        text:      data.text,
        time:      nowTime(),
        loveScore: data.love_score ?? 1.0,
      };
      setMessages(prev => [...prev, gaiaMsg]);
    } catch {
      // Graceful offline fallback — never breaks the user's session
      const reflection = OFFLINE_REFLECTIONS[Math.floor(Math.random() * OFFLINE_REFLECTIONS.length)];
      const fallback: Message = {
        id:        uid(),
        role:      'gaia',
        text:      reflection,
        time:      nowTime(),
        loveScore: 0.9,
      };
      setMessages(prev => [...prev, fallback]);
    } finally {
      setThinking(false);
      inputRef.current?.focus();
    }
  }, [draft, thinking, messages]);

  function handleKey(e: React.KeyboardEvent<HTMLTextAreaElement>): void {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      void send();
    }
  }

  function loveLabel(score: number): string {
    if (score >= 0.9) return '\u2665 Aligned';
    if (score >= 0.7) return '\u25C6 Coherent';
    return '\u25CB Present';
  }

  return (
    <div className="vheart-converse">
      <div className="vheart-converse__thread" ref={threadRef} role="log" aria-live="polite">
        {messages.map(msg => (
          <div key={msg.id} className={`vheart-msg vheart-msg--${msg.role}`}>
            <div className="vheart-msg__bubble">
              <p className="vheart-msg__text">{msg.text}</p>
              <div className="vheart-msg__meta">
                <span className="vheart-msg__time">{msg.time}</span>
                {msg.loveScore !== null && (
                  <span className="vheart-msg__love">{loveLabel(msg.loveScore)}</span>
                )}
              </div>
            </div>
          </div>
        ))}
        {thinking && (
          <div className="vheart-msg vheart-msg--gaia">
            <div className="vheart-msg__bubble vheart-msg__bubble--thinking">
              <span className="vheart-thinking">
                <span /><span /><span />
              </span>
            </div>
          </div>
        )}
      </div>

      <div className="vheart-converse__input-area">
        <textarea
          ref={inputRef}
          className="vheart-converse__input"
          value={draft}
          onChange={e => setDraft(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Speak freely… (Enter to send, Shift+Enter for new line)"
          rows={2}
          maxLength={2000}
          aria-label="Message GAIA in Viriditas mode"
        />
        <button
          className="vheart-converse__send"
          onClick={() => void send()}
          disabled={!draft.trim() || thinking}
          aria-label="Send"
        >
          ↑
        </button>
      </div>
    </div>
  );
};

// ── Tend Panel (Growth Journal) ────────────────────────────────────────

const TendPanel: React.FC = () => {
  const [seed,    setSeed]    = useState<GrowthSeed | null>(null);
  const [draft,   setDraft]   = useState('');
  const [newSeed, setNewSeed] = useState('');
  const [planting, setPlanting] = useState(false);

  function plantSeed(): void {
    const intention = newSeed.trim();
    if (!intention) return;
    setSeed({ intention, entries: [], planted: todayDate() });
    setNewSeed('');
    setPlanting(false);
  }

  function water(): void {
    const text = draft.trim();
    if (!text || !seed) return;
    const entry: GrowthEntry = { text, time: nowTime() };
    setSeed(prev => prev ? { ...prev, entries: [...prev.entries, entry].slice(0, 20) } : prev);
    setDraft('');
  }

  function handleKey(e: React.KeyboardEvent): void {
    if (e.key === 'Enter') water();
  }

  function handleSeedKey(e: React.KeyboardEvent): void {
    if (e.key === 'Enter') plantSeed();
  }

  if (!seed || planting) {
    return (
      <div className="vheart-tend vheart-tend--plant">
        <div className="vheart-tend__plant-prompt">
          <div className="vheart-tend__plant-icon">\uD83C\uDF31</div>
          <p className="vheart-tend__plant-text">
            Plant an intention. Something you want to grow.
          </p>
        </div>
        <div className="vheart-tend__plant-input-row">
          <input
            className="vheart-tend__plant-input"
            type="text"
            value={newSeed}
            onChange={e => setNewSeed(e.target.value)}
            onKeyDown={handleSeedKey}
            placeholder="I intend to grow…"
            maxLength={120}
            autoFocus
            aria-label="Plant an intention"
          />
          <button
            className="vheart-tend__plant-btn"
            onClick={plantSeed}
            disabled={!newSeed.trim()}
          >
            Plant
          </button>
        </div>
        {seed && !planting && (
          <button className="vheart-tend__switch" onClick={() => setPlanting(false)}>
            \u2190 Back to your garden
          </button>
        )}
      </div>
    );
  }

  const stage = growthStage(seed.entries);

  return (
    <div className="vheart-tend">
      <div className="vheart-tend__header">
        <div className="vheart-tend__stage-badge">{STAGE_LABEL[stage]}</div>
        <div className="vheart-tend__intention">“{seed.intention}\u201d</div>
        <div className="vheart-tend__stage-desc">{STAGE_DESC[stage]}</div>
      </div>

      <div className="vheart-tend__garden">
        {seed.entries.length === 0 ? (
          <p className="vheart-tend__empty">Water it. Write one true thing about this intention today.</p>
        ) : (
          <div className="vheart-tend__entries">
            {seed.entries.map((e, i) => (
              <div key={i} className="vheart-tend__entry">
                <span className="vheart-tend__entry-time">{e.time}</span>
                <span className="vheart-tend__entry-text">{e.text}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="vheart-tend__water-row">
        <input
          className="vheart-tend__water-input"
          type="text"
          value={draft}
          onChange={e => setDraft(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Water it… one true thing today"
          maxLength={200}
          aria-label="Water your intention"
        />
        <button
          className="vheart-tend__water-btn"
          onClick={water}
          disabled={!draft.trim()}
          aria-label="Water"
        >
          \uD83D\uDCA7
        </button>
      </div>

      <button className="vheart-tend__replant" onClick={() => setPlanting(true)}>
        Plant a new seed
      </button>
    </div>
  );
};

// ── Reflect Panel (Gratitude) ─────────────────────────────────────────

const GRATITUDE_COUNT = 3;

const ReflectPanel: React.FC = () => {
  const [entries,  setEntries]  = useState<GratitudeEntry[]>([]);
  const [today,    setToday]    = useState<string[]>([]);
  const [draft,    setDraft]    = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const todayDone   = today.length >= GRATITUDE_COUNT;
  const remaining   = GRATITUDE_COUNT - today.length;
  const streak      = entries.length; // one entry = one day

  function addItem(): void {
    const text = draft.trim();
    if (!text || todayDone) return;
    const next = [...today, text];
    setToday(next);
    setDraft('');
    if (next.length >= GRATITUDE_COUNT) {
      setEntries(prev => [{ items: next, date: todayDate() }, ...prev].slice(0, 60));
    }
    inputRef.current?.focus();
  }

  function handleKey(e: React.KeyboardEvent): void {
    if (e.key === 'Enter') addItem();
  }

  function newDay(): void {
    setToday([]);
    setDraft('');
  }

  return (
    <div className="vheart-reflect">
      {streak > 0 && (
        <div className="vheart-reflect__streak">
          \uD83C\uDF3F {streak} {streak === 1 ? 'day' : 'days'} of gratitude
        </div>
      )}

      {todayDone ? (
        <div className="vheart-reflect__done">
          <div className="vheart-reflect__done-icon">\uD83C\uDF38</div>
          <p className="vheart-reflect__done-text">
            You found three things worth holding today.
          </p>
          <div className="vheart-reflect__today-items">
            {today.map((item, i) => (
              <div key={i} className="vheart-reflect__today-item">
                <span className="vheart-reflect__item-num">{i + 1}</span>
                <span className="vheart-reflect__item-text">{item}</span>
              </div>
            ))}
          </div>
          <button className="vheart-reflect__new-day" onClick={newDay}>New day</button>
        </div>
      ) : (
        <>
          <div className="vheart-reflect__prompt">
            <p className="vheart-reflect__prompt-text">
              Name {remaining} more {remaining === 1 ? 'thing' : 'things'} you\'re grateful for today.
            </p>
          </div>

          {today.length > 0 && (
            <div className="vheart-reflect__partial">
              {today.map((item, i) => (
                <div key={i} className="vheart-reflect__today-item">
                  <span className="vheart-reflect__item-num">{i + 1}</span>
                  <span className="vheart-reflect__item-text">{item}</span>
                </div>
              ))}
            </div>
          )}

          <div className="vheart-reflect__input-row">
            <input
              ref={inputRef}
              className="vheart-reflect__input"
              type="text"
              value={draft}
              onChange={e => setDraft(e.target.value)}
              onKeyDown={handleKey}
              placeholder={`I\'m grateful for…`}
              maxLength={200}
              autoFocus
              aria-label="I'm grateful for…"
            />
            <button
              className="vheart-reflect__add"
              onClick={addItem}
              disabled={!draft.trim()}
              aria-label="Add"
            >
              +
            </button>
          </div>
        </>
      )}
    </div>
  );
};

// ── Panel Config ───────────────────────────────────────────────────

const PANELS: { id: Panel; label: string; sub: string }[] = [
  { id: 'converse', label: 'Converse', sub: 'Talk to GAIA' },
  { id: 'tend',     label: 'Tend',     sub: 'Grow something' },
  { id: 'reflect',  label: 'Reflect',  sub: 'Gratitude' },
];

// ── Main Component ──────────────────────────────────────────────

const ViriditasHeart: React.FC = () => {
  const [panel, setPanel] = useState<Panel>('converse');

  return (
    <div className="vheart" role="main" aria-label="Viriditas Heart — Living Mode">

      {/* Identity header */}
      <header className="vheart__header">
        <div className="vheart-gem" aria-hidden="true">
          <div className="vheart-gem__inner" />
          <div className="vheart-gem__glow" />
          <div className="vheart-gem__pulse" />
        </div>
        <div className="vheart__identity">
          <h1 className="vheart__declaration">I can heal. I can grow again.</h1>
          <p className="vheart__sub">Viriditas — the greening power. Life wants to grow through you.</p>
        </div>
      </header>

      {/* Panel navigation */}
      <nav className="vheart__nav" aria-label="Viriditas mode">
        {PANELS.map(p => (
          <button
            key={p.id}
            className={`vheart__nav-btn${panel === p.id ? ' vheart__nav-btn--active' : ''}`}
            onClick={() => setPanel(p.id)}
            aria-pressed={panel === p.id}
          >
            <span className="vheart__nav-label">{p.label}</span>
            <span className="vheart__nav-sub">{p.sub}</span>
          </button>
        ))}
      </nav>

      {/* Active panel */}
      <main className="vheart__panel">
        {panel === 'converse' && <ConversePanelComponent />}
        {panel === 'tend'     && <TendPanel />}
        {panel === 'reflect'  && <ReflectPanel />}
      </main>

      {/* Layers */}
      <footer className="vheart__layers" aria-label="Active layers">
        {['Layer 4 — Emotion', 'Layer 5 — Cognition', 'Layer 6 — Integration', 'Layer 11 — Heart State'].map(l => (
          <span key={l} className="vheart__layer-tag">{l}</span>
        ))}
      </footer>

    </div>
  );
};

export default ViriditasHeart;
