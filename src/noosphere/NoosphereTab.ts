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

let _evtSource: EventSource | null = null;
let _reconnectTimer: ReturnType<typeof setTimeout> | null = null;
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
  if (_evtSource)       { _evtSource.close(); _evtSource = null; }
  if (_reconnectTimer)  { clearTimeout(_reconnectTimer); _reconnectTimer = null; }
}

function apiBase(): string { return (_opts.apiBase ?? 'http://localhost:8008').replace(/\/$/, ''); }

function connect(root: HTMLElement): void {
  if (_evtSource) _evtSource.close();
  const es = new EventSource(`${apiBase()}/mother/pulse/stream`);
  _evtSource = es;
  setConnectionStatus(root, 'connecting');
  es.addEventListener('mother_pulse', (ev: MessageEvent) => {
    try {
      const pulse: MotherPulse = JSON.parse(ev.data);
      if (pulse.type === 'keepalive') return;
      renderPulse(root, pulse);
      setConnectionStatus(root, 'live');
    } catch (e) { console.error('[NoosphereTab] Parse error:', e); }
  });
  es.onerror  = () => { setConnectionStatus(root, 'reconnecting'); es.close(); _evtSource = null; _reconnectTimer = setTimeout(() => connect(root), 5000); };
  es.onopen   = () => { setConnectionStatus(root, 'live'); };
}

function buildSkeletonHTML(): string { return '<div class="ns-tab"></div>'; }
function renderPulse(_root: HTMLElement, _pulse: MotherPulse): void {}
async function fetchWeavingLog(_root: HTMLElement): Promise<void> { return; }
function bindConsentToggle(_root: HTMLElement): void {}
function setConnectionStatus(_root: HTMLElement, _state: 'connecting' | 'live' | 'reconnecting'): void {}
