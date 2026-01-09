// --- CONFIGURATION ---
const LANE_WIDTH = 3;
const GAME_SPEED_START = 0.25; // Reduced from 0.5 for better playability
const COLORS = {
    sky: 0x87CEEB,
    ground: 0x333333,
    hero: 0xFFFFFF,    // White Rabbit
    heroDetail: 0x679d39, // Green accessories
    obstacle: 0x8B4513, // IKEA Box Brown
    coin: 0xFFA500     // Carrot Orange
};

const TASKRABBIT_FACTS = [
    "TaskRabbit has completed over 10 million tasks!",
    "The average Tasker earns $35-50 per hour!",
    "Furniture assembly is the #1 task category!",
    "TaskRabbit operates in 8,000+ cities worldwide!",
    "IKEA assembly requests grew 300% since 2017!",
    "Peak booking day: Black Friday with 50,000+ tasks!",
    "TaskRabbit was founded in Boston in 2008!",
    "IKEA acquired TaskRabbit in September 2017!",
    "The most expensive task was $15,000 (full renovation)!",
    "Taskers have assembled 5+ million IKEA items!",
    "Moving help is the fastest-growing category!",
    "Average task completion time is 2.5 hours!",
    "98% of tasks receive 5-star ratings!",
    "San Francisco has the most Taskers per capita!",
    "Holiday season sees 400% more cleaning tasks!"
];

// --- GLOBAL VARIABLES ---
let scene, camera, renderer;
let hero;
let rollingGround;
let obstacles = [];
let coins = [];
let particles = [];
let landmarks = [];
let buildings = []; // Continuous cityscape buildings
let gameActive = false;
let score = 0;
let currentLane = 1; // 0: Left, 1: Middle, 2: Right
let heroY = 0; // Jump height
let isJumping = false;
let gameSpeed = GAME_SPEED_START;
let lives = 3; // Player has 3 lives
let invincible = false; // Invincibility after hit
let invincibilityTimer = 0;

// --- AUDIO SYSTEM ---
const audioContext = new (window.AudioContext || window.webkitAudioContext)();
const sounds = {
    jump: null,
    collect: null,
    crash: null,
    bonus: null
};

let backgroundMusic = null;
let musicGain = null;
let musicMuted = localStorage.getItem('musicMuted') === 'true';

function createSound(type, frequency, duration) {
    return function() {
        if (musicMuted) return;
        
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = frequency;
        oscillator.type = type;
        
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + duration);
    };
}

function initSounds() {
    sounds.jump = createSound('sine', 400, 0.1); // Jump - upward tone
    sounds.collect = createSound('square', 800, 0.1); // Collect - happy beep
    sounds.crash = createSound('sawtooth', 100, 0.3); // Crash - low harsh sound
    sounds.bonus = createSound('sine', 1000, 0.2); // Bonus - high pleasant tone
}

function playSound(soundName) {
    if (sounds[soundName]) {
        try {
            sounds[soundName]();
        } catch (e) {
            console.log('Audio playback failed:', e);
        }
    }
}

function initBackgroundMusic() {
    // Create a simple looping melody using oscillators
    musicGain = audioContext.createGain();
    musicGain.connect(audioContext.destination);
    musicGain.gain.value = musicMuted ? 0 : 0.1;
    
    // Update toggle button
    updateMusicToggle();
}

function playBackgroundMusic() {
    if (musicMuted) return;
    
    // Simple repeating melody pattern
    const notes = [262, 294, 330, 349, 392, 440, 494, 523]; // C major scale
    const pattern = [0, 2, 4, 2, 5, 4, 2, 0]; // Melody pattern
    let noteIndex = 0;
    
    function playNote() {
        if (!gameActive || musicMuted) return;
        
        const oscillator = audioContext.createOscillator();
        const noteGain = audioContext.createGain();
        
        oscillator.connect(noteGain);
        noteGain.connect(musicGain);
        
        oscillator.frequency.value = notes[pattern[noteIndex]];
        oscillator.type = 'triangle';
        
        noteGain.gain.setValueAtTime(0.05, audioContext.currentTime);
        noteGain.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.3);
        
        noteIndex = (noteIndex + 1) % pattern.length;
        
        if (gameActive) {
            setTimeout(playNote, 400);
        }
    }
    
    playNote();
}

function toggleMusic() {
    musicMuted = !musicMuted;
    localStorage.setItem('musicMuted', musicMuted);
    
    if (musicGain) {
        musicGain.gain.value = musicMuted ? 0 : 0.1;
    }
    
    updateMusicToggle();
    
    if (!musicMuted && gameActive) {
        playBackgroundMusic();
    }
}

function updateMusicToggle() {
    const toggle = document.getElementById('music-toggle');
    if (toggle) {
        toggle.textContent = musicMuted ? '🔇' : '🔊';
    }
}

// --- INITIALIZATION ---
function initGame() {
    init();
}

let gameInitialized = false;

function init() {
    console.log("init() called");
    if (gameInitialized) return;
    
    // Wait for username modal if needed
    if (typeof gameCanStart !== 'undefined' && !gameCanStart) {
        console.log("Waiting for username modal...");
        setTimeout(init, 100);
        return;
    }
    console.log("Proceeding with initialization...");
    
    // Initialize sounds
    initSounds();
    initBackgroundMusic();
    
    // Setup music toggle button
    document.getElementById('music-toggle').addEventListener('click', toggleMusic);
    
    // 1. Setup Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(COLORS.sky);
    scene.fog = new THREE.Fog(COLORS.sky, 10, 50); // Distance fog

    // 2. Setup Camera
    camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 100);
    camera.position.set(0, 3, 6);
    camera.lookAt(0, 0, -5);

    // 3. Setup Renderer
    renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.shadowMap.enabled = true;
    document.getElementById('game-container').appendChild(renderer.domElement);

    // 4. Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
    dirLight.position.set(10, 20, 10);
    dirLight.castShadow = true;
    scene.add(dirLight);

    createWorld();
    console.log("World created");
    createHero();
    console.log("Hero created");
    
    try {
        createSFLandmarks();
        console.log("Landmarks created");
    } catch (e) {
        console.error("Error creating landmarks:", e);
    }
    
    // Initialize continuous building rows on both sides
    try {
        for (let i = 0; i < 10; i++) {
            spawnBuildingRow(-10 - i * 8);
        }
        console.log("Buildings spawned");
    } catch (e) {
        console.error("Error spawning buildings:", e);
    }

    // Start Game Loop
    gameActive = true;
    gameInitialized = true;
    console.log("Game loop starting...");
    playBackgroundMusic();
    animate();
}

