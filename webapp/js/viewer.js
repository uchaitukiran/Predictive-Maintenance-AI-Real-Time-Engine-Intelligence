// SCENE
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf0f0f0);

// CAMERA
const camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 0.1, 1000);
camera.position.set(0,1.5,6);

// RENDERER
const renderer = new THREE.WebGLRenderer({
    canvas: document.querySelector("#scene"),
    antialias:true
});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);

renderer.outputEncoding = THREE.sRGBEncoding;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.4;

renderer.shadowMap.enabled = true;

// CONTROLS
const controls = new THREE.OrbitControls(camera, renderer.domElement);

// HDRI
new THREE.RGBELoader().load("hdri/studio.hdr", function(texture){
    texture.mapping = THREE.EquirectangularReflectionMapping;
    scene.environment = texture;
});

// LIGHT
const light = new THREE.DirectionalLight(0xffffff, 1.6);
light.position.set(5, 12, 6);
light.castShadow = true;
scene.add(light);
scene.add(new THREE.AmbientLight(0xffffff, 0.18));

// GROUND
const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(200, 200),
    new THREE.ShadowMaterial({ opacity: 0.15 })
);
ground.rotation.x = -Math.PI / 2;
ground.position.y = -3.2;
ground.receiveShadow = true;
scene.add(ground);

// -------------------------
let model, fan, compressor, turbine, body, details;
let rotationSpeed = { fan:0.12, compressor:0.18, turbine:0.2 };
let vibration = 0;

// -------------------------
// MODEL LOAD
// -------------------------
const loader = new THREE.GLTFLoader();

loader.load("models/engine.glb", function(gltf){

    model = gltf.scene;
    model.scale.set(3,3,3);

    const box = new THREE.Box3().setFromObject(model);
    const center = box.getCenter(new THREE.Vector3());
    model.position.sub(center);

    scene.add(model);

    // Material tuning
    model.traverse(function(child){
        if(child.isMesh){
            child.castShadow = true;
            child.material.envMapIntensity = 2.8;
            child.material.metalness = 0.7;
            child.material.roughness = 0.15;
        }
    });

    // ✅ IMPORTANT: pick ONLY front fan (first rotating part)
    // 🔥 FIND ALL PARTS PROPERLY
model.traverse((obj) => {

    if(obj.name === "fan_rotor") fan = obj;
    if(obj.name === "compressor_rotor") compressor = obj;
    if(obj.name === "turbine_rotor") turbine = obj;

    if(obj.name === "engine_body") body = obj;
    if(obj.name === "engine_details") details = obj;

});

// DEBUG (check once)
console.log("FAN:", fan);
console.log("COMPRESSOR:", compressor);
console.log("TURBINE:", turbine);

// fallback (if fan not found)
if(!fan){
    fan = model.children[0];
}

// DEBUG
console.log("FAN:", fan);
console.log("BODY:", body);
console.log("DETAILS:", details);

    getPrediction();
});

// -------------------------
// API CALL
// -------------------------
async function getPrediction(){
    try{
        const res = await fetch("http://127.0.0.1:5000/predict",{
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                temperature: 85,
                pressure: 30,
                vibration: 0.3
            })
        });

        const data = await res.json();

        document.getElementById("stateText").innerText = "State: " + data.state;
        document.getElementById("rulText").innerText = "RUL: " + data.Predicted_RUL.toFixed(2);

        applyState(data.state);

    }catch(err){
        console.error(err);
    }
}

// -------------------------
// RESET COLORS
// -------------------------
function resetColors(){
    if(!model) return;

    model.traverse(function(obj){
        if(obj.isMesh){
            obj.material.emissive.set(0x000000);
            obj.material.emissiveIntensity = 0;
        }
    });
}

// -------------------------
// APPLY STATE
// -------------------------
function applyState(state){

    resetColors();

    if(state === "GOOD"){

        // 🟢 FULL ENGINE GREEN (SOFT, NOT UGLY)
        model.traverse(function(obj){
            if(obj.isMesh){
                obj.material.emissive.set(0x00ff00);
                obj.material.emissiveIntensity = 0.35; // 🔥 balanced
            }
        });

        rotationSpeed = { fan:0.1, compressor:0.15, turbine:0.2 };
        vibration = 0;

    }else if(state === "WARNING"){

        model.traverse(function(obj){
            if(obj.isMesh){
                obj.material.emissive.set(0xffaa00);
                obj.material.emissiveIntensity = 0.5;
            }
        });

        rotationSpeed = { fan:0.15, compressor:0.2, turbine:0.25 };
        vibration = 0.02;

    }else{

    model.traverse((obj)=>{
        if(obj.isMesh){

            // 🔴 base red
            obj.material.emissive.set(0xff0000);
            obj.material.emissiveIntensity = 0.8;

            // 🔥 EXTRA HEAT ON TURBINE
            if(obj.name.toLowerCase().includes("turbine")){
                obj.material.emissive.set(0xff2200); // hot orange-red
                obj.material.emissiveIntensity = 1.5; // 🔥 glow boost
            }

        }
    });

    rotationSpeed = {
        fan: 0.3,
        compressor: 0.35,
        turbine: 0.45
    };

    vibration = 0.08; // stronger shake
}

    document.getElementById("stateText").innerText = "State: " + state;
}

// -------------------------
// AUTO TEST
// -------------------------
let autoInterval = null;

function startAutoTest(){
    if(autoInterval) clearInterval(autoInterval);

    const states = ["GOOD", "WARNING", "CRITICAL"];
    let i = 0;

    autoInterval = setInterval(()=>{
        applyState(states[i]);
        i = (i + 1) % states.length;
    }, 2000);
}

// -------------------------
// REAL ENGINE RESET
// -------------------------
function showRealEngine(){
    if(autoInterval) clearInterval(autoInterval);

    resetColors();

    setTimeout(()=>{
        applyState("WARNING");
    }, 3000);
}

// -------------------------
// ANIMATION
// -------------------------
function animate(){

    requestAnimationFrame(animate);

    if(fan) fan.rotation.x += rotationSpeed.fan;

    if(compressor) compressor.rotation.x += rotationSpeed.compressor;

    if(turbine) turbine.rotation.x += rotationSpeed.turbine;

    // 🔥 SHAKE ENGINE ONLY
    if(model){
        if(vibration > 0){
            model.position.x = (Math.random() - 0.5) * vibration;
            model.position.y = (Math.random() - 0.5) * vibration;
        }else{
            model.position.x = 0;
            model.position.y = 0;
        }
    }

    renderer.render(scene, camera);
}

// 🔥 BUTTON FIX (ensure DOM loaded)
window.addEventListener("load", () => {

    document.getElementById("btnBody").onclick = () => {
        if(body){
            body.visible = !body.visible;
            console.log("Body toggled:", body.visible);
        } else {
            console.log("Body NOT FOUND");
        }
    };

    document.getElementById("btnDetails").onclick = () => {
        if(details){
            details.visible = !details.visible;
            console.log("Details toggled:", details.visible);
        } else {
            console.log("Details NOT FOUND");
        }
    };

});

animate();

// RESIZE
window.addEventListener("resize", function(){
    camera.aspect = window.innerWidth/window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});