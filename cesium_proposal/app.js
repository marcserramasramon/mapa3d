import { hospitals, caps } from './data/locations.js';

// --- Initialization ---

if (typeof Cesium === 'undefined') {
    alert("FATAL ERROR: CesiumJS library not loaded. Check internet connection or script URL.");
    throw new Error("CesiumJS not loaded");
}

Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIwZWNhN2VjYS00ZTY0LTQ2ZDAtODFlZS1mMzE5NDJiYjMxZGYiLCJpZCI6MzkwNjgyLCJpYXQiOjE3NzExMDQwNjV9.OTolrf3RS_F7tU97LnSNDe1lKeAKXX2Nf6smKQgC5io';

let viewer;
try {
    // Attempting Basic Viewer with Token Defaults (Bing Maps + World Terrain)
    viewer = new Cesium.Viewer('cesiumContainer', {
        terrain: Cesium.Terrain.fromWorldTerrain(), // Updated API for v1.107+
        // Enable default widgets for debugging (BaseLayerPicker allows switching imagery)
        baseLayerPicker: true,
        geocoder: false,
        homeButton: false,
        infoBox: false,
        sceneModePicker: false,
        selectionIndicator: false,
        timeline: false,
        animation: false,
        navigationHelpButton: false,
        navigationInstructionsInitiallyVisible: false,
        shouldAnimate: true // CRITICAL: Required for SampledPositionProperty to animate
    });
} catch (e) {
    alert("Cesium Initialization Error: " + e.message);
    console.error(e);
}

if (!viewer) {
    throw new Error("Viewer not initialized");
}

viewer.cesiumWidget.creditContainer.style.display = "none";

// Initial View: Girona
viewer.camera.flyTo({
    destination: Cesium.Cartesian3.fromDegrees(2.8214, 41.9794, 60000),
    orientation: {
        heading: Cesium.Math.toRadians(0),
        pitch: Cesium.Math.toRadians(-50),
        roll: 0.0
    }
});

// --- State & Settings ---
const state = {
    simulationSpeed: 5,
    showCaps: true,
    showHospitals: true,
    showTraffic: true,
    showCivilians: false, // Default off
    activeAmbulances: 0,
    totalPatients: 0,
    erRate: 0
};

// --- Entity Management ---
const hospitalEntities = [];
const capEntities = [];
const civilianEntities = []; // Active Civilians
const connections = [];
let activeTrackers = []; // HUD Trackers

// ... (Entity Management) ...

// --- Civilian Simulation ---
function spawnCivilian() {
    if (!state.showCivilians) return;

    // Pick a random facility as destination
    const allFacilities = [...hospitalEntities, ...capEntities];
    const targetEntity = allFacilities[Math.floor(Math.random() * allFacilities.length)];
    const targetCoords = targetEntity.customData.coords;

    // Generate random start point within 0.02 degrees (~2km)
    const angle = Math.random() * Math.PI * 2;
    const distance = 0.005 + Math.random() * 0.015;
    const startLng = targetCoords[0] + Math.cos(angle) * distance;
    const startLat = targetCoords[1] + Math.sin(angle) * distance;

    const startPos = Cesium.Cartesian3.fromDegrees(startLng, startLat);
    const endPos = Cesium.Cartesian3.fromDegrees(targetCoords[0], targetCoords[1]);

    const duration = (90000 + Math.random() * 60000) / state.simulationSpeed; // Base 1.5 - 2.5 mins
    const startTime = Cesium.JulianDate.now();
    const stopTime = Cesium.JulianDate.addSeconds(startTime, duration / 1000, new Cesium.JulianDate());

    const positionProperty = new Cesium.SampledPositionProperty();
    positionProperty.addSample(startTime, startPos);
    positionProperty.addSample(stopTime, endPos);

    // White Flag Icon (SVG Data URI)
    const flagIcon = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJ3aGl0ZSIgc3Ryb2tlPSJibGFjayIgc3Ryb2tlLXdpZHRoPSIxIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik00IDE1czEtMSA0LTEgNSAyIDggMiA0LTEgNC0xVjNzLTEgMS00IDEtNS0yLTgtMi00IDEtNCAxeiI+PC9wYXRoPjxsaW5lIHgxPSI0IiB5MT0iMjIiIHgyPSI0IiB5Mj0iMTUiPjwvbGluZT48L3N2Zz4=";

    const entity = viewer.entities.add({
        position: positionProperty,
        orientation: new Cesium.VelocityOrientationProperty(positionProperty),
        billboard: {
            image: flagIcon,
            scale: 1.2,
            verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
            heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
            disableDepthTestDistance: Number.POSITIVE_INFINITY // Always visible on top
        },
        path: {
            resolution: 1,
            material: new Cesium.PolylineDashMaterialProperty({
                color: Cesium.Color.WHITE.withAlpha(0.5),
                dashLength: 8.0
            }),
            width: 2,
            leadTime: 0,
            trailTime: 0.5,
            clampToGround: true
        }
    });

    civilianEntities.push(entity);

    setTimeout(() => {
        viewer.entities.remove(entity);
        const idx = civilianEntities.indexOf(entity);
        if (idx > -1) civilianEntities.splice(idx, 1);
    }, duration);
}

