// ---------------------------------------------------------
// VARIABLES & SETTINGS
// ---------------------------------------------------------

let lastPredictionTime = 0;
let isThermalMode = false;
let originalMaterials = {}; 

// Dashboard Variables
let dashboardMesh = null;
let dashboardCanvas = null;
let dashboardCtx = null;
let dashboardTexture = null;

// X-Ray Variables
let isXRayMode = false;

// Fault Localization Variables
let faultRing = null;
let showFaultMarkers = true;

// Demo Mode Flag
let isDemoMode = false;

// Data history for graphs
const historyLength = 50;
const tempHistory = [];
const pressHistory = [];
const vibHistory = [];

for(let i=0; i<historyLength; i++) {
    tempHistory.push(0);
    pressHistory.push(0);
    vibHistory.push(0);
}

// ---------------------------------------------------------
// SCENE SETUP
// ---------------------------------------------------------
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 1.5, 6);

const renderer = new THREE.WebGLRenderer({
    canvas: document.querySelector("#scene"),
    antialias: true, 
    powerPreference: "high-performance"
});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.2; 
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputEncoding = THREE.sRGBEncoding; 

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05; 
controls.maxPolarAngle = Math.PI / 2; 
controls.minDistance = 2; 
controls.maxDistance = 20; 

// ---------------------------------------------------------
// POST PROCESSING
// ---------------------------------------------------------
let composer = null;

function setupPostProcessing() {
    if (typeof THREE.EffectComposer !== 'undefined') {
        composer = new THREE.EffectComposer(renderer);
        const renderPass = new THREE.RenderPass(scene, camera);
        composer.addPass(renderPass);
        const bloomPass = new THREE.UnrealBloomPass(new THREE.Vector2(window.innerWidth, window.innerHeight), 0.5, 0.3, 0.9);
        composer.addPass(bloomPass);
        if (typeof THREE.FXAAShader !== 'undefined') {
            const fxaaPass = new THREE.ShaderPass(THREE.FXAAShader);
            const pixelRatio = renderer.getPixelRatio();
            fxaaPass.uniforms['resolution'].value.set(1.0 / (window.innerWidth * pixelRatio), 1.0 / (window.innerHeight * pixelRatio));
            composer.addPass(fxaaPass);
        }
    }
}

// ---------------------------------------------------------
// ENVIRONMENT (HDRI)
// ---------------------------------------------------------
let skySphere = null;
function createSkySphere(texture) {
    const geometry = new THREE.SphereGeometry(500, 60, 40);
    geometry.scale(-1, 1, 1); 
    const material = new THREE.MeshBasicMaterial({ map: texture });
    skySphere = new THREE.Mesh(geometry, material);
    scene.add(skySphere);
}
const rgbeLoader = new THREE.RGBELoader();
rgbeLoader.load("hdri/env.hdr", function(texture) {
    texture.mapping = THREE.EquirectangularReflectionMapping;
    scene.environment = texture;
    createSkySphere(texture);
}, undefined, function(err) { console.error("HDRI Error", err); });

// ---------------------------------------------------------
// GROUND & SHADOWS
// ---------------------------------------------------------
const groundGeo = new THREE.PlaneGeometry(200, 200);
const groundMat = new THREE.ShadowMaterial({ opacity: 0.3 });
const ground = new THREE.Mesh(groundGeo, groundMat);
ground.rotation.x = -Math.PI / 2;
ground.position.y = 0;
ground.receiveShadow = true;
scene.add(ground);

const contactShadowGeo = new THREE.PlaneGeometry(10, 10);
const canvas = document.createElement('canvas');
canvas.width = 512; canvas.height = 512;
const ctx = canvas.getContext('2d');
const gradient = ctx.createRadialGradient(256, 256, 0, 256, 256, 256);
gradient.addColorStop(0, 'rgba(0,0,0,0.6)');
gradient.addColorStop(1, 'rgba(0,0,0,0)');
ctx.fillStyle = gradient;
ctx.fillRect(0, 0, 512, 512);
const shadowTexture = new THREE.CanvasTexture(canvas);
const contactShadowMat = new THREE.MeshBasicMaterial({ map: shadowTexture, transparent: true, depthWrite: false });
const contactShadow = new THREE.Mesh(contactShadowGeo, contactShadowMat);
contactShadow.rotation.x = -Math.PI / 2;
contactShadow.position.y = 0.01;
scene.add(contactShadow);

// ---------------------------------------------------------
// LIGHTING
// ---------------------------------------------------------
const keyLight = new THREE.SpotLight(0xffffff, 2.5); 
keyLight.position.set(10, 20, 10);
keyLight.castShadow = true;
keyLight.shadow.mapSize.width = 2048; 
keyLight.shadow.mapSize.height = 2048;
scene.add(keyLight);

const fillLight = new THREE.DirectionalLight(0xffffff, 1.5);
fillLight.position.set(-10, 5, 5);
scene.add(fillLight);
const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambientLight);
const hemiLight = new THREE.HemisphereLight(0xffffbb, 0x080820, 0.5);
scene.add(hemiLight);

