/**
 * ConvertMD 3D Web Experience - Three.js WebGL Interactive Scene
 * Developed following the 3d-web-experience & impeccable skill principles.
 * Zero emojis, clean vector texturing, high performance (<10k polygons), battery-friendly.
 */

import * as THREE from 'https://unpkg.com/three@0.160.0/build/three.module.js';

class ConvertMD3DScene {
  constructor(canvasContainerId) {
    this.container = document.getElementById(canvasContainerId);
    if (!this.container) return;

    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.coreMesh = null;
    this.coreWireframe = null;
    this.documentCards = [];
    this.particleSystem = null;
    this.animationFrameId = null;
    this.isVisible = true;

    // Mouse parallax tracking
    this.mouse = { x: 0, y: 0, targetX: 0, targetY: 0 };
    this.clock = new THREE.Clock();

    // Check reduced motion preference
    this.reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    this.init();
  }

  init() {
    try {
      this.scene = new THREE.Scene();

      const width = this.container.clientWidth;
      const height = this.container.clientHeight;
      this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
      this.camera.position.set(0, 0, 7.5);

      this.renderer = new THREE.WebGLRenderer({
        antialias: true,
        alpha: true,
        powerPreference: 'high-performance'
      });
      this.renderer.setSize(width, height);
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
      this.renderer.toneMappingExposure = 1.1;

      const canvas = this.renderer.domElement;
      canvas.id = 'canvas-3d';
      this.container.appendChild(canvas);

      this.setupLights();
      this.createCentralCore();
      this.createOrbitingDocuments();
      this.createDataParticles();
      this.setupEventListeners();
      this.setupIntersectionObserver();
      this.animate();
    } catch (e) {
      console.warn('ConvertMD WebGL initialized with fallback:', e);
      this.renderFallback();
    }
  }

  setupLights() {
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.75);
    this.scene.add(ambientLight);

    const blueLight = new THREE.PointLight(0x89b4fa, 3.5, 20);
    blueLight.position.set(4, 3, 4);
    this.scene.add(blueLight);

    const greenLight = new THREE.PointLight(0x22c55e, 2.8, 18);
    greenLight.position.set(-4, -3, 3);
    this.scene.add(greenLight);

