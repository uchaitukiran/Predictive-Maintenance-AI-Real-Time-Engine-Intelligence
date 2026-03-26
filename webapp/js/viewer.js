// ---------------------------------------------------------
// SCENE SETUP
// ---------------------------------------------------------
const scene = new THREE.Scene();

// CAMERA
const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 1.5, 6);

// RENDERER
const renderer = new THREE.WebGLRenderer({
    canvas: document.querySelector("#scene"),
    antialias: false, 
    powerPreference: "high-performance"
});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.8; 
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

// CONTROLS
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.maxPolarAngle = Math.PI / 2; 

// ---------------------------------------------------------
// POST PROCESSING (BLOOM)
// ---------------------------------------------------------
let composer = null;

function setupPostProcessing() {
    if (typeof THREE.EffectComposer !== 'undefined') {
        composer = new THREE.EffectComposer(renderer);
        
        const renderPass = new THREE.RenderPass(scene, camera);
        composer.addPass(renderPass);

        // Bloom Settings:
        // Strength 0.3 (Subtle Glow)
        // Threshold 0.88 (High cutoff - stops Sky/Env from glowing)
        const bloomPass = new THREE.UnrealBloomPass(
            new THREE.Vector2(window.innerWidth, window.innerHeight),
            0.2,  // Strength
            0.15,  // Radius
            0.8  // Threshold
        );
        composer.addPass(bloomPass);

        // FXAA
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
}, undefined, function(err) {
    console.error("HDRI Error", err);
});

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
const keyLight = new THREE.SpotLight(0xffffff, 2.0);
keyLight.position.set(10, 20, 10);
keyLight.castShadow = true;
scene.add(keyLight);

const fillLight = new THREE.DirectionalLight(0xffffff, 1.0);
fillLight.position.set(-10, 5, 5);
scene.add(fillLight);

scene.add(new THREE.AmbientLight(0xffffff, 0.5));

// ---------------------------------------------------------
// SMOKE SYSTEM
// ---------------------------------------------------------
let smokeParticles = null;
let turbinePosition = new THREE.Vector3(); 
let exhaustDirection = new THREE.Vector3(0, 0, -1); 
const smokeCount = 200;

function createSmokeSystem() {
    const canvas = document.createElement('canvas');
    canvas.width = 64;
    canvas.height = 64;
    const ctx = canvas.getContext('2d');
    
    const gradient = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
    gradient.addColorStop(0, 'rgba(255, 255, 255, 1.0)');
    gradient.addColorStop(0.4, 'rgba(200, 200, 200, 0.8)');
    gradient.addColorStop(1, 'rgba(150, 150, 150, 0)');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 64, 64);
    
    const smokeTexture = new THREE.CanvasTexture(canvas);
    
    const smokeMaterial = new THREE.PointsMaterial({
        size: 3.5, 
        map: smokeTexture,
        transparent: true,
        opacity: 0.7,
        depthWrite: false,
        blending: THREE.NormalBlending
    });

    const smokeGeometry = new THREE.BufferGeometry();
    const positions = new Float32Array(smokeCount * 3);
    const velocities = [];

    for (let i = 0; i < smokeCount; i++) {
        positions[i * 3] = 0; 
        positions[i * 3 + 1] = 0; 
        positions[i * 3 + 2] = 0;
        
        velocities.push({
            speed: 0.15 + Math.random() * 0.1
        });
    }

    smokeGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    smokeGeometry.userData.velocities = velocities;

    smokeParticles = new THREE.Points(smokeGeometry, smokeMaterial);
    smokeParticles.visible = false;
    scene.add(smokeParticles);
}

function updateSmoke() {
    if (!smokeParticles || !smokeParticles.visible) return;

    const positions = smokeParticles.geometry.attributes.position.array;
    const velocities = smokeParticles.geometry.userData.velocities;

    for (let i = 0; i < smokeCount; i++) {
        positions[i * 3] += exhaustDirection.x * velocities[i].speed;
        positions[i * 3 + 1] += exhaustDirection.y * velocities[i].speed;
        positions[i * 3 + 2] += exhaustDirection.z * velocities[i].speed;

        const dx = positions[i * 3] - turbinePosition.x;
        const dy = positions[i * 3 + 1] - turbinePosition.y;
        const dz = positions[i * 3 + 2] - turbinePosition.z;
        const dist = Math.sqrt(dx*dx + dy*dy + dz*dz);

        if (dist > 10.0) {
            positions[i * 3] = turbinePosition.x + (Math.random() - 0.5) * 0.5;
            positions[i * 3 + 1] = turbinePosition.y + (Math.random() - 0.5) * 0.5;
            positions[i * 3 + 2] = turbinePosition.z + (Math.random() - 0.5) * 0.5;
        }
    }

    smokeParticles.geometry.attributes.position.needsUpdate = true;
}

// ---------------------------------------------------------
// AUDIO MANAGEMENT
// ---------------------------------------------------------
const soundEngine = document.getElementById('soundEngine');
const soundWarning = document.getElementById('soundWarning');
const soundAlarm = document.getElementById('soundAlarm');
const btnSound = document.getElementById('btnSound');

