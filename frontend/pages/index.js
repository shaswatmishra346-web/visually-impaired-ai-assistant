import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';

export default function Home() {
  const containerRef = useRef(null);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    if (!containerRef.current || isLoaded) return;

    // Scene setup
    const scene = new THREE.Scene();
    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;

    // Renderer
    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // Camera - positioned to view the globe from the left
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(-3.5, 0, 0);
    camera.lookAt(0, 0, 0);

    // Globe group
    const globeGroup = new THREE.Group();
    scene.add(globeGroup);

    // Earth geometry
    const earthGeometry = new THREE.SphereGeometry(1.5, 64, 64);

    // Earth material with procedural texture
    const earthMaterial = new THREE.MeshStandardMaterial({
      color: 0x0a1a2f,
      metalness: 0.1,
      roughness: 0.8,
    });
    const earth = new THREE.Mesh(earthGeometry, earthMaterial);
    globeGroup.add(earth);

    // Atmosphere glow
    const atmosphereGeometry = new THREE.SphereGeometry(1.6, 64, 64);
    const atmosphereMaterial = new THREE.MeshBasicMaterial({
      color: 0x00d4ff,
      transparent: true,
      opacity: 0.1,
      side: THREE.BackSide,
    });
    const atmosphere = new THREE.Mesh(atmosphereGeometry, atmosphereMaterial);
    globeGroup.add(atmosphere);

    // Wireframe overlay for tech look
    const wireframeGeometry = new THREE.SphereGeometry(1.52, 32, 32);
    const wireframeMaterial = new THREE.MeshBasicMaterial({
      color: 0x00d4ff,
      wireframe: true,
      transparent: true,
      opacity: 0.15,
    });
    const wireframe = new THREE.Mesh(wireframeGeometry, wireframeMaterial);
    globeGroup.add(wireframe);

    // Particle system for connection points
    const particlesGeometry = new THREE.BufferGeometry();
    const particleCount = 2000;
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    const sizes = new Float32Array(particleCount);

    const color1 = new THREE.Color(0x00d4ff);
    const color2 = new THREE.Color(0x7c3aed);
    const color3 = new THREE.Color(0x00ff88);

    for (let i = 0; i < particleCount; i++) {
      const radius = 1.5 + Math.random() * 0.3;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);

      positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
      positions[i * 3 + 2] = radius * Math.cos(phi);

      const colorChoice = Math.random();
      let color;
      if (colorChoice < 0.33) color = color1;
      else if (colorChoice < 0.66) color = color2;
      else color = color3;

      colors[i * 3] = color.r;
      colors[i * 3 + 1] = color.g;
      colors[i * 3 + 2] = color.b;

      sizes[i] = Math.random() * 2 + 1;
    }

    particlesGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    particlesGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    particlesGeometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

    const particlesMaterial = new THREE.PointsMaterial({
      size: 0.02,
      vertexColors: true,
      transparent: true,
      opacity: 0.6,
      sizeAttenuation: true,
    });
    const particles = new THREE.Points(particlesGeometry, particlesMaterial);
    globeGroup.add(particles);

    // Ring around the globe
    const ringGeometry = new THREE.RingGeometry(1.8, 2.0, 64);
    const ringMaterial = new THREE.MeshBasicMaterial({
      color: 0x00d4ff,
      transparent: true,
      opacity: 0.1,
      side: THREE.DoubleSide,
    });
    const ring = new THREE.Mesh(ringGeometry, ringMaterial);
    ring.rotation.x = -Math.PI / 2;
    globeGroup.add(ring);

    // Second ring rotating opposite direction
    const ring2Geometry = new THREE.RingGeometry(2.1, 2.2, 64);
    const ring2Material = new THREE.MeshBasicMaterial({
      color: 0x7c3aed,
      transparent: true,
      opacity: 0.08,
      side: THREE.DoubleSide,
    });
    const ring2 = new THREE.Mesh(ring2Geometry, ring2Material);
    ring2.rotation.x = Math.PI / 2.5;
    globeGroup.add(ring2);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(-5, 3, 5);
    scene.add(directionalLight);

    const pointLight1 = new THREE.PointLight(0x00d4ff, 1, 10);
    pointLight1.position.set(-3, 2, 3);
    scene.add(pointLight1);

    const pointLight2 = new THREE.PointLight(0x7c3aed, 1, 10);
    pointLight2.position.set(3, -2, -3);
    scene.add(pointLight2);

    // Animation loop
    let animationId;
    const clock = new THREE.Clock();

    const animate = () => {
      animationId = requestAnimationFrame(animate);

      const elapsed = clock.getElapsedTime();

      // Rotate globe
      globeGroup.rotation.y = elapsed * 0.05;

      // Rotate wireframe opposite
      wireframe.rotation.y = -elapsed * 0.03;
      wireframe.rotation.x = elapsed * 0.01;

      // Rotate particles
      particles.rotation.y = elapsed * 0.02;
      particles.rotation.x = Math.sin(elapsed * 0.1) * 0.1;

      // Rotate rings
      ring.rotation.z = elapsed * 0.02;
      ring2.rotation.z = -elapsed * 0.03;

      // Pulse atmosphere
      atmosphere.scale.setScalar(1 + Math.sin(elapsed * 2) * 0.02);
      atmosphere.material.opacity = 0.1 + Math.sin(elapsed * 1.5) * 0.03;

      // Pulse rings
      ring.material.opacity = 0.1 + Math.sin(elapsed * 1.8) * 0.03;
      ring2.material.opacity = 0.08 + Math.sin(elapsed * 2.2) * 0.02;

      // Float the whole group slightly
      globeGroup.position.y = Math.sin(elapsed * 0.5) * 0.05;

      renderer.render(scene, camera);
    };

    animate();

    // Handle resize
    const handleResize = () => {
      if (!containerRef.current) return;
      const width = containerRef.current.clientWidth;
      const height = containerRef.current.clientHeight;

      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    };

    window.addEventListener('resize', handleResize);
    setIsLoaded(true);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationId);
      renderer.dispose();
      earthGeometry.dispose();
      atmosphereGeometry.dispose();
      wireframeGeometry.dispose();
      particlesGeometry.dispose();
      ringGeometry.dispose();
      ring2Geometry.dispose();
      earthMaterial.dispose();
      atmosphereMaterial.dispose();
      wireframeMaterial.dispose();
      particlesMaterial.dispose();
      ringMaterial.dispose();
      ring2Material.dispose();
      if (containerRef.current) {
        containerRef.current.innerHTML = '';
      }
    };
  }, [isLoaded]);

  return (
    <div style={styles.page}>
      {/* Left side - Globe with content overlay */}
      <div style={styles.leftSection}>
        {/* 3D Globe Container */}
        <div
          ref={containerRef}
          style={styles.globeContainer}
          aria-label="Animated 3D Globe"
        />

        {/* Glassmorphism Content Overlay */}
        <div style={styles.contentOverlay}>
          <div style={styles.glassCard}>
            <div style={styles.logo}>
              <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="24" cy="24" r="22" stroke="url(#gradient)" strokeWidth="3"/>
                <path d="M24 14V34M14 24H34" stroke="url(#gradient)" strokeWidth="3" strokeLinecap="round"/>
                <defs>
                  <linearGradient id="gradient" x1="0" y1="0" x2="48" y2="48">
                    <stop stopColor="#00d4ff"/>
                    <stop offset="1" stopColor="#7c3aed"/>
                  </linearGradient>
                </defs>
              </svg>
            </div>
            <h1 style={styles.title}>Assistive AI Platform</h1>
            <p style={styles.subtitle}>
              Empowering the visually impaired with real-time AI assistance
            </p>
            <div style={styles.features}>
              <div style={styles.feature}>
                <span style={styles.featureIcon}>👁️</span>
                <span>Object Detection</span>
              </div>
              <div style={styles.feature}>
                <span style={styles.featureIcon}>📝</span>
                <span>Text Recognition</span>
              </div>
              <div style={styles.feature}>
                <span style={styles.featureIcon}>🎯</span>
                <span>Scene Description</span>
              </div>
              <div style={styles.feature}>
                <span style={styles.featureIcon}>🔊</span>
                <span>Audio Feedback</span>
              </div>
            </div>
            <a
              href="/app"
              style={styles.ctaButton}
            >
              Launch Application
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{marginLeft: '8px'}}>
                <path d="M5 12h14M12 5l7 7-7 7"/>
              </svg>
            </a>
            <p style={styles.footer}>
              Powered by AI • Real-time Processing • Privacy First
            </p>
          </div>
        </div>
      </div>

      {/* Right side - Visual accent */}
      <div style={styles.rightSection}>
        <div style={styles.accentPattern}></div>
        <div style={styles.stats}>
          <div style={styles.stat}>
            <span style={styles.statNumber}>99.9%</span>
            <span style={styles.statLabel}>Uptime</span>
          </div>
          <div style={styles.stat}>
            <span style={styles.statNumber}>{'<50ms'}</span>
            <span style={styles.statLabel}>Latency</span>
          </div>
          <div style={styles.stat}>
            <span style={styles.statNumber}>50+</span>
            <span style={styles.statLabel}>Languages</span>
          </div>
          <div style={styles.stat}>
            <span style={styles.statNumber}>24/7</span>
            <span style={styles.statLabel}>Support</span>
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  page: {
    display: 'flex',
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #050510 0%, #0a0a1a 50%, #0f0f23 100%)',
    color: '#ffffff',
    fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    overflow: 'hidden',
  },
  leftSection: {
    flex: '1',
    position: 'relative',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    minWidth: 0,
    padding: '2rem',
  },
  globeContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    zIndex: 1,
  },
  contentOverlay: {
    position: 'relative',
    zIndex: 10,
    width: '100%',
    maxWidth: '500px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '2rem',
  },
  glassCard: {
    width: '100%',
    background: 'rgba(15, 15, 35, 0.7)',
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
    border: '1px solid rgba(0, 212, 255, 0.2)',
    borderRadius: '24px',
    padding: '3rem',
    boxShadow: `
      0 8px 32px rgba(0, 0, 0, 0.4),
      0 0 0 1px rgba(0, 212, 255, 0.1) inset,
      0 0 60px rgba(0, 212, 255, 0.05)
    `,
    textAlign: 'center',
  },
  logo: {
    marginBottom: '1.5rem',
    filter: 'drop-shadow(0 0 20px rgba(0, 212, 255, 0.3))',
  },
  title: {
    fontSize: 'clamp(2.5rem, 5vw, 3.5rem)',
    fontWeight: '700',
    margin: '0 0 1rem',
    background: 'linear-gradient(135deg, #ffffff 0%, #00d4ff 50%, #7c3aed 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
    letterSpacing: '-0.02em',
  },
  subtitle: {
    fontSize: 'clamp(1rem, 2vw, 1.25rem)',
    color: 'rgba(255, 255, 255, 0.7)',
    margin: '0 0 2.5rem',
    lineHeight: 1.6,
    fontWeight: '400',
  },
  features: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '0.75rem',
    justifyContent: 'center',
    marginBottom: '2.5rem',
  },
  feature: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    padding: '0.625rem 1rem',
    background: 'rgba(0, 212, 255, 0.1)',
    border: '1px solid rgba(0, 212, 255, 0.2)',
    borderRadius: '50px',
    fontSize: '0.875rem',
    color: 'rgba(255, 255, 255, 0.9)',
    transition: 'all 0.3s ease',
  },
  featureIcon: {
    fontSize: '1rem',
  },
  ctaButton: {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '1rem 2.5rem',
    background: 'linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%)',
    color: '#050510',
    fontSize: '1.125rem',
    fontWeight: '600',
    borderRadius: '50px',
    textDecoration: 'none',
    border: 'none',
    cursor: 'pointer',
    boxShadow: `
      0 4px 20px rgba(0, 212, 255, 0.3),
      0 0 0 1px rgba(255, 255, 255, 0.1) inset
    `,
    transition: 'all 0.3s ease',
  },
  footer: {
    marginTop: '2rem',
    fontSize: '0.875rem',
    color: 'rgba(255, 255, 255, 0.4)',
    letterSpacing: '0.05em',
    textTransform: 'uppercase',
  },
  rightSection: {
    flex: '1',
    position: 'relative',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    minWidth: 0,
    padding: '2rem',
    overflow: 'hidden',
  },
  accentPattern: {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    backgroundImage: `
      radial-gradient(ellipse at 20% 20%, rgba(0, 212, 255, 0.08) 0%, transparent 50%),
      radial-gradient(ellipse at 80% 80%, rgba(124, 58, 237, 0.08) 0%, transparent 50%),
      linear-gradient(180deg, transparent 0%, rgba(0, 212, 255, 0.02) 50%, transparent 100%)
    `,
    pointerEvents: 'none',
  },
  stats: {
    position: 'relative',
    zIndex: 5,
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '1.5rem',
    width: '100%',
    maxWidth: '400px',
  },
  stat: {
    textAlign: 'center',
    padding: '1.5rem',
    background: 'rgba(15, 15, 35, 0.5)',
    backdropFilter: 'blur(10px)',
    border: '1px solid rgba(255, 255, 255, 0.05)',
    borderRadius: '16px',
    transition: 'all 0.3s ease',
  },
  statNumber: {
    display: 'block',
    fontSize: '2.5rem',
    fontWeight: '700',
    background: 'linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
    lineHeight: 1.2,
    marginBottom: '0.5rem',
  },
  statLabel: {
    fontSize: '0.875rem',
    color: 'rgba(255, 255, 255, 0.6)',
    textTransform: 'uppercase',
    letterSpacing: '0.1em',
  },
};

// Add dynamic styles for hover effects
if (typeof window !== 'undefined') {
  const styleSheet = document.createElement('style');
  styleSheet.textContent = `
    .feature:hover {
      background: rgba(0, 212, 255, 0.2) !important;
      border-color: rgba(0, 212, 255, 0.4) !important;
      transform: translateY(-2px);
    }
    .ctaButton:hover {
      transform: translateY(-2px) !important;
      box-shadow: 0 8px 30px rgba(0, 212, 255, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.2) inset !important;
    }
    .stat:hover {
      border-color: rgba(0, 212, 255, 0.2) !important;
      transform: translateY(-4px);
    }
    @media (max-width: 1024px) {
      .rightSection { display: none; }
      .leftSection { flex: 1; }
    }
    @media (max-width: 640px) {
      .glassCard { padding: 2rem 1.5rem; }
      .stats { grid-template-columns: 1fr 1fr; }
    }
  `;
  document.head.appendChild(styleSheet);
}