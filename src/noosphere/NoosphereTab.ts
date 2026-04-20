import './NoosphereTab.css';

export interface NoosphereTabOptions {
  root: HTMLElement;
  apiBase?: string;
  gaianSlug?: string;
  authToken?: string;
}

interface CollectiveField {
  active_gaians: number;
  consenting_gaians: number;
  total_registered: number;
  avg_bond_depth: number;
  avg_noosphere_health: number;
  avg_synergy_factor: number;
  collective_phi: number;
  schumann_aligned_count: number;
  dominant_element: string;
  element_distribution: Record<string, number>;
  individuation_distribution: Record<string, number>;
  noosphere_stage: string;
  field_resonance_pct: number;
  field_coherence_label: string;
  privacy_note: string;
  doctrine_ref: string;
}

interface MotherPulse {
  pulse_id: string;
  sequence: number;
  timestamp: number;
  collective_field: CollectiveField;
  mother_voice: string | null;
  criticality_regime: string;
  coherence_candidate: boolean;
  coherence_candidate_label: string | null;
  weaving_record_id: string;
  doctrine_ref: string;
  type?: string;
}

interface WeavingRecord {
  record_id: string;
  seq: number;
  timestamp: number;
  active_gaians: number;
  phi: number;
  stage: string;
  regime: string;
  candidate: boolean;
  voice: string | null;
  epistemic_note: string | null;
}

const NOOSPHERE_STAGES = ['Geosphere','Biosphere','Primitive Mind','Social Weave','Noosphere','Resonant Field','Omega Point'];
const ELEMENT_COLORS: Record<string, string> = { fire:'#e63946', water:'#4895ef', earth:'#52b788', air:'#adb5bd', aether:'#9b72cf', wood:'#8cb369', metal:'#c9ada7', thunder:'#f4a261', void:'#6c757d' };
const REGIME_CONFIG: Record<string, { label: string; cls: string }> = { critical:{ label:'CRITICAL', cls:'regime-critical' }, too_ordered:{ label:'TOO ORDERED', cls:'regime-ordered' }, too_chaotic:{ label:'TOO CHAOTIC', cls:'regime-chaotic' } };
const COHERENCE_LABEL_CONFIG: Record<string, { label: string; cls: string }> = { dormant:{ label:'DORMANT', cls:'coh-dormant' }, nascent:{ label:'NASCENT', cls:'coh-nascent' }, building:{ label:'BUILDING', cls:'coh-building' }, coherent:{ label:'COHERENT', cls:'coh-coherent' }, high_resonance:{ label:'HIGH RESONANCE', cls:'coh-high' } };

let _evtSource: EventSource | null = null;
let _reconnectTimer: ReturnType<typeof setTimeout> | null = null;
let _voiceFadeTimer: ReturnType<typeof setTimeout> | null = null;
let _opts: NoosphereTabOptions = { root: document.body };

export function mountNoosphereTab(opts: NoosphereTabOptions): void {
  _opts = opts;
  const { root } = opts;
  root.innerHTML = buildSkeletonHTML();
  bindConsentToggle(root);
  connect(root);
  void fetchWeavingLog(root);
}

export function unmountNoosphereTab(): void {
  if (_evtSource) { _evtSource.close(); _evtSource = null; }
  if (_reconnectTimer) { clearTimeout(_reconnectTimer); _reconnectTimer = null; }
  if (_voiceFadeTimer) { clearTimeout(_voiceFadeTimer); _voiceFadeTimer = null; }
}

function apiBase(): string { return (_opts.apiBase ?? 'http://localhost:8008').replace(/\/$/, ''); }
function connect(root: HTMLElement): void { if (_evtSource) _evtSource.close(); const es = new EventSource(`${apiBase()}/mother/pulse/stream`); _evtSource = es; setConnectionStatus(root, 'connecting'); es.addEventListener('mother_pulse', (ev: MessageEvent) => { try { const pulse: MotherPulse = JSON.parse(ev.data); if (pulse.type === 'keepalive') return; renderPulse(root, pulse); setConnectionStatus(root, 'live'); } catch (e) { console.error('[NoosphereTab] Parse error:', e); } }); es.onerror = () => { setConnectionStatus(root, 'reconnecting'); es.close(); _evtSource = null; _reconnectTimer = setTimeout(() => connect(root), 5000); }; es.onopen = () => { setConnectionStatus(root, 'live'); }; }
function buildSkeletonHTML(): string { return '<div class="ns-tab"></div>'; }
function renderPulse(_root: HTMLElement, _pulse: MotherPulse): void {}
function renderMotherVoice(_root: HTMLElement, _voice: string): void {}
function renderDistBars(_container: Element | null, _dist: Record<string, number>, _colorFn: (key: string) => string): void {}
async function fetchWeavingLog(_root: HTMLElement): Promise<void> { return; }
function bindConsentToggle(_root: HTMLElement): void {}
function setConnectionStatus(_root: HTMLElement, _state: 'connecting' | 'live' | 'reconnecting'): void {}
function phiColor(phi: number): string { if (phi >= 0.75) return '#52b788'; if (phi >= 0.5) return '#9b72cf'; if (phi >= 0.25) return '#4895ef'; return '#6c757d'; }
function setText(root: HTMLElement, selector: string, value: string): void { const el = root.querySelector<HTMLElement>(selector); if (el) el.textContent = value; }
function escHtml(s: string): string { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