// --- WORLD BUILDING ---
function createWorld() {
    // Rolling Floor (Infinite illusion)
    const geometry = new THREE.PlaneGeometry(50, 200, 50, 50);
    const material = new THREE.MeshPhongMaterial({
        color: COLORS.ground,
        flatShading: true
    });
    rollingGround = new THREE.Mesh(geometry, material);
    rollingGround.rotation.x = -Math.PI / 2;
    rollingGround.position.y = -1;
    rollingGround.receiveShadow = true;
    scene.add(rollingGround);

    // Add Sidewalk Lines
    const lineGeo = new THREE.BoxGeometry(0.2, 0.1, 200);
    const lineMat = new THREE.MeshBasicMaterial({ color: 0xffffff });

    const leftLine = new THREE.Mesh(lineGeo, lineMat);
    leftLine.position.set(-1.5, -0.9, 0);
    scene.add(leftLine);

    const rightLine = new THREE.Mesh(lineGeo, lineMat);
    rightLine.position.set(1.5, -0.9, 0);
    scene.add(rightLine);
}

function createHero() {
    // Create a group for the rabbit - emoji-style cute bunny
    hero = new THREE.Group();
    hero.position.y = 0;
    
    // Body - Rounder, cuter white sphere
    const bodyGeo = new THREE.SphereGeometry(0.6, 32, 32);
    const bodyMat = new THREE.MeshPhongMaterial({ 
        color: 0xFFFFFF,
        emissive: 0x666666,
        flatShading: true,
        shininess: 10
    });
    const body = new THREE.Mesh(bodyGeo, bodyMat);
    body.castShadow = true;
    body.position.y = 0.4;
    hero.add(body);
    
    // Head - Bigger, rounder for cuteness
    const headGeo = new THREE.SphereGeometry(0.45, 32, 32);
    const headMat = new THREE.MeshPhongMaterial({ 
        color: 0xFFFFFF,
        emissive: 0x666666,
        flatShading: true,
        shininess: 10
    });
    const head = new THREE.Mesh(headGeo, headMat);
    head.castShadow = true;
    head.position.y = 1.15;
    hero.add(head);
    
    // Super long cute ears - emoji style (using cylinders instead of capsules)
    const earGeo = new THREE.CylinderGeometry(0.1, 0.1, 0.8, 16);
    const earMat = new THREE.MeshPhongMaterial({ 
        color: 0xFFFFFF,
        emissive: 0x555555,
        flatShading: true,
        shininess: 10
    });
    
    // Pink inner ears
    const innerEarGeo = new THREE.CylinderGeometry(0.06, 0.06, 0.6, 16);
    const innerEarMat = new THREE.MeshPhongMaterial({ 
        color: 0xFFB6C1,
        emissive: 0x884466,
        flatShading: true,
        shininess: 10
    });
    
    const leftEar = new THREE.Mesh(earGeo, earMat);
    leftEar.position.set(-0.2, 1.75, -0.1);
    leftEar.rotation.z = 0.15;
    leftEar.castShadow = true;
    hero.add(leftEar);
    
    const leftInnerEar = new THREE.Mesh(innerEarGeo, innerEarMat);
    leftInnerEar.position.set(-0.2, 1.75, -0.05);
    leftInnerEar.rotation.z = 0.15;
    hero.add(leftInnerEar);
    
    const rightEar = new THREE.Mesh(earGeo, earMat);
    rightEar.position.set(0.2, 1.75, -0.1);
    rightEar.rotation.z = -0.15;
    rightEar.castShadow = true;
    hero.add(rightEar);
    
    const rightInnerEar = new THREE.Mesh(innerEarGeo, innerEarMat);
    rightInnerEar.position.set(0.2, 1.75, -0.05);
    rightInnerEar.rotation.z = -0.15;
    hero.add(rightInnerEar);
    
    // Adorable big nose - emoji style
    const noseGeo = new THREE.SphereGeometry(0.1, 16, 16);
    const noseMat = new THREE.MeshPhongMaterial({ 
        color: 0xFF69B4,
        emissive: 0x884466,
        shininess: 50
    });
    const nose = new THREE.Mesh(noseGeo, noseMat);
    nose.position.set(0, 1.1, 0.4);
    hero.add(nose);
    
    // Big cute eyes - anime/emoji style
    const eyeGeo = new THREE.SphereGeometry(0.09, 16, 16);
    const eyeMat = new THREE.MeshBasicMaterial({ color: 0x000000 });
    
    const leftEye = new THREE.Mesh(eyeGeo, eyeMat);
    leftEye.position.set(-0.15, 1.25, 0.35);
    hero.add(leftEye);
    
    const rightEye = new THREE.Mesh(eyeGeo, eyeMat);
    rightEye.position.set(0.15, 1.25, 0.35);
    hero.add(rightEye);
    
    // Big eye sparkles for cuteness
    const sparkleGeo = new THREE.SphereGeometry(0.035, 8, 8);
    const sparkleMat = new THREE.MeshBasicMaterial({ color: 0xFFFFFF });
    
    const leftSparkle = new THREE.Mesh(sparkleGeo, sparkleMat);
    leftSparkle.position.set(-0.13, 1.3, 0.42);
    hero.add(leftSparkle);
    
    const rightSparkle = new THREE.Mesh(sparkleGeo, sparkleMat);
    rightSparkle.position.set(0.17, 1.3, 0.42);
    hero.add(rightSparkle);
    
    // Tiny sparkle accents
    const tinySparkle1 = new THREE.Mesh(new THREE.SphereGeometry(0.02, 8, 8), sparkleMat);
    tinySparkle1.position.set(-0.18, 1.32, 0.38);
    hero.add(tinySparkle1);
    
    const tinySparkle2 = new THREE.Mesh(new THREE.SphereGeometry(0.02, 8, 8), sparkleMat);
    tinySparkle2.position.set(0.12, 1.32, 0.38);
    hero.add(tinySparkle2);
    
    // Cute little mouth - simple curve
    const mouthGeo = new THREE.TorusGeometry(0.08, 0.02, 8, 12, Math.PI);
    const mouthMat = new THREE.MeshBasicMaterial({ color: 0x000000 });
    const mouth = new THREE.Mesh(mouthGeo, mouthMat);
    mouth.position.set(0, 1.02, 0.38);
    mouth.rotation.x = -0.3;
    hero.add(mouth);
    
    // Super fluffy round tail - emoji style
    const tailGeo = new THREE.SphereGeometry(0.22, 16, 16);
    const tailMat = new THREE.MeshPhongMaterial({ 
        color: 0xFFFFFF,
        emissive: 0x555555,
        flatShading: true,
        shininess: 10
    });
    const tail = new THREE.Mesh(tailGeo, tailMat);
    tail.position.set(0, 0.45, -0.55);
    tail.castShadow = true;
    hero.add(tail);
    hero.tail = tail; // Store reference for animation
    
    // Cute stubby feet - round
    const footGeo = new THREE.SphereGeometry(0.15, 16, 16);
    const footMat = new THREE.MeshPhongMaterial({ 
        color: 0xFFFFFF,
        emissive: 0x555555,
        flatShading: true,
        shininess: 10
    });
    
    const leftFoot = new THREE.Mesh(footGeo, footMat);
    leftFoot.position.set(-0.25, 0.1, 0.25);
    leftFoot.scale.set(1, 0.6, 1.3);
    leftFoot.castShadow = true;
    hero.add(leftFoot);
    
    const rightFoot = new THREE.Mesh(footGeo, footMat);
    rightFoot.position.set(0.25, 0.1, 0.25);
    rightFoot.scale.set(1, 0.6, 1.3);
    rightFoot.castShadow = true;
    hero.add(rightFoot);
    
    scene.add(hero);
}