// ---------------------------------------------------------
// SMOKE SYSTEM
// ---------------------------------------------------------
let smokeParticles = null;
let turbinePosition = new THREE.Vector3(); 
let exhaustDirection = new THREE.Vector3(0, 0, -1); 
const smokeCount = 100; 

function createSmokeSystem() {
    const canvas = document.createElement('canvas');
    canvas.width = 64; canvas.height = 64;
    const ctx = canvas.getContext('2d');
    const gradient = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
    gradient.addColorStop(0, 'rgba(20, 20, 20, 1.0)');
    gradient.addColorStop(0.5, 'rgba(10, 10, 10, 0.5)');
    gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 64, 64);
    
    const smokeTexture = new THREE.CanvasTexture(canvas);
    const smokeMaterial = new THREE.PointsMaterial({ size: 5.0, map: smokeTexture, transparent: true, opacity: 0.5, depthWrite: false, blending: THREE.NormalBlending });
    const smokeGeometry = new THREE.BufferGeometry();
    const positions = new Float32Array(smokeCount * 3);
    const velocities = [];
    for (let i = 0; i < smokeCount; i++) {
        positions[i * 3] = turbinePosition.x + (Math.random() - 0.5) * 0.2;
        positions[i * 3 + 1] = turbinePosition.y + (Math.random() - 0.5) * 0.2;
        positions[i * 3 + 2] = turbinePosition.z + (Math.random() - 0.5) * 0.2;
        velocities.push({ vx: 0, vy: 0, vz: 0 });
    }
    smokeGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    smokeGeometry.userData.velocities = velocities;
    smokeParticles = new THREE.Points(smokeGeometry, smokeMaterial);
    smokeParticles.frustumCulled = false;
    smokeParticles.visible = false;
    scene.add(smokeParticles);
}

function updateSmoke() {
    if (!smokeParticles || !smokeParticles.visible) return;
    const positions = smokeParticles.geometry.attributes.position.array;
    const velocities = smokeParticles.geometry.userData.velocities;
    for (let i = 0; i < smokeCount; i++) {
        positions[i * 3] += velocities[i].vx;
        positions[i * 3 + 1] += velocities[i].vy;
        positions[i * 3 + 2] += velocities[i].vz;
        const dist = Math.sqrt(Math.pow(positions[i * 3] - turbinePosition.x, 2) + Math.pow(positions[i * 3 + 1] - turbinePosition.y, 2) + Math.pow(positions[i * 3 + 2] - turbinePosition.z, 2));
        if (dist > 12.0) {
            positions[i * 3] = turbinePosition.x + (Math.random() - 0.5) * 0.2;
            positions[i * 3 + 1] = turbinePosition.y + (Math.random() - 0.5) * 0.2;
            positions[i * 3 + 2] = turbinePosition.z + (Math.random() - 0.5) * 0.2;
            const speed = 0.15 + Math.random() * 0.05; const spread = 0.04;
            velocities[i].vx = exhaustDirection.x * speed + (Math.random() - 0.5) * spread;
            velocities[i].vy = exhaustDirection.y * speed + (Math.random() - 0.5) * spread;
            velocities[i].vz = exhaustDirection.z * speed + (Math.random() - 0.5) * spread;
        }
    }
    smokeParticles.geometry.attributes.position.needsUpdate = true;
}

// ---------------------------------------------------------
// FIRE EXHAUST SYSTEM
// ---------------------------------------------------------
let fireParticles = null;
const fireCount = 300;

function createFireSystem() {
    const canvas = document.createElement('canvas');
    canvas.width = 64; canvas.height = 64;
    const ctx = canvas.getContext('2d');
    const gradient = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
    gradient.addColorStop(0, 'rgba(255, 255, 255, 1.0)');
    gradient.addColorStop(0.2, 'rgba(255, 200, 50, 0.8)');
    gradient.addColorStop(0.6, 'rgba(255, 50, 0, 0.5)');
    gradient.addColorStop(1, 'rgba(100, 0, 0, 0)');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 64, 64);
    
    const fireTexture = new THREE.CanvasTexture(canvas);
    const fireMaterial = new THREE.PointsMaterial({ size: 2.0, map: fireTexture, transparent: true, opacity: 1.0, depthWrite: false, blending: THREE.AdditiveBlending });
    const fireGeometry = new THREE.BufferGeometry();
    const positions = new Float32Array(fireCount * 3);
    const velocities = [];
    const colors = new Float32Array(fireCount * 3);
    for (let i = 0; i < fireCount; i++) {
        positions[i * 3] = 0; positions[i * 3 + 1] = 0; positions[i * 3 + 2] = 0;
        velocities.push({ vx: 0, vy: 0, vz: 0, life: 0 });
        colors[i * 3] = 1.0; colors[i * 3 + 1] = 0.2; colors[i * 3 + 2] = 0.0;
    }
    fireGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    fireGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    fireGeometry.userData.velocities = velocities;
    fireParticles = new THREE.Points(fireGeometry, fireMaterial);
    fireParticles.frustumCulled = false;
    fireParticles.visible = false;
    scene.add(fireParticles);
}

