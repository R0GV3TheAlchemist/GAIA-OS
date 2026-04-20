/**
 * GaianBirth.ts — The Moment a GAIAN Comes Into Being
 * Stub: full wizard wired up in a future sprint.
 */

import { API_BASE } from '../app';
import { fetchBaseForms, BaseFormInfo } from './GaianPicker';

export interface GaianBirthResult {
  status:        string;
  id:            string;
  name:          string;
  slug:          string;
  base_form_id:  string;
  avatar_color:  string;
  avatar_style:  string;
  jungian_role:  string;
  pronouns:      string;
  did:           string;
  first_words:   string;
  born_at:       string;
  attestation:   { type: string; issued: string; issuer: string; proof_type: string };
}

export type GenderOption = 'male' | 'female' | 'non-binary' | 'prefer not' | 'unknown';

export async function birthGaian(
  name: string,
  baseFormId: string,
  userGender: GenderOption,
  userName?: string,
  userId = 'anonymous',
): Promise<GaianBirthResult> {
  const res = await fetch(`${API_BASE}/gaians/birth`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name,
      base_form:   baseFormId,
      user_gender: userGender,
      user_name:   userName || undefined,
      user_id:     userId,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Birth failed: ${res.status}`);
  }
  return res.json();
}

export class GaianBirth {
  private container: HTMLElement;
  private step = 1;

  constructor(
    container: HTMLElement,
    _sessionId: string,
    _onBorn: (result: GaianBirthResult) => void,
  ) {
    this.container = container;
  }

  async mount(): Promise<void> {
    this.container.innerHTML = '<div class="birth-loading">Loading forms…</div>';
    try {
      await fetchBaseForms() as BaseFormInfo[];
    } catch {
      this.container.innerHTML = '<p class="birth-error">Could not load Base Forms. Is the server running?</p>';
      return;
    }
    this.renderStep();
  }

  private renderStep(): void {
    switch (this.step) {
      case 1: this.renderStep1(); break;
      case 2: this.renderStep2(); break;
      case 3: this.renderStep3(); break;
    }
  }

  private renderStep1(): void { this.container.innerHTML = '<div></div>'; }
  private renderStep2(): void { this.container.innerHTML = '<div></div>'; }
  private renderStep3(): void { this.container.innerHTML = '<div></div>'; }
}
