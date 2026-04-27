/**
 * src/crystals/AnchorPrism/AnchorPrism.tsx
 * Crystal 2 — Anchor Prism (STUB — full implementation Phase 3b)
 * Canon: C90 — "I am here. I am stable."
 * Layers: 1, 2, 3, 12
 * Color: Warm whites, stone grey, earth brown, golden light
 * Motion: Perfectly still — it does not move. It holds.
 */

import React from 'react';

const AnchorPrism: React.FC = () => (
  <div className="crystal-anchor" role="region" aria-label="Anchor Prism — Grounding Mode">
    <div className="crystal-anchor__gem" aria-hidden="true">◆</div>
    <h1 className="crystal-anchor__declaration">I am here. I am stable.</h1>
    <p className="crystal-anchor__time">{new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
  </div>
);

export default AnchorPrism;