function spawnObstacle() {
    // Traffic cone obstacle
    const lanes = [-LANE_WIDTH, 0, LANE_WIDTH];
    const chosenLane = lanes[Math.floor(Math.random() * lanes.length)];

    const coneGroup = new THREE.Group();
    
    // Main cone body - orange
    const coneGeo = new THREE.ConeGeometry(0.4, 1.2, 8);
    const coneMat = new THREE.MeshPhongMaterial({ 
        color: 0xFF6600,  // Orange
        emissive: 0x884400
    });
    const cone = new THREE.Mesh(coneGeo, coneMat);
    cone.position.y = 0.6;
    cone.castShadow = true;
    coneGroup.add(cone);
    
    // White stripe 1
    const stripeGeo = new THREE.CylinderGeometry(0.32, 0.35, 0.15, 8);
    const stripeMat = new THREE.MeshPhongMaterial({ color: 0xFFFFFF });
    const stripe1 = new THREE.Mesh(stripeGeo, stripeMat);
    stripe1.position.y = 0.9;
    coneGroup.add(stripe1);
    
    // White stripe 2
    const stripe2 = new THREE.Mesh(stripeGeo, stripeMat);
    stripe2.position.y = 0.5;
    coneGroup.add(stripe2);
    
    // Base - black square
    const baseGeo = new THREE.BoxGeometry(0.6, 0.1, 0.6);
    const baseMat = new THREE.MeshPhongMaterial({ color: 0x222222 });
    const base = new THREE.Mesh(baseGeo, baseMat);
    base.position.y = 0.05;
    base.castShadow = true;
    coneGroup.add(base);

    coneGroup.position.set(chosenLane, 0, -50);
    coneGroup.castShadow = true;

    scene.add(coneGroup);
    obstacles.push(coneGroup);
}

function spawnCoin() {
    const lanes = [-LANE_WIDTH, 0, LANE_WIDTH];
    const chosenLane = lanes[Math.floor(Math.random() * lanes.length)];

    const group = new THREE.Group();
    
    // US Dollar bill - green rectangular paper
    const billGeo = new THREE.BoxGeometry(0.6, 0.3, 0.02);
    const billMat = new THREE.MeshPhongMaterial({ 
        color: 0x85BB65,  // Dollar bill green
        emissive: 0x2a4418,
        shininess: 20
    });
    const bill = new THREE.Mesh(billGeo, billMat);
    group.add(bill);
    
    // Border decoration - darker green
    const borderMat = new THREE.MeshPhongMaterial({ 
        color: 0x4A7C45,
        emissive: 0x1a2a18
    });
    
    // Top border
    const borderGeo = new THREE.BoxGeometry(0.62, 0.04, 0.03);
    const topBorder = new THREE.Mesh(borderGeo, borderMat);
    topBorder.position.y = 0.13;
    group.add(topBorder);
    
    // Bottom border
    const bottomBorder = new THREE.Mesh(borderGeo, borderMat);
    bottomBorder.position.y = -0.13;
    group.add(bottomBorder);
    
    // Side borders
    const sideBorderGeo = new THREE.BoxGeometry(0.04, 0.3, 0.03);
    const leftBorder = new THREE.Mesh(sideBorderGeo, borderMat);
    leftBorder.position.x = -0.28;
    group.add(leftBorder);
    
    const rightBorder = new THREE.Mesh(sideBorderGeo, borderMat);
    rightBorder.position.x = 0.28;
    group.add(rightBorder);
    
    // Center "$" symbol
    const symbolMat = new THREE.MeshPhongMaterial({ 
        color: 0x2a4418,
        emissive: 0x0a1408
    });
    
    const symbolGeo = new THREE.BoxGeometry(0.15, 0.2, 0.04);
    const symbol = new THREE.Mesh(symbolGeo, symbolMat);
    symbol.position.z = 0.02;
    group.add(symbol);

    group.position.set(chosenLane, 0.5, -50);
    group.rotation.y = 0;
    group.itemType = 'dollar';
    scene.add(group);
    coins.push(group);
}

