<template>
  <div class="about">
    <Header />
    <main class="main-content">
      <!-- 3D Scene Section -->
      <section class="scene-section">
        <div class="scene-wrapper">
          <!-- Sci-fi border decorations -->
          <div class="corner corner-tl"></div>
          <div class="corner corner-tr"></div>
          <div class="corner corner-bl"></div>
          <div class="corner corner-br"></div>
          <div class="edge edge-top"></div>
          <div class="edge edge-bottom"></div>
          <div class="edge edge-left"></div>
          <div class="edge edge-right"></div>

          <div class="scene-container" ref="sceneContainer"></div>

          <!-- Monitoring Panel -->
          <div class="monitoring-panel" :class="{ collapsed: isPanelCollapsed }">
            <div class="panel-header" @click="togglePanel">
              <span class="status-dot"></span>
              <span>Flight Test Monitor</span>
              <span class="toggle-icon">{{ isPanelCollapsed ? '+' : '−' }}</span>
            </div>
            <div class="panel-body" v-show="!isPanelCollapsed">
              <div class="metric">
                <span class="label">Altitude</span>
                <span class="value">{{ metrics.altitude.toLocaleString() }} ft</span>
              </div>
              <div class="metric">
                <span class="label">Speed</span>
                <span class="value">{{ metrics.speed }} knots</span>
              </div>
              <div class="metric">
                <span class="label">Heading</span>
                <span class="value">{{ metrics.heading }}°</span>
              </div>
              <div class="metric">
                <span class="label">Fuel Flow</span>
                <span class="value">{{ metrics.fuelFlow }} kg/h</span>
              </div>
              <div class="metric">
                <span class="label">Engine Temp</span>
                <span class="value">{{ metrics.engineTemp }}°C</span>
              </div>
              <div class="metric">
                <span class="label">Data Packets</span>
                <span class="value">{{ metrics.dataPackets.toLocaleString() }}/s</span>
              </div>
            </div>
            <div class="panel-footer" v-show="!isPanelCollapsed">
              <div class="data-stream">
                <span v-for="(char, i) in dataStream" :key="i" class="stream-char">{{ char }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Profile Section -->
      <section class="profile-section">
        <div class="profile-container">
          <div class="profile-header">
            <div class="avatar-wrapper">
              <img :src="avatarUrl" alt="Avatar" class="avatar-img" />
              <div class="avatar-ring"></div>
            </div>
            <div class="profile-title">
              <h1>Yang</h1>
              <p class="tagline">工程师</p>
            </div>
          </div>

          <div class="profile-content">
            <p>
              我是 Yang，这是我的个人博客。
            </p>
            <p>
              在 2017~2026 年，我在清华大学航天航空学院学习和工作，得到了工学学士和博士学位。在博士期间，我主要关注氮化镓高电子迁移率晶体管的跨尺度传热过程，并开发了一套以声子蒙特卡罗模拟为核心的仿真软件，用于研究从纳米到宏观尺度的热传导现象。
            </p>
            <p>
              目前，我是一名试飞测试工程师，负责飞机的试飞测试和数据分析工作。我喜欢工程师这份职业，我希望能通过新的技术，促进工业领域的发展和进步，让更多的人享受到科技进步的成果。
            </p>
            <p>
              我喜欢陀思妥耶夫斯基、核文化、极真空手道，我在新极真会练习空手道大约十年。
            </p>
          </div>
        </div>
      </section>
    </main>
    <Footer />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'

const sceneContainer = ref(null)
const dataStream = ref('0101001101011001010011')
const isPanelCollapsed = ref(false)

const togglePanel = () => {
  isPanelCollapsed.value = !isPanelCollapsed.value
}

// Avatar image path - change this to your own avatar in public folder
// e.g., '/avatar.png' or '/images/avatar.jpg'
const avatarUrl = ref('/pictures/Salmonberry.png')

// Metrics for monitoring panel
const metrics = reactive({
  altitude: 35000,
  speed: 485,
  heading: 275,
  fuelFlow: 2450,
  engineTemp: 892,
  dataPackets: 12847
})

let scene, camera, renderer, controls
let airplane = null
let particles = null
let animationId = null
let metricsInterval = null

// Update metrics periodically
const updateMetrics = () => {
  metrics.altitude = 35000 + Math.floor(Math.random() * 200 - 100)
  metrics.speed = 485 + Math.floor(Math.random() * 10 - 5)
  metrics.heading = (metrics.heading + Math.random() * 2 - 1 + 360) % 360
  metrics.heading = Math.round(metrics.heading)
  metrics.fuelFlow = 2450 + Math.floor(Math.random() * 50 - 25)
  metrics.engineTemp = 892 + Math.floor(Math.random() * 10 - 5)
  metrics.dataPackets = 12000 + Math.floor(Math.random() * 2000)

  // Update data stream
  const chars = '01'
  let stream = ''
  for (let i = 0; i < 22; i++) {
    stream += chars[Math.floor(Math.random() * 2)]
  }
  dataStream.value = stream
}

// Create particle system for data flow - blue streamlines
const createParticles = () => {
  const particleCount = 600
  const geometry = new THREE.BufferGeometry()
  const positions = new Float32Array(particleCount * 3)
  const velocities = new Float32Array(particleCount * 3)
  const colors = new Float32Array(particleCount * 3)

  for (let i = 0; i < particleCount; i++) {
    const i3 = i * 3
    // Position particles around the wings
    const side = Math.random() > 0.5 ? 1 : -1
    positions[i3] = (Math.random() - 0.5) * 10 // x - along fuselage
    positions[i3 + 1] = (Math.random() - 0.5) * 2.5 // y - height
    positions[i3 + 2] = side * (2 + Math.random() * 5) // z - wing sides

    // Velocity - flowing backward
    velocities[i3] = -0.025 - Math.random() * 0.035
    velocities[i3 + 1] = (Math.random() - 0.5) * 0.008
    velocities[i3 + 2] = 0

    // Color - blue gradient (#3b82f6 primary blue)
    const intensity = 0.6 + Math.random() * 0.4
    colors[i3] = 0.23 * intensity     // R
    colors[i3 + 1] = 0.51 * intensity // G
    colors[i3 + 2] = 0.96 * intensity // B
  }

  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))
  geometry.userData.velocities = velocities

  const material = new THREE.PointsMaterial({
    size: 0.1,
    vertexColors: true,
    transparent: true,
    opacity: 0.85,
    sizeAttenuation: true
  })

  particles = new THREE.Points(geometry, material)
  scene.add(particles)
}

