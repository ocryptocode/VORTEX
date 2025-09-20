// 3D Scene Variables
let scene, camera, renderer, controls;
let village, trees, particles;
let animationId;

// Navigation and UI
let currentSection = 'home';
let isMenuOpen = false;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    init3DScene();
    initNavigation();
    initAnimations();
    initCounters();
    initMobileMenu();
});

// 3D Scene Initialization
function init3DScene() {
    const container = document.getElementById('scene-container');
    
    // Scene setup
    scene = new THREE.Scene();
    scene.fog = new THREE.Fog(0x0a0a0a, 50, 200);
    
    // Camera setup
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 10, 20);
    
    // Renderer setup
    renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setClearColor(0x0a0a0a, 0);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(renderer.domElement);
    
    // Controls
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.maxPolarAngle = Math.PI / 2;
    controls.minDistance = 10;
    controls.maxDistance = 50;
    
    // Lighting
    setupLighting();
    
    // Create village environment
    createVillage();
    createTrees();
    createParticles();
    
    // Start animation loop
    animate();
    
    // Handle window resize
    window.addEventListener('resize', onWindowResize);
}

// Setup lighting for the 3D scene
function setupLighting() {
    // Ambient light
    const ambientLight = new THREE.AmbientLight(0x404040, 0.3);
    scene.add(ambientLight);
    
    // Main directional light (moonlight)
    const directionalLight = new THREE.DirectionalLight(0x00d4ff, 0.8);
    directionalLight.position.set(20, 20, 10);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    directionalLight.shadow.camera.near = 0.5;
    directionalLight.shadow.camera.far = 50;
    directionalLight.shadow.camera.left = -25;
    directionalLight.shadow.camera.right = 25;
    directionalLight.shadow.camera.top = 25;
    directionalLight.shadow.camera.bottom = -25;
    scene.add(directionalLight);
    
    // Point lights for village glow
    const pointLight1 = new THREE.PointLight(0x00d4ff, 1, 30);
    pointLight1.position.set(0, 5, 0);
    scene.add(pointLight1);
    
    const pointLight2 = new THREE.PointLight(0xff6b6b, 0.8, 25);
    pointLight2.position.set(-10, 3, 5);
    scene.add(pointLight2);
    
    const pointLight3 = new THREE.PointLight(0x4ecdc4, 0.8, 25);
    pointLight3.position.set(10, 3, -5);
    scene.add(pointLight3);
}

// Create village structures
function createVillage() {
    village = new THREE.Group();
    
    // Central building (main structure)
    const centralGeometry = new THREE.BoxGeometry(8, 6, 8);
    const centralMaterial = new THREE.MeshPhongMaterial({ 
        color: 0x1a1a2e,
        transparent: true,
        opacity: 0.9
    });
    const centralBuilding = new THREE.Mesh(centralGeometry, centralMaterial);
    centralBuilding.position.y = 3;
    centralBuilding.castShadow = true;
    centralBuilding.receiveShadow = true;
    village.add(centralBuilding);
    
    // Add glowing windows
    for (let i = 0; i < 4; i++) {
        const windowGeometry = new THREE.PlaneGeometry(1, 1.5);
        const windowMaterial = new THREE.MeshBasicMaterial({ 
            color: 0x00d4ff,
            transparent: true,
            opacity: 0.8
        });
        const window = new THREE.Mesh(windowGeometry, windowMaterial);
        window.position.set(
            i < 2 ? (i === 0 ? -4.1 : 4.1) : 0,
            2,
            i >= 2 ? (i === 2 ? -4.1 : 4.1) : 0
        );
        window.rotation.y = i < 2 ? (i === 0 ? Math.PI / 2 : -Math.PI / 2) : (i === 2 ? 0 : Math.PI);
        village.add(window);
    }
    
    // Surrounding smaller buildings
    for (let i = 0; i < 6; i++) {
        const angle = (i / 6) * Math.PI * 2;
        const radius = 15;
        
        const buildingGeometry = new THREE.BoxGeometry(3, 4, 3);
        const buildingMaterial = new THREE.MeshPhongMaterial({ 
            color: 0x16213e,
            transparent: true,
            opacity: 0.8
        });
        const building = new THREE.Mesh(buildingGeometry, buildingMaterial);
        building.position.set(
            Math.cos(angle) * radius,
            2,
            Math.sin(angle) * radius
        );
        building.castShadow = true;
        building.receiveShadow = true;
        village.add(building);
        
        // Add small glowing lights
        const lightGeometry = new THREE.SphereGeometry(0.2, 8, 8);
        const lightMaterial = new THREE.MeshBasicMaterial({ 
            color: 0x00d4ff,
            transparent: true,
            opacity: 0.9
        });
        const light = new THREE.Mesh(lightGeometry, lightMaterial);
        light.position.set(
            Math.cos(angle) * radius,
            4.5,
            Math.sin(angle) * radius
        );
        village.add(light);
    }
    
    // Ground plane
    const groundGeometry = new THREE.PlaneGeometry(100, 100);
    const groundMaterial = new THREE.MeshPhongMaterial({ 
        color: 0x0a0a0a,
        transparent: true,
        opacity: 0.8
    });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    village.add(ground);
    
    scene.add(village);
}

// Create 3D trees around the village
function createTrees() {
    trees = new THREE.Group();
    
    for (let i = 0; i < 20; i++) {
        const tree = createTree();
        const angle = Math.random() * Math.PI * 2;
        const radius = 20 + Math.random() * 30;
        
        tree.position.set(
            Math.cos(angle) * radius,
            0,
            Math.sin(angle) * radius
        );
        tree.scale.setScalar(0.5 + Math.random() * 0.5);
        trees.add(tree);
    }
    
    scene.add(trees);
}