// --- SF LANDMARKS ---
function createSFLandmarks() {
    // ========================================
    // GOLDEN GATE BRIDGE - GLOWING NEON STYLE
    // ========================================
    const bridgeZ = -30; // Closer for visibility
    
    // Glowing neon orange material - bright and unmissable
    const glowingOrange = new THREE.MeshPhongMaterial({ 
        color: 0xFF4500,        // Bright orange-red
        emissive: 0xFF6347,     // Strong self-illumination
        specular: 0xFFFFFF,
        shininess: 100,
        flatShading: false
    });
    
    // Glow halo material for neon effect
    const glowHaloMat = new THREE.MeshBasicMaterial({
        color: 0xFF6600,
        transparent: true,
        opacity: 0.25,
        side: THREE.BackSide
    });

    function createBridgeTower(x) {
        const tower = new THREE.Group();
        
        // Main tower legs - glowing
        const legGeo = new THREE.BoxGeometry(0.8, 12, 0.8);
        const leftLeg = new THREE.Mesh(legGeo, glowingOrange);
        leftLeg.position.x = -0.6;
        const rightLeg = new THREE.Mesh(legGeo, glowingOrange);
        rightLeg.position.x = 0.6;
        tower.add(leftLeg, rightLeg);
        
        // Glow halos behind legs
        const haloGeo = new THREE.BoxGeometry(1.2, 13, 1.2);
        const leftHalo = new THREE.Mesh(haloGeo, glowHaloMat);
        leftHalo.position.x = -0.6;
        const rightHalo = new THREE.Mesh(haloGeo, glowHaloMat);
        rightHalo.position.x = 0.6;
        tower.add(leftHalo, rightHalo);
        
        // Cross-bracing (the iconic horizontal bars)
        const braceGeo = new THREE.BoxGeometry(1.6, 0.5, 0.7);
        for (let i = 0; i < 4; i++) {
            const brace = new THREE.Mesh(braceGeo, glowingOrange);
            brace.position.y = -4 + (i * 3);
            tower.add(brace);
        }
        
        tower.position.set(x, 6, bridgeZ);
        scene.add(tower);
        return tower;
    }

    const tower1 = createBridgeTower(-10);
    const tower2 = createBridgeTower(10);

    // Bridge deck - glowing
    const deckGeo = new THREE.BoxGeometry(26, 0.7, 2.5);
    const deck = new THREE.Mesh(deckGeo, glowingOrange);
    deck.position.set(0, 3, bridgeZ);
    scene.add(deck);
    
    // Deck glow halo
    const deckHaloGeo = new THREE.BoxGeometry(27, 1.2, 3);
    const deckHalo = new THREE.Mesh(deckHaloGeo, glowHaloMat);
    deckHalo.position.set(0, 3, bridgeZ);
    scene.add(deckHalo);

    // Curved Suspension Cables - also glowing
    const cableMat = new THREE.MeshPhongMaterial({ 
        color: 0xFF5722,
        emissive: 0xFF4500,
        shininess: 80
    });
    
    // Create curve between towers
    const curve = new THREE.QuadraticBezierCurve3(
        new THREE.Vector3(-10, 11, bridgeZ),
        new THREE.Vector3(0, 4.5, bridgeZ),
        new THREE.Vector3(10, 11, bridgeZ)
    );
    
    const points = curve.getPoints(30);
    const cableRadius = 0.15;
    
    for (let i = 0; i < points.length - 1; i++) {
        const start = points[i];
        const end = points[i+1];
        const distance = start.distanceTo(end);
        
        const segmentGeo = new THREE.CylinderGeometry(cableRadius, cableRadius, distance, 8);
        const segment = new THREE.Mesh(segmentGeo, cableMat);
        
        segment.position.copy(start).lerp(end, 0.5);
        segment.lookAt(end);
        segment.rotation.x += Math.PI / 2;
        
        scene.add(segment);

        // Vertical suspender cables
        if (i % 3 === 0 && i > 0 && i < points.length - 1) {
            const suspenderHeight = segment.position.y - 3;
            if (suspenderHeight > 0) {
                const suspenderGeo = new THREE.CylinderGeometry(0.06, 0.06, suspenderHeight, 6);
                const suspender = new THREE.Mesh(suspenderGeo, cableMat);
                suspender.position.set(segment.position.x, 3 + suspenderHeight/2, bridgeZ);
                scene.add(suspender);
            }
        }
    }

    // ========================================
    // ENHANCED LIGHTING FOR THE BRIDGE
    // ========================================
    
    // Strong point lights at towers (intensity 3)
    const bridgeLight1 = new THREE.PointLight(0xFF4500, 3, 30);
    bridgeLight1.position.set(-10, 10, bridgeZ + 3);
    scene.add(bridgeLight1);

    const bridgeLight2 = new THREE.PointLight(0xFF4500, 3, 30);
    bridgeLight2.position.set(10, 10, bridgeZ + 3);
    scene.add(bridgeLight2);
    
    // Upward spotlights on towers
    const spotlight1 = new THREE.SpotLight(0xFF6347, 2, 20, Math.PI / 6, 0.5);
    spotlight1.position.set(-10, 0, bridgeZ + 2);
    spotlight1.target.position.set(-10, 15, bridgeZ);
    scene.add(spotlight1);
    scene.add(spotlight1.target);
    
    const spotlight2 = new THREE.SpotLight(0xFF6347, 2, 20, Math.PI / 6, 0.5);
    spotlight2.position.set(10, 0, bridgeZ + 2);
    spotlight2.target.position.set(10, 15, bridgeZ);
    scene.add(spotlight2);
    scene.add(spotlight2.target);
    
    // Center bridge light
    const centerLight = new THREE.PointLight(0xFF5722, 2, 25);
    centerLight.position.set(0, 6, bridgeZ + 2);
    scene.add(centerLight);

    // ========================================
    // WATER/BAY REFLECTION BELOW BRIDGE
    // ========================================
    const waterGeo = new THREE.PlaneGeometry(40, 15);
    const waterMat = new THREE.MeshPhongMaterial({
        color: 0x1E3A5F,
        emissive: 0x0A1929,
        specular: 0x4488AA,
        shininess: 100,
        transparent: true,
        opacity: 0.7
    });
    const water = new THREE.Mesh(waterGeo, waterMat);
    water.rotation.x = -Math.PI / 2;
    water.position.set(0, -0.5, bridgeZ);
    scene.add(water);
    
    // Water reflection glow
    const waterGlow = new THREE.PointLight(0xFF4500, 0.5, 15);
    waterGlow.position.set(0, -1, bridgeZ);
    scene.add(waterGlow);

    // ========================================
    // TRANSAMERICA PYRAMID - Pushed back
    // ========================================
    const pyramidGeo = new THREE.ConeGeometry(2, 10, 4);
    const pyramidMat = new THREE.MeshPhongMaterial({ 
        color: 0xEEEEEE,
        emissive: 0x333333
    });
    const pyramid = new THREE.Mesh(pyramidGeo, pyramidMat);
    pyramid.position.set(18, 4, -55);
    pyramid.rotation.y = Math.PI / 4;
    scene.add(pyramid);
    
    // ========================================
    // SKYLINE BUILDINGS - Pushed far back
    // ========================================
    const buildingPositions = [
        { x: -18, h: 12, z: -60 },
        { x: -12, h: 8, z: -65 },
        { x: 14, h: 15, z: -62 },
        { x: 22, h: 10, z: -58 },
        { x: 25, h: 7, z: -55 }
    ];
    
    buildingPositions.forEach(pos => {
        const buildingGeo = new THREE.BoxGeometry(2, pos.h, 2);
        const buildingMat = new THREE.MeshPhongMaterial({ 
            color: 0x444444,
            transparent: true,
            opacity: 0.5  // Dimmed to not compete with bridge
        });
        const building = new THREE.Mesh(buildingGeo, buildingMat);
        building.position.set(pos.x, pos.h / 2, pos.z);
        scene.add(building);
    });
}
function spawnBARTTrain() {
    // Large traffic cone variant as obstacle
    const lanes = [-LANE_WIDTH, 0, LANE_WIDTH];
    const chosenLane = lanes[Math.floor(Math.random() * lanes.length)];
    
    const coneGroup = new THREE.Group();
    
    // Larger cone body - orange
    const coneGeo = new THREE.ConeGeometry(0.5, 1.5, 8);
    const coneMat = new THREE.MeshPhongMaterial({ 
        color: 0xFF4400,  // Brighter orange
        emissive: 0x992200
    });
    const cone = new THREE.Mesh(coneGeo, coneMat);
    cone.position.y = 0.75;
    cone.castShadow = true;
    coneGroup.add(cone);
    
    // White reflective stripes
    const stripeGeo1 = new THREE.CylinderGeometry(0.4, 0.43, 0.12, 8);
    const stripeMat = new THREE.MeshPhongMaterial({ 
        color: 0xFFFFFF,
        emissive: 0x666666
    });
    
    const stripe1 = new THREE.Mesh(stripeGeo1, stripeMat);
    stripe1.position.y = 1.1;
    coneGroup.add(stripe1);
    
    const stripe2 = new THREE.Mesh(stripeGeo1, stripeMat);
    stripe2.position.y = 0.7;
    coneGroup.add(stripe2);
    
    const stripe3 = new THREE.Mesh(stripeGeo1, stripeMat);
    stripe3.position.y = 0.3;
    coneGroup.add(stripe3);
    
    // Heavy base
    const baseGeo = new THREE.BoxGeometry(0.8, 0.15, 0.8);
    const baseMat = new THREE.MeshPhongMaterial({ color: 0x111111 });
    const base = new THREE.Mesh(baseGeo, baseMat);
    base.position.y = 0.08;
    base.castShadow = true;
    coneGroup.add(base);
    
    coneGroup.position.set(chosenLane, 0, -50);
    coneGroup.obstacleType = 'large_cone';
    
    scene.add(coneGroup);
    obstacles.push(coneGroup);
}

