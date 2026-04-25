/**
 * GaianOrb.ts
 * Living Earth avatar — Three.js WebGL renderer.
 *
 * Features:
 *  - Realistic land/ocean sphere with texture
 *  - Animated scrolling cloud layer
 *  - Fresnel atmosphere glow shader
 *  - GLSL aurora effect at the poles
 *  - Real-time day/night terminator line
 *  - GSAP-driven mood transitions
 *  - WebSocket listener for /mood events from the Python backend
 *
 * Usage:
 *   const orb = new GaianOrb(document.getElementById('orb-canvas') as HTMLCanvasElement);
 *   orb.start();
 *   orb.setMood('joyful');
 *   orb.dispose(); // cleanup on unmount
 */

import * as THREE from 'three';
import { gsap } from 'gsap';
import { gaianMood, GaianMoodState, MoodProfile, MOOD_PROFILES } from './GaianMood';

// ── GLSL Shaders ─────────────────────────────────────────────────────────────

const ATMOSPHERE_VERT = /* glsl */`
  varying vec3 vNormal;
  varying vec3 vPosition;
  void main() {
    vNormal   = normalize(normalMatrix * normal);
    vPosition = (modelViewMatrix * vec4(position, 1.0)).xyz;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

const ATMOSPHERE_FRAG = /* glsl */`
  uniform vec3  uGlowColor;
  uniform float uGlowIntensity;
  varying vec3  vNormal;
  varying vec3  vPosition;

  void main() {
    vec3  viewDir  = normalize(-vPosition);
    float rim      = 1.0 - max(dot(viewDir, vNormal), 0.0);
    float glow     = pow(rim, 3.5) * uGlowIntensity;
    gl_FragColor   = vec4(uGlowColor * glow, glow * 0.85);
  }