function updateFire() {
    if (!fireParticles || !fireParticles.visible) return;
    const positions = fireParticles.geometry.attributes.position.array;
    const colors = fireParticles.geometry.attributes.color.array;
    const velocities = fireParticles.geometry.userData.velocities;
    for (let i = 0; i < fireCount; i++) {
        positions[i * 3] += velocities[i].vx;
        positions[i * 3 + 1] += velocities[i].vy;
        positions[i * 3 + 2] += velocities[i].vz;
        velocities[i].life -= 0.04;
        if (velocities[i].life <= 0) {
            positions[i * 3] = turbinePosition.x + (Math.random() - 0.5) * 0.3;
            positions[i * 3 + 1] = turbinePosition.y + (Math.random() - 0.5) * 0.3;
            positions[i * 3 + 2] = turbinePosition.z + (Math.random() - 0.5) * 0.3;
            const speed = 0.4 + Math.random() * 0.2; const spread = 0.1;
            velocities[i].vx = exhaustDirection.x * speed + (Math.random() - 0.5) * spread;
            velocities[i].vy = exhaustDirection.y * speed + (Math.random() - 0.5) * spread;
            velocities[i].vz = exhaustDirection.z * speed + (Math.random() - 0.5) * spread;
            velocities[i].life = 1.0;
            colors[i * 3] = 1.0; colors[i * 3 + 1] = 0.8; colors[i * 3 + 2] = 0.2;
        } else {
            colors[i * 3] = 1.0; colors[i * 3 + 1] *= 0.96; colors[i * 3 + 2] *= 0.9;
        }
    }
    fireParticles.geometry.attributes.position.needsUpdate = true;
    fireParticles.geometry.attributes.color.needsUpdate = true;
}

// ---------------------------------------------------------
// SPARKS SYSTEM
// ---------------------------------------------------------
let sparkParticles = null;
const sparkCount = 450; 
let sparkTempVec = new THREE.Vector3();
let turbineMesh = null, detailsMesh = null, fanMesh = null;
let turbineGeometryAttr = null, detailsGeometryAttr = null, fanGeometryAttr = null;

function createSparkSystem() {
    const canvas = document.createElement('canvas');
    canvas.width = 32; canvas.height = 32;
    const ctx = canvas.getContext('2d');
    const gradient = ctx.createRadialGradient(16, 16, 0, 16, 16, 16);
    gradient.addColorStop(0, 'rgba(255, 255, 255, 1.0)');
    gradient.addColorStop(0.3, 'rgba(255, 255, 100, 0.8)');
    gradient.addColorStop(1, 'rgba(255, 100, 0, 0)');
    ctx.fillStyle = gradient; ctx.fillRect(0, 0, 32, 32);
    
    const sparkTexture = new THREE.CanvasTexture(canvas);
    const sparkMaterial = new THREE.PointsMaterial({ size: 0.15, map: sparkTexture, transparent: true, opacity: 1.0, depthWrite: false, blending: THREE.AdditiveBlending });
    const sparkGeometry = new THREE.BufferGeometry();
    const positions = new Float32Array(sparkCount * 3);
    const velocities = [];
    for (let i = 0; i < sparkCount; i++) { positions[i * 3] = 0; positions[i * 3 + 1] = 0; positions[i * 3 + 2] = 0; velocities.push({ vx: 0, vy: 0, vz: 0, life: 0 }); }
    sparkGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    sparkGeometry.userData.velocities = velocities;
    sparkParticles = new THREE.Points(sparkGeometry, sparkMaterial);
    sparkParticles.frustumCulled = false; sparkParticles.visible = false;
    scene.add(sparkParticles);
}