function spawnCableCar() {
    // TaskRabbit Badge - Premium collectible with TR logo!
    const lanes = [-LANE_WIDTH, 0, LANE_WIDTH];
    const chosenLane = lanes[Math.floor(Math.random() * lanes.length)];
    
    const badgeGroup = new THREE.Group();
    
    // TaskRabbit green color
    const trGreen = 0x1DBF73;
    const trGreenDark = 0x18A863;
    const cream = 0xF5F5DC;
    
    // Green material for the badge
    const greenMat = new THREE.MeshPhongMaterial({ 
        color: trGreen,
        emissive: 0x0D8050,
        specular: 0x88FFAA,
        shininess: 80
    });
    
    // Dark border material
    const borderMat = new THREE.MeshPhongMaterial({ 
        color: 0x333333,
        emissive: 0x111111,
        specular: 0x444444,
        shininess: 50
    });
    
    // Cream/white material for the rabbit logo
    const logoMat = new THREE.MeshPhongMaterial({ 
        color: cream,
        emissive: 0xCCCCBB,
        specular: 0xFFFFFF,
        shininess: 100
    });
    
    // Outer dark ring (border)
    const outerRingGeo = new THREE.CylinderGeometry(0.75, 0.75, 0.12, 32);
    const outerRing = new THREE.Mesh(outerRingGeo, borderMat);
    outerRing.rotation.x = Math.PI / 2;
    badgeGroup.add(outerRing);
    
    // Green circle (main badge)
    const circleGeo = new THREE.CylinderGeometry(0.65, 0.65, 0.14, 32);
    const circle = new THREE.Mesh(circleGeo, greenMat);
    circle.rotation.x = Math.PI / 2;
    circle.position.z = 0.02;
    badgeGroup.add(circle);
    
    // === TaskRabbit Rabbit Logo ===
    // The logo is a stylized rabbit made of curved lines
    
    // Main body curve (the "C" shape)
    const bodyGeo = new THREE.TorusGeometry(0.28, 0.055, 8, 24, Math.PI * 1.4);
    const body = new THREE.Mesh(bodyGeo, logoMat);
    body.rotation.z = Math.PI * 0.3;
    body.position.set(-0.05, -0.08, 0.1);
    badgeGroup.add(body);
    
    // Head (small circle at top of C)
    const headGeo = new THREE.SphereGeometry(0.1, 16, 16);
    const head = new THREE.Mesh(headGeo, logoMat);
    head.position.set(0.15, 0.22, 0.1);
    head.scale.z = 0.5;
    badgeGroup.add(head);
    
    // Ear (the tall curved part - like a "9" or "?")
    const earGeo = new THREE.TorusGeometry(0.15, 0.045, 8, 16, Math.PI * 1.2);
    const ear = new THREE.Mesh(earGeo, logoMat);
    ear.rotation.z = -Math.PI * 0.2;
    ear.position.set(0.22, 0.32, 0.1);
    badgeGroup.add(ear);
    
    // Ear tip (small ball at top)
    const earTipGeo = new THREE.SphereGeometry(0.055, 12, 12);
    const earTip = new THREE.Mesh(earTipGeo, logoMat);
    earTip.position.set(0.32, 0.48, 0.1);
    earTip.scale.z = 0.5;
    badgeGroup.add(earTip);
    
    // Tail curve (bottom part connecting back)
    const tailGeo = new THREE.TorusGeometry(0.12, 0.04, 8, 12, Math.PI * 0.8);
    const tail = new THREE.Mesh(tailGeo, logoMat);
    tail.rotation.z = Math.PI * 1.1;
    tail.position.set(-0.18, -0.32, 0.1);
    badgeGroup.add(tail);
    
    // Connecting line (vertical part of the rabbit)
    const lineGeo = new THREE.CylinderGeometry(0.04, 0.04, 0.25, 8);
    const line = new THREE.Mesh(lineGeo, logoMat);
    line.position.set(0.22, 0.08, 0.1);
    line.rotation.z = Math.PI * 0.05;
    badgeGroup.add(line);
    
    // Add glow effect
    const glowLight = new THREE.PointLight(trGreen, 1, 3);
    glowLight.position.z = 0.3;
    badgeGroup.add(glowLight);
    
    // Position and configure
    badgeGroup.position.set(chosenLane, 0.8, -50);
    badgeGroup.isBonus = true;
    
    // Rotate to face player
    badgeGroup.rotation.x = -Math.PI / 6; // Tilt towards player
    
    scene.add(badgeGroup);
    coins.push(badgeGroup);
}

function spawnScrewdriver() {
    // Screwdriver task item
    const lanes = [-LANE_WIDTH, 0, LANE_WIDTH];
    const chosenLane = lanes[Math.floor(Math.random() * lanes.length)];
    
    const group = new THREE.Group();
    
    // Handle - yellow
    const handleGeo = new THREE.CylinderGeometry(0.08, 0.08, 0.4, 8);
    const handleMat = new THREE.MeshPhongMaterial({ 
        color: 0xFFD700,
        emissive: 0x886600
    });
    const handle = new THREE.Mesh(handleGeo, handleMat);
    handle.rotation.z = Math.PI / 2;
    group.add(handle);
    
    // Metal shaft - silver
    const shaftGeo = new THREE.CylinderGeometry(0.04, 0.04, 0.5, 8);
    const shaftMat = new THREE.MeshPhongMaterial({ 
        color: 0xC0C0C0,
        shininess: 80,
        specular: 0xFFFFFF
    });
    const shaft = new THREE.Mesh(shaftGeo, shaftMat);
    shaft.rotation.z = Math.PI / 2;
    shaft.position.x = 0.45;
    group.add(shaft);
    
    // Tip
    const tipGeo = new THREE.ConeGeometry(0.05, 0.1, 8);
    const tip = new THREE.Mesh(tipGeo, shaftMat);
    tip.rotation.z = -Math.PI / 2;
    tip.position.x = 0.75;
    group.add(tip);
    
    group.position.set(chosenLane, 0.5, -50);
    group.rotation.y = Math.PI / 4;
    group.itemType = 'task';
    scene.add(group);
    coins.push(group);
}

