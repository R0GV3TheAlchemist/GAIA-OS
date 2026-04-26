/**
 * SurfaceDetector.ts
 *
 * Detects flat horizontal surfaces in the room panorama
 * using a lightweight heuristic (brightness row analysis).
 * Allows the user to tap/click a surface to place GAIA there.
 * Placement is persisted via RoomStore.
 *
 * Full depth-sensing requires XRDepthInformation (Phase 3b).
 * This provides a usable desktop-friendly approximation.
 *
 * Canon Ref: C20 (Home Twin — Spatial Presence)
 */

import { RoomStore, type GAIAPlacement } from './RoomStore';

export interface Surface {
  id: string;
  label: string;
  yPercent: number;   // vertical position in panorama as 0-1
  confidence: number; // 0-1
}

export class SurfaceDetector {
  private container: HTMLElement;
  private store: RoomStore;
  private onPlace: (placement: GAIAPlacement) => void;
  private surfaces: Surface[] = [];

  constructor(container: HTMLElement, onPlace: (placement: GAIAPlacement) => void) {
    this.container = container;
    this.store     = new RoomStore();
    this.onPlace   = onPlace;
  }

  /**
   * Analyse a panorama image and return candidate horizontal surfaces.
   * Uses brightness-gradient analysis: surfaces typically show a sharp
   * horizontal brightness transition (light from above hitting a flat plane).
   */
  async detect(panoramaDataUrl: string): Promise<Surface[]> {
    const img = await this._loadImage(panoramaDataUrl);
    const canvas = document.createElement('canvas');
    // Analyse at reduced resolution for speed
    canvas.width  = 320;
    canvas.height = 160;
    const ctx = canvas.getContext('2d')!;
    ctx.drawImage(img, 0, 0, 320, 160);
    const { data } = ctx.getImageData(0, 0, 320, 160);

    // Compute per-row average brightness
    const rowBrightness: number[] = [];
    for (let y = 0; y < 160; y++) {
      let sum = 0;
      for (let x = 0; x < 320; x++) {
        const i = (y * 320 + x) * 4;
        sum += (data[i] * 0.299 + data[i+1] * 0.587 + data[i+2] * 0.114);
      }
      rowBrightness.push(sum / 320);
    }

    // Find rows with high downward brightness gradient (surface top edge)
    const surfaces: Surface[] = [];
    const LABELS = ['floor', 'desk', 'table', 'shelf', 'bed'];
    for (let y = 2; y < 158; y++) {
      const grad = rowBrightness[y] - rowBrightness[y + 1];
      if (grad > 18) { // threshold for a significant brightness drop
        const yPct = y / 160;
        // Avoid clustering — must be >8% away from last surface
        const last = surfaces[surfaces.length - 1];
        if (!last || Math.abs(yPct - last.yPercent) > 0.08) {
          surfaces.push({
            id:         `surface-${y}`,
            label:      LABELS[surfaces.length % LABELS.length],
            yPercent:   yPct,
            confidence: Math.min(1, grad / 60),
          });
        }
      }
    }

    this.surfaces = surfaces.slice(0, 5);
    return this.surfaces;
  }

  /**
   * Render clickable surface overlay on the container.
   * Each detected surface gets a horizontal highlight band.
   */
  renderOverlay(): void {
    this.container.querySelectorAll('.ht-surface-overlay').forEach(el => el.remove());

    for (const surface of this.surfaces) {
      const band = document.createElement('div');
      band.className = 'ht-surface-overlay';
      band.dataset.id = surface.id;
      band.style.cssText = `
        position:absolute; left:0; right:0;
        top:${(surface.yPercent * 100).toFixed(1)}%;
        height:3px;
        background:rgba(34,197,94,0.55);
        cursor:pointer; z-index:10;
        transition: background 0.2s;
      `;
      band.title = `Place GAIA on ${surface.label} (${Math.round(surface.confidence * 100)}% confidence)`;

      const pill = document.createElement('span');
      pill.className = 'ht-surface-pill';
      pill.textContent = `◉ ${surface.label}`;
      pill.style.cssText = `
        position:absolute; left:12px; top:-12px;
        background:rgba(0,0,0,0.7); color:#22c55e;
        font-size:11px; padding:2px 8px; border-radius:8px;
        pointer-events:none;
      `;
      band.appendChild(pill);

      band.addEventListener('click', () => this._placeSurface(surface, band));
      band.addEventListener('mouseenter', () => band.style.background = 'rgba(34,197,94,0.9)');
      band.addEventListener('mouseleave', () => band.style.background = 'rgba(34,197,94,0.55)');

      this.container.appendChild(band);
    }
  }

  private async _placeSurface(surface: Surface, band: HTMLElement): Promise<void> {
    const placement: GAIAPlacement = {
      surfaceId:   surface.id,
      surfaceLabel: surface.label,
      yPercent:    surface.yPercent,
      placedAt:    new Date().toISOString(),
    };
    await this.store.savePlacement(placement);

    // Visual confirmation
    band.style.background = 'rgba(167,139,250,0.9)';
    band.querySelector('span')!.textContent = `✓ GAIA placed on ${surface.label}`;
    setTimeout(() => {
      this.container.querySelectorAll('.ht-surface-overlay').forEach(el => el.remove());
    }, 1200);

    this.onPlace(placement);
  }

  private _loadImage(src: string): Promise<HTMLImageElement> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload  = () => resolve(img);
      img.onerror = reject;
      img.src = src;
    });
  }
}