function updateSparks() {
    if (!sparkParticles || !sparkParticles.visible) return;
    const positions = sparkParticles.geometry.attributes.position.array;
    const velocities = sparkParticles.geometry.userData.velocities;
    for (let i = 0; i < sparkCount; i++) {
        velocities[i].vy -= 0.01; 
        positions[i * 3] += velocities[i].vx; positions[i * 3 + 1] += velocities[i].vy; positions[i * 3 + 2] += velocities[i].vz;
        velocities[i].life -= 0.02;
        if (velocities[i].life <= 0) {
            let spawnPos = turbinePosition;
            const sourceChoice = Math.random();
            if (sourceChoice < 0.33 && turbineGeometryAttr) {
                const idx = Math.floor(Math.random() * turbineGeometryAttr.count);
                sparkTempVec.fromBufferAttribute(turbineGeometryAttr, idx);
                if (turbineMesh) turbineMesh.localToWorld(sparkTempVec); spawnPos = sparkTempVec;
                const splitSpeed = 0.1 + Math.random() * 0.1;
                velocities[i].vx = exhaustDirection.x * splitSpeed + (Math.random() - 0.5) * 0.05;
                velocities[i].vy = exhaustDirection.y * splitSpeed + (Math.random() - 0.5) * 0.05;
                velocities[i].vz = exhaustDirection.z * splitSpeed + (Math.random() - 0.5) * 0.05;
            } else if (sourceChoice < 0.66 && detailsGeometryAttr) {
                const idx = Math.floor(Math.random() * detailsGeometryAttr.count);
                sparkTempVec.fromBufferAttribute(detailsGeometryAttr, idx);
                if (detailsMesh) detailsMesh.localToWorld(sparkTempVec); spawnPos = sparkTempVec;
                velocities[i].vx = (Math.random() - 0.5) * 0.02; velocities[i].vy = -0.02; velocities[i].vz = (Math.random() - 0.5) * 0.02;
            } else if (fanGeometryAttr) {
                const idx = Math.floor(Math.random() * fanGeometryAttr.count);
                sparkTempVec.fromBufferAttribute(fanGeometryAttr, idx);
                if (fanMesh) fanMesh.localToWorld(sparkTempVec); spawnPos = sparkTempVec;
                const splitSpeed = 0.1 + Math.random() * 0.1;
                velocities[i].vx = -exhaustDirection.x * splitSpeed + (Math.random() - 0.5) * 0.05;
                velocities[i].vy = -exhaustDirection.y * splitSpeed + (Math.random() - 0.5) * 0.05;
                velocities[i].vz = -exhaustDirection.z * splitSpeed + (Math.random() - 0.5) * 0.05;
            } else if (turbineGeometryAttr) {
                 const idx = Math.floor(Math.random() * turbineGeometryAttr.count);
                 sparkTempVec.fromBufferAttribute(turbineGeometryAttr, idx);
                 if (turbineMesh) turbineMesh.localToWorld(sparkTempVec); spawnPos = sparkTempVec;
                 velocities[i].vx = (Math.random() - 0.5) * 0.05; velocities[i].vy = -0.02; velocities[i].vz = (Math.random() - 0.5) * 0.05;
            }
            positions[i * 3] = spawnPos.x + (Math.random() - 0.5) * 0.5;
            positions[i * 3 + 1] = spawnPos.y + (Math.random() - 0.5) * 0.5;
            positions[i * 3 + 2] = spawnPos.z + (Math.random() - 0.5) * 0.5;
            velocities[i].life = 1.0;
        }
    }
    sparkParticles.geometry.attributes.position.needsUpdate = true;
}

// ---------------------------------------------------------
// AUDIO MANAGEMENT
// ---------------------------------------------------------
const soundEngine = document.getElementById('soundEngine');
const soundWarning = document.getElementById('soundWarning');
const soundAlarm = document.getElementById('soundAlarm');
const btnSound = document.getElementById('btnSound');
let isMuted = true;
function toggleSound() { try { isMuted = !isMuted; if (isMuted) { btnSound.innerText = "Sound: OFF"; stopAllAudio(); } else { btnSound.innerText = "Sound: ON"; const stateText = document.getElementById("stateValue").innerText; playSoundForState(stateText); } } catch (e) { console.log("Sound error", e); } }
function stopAllAudio() { try { if(soundEngine) soundEngine.pause(); if(soundWarning) soundWarning.pause(); if(soundAlarm) soundAlarm.pause(); } catch (e) {} }
function playSoundForState(state) { if (isMuted) return; stopAllAudio(); try { if (state === "GOOD") { if(soundEngine) soundEngine.play(); } else if (state === "WARNING") { if(soundWarning) soundWarning.play(); } else if (state === "CRITICAL") { if(soundAlarm) soundAlarm.play(); } } catch (e) { console.log("Audio play failed", e); } }

// ---------------------------------------------------------
// VARIABLES
// ---------------------------------------------------------
let model, fan, compressor, turbine, body, details;
let allMeshes = [];
let fixedRandomParts = []; 
let rotationSpeed = { fan: 0.12, compressor: 0.18, turbine: 0.2 };
let vibration = 0;

