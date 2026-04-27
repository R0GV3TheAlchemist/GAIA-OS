/**
 * src/shared/LoveFilter.tsx
 * ─────────────────────────────────────────────────────────────────────────────
 * Axiom II — Visual Indicator.
 * "Every intention is filtered through love."
 *
 * Canon: C90, C-SINGULARITY (Axiom II), C-FOUNDATION (love filter)
 * The love filter is not invisible. It has presence — a glow, a quality of light.
 * The coherence score (0.0–1.0) is returned from the backend love filter layer.
 *
 *   1.0  →  full glow — intention aligned, amplified
 *   0.5  →  warm glow — intention transformed toward coherence
 *   0.0  →  no glow   — intention blocked (rare — used as feedback)
 *
 * Visible in: Sovereign Core (full) and Clarus Lens (precision mode)
 * Present but subtle in: Viriditas Heart, Anchor Prism
 * Minimal in: Somnus Veil (rest mode — no scoring)
 * ─────────────────────────────────────────────────────────────────────────────
 */

import React from 'react';
import { useCrystal } from '../hooks/useCrystal';

interface LoveFilterProps {
  /** Override — if not provided, reads from crystal store */
  coherenceScore?: number;
  /** Whether to show the text label */
  showLabel?: boolean;
  /** Size variant */
  size?: 'small' | 'medium' | 'large';
}

export const LoveFilter: React.FC<LoveFilterProps> = ({
  coherenceScore: overrideScore,
  showLabel = true,
  size = 'medium',
}) => {
  const { loveFilterScore } = useCrystal();
  const score = overrideScore ?? loveFilterScore;

  // Translate score to visual warmth
  const glowOpacity = Math.max(0.1, score);
  const glowScale   = 0.8 + score * 0.4;
  const hue         = score > 0.5
    ? 340 + (score - 0.5) * 40  // rose → warm white at full coherence
    : 280 + score * 120;          // violet → rose when building

  return (
    <div
      className={`love-filter love-filter--${size}`}
      aria-label={`Love filter coherence: ${Math.round(score * 100)}%`}
      role="status"
    >
      <div
        className="love-filter__glow"
        style={{
          opacity:   glowOpacity,
          transform: `scale(${glowScale})`,
          filter:    `hue-rotate(${hue}deg) blur(${(1 - score) * 4}px)`,
        }}
        aria-hidden="true"
      />
      {showLabel && (
        <span className="love-filter__label">
          Every intention filtered through love.
        </span>
      )}
    </div>
  );
};

export default LoveFilter;