// Create individual tree
function createTree() {
    const tree = new THREE.Group();
    
    // Trunk
    const trunkGeometry = new THREE.CylinderGeometry(0.3, 0.5, 4, 8);
    const trunkMaterial = new THREE.MeshPhongMaterial({ color: 0x4a3728 });
    const trunk = new THREE.Mesh(trunkGeometry, trunkMaterial);
    trunk.position.y = 2;
    trunk.castShadow = true;
    tree.add(trunk);
    
    // Leaves
    const leavesGeometry = new THREE.SphereGeometry(2, 8, 6);
    const leavesMaterial = new THREE.MeshPhongMaterial({ 
        color: 0x2d5016,
        transparent: true,
        opacity: 0.8
    });
    const leaves = new THREE.Mesh(leavesGeometry, leavesMaterial);
    leaves.position.y = 5;
    leaves.castShadow = true;
    tree.add(leaves);
    
    return tree;
}

// Create particle system for atmosphere
function createParticles() {
    const particleCount = 1000;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    
    for (let i = 0; i < particleCount * 3; i++) {
        positions[i] = (Math.random() - 0.5) * 200;
    }
    
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    
    const material = new THREE.PointsMaterial({
        color: 0x00d4ff,
        size: 0.5,
        transparent: true,
        opacity: 0.6
    });
    
    particles = new THREE.Points(geometry, material);
    scene.add(particles);
}

// Animation loop
function animate() {
    animationId = requestAnimationFrame(animate);
    
    // Rotate village slowly
    if (village) {
        village.rotation.y += 0.001;
    }
    
    // Rotate trees
    if (trees) {
        trees.children.forEach((tree, index) => {
            tree.rotation.y += 0.002 + (index * 0.0001);
        });
    }
    
    // Rotate particles
    if (particles) {
        particles.rotation.y += 0.0005;
    }
    
    // Update controls
    controls.update();
    
    // Render scene
    renderer.render(scene, camera);
}

// Handle window resize
function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

// Navigation functionality
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.section');
    
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetSection = link.getAttribute('href').substring(1);
            showSection(targetSection);
            
            // Update active nav link
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        });
    });
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Show specific section
function showSection(sectionId) {
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => {
        section.classList.remove('active');
    });
    
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
        currentSection = sectionId;
    }
}

// Initialize counter animations
function initCounters() {
    const counters = document.querySelectorAll('.stat-number');
    
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px 0px -100px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    counters.forEach(counter => {
        observer.observe(counter);
    });
}

// Animate counter numbers
function animateCounter(element) {
    const target = parseInt(element.getAttribute('data-target'));
    const duration = 2000;
    const start = performance.now();
    
    function updateCounter(currentTime) {
        const elapsed = currentTime - start;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = Math.floor(progress * target);
        element.textContent = current.toLocaleString();
        
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        }
    }
    
    requestAnimationFrame(updateCounter);
}

// Initialize mobile menu
function initMobileMenu() {
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', () => {
            isMenuOpen = !isMenuOpen;
            navMenu.classList.toggle('active');
            navToggle.classList.toggle('active');
        });
        
        // Close menu when clicking on a link
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('active');
                navToggle.classList.remove('active');
                isMenuOpen = false;
            });
        });
    }
}

// Initialize other animations
function initAnimations() {
    // Add floating animation to cards
    const cards = document.querySelectorAll('.about-card, .presale-card, .collab-card');
    
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in-up');
    });
    
    // Add CSS for fade-in animation
    const style = document.createElement('style');
    style.textContent = `
        .fade-in-up {
            animation: fadeInUp 0.6s ease-out forwards;
            opacity: 0;
            transform: translateY(30px);
        }
        
        @keyframes fadeInUp {
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    `;
    document.head.appendChild(style);
}

// Handle scroll effects
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const parallax = scrolled * 0.5;
    
    // Parallax effect for 3D scene
    if (village) {
        village.position.y = -parallax * 0.1;
    }
    
    // Update camera position based on scroll
    if (camera) {
        camera.position.y = 10 + scrolled * 0.01;
    }
});

// Add interactive hover effects for 3D objects
function addInteractivity() {
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    
    function onMouseMove(event) {
        mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
        
        raycaster.setFromCamera(mouse, camera);
        
        // Check intersections with village buildings
        if (village) {
            const intersects = raycaster.intersectObjects(village.children, true);
            
            if (intersects.length > 0) {
                document.body.style.cursor = 'pointer';
                // Add glow effect to hovered object
                intersects[0].object.material.emissive = new THREE.Color(0x00d4ff);
                intersects[0].object.material.emissiveIntensity = 0.2;
            } else {
                document.body.style.cursor = 'default';
                // Reset emissive properties
                village.traverse((child) => {
                    if (child.material) {
                        child.material.emissive = new THREE.Color(0x000000);
                        child.material.emissiveIntensity = 0;
                    }
                });
            }
        }
    }
    
    window.addEventListener('mousemove', onMouseMove);
}

// Initialize interactivity after scene is loaded
setTimeout(addInteractivity, 1000);

// Performance optimization: pause animations when tab is not visible
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        if (animationId) {
            cancelAnimationFrame(animationId);
        }
    } else {
        animate();
    }
});

// Add loading screen
window.addEventListener('load', () => {
    const loader = document.querySelector('.loader');
    if (loader) {
        loader.style.opacity = '0';
        setTimeout(() => {
            loader.style.display = 'none';
        }, 500);
    }
});

// Export functions for potential external use
window.VortexVillage = {
    showSection,
    init3DScene,
    animate
};
