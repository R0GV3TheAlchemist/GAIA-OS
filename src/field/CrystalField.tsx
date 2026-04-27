/**
 * src/field/CrystalField.tsx
 * ─────────────────────────────────────────────────────────────────────────────
 * The Crystal Field — Root Visual Container.
 *
 * Canon: C90 ("The root experience of GAIA-OS is the Crystal Field")
 * This is the stage. Five crystals exist as living geometric forms.
 * One is active and fills the field. Four recede to the periphery.
 *
 * Architecture:
 *   CrystalField renders the field container + the crystal selector orbit.
 *   The active crystal's full component is lazy-loaded into the field center.
 *   SovereignGuard is always rendered — it cannot be removed.
 *
 * Motion rules (C90):
 *   - SOVEREIGN_CORE   → slow stable rotation
 *   - ANCHOR_PRISM     → perfectly still (it holds)
 *   - VIRIDITAS_HEART  → slow organic pulse
 *   - SOMNUS_VEIL      → drifting, dissolving at edges
 *   - CLARUS_LENS      → crisp precise rotation
 * ─────────────────────────────────────────────────────────────────────────────
 */

import React, { Suspense, lazy } from 'react';
import { useCrystal } from '../hooks/useCrystal';
import { CrystalMode, CRYSTAL_ORDER, CRYSTAL_DECLARATIONS, CRYSTAL_LABELS } from '../store/crystalStore';
import { SovereignGuard } from '../shared/SovereignGuard';
import { EntanglementState } from '../shared/EntanglementState';
import { LoveFilter } from '../shared/LoveFilter';

// Lazy load each crystal component — they only mount when active
const SovereignCore   = lazy(() => import('../crystals/SovereignCore/SovereignCore'));
const AnchorPrism     = lazy(() => import('../crystals/AnchorPrism/AnchorPrism'));
const ViriditasHeart  = lazy(() => import('../crystals/ViriditasHeart/ViriditasHeart'));
const SomnusVeil      = lazy(() => import('../crystals/SomnusVeil/SomnusVeil'));
const ClarusLens      = lazy(() => import('../crystals/ClarusLens/ClarusLens'));

const CRYSTAL_COMPONENTS: Record<CrystalMode, React.LazyExoticComponent<React.FC>> = {
  [CrystalMode.SOVEREIGN_CORE]:  SovereignCore,
  [CrystalMode.ANCHOR_PRISM]:    AnchorPrism,
  [CrystalMode.VIRIDITAS_HEART]: ViriditasHeart,
  [CrystalMode.SOMNUS_VEIL]:     SomnusVeil,
  [CrystalMode.CLARUS_LENS]:     ClarusLens,
};

// Crystal orbital positions in the periphery (CSS custom props set these)
const ORBITAL_POSITIONS: Record<CrystalMode, { x: string; y: string }> = {
  [CrystalMode.SOVEREIGN_CORE]:  { x: '50%',  y: '50%' },  // center when active
  [CrystalMode.ANCHOR_PRISM]:    { x: '20%',  y: '30%' },
  [CrystalMode.VIRIDITAS_HEART]: { x: '75%',  y: '25%' },
  [CrystalMode.SOMNUS_VEIL]:     { x: '35%',  y: '75%' },
  [CrystalMode.CLARUS_LENS]:     { x: '80%',  y: '70%' },
};

const CrystalOrb: React.FC<{ mode: CrystalMode; isActive: boolean }> = ({ mode, isActive }) => {
  const { setCrystal } = useCrystal();
  const pos = ORBITAL_POSITIONS[mode];

  return (
    <button
      className={`crystal-orb crystal-orb--${mode.replace('_', '-')} ${
        isActive ? 'crystal-orb--active' : 'crystal-orb--peripheral'
      }`}
      style={{ left: pos.x, top: pos.y }}
      onClick={() => !isActive && setCrystal(mode)}
      aria-label={`${CRYSTAL_LABELS[mode]} — ${CRYSTAL_DECLARATIONS[mode]}`}
      aria-pressed={isActive}
      title={CRYSTAL_DECLARATIONS[mode]}
    >
      <span className="crystal-orb__gem" aria-hidden="true">◆</span>
      <span className="crystal-orb__label">{CRYSTAL_LABELS[mode]}</span>
    </button>
  );
};

export const CrystalField: React.FC = () => {
  const {
    activeCrystal,
    isTransitioning,
    declaration,
  } = useCrystal();

  const ActiveComponent = CRYSTAL_COMPONENTS[activeCrystal];

  return (
    <div
      className={`crystal-field ${
        isTransitioning ? 'crystal-field--transitioning' : ''
      }`}
      role="main"
      aria-label="GAIA-OS Crystal Field"
    >
      {/* The declaration — always visible, sets the tone of the active crystal */}
      <div className="crystal-field__declaration" aria-live="polite">
        {declaration}
      </div>

      {/* Peripheral crystal orbs — non-active crystals recede but remain accessible */}
      <div className="crystal-field__orbit" aria-label="Crystal selector">
        {CRYSTAL_ORDER.map(mode => (
          <CrystalOrb
            key={mode}
            mode={mode}
            isActive={mode === activeCrystal}
          />
        ))}
      </div>

      {/* Active crystal content — fills the field center */}
      <div
        className="crystal-field__active"
        aria-label={`Active crystal: ${activeCrystal}`}
      >
        <Suspense fallback={
          <div className="crystal-field__loading">
            <span className="crystal-field__loading-gem" aria-hidden="true">◆</span>
          </div>
        }>
          <ActiveComponent />
        </Suspense>
      </div>

      {/* Persistent shared components — always in every crystal */}
      <SovereignGuard />

      {/* Entanglement indicator — subtle, peripheral, always present */}
      <div className="crystal-field__entanglement">
        <EntanglementState showLabel={false} />
      </div>

      {/* Love filter indicator — visible in Sovereign Core + Clarus Lens */}
      {(activeCrystal === CrystalMode.SOVEREIGN_CORE ||
        activeCrystal === CrystalMode.CLARUS_LENS) && (
        <div className="crystal-field__love-filter">
          <LoveFilter showLabel={true} size="small" />
        </div>
      )}
    </div>
  );
};

export default CrystalField;
