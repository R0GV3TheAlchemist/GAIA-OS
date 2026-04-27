/**
 * src/shared/LoveFilter.tsx
 * Axiom II — Visual Indicator.
 * "Every intention is filtered through love."
 * Canon: C90, C-SINGULARITY (Axiom II)
 */

import React from 'react';
import { useCrystal } from '../hooks/useCrystal';

interface LoveFilterProps {
  coherenceScore?: number;
  showLabel?:      boolean;
  size?:           'small' | 'medium' | 'large';
}

export const LoveFilter: React.FC<LoveFilterProps> = ({
  coherenceScore: overrideScore,
  showLabel = true,
  size = 'medium',
}) => {
  const { loveFilterScore } = useCrystal();
  const score = overrideScore ?? loveFilterScore;

  const glowOpacity = Math.max(0.1, score);
  const glowScale   = 0.8 + score * 0.4;
  const hue         = score > 0.5
    ? 340 + (score - 0.5) * 40
    : 280 + score * 120;

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