    const rimLight = new THREE.DirectionalLight(0xcba6f7, 1.2);
    rimLight.position.set(0, 5, -2);
    this.scene.add(rimLight);
  }

  createCentralCore() {
    const geometry = new THREE.OctahedronGeometry(1.35, 0);

    const material = new THREE.MeshPhysicalMaterial({
      color: 0x181825,
      emissive: 0x1e293b,
      roughness: 0.15,
      metalness: 0.8,
      clearcoat: 1.0,
      clearcoatRoughness: 0.1,
      transparent: true,
      opacity: 0.92
    });

    this.coreMesh = new THREE.Mesh(geometry, material);
    this.scene.add(this.coreMesh);

    const wireGeo = new THREE.WireframeGeometry(geometry);
    const wireMat = new THREE.LineBasicMaterial({
      color: 0x89b4fa,
      transparent: true,
      opacity: 0.75,
      linewidth: 1.5
    });
    this.coreWireframe = new THREE.LineSegments(wireGeo, wireMat);
    this.coreMesh.add(this.coreWireframe);

    const ringGeo = new THREE.TorusGeometry(2.1, 0.02, 16, 100);
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0x38bdf8,
      transparent: true,
      opacity: 0.4
    });
    this.ringMesh = new THREE.Mesh(ringGeo, ringMat);
    this.ringMesh.rotation.x = Math.PI / 2.5;
    this.scene.add(this.ringMesh);
  }

  createDocumentCardTexture(text, colorHex, badgeText) {
    const canvas = document.createElement('canvas');
    canvas.width = 256;
    canvas.height = 160;
    const ctx = canvas.getContext('2d');

    // Rounded card background
    ctx.fillStyle = '#181825';
    ctx.strokeStyle = colorHex;
    ctx.lineWidth = 6;
    
    const r = 16;
    ctx.beginPath();
    ctx.moveTo(r, 0);
    ctx.lineTo(256 - r, 0);
    ctx.quadraticCurveTo(256, 0, 256, r);
    ctx.lineTo(256, 160 - r);
    ctx.quadraticCurveTo(256, 160, 256 - r, 160);
    ctx.lineTo(r, 160);
    ctx.quadraticCurveTo(0, 160, 0, 160 - r);
    ctx.lineTo(0, r);
    ctx.quadraticCurveTo(0, 0, r, 0);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Clean vector document icon with folded corner (NO EMOJI)
    ctx.fillStyle = colorHex;
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(34, 28);
    ctx.lineTo(46, 28);
    ctx.lineTo(52, 34);
    ctx.lineTo(52, 54);
    ctx.lineTo(34, 54);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Main format extension text
    ctx.fillStyle = '#f8fafc';
    ctx.font = 'bold 26px -apple-system, sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText(text, 68, 48);

    // Subtitle label
    ctx.fillStyle = '#94a3b8';
    ctx.font = '14px monospace';
    ctx.fillText(badgeText, 32, 115);

    const texture = new THREE.CanvasTexture(canvas);
    texture.minFilter = THREE.LinearFilter;
    return texture;
  }

  createOrbitingDocuments() {
    const docFormats = [
      { ext: '.DOCX', color: '#38bdf8', label: 'Office Word' },
      { ext: '.XLSX', color: '#22c55e', label: 'Excel Spreadsheets' },
      { ext: '.PDF',  color: '#f87171', label: 'Adobe Acrobat' },
      { ext: '.PPTX', color: '#fb923c', label: 'PowerPoint Slides' },
      { ext: '.CSV',  color: '#34d399', label: 'Tabular Data' },
      { ext: '.OCR',  color: '#cba6f7', label: 'Images & Text' }
    ];

    const cardGeometry = new THREE.PlaneGeometry(1.2, 0.75);

    docFormats.forEach((doc, index) => {
      const texture = this.createDocumentCardTexture(doc.ext, doc.color, doc.label);
      const cardMaterial = new THREE.MeshStandardMaterial({
        map: texture,
        transparent: true,
        side: THREE.DoubleSide,
        roughness: 0.3,
        metalness: 0.1
      });

      const cardMesh = new THREE.Mesh(cardGeometry, cardMaterial);
      const angle = (index / docFormats.length) * Math.PI * 2;
      const radius = 2.85;

      cardMesh.userData = {
        baseAngle: angle,
        orbitRadius: radius,
        orbitSpeed: 0.45,
        verticalOffset: Math.sin(index * 1.5) * 0.5,
        floatFreq: 1.2 + (index % 3) * 0.4
      };

      this.scene.add(cardMesh);
      this.documentCards.push(cardMesh);
    });
  }

  createDataParticles() {
    const particleCount = 220;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    const colorBlue = new THREE.Color(0x89b4fa);
    const colorGreen = new THREE.Color(0x22c55e);

    for (let i = 0; i < particleCount; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(Math.random() * 2 - 1);
      const r = 1.6 + Math.random() * 2.2;

      positions[i * 3]     = r * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      positions[i * 3 + 2] = r * Math.cos(phi);

      const mixedColor = colorBlue.clone().lerp(colorGreen, Math.random());
      colors[i * 3]     = mixedColor.r;
      colors[i * 3 + 1] = mixedColor.g;
      colors[i * 3 + 2] = mixedColor.b;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
      size: 0.055,
      vertexColors: true,
      transparent: true,
      opacity: 0.75,
      blending: THREE.AdditiveBlending
    });

    this.particleSystem = new THREE.Points(geometry, material);
    this.scene.add(this.particleSystem);
  }

  setupEventListeners() {
    window.addEventListener('resize', () => this.onWindowResize());

    this.container.addEventListener('mousemove', (e) => {
      const rect = this.container.getBoundingClientRect();
      this.mouse.targetX = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      this.mouse.targetY = -(((e.clientY - rect.top) / rect.height) * 2 - 1);
    });

    this.container.addEventListener('mouseleave', () => {
      this.mouse.targetX = 0;
      this.mouse.targetY = 0;
    });
  }

  setupIntersectionObserver() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        this.isVisible = entry.isIntersecting;
        if (this.isVisible && !this.animationFrameId) {
          this.animate();
        }
      });
    }, { threshold: 0.1 });

    observer.observe(this.container);
  }

  onWindowResize() {
    if (!this.container || !this.renderer || !this.camera) return;
    const width = this.container.clientWidth;
    const height = this.container.clientHeight;
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);
  }

  animate() {
    if (!this.isVisible) {
      this.animationFrameId = null;
      return;
    }

    this.animationFrameId = requestAnimationFrame(() => this.animate());

    const delta = this.clock.getDelta();
    const elapsedTime = this.clock.getElapsedTime();

    this.mouse.x += (this.mouse.targetX - this.mouse.x) * 0.05;
    this.mouse.y += (this.mouse.targetY - this.mouse.y) * 0.05;

    this.camera.position.x = this.mouse.x * 0.7;
    this.camera.position.y = this.mouse.y * 0.5;
    this.camera.lookAt(0, 0, 0);

    if (this.coreMesh) {
      const speed = this.reducedMotion ? 0.05 : 0.45;
      this.coreMesh.rotation.y = elapsedTime * speed;
      this.coreMesh.rotation.x = Math.sin(elapsedTime * 0.5) * 0.2;

      const scale = 1.0 + Math.sin(elapsedTime * 1.5) * 0.03;
      this.coreMesh.scale.set(scale, scale, scale);
    }

    if (this.ringMesh) {
      this.ringMesh.rotation.z = elapsedTime * 0.2;
    }

    this.documentCards.forEach((card) => {
      const u = card.userData;
      const angle = u.baseAngle + (elapsedTime * u.orbitSpeed * (this.reducedMotion ? 0.2 : 0.6));

      card.position.x = Math.cos(angle) * u.orbitRadius;
      card.position.z = Math.sin(angle) * u.orbitRadius;
      card.position.y = u.verticalOffset + Math.sin(elapsedTime * u.floatFreq) * 0.15;

      card.lookAt(this.camera.position);
    });

    if (this.particleSystem) {
      this.particleSystem.rotation.y = elapsedTime * 0.15;
      this.particleSystem.rotation.x = elapsedTime * 0.08;
    }

    this.renderer.render(this.scene, this.camera);
  }

  renderFallback() {
    this.container.innerHTML = `
      <div style="text-align: center; padding: 2rem; color: #89b4fa;">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 1rem;">
          <polygon points="12 2 2 7 12 12 22 7 12 2"/>
          <polyline points="2 17 12 22 22 17"/>
          <polyline points="2 12 12 17 22 12"/>
        </svg>
        <p style="font-weight: 600; color: #f8fafc;">ConvertMD Hub Visualizer</p>
        <p style="font-size: 0.85rem; color: #94a3b8;">Transformación universal de documentos a Markdown optimizado.</p>
      </div>
    `;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('scene3d-container');
  if (container) {
    new ConvertMD3DScene('scene3d-container');
  }
});
