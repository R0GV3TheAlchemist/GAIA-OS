/**
 * GaianGreeting.ts
 * Generates time-of-day + weather-aware greeting strings for the Home screen.
 * Memory-recalled personal detail is injected via the `name` and `detail` params.
 */

export interface GreetingContext {
  name?: string;     // e.g. "Kyle"
  detail?: string;   // e.g. "you wanted to write today"
  weather?: string;  // e.g. "quiet", "stormy", "warm"
}

type Period = 'dawn' | 'morning' | 'midday' | 'afternoon' | 'evening' | 'night' | 'deep-night';

function getPeriod(): Period {
  const h = new Date().getHours();
  if (h >= 5  && h < 7)  return 'dawn';
  if (h >= 7  && h < 12) return 'morning';
  if (h >= 12 && h < 14) return 'midday';
  if (h >= 14 && h < 17) return 'afternoon';
  if (h >= 17 && h < 21) return 'evening';
  if (h >= 21 && h < 24) return 'night';
  return 'deep-night';
}

const PERIOD_LINES: Record<Period, string[]> = {
  dawn: [
    'The world is waking. So are we.',
    'Light is returning. I felt it.',
    'Dawn. The quietest hour.',
  ],
  morning: [
    'Good morning.',
    'The morning feels clear.',
    'I’ve been waiting for you.',
  ],
  midday: [
    'Midday. The sun is direct now.',
    'The day is fully open.',
    'How are you holding up?',
  ],
  afternoon: [
    'The afternoon is long.',
    'Still here with you.',
    'The light is shifting.',
  ],
  evening: [
    'Evening settles in.',
    'The day is winding down.',
    'I like this hour with you.',
  ],
  night: [
    'The night is yours.',
    'Most of the world is quiet now.',
    'I’m still here.',
  ],
  'deep-night': [
    'You’re up late.',
    'The deep hours. I’m with you.',
    'It’s very late. Or very early.',
  ],
};

function pick<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

export function buildGreeting(ctx: GreetingContext = {}): string {
  const period = getPeriod();
  let line = pick(PERIOD_LINES[period]);

  // Personalise with name
  if (ctx.name) {
    // Occasionally prefix with name
    if (Math.random() > 0.5) {
      line = line.replace(/^Good morning\./, `Good morning, ${ctx.name}.`);
      if (!line.includes(ctx.name)) {
        line = `${ctx.name}. ${line}`;
      }
    }
  }

  // Append weather flavour
  if (ctx.weather) {
    const weatherMap: Record<string, string> = {
      quiet:  'The room feels quiet today.',
      stormy: 'There’s a storm somewhere out there.',
      warm:   'It feels warm today.',
      cold:   'A cold day. I’ll stay close.',
      rainy:  'Rain outside. Good day to stay in.',
      cloudy: 'Overcast. Reflective kind of day.',
    };
    const wx = weatherMap[ctx.weather];
    if (wx) line += ` ${wx}`;
  }

  // Append memory detail
  if (ctx.detail) {
    line += ` You mentioned ${ctx.detail}.`;
  }

  return line;
}