// ... (Existing spawnReferral) ...

// --- Entity Management (Functions) ---

function createFacilityEntity(id, data, isHospital) {
    const color = isHospital ? Cesium.Color.RED : Cesium.Color.CYAN;
    // MUCH Larger Sizes:
    // Hospital: Radius ~250m, Base Height ~1200m
    // CAP: Radius ~150m, Base Height ~400m
    const baseRadius = isHospital ? 250 : 150;
    const heightMultiplier = isHospital ? 50 : 20;

    // Scale pixel size by patient load (simple visualization)
    const loadScale = 1 + (data.patients / data.capacity);

    const entity = viewer.entities.add({
        id: id,
        position: Cesium.Cartesian3.fromDegrees(data.coords[0], data.coords[1]),
        cylinder: {
            length: heightMultiplier * 20 * loadScale, // Approx 1000m - 2000m range
            topRadius: baseRadius * loadScale,
            bottomRadius: baseRadius * loadScale,
            material: color,
            outline: true,
            outlineColor: Cesium.Color.WHITE,
            outlineWidth: 1,
            heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
        },
        label: {
            text: data.name,
            font: isHospital ? "14pt monospace" : "10pt monospace",
            style: Cesium.LabelStyle.FILL_AND_OUTLINE,
            outlineWidth: 2,
            verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
            // Use baseRadius for offset, as size is no longer defined
            pixelOffset: new Cesium.Cartesian2(0, -baseRadius * loadScale),
            scaleByDistance: new Cesium.NearFarScalar(1.5e2, 1.5, 8.0e6, 0.0),
            heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
        },
        description: `
            <h3>${data.name}</h3>
            <p>Role: ${data.role || "Primary Care"}</p>
            <p>Patients: <span id="info-patients">${data.patients}</span> / ${data.capacity}</p>
        `
    });

    // Store custom data for simulation
    entity.customData = { ...data, type: isHospital ? 'hospital' : 'cap' };

    return entity;
}

function createConnectionLine(id, startCoords, endCoords, color) {
    const start = Cesium.Cartesian3.fromDegrees(startCoords[0], startCoords[1]);
    const end = Cesium.Cartesian3.fromDegrees(endCoords[0], endCoords[1]);

    // SKY HIGHWAY: Corridor at 3000m with 100m width
    const entity = viewer.entities.add({
        id: id,
        corridor: {
            positions: [start, end],
            height: 3000.0,
            width: 100.0,
            material: new Cesium.ColorMaterialProperty(color.withAlpha(0.1)),
            outline: true,
            outlineColor: color.withAlpha(0.3)
        }
    });
    connections.push(entity);
}

// Load Entities
Object.entries(hospitals).forEach(([id, data]) => {
    hospitalEntities.push(createFacilityEntity(id, data, true));
});

Object.entries(caps).forEach(([id, data]) => {
    capEntities.push(createFacilityEntity(id, data, false));

    // Create connection to parent
    if (data.parent && hospitals[data.parent]) {
        createConnectionLine(
            `conn-cap-${id}-${data.parent}`,
            data.coords,
            hospitals[data.parent].coords,
            Cesium.Color.YELLOW
        );
    }
});

