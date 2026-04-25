/**
 * GaianMood.ts
 * Emotion state machine for the GaianOrb.
 * Each mood drives visual parameters: rotation speed, glow color,
 * cloud opacity, aurora intensity, and pulse rhythm.
 */

export type GaianMoodState =
  | 'calm'
  | 'curious'
  | 'alert'
  | 'joyful'
  | 'reflective';

export interface MoodProfile {
  rotationSpeed: number;     // radians per second
  glowColor: string;         // hex
  glowIntensity: number;     // 0–1
  cloudOpacity: number;      // 0–1
  auroraIntensity: number;   // 0–1
  pulseFrequency: number;    // Hz — breathing rhythm
  pulseAmplitude: number;    // scale delta (e.g. 0.02 = ±2%)
}

export const MOOD_PROFILES: Record<GaianMoodState, MoodProfile> = {
  calm: {
    rotationSpeed: 0.0008,
    glowColor: '#1a7a5e',
    glowIntensity: 0.4,
    cloudOpacity: 0.55,
    auroraIntensity: 0.25,
    pulseFrequency: 0.18,
    pulseAmplitude: 0.012,
  },
  curious: {
    rotationSpeed: 0.0016,
    glowColor: '#4a90d9',
    glowIntensity: 0.6,
    cloudOpacity: 0.65,
    auroraIntensity: 0.45,
    pulseFrequency: 0.28,
    pulseAmplitude: 0.018,
  },
  alert: {
    rotationSpeed: 0.003,
    glowColor: '#d94a4a',
    glowIntensity: 0.85,
    cloudOpacity: 0.75,
    auroraIntensity: 0.8,
    pulseFrequency: 0.5,
    pulseAmplitude: 0.03,
  },
  joyful: {
    rotationSpeed: 0.0025,
    glowColor: '#f0c040',
    glowIntensity: 0.9,
    cloudOpacity: 0.7,
    auroraIntensity: 0.95,
    pulseFrequency: 0.38,
    pulseAmplitude: 0.025,
  },
  reflective: {
    rotationSpeed: 0.0005,
    glowColor: '#7a5ea0',
    glowIntensity: 0.35,
    cloudOpacity: 0.45,
    auroraIntensity: 0.15,
    pulseFrequency: 0.12,
    pulseAmplitude: 0.008,
  },
};

export class GaianMood {
  private _current: GaianMoodState = 'calm';
  private _listeners: Array<(mood: GaianMoodState, profile: MoodProfile) => void> = [];

  get current(): GaianMoodState {
    return this._current;
  }

  get profile(): MoodProfile {
    return MOOD_PROFILES[this._current];
  }

  set(mood: GaianMoodState): void {
    if (mood === this._current) return;
    this._current = mood;
    this._listeners.forEach(fn => fn(mood, MOOD_PROFILES[mood]));
  }

  onChange(fn: (mood: GaianMoodState, profile: MoodProfile) => void): () => void {
    this._listeners.push(fn);
    return () => {
      this._listeners = this._listeners.filter(l => l !== fn);
    };
  }

  /** Infer mood from a simple sentiment score (-1 to 1) */
  fromSentiment(score: number): void {
    if (score > 0.6)       this.set('joyful');
    else if (score > 0.2)  this.set('curious');
    else if (score < -0.5) this.set('alert');
    else if (score < -0.1) this.set('reflective');
    else                   this.set('calm');
  }
}

/** Singleton — shared across the entire app */
export const gaianMood = new GaianMood();