function spawnMop() {
    // Mop task item
    const lanes = [-LANE_WIDTH, 0, LANE_WIDTH];
    const chosenLane = lanes[Math.floor(Math.random() * lanes.length)];
    
    const group = new THREE.Group();
    
    // Handle - brown wood
    const handleGeo = new THREE.CylinderGeometry(0.05, 0.05, 1.2, 8);
    const handleMat = new THREE.MeshPhongMaterial({ 
        color: 0x8B4513,
        emissive: 0x442211
    });
    const handle = new THREE.Mesh(handleGeo, handleMat);
    handle.position.y = 0.6;
    group.add(handle);
    
    // Mop head - white/gray
    const mopHeadGeo = new THREE.BoxGeometry(0.3, 0.15, 0.4);
    const mopHeadMat = new THREE.MeshPhongMaterial({ 
        color: 0xDDDDDD,
        emissive: 0x444444
    });
    const mopHead = new THREE.Mesh(mopHeadGeo, mopHeadMat);
    mopHead.position.y = 0;
    group.add(mopHead);
    
    // Mop strands (simplified)
    for (let i = 0; i < 3; i++) {
        const strandGeo = new THREE.BoxGeometry(0.08, 0.25, 0.08);
        const strand = new THREE.Mesh(strandGeo, mopHeadMat);
        strand.position.set(-0.1 + i * 0.1, -0.15, 0);
        group.add(strand);
    }
    
    group.position.set(chosenLane, 0.5, -50);
    group.rotation.z = Math.PI / 6;
    group.itemType = 'task';
    scene.add(group);
    coins.push(group);
}

function spawnIkeaBox() {
    // IKEA box as task item - with clear IKEA letters
    const lanes = [-LANE_WIDTH, 0, LANE_WIDTH];
    const chosenLane = lanes[Math.floor(Math.random() * lanes.length)];
    
    const group = new THREE.Group();
    
    // Main box - brown cardboard (bigger)
    const boxGeo = new THREE.BoxGeometry(0.8, 0.8, 0.5);
    const boxMat = new THREE.MeshPhongMaterial({ 
        color: 0xD2B48C,  // Tan/cardboard color
        emissive: 0x443322,
        flatShading: true
    });
    const box = new THREE.Mesh(boxGeo, boxMat);
    group.add(box);
    
    // Large IKEA blue panel (most of the front)
    const bluePanelGeo = new THREE.BoxGeometry(0.82, 0.5, 0.51);
    const bluePanelMat = new THREE.MeshPhongMaterial({ 
        color: 0x0051BA,  // IKEA blue
        emissive: 0x003388,
        shininess: 20,
        flatShading: true
    });
    const bluePanel = new THREE.Mesh(bluePanelGeo, bluePanelMat);
    bluePanel.position.y = 0.05;
    group.add(bluePanel);
    
    // Yellow stripe at bottom
    const yellowStripeGeo = new THREE.BoxGeometry(0.82, 0.15, 0.51);
    const yellowStripeMat = new THREE.MeshPhongMaterial({ 
        color: 0xFFDB00,  // IKEA yellow
        emissive: 0xCC8800,
        shininess: 20,
        flatShading: true
    });
    const yellowStripe = new THREE.Mesh(yellowStripeGeo, yellowStripeMat);
    yellowStripe.position.y = -0.325;
    group.add(yellowStripe);
    
    // Create IKEA letters with yellow on blue background
    const letterMat = new THREE.MeshPhongMaterial({ 
        color: 0xFFDB00,  // IKEA yellow
        emissive: 0xFFAA00,
        shininess: 30,
        flatShading: true
    });
    
    const zOffset = 0.26; // Slightly in front of blue panel
    
    // Letter I - simple vertical bar
    const iGeo = new THREE.BoxGeometry(0.08, 0.2, 0.02);
    const letterI = new THREE.Mesh(iGeo, letterMat);
    letterI.position.set(-0.27, 0.05, zOffset);
    group.add(letterI);
    
    // Letter K - vertical bar + two diagonals
    const kVert = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.2, 0.02), letterMat);
    kVert.position.set(-0.1, 0.05, zOffset);
    group.add(kVert);
    
    const kDiag1 = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.12, 0.02), letterMat);
    kDiag1.position.set(-0.04, 0.08, zOffset);
    kDiag1.rotation.z = -Math.PI / 4;
    group.add(kDiag1);
    
    const kDiag2 = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.12, 0.02), letterMat);
    kDiag2.position.set(-0.04, 0.02, zOffset);
    kDiag2.rotation.z = Math.PI / 4;
    group.add(kDiag2);
    
    // Letter E - vertical bar + three horizontal bars
    const eVert = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.2, 0.02), letterMat);
    eVert.position.set(0.08, 0.05, zOffset);
    group.add(eVert);
    
    const eTop = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.06, 0.02), letterMat);
    eTop.position.set(0.14, 0.12, zOffset);
    group.add(eTop);
    
    const eMid = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.06, 0.02), letterMat);
    eMid.position.set(0.13, 0.05, zOffset);
    group.add(eMid);
    
    const eBot = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.06, 0.02), letterMat);
    eBot.position.set(0.14, -0.02, zOffset);
    group.add(eBot);
    
    // Letter A - two diagonals + horizontal bar
    const aDiag1 = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.22, 0.02), letterMat);
    aDiag1.position.set(0.24, 0.05, zOffset);
    aDiag1.rotation.z = -Math.PI / 8;
    group.add(aDiag1);
    
    const aDiag2 = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.22, 0.02), letterMat);
    aDiag2.position.set(0.32, 0.05, zOffset);
    aDiag2.rotation.z = Math.PI / 8;
    group.add(aDiag2);
    
    const aBar = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.05, 0.02), letterMat);
    aBar.position.set(0.28, 0.02, zOffset);
    group.add(aBar);
    
    group.position.set(chosenLane, 0.5, -50);
    group.rotation.y = 0; // Face forward for better visibility
    group.itemType = 'task';
    scene.add(group);
    coins.push(group);
}

function spawnStreetSign() {
    // Street signs along the sides
    const side = Math.random() > 0.5 ? 5 : -5; // Left or right of lanes
    
    const signGroup = new THREE.Group();
    
    // Post
    const postGeo = new THREE.CylinderGeometry(0.1, 0.1, 3, 8);
    const postMat = new THREE.MeshPhongMaterial({ color: 0x555555 });
    const post = new THREE.Mesh(postGeo, postMat);
    post.position.y = 1.5;
    signGroup.add(post);
    
    // Sign board
    const signGeo = new THREE.BoxGeometry(1.5, 0.5, 0.1);
    const signMat = new THREE.MeshPhongMaterial({ color: 0x006400 }); // Green sign
    const sign = new THREE.Mesh(signGeo, signMat);
    sign.position.y = 2.8;
    signGroup.add(sign);
    
    signGroup.position.set(side, 0, -50);
    signGroup.isDecoration = true;
    
    scene.add(signGroup);
    landmarks.push(signGroup);
}

