/**
 * HomeBackground.ts
 * Manages the parallax room-photo backdrop behind the GaianOrb.
 *
 * Fallback chain (first success wins):
 *   1. Saved room scan via Tauri asset protocol (~/.local/share/GAIA/room.jpg)
 *   2. Bundled dev reference image (src/assets/room-reference.png)
 *   3. Deep-space CSS gradient
 *
 * - Applies subtle mouse-parallax for depth illusion
 * - Adds a soft vignette overlay so the orb reads against any background
 */

// Vite static import — bundled at build time so it works in both dev and prod
import roomReferenceUrl from '../assets/room-reference.png';

export class HomeBackground {
  private bg: HTMLDivElement;
  private vignette: HTMLDivElement;
  private _onMouseMove: (e: MouseEvent) => void;

  constructor(container: HTMLElement) {
    // Background layer
    this.bg = document.createElement('div');
    this.bg.className = 'home-bg';
    container.insertBefore(this.bg, container.firstChild);

    // Vignette overlay
    this.vignette = document.createElement('div');
    this.vignette.className = 'home-vignette';
    container.insertBefore(this.vignette, container.firstChild);

    // Parallax handler
    this._onMouseMove = this._handleMouseMove.bind(this);
    window.addEventListener('mousemove', this._onMouseMove, { passive: true });

    // Try to load a saved room scan; fall back to bundled reference
    this._tryLoadRoom(container);
  }

  private async _tryLoadRoom(container: HTMLElement): Promise<void> {
    // 1 — Try Tauri saved room scan
    try {
      const { appDataDir, join } = await import('@tauri-apps/api/path');
      const { exists }           = await import('@tauri-apps/plugin-fs');
      const dataDir   = await appDataDir();
      const roomPath  = await join(dataDir, 'room.jpg');
      if (await exists(roomPath)) {
        const { convertFileSrc } = await import('@tauri-apps/api/core');
        const assetUrl = convertFileSrc(roomPath);
        this._applyImage(assetUrl);
        return;
      }
    } catch {
      void container;
    }

    // 2 — Fall back to bundled reference image
    if (roomReferenceUrl) {
      this._applyImage(roomReferenceUrl);
      return;
    }

    // 3 — Pure CSS gradient (already active via .home-bg default styles)
  }

  private _applyImage(url: string): void {
    this.bg.style.backgroundImage = `url('${url}')`;
    this.bg.classList.add('has-room');
  }

  private _handleMouseMove(e: MouseEvent): void {
    const { innerWidth: w, innerHeight: h } = window;
    const dx = ((e.clientX / w) - 0.5) * 12; // ±6px horizontal shift
    const dy = ((e.clientY / h) - 0.5) * 8;  // ±4px vertical shift
    this.bg.style.transform = `translate(${dx}px, ${dy}px) scale(1.04)`;
  }

  dispose(): void {
    window.removeEventListener('mousemove', this._onMouseMove);
    this.bg.remove();
    this.vignette.remove();
  }
}
