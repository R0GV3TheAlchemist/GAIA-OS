/**
 * GaianPicker.ts — v0.5.1
 *
 * A UI component that:
 *   1. Fetches available Base Forms from GET /gaians/base-forms
 *   2. Fetches the user's existing GAIANs from GET /gaians
 *   3. Renders a picker panel with Base Form cards + a "New GAIAN" flow
 *   4. For new creation: launches GaianBirth wizard (POST /gaians/birth)
 *   5. For existing GAIANs: activates them for the session
 *
 * v0.5.1 changes:
 *   - spawnGaian() deprecated → birthGaian() (re-exported from GaianBirth)
 *   - buildGaianPickerHTML() now renders a "+ New GAIAN" button that
 *     mounts the GaianBirth wizard in-place instead of an inline form
 *   - GaianInfo extended with jungian_role, pronouns, did (from born GAIANs)
 *
 * Usage: import { GaianPicker } from '../gaian/GaianPicker'
 */

import { API_BASE } from '../app';

export interface BaseFormInfo {
  id: string;
  name: string;
  role: string;
  avatar_color: string;
  avatar_style: string;
  capabilities: string[];
  is_default: boolean;
}

export interface GaianInfo {
  id: string;
  name: string;
  slug: string;
  base_form_id: string;
  avatar_color: string;
  avatar_style: string;
  relationship_depth: number;
  total_exchanges: number;
  last_active: number;
  // Fields present on GAIANs born via /gaians/birth (v0.5.1+)
  jungian_role?: string;
  pronouns?:     string;
  did?:          string;
}

// ------------------------------------------------------------------ //
//  API                                                                 //
// ------------------------------------------------------------------ //

export async function fetchBaseForms(): Promise<BaseFormInfo[]> {
  const res = await fetch(`${API_BASE}/gaians/base-forms`);
  if (!res.ok) throw new Error('Failed to fetch base forms');
  const data = await res.json();
  return data.base_forms;
}

export async function fetchGaians(): Promise<GaianInfo[]> {
  const res = await fetch(`${API_BASE}/gaians`);
  if (!res.ok) throw new Error('Failed to fetch GAIANs');
  const data = await res.json();
  return data.gaians;
}

/**
 * @deprecated Use birthGaian() from GaianBirth.ts for new GAIAN creation.
 * This function calls the legacy POST /gaians endpoint (no DID, no Jungian
 * assignment, no first_words). Kept for internal/admin use only.
 */
export async function spawnGaian(
  name: string,
  baseFormId: string,
  userName?: string,
): Promise<GaianInfo> {
  const res = await fetch(`${API_BASE}/gaians`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, base_form: baseFormId, user_name: userName }),
  });
  if (!res.ok) throw new Error('Failed to spawn GAIAN');
  return res.json();
}

export async function setActiveGaian(
  sessionId: string,
  gaianSlug: string,
): Promise<void> {
  await fetch(`${API_BASE}/session/${sessionId}/gaian`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ gaian_slug: gaianSlug }),
  });
}

// ------------------------------------------------------------------ //
//  Avatar Renderer                                                     //
// ------------------------------------------------------------------ //

export function renderAvatarHTML(form: BaseFormInfo | GaianInfo, size = 64): string {
  const style = form.avatar_style;
  const color = form.avatar_color;
  const s = `${size}px`;

  if (style === 'digital_earth') {
    return `
      <div class="gaian-avatar gaian-avatar--earth" style="width:${s};height:${s};">
        <div class="earth-globe" style="--earth-color:${color};">
          <div class="earth-land"></div>
          <div class="earth-clouds"></div>
          <div class="earth-glow"></div>
        </div>
      </div>`;
  }

  const initials = ('name' in form ? form.name : 'G').slice(0, 2).toUpperCase();
  return `
    <div class="gaian-avatar gaian-avatar--${style}"
         style="width:${s};height:${s};background:${color};">
      <span class="gaian-avatar__initials">${initials}</span>
    </div>`;
}

// ------------------------------------------------------------------ //
//  Picker Panel Builder                                                //
// ------------------------------------------------------------------ //

/**
 * Builds and mounts the GAIAN picker UI into the given container.
 * Existing GAIANs are shown as clickable cards (calls setActiveGaian).
 * "+ New GAIAN" button mounts the GaianBirth wizard in-place.
 *
 * @param container  The HTMLElement to render into
 * @param sessionId  Current session ID (for setActiveGaian)
 * @param onSelect   Called when an existing GAIAN is activated
 * @param onBorn     Called when a new GAIAN completes birth sequence
 */
