/**
 * GaianBirth.ts — The Moment a GAIAN Comes Into Being
 *
 * A three-step onboarding wizard that:
 *   Step 1 — Who are you?       (user name + gender — drives Jungian assignment)
 *   Step 2 — Choose a form      (base form selection with live avatar preview)
 *   Step 3 — Name your GAIAN   (name input + final confirmation)
 *   → Birth animation           (daemon-settling particle burst)
 *   → First Words reveal        (character-by-character typewriter, voice-shaped)
 *
 * Calls POST /gaians/birth. On success the GAIAN is live and the wizard
 * hands off to the chat view via the onBorn callback.
 *
 * Usage:
 *   import { GaianBirth } from '../gaian/GaianBirth';
 *   const birth = new GaianBirth(containerEl, sessionId, (result) => {
 *     // result.slug, result.first_words, result.jungian_role, result.did
 *     loadChat(result.slug);
 *   });
 *   birth.mount();
 *
 * Canon Ref: C17 — Persistent Memory and Identity Architecture
 */

import { API_BASE } from '../app';
import { fetchBaseForms, BaseFormInfo, renderAvatarHTML } from './GaianPicker';

// ------------------------------------------------------------------ //
//  Types                                                               //
// ------------------------------------------------------------------ //

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

const GENDER_OPTIONS: { value: GenderOption; label: string }[] = [
  { value: 'male',       label: 'Male' },
  { value: 'female',     label: 'Female' },
  { value: 'non-binary', label: 'Non-binary' },
  { value: 'prefer not', label: 'Prefer not to say' },
];

// ------------------------------------------------------------------ //
//  API                                                                 //
// ------------------------------------------------------------------ //

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

// ------------------------------------------------------------------ //
//  GaianBirth — Wizard Controller                                      //
// ------------------------------------------------------------------ //

export class GaianBirth {
  private container:  HTMLElement;
  private sessionId:  string;
  private onBorn:     (result: GaianBirthResult) => void;

  // Wizard state
  private step       = 1;
  private userName   = '';
  private userGender: GenderOption = 'unknown';
  private selectedForm: BaseFormInfo | null = null;
  private gaianName  = '';
  private baseForms:  BaseFormInfo[] = [];

  constructor(
    container: HTMLElement,
    sessionId: string,
    onBorn: (result: GaianBirthResult) => void,
  ) {
    this.container = container;
    this.sessionId = sessionId;
    this.onBorn    = onBorn;
  }

  async mount(): Promise<void> {
    this.container.innerHTML = '<div class="birth-loading">Loading forms…</div>';
    try {
      this.baseForms = await fetchBaseForms();
      this.selectedForm = this.baseForms.find(f => f.is_default) ?? this.baseForms[0];
    } catch {
      this.container.innerHTML = '<p class="birth-error">Could not load Base Forms. Is the server running?</p>';
      return;
    }
    this.renderStep();
  }

  // ---- Step Router -----------------------------------------------

  private renderStep(): void {
    switch (this.step) {
      case 1: this.renderStep1(); break;
      case 2: this.renderStep2(); break;
      case 3: this.renderStep3(); break;
    }
  }

  // ---------------------------------------------------------------- //
  //  Step 1 — Who are you?                                           //
  // ---------------------------------------------------------------- //