// Create Full Mesh between Hospitals (Inter-Hospital Network)
for (let i = 0; i < hospitalEntities.length; i++) {
    for (let j = i + 1; j < hospitalEntities.length; j++) {
        const h1 = hospitalEntities[i];
        const h2 = hospitalEntities[j];
        createConnectionLine(
            `conn-hosp-${h1.id}-${h2.id}`,
            h1.customData.coords,
            h2.customData.coords,
            Cesium.Color.CYAN // Distinct color for backbone
        );
    }
}

// --- Simulation Logic ---

function getLoadColor(percentage) {
    if (percentage < 0.5) return Cesium.Color.fromCssColorString('#00ff00'); // Green
    if (percentage < 0.8) return Cesium.Color.fromCssColorString('#ffff00'); // Yellow
    return Cesium.Color.fromCssColorString('#ff0000'); // Red
}

function updatePatientLoads() {
    // Randomly fluctuate patient numbers
    [...hospitalEntities, ...capEntities].forEach(entity => {
        const change = Math.floor(Math.random() * 5) - 2; // -2 to +2
        let newCount = entity.customData.patients + change;
        if (newCount < 0) newCount = 0;

        entity.customData.patients = newCount;
        const capacity = entity.customData.capacity;
        const percentage = newCount / capacity;

        // Visual update (cylinder size and COLOR)
        const baseRadius = entity.customData.type === 'hospital' ? 250 : 150;
        const heightMultiplier = entity.customData.type === 'hospital' ? 50 : 20;
        const loadScale = 1 + percentage;

        entity.cylinder.length = heightMultiplier * 20 * loadScale;
        entity.cylinder.topRadius = baseRadius * loadScale;
        entity.cylinder.bottomRadius = baseRadius * loadScale;
        entity.cylinder.material = getLoadColor(percentage);
    });
}