let isMuted = true;

function toggleSound() {
    try {
        isMuted = !isMuted;
        if (isMuted) {
            btnSound.innerText = "Sound: OFF";
            stopAllAudio();
        } else {
            btnSound.innerText = "Sound: ON";
            const stateText = document.getElementById("stateText").innerText.split(": ")[1];
            playSoundForState(stateText);
        }
    } catch (e) { console.log("Sound error", e); }
}

function stopAllAudio() {
    try {
        if(soundEngine) soundEngine.pause();
        if(soundWarning) soundWarning.pause();
        if(soundAlarm) soundAlarm.pause();
    } catch (e) {}
}

function playSoundForState(state) {
    if (isMuted) return;
    stopAllAudio();
    try {
        if (state === "GOOD") { if(soundEngine) soundEngine.play(); }
        else if (state === "WARNING") { if(soundWarning) soundWarning.play(); }
        else if (state === "CRITICAL") { if(soundAlarm) soundAlarm.play(); }
    } catch (e) { console.log("Audio play failed", e); }
}

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

    model = gltf.scene;
    model.scale.set(3, 3, 3);

    const box = new THREE.Box3().setFromObject(model);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());

    model.position.x = -center.x;
    model.position.z = -center.z;
    model.position.y = -box.min.y; 
    model.userData.baseY = model.position.y;

    scene.add(model);

    const focusTarget = new THREE.Vector3(0, size.y * 0.3, 0); 
    controls.target.copy(focusTarget);
    camera.lookAt(focusTarget);
    const maxDim = Math.max(size.x, size.y, size.z);
    camera.position.set(0, size.y * 0.5, maxDim * 1.5);

    model.traverse(function(child) {
        if (child.isMesh) {
            if (child.material) {
                child.material = child.material.clone();
            }
            
            child.castShadow = true;
            child.receiveShadow = true;
            child.material.envMapIntensity = 1.0;
            const maxAnisotropy = renderer.capabilities.getMaxAnisotropy();
            if (child.material.map) child.material.map.anisotropy = maxAnisotropy;
            
            allMeshes.push(child);
        }
    });

    // Identify parts
    model.traverse((obj) => {
        if (obj.name === "fan_rotor") fan = obj;
        if (obj.name === "compressor_rotor") compressor = obj;
        if (obj.name === "turbine_rotor") turbine = obj;
        if (obj.name === "engine_body") body = obj;
        if (obj.name === "engine_details") details = obj;
    });

    if (!fan) fan = model.children[0];

    // CALCULATE SMOKE DIRECTION (FAN -> TURBINE)
    if (fan && turbine) {
        const fanPos = new THREE.Vector3();
        fan.getWorldPosition(fanPos);
        turbinePosition = new THREE.Vector3();
        turbine.getWorldPosition(turbinePosition);
        
        exhaustDirection.subVectors(turbinePosition, fanPos);
        exhaustDirection.normalize();
    }

    // -----------------------------------------------------
    // 🔥 FIXED PARTS LOGIC (FIXED FAN EXCLUSION)
    // -----------------------------------------------------
    
    // Helper to check if a mesh is inside the Fan (Child of Fan)
    function isInsideFan(mesh, fanObj) {
        if (!fanObj) return false;
        let parent = mesh.parent;
        while (parent) {
            if (parent === fanObj) return true;
            parent = parent.parent;
        }
        return false;
    }

    // Helper to create a consistent number from a string name
    function getFixedSeed(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            hash = ((hash << 5) - hash) + str.charCodeAt(i);
            hash |= 0; 
        }
        return Math.abs(hash);
    }

    // Exclude the Fan itself AND anything inside it
    const colorableParts = allMeshes.filter(mesh => {
        // 1. Exclude if it IS the fan
        if (mesh === fan) return false;
        
        // 2. Exclude if it is INSIDE the fan group (e.g. blades)
        if (isInsideFan(mesh, fan)) return false;

        return true;
    });

    // Sort by Name Hash instead of Math.random()
    const shuffled = [...colorableParts].sort((a, b) => {
        return getFixedSeed(a.name) - getFixedSeed(b.name);
    });

    // Select 80% of parts
    const numParts = Math.floor(colorableParts.length * 0.72); 
    fixedRandomParts = shuffled.slice(0, numParts);

    console.log("Fixed Parts Selected:", fixedRandomParts.length);

    setupPostProcessing();
    createSmokeSystem(); 
    getPrediction();

});

// ---------------------------------------------------------
// API & LOGIC
// ---------------------------------------------------------
async function getPrediction() {
    try {
        const res = await fetch("http://127.0.0.1:5000/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ temperature: 85, pressure: 30, vibration: 0.3 })
        });
        const data = await res.json();
        document.getElementById("stateText").innerText = "State: " + data.state;
        document.getElementById("rulText").innerText = "RUL: " + data.Predicted_RUL.toFixed(2);
        applyState(data.state);
    } catch (err) {
        console.error("API Error:", err);
        document.getElementById("stateText").innerText = "State: Server Offline";
        applyState("WARNING");
    }
}