`;

const AURORA_VERT = /* glsl */`
  varying vec2 vUv;
  varying vec3 vNormal;
  void main() {
    vUv        = uv;
    vNormal    = normalize(normalMatrix * normal);
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

const AURORA_FRAG = /* glsl */`
  uniform float uTime;
  uniform float uIntensity;
  varying vec2  vUv;
  varying vec3  vNormal;

  float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
  }

  float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(
      mix(hash(i), hash(i + vec2(1,0)), f.x),
      mix(hash(i + vec2(0,1)), hash(i + vec2(1,1)), f.x),
      f.y
    );
  }

  void main() {
    // Only render near the poles (|latitude| > ~70°)
    float lat       = abs(vUv.y - 0.5) * 2.0;  // 0 at equator, 1 at pole
    float poleMask  = smoothstep(0.55, 0.85, lat);

    // Animated curtain bands
    float n  = noise(vec2(vUv.x * 6.0 + uTime * 0.3, vUv.y * 4.0 + uTime * 0.15));
    float n2 = noise(vec2(vUv.x * 12.0 - uTime * 0.2, vUv.y * 8.0));
    float band = smoothstep(0.35, 0.65, n) * smoothstep(0.4, 0.6, n2);

    // Aurora color — teal-green with purple fringe
    vec3  color = mix(vec3(0.0, 0.9, 0.6), vec3(0.5, 0.1, 0.9), n2);
    float alpha = poleMask * band * uIntensity * 0.75;

    gl_FragColor = vec4(color, alpha);
  }
`;

// ── Helper: hex string → THREE.Color ────────────────────────────────────────
function hexToColor(hex: string): THREE.Color {
  return new THREE.Color(hex);
}

// ── Sun direction from UTC time (approximate) ────────────────────────────────
function sunDirection(): THREE.Vector3 {
  const now    = new Date();
  const hours  = now.getUTCHours() + now.getUTCMinutes() / 60;
  // Sun longitude: noon UTC ≈ sun over prime meridian
  const sunLon = ((hours / 24) * 2 * Math.PI) - Math.PI;
  const sunLat = 0; // simplified — ignore seasonal declination for now
  return new THREE.Vector3(
    Math.cos(sunLat) * Math.cos(sunLon),
    Math.sin(sunLat),
    Math.cos(sunLat) * Math.sin(sunLon),
  ).normalize();
}

// ── GaianOrb class ───────────────────────────────────────────────────────────

export class GaianOrb {
  private canvas:     HTMLCanvasElement;
  private renderer:   THREE.WebGLRenderer;
  private scene:      THREE.Scene;
  private camera:     THREE.PerspectiveCamera;
  private clock:      THREE.Clock;

  // Meshes
  private earthMesh:   THREE.Mesh;
  private cloudMesh:   THREE.Mesh;
  private atmMesh:     THREE.Mesh;
  private auroraMesh:  THREE.Mesh;

  // Materials with uniforms we animate
  private atmMat:    THREE.ShaderMaterial;
  private auroraMat: THREE.ShaderMaterial;
  private cloudMat:  THREE.MeshStandardMaterial;

  // Lighting
  private sunLight: THREE.DirectionalLight;

  // State
  private _raf:      number | null = null;
  private _ws:       WebSocket | null = null;
  private _moodUnsub: (() => void) | null = null;

  // Current animated values (GSAP tweens these)
  private _live = {
    rotationSpeed:  MOOD_PROFILES.calm.rotationSpeed,
    glowIntensity:  MOOD_PROFILES.calm.glowIntensity,
    cloudOpacity:   MOOD_PROFILES.calm.cloudOpacity,
    auroraIntensity:MOOD_PROFILES.calm.auroraIntensity,
    pulsePhase:     0,
    scale:          1,
  };

  constructor(canvas: HTMLCanvasElement) {
    this.canvas = canvas;

    // ── Renderer
    this.renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      alpha: true,
    });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.setSize(canvas.clientWidth, canvas.clientHeight);

    // ── Scene + Camera
    this.scene  = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(45, canvas.clientWidth / canvas.clientHeight, 0.1, 100);
    this.camera.position.z = 2.8;
    this.clock  = new THREE.Clock();

    // ── Lights
    const ambient = new THREE.AmbientLight(0x111122, 0.6);
    this.scene.add(ambient);

    this.sunLight = new THREE.DirectionalLight(0xfff5e0, 1.4);
    this.sunLight.position.copy(sunDirection()).multiplyScalar(5);
    this.scene.add(this.sunLight);

    // ── Geometry (shared sphere)
    const sphere = new THREE.SphereGeometry(1, 64, 64);

    // ── Earth
    const earthMat = new THREE.MeshStandardMaterial({
      color:     0x1a4a7a,
      roughness: 0.85,
      metalness: 0.05,
    });
    // Texture loading — gracefully skipped if assets not present yet
    const loader = new THREE.TextureLoader();
    loader.load('/assets/earth-day.jpg',   t => { earthMat.map = t; earthMat.needsUpdate = true; });
    loader.load('/assets/earth-normal.jpg', t => { earthMat.normalMap = t; earthMat.needsUpdate = true; });

    this.earthMesh = new THREE.Mesh(sphere, earthMat);
    this.scene.add(this.earthMesh);

    // ── Clouds
    this.cloudMat = new THREE.MeshStandardMaterial({
      color:       0xffffff,
      transparent: true,
      opacity:     this._live.cloudOpacity,
      depthWrite:  false,
    });
    loader.load('/assets/earth-clouds.jpg', t => {
      this.cloudMat.alphaMap = t;
      this.cloudMat.needsUpdate = true;
    });
    this.cloudMesh = new THREE.Mesh(new THREE.SphereGeometry(1.008, 64, 64), this.cloudMat);
    this.scene.add(this.cloudMesh);

    // ── Atmosphere glow (inverted sphere, additive blend)
    this.atmMat = new THREE.ShaderMaterial({
      vertexShader:   ATMOSPHERE_VERT,
      fragmentShader: ATMOSPHERE_FRAG,
      uniforms: {
        uGlowColor:     { value: hexToColor(MOOD_PROFILES.calm.glowColor) },
        uGlowIntensity: { value: MOOD_PROFILES.calm.glowIntensity },
      },
      side:        THREE.BackSide,
      transparent: true,
      blending:    THREE.AdditiveBlending,
      depthWrite:  false,
    });
    this.atmMesh = new THREE.Mesh(new THREE.SphereGeometry(1.18, 64, 64), this.atmMat);
    this.scene.add(this.atmMesh);

    // ── Aurora (transparent overlay)
    this.auroraMat = new THREE.ShaderMaterial({
      vertexShader:   AURORA_VERT,
      fragmentShader: AURORA_FRAG,
      uniforms: {
        uTime:      { value: 0 },
        uIntensity: { value: MOOD_PROFILES.calm.auroraIntensity },
      },
      transparent: true,
      blending:    THREE.AdditiveBlending,
      depthWrite:  false,
      side:        THREE.FrontSide,
    });
    this.auroraMesh = new THREE.Mesh(new THREE.SphereGeometry(1.01, 64, 64), this.auroraMat);
    this.scene.add(this.auroraMesh);

    // ── Resize observer
    new ResizeObserver(() => this._onResize()).observe(canvas);
  }

  // ── Public API ──────────────────────────────────────────────────────────────

  start(): void {
    this._moodUnsub = gaianMood.onChange((_, profile) => this._transitionToProfile(profile));
    this._connectWebSocket();
    this._loop();
  }

  setMood(mood: GaianMoodState): void {
    gaianMood.set(mood);
  }

  dispose(): void {
    if (this._raf)    cancelAnimationFrame(this._raf);
    if (this._ws)     this._ws.close();
    if (this._moodUnsub) this._moodUnsub();
    this.renderer.dispose();
  }

  // ── Render loop ─────────────────────────────────────────────────────────────

  private _loop(): void {
    this._raf = requestAnimationFrame(() => this._loop());
    const elapsed = this.clock.getElapsedTime();
    const delta   = this.clock.getDelta();

    // Rotate Earth + clouds (clouds slightly faster for parallax feel)
    this.earthMesh.rotation.y  += this._live.rotationSpeed;
    this.cloudMesh.rotation.y  += this._live.rotationSpeed * 1.15;
    this.auroraMesh.rotation.y += this._live.rotationSpeed * 0.5;

    // Breathing pulse
    const profile = gaianMood.profile;
    const breathe = 1 + Math.sin(elapsed * profile.pulseFrequency * Math.PI * 2) * profile.pulseAmplitude;
    this.earthMesh.scale.setScalar(breathe);
    this.cloudMesh.scale.setScalar(breathe * 1.008);
    this.atmMesh.scale.setScalar(breathe * 1.18);

    // Update uniforms
    this.atmMat.uniforms.uGlowIntensity.value = this._live.glowIntensity;
    this.auroraMat.uniforms.uTime.value       = elapsed;
    this.auroraMat.uniforms.uIntensity.value  = this._live.auroraIntensity;
    this.cloudMat.opacity                     = this._live.cloudOpacity;

    // Update sun direction every 60s
    if (Math.floor(elapsed) % 60 === 0) {
      this.sunLight.position.copy(sunDirection()).multiplyScalar(5);
    }

    this.renderer.render(this.scene, this.camera);
  }

  // ── Mood transition (GSAP) ──────────────────────────────────────────────────

  private _transitionToProfile(profile: MoodProfile): void {
    gsap.to(this._live, {
      duration:        1.4,
      ease:            'power2.inOut',
      rotationSpeed:   profile.rotationSpeed,
      glowIntensity:   profile.glowIntensity,
      cloudOpacity:    profile.cloudOpacity,
      auroraIntensity: profile.auroraIntensity,
    });

    // Glow color requires direct THREE.Color lerp
    gsap.to(this.atmMat.uniforms.uGlowColor.value, {
      duration: 1.4,
      ease:     'power2.inOut',
      r: hexToColor(profile.glowColor).r,
      g: hexToColor(profile.glowColor).g,
      b: hexToColor(profile.glowColor).b,
    });
  }

  // ── WebSocket — backend /mood events ───────────────────────────────────────

  private _connectWebSocket(): void {
    const WS_URL = 'ws://localhost:8008/ws/mood';
    try {
      this._ws = new WebSocket(WS_URL);

      this._ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as { mood?: GaianMoodState; sentiment?: number };
          if (data.mood) {
            gaianMood.set(data.mood);
          } else if (typeof data.sentiment === 'number') {
            gaianMood.fromSentiment(data.sentiment);
          }
        } catch {
          // malformed message — ignore
        }
      };

      this._ws.onclose = () => {
        // Reconnect after 3s
        setTimeout(() => this._connectWebSocket(), 3000);
      };

      this._ws.onerror = () => {
        this._ws?.close();
      };
    } catch {
      // WebSocket not available (e.g. backend not running) — silent fail
    }
  }

  // ── Resize ──────────────────────────────────────────────────────────────────

  private _onResize(): void {
    const w = this.canvas.clientWidth;
    const h = this.canvas.clientHeight;
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(w, h);
  }
}