function spawnReferral() {
    if (!state.showTraffic) return;

    const startEntity = capEntities[Math.floor(Math.random() * capEntities.length)];
    let targetId = startEntity.customData.parent || "HJT";
    let targetEntity = hospitalEntities.find(e => e.id === targetId);
    if (!targetEntity) targetEntity = hospitalEntities[0];

    // PULSE EFFECT on the connection line
    const connectionId = `conn-cap-${startEntity.id}-${targetId}`;
    const connectionEntity = viewer.entities.getById(connectionId);

    if (connectionEntity && connectionEntity.corridor) {
        // Flash to bright yellow
        connectionEntity.corridor.material = new Cesium.ColorMaterialProperty(Cesium.Color.YELLOW.withAlpha(0.8));

        // Revert after 500ms
        setTimeout(() => {
            if (viewer.entities.getById(connectionId)) {
                connectionEntity.corridor.material = new Cesium.ColorMaterialProperty(Cesium.Color.YELLOW.withAlpha(0.1));
            }
        }, 500);
    }

    // Height offset for visualization (Above the Sky Highway)
    const flightHeight = 3100;

    // Start/End with height
    const startPos = Cesium.Cartesian3.fromDegrees(startEntity.customData.coords[0], startEntity.customData.coords[1], flightHeight);
    const endPos = Cesium.Cartesian3.fromDegrees(targetEntity.customData.coords[0], targetEntity.customData.coords[1], flightHeight);

    // Slower Speed: Base 60s (1 min) instead of 10s
    const duration = 60000 / state.simulationSpeed;
    const startTime = Cesium.JulianDate.now();
    const stopTime = Cesium.JulianDate.addSeconds(startTime, duration / 1000, new Cesium.JulianDate());

    const positionProperty = new Cesium.SampledPositionProperty();
    positionProperty.addSample(startTime, startPos);
    positionProperty.addSample(stopTime, endPos);

    // Generate random patient data
    const pathologies = ["Trauma", "Cardíac", "Respiratori", "Ictus", "Sèpsia", "Pediatria"];
    const pathology = pathologies[Math.floor(Math.random() * pathologies.length)];
    const urgency = Math.floor(Math.random() * 5) + 1; // 1-5
    const urgencyColors = ['#00ff00', '#adff2f', '#ffff00', '#ffa500', '#ff0000'];
    const urgencyColor = Cesium.Color.fromCssColorString(urgencyColors[urgency - 1]);

    // Extended Data for Detail View
    const names = ["Maria G.", "Joan P.", "Anna M.", "Jordi L.", "Laura T.", "Marc R.", "Carme S.", "Pau B."];
    const patientName = names[Math.floor(Math.random() * names.length)];
    const patientAge = Math.floor(Math.random() * 80) + 5;
    const patientID = "PAC-" + Math.floor(Math.random() * 10000);

    let entityOptions = {
        position: positionProperty,
        orientation: new Cesium.VelocityOrientationProperty(positionProperty),
        // Tracked by HUD, no 3D label/cylinder needed
    };

    if (state.trafficStyle === 'ambulance') {
        entityOptions.model = {
            uri: 'https://cesium.com/public/Sandcastle/SampleData/models/CesiumAir/Cesium_Air.glb',
            minimumPixelSize: 64,
            scale: 1.0,
        };
        entityOptions.path = {
            resolution: 1,
            material: new Cesium.PolylineGlowMaterialProperty({
                glowPower: 0.2,
                color: urgencyColor
            }),
            width: 4,
            leadTime: 0,
            trailTime: duration,
        };
    } else {
        // Particle Style
        entityOptions.point = {
            pixelSize: 12,
            color: urgencyColor,
            outlineColor: Cesium.Color.WHITE,
            outlineWidth: 2,
        };
        entityOptions.path = {
            resolution: 0.5,
            material: new Cesium.PolylineGlowMaterialProperty({
                glowPower: 0.2,
                color: urgencyColor
            }),
            width: 6,
            leadTime: 0,
            trailTime: 1.5,
        };
    }

    const referralEntity = viewer.entities.add(entityOptions);

    // --- HUD INTEGRATION ---
    const hudContainer = document.getElementById('hud-top-bar');
    const svgLayer = document.getElementById('connections-layer');

    // Create Card
    const card = document.createElement('div');
    card.className = 'patient-card';
    card.innerHTML = `<strong>${pathology}</strong><br>Urgència: ${urgency}`;
    card.style.borderLeft = `5px solid ${urgencyColors[urgency - 1]}`;
    card.style.cursor = 'pointer'; // Make it look clickable

    // CLICK HANDLER for Detail View
    card.addEventListener('click', () => {
        const overlay = document.getElementById('patient-detail-overlay');
        document.getElementById('detail-id').innerText = patientID;
        document.getElementById('detail-id').style.color = urgencyColors[urgency - 1]; // Color code title
        document.getElementById('detail-name').innerText = patientName;
        document.getElementById('detail-age').innerText = patientAge + " anys";
        document.getElementById('detail-pathology').innerText = pathology;
        document.getElementById('detail-urgency').innerText = urgency;
        document.getElementById('detail-origin').innerText = startEntity.customData.name;
        document.getElementById('detail-dest').innerText = targetEntity.customData.name;

        overlay.classList.remove('hidden');
    });

    hudContainer.appendChild(card);

    // Create SVG Line
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('stroke', urgencyColors[urgency - 1]);
    line.setAttribute('stroke-width', '2');
    line.setAttribute('stroke-dasharray', '5,5'); // Dashed line
    svgLayer.appendChild(line);

    // Add to tracking list
    const tracker = { entity: referralEntity, card: card, line: line };
    activeTrackers.push(tracker);

    state.activeAmbulances++;

    setTimeout(() => {
        viewer.entities.remove(referralEntity);
        // Cleanup HUD
        if (card.parentNode) card.parentNode.removeChild(card);
        if (line.parentNode) line.parentNode.removeChild(line);
        activeTrackers = activeTrackers.filter(t => t !== tracker);

        state.activeAmbulances--;
    }, duration);
}


// Stats Update
function updateStats() {
    // Aggregate Total Patients
    let total = 0;
    [...hospitalEntities, ...capEntities].forEach(e => total += e.customData.patients);
    state.totalPatients = total;

    // Update DOM
    document.getElementById('total-patients').innerText = state.totalPatients;
    document.getElementById('active-ambulances').innerText = state.activeAmbulances;

    // Simulated ER Rate
    const rate = Math.floor(Math.random() * 20) + 50;
    document.getElementById('er-rate').innerText = rate + "/h";
}