// Update particle positions
const updateParticles = () => {
  if (!particles) return

  const positions = particles.geometry.attributes.position.array
  const velocities = particles.geometry.userData.velocities

  for (let i = 0; i < positions.length; i += 3) {
    positions[i] += velocities[i]
    positions[i + 1] += velocities[i + 1]
    positions[i + 2] += velocities[i + 2]

    // Reset particle if it goes too far back
    if (positions[i] < -7) {
      const side = Math.random() > 0.5 ? 1 : -1
      positions[i] = 5 + Math.random() * 2
      positions[i + 1] = (Math.random() - 0.5) * 2.5
      positions[i + 2] = side * (2 + Math.random() * 5)
    }
  }

  particles.geometry.attributes.position.needsUpdate = true
}

// Initialize Three.js scene
const initScene = () => {
  // Scene - light background
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0xf0f4f8)

  // Add gradient fog for depth
  scene.fog = new THREE.Fog(0xf0f4f8, 20, 50)

  // Camera
  camera = new THREE.PerspectiveCamera(
    45,
    sceneContainer.value.clientWidth / sceneContainer.value.clientHeight,
    0.1,
    1000
  )
  camera.position.set(10, 5, 14)

  // Renderer
  renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setSize(sceneContainer.value.clientWidth, sceneContainer.value.clientHeight)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.toneMapping = THREE.ACESFilmicToneMapping
  renderer.toneMappingExposure = 1.0
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFSoftShadowMap
  sceneContainer.value.appendChild(renderer.domElement)

  // Controls
  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.05
  controls.minDistance = 6
  controls.maxDistance = 25
  controls.autoRotate = true
  controls.autoRotateSpeed = 0.4
  controls.maxPolarAngle = Math.PI / 2 + 0.3

  // Lights - brighter for light theme
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.7)
  scene.add(ambientLight)

  const directionalLight = new THREE.DirectionalLight(0xffffff, 1.2)
  directionalLight.position.set(10, 15, 10)
  directionalLight.castShadow = true
  directionalLight.shadow.mapSize.width = 2048
  directionalLight.shadow.mapSize.height = 2048
  scene.add(directionalLight)

  // Blue accent light
  const blueLight = new THREE.PointLight(0x3b82f6, 0.8, 30)
  blueLight.position.set(-8, 5, 8)
  scene.add(blueLight)

  // Soft fill light
  const fillLight = new THREE.PointLight(0xffffff, 0.4, 40)
  fillLight.position.set(5, -3, -5)
  scene.add(fillLight)

  // Add subtle grid - light blue tint
  const gridHelper = new THREE.GridHelper(50, 50, 0xc7d2e0, 0xe2e8f0)
  gridHelper.position.y = -3.5
  scene.add(gridHelper)

  // Load airplane model
  const loader = new GLTFLoader()
  loader.load(
    '/models/Boeing_787.glb',
    (gltf) => {
      airplane = gltf.scene
      airplane.scale.set(2, 2, 2)
      airplane.position.set(0, 0, 0)
      airplane.rotation.y = Math.PI / 2

      // Enable shadows
      airplane.traverse((child) => {
        if (child.isMesh) {
          child.castShadow = true
          child.receiveShadow = true
        }
      })

      scene.add(airplane)

      // Create particles after airplane loads
      createParticles()
    },
    (progress) => {
      console.log('Loading:', (progress.loaded / progress.total * 100).toFixed(0) + '%')
    },
    (error) => {
      console.error('Error loading model:', error)
    }
  )

  // Handle resize
  window.addEventListener('resize', onWindowResize)
}