// ---------------------------------------------------------
// LOAD MODEL
// ---------------------------------------------------------
const loader = new THREE.GLTFLoader();
loader.load("models/engine.glb", function(gltf) {
    model = gltf.scene; model.scale.set(3, 3, 3);
    const box = new THREE.Box3().setFromObject(model);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    model.position.x = -center.x; model.position.z = -center.z; model.position.y = -box.min.y; model.userData.baseY = model.position.y;
    scene.add(model);
    const focusTarget = new THREE.Vector3(0, size.y * 0.3, 0); controls.target.copy(focusTarget); camera.lookAt(focusTarget);
    const maxDim = Math.max(size.x, size.y, size.z);
    camera.position.set(0, size.y * 0.5, maxDim * 1.5);
    model.traverse(function(child) {
        if (child.isMesh) {
            if (child.material) { child.material = child.material.clone(); }
            child.castShadow = true; child.receiveShadow = true; child.material.envMapIntensity = 1.5;
            const maxAnisotropy = renderer.capabilities.getMaxAnisotropy();
            if (child.material.map) child.material.map.anisotropy = maxAnisotropy;
            allMeshes.push(child);
        }
    });
    model.traverse((obj) => {
        if (obj.name === "fan_rotor") fan = obj;
        if (obj.name === "compressor_rotor") compressor = obj;
        if (obj.name === "turbine_rotor") turbine = obj;
        if (obj.name === "engine_body") body = obj;
        if (obj.name === "engine_details") details = obj;
    });
    if (!fan) fan = model.children[0];
    if (fan && turbine) {
        const fanPos = new THREE.Vector3(); fan.getWorldPosition(fanPos);
        turbinePosition = new THREE.Vector3(); turbine.getWorldPosition(turbinePosition);
        exhaustDirection.subVectors(turbinePosition, fanPos); exhaustDirection.normalize();
    }
    function isInsideFan(mesh, fanObj) { if (!fanObj) return false; let parent = mesh.parent; while (parent) { if (parent === fanObj) return true; parent = parent.parent; } return false; }
    function getFixedSeed(str) { let hash = 0; for (let i = 0; i < str.length; i++) { hash = ((hash << 5) - hash) + str.charCodeAt(i); hash |= 0; } return Math.abs(hash); }
    const colorableParts = allMeshes.filter(mesh => { if (mesh === fan) return false; if (isInsideFan(mesh, fan)) return false; return true; });
    const shuffled = [...colorableParts].sort((a, b) => { return getFixedSeed(a.name) - getFixedSeed(b.name); });
    fixedRandomParts = shuffled.slice(0, Math.floor(colorableParts.length * 0.7));
    if (turbine) { turbine.traverse((child) => { if (child.isMesh && !turbineMesh) turbineMesh = child; }); if (!turbineMesh && turbine.isMesh) turbineMesh = turbine; if (turbineMesh && turbineMesh.geometry) turbineGeometryAttr = turbineMesh.geometry.attributes.position; }
    if (details) { details.traverse((child) => { if (child.isMesh && !detailsMesh) detailsMesh = child; }); if (!detailsMesh && details.isMesh) detailsMesh = details; if (detailsMesh && detailsMesh.geometry) detailsGeometryAttr = detailsMesh.geometry.attributes.position; }
    if (fan) { fan.traverse((child) => { if (child.isMesh && !fanMesh) fanMesh = child; }); if (!fanMesh && fan.isMesh) fanMesh = fan; if (fanMesh && fanMesh.geometry) fanGeometryAttr = fanMesh.geometry.attributes.position; }
    
    setupPostProcessing();
    createSmokeSystem(); createFireSystem(); createSparkSystem(); createDashboard(); createFaultIndicator(); 
    // Initial call
    getPrediction();
});

// ---------------------------------------------------------
// CONSOLE HELPER (VISUAL LOG)
// ---------------------------------------------------------
function toggleVisualConsole() {
    const consoleEl = document.getElementById("visual-console");
    if (consoleEl) {
        if (consoleEl.style.display === "none") {
            consoleEl.style.display = "block";
        } else {
            consoleEl.style.display = "none";
        }
    }
}

// Override console.log to show on screen
const originalLog = console.log;
console.log = function(...args) {
    originalLog.apply(console, args); // Keep showing in browser console
    
    const logContent = document.getElementById("log-content");
    if (logContent) {
        const msg = args.map(a => {
            try { return JSON.stringify(a); } catch (e) { return String(a); }
        }).join(' ');
        const div = document.createElement('div');
        div.innerText = "> " + msg;
        logContent.appendChild(div);
        logContent.scrollTop = logContent.scrollHeight; // Auto scroll
    }
};

// ---------------------------------------------------------
// API & LOGIC
// ---------------------------------------------------------
async function getPrediction() {
    if (isDemoMode) return;

    try {
        const dataRes = await fetch("http://127.0.0.1:8000/get_real_data");
        const sensorData = await dataRes.json();

        const res = await fetch("http://127.0.0.1:8000/predict", { 
            method: "POST", 
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(sensorData)
        });
        const prediction = await res.json();
        
        console.log("Row ID:", sensorData.id, "RUL:", prediction.Predicted_RUL);

        const rul = prediction.Predicted_RUL;
        document.getElementById("rulVal").innerText = rul.toFixed(2);
        
        const percent = Math.min(100, Math.max(0, rul));
        document.getElementById("rulFill").style.width = percent + "%";
        document.getElementById("rulPercent").innerText = Math.round(percent) + "%";
        
        applyState(prediction.state);
        updateDashboard(prediction.state, sensorData);

    } catch (err) {
        console.error("API Error:", err);
        document.getElementById("stateValue").innerText = "OFFLINE";
        applyState("CRITICAL");
        updateDashboard("CRITICAL", {});
    }
}

function resetColors() { allMeshes.forEach(function(obj) { obj.material.emissive.set(0x000000); obj.material.emissiveIntensity = 0; obj.userData.colorType = "none"; }); }
function setGroupColor(groupObj, colorHex, type) { if (!groupObj) return; if (groupObj.children && groupObj.children.length > 0) { groupObj.traverse((child) => { if (child.isMesh) { child.material.emissive.set(colorHex); child.userData.colorType = type; } }); } else if (groupObj.isMesh) { groupObj.material.emissive.set(colorHex); groupObj.userData.colorType = type; } }