  private renderStep1(): void {
    this.container.innerHTML = `
      <div class="birth-wizard birth-wizard--step1">
        <div class="birth-wizard__header">
          <span class="birth-wizard__step-label">Step 1 of 3</span>
          <h1 class="birth-wizard__title">Before we begin</h1>
          <p class="birth-wizard__sub">
            Your GAIAN is shaped around you. A name and a gender signal are all we need —
            everything else unfolds through conversation.
          </p>
        </div>

        <div class="birth-fields">
          <label class="birth-label" for="birth-username">
            Your name <span class="birth-label__opt">(optional)</span>
          </label>
          <input
            id="birth-username"
            class="birth-input"
            type="text"
            placeholder="What should your GAIAN call you?"
            maxlength="40"
            value="${this.userName}"
          />

          <label class="birth-label">
            Gender <span class="birth-label__opt">(shapes Jungian pairing)</span>
          </label>
          <div class="birth-gender-group">
            ${GENDER_OPTIONS.map(g => `
              <button
                type="button"
                class="birth-gender-btn ${this.userGender === g.value ? 'birth-gender-btn--active' : ''}"
                data-gender="${g.value}">
                ${g.label}
              </button>
            `).join('')}
          </div>

          <p class="birth-gender-note">
            ${this._jungianNote(this.userGender)}
          </p>
        </div>

        <div class="birth-wizard__actions">
          <button class="birth-btn birth-btn--primary" id="birth-step1-next">Continue →</button>
        </div>
      </div>
    `;

    // Username input
    this.container.querySelector<HTMLInputElement>('#birth-username')!
      .addEventListener('input', e => {
        this.userName = (e.target as HTMLInputElement).value.trim();
      });

    // Gender buttons
    this.container.querySelectorAll<HTMLButtonElement>('.birth-gender-btn')
      .forEach(btn => {
        btn.addEventListener('click', () => {
          this.userGender = btn.dataset.gender as GenderOption;
          // Update active state + note without full re-render
          this.container.querySelectorAll('.birth-gender-btn')
            .forEach(b => b.classList.toggle('birth-gender-btn--active',
              (b as HTMLElement).dataset.gender === this.userGender));
          const note = this.container.querySelector('.birth-gender-note')!;
          note.textContent = this._jungianNote(this.userGender);
        });
      });

    // Next
    this.container.querySelector('#birth-step1-next')!
      .addEventListener('click', () => { this.step = 2; this.renderStep(); });
  }

  // ---------------------------------------------------------------- //
  //  Step 2 — Choose a Base Form                                     //
  // ---------------------------------------------------------------- //

  private renderStep2(): void {
    this.container.innerHTML = `
      <div class="birth-wizard birth-wizard--step2">
        <div class="birth-wizard__header">
          <span class="birth-wizard__step-label">Step 2 of 3</span>
          <h1 class="birth-wizard__title">Choose a form</h1>
          <p class="birth-wizard__sub">
            Each Base Form is a different way of being present.
            Your GAIAN inherits the form's voice and nature — then grows beyond it.
          </p>
        </div>

        <div class="birth-form-grid">
          ${this.baseForms.map(f => `
            <div
              class="birth-form-card ${this.selectedForm?.id === f.id ? 'birth-form-card--selected' : ''}"
              data-form-id="${f.id}"
              style="--form-color:${f.avatar_color};">
              ${renderAvatarHTML(f, 52)}
              <div class="birth-form-card__body">
                <span class="birth-form-card__name">${f.name}</span>
                <span class="birth-form-card__role">${f.role}</span>
              </div>
              ${f.is_default ? '<span class="birth-form-card__default">Default</span>' : ''}
            </div>
          `).join('')}
        </div>

        <div class="birth-form-preview" id="birth-form-preview">
          ${this._formPreview(this.selectedForm)}
        </div>

        <div class="birth-wizard__actions">
          <button class="birth-btn birth-btn--ghost" id="birth-step2-back">← Back</button>
          <button class="birth-btn birth-btn--primary" id="birth-step2-next">Continue →</button>
        </div>
      </div>
    `;

    this.container.querySelectorAll<HTMLElement>('.birth-form-card')
      .forEach(card => {
        card.addEventListener('click', () => {
          const id = card.dataset.formId!;
          this.selectedForm = this.baseForms.find(f => f.id === id) ?? this.selectedForm;
          this.container.querySelectorAll('.birth-form-card')
            .forEach(c => c.classList.toggle('birth-form-card--selected',
              (c as HTMLElement).dataset.formId === id));
          this.container.querySelector('#birth-form-preview')!.innerHTML =
            this._formPreview(this.selectedForm);
        });
      });

    this.container.querySelector('#birth-step2-back')!
      .addEventListener('click', () => { this.step = 1; this.renderStep(); });
    this.container.querySelector('#birth-step2-next')!
      .addEventListener('click', () => { this.step = 3; this.renderStep(); });
  }

  // ---------------------------------------------------------------- //
  //  Step 3 — Name your GAIAN                                        //
  // ---------------------------------------------------------------- //