function createCityBuilding(x, z, height, width, depth, color) {
    // Create a single building with windows
    const group = new THREE.Group();
    
    // Main building body
    const buildingGeo = new THREE.BoxGeometry(width, height, depth);
    const buildingMat = new THREE.MeshPhongMaterial({
        color: color,
        emissive: color,
        emissiveIntensity: 0.1,
        flatShading: true
    });
    const building = new THREE.Mesh(buildingGeo, buildingMat);
    building.position.y = height / 2;
    group.add(building);
    
    // Add windows (grid pattern)
    const windowMat = new THREE.MeshPhongMaterial({
        color: 0xFFFFAA,
        emissive: 0xFFFF88,
        emissiveIntensity: Math.random() > 0.3 ? 0.5 : 0.1, // Some windows are lit
        flatShading: true
    });
    
    const floors = Math.floor(height / 0.8);
    const windowsPerFloor = Math.floor(width / 0.4);
    
    for (let floor = 0; floor < floors; floor++) {
        for (let win = 0; win < windowsPerFloor; win++) {
            const windowGeo = new THREE.BoxGeometry(0.2, 0.3, 0.02);
            const window = new THREE.Mesh(windowGeo, windowMat);
            window.position.set(
                -width/2 + 0.3 + win * 0.4,
                0.5 + floor * 0.8,
                depth/2 + 0.01
            );
            group.add(window);
        }
    }
    
    group.position.set(x, 0, z);
    return group;
}

function spawnBuildingRow(z) {
    // Create a continuous row of buildings on both sides
    const leftSide = -LANE_WIDTH * 2 - 2;
    const rightSide = LANE_WIDTH * 2 + 2;
    
    // Left side buildings
    for (let i = 0; i < 3; i++) {
        const height = 3 + Math.random() * 5;
        const width = 1.5 + Math.random() * 1;
        const depth = 2 + Math.random() * 2;
        const colors = [0x8B8B8B, 0xA9A9A9, 0x696969, 0x708090, 0x778899];
        const color = colors[Math.floor(Math.random() * colors.length)];
        
        const building = createCityBuilding(
            leftSide - i * 2,
            z,
            height,
            width,
            depth,
            color
        );
        scene.add(building);
        buildings.push(building);
    }
    
    // Right side buildings
    for (let i = 0; i < 3; i++) {
        const height = 3 + Math.random() * 5;
        const width = 1.5 + Math.random() * 1;
        const depth = 2 + Math.random() * 2;
        const colors = [0x8B8B8B, 0xA9A9A9, 0x696969, 0x708090, 0x778899];
        const color = colors[Math.floor(Math.random() * colors.length)];
        
        const building = createCityBuilding(
            rightSide + i * 2,
            z,
            height,
            width,
            depth,
            color
        );
        scene.add(building);
        buildings.push(building);
    }
}

function spawnHillside() {
    // SF hillside terrain on the side
    const side = Math.random() > 0.5 ? 7 : -7;
    
    const hillGroup = new THREE.Group();
    
    // Hill shape - green slope
    const hillGeo = new THREE.ConeGeometry(2, 3, 8);
    const hillMat = new THREE.MeshPhongMaterial({ 
        color: 0x6B8E23,
        emissive: 0x2a3a18,
        flatShading: true
    });
    const hill = new THREE.Mesh(hillGeo, hillMat);
    hill.position.y = 1.5;
    hill.rotation.y = Math.random() * Math.PI;
    hillGroup.add(hill);
    
    hillGroup.position.set(side, 0, -50);
    hillGroup.isDecoration = true;
    
    scene.add(hillGroup);
    landmarks.push(hillGroup);
}

function spawnLombardStreet() {
    // Lombard Street - famous curvy road section as special challenge
    const lombardGroup = new THREE.Group();
    
    // Create zigzag road pattern
    for (let i = 0; i < 5; i++) {
        const segmentGeo = new THREE.BoxGeometry(1, 0.2, 2);
        const segmentMat = new THREE.MeshPhongMaterial({ color: 0x333333 });
        const segment = new THREE.Mesh(segmentGeo, segmentMat);
        
        // Alternate left and right
        const offset = (i % 2 === 0) ? -1.5 : 1.5;
        segment.position.set(offset, 0.1, -i * 2);
        segment.rotation.y = (i % 2 === 0) ? 0.3 : -0.3;
        lombardGroup.add(segment);
        
        // Add flowers/bushes on sides
        const bushGeo = new THREE.SphereGeometry(0.3, 8, 8);
        const bushMat = new THREE.MeshPhongMaterial({ color: 0xFF69B4 }); // Pink flowers
        const bush1 = new THREE.Mesh(bushGeo, bushMat);
        bush1.position.set(offset - 0.8, 0.3, -i * 2);
        lombardGroup.add(bush1);
        
        const bush2 = new THREE.Mesh(bushGeo, bushMat);
        bush2.position.set(offset + 0.8, 0.3, -i * 2);
        lombardGroup.add(bush2);
    }
    
    lombardGroup.position.set(0, 0, -50);
    lombardGroup.isDecoration = true;
    lombardGroup.isLombard = true;
    
    scene.add(lombardGroup);
    landmarks.push(lombardGroup);
}

function spawnCableCarTurnaround() {
    // Cable car turnaround platform decoration
    const turnaroundGroup = new THREE.Group();
    
    // Circular platform
    const platformGeo = new THREE.CylinderGeometry(2, 2, 0.3, 16);
    const platformMat = new THREE.MeshPhongMaterial({ color: 0x8B7355 });
    const platform = new THREE.Mesh(platformGeo, platformMat);
    turnaroundGroup.add(platform);
    
    // Rails
    const railGeo = new THREE.TorusGeometry(1.5, 0.05, 8, 16);
    const railMat = new THREE.MeshPhongMaterial({ color: 0x888888 });
    const rail = new THREE.Mesh(railGeo, railMat);
    rail.rotation.x = Math.PI / 2;
    rail.position.y = 0.2;
    turnaroundGroup.add(rail);
    
    const side = Math.random() > 0.5 ? 6 : -6;
    turnaroundGroup.position.set(side, 0, -50);
    turnaroundGroup.isDecoration = true;
    
    scene.add(turnaroundGroup);
    landmarks.push(turnaroundGroup);
}