// Game Loop
setInterval(() => {
    updatePatientLoads();
    updateStats();

    // Chance to spawn referral based on speed (increased probability)
    // was 0.1, increasing to 0.3 for better visibility
    if (Math.random() < (state.simulationSpeed * 0.3)) {
        spawnReferral();
    }

    // Spawn Civilians (Higher rate because they are local)
    if (state.showCivilians && Math.random() < (state.simulationSpeed * 0.5)) {
        spawnCivilian();
    }

}, 1000); // 1 second tick

// --- Interaction Handlers ---

// Settings
document.getElementById('toggle-caps').addEventListener('change', (e) => {
    state.showCaps = e.target.checked;
    capEntities.forEach(e => e.show = state.showCaps);
});

document.getElementById('toggle-hospitals').addEventListener('change', (e) => {
    state.showHospitals = e.target.checked;
    hospitalEntities.forEach(e => e.show = state.showHospitals);
});

document.getElementById('toggle-traffic').addEventListener('change', (e) => {
    state.showTraffic = e.target.checked;
    // Toggle existing trackers (Ambulances/Dots)
    activeTrackers.forEach(t => t.entity.show = state.showTraffic);
});

document.getElementById('toggle-civilians').addEventListener('change', (e) => {
    state.showCivilians = e.target.checked;
    // Toggle existing civilians
    civilianEntities.forEach(e => e.show = state.showCivilians);
});

document.getElementById('toggle-arcs').addEventListener('change', (e) => {
    // Toggles the Sky Highway Corridors
    const show = e.target.checked;
    connections.forEach(e => e.show = show);
});

document.getElementById('traffic-style').addEventListener('change', (e) => {
    state.trafficStyle = e.target.value;
});

document.getElementById('map-style').addEventListener('change', (e) => {
    const style = e.target.value;
    viewer.imageryLayers.removeAll();

    if (style === 'osm') {
        viewer.imageryLayers.addImageryProvider(new Cesium.OpenStreetMapImageryProvider({
            url: 'https://a.tile.openstreetmap.org/'
        }));
    } else {
        // Default to Ion World Imagery (Satellite)
        viewer.imageryLayers.addImageryProvider(Cesium.createWorldImagery());
    }
});

document.getElementById('sim-speed').addEventListener('input', (e) => {
    state.simulationSpeed = parseFloat(e.target.value);
});


// Picking
const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);
handler.setInputAction(function (movement) {
    const pickedObject = viewer.scene.pick(movement.position);
    if (Cesium.defined(pickedObject) && pickedObject.id && pickedObject.id.customData) {
        const data = pickedObject.id.customData;
        const infoDiv = document.getElementById('entity-info');
        const contentDiv = document.getElementById('info-content');

        infoDiv.classList.remove('hidden');
        contentDiv.innerHTML = `
            <strong>${data.name}</strong><br>
            Role: ${data.role || "CAP"}<br>
            Patients: ${data.patients} / ${data.capacity}<br>
            Parent: ${data.parent || "None"}
        `;
    } else {
        document.getElementById('entity-info').classList.add('hidden');
    }
}, Cesium.ScreenSpaceEventType.LEFT_CLICK);

// --- HUD Update Loop (Sync SVG lines) ---
viewer.scene.postRender.addEventListener(function () {
    const scene = viewer.scene;

    activeTrackers.forEach(tracker => {
        const entity = tracker.entity;
        const position = entity.position.getValue(viewer.clock.currentTime);

        if (position) {
            const canvasPosition = Cesium.SceneTransforms.wgs84ToWindowCoordinates(scene, position);

            if (canvasPosition) {
                // Get Card Position (Bottom Center)
                const cardRect = tracker.card.getBoundingClientRect();
                const startX = cardRect.left + (cardRect.width / 2);
                const startY = cardRect.bottom;

                // Update SVG Line
                tracker.line.setAttribute('x1', startX);
                tracker.line.setAttribute('y1', startY);
                tracker.line.setAttribute('x2', canvasPosition.x);
                tracker.line.setAttribute('y2', canvasPosition.y);
                tracker.line.style.display = 'block';
            } else {
                tracker.line.style.display = 'none'; // Off screen
            }
        }
    });
});