function applyState(state) {
    resetColors();
    if (smokeParticles) smokeParticles.visible = false; 
    if (fireParticles) fireParticles.visible = false; 
    if (sparkParticles) sparkParticles.visible = false;
    if(faultRing) faultRing.visible = false;

    const box = document.getElementById("statusBox");
    const stateEl = document.getElementById("stateValue");

    box.classList.remove("status-good", "status-warning", "status-critical");

    if (state === "GOOD") { 
        rotationSpeed = { fan: 0.1, compressor: 0.15, turbine: 0.2 }; vibration = 0;
        box.classList.add("status-good");
        stateEl.innerText = "GOOD";
    } 
    else if (state === "WARNING") { 
        const yellowColor = 0xFFAA00; const yellowIntensity = 3.0; 
        setGroupColor(compressor, yellowColor, "yellow"); 
        fixedRandomParts.forEach(part => { part.material.emissive.set(yellowColor); part.material.emissiveIntensity = yellowIntensity; part.userData.colorType = "yellow"; }); 
        rotationSpeed = { fan: 0.15, compressor: 0.2, turbine: 0.25 }; vibration = 0.02;
        box.classList.add("status-warning");
        stateEl.innerText = "WARNING";
        updateFaultIndicator(compressor, "WARNING");
    } 
    else if (state === "CRITICAL") { 
        const redColor = 0xFF0000; const redIntensity = 4.0; 
        setGroupColor(turbine, redColor, "red"); 
        fixedRandomParts.forEach(part => { part.material.emissive.set(redColor); part.material.emissiveIntensity = redIntensity; part.userData.colorType = "red"; }); 
        if (smokeParticles) smokeParticles.visible = true; 
        if (fireParticles) fireParticles.visible = true; 
        if (sparkParticles) sparkParticles.visible = true; 
        rotationSpeed = { fan: 0.3, compressor: 0.35, turbine: 0.45 }; vibration = 0.08;
        box.classList.add("status-critical");
        stateEl.innerText = "CRITICAL";
        updateFaultIndicator(turbine, "CRITICAL");
    }

    playSoundForState(state);
}

// ---------------------------------------------------------
// BUTTON LOGIC (FIXED)
// ---------------------------------------------------------
let autoTestTimer = null;

function startAutoTest() {
    console.log("Starting Auto Test...");
    isDemoMode = true;
    if (autoTestTimer) clearTimeout(autoTestTimer);

    // Sequence: GOOD (3s) -> WARNING (3s) -> CRITICAL (3s) -> Resume
    applyState("GOOD");
    updateDashboard("GOOD", { sensor_2: 600, sensor_7: 500, sensor_4: 1000 }); 

    autoTestTimer = setTimeout(() => {
        applyState("WARNING");
        updateDashboard("WARNING", { sensor_2: 800, sensor_7: 550, sensor_4: 1200 });
        
        autoTestTimer = setTimeout(() => {
            applyState("CRITICAL");
            updateDashboard("CRITICAL", { sensor_2: 1000, sensor_7: 600, sensor_4: 1500 });

            autoTestTimer = setTimeout(() => {
                console.log("Auto Test Complete.");
                isDemoMode = false;
                getPrediction();
            }, 3000);
        }, 3000);
    }, 3000);
}

// REAL ENGINE BUTTON: Shows clean model (Lookdev) for 5 seconds
function showRealEngine() {
    console.log("👁️ Activating Real Engine Lookdev...");
    
    // 1. Stop Demos and Auto Predictions
    if (autoTestTimer) clearTimeout(autoTestTimer);
    isDemoMode = true;

    // 2. RESET COLORS (Show clean metal/geometry)
    resetColors();
    
    // Stop particles
    if (smokeParticles) smokeParticles.visible = false;
    if (fireParticles) fireParticles.visible = false;
    if (sparkParticles) sparkParticles.visible = false;
    if (faultRing) faultRing.visible = false;

    // Set text
    const stateEl = document.getElementById("stateValue");
    stateEl.innerText = "LOOKDEV";
    document.getElementById("statusBox").classList.remove("status-good", "status-warning", "status-critical");

    // 3. Wait 5 seconds to admire the model
    setTimeout(() => {
        console.log("✅ Lookdev Complete. Resuming Live Data.");
        isDemoMode = false;
        getPrediction(); // Resume live feed
    }, 5000);
}

