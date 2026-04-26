/**
 * RoomRenderer.ts
 *
 * Loads the room panorama as a Three.js equirectangular skybox
 * and composites the GaianOrb canvas into the scene with:
 *   - Correct depth layering (orb floats in front of room)
 *   - Soft radial shadow beneath the orb (grounding)
 *   - Parallax mouse tracking for depth illusion
 *
 * Requires three.js: `npm install three @types/three`
 * Falls back to a gradient background if three.js is not installed.
 *
 * Canon Ref: C20 (Home Twin — Spatial Presence)
 */

import { RoomStore, type RoomConfig } from './RoomStore';

const PARALLAX_STRENGTH = 12;
const SHADOW_OPACITY    = 0.22;

export class RoomRenderer {
  private container: HTMLElement;
  private animFrame: number | null = null;
  private mouseX = 0;
  private mouseY = 0;
  private threeScene: ThreeScene | null = null;
  private config: RoomConfig | null = null;

  constructor(container: HTMLElement) {
    this.container = container;
  }

  async mount(): Promise<void> {
    const store = new RoomStore();
    this.config = await store.loadRoom();

    this._buildDOM();
    this._bindMouse();

    if (this.config?.panoramaDataUrl) {
      await this._mountThree(this.config.panoramaDataUrl);
    } else {
      this._mountFallbackGradient();
    }

    this._startLoop();
  }

  dispose(): void {
    if (this.animFrame !== null) cancelAnimationFrame(this.animFrame);
    this.threeScene?.dispose();
    this.container.querySelector('.ht-bg-layer')?.remove();
    this.container.querySelector('.ht-shadow')?.remove();
    document.removeEventListener('mousemove', this._onMouseMove);
  }

  // ------------------------------------------------------------------ //
  //  DOM                                                                 //
  // ------------------------------------------------------------------ //

  private _buildDOM(): void {
    const bg = document.createElement('div');
    bg.className = 'ht-bg-layer';
    this.container.prepend(bg);

    const shadow = document.createElement('div');
    shadow.className = 'ht-shadow';
    shadow.style.cssText = [
      'position:absolute; bottom:18%; left:50%; transform:translateX(-50%);',
      'width:160px; height:32px;',
      `background: radial-gradient(ellipse, rgba(0,0,0,${SHADOW_OPACITY}) 0%, transparent 70%);`,
      'pointer-events:none; z-index:2;',
    ].join(' ');
    this.container.appendChild(shadow);
  }

  private async _mountThree(panoramaDataUrl: string): Promise<void> {
    try {
      const THREE = await import('three');
      this.threeScene = new ThreeScene(this.container, THREE, panoramaDataUrl);
      await this.threeScene.init();
    } catch {
      this._mountFallbackGradient();
    }
  }

  private _mountFallbackGradient(): void {
    const bg = this.container.querySelector<HTMLElement>('.ht-bg-layer');
    if (bg) {
      bg.style.cssText = [
        'position:absolute; inset:0; z-index:0;',
        'background: radial-gradient(ellipse at 40% 60%, #0d2b1a 0%, #0a0a1a 55%, #1a0a2e 100%);',
      ].join(' ');
    }
  }

  // ------------------------------------------------------------------ //
  //  Parallax                                                            //
  // ------------------------------------------------------------------ //

  private _onMouseMove = (e: MouseEvent): void => {
    const rect = this.container.getBoundingClientRect();
    this.mouseX = ((e.clientX - rect.left) / rect.width  - 0.5) * 2;
    this.mouseY = ((e.clientY - rect.top)  / rect.height - 0.5) * 2;
  };

  private _bindMouse(): void {
    document.addEventListener('mousemove', this._onMouseMove, { passive: true });
  }

  private _startLoop(): void {
    const tick = () => {
      this.threeScene?.applyParallax(this.mouseX * PARALLAX_STRENGTH, this.mouseY * PARALLAX_STRENGTH);
      this.animFrame = requestAnimationFrame(tick);
    };
    this.animFrame = requestAnimationFrame(tick);
  }
}

// ---------------------------------------------------------------------------
// ThreeScene — encapsulates the three.js skybox
// ---------------------------------------------------------------------------

class ThreeScene {
  private container: HTMLElement;
  private THREE: typeof import('three');
  private panoramaDataUrl: string;
  private renderer: import('three').WebGLRenderer | null = null;
  private scene:    import('three').Scene | null = null;
  private camera:   import('three').PerspectiveCamera | null = null;
  private sphere:   import('three').Mesh | null = null;
  private animFrame: number | null = null;

  constructor(container: HTMLElement, THREE: typeof import('three'), panoramaDataUrl: string) {
    this.container       = container;
    this.THREE           = THREE;
    this.panoramaDataUrl = panoramaDataUrl;
  }

  async init(): Promise<void> {
    const THREE = this.THREE;
    const w = this.container.clientWidth  || window.innerWidth;
    const h = this.container.clientHeight || window.innerHeight;

    this.renderer = new THREE.WebGLRenderer({ antialias: false, alpha: true });
    this.renderer.setSize(w, h);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.domElement.className = 'ht-three-canvas';
    this.renderer.domElement.style.cssText = 'position:absolute;inset:0;z-index:0;';
    this.container.prepend(this.renderer.domElement);

    this.scene  = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(75, w / h, 0.1, 1000);
    this.camera.position.set(0, 0, 0.01);

    const texture = await new Promise<import('three').Texture>((resolve, reject) => {
      const loader = new THREE.TextureLoader();
      loader.load(this.panoramaDataUrl, resolve, undefined, reject);
    });
    texture.mapping = THREE.EquirectangularReflectionMapping;

    const geo = new THREE.SphereGeometry(500, 60, 40);
    geo.scale(-1, 1, 1);
    const mat = new THREE.MeshBasicMaterial({ map: texture });
    this.sphere = new THREE.Mesh(geo, mat);
    this.scene.add(this.sphere);

    window.addEventListener('resize', this._onResize);
    this._animate();
  }

  applyParallax(dx: number, dy: number): void {
    if (!this.camera) return;
    const targetYaw   = (dx / window.innerWidth)  * 0.08;
    const targetPitch = (dy / window.innerHeight) * 0.04;
    this.camera.rotation.y += (targetYaw   - this.camera.rotation.y) * 0.05;
    this.camera.rotation.x += (targetPitch - this.camera.rotation.x) * 0.05;
  }

  dispose(): void {
    if (this.animFrame !== null) cancelAnimationFrame(this.animFrame);
    window.removeEventListener('resize', this._onResize);
    this.renderer?.dispose();
    this.renderer?.domElement.remove();
    // suppress unused field warning
    void this.sphere;
  }

  private _onResize = (): void => {
    if (!this.renderer || !this.camera) return;
    const w = this.container.clientWidth;
    const h = this.container.clientHeight;
    this.renderer.setSize(w, h);
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
  };

  private _animate = (): void => {
    this.animFrame = requestAnimationFrame(this._animate);
    if (this.renderer && this.scene && this.camera) {
      this.renderer.render(this.scene, this.camera);
    }
  };
}