export async function mountGaianPicker(
  container: HTMLElement,
  sessionId: string,
  onSelect: (gaian: GaianInfo) => void,
  onBorn: (result: import('./GaianBirth').GaianBirthResult) => void,
): Promise<void> {
  container.innerHTML = '<div class="birth-loading">Loading your GAIANs…</div>';

  const [baseForms, myGaians] = await Promise.all([fetchBaseForms(), fetchGaians()]
    .map(p => p.catch(() => []))
  ) as [BaseFormInfo[], GaianInfo[]];

  const myGaianCards = myGaians.length > 0
    ? myGaians.map(g => `
      <div class="gaian-card" data-gaian-slug="${g.slug}"
           style="--gaian-color:${g.avatar_color};">
        ${renderAvatarHTML(g, 40)}
        <div class="gaian-card__info">
          <span class="gaian-card__name">${g.name}</span>
          <span class="gaian-card__depth">
            Depth ${g.relationship_depth}/100
            ${g.jungian_role ? `· <span class="gaian-card__role">${g.jungian_role}</span>` : ''}
          </span>
        </div>
      </div>
    `).join('')
    : '<p class="gaian-picker__empty">No GAIANs yet — bring your first into being below.</p>';

  container.innerHTML = `
    <div class="gaian-picker" id="gaian-picker">
      <section class="gaian-picker__section">
        <h2 class="gaian-picker__heading">Your GAIANs</h2>
        <div class="gaian-cards">${myGaianCards}</div>
      </section>

      <section class="gaian-picker__section">
        <h2 class="gaian-picker__heading">Base Forms</h2>
        <div class="base-form-cards">
          ${baseForms.map(f => `
            <div class="base-form-card" data-form-id="${f.id}"
                 style="--form-color:${f.avatar_color};">
              ${renderAvatarHTML(f, 48)}
              <div class="base-form-card__info">
                <span class="base-form-card__name">${f.name}</span>
                <span class="base-form-card__role">${f.role}</span>
                <div class="base-form-card__caps">
                  ${f.capabilities.map(c => `<span class="cap-tag">${c}</span>`).join('')}
                </div>
              </div>
              ${f.is_default ? '<span class="base-form-card__default-badge">Default</span>' : ''}
            </div>
          `).join('')}
        </div>
      </section>

      <section class="gaian-picker__section">
        <button class="birth-btn birth-btn--primary" id="open-birth-wizard">
          + Bring a new GAIAN into being
        </button>
      </section>

      <div id="birth-wizard-mount" style="display:none;"></div>
    </div>
  `;

  // Existing GAIAN cards
  container.querySelectorAll<HTMLElement>('.gaian-card')
    .forEach(card => {
      card.addEventListener('click', async () => {
        const slug = card.dataset.gaianSlug!;
        const gaian = myGaians.find(g => g.slug === slug);
        if (!gaian) return;
        await setActiveGaian(sessionId, slug);
        onSelect(gaian);
      });
    });

  // New GAIAN birth wizard
  container.querySelector('#open-birth-wizard')!
    .addEventListener('click', async () => {
      const mount = container.querySelector<HTMLElement>('#birth-wizard-mount')!;
      mount.style.display = 'block';
      container.querySelector<HTMLElement>('#gaian-picker > section:last-of-type')!.style.display = 'none';

      const { GaianBirth } = await import('./GaianBirth');
      const wizard = new GaianBirth(mount, sessionId, async (result) => {
        await setActiveGaian(sessionId, result.slug);
        onBorn(result);
      });
      wizard.mount();
    });
}

/**
 * @deprecated Use mountGaianPicker() instead.
 * Kept for backwards-compatibility with any existing callers.
 */
export async function buildGaianPickerHTML(sessionId: string): Promise<string> {
  const [baseForms, myGaians] = await Promise.all([fetchBaseForms(), fetchGaians()]);

  const baseFormCards = baseForms.map(f => `
    <div class="base-form-card" data-form-id="${f.id}"
         style="--form-color:${f.avatar_color};">
      ${renderAvatarHTML(f, 48)}
      <div class="base-form-card__info">
        <span class="base-form-card__name">${f.name}</span>
        <span class="base-form-card__role">${f.role}</span>
        <div class="base-form-card__caps">
          ${f.capabilities.map(c => `<span class="cap-tag">${c}</span>`).join('')}
        </div>
      </div>
      ${f.is_default ? '<span class="base-form-card__default-badge">Default</span>' : ''}
    </div>
  `).join('');

  const myGaianCards = myGaians.length > 0
    ? myGaians.map(g => `
      <div class="gaian-card" data-gaian-slug="${g.slug}"
           style="--gaian-color:${g.avatar_color};">
        ${renderAvatarHTML(g, 40)}
        <div class="gaian-card__info">
          <span class="gaian-card__name">${g.name}</span>
          <span class="gaian-card__depth">Depth ${g.relationship_depth}/100</span>
        </div>
      </div>
    `).join('')
    : '<p class="gaian-picker__empty">No GAIANs yet. Bring your first into being below.</p>';

  return `
    <div class="gaian-picker" id="gaian-picker">
      <section class="gaian-picker__section">
        <h2 class="gaian-picker__heading">Your GAIANs</h2>
        <div class="gaian-cards">${myGaianCards}</div>
      </section>
      <section class="gaian-picker__section">
        <h2 class="gaian-picker__heading">Base Forms</h2>
        <div class="base-form-cards">${baseFormCards}</div>
      </section>
      <section class="gaian-picker__section gaian-picker__spawn">
        <h2 class="gaian-picker__heading">Bring a new GAIAN into being</h2>
        <p style="color:var(--text-muted,#888);font-size:0.9rem;">
          Use <code>mountGaianPicker()</code> to access the full birth wizard.
        </p>
      </section>
    </div>
  `;
}