// ---------------------------------------------------------
// ANIMATION LOOP
// ---------------------------------------------------------
function animate() {
    requestAnimationFrame(animate);
    controls.update();
    const rotSlider = document.getElementById('rotationSlider');
    if (skySphere && rotSlider) { const angle = rotSlider.value * (Math.PI / 180); skySphere.rotation.y = angle; }
    if (fan) fan.rotation.x += rotationSpeed.fan;
    if (compressor) compressor.rotation.x += rotationSpeed.compressor;
    if (turbine) turbine.rotation.x += rotationSpeed.turbine;
    
    const time = Date.now() * 0.002;
    
    if (!isDemoMode && time - lastPredictionTime > 2.0) {
        getPrediction();
        lastPredictionTime = time;
    }
    
    allMeshes.forEach((obj) => { if (obj.userData.colorType === "yellow") { const pulse = Math.sin(time + obj.position.x); obj.material.emissiveIntensity = 1.5 + pulse * 1.0; } else if (obj.userData.colorType === "red") { const wave = Math.sin(time * 2.0 - obj.position.x * 3.0); obj.material.emissiveIntensity = 4.0 + wave * 1.5; } });
    updateSmoke(); updateFire(); updateSparks();
    
    if(faultRing && faultRing.visible) {
        faultRing.rotation.z += 0.05;
        const scale = 1.0 + Math.sin(time * 5) * 0.1;
        faultRing.scale.set(scale, scale, scale);
    }
    if (dashboardMesh) dashboardMesh.lookAt(camera.position);
    if (model) { if (model.userData.baseY === undefined) model.userData.baseY = model.position.y; if (vibration > 0) { model.position.x = (Math.random() - 0.5) * vibration; model.position.y = model.userData.baseY + (Math.random() - 0.5) * vibration; } else { model.position.x = 0; model.position.y = model.userData.baseY; } }
    if (composer) composer.render(); else renderer.render(scene, camera);
}
window.addEventListener("load", () => { 
    document.getElementById("btnBody").onclick = () => { if(body) body.visible = !body.visible; }; 
    document.getElementById("btnDetails").onclick = () => { if(details) details.visible = !details.visible; }; 
});
window.addEventListener("resize", function() {
    const width = window.innerWidth; const height = window.innerHeight;
    camera.aspect = width / height; camera.updateProjectionMatrix(); renderer.setSize(width, height);
    if (composer) { composer.setSize(width, height); composer.passes.forEach(pass => { if (pass.uniforms && pass.uniforms['resolution']) { const pixelRatio = renderer.getPixelRatio(); pass.uniforms['resolution'].value.set(1.0 / (width * pixelRatio), 1.0 / (height * pixelRatio)); } }); }
});
animate();

// ---------------------------------------------------------
// THERMAL VISION MODE
// ---------------------------------------------------------
function toggleThermal() { isThermalMode = !isThermalMode; if (isThermalMode) { applyThermalColors(); } else { restoreOriginalColors(); } }
function applyThermalColors() {
    if (Object.keys(originalMaterials).length === 0) { allMeshes.forEach(obj => { originalMaterials[obj.uuid] = { emissive: obj.material.emissive.getHex(), intensity: obj.material.emissiveIntensity }; }); }
    allMeshes.forEach(obj => {
        let heatColor = 0x000000; 
        if (obj.userData.colorType === "red" || obj.name.toLowerCase().includes("turbine")) { heatColor = 0xFF2200; obj.material.emissiveIntensity = 2.0; } 
        else if (obj.userData.colorType === "yellow" || obj.name.toLowerCase().includes("compressor")) { heatColor = 0xFFAA00; obj.material.emissiveIntensity = 1.5; } 
        else if (obj.name.toLowerCase().includes("fan")) { heatColor = 0x00FFFF; obj.material.emissiveIntensity = 0.8; } 
        else { heatColor = 0x003366; obj.material.emissiveIntensity = 0.5; }
        obj.material.emissive.setHex(heatColor);
    });
}
function restoreOriginalColors() { allMeshes.forEach(obj => { if (originalMaterials[obj.uuid]) { obj.material.emissive.setHex(originalMaterials[obj.uuid].emissive); obj.material.emissiveIntensity = originalMaterials[obj.uuid].intensity; } }); applyState(document.getElementById("stateValue").innerText); }

// ---------------------------------------------------------
// FEATURE 1: DASHBOARD (FIXED AUTO-SCALING)
// ---------------------------------------------------------
function createDashboard() {
    dashboardCanvas = document.createElement('canvas'); dashboardCanvas.width = 512; dashboardCanvas.height = 256;
    dashboardCtx = dashboardCanvas.getContext('2d'); dashboardTexture = new THREE.CanvasTexture(dashboardCanvas); dashboardTexture.minFilter = THREE.LinearFilter;
    const planeGeo = new THREE.PlaneGeometry(5, 2.5);
    const planeMat = new THREE.MeshBasicMaterial({ map: dashboardTexture, transparent: true, side: THREE.DoubleSide, depthWrite: false, opacity: 0.9 });
    dashboardMesh = new THREE.Mesh(planeGeo, planeMat);
    dashboardMesh.position.set(-0.5, 6.4, 0.3);
    scene.add(dashboardMesh);
}

