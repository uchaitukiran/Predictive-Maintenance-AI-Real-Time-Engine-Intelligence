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
renderer.toneMappingExposure = 0.4; // slight lift

renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

// CONTROLS
const controls = new THREE.OrbitControls(camera, renderer.domElement);

// 🔥 HDRI (YOUR LOCAL FILE)
// HDRI (FIXED)
new THREE.RGBELoader()
.setDataType(THREE.UnsignedByteType)
.load("hdri/studio.hdr", function(texture){

    texture.mapping = THREE.EquirectangularReflectionMapping;

    const pmrem = new THREE.PMREMGenerator(renderer);
    const envMap = pmrem.fromEquirectangular(texture).texture;

    scene.environment = envMap;
    scene.background = new THREE.Color(0xdcdcd0); // darker gray (better contrast)

});

// LIGHT (SOFT, NOT OVERBRIGHT)
const light = new THREE.DirectionalLight(0xffffff, 1.6);
light.position.set(5, 12, 6);
light.castShadow = true;

// 🔥 SHADOW QUALITY BOOST
light.shadow.mapSize.width = 4096;
light.shadow.mapSize.height = 4096;

light.shadow.radius = 6;              // 👈 BLUR
light.shadow.bias = -0.0003;          // 👈 reduce artifacts

// 🔥 BIGGER SHADOW AREA (prevents cut)
light.shadow.camera.left = -15;
light.shadow.camera.right = 15;
light.shadow.camera.top = 15;
light.shadow.camera.bottom = -15;

scene.add(light);

// Slight ambient lift (important for metals)
scene.add(new THREE.AmbientLight(0xffffff, 0.18));

// GROUND (FIXED SHADOW, NO CUT)
const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(200, 200), // 👈 bigger = no cut
    new THREE.ShadowMaterial({ 
        opacity: 0.15  // softer shadow
    })
);

ground.rotation.x = -Math.PI / 2;
ground.position.y = -3.2;  // 👈 slight adjust for better contact

ground.receiveShadow = true;

scene.add(ground);

// 🔥 REALISTIC SOFT SHADOW (BLUR IMAGE BASED)
const textureLoader = new THREE.TextureLoader();

const shadowTexture = textureLoader.load(
    "https://threejs.org/examples/textures/roundshadow.png"
);

const softShadow = new THREE.Mesh(
    new THREE.PlaneGeometry(18, 18),
    new THREE.MeshBasicMaterial({
        map: shadowTexture,
        transparent: true,
        opacity: 0.35,
        depthWrite: false
    })
);

softShadow.rotation.x = -Math.PI / 2;
softShadow.position.y = -3.15; // slightly above ground

scene.add(softShadow);



// MODEL
let fan, compressor, turbine, body, details;

const loader = new THREE.GLTFLoader();

loader.load("models/engine.glb", function(gltf){

    const model = gltf.scene;

    model.scale.set(3,3,3);

    const box = new THREE.Box3().setFromObject(model);
    const center = box.getCenter(new THREE.Vector3());
    model.position.sub(center);

    scene.add(model);

    model.traverse(function(child){
        if(child.isMesh){

            child.castShadow = true;

            child.material.envMapIntensity = 1.0;
            child.material.metalness = 0.5;
            child.material.roughness = 0.5;
        }
    });

    // 🔥 METAL LOOK FIX
    model.traverse(function(child){
        if(child.isMesh){

            child.castShadow = true;

            child.material.envMapIntensity = 1.5; // 🔥 STRONG REFLECTION
            child.material.metalness = 0.70;
            child.material.roughness = 0.13;

            child.material.needsUpdate = true;
        }
    });

    // ✅ YOUR REAL NAMES
    fan = model.getObjectByName("fan_rotor");
    compressor = model.getObjectByName("compressor_rotor");
    turbine = model.getObjectByName("turbine_rotor");
    body = model.getObjectByName("engine_body");
    details = model.getObjectByName("engine_details");

});

// BUTTONS (FIXED)
document.getElementById("btnBody").onclick = function(){
    if(body) body.visible = !body.visible;
};

document.getElementById("btnDetails").onclick = function(){
    if(details) details.visible = !details.visible;
};

// ANIMATION
function animate(){

    requestAnimationFrame(animate);

    if(fan) fan.rotation.x += 0.1;
    if(compressor) compressor.rotation.x += 0.15;
    if(turbine) turbine.rotation.x += 0.2;

    renderer.render(scene, camera);
}

animate();

// RESIZE
window.addEventListener("resize", function(){
    camera.aspect = window.innerWidth/window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});