// --- GAME LOGIC ---
function update() {
    if (!gameActive) return;

    // 1. Hero Movement (Smooth Lerp)
    const targetX = (currentLane - 1) * LANE_WIDTH;
    hero.position.x += (targetX - hero.position.x) * 0.1; // Smooth slide

    // Jump Physics
    if (isJumping) {
        hero.position.y += 0.2;
        hero.rotation.x -= 0.1; // Flip
        if (hero.position.y > 2) isJumping = false;
    } else if (hero.position.y > 0) {
        hero.position.y -= 0.2;
        hero.rotation.x = 0;
    } else {
        // Keep rabbit on ground - no vertical bounce
        hero.position.y = 0;
        
        // Forward-leaning running pose - dynamic side-to-side motion
        const runTime = Date.now() * 0.003;
        hero.rotation.z = Math.sin(runTime * 2) * 0.05; // Slight side-to-side lean
        
        // Tilt entire body forward slightly to show running motion
        hero.rotation.x = -0.05; // Small forward lean
    }
    
    // Wag tail animation
    if (hero.tail) {
        hero.tail.rotation.y = Math.sin(Date.now() * 0.008) * 0.5;
    }
    
    // Handle invincibility
    if (invincible) {
        invincibilityTimer--;
        // Flash effect during invincibility
        hero.visible = Math.floor(Date.now() / 100) % 2 === 0;
        
        if (invincibilityTimer <= 0) {
            invincible = false;
            hero.visible = true;
        }
    }

    // 2. Move Obstacles
    obstacles.forEach((obj, index) => {
        obj.position.z += gameSpeed;

        // Collision Detection
        if (obj.position.z > -1 && obj.position.z < 1) { // Near player Z
            // Check Lane matches & Player is on ground (roughly)
            const laneDiff = Math.abs(obj.position.x - hero.position.x);
            if (laneDiff < 1 && hero.position.y < 1 && !invincible) {
                loseLife();
                // Remove the obstacle after hit
                scene.remove(obj);
                obstacles.splice(index, 1);
            }
        }

        // Remove if passed
        if (obj.position.z > 10) {
            scene.remove(obj);
            obstacles.splice(index, 1);
        }
    });

    // 3. Move Coins
    coins.forEach((obj, index) => {
        obj.position.z += gameSpeed;
        obj.rotation.y += 0.1; // Spin

        // Collection
        const laneDiff = Math.abs(obj.position.x - hero.position.x);
        const zDiff = Math.abs(obj.position.z - hero.position.z);

        if (zDiff < 1 && laneDiff < 1) {
            // Collected item!
            if (obj.itemType === 'task' || obj.isBonus) {
                // Task item OR Trophy - show random fact
                score += obj.isBonus ? 50 : 20;  // Trophy worth more!
                playSound('bonus');
                const randomFact = TASKRABBIT_FACTS[Math.floor(Math.random() * TASKRABBIT_FACTS.length)];
                showTaskMessage(randomFact);
            } else {
                // Regular dollar sign
                score += 10;
                playSound('collect');
                showTaskMessage("I got some tip!");
            }
            document.getElementById('score').innerText = score;
            scene.remove(obj);
            coins.splice(index, 1);
        }

        if (obj.position.z > 10) {
            scene.remove(obj);
            coins.splice(index, 1);
        }
    });

    // 4. Spawning Logic - Simplified (only essentials)
    const rand = Math.random();
    if (rand < 0.01) spawnObstacle(); // Traffic cones
    else if (rand < 0.015) spawnBARTTrain(); // Large traffic cones
    
    const collectRand = Math.random();
    if (collectRand < 0.012) spawnCoin(); // Dollar signs
    else if (collectRand < 0.016) spawnScrewdriver(); // Screwdriver task
    else if (collectRand < 0.020) spawnMop(); // Mop task
    else if (collectRand < 0.024) spawnIkeaBox(); // IKEA box task
    
    // SF Decorative elements on the sides
    const decorRand = Math.random();
    if (decorRand < 0.006) spawnStreetSign();
    else if (decorRand < 0.010) spawnCableCar();
    else if (decorRand < 0.013) spawnHillside();
    
    // 5. Move and cleanup landmarks (street signs, etc.)
    landmarks.forEach((obj, index) => {
        obj.position.z += gameSpeed;
        if (obj.position.z > 10) {
            scene.remove(obj);
            landmarks.splice(index, 1);
        }
    });
    
    // 6. Move and recycle buildings for continuous cityscape
    buildings.forEach((obj, index) => {
        obj.position.z += gameSpeed;
        if (obj.position.z > 10) {
            scene.remove(obj);
            buildings.splice(index, 1);
        }
    });
    
    // Spawn new building rows as needed for continuous cityscape
    if (buildings.length < 60) { // Keep ~10 rows of 6 buildings
        spawnBuildingRow(-50);
    }
    
    // Progressive difficulty
    if (score > 100 && gameSpeed < 0.5) {
        gameSpeed += 0.0001; // Gradual speed increase
    }
}

function animate() {
    requestAnimationFrame(animate);
    update();
    renderer.render(scene, camera);
}

function loseLife() {
    lives--;
    updateLivesDisplay();
    playSound('crash');
    
    // Shake effect
    document.getElementById('lives-box').classList.add('shake');
    setTimeout(() => {
        document.getElementById('lives-box').classList.remove('shake');
    }, 500);
    
    if (lives <= 0) {
        gameOver();
    } else {
        // Grant temporary invincibility (2 seconds = ~120 frames)
        invincible = true;
        invincibilityTimer = 120;
    }
}

function updateLivesDisplay() {
    const lifeElements = document.querySelectorAll('.life');
    lifeElements.forEach((life, index) => {
        if (index >= lives) {
            life.classList.add('lost');
        } else {
            life.classList.remove('lost');
        }
    });
}

function showTaskMessage(message) {
    // Show dynamic message bubble
    let messageDiv = document.getElementById('task-message');
    if (!messageDiv) {
        messageDiv = document.createElement('div');
        messageDiv.id = 'task-message';
        messageDiv.className = 'task-message';
        document.body.appendChild(messageDiv);
    }
    
    messageDiv.textContent = message || 'I got a task!';
    messageDiv.classList.add('show');
    
    // Hide after 2 seconds (slightly longer for reading facts)
    setTimeout(() => {
        messageDiv.classList.remove('show');
    }, 2000);
}

function gameOver() {
    gameActive = false;
    
    // Save score and redirect to lottery
    fetch('/save_score', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ score: score })
    })
    .then(response => response.json())
    .then(data => {
        if (data.redirect) {
            window.location.href = data.redirect;
        }
    })
    .catch(error => {
        console.error('Error saving score:', error);
        // Fallback: show game over screen
        document.getElementById('game-over').classList.remove('hidden');
        document.getElementById('final-score').innerText = score;
    });
}

function resetGame() {
    // Clear scene objects
    obstacles.forEach(o => scene.remove(o));
    coins.forEach(c => scene.remove(c));
    landmarks.forEach(l => scene.remove(l));
    buildings.forEach(b => scene.remove(b));
    obstacles = [];
    coins = [];
    landmarks = [];
    buildings = [];

    score = 0;
    lives = 3;
    invincible = false;
    invincibilityTimer = 0;
    document.getElementById('score').innerText = '0';
    updateLivesDisplay();
    document.getElementById('game-over').classList.add('hidden');
    
    // Re-initialize buildings
    for (let i = 0; i < 10; i++) {
        spawnBuildingRow(-10 - i * 8);
    }
    
    gameActive = true;
}

// --- CONTROLS ---
document.addEventListener('keydown', (e) => {
    if (!gameActive) return;

    if (e.key === 'ArrowLeft' && currentLane > 0) {
        currentLane--;
    } else if (e.key === 'ArrowRight' && currentLane < 2) {
        currentLane++;
    } else if (e.key === 'ArrowUp' && hero.position.y < 0.5) {
        isJumping = true;
        playSound('jump');
    }
});

// Start - wait for username modal if needed
if (typeof gameCanStart !== 'undefined' && gameCanStart) {
    init();
} else if (typeof gameCanStart === 'undefined') {
    // If variable doesn't exist, start immediately (for direct access)
    init();
}

// Resize Handler
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});