function updateDashboard(state, sensorData) {
    if (!dashboardCtx) return;

    // 1. Get Data (Fallback to defaults if missing)
    const newTemp = sensorData.sensor_2 || 600; 
    const newPress = sensorData.sensor_7 || 550;
    const newVib = sensorData.sensor_4 || 1200;

    // 2. Update History Arrays
    tempHistory.push(newTemp);
    tempHistory.shift();
    pressHistory.push(newPress);
    pressHistory.shift();
    vibHistory.push(newVib);
    vibHistory.shift();

    // 3. Draw Background
    dashboardCtx.clearRect(0, 0, 512, 256);
    dashboardCtx.fillStyle = 'rgba(0, 5, 15, 0.85)';
    dashboardCtx.beginPath();
    dashboardCtx.roundRect(10, 10, 492, 236, 10);
    dashboardCtx.fill();
    
    // Border Color based on state
    let borderColor = 'rgba(0, 255, 255, 0.5)';
    if(state === "WARNING") borderColor = 'rgba(255, 170, 0, 0.8)';
    if(state === "CRITICAL") borderColor = 'rgba(255, 0, 0, 0.8)';
    
    dashboardCtx.strokeStyle = borderColor;
    dashboardCtx.lineWidth = 2;
    dashboardCtx.stroke();

    // Header
    dashboardCtx.font = "bold 24px Arial";
    dashboardCtx.fillStyle = "#00ffff";
    dashboardCtx.shadowColor = '#00ffff';
    dashboardCtx.shadowBlur = 10;
    dashboardCtx.fillText("SENSOR DATA", 20, 40);
    dashboardCtx.shadowBlur = 0;

    // Divider
    dashboardCtx.strokeStyle = 'rgba(0, 255, 255, 0.3)';
    dashboardCtx.beginPath();
    dashboardCtx.moveTo(20, 50);
    dashboardCtx.lineTo(492, 50);
    dashboardCtx.stroke();

    // 4. Improved Auto-Scaling Graph Function
    function drawGraph(data, color, yBase) {
        const minVal = Math.min(...data);
        const maxVal = Math.max(...data);
        // Add 10% padding to range so line doesn't touch top/bottom
        let range = (maxVal - minVal) * 1.2; 
        if (range < 1) range = 10; // Minimum range to avoid flat lines

        dashboardCtx.strokeStyle = color;
        dashboardCtx.lineWidth = 2;
        dashboardCtx.shadowColor = color;
        dashboardCtx.shadowBlur = 5;
        dashboardCtx.beginPath();
        
        data.forEach((val, index) => {
            const x = 20 + (index / historyLength) * 470;
            // Center the graph vertically in its 40px slot
            const y = yBase - ((val - minVal) / range) * 40 + 20;
            
            if (index === 0) dashboardCtx.moveTo(x, y);
            else dashboardCtx.lineTo(x, y);
        });
        
        dashboardCtx.stroke();
        dashboardCtx.shadowBlur = 0;
    }

    dashboardCtx.font = "14px Arial";
    
    // Temperature (Red)
    dashboardCtx.fillStyle = "#ff4444";
    dashboardCtx.fillText("TEMP: " + Math.round(newTemp), 20, 75);
    drawGraph(tempHistory, '#ff4444', 115);

    // Pressure (Green)
    dashboardCtx.fillStyle = "#44ff44";
    dashboardCtx.fillText("PRES: " + Math.round(newPress), 20, 125);
    drawGraph(pressHistory, '#44ff44', 170);

    // Vibration (Blue)
    dashboardCtx.fillStyle = "#4488ff";
    dashboardCtx.fillText("VIB: " + Math.round(newVib), 20, 190);
    drawGraph(vibHistory, '#4488ff', 235);

    dashboardTexture.needsUpdate = true;
}

// ---------------------------------------------------------
// FEATURE 2: X-RAY VISION
// ---------------------------------------------------------
function toggleXRay() {
    isXRayMode = !isXRayMode;
    if (body) {
        body.traverse((child) => {
            if (child.isMesh) {
                if (isXRayMode) {
                    child.material.transparent = true;
                    child.material.opacity = 0.15;
                    child.material.side = THREE.DoubleSide;
                } else {
                    child.material.transparent = false;
                    child.material.opacity = 1.0;
                    child.material.side = THREE.FrontSide;
                }
            }
        });
    }
}

// ---------------------------------------------------------
// FEATURE 3: FAULT LOCALIZATION
// ---------------------------------------------------------
function createFaultIndicator() {
    const geometry = new THREE.TorusGeometry(0.8, 0.05, 16, 50);
    const material = new THREE.MeshBasicMaterial({ color: 0xff0000, transparent: true, opacity: 0.8 });
    faultRing = new THREE.Mesh(geometry, material);
    faultRing.rotation.y = Math.PI / 2;
    faultRing.visible = false;
    scene.add(faultRing);
}

function toggleFaultMarkers() {
    showFaultMarkers = !showFaultMarkers;
    if(faultRing) faultRing.visible = showFaultMarkers && (document.getElementById("stateValue").innerText.includes("WARNING") || document.getElementById("stateValue").innerText.includes("CRITICAL"));
}

function updateFaultIndicator(targetPart, state) {
    if (!faultRing || !showFaultMarkers) return;
    if (targetPart) {
        const pos = new THREE.Vector3();
        targetPart.getWorldPosition(pos);
        faultRing.position.copy(pos);
        if (state === "WARNING") {
            faultRing.material.color.setHex(0xFFAA00);
        } else if (state === "CRITICAL") {
            faultRing.material.color.setHex(0xFF0000);
        }
        faultRing.visible = true;
    }
}