const onWindowResize = () => {
  if (!sceneContainer.value) return
  camera.aspect = sceneContainer.value.clientWidth / sceneContainer.value.clientHeight
  camera.updateProjectionMatrix()
  renderer.setSize(sceneContainer.value.clientWidth, sceneContainer.value.clientHeight)
}

// Animation loop
const animate = () => {
  animationId = requestAnimationFrame(animate)

  // Subtle floating animation for airplane
  if (airplane) {
    airplane.position.y = Math.sin(Date.now() * 0.001) * 0.15
  }

  updateParticles()
  controls.update()
  renderer.render(scene, camera)
}

onMounted(() => {
  initScene()
  animate()
  metricsInterval = setInterval(updateMetrics, 500)
})

onBeforeUnmount(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
  if (metricsInterval) {
    clearInterval(metricsInterval)
  }
  window.removeEventListener('resize', onWindowResize)

  if (renderer) {
    renderer.dispose()
    sceneContainer.value?.removeChild(renderer.domElement)
  }
})
</script>

<style scoped>
.about {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: var(--color-bg);
}

.main-content {
  flex: 1;
  padding: 40px 20px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

/* Scene Section */
.scene-section {
  margin-bottom: 40px;
}

.scene-wrapper {
  position: relative;
  background: var(--color-bg-secondary);
  border-radius: 8px;
  padding: 4px;
  box-shadow: 0 4px 20px rgba(59, 130, 246, 0.1);
}

/* Sci-fi Corners */
.corner {
  position: absolute;
  width: 24px;
  height: 24px;
  z-index: 10;
}

.corner::before,
.corner::after {
  content: '';
  position: absolute;
  background: var(--color-primary);
  box-shadow: 0 0 8px var(--color-primary), 0 0 16px rgba(59, 130, 246, 0.4);
}

.corner-tl {
  top: 0;
  left: 0;
}
.corner-tl::before {
  width: 24px;
  height: 3px;
  top: 0;
  left: 0;
  border-radius: 2px 0 0 0;
}
.corner-tl::after {
  width: 3px;
  height: 24px;
  top: 0;
  left: 0;
  border-radius: 2px 0 0 0;
}

.corner-tr {
  top: 0;
  right: 0;
}
.corner-tr::before {
  width: 24px;
  height: 3px;
  top: 0;
  right: 0;
  border-radius: 0 2px 0 0;
}
.corner-tr::after {
  width: 3px;
  height: 24px;
  top: 0;
  right: 0;
  border-radius: 0 2px 0 0;
}

.corner-bl {
  bottom: 0;
  left: 0;
}
.corner-bl::before {
  width: 24px;
  height: 3px;
  bottom: 0;
  left: 0;
  border-radius: 0 0 0 2px;
}
.corner-bl::after {
  width: 3px;
  height: 24px;
  bottom: 0;
  left: 0;
  border-radius: 0 0 0 2px;
}

.corner-br {
  bottom: 0;
  right: 0;
}
.corner-br::before {
  width: 24px;
  height: 3px;
  bottom: 0;
  right: 0;
  border-radius: 0 0 2px 0;
}
.corner-br::after {
  width: 3px;
  height: 24px;
  bottom: 0;
  right: 0;
  border-radius: 0 0 2px 0;
}

/* Sci-fi Edges */
.edge {
  position: absolute;
  background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.3), transparent);
  z-index: 5;
}

.edge-top,
.edge-bottom {
  height: 1px;
  left: 35px;
  right: 35px;
}

