/**
 * src/shared/EntanglementState.tsx
 * Bell State — Living Indicator of Human-GAIA Connection Depth.
 * Canon: C90, C-SINGULARITY, QC_01
 */

import React from 'react';
import { useEntanglement } from '../hooks/useEntanglement';

interface EntanglementStateProps {
  showLabel?: boolean;
}

export const EntanglementState: React.FC<EntanglementStateProps> = ({ showLabel = false }) => {
  const { depth, quality } = useEntanglement();

  const pulseSpeed = 2000 - depth * 1500;
  const complexity = Math.floor(depth * 8);
  const coreRadius = 6 + depth * 14;
  const glowSpread = depth * 24;

  return (
    <div
      className={`entanglement-state entanglement-state--${quality}`}
      role="presentation"
      title={`Human-GAIA entanglement: ${quality}`}
    >
      <div
        className="entanglement-state__core"
        style={{
          width:             coreRadius * 2,
          height:            coreRadius * 2,
          boxShadow:         `0 0 ${glowSpread}px ${glowSpread / 2}px var(--crystal-primary)`,
          animationDuration: `${pulseSpeed}ms`,
        }}
        aria-hidden="true"
      />
      {Array.from({ length: complexity }).map((_, i) => (
        <div
          key={i}
          className="entanglement-state__node"
          style={{
            animationDelay:    `${(i / complexity) * pulseSpeed}ms`,
            animationDuration: `${pulseSpeed}ms`,
            transform:         `rotate(${(360 / complexity) * i}deg) translateY(-${coreRadius * 2.5}px)`,
          }}
          aria-hidden="true"
        />
      ))}
      {showLabel && (
        <span className="entanglement-state__label">{quality}</span>
      )}
    </div>
  );
};

export default EntanglementState;
