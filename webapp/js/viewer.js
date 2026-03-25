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

// LIGHTS
const light = new THREE.DirectionalLight(0xffffff, 1.6);
light.position.set(5, 12, 6);
light.castShadow = true;
scene.add(light);

const fillLight = new THREE.DirectionalLight(0xffffff, 0.8);
fillLight.position.set(-5, 3, 5);
scene.add(fillLight);

const rimLight = new THREE.DirectionalLight(0xffffff, 1.2);
rimLight.position.set(0, 5, -8);
scene.add(rimLight);

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
const loader = new THREE.GLTFLoader();

loader.load("models/engine.glb", function(gltf){

    model = gltf.scene;
    model.scale.set(3,3,3);

    const box = new THREE.Box3().setFromObject(model);
    const center = box.getCenter(new THREE.Vector3());
    model.position.sub(center);

    scene.add(model);

    model.traverse(function(child){
        if(child.isMesh){
            child.castShadow = true;
            child.material.envMapIntensity = 2.8;
        }
    });

    model.traverse((obj) => {
        if(obj.name === "fan_rotor") fan = obj;
        if(obj.name === "compressor_rotor") compressor = obj;
        if(obj.name === "turbine_rotor") turbine = obj;

        if(obj.name === "engine_body") body = obj;
        if(obj.name === "engine_details") details = obj;
    });

    if(!fan){
        fan = model.children[0];
    }

    getPrediction();
});

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
function resetColors(){
    if(!model) return;

    model.traverse(function(obj){
        if(obj.isMesh){
            obj.material.emissive.set(0x000000);
            obj.material.emissiveIntensity = 0;
            obj.userData.baseGlow = 0;
            obj.userData.isBreathing = false;
        }
    });
}

// -------------------------
function applyState(state){

    resetColors();

    if(state === "GOOD"){
        rotationSpeed = { fan:0.1, compressor:0.15, turbine:0.2 };
        vibration = 0;
    }

    // WARNING = compressor only, yellow
    else if(state === "WARNING"){

        if(compressor){
            compressor.traverse(obj=>{
                if(obj.isMesh){
                    obj.material.emissive.set(0xffcc00);
                    obj.material.emissiveIntensity = 0.9;
                    obj.userData.baseGlow = 0.9;
                    obj.userData.isBreathing = true;
                }
            });
        }

        rotationSpeed = { fan:0.15, compressor:0.2, turbine:0.25 };
        vibration = 0.02;
    }

    // CRITICAL = turbine + compressor, both red family only
    else{

        if(turbine){
            turbine.traverse(obj=>{
                if(obj.isMesh){
                    obj.material.emissive.set(0xff0000);
                    obj.material.emissiveIntensity = 1.2;
                    obj.userData.baseGlow = 1.2;
                    obj.userData.isBreathing = true;
                }
            });
        }

        if(compressor){
            compressor.traverse(obj=>{
                if(obj.isMesh){
                    obj.material.emissive.set(0xcc0000);
                    obj.material.emissiveIntensity = 0.8;
                    obj.userData.baseGlow = 0.8;
                    obj.userData.isBreathing = true;
                }
            });
        }

        rotationSpeed = { fan:0.3, compressor:0.35, turbine:0.45 };
        vibration = 0.08;
    }

    document.getElementById("stateText").innerText = "State: " + state;
}

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
function showRealEngine(){
    if(autoInterval) clearInterval(autoInterval);

    resetColors();

    setTimeout(()=>{
        applyState("WARNING");
    }, 3000);
}

// -------------------------
function animate(){

    requestAnimationFrame(animate);

    if(fan) fan.rotation.x += rotationSpeed.fan;
    if(compressor) compressor.rotation.x += rotationSpeed.compressor;
    if(turbine) turbine.rotation.x += rotationSpeed.turbine;

    // visible breathing
    const pulse = (Math.sin(Date.now() * 0.004) + 1) / 2;

    if(model){
        model.traverse((obj)=>{
            if(obj.isMesh && obj.userData.isBreathing){
                obj.material.emissiveIntensity =
                    obj.userData.baseGlow * (0.55 + pulse * 0.85);
            }
        });
    }

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

// BUTTONS (UNCHANGED)
window.addEventListener("load", () => {

    document.getElementById("btnBody").onclick = () => {
        if(body) body.visible = !body.visible;
    };

    document.getElementById("btnDetails").onclick = () => {
        if(details) details.visible = !details.visible;
    };

});

animate();

// RESIZE
window.addEventListener("resize", function(){
    camera.aspect = window.innerWidth/window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});