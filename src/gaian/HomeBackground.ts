/**
 * HomeBackground.ts
 * Manages the parallax room-photo backdrop behind the GaianOrb.
 * - Loads a room scan image from the GAIA data dir (if available)
 * - Falls back to a deep-space CSS gradient
 * - Applies subtle mouse-parallax for depth illusion
 * - Adds a soft vignette overlay so the orb reads against any background
 */

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

    // Try to load a saved room scan
    this._tryLoadRoom(container);
  }

  private async _tryLoadRoom(container: HTMLElement): Promise<void> {
    // Dynamic import so it doesn’t crash in a non-Tauri web context
    try {
      const { appDataDir, join } = await import('@tauri-apps/api/path');
      const { exists }           = await import('@tauri-apps/plugin-fs');
      const dataDir   = await appDataDir();
      const roomPath  = await join(dataDir, 'room.jpg');
      if (await exists(roomPath)) {
        // Use Tauri’s asset protocol to serve the file
        const { convertFileSrc } = await import('@tauri-apps/api/core');
        const assetUrl = convertFileSrc(roomPath);
        this.bg.style.backgroundImage = `url('${assetUrl}')`;
        this.bg.classList.add('has-room');
      }
    } catch {
      // Not running in Tauri, or no room scan — fallback gradient is already active
      void container; // suppress unused-in-catch lint noise
    }
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
