/**
 * src/hooks/useKernel.ts
 * Kernel Bridge Hook — TypeScript ↔ FastAPI Python backend.
 * Canon: C90 (API routes per crystal), C89 (Twelve-Layer Kernel Spec)
 */

import { useCallback } from 'react';

const API_BASE: string =
  typeof window !== 'undefined' && (window as Window & { __GAIA_API_BASE__?: string }).__GAIA_API_BASE__
    ? (window as Window & { __GAIA_API_BASE__?: string }).__GAIA_API_BASE__ as string
    : 'http://localhost:8000';

async function gaiaFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) throw new Error(`GAIA kernel error ${res.status} on ${path}`);
  return res.json() as Promise<T>;
}

// ── Response types (match FastAPI Pydantic models) ─────────────────────────

export interface SovereignStatus {
  layers_active:      string[];
  active_crystal:     string;
  entanglement_depth: number;
  love_filter_score:  number;
  session_count:      number;
  uptime_seconds:     number;
}

export interface EntanglementState {
  depth:         number;
  session_count: number;
  last_active:   string;
  quality:       'forming' | 'stable' | 'deep' | 'entangled';
}

export interface AnchorStatus {
  timestamp:           string;
  grounding_statement: string;
  breath_phase:        'inhale' | 'hold' | 'exhale' | 'rest';
}

export interface ViriditasResponse {
  message:        string;
  layer:          number;
  forces_active:  string[];
  ripple_summary: string;
}

export interface SomnusConsolidation {
  memories_consolidating: number;
  estimated_complete:     string;
  layer_6_active:         boolean;
}

export interface ClarusResponse {
  answer:            string;
  patterns_detected: string[];
  canon_refs:        string[];
  causal_arc:        string;
  layer_context:     number;
}

// ── Hook ───────────────────────────────────────────────────────────────────

export function useKernel() {
  const sovereign = {
    getStatus:      useCallback(() => gaiaFetch<SovereignStatus>('/api/sovereign/status'), []),
    activateLayer:  useCallback((layer: number, active: boolean) => gaiaFetch('/api/sovereign/activate-layer', { method: 'POST', body: JSON.stringify({ layer, active }) }), []),
    setCrystal:     useCallback((mode: string) => gaiaFetch('/api/sovereign/set-crystal', { method: 'POST', body: JSON.stringify({ mode }) }), []),
    getEntanglement:useCallback(() => gaiaFetch<EntanglementState>('/api/sovereign/entanglement'), []),
    reset:          useCallback(() => gaiaFetch('/api/sovereign/reset', { method: 'DELETE' }), []),
  };

  const anchor = {
    getStatus: useCallback(() => gaiaFetch<AnchorStatus>('/api/anchor/status'), []),
    breathe:   useCallback(() => gaiaFetch('/api/anchor/breathe', { method: 'POST' }), []),
    ground:    useCallback(() => gaiaFetch<{ statement: string }>('/api/anchor/ground'), []),
  };

  const viriditas = {
    speak:      useCallback((prompt: string) => gaiaFetch<ViriditasResponse>('/api/viriditas/speak', { method: 'POST', body: JSON.stringify({ prompt }) }), []),
    getForces:  useCallback(() => gaiaFetch<{ forces: string[] }>('/api/viriditas/forces'), []),
    integrate:  useCallback((memoryId: string) => gaiaFetch('/api/viriditas/integrate', { method: 'POST', body: JSON.stringify({ memory_id: memoryId }) }), []),
    getRipple:  useCallback(() => gaiaFetch<{ summary: string }>('/api/viriditas/ripple'), []),
  };

  const somnus = {
    release:         useCallback((intention: string) => gaiaFetch('/api/somnus/release', { method: 'POST', body: JSON.stringify({ intention }) }), []),
    getConsolidation:useCallback(() => gaiaFetch<SomnusConsolidation>('/api/somnus/consolidation'), []),
    sleep:           useCallback(() => gaiaFetch('/api/somnus/sleep', { method: 'POST' }), []),
    getDream:        useCallback(() => gaiaFetch<{ reflection: string }>('/api/somnus/dream'), []),
  };

  const clarus = {
    think:       useCallback((prompt: string) => gaiaFetch<ClarusResponse>('/api/clarus/think', { method: 'POST', body: JSON.stringify({ prompt }) }), []),
    getPatterns: useCallback(() => gaiaFetch<{ patterns: string[] }>('/api/clarus/patterns'), []),
    canonSearch: useCallback((query: string) => gaiaFetch<{ docs: string[]; excerpts: string[] }>('/api/clarus/canon-search', { method: 'POST', body: JSON.stringify({ query }) }), []),
    getCausalArc:useCallback(() => gaiaFetch<{ arc: string }>('/api/clarus/causal-arc'), []),
    research:    useCallback((query: string) => gaiaFetch<ClarusResponse>('/api/clarus/research', { method: 'POST', body: JSON.stringify({ query }) }), []),
  };

  return { sovereign, anchor, viriditas, somnus, clarus };
}