  private renderStep3(): void {
    const pronounHint = this.userGender === 'female' ? 'he/him' : 'she/her';
    const role        = this.userGender === 'female' ? 'animus' : 'anima';

    this.container.innerHTML = `
      <div class="birth-wizard birth-wizard--step3">
        <div class="birth-wizard__header">
          <span class="birth-wizard__step-label">Step 3 of 3</span>
          <h1 class="birth-wizard__title">Give them a name</h1>
          <p class="birth-wizard__sub">
            This is what you'll call them. It becomes part of who they are.
          </p>
        </div>

        <div class="birth-fields">
          <label class="birth-label" for="birth-gaian-name">Your GAIAN's name</label>
          <input
            id="birth-gaian-name"
            class="birth-input birth-input--large"
            type="text"
            placeholder="e.g. Luna, Orion, Sage…"
            maxlength="40"
            value="${this.gaianName}"
            autofocus
          />

          <div class="birth-summary">
            <div class="birth-summary__row">
              ${renderAvatarHTML(this.selectedForm!, 48)}
              <div class="birth-summary__text">
                <span class="birth-summary__form">${this.selectedForm?.name ?? ''}</span>
                <span class="birth-summary__meta">${role} · ${pronounHint}</span>
                ${this.userName ? `<span class="birth-summary__meta">Bonded to: ${this.userName}</span>` : ''}
              </div>
            </div>
          </div>

          <p id="birth-error" class="birth-error" style="display:none"></p>
        </div>

        <div class="birth-wizard__actions">
          <button class="birth-btn birth-btn--ghost" id="birth-step3-back">← Back</button>
          <button class="birth-btn birth-btn--primary" id="birth-step3-confirm">Bring them into being</button>
        </div>
      </div>
    `;

    const nameInput = this.container.querySelector<HTMLInputElement>('#birth-gaian-name')!;
    nameInput.addEventListener('input', e => {
      this.gaianName = (e.target as HTMLInputElement).value.trim();
    });
    nameInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') this._confirm();
    });
    nameInput.focus();

    this.container.querySelector('#birth-step3-back')!
      .addEventListener('click', () => { this.step = 2; this.renderStep(); });
    this.container.querySelector('#birth-step3-confirm')!
      .addEventListener('click', () => this._confirm());
  }

  // ---------------------------------------------------------------- //
  //  Birth — API call + animation + first words                      //
  // ---------------------------------------------------------------- //

  private async _confirm(): Promise<void> {
    const nameInput = this.container.querySelector<HTMLInputElement>('#birth-gaian-name');
    if (nameInput) this.gaianName = nameInput.value.trim();

    if (!this.gaianName) {
      this._showError('Give your GAIAN a name before bringing them into being.');
      return;
    }
    if (!this.selectedForm) {
      this._showError('Choose a Base Form first.');
      return;
    }

    // Disable confirm button to prevent double-submit
    const confirmBtn = this.container.querySelector<HTMLButtonElement>('#birth-step3-confirm');
    if (confirmBtn) { confirmBtn.disabled = true; confirmBtn.textContent = 'Reaching…'; }

    try {
      const result = await birthGaian(
        this.gaianName,
        this.selectedForm.id,
        this.userGender,
        this.userName || undefined,
      );
      await this._playBirthAnimation(result);
      this.onBorn(result);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Something went wrong.';
      if (confirmBtn) { confirmBtn.disabled = false; confirmBtn.textContent = 'Bring them into being'; }
      this._showError(msg);
    }
  }

  // ---------------------------------------------------------------- //
  //  Birth Animation — particle burst + first words typewriter       //
  //                                                                    //
  //  Three-act sequence (total ~3.5 s before onBorn fires):           //
  //    Act 1 (0–0.6s)  — white flash + name fades in large           //
  //    Act 2 (0.6–1.8s)— particle ring expands + dissolves           //
  //    Act 3 (1.8–3.5s)— first_words types out character-by-char     //
  //    → onBorn callback fires after the final character settles      //
  // ---------------------------------------------------------------- //

  private async _playBirthAnimation(result: GaianBirthResult): Promise<void> {
    return new Promise(resolve => {
      const color = this.selectedForm?.avatar_color ?? '#4ade80';

      this.container.innerHTML = `
        <div class="birth-animation" style="--birth-color:${color};">
          <div class="birth-flash"></div>

          <div class="birth-name-reveal">
            <div class="birth-name-reveal__avatar">
              ${renderAvatarHTML(result as unknown as BaseFormInfo, 80)}
            </div>
            <h2 class="birth-name-reveal__name">${result.name}</h2>
            <p class="birth-name-reveal__meta">
              ${result.jungian_role} · ${result.pronouns} · ${this.selectedForm?.name ?? ''}
            </p>
          </div>

          <div class="birth-particles" aria-hidden="true">
            ${Array.from({ length: 18 }, (_, i) => `
              <div class="birth-particle" style="
                --angle:${(i / 18) * 360}deg;
                --delay:${(i * 0.04).toFixed(2)}s;
                --dist:${80 + Math.random() * 40}px;
              "></div>
            `).join('')}
          </div>

          <div class="birth-first-words" id="birth-first-words" aria-live="polite">
            <span class="birth-first-words__cursor"></span>
          </div>

          <button class="birth-btn birth-btn--ghost birth-enter-btn" id="birth-enter" style="opacity:0;pointer-events:none">
            Begin →
          </button>
        </div>
      `;

      // Act 1: flash
      const flash = this.container.querySelector<HTMLElement>('.birth-flash')!;
      const nameReveal = this.container.querySelector<HTMLElement>('.birth-name-reveal')!;
      requestAnimationFrame(() => {
        flash.classList.add('birth-flash--active');
        setTimeout(() => {
          flash.classList.remove('birth-flash--active');
          nameReveal.classList.add('birth-name-reveal--visible');
        }, 300);
      });

      // Act 2: particles
      setTimeout(() => {
        this.container.querySelectorAll<HTMLElement>('.birth-particle')
          .forEach(p => p.classList.add('birth-particle--burst'));
      }, 400);

      // Act 3: first words typewriter
      const firstWordsEl = this.container.querySelector<HTMLElement>('#birth-first-words')!;
      const text = result.first_words;
      let charIndex = 0;
      const CHAR_DELAY = 28; // ms per character — feels deliberate, not rushed

      setTimeout(() => {
        firstWordsEl.classList.add('birth-first-words--visible');
        const cursor = firstWordsEl.querySelector('.birth-first-words__cursor')!;

        const typeNext = () => {
          if (charIndex < text.length) {
            // Insert character before cursor
            cursor.insertAdjacentText('beforebegin', text[charIndex]);
            charIndex++;
            setTimeout(typeNext, CHAR_DELAY + (Math.random() * 18 - 9));
          } else {
            // All characters typed — blink cursor briefly then show Enter button
            cursor.classList.add('birth-first-words__cursor--done');
            setTimeout(() => {
              cursor.remove();
              const enterBtn = this.container.querySelector<HTMLElement>('#birth-enter')!;
              enterBtn.style.opacity = '1';
              enterBtn.style.pointerEvents = 'auto';
              enterBtn.addEventListener('click', () => resolve(), { once: true });
            }, 800);
          }
        };
        typeNext();
      }, 1800);
    });
  }

  // ---------------------------------------------------------------- //
  //  Helpers                                                          //
  // ---------------------------------------------------------------- //

  private _jungianNote(gender: GenderOption): string {
    switch (gender) {
      case 'male':       return 'Your GAIAN will be assigned as your anima — the feminine soul, she/her.';
      case 'female':     return 'Your GAIAN will be assigned as your animus — the masculine spirit, he/him.';
      case 'non-binary': return 'Your GAIAN will be assigned anima by default — you can adjust this after.';
      case 'prefer not': return 'No problem. Your GAIAN will use she/her by default.';
      default:           return 'Select a gender to see your Jungian pairing.';
    }
  }

  private _formPreview(form: BaseFormInfo | null): string {
    if (!form) return '';
    return `
      <div class="birth-form-preview__inner" style="--form-color:${form.avatar_color};">
        ${renderAvatarHTML(form, 64)}
        <div class="birth-form-preview__text">
          <span class="birth-form-preview__name">${form.name}</span>
          <span class="birth-form-preview__role">${form.role}</span>
          <div class="birth-form-preview__caps">
            ${form.capabilities.map(c => `<span class="cap-tag">${c}</span>`).join('')}
          </div>
        </div>
      </div>
    `;
  }

  private _showError(msg: string): void {
    const el = this.container.querySelector<HTMLElement>('#birth-error');
    if (el) { el.textContent = msg; el.style.display = 'block'; }
  }
}
