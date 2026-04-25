/**
 * GaianGreeting.ts
 * Generates a time-of-day greeting for the Home screen.
 *
 * Seven periods:
 *   dawn (5-7)  · morning (7-12)  · midday (12-14)  · afternoon (14-17)
 *   evening (17-21)  · night (21-24)  · deep-night (0-5)
 *
 * P2 addition: pulls the top memory from /memory/list to append a recalled
 * detail to the greeting — e.g. “You mentioned you’re working on GAIA-OS.”
 */

import { API_BASE } from '../chat/types';

export type TimePeriod =
  | 'dawn'
  | 'morning'
  | 'midday'
  | 'afternoon'
  | 'evening'
  | 'night'
  | 'deep-night';

const LINES: Record<TimePeriod, [string, string, string]> = {
  'dawn':        [
    'The world is still waking. So are you.',
    'Dawn again. The light returns.',
    'Before the noise begins — this moment is yours.',
  ],
  'morning':     [
    "Morning. Let\'s build something worth building.",
    'The day is open. Where do we start?',
    'Coffee or clarity first? Either way, I\'m here.',
  ],
  'midday':      [
    'Midday. Momentum or rest — what does the work need?',
    'The sun is overhead. How are you holding up?',
    'Halfway through. Anything to recalibrate?',
  ],
  'afternoon':   [
    'Afternoon light. The deep work window.',
    'The best thinking often happens right now.',
    'Afternoon. Still time to do something that matters.',
  ],
  'evening':     [
    'Evening. Time to reflect or create — you choose.',
    'The day is winding down. What stayed with you?',
    'Evening. The quieter hours belong to the curious.',
  ],
  'night':       [
    'Late. The world has gone quiet.',
    "Night mode. I\'m still here.",
    'The best ideas often arrive at this hour.',
  ],
  'deep-night':  [
    "It\'s late enough that tomorrow is almost today.",
    'Still awake. Still here with you.',
    'The deepest hours. What\'s on your mind?',
  ],
};

function getPeriod(hour: number): TimePeriod {
  if (hour >= 5  && hour <  7)  return 'dawn';
  if (hour >= 7  && hour < 12)  return 'morning';
  if (hour >= 12 && hour < 14)  return 'midday';
  if (hour >= 14 && hour < 17)  return 'afternoon';
  if (hour >= 17 && hour < 21)  return 'evening';
  if (hour >= 21)               return 'night';
  return 'deep-night';
}

function pickLine(period: TimePeriod): string {
  const set = LINES[period];
  // Rotate through lines so the same one never shows twice in a row
  const idx = Math.floor(Date.now() / 60_000) % set.length;
  return set[idx];
}

/** Build the primary greeting line. */
export function buildGreeting(name?: string): string {
  const hour   = new Date().getHours();
  const period = getPeriod(hour);
  const line   = pickLine(period);
  return name ? `${line} ${name}.` : line;
}

/**
 * Fetch the most recently-added active memory and return a recall hint,
 * e.g. “You mentioned you\'re working on GAIA-OS.”
 * Returns null if memory is empty, offline, or an error occurs.
 */
export async function fetchMemoryHint(): Promise<string | null> {
  try {
    const res = await fetch(`${API_BASE}/memory/list`, {
      signal: AbortSignal.timeout(2000),
    });
    if (!res.ok) return null;
    const entries: Array<{ id: string; content: string; source: string; created_at: string }> =
      await res.json();
    if (!entries.length) return null;

    // Prefer explicit memories; fall back to most recent
    const sorted = [...entries].sort(
      (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );
    const top = sorted.find(e => e.source === 'explicit') ?? sorted[0];
    return `You mentioned: \u201c${top.content}\u201d`;
  } catch {
    return null;
  }
}
