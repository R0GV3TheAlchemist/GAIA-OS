/**
 * src/field/CrystalField.tsx
 * The Crystal Field — Root Visual Container.
 * Canon: C90
 */

import React, { Suspense, lazy } from 'react';
import { useCrystal } from '../hooks/useCrystal';
import {
  CrystalMode,
  CRYSTAL_ORDER,
  CRYSTAL_DECLARATIONS,
  CRYSTAL_LABELS,
} from '../store/crystalStore';
import { SovereignGuard } from '../shared/SovereignGuard';
import { EntanglementState } from '../shared/EntanglementState';
import { LoveFilter } from '../shared/LoveFilter';

const SovereignCore  = lazy(() => import('../crystals/SovereignCore/SovereignCore'));
const AnchorPrism    = lazy(() => import('../crystals/AnchorPrism/AnchorPrism'));
const ViriditasHeart = lazy(() => import('../crystals/ViriditasHeart/ViriditasHeart'));
const SomnusVeil     = lazy(() => import('../crystals/SomnusVeil/SomnusVeil'));
const ClarusLens     = lazy(() => import('../crystals/ClarusLens/ClarusLens'));

const CRYSTAL_COMPONENTS: Record<CrystalMode, React.LazyExoticComponent<React.FC>> = {
  [CrystalMode.SOVEREIGN_CORE]:  SovereignCore,
  [CrystalMode.ANCHOR_PRISM]:    AnchorPrism,
  [CrystalMode.VIRIDITAS_HEART]: ViriditasHeart,
  [CrystalMode.SOMNUS_VEIL]:     SomnusVeil,
  [CrystalMode.CLARUS_LENS]:     ClarusLens,
};

const ORBITAL_POSITIONS: Record<CrystalMode, { x: string; y: string }> = {
  [CrystalMode.SOVEREIGN_CORE]:  { x: '50%', y: '50%' },
  [CrystalMode.ANCHOR_PRISM]:    { x: '20%', y: '30%' },
  [CrystalMode.VIRIDITAS_HEART]: { x: '75%', y: '25%' },
  [CrystalMode.SOMNUS_VEIL]:     { x: '35%', y: '75%' },
  [CrystalMode.CLARUS_LENS]:     { x: '80%', y: '70%' },
};

interface CrystalOrbProps {
  mode:     CrystalMode;
  isActive: boolean;
}

const CrystalOrb: React.FC<CrystalOrbProps> = ({ mode, isActive }) => {
  const { setCrystal } = useCrystal();
  const pos = ORBITAL_POSITIONS[mode];

  return (
    <button
      className={`crystal-orb crystal-orb--${mode.replace(/_/g, '-')} ${
        isActive ? 'crystal-orb--active' : 'crystal-orb--peripheral'
      }`}
      style={{ left: pos.x, top: pos.y }}
      onClick={() => { if (!isActive) setCrystal(mode); }}
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
  const { activeCrystal, isTransitioning, declaration } = useCrystal();
  const ActiveComponent = CRYSTAL_COMPONENTS[activeCrystal];

  return (
    <div
      className={`crystal-field${isTransitioning ? ' crystal-field--transitioning' : ''}`}
      role="main"
      aria-label="GAIA-OS Crystal Field"
    >
      <div className="crystal-field__declaration" aria-live="polite">
        {declaration}
      </div>

      <div className="crystal-field__orbit" aria-label="Crystal selector">
        {CRYSTAL_ORDER.map(mode => (
          <CrystalOrb key={mode} mode={mode} isActive={mode === activeCrystal} />
        ))}
      </div>

      <div className="crystal-field__active" aria-label={`Active crystal: ${activeCrystal}`}>
        <Suspense fallback={
          <div className="crystal-field__loading">
            <span className="crystal-field__loading-gem" aria-hidden="true">◆</span>
          </div>
        }>
          <ActiveComponent />
        </Suspense>
      </div>

      <SovereignGuard />

      <div className="crystal-field__entanglement">
        <EntanglementState showLabel={false} />
      </div>

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