function resetColors() {
    allMeshes.forEach(function(obj) {
        obj.material.emissive.set(0x000000);
        obj.material.emissiveIntensity = 0;
        obj.userData.colorType = "none";
    });
}

function setGroupColor(groupObj, colorHex, type) {
    if (!groupObj) return;
    if (groupObj.children && groupObj.children.length > 0) {
        groupObj.traverse((child) => {
            if (child.isMesh) {
                child.material.emissive.set(colorHex);
                child.userData.colorType = type;
            }
        });
    } else if (groupObj.isMesh) {
        groupObj.material.emissive.set(colorHex);
        groupObj.userData.colorType = type;
    }
}

function applyState(state) {
    
    resetColors();

    if (smokeParticles) smokeParticles.visible = false;

    if (state === "GOOD") {
        rotationSpeed = { fan: 0.1, compressor: 0.15, turbine: 0.2 };
        vibration = 0;
    } 
    else if (state === "WARNING") {
        // YELLOW GLOW
        const yellowColor = 0xFFAA00;
        const yellowIntensity = 3.0;

        setGroupColor(compressor, yellowColor, "yellow");
        
        fixedRandomParts.forEach(part => {
            part.material.emissive.set(yellowColor);
            part.material.emissiveIntensity = yellowIntensity;
            part.userData.colorType = "yellow";
        });

        rotationSpeed = { fan: 0.15, compressor: 0.2, turbine: 0.25 };
        vibration = 0.02;
    } 
    else if (state === "CRITICAL") {
        // DEEP HEAT RED
        const redColor = 0xFF2200;
        const redIntensity = 5.0;

        setGroupColor(turbine, redColor, "red"); 

        fixedRandomParts.forEach(part => {
            part.material.emissive.set(redColor);
            part.material.emissiveIntensity = redIntensity;
            part.userData.colorType = "red";
        });

        if (smokeParticles) smokeParticles.visible = true;

        rotationSpeed = { fan: 0.3, compressor: 0.35, turbine: 0.45 };
        vibration = 0.08;
    }

    document.getElementById("stateText").innerText = "State: " + state;
    playSoundForState(state);
}

let autoInterval = null;
function startAutoTest() {
    if (autoInterval) clearInterval(autoInterval);
    const states = ["GOOD", "WARNING", "CRITICAL"];
    let i = 0;
    autoInterval = setInterval(() => {
        applyState(states[i]);
        i = (i + 1) % states.length;
    }, 2000);
}

function showRealEngine() {
    if (autoInterval) clearInterval(autoInterval);
    resetColors();
    setTimeout(() => { applyState("WARNING"); }, 3000);
}

// ---------------------------------------------------------
// ANIMATION LOOP
// ---------------------------------------------------------
function animate() {
    requestAnimationFrame(animate);
    controls.update();

    const rotSlider = document.getElementById('rotationSlider');
    if (skySphere && rotSlider) {
        const angle = rotSlider.value * (Math.PI / 180);
        skySphere.rotation.y = angle;
    }

    if (fan) fan.rotation.x += rotationSpeed.fan;
    if (compressor) compressor.rotation.x += rotationSpeed.compressor;
    if (turbine) turbine.rotation.x += rotationSpeed.turbine;

    const time = Date.now() * 0.002;
    
    // Breathing Animation
    allMeshes.forEach((obj) => {
        if (obj.userData.colorType === "yellow") {
            const pulse = Math.sin(time + obj.position.x);
            obj.material.emissiveIntensity = 3.0 + pulse * 1.0;
        } 
        else if (obj.userData.colorType === "red") {
            const pulse = Math.sin(time + obj.position.x);
            obj.material.emissiveIntensity = 5.0 + pulse * 1.5;
        }
    });

    updateSmoke();

    if (model) {
        if (model.userData.baseY === undefined) model.userData.baseY = model.position.y;
        if (vibration > 0) {
            model.position.x = (Math.random() - 0.5) * vibration;
            model.position.y = model.userData.baseY + (Math.random() - 0.5) * vibration;
        } else {
            model.position.x = 0;
            model.position.y = model.userData.baseY;
        }
    }

    if (composer) composer.render();
    else renderer.render(scene, camera);
}

window.addEventListener("load", () => {
    document.getElementById("btnBody").onclick = () => { if(body) body.visible = !body.visible; };
    document.getElementById("btnDetails").onclick = () => { if(details) details.visible = !details.visible; };
});

window.addEventListener("resize", function() {
    const width = window.innerWidth;
    const height = window.innerHeight;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
    if (composer) {
        composer.setSize(width, height);
        composer.passes.forEach(pass => {
            if (pass.uniforms && pass.uniforms['resolution']) {
                const pixelRatio = renderer.getPixelRatio();
                pass.uniforms['resolution'].value.set(1.0 / (width * pixelRatio), 1.0 / (height * pixelRatio));
            }
        });
    }
});

animate();