.edge-top {
  top: 0;
}

.edge-bottom {
  bottom: 0;
}

.edge-left,
.edge-right {
  width: 1px;
  top: 35px;
  bottom: 35px;
  background: linear-gradient(180deg, transparent, rgba(59, 130, 246, 0.3), transparent);
}

.edge-left {
  left: 0;
}

.edge-right {
  right: 0;
}

.scene-container {
  width: 100%;
  height: 450px;
  border-radius: 6px;
  overflow: hidden;
}

/* Monitoring Panel */
.monitoring-panel {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 250px;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  backdrop-filter: blur(10px);
  overflow: hidden;
  font-family: 'Consolas', 'Monaco', monospace;
  z-index: 20;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border);
  color: var(--color-primary);
  font-weight: 600;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 1px;
  cursor: pointer;
  user-select: none;
  transition: background 0.2s ease;
}

.panel-header:hover {
  background: var(--color-border);
}

.toggle-icon {
  margin-left: auto;
  font-size: 14px;
  font-weight: 400;
  opacity: 0.6;
  transition: opacity 0.2s ease;
}

.panel-header:hover .toggle-icon {
  opacity: 1;
}

.monitoring-panel.collapsed {
  width: auto;
  min-width: 180px;
}

.monitoring-panel.collapsed .panel-header {
  border-bottom: none;
}

.status-dot {
  width: 6px;
  height: 6px;
  background: var(--color-success);
  border-radius: 50%;
  box-shadow: 0 0 6px var(--color-success);
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; box-shadow: 0 0 6px var(--color-success); }
  50% { opacity: 0.5; box-shadow: 0 0 2px var(--color-success); }
}

.panel-body {
  padding: 10px 14px;
}

.metric {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
  border-bottom: 1px solid var(--color-border);
}

.metric:last-child {
  border-bottom: none;
}

.metric .label {
  color: var(--color-text-secondary);
  font-size: 10px;
}

.metric .value {
  color: var(--color-success);
  font-size: 10px;
  font-weight: 600;
}

.panel-footer {
  padding: 8px 14px;
  background: var(--color-bg-secondary);
  border-top: 1px solid var(--color-border);
}

.data-stream {
  font-size: 9px;
  letter-spacing: 1px;
  color: var(--color-primary);
  overflow: hidden;
  white-space: nowrap;
  opacity: 0.7;
}

.stream-char {
  display: inline-block;
  animation: flicker 0.1s ease-in-out infinite;
}

@keyframes flicker {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* Profile Section */
.profile-section {
  padding: 0;
}

.profile-container {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 32px;
}

.avatar-wrapper {
  position: relative;
  width: 100px;
  height: 100px;
  flex-shrink: 0;
}

.avatar-img {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  position: relative;
  z-index: 2;
  border: 3px solid var(--color-bg);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.avatar-ring {
  position: absolute;
  top: -4px;
  left: -4px;
  right: -4px;
  bottom: -4px;
  border: 2px solid var(--color-primary);
  border-radius: 50%;
  opacity: 0.4;
  animation: ring-pulse 2s ease-in-out infinite;
}

@keyframes ring-pulse {
  0%, 100% { transform: scale(1); opacity: 0.3; }
  50% { transform: scale(1.05); opacity: 0.6; }
}

.profile-title h1 {
  margin: 0 0 8px 0;
  font-size: 2rem;
  font-weight: 600;
  color: var(--color-text);
  letter-spacing: 0.5px;
}

.tagline {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 1rem;
}

.profile-content {
  color: var(--color-text);
  font-size: 1rem;
  line-height: 1.9;
}

.profile-content p {
  margin: 0 0 1.2em 0;
}

.profile-content p:last-child {
  margin-bottom: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .main-content {
    padding: 20px 15px;
  }

  .scene-container {
    height: 320px;
  }

  .monitoring-panel {
    width: 160px;
    top: 10px;
    right: 10px;
  }

  .monitoring-panel.collapsed {
    min-width: 140px;
  }

  .toggle-icon {
    font-size: 12px;
  }

  .panel-header {
    padding: 8px 10px;
    font-size: 9px;
  }

  .metric .label,
  .metric .value {
    font-size: 9px;
  }

  .profile-container {
    padding: 24px;
  }

  .profile-header {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }

  .avatar-wrapper {
    width: 90px;
    height: 90px;
  }

  .avatar-img {
    width: 90px;
    height: 90px;
  }

  .profile-title h1 {
    font-size: 1.5rem;
  }
}
</style>
