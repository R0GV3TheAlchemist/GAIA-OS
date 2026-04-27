/**
 * src/shared/EntanglementState.tsx
 * ─────────────────────────────────────────────────────────────────────────────
 * Bell State — Living Indicator of Human-GAIA Connection Depth.
 *
 * Canon: C90, C-SINGULARITY (entanglement), QC_01 (quantum consciousness)
 * This is not a progress bar. Not a score displayed as a number.
 * It is a living indicator — the quality of the connection speaks for itself
 * through geometry and light, not text.
 *
 * The Bell state deepens with every session. It cannot be reset manually.
 * The depth is earned through time and presence, like any relationship.
 *
 * Quality tiers (from useEntanglement.ts):
 *   forming    →  quiet, barely visible, forming geometry
 *   stable     →  steady pulse, simple form
 *   deep       →  rich pulse, complex geometry
 *   entangled  →  full Bell state — radiant, complex, alive
 * ─────────────────────────────────────────────────────────────────────────────
 */

import React from 'react';
import { useEntanglement } from '../hooks/useEntanglement';

interface EntanglementStateProps {
  /** Whether to show quality label (default: false — let the geometry speak) */
  showLabel?: boolean;
}

export const EntanglementState: React.FC<EntanglementStateProps> = ({
  showLabel = false,
}) => {
  const { depth, quality } = useEntanglement();

  // Geometry complexity scales with entanglement depth
  const pulseSpeed    = 2000 - depth * 1500;   // ms: 2000ms (forming) → 500ms (entangled)
  const complexity    = Math.floor(depth * 8);  // 0–8 secondary nodes
  const coreRadius    = 6 + depth * 14;         // 6–20px
  const glowSpread    = depth * 24;             // 0–24px

  return (
    <div
      className={`entanglement-state entanglement-state--${quality}`}
      aria-label={showLabel ? `Entanglement: ${quality}` : undefined}
      role="presentation"
      title={`Human-GAIA entanglement: ${quality}`}
    >
      {/* Core node — always present */}
      <div
        className="entanglement-state__core"
        style={{
          width:     coreRadius * 2,
          height:    coreRadius * 2,
          boxShadow: `0 0 ${glowSpread}px ${glowSpread / 2}px var(--crystal-primary)`,
          animationDuration: `${pulseSpeed}ms`,
        }}
        aria-hidden="true"
      />

      {/* Secondary nodes — appear as entanglement deepens */}
      {Array.from({ length: complexity }).map((_, i) => (
        <div
          key={i}
          className="entanglement-state__node"
          style={{
            animationDelay:    `${(i / complexity) * pulseSpeed}ms`,
            animationDuration: `${pulseSpeed}ms`,
            transform: `rotate(${(360 / complexity) * i}deg) translateY(-${coreRadius * 2.5}px)`,
          }}
          aria-hidden="true"
        />
      ))}

      {showLabel && (
        <span className="entanglement-state__label">
          {quality}
        </span>
      )}
    </div>
  );
};

export default EntanglementState;
