/* Hero background: wireframe elevation contours of the northern cerros.
   Loaded lazily (desktop, post-load, motion-safe) from index.js. */
import * as THREE from './vendor/three.module.min.js';

const ROWS = 64;
const COLS = 120;
const WIDTH = 44;
const DEPTH = 26;

// Brand colors (tailwind tokens --color-primary-soft / --color-background-dark)
const TERRACOTTA = new THREE.Color('#c0625d');
const BACKGROUND = new THREE.Color('#1d1515');

/* Ridged pseudo-noise: cheap sin/cos octaves, peaks like eroded ridgelines. */
function height(x, z, t) {
  const ridge = (u, v) => 1 - Math.abs(Math.sin(u) * Math.cos(v));
  let h = 0;
  h += ridge(x * 0.14 + t * 0.18, z * 0.21 - t * 0.05) * 1.9;
  h += ridge(x * 0.33 - t * 0.11, z * 0.42 + 1.7) * 0.7;
  h += Math.sin(x * 0.9 + z * 1.3 + t * 0.4) * 0.12;
  // Amplitude swells toward the right and the horizon, valley under the copy
  const swell = THREE.MathUtils.smoothstep(x, -WIDTH * 0.45, WIDTH * 0.42);
  const far = THREE.MathUtils.smoothstep(-z, -DEPTH * 0.15, DEPTH * 0.4);
  return h * (0.25 + swell * 1.15) * (0.45 + far * 0.8);
}

export function mountHero3D(container) {
  const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: 'low-power' });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
  renderer.setSize(container.clientWidth, container.clientHeight);
  container.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(50, container.clientWidth / container.clientHeight, 0.1, 80);
  const camBase = new THREE.Vector3(0, 3.1, 9.6);
  camera.position.copy(camBase);

  // One LineSegments buffer: ROWS contour lines running along X
  const segCount = ROWS * (COLS - 1) * 2;
  const positions = new Float32Array(segCount * 3);
  const colors = new Float32Array(segCount * 3);
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  const material = new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, opacity: 0.62 });
  scene.add(new THREE.LineSegments(geometry, material));

  const gridX = (c) => (c / (COLS - 1) - 0.5) * WIDTH;
  const gridZ = (r) => (r / (ROWS - 1)) * -DEPTH + 2;
  const tmp = new THREE.Color();

  function update(t) {
    let i = 0;
    for (let r = 0; r < ROWS; r++) {
      const z = gridZ(r);
      const depthFade = 1 - r / (ROWS - 1); // far rows sink into the background
      for (let c = 0; c < COLS - 1; c++) {
        for (const cc of [c, c + 1]) {
          const x = gridX(cc);
          const y = height(x, z, t);
          positions[i * 3] = x;
          positions[i * 3 + 1] = y;
          positions[i * 3 + 2] = z;
          // Brightness follows elevation, fades with distance; alpha-free fade
          // works because lines blend toward the page background color.
          const lum = 0.16 + Math.min(y * 0.24, 0.5) + depthFade * 0.28;
          tmp.copy(BACKGROUND).lerp(TERRACOTTA, Math.min(lum, 1));
          colors[i * 3] = tmp.r;
          colors[i * 3 + 1] = tmp.g;
          colors[i * 3 + 2] = tmp.b;
          i++;
        }
      }
    }
    geometry.attributes.position.needsUpdate = true;
    geometry.attributes.color.needsUpdate = true;
  }

  // Gentle pointer parallax (lerped; no re-render storms, runs inside rAF)
  const pointer = { x: 0, y: 0 };
  const onPointer = (e) => {
    pointer.x = (e.clientX / window.innerWidth - 0.5) * 2;
    pointer.y = (e.clientY / window.innerHeight - 0.5) * 2;
  };
  window.addEventListener('pointermove', onPointer, { passive: true });

  let raf = null;
  let visible = true;
  const clock = new THREE.Clock();
  let elapsed = 0;

  function frame() {
    raf = null;
    elapsed += clock.getDelta();
    update(elapsed * 0.55);
    camera.position.x = camBase.x + THREE.MathUtils.lerp(camera.position.x - camBase.x, pointer.x * 0.45, 0.05);
    camera.position.y = camBase.y + THREE.MathUtils.lerp(camera.position.y - camBase.y, -pointer.y * 0.25, 0.05);
    camera.lookAt(0, 0.7, -4);
    renderer.render(scene, camera);
    if (visible) raf = requestAnimationFrame(frame);
  }

  function play() {
    if (!raf && visible) {
      clock.getDelta(); // swallow the pause gap
      raf = requestAnimationFrame(frame);
    }
  }

  function stop() {
    if (raf) cancelAnimationFrame(raf);
    raf = null;
  }

  const io = new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting;
    visible ? play() : stop();
  });
  io.observe(container);
  document.addEventListener('visibilitychange', () => (document.hidden ? stop() : play()));

  window.addEventListener('resize', () => {
    renderer.setSize(container.clientWidth, container.clientHeight);
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
  });

  update(0);
  renderer.render(scene, camera);
  renderer.domElement.classList.add('is-ready');
  play();
}
