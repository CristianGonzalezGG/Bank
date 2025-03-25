// Inicialización de AOS (Animate On Scroll)
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar animaciones al hacer scroll
    AOS.init({
        duration: 1000,
        once: false,
        mirror: true,
        anchorPlacement: 'top-bottom'
    });

    // Configuración de partículas para el CTA final
    if (document.getElementById('particles-js')) {
        particlesJS('particles-js', {
            particles: {
                number: { value: 80, density: { enable: true, value_area: 800 } },
                color: { value: '#ffffff' },
                shape: { type: 'circle' },
                opacity: { value: 0.5, random: true },
                size: { value: 3, random: true },
                line_linked: { enable: true, distance: 150, color: '#ffffff', opacity: 0.4, width: 1 },
                move: { enable: true, speed: 2, direction: 'none', random: false, straight: false, out_mode: 'out', bounce: false }
            },
            interactivity: {
                detect_on: 'canvas',
                events: { onhover: { enable: true, mode: 'grab' }, onclick: { enable: true, mode: 'push' }, resize: true },
                modes: { grab: { distance: 140, line_linked: { opacity: 1 } }, push: { particles_nb: 4 } }
            },
            retina_detect: true
        });
    }
    
    // Inicialización de parallax para secciones con efecto de profundidad
    const sceneElements = document.querySelectorAll('.parallax-bg, .cards-floating-container, .parallax-container');
    sceneElements.forEach(el => {
        if (el) new Parallax(el);
    });
    
    // Efecto 3D para hover de tarjetas
    const cards = document.querySelectorAll('.card-3d-wrap');
    cards.forEach(card => {
        card.addEventListener('mousemove', e => {
            const cardWidth = card.offsetWidth;
            const cardHeight = card.offsetHeight;
            const centerX = card.offsetLeft + cardWidth/2;
            const centerY = card.offsetTop + cardHeight/2;
            const mouseX = e.clientX - centerX;
            const mouseY = e.clientY - centerY;
            const rotateY = 20 * mouseX / (cardWidth/2);
            const rotateX = -20 * mouseY / (cardHeight/2);
            
            card.querySelector('.card-3d-wrapper').style.transform = `rotateY(${rotateY}deg) rotateX(${rotateX}deg)`;
        });
        
        card.addEventListener('mouseout', () => {
            card.querySelector('.card-3d-wrapper').style.transform = 'rotateY(0deg) rotateX(0deg)';
        });
    });
    
    // Configuración de Three.js para el canvas de sección de control de app
    if (document.getElementById('app-control-canvas')) {
        setupThreeJsScene();
    }
    
    // Slider de tarjetas
    setupCardCarousel();
    
    // Animación del teléfono y app interface
    animateAppInterface();
    
    // Animación de header con scroll
    initHeaderAnimation();
    
    // Slider de testimonios
    initTestimonialsSlider();
});

// Función para el carrusel de tarjetas
function setupCardCarousel() {
    const carousel = document.querySelector('.card-carousel');
    if (!carousel) return;
    
    const items = carousel.querySelectorAll('.card-item');
    const dotsContainer = document.querySelector('.carousel-dots');
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');
    let currentIndex = 0;
    
    // Crear indicadores (dots)
    items.forEach((_, index) => {
        const dot = document.createElement('span');
        dot.classList.add('carousel-dot');
        if (index === 0) dot.classList.add('active');
        dot.addEventListener('click', () => goToSlide(index));
        dotsContainer.appendChild(dot);
    });
    
    // Función para actualizar la posición del carrusel
    function updateCarousel() {
        const slideWidth = items[0].offsetWidth + 20; // +20 por el margen
        carousel.style.transform = `translateX(-${currentIndex * slideWidth}px)`;
        
        // Actualizar dots
        document.querySelectorAll('.carousel-dot').forEach((dot, index) => {
            dot.classList.toggle('active', index === currentIndex);
        });
    }
    
    // Función para ir a un slide específico
    function goToSlide(index) {
        currentIndex = index;
        if (currentIndex < 0) currentIndex = items.length - 1;
        if (currentIndex >= items.length) currentIndex = 0;
        updateCarousel();
    }
    
    // Event listeners para botones
    prevBtn.addEventListener('click', () => goToSlide(currentIndex - 1));
    nextBtn.addEventListener('click', () => goToSlide(currentIndex + 1));
    
    // Inicializar carrusel
    updateCarousel();
    
    // Responsive: Reajustar carrusel al cambiar tamaño de ventana
    window.addEventListener('resize', updateCarousel);
    
    // Auto-rotación del carrusel (opcional)
    setInterval(() => {
        goToSlide(currentIndex + 1);
    }, 5000);
}

// Función para animar la interfaz de la app en el mockup
function animateAppInterface() {
    const appInterface = document.querySelector('.app-interface');
    if (!appInterface) return;
    
    // Secuencia de animación con GSAP
    const tl = gsap.timeline({repeat: -1, repeatDelay: 1});
    
    // Animación de la pantalla principal
    tl.to('.app-card-visual', {duration: 0.5, opacity: 1, scale: 1, ease: 'back.out'})
      .to('.app-toggle-button', {duration: 0.3, opacity: 1, x: 0, ease: 'power2.out'}, '-=0.2')
      .to('.app-toggle-button', {duration: 0.3, backgroundColor: '#4CAF50', ease: 'none'}, '+=0.5')
      .to('.app-toggle-button', {duration: 0.3, backgroundColor: '#F44336', ease: 'none'}, '+=1')
      .to('.app-menu-item', {duration: 0.3, opacity: 1, stagger: 0.1, ease: 'power1.out'}, '-=0.2')
      .to('.app-menu-item.active', {duration: 0.3, backgroundColor: '#007BFF', ease: 'none'}, '-=0.1')
      .to('.app-card-visual', {duration: 0.3, rotationY: 180, ease: 'power2.inOut'}, '+=0.5')
      .to('.app-card-visual', {duration: 0.3, rotationY: 0, ease: 'power2.inOut'}, '+=0.5');
}

// Escena 3D avanzada con Three.js
function setupThreeJsScene() {
    const canvas = document.getElementById('app-control-canvas');
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / (window.innerHeight * 0.6), 0.1, 1000);
    
    const renderer = new THREE.WebGLRenderer({
        canvas: canvas,
        alpha: true,
        antialias: true
    });
    renderer.setSize(window.innerWidth, window.innerHeight * 0.6);
    
    // Iluminación
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(10, 10, 10);
    scene.add(directionalLight);
    
    // Crear tarjeta 3D
    const cardGeometry = new THREE.BoxGeometry(5, 3, 0.1);
    const cardMaterial = new THREE.MeshStandardMaterial({
        color: 0x111111,
        metalness: 0.7,
        roughness: 0.2,
        emissive: 0x222222
    });
    
    const card = new THREE.Mesh(cardGeometry, cardMaterial);
    scene.add(card);
    
    // Crear chip dorado (simplificado sin usar TextGeometry)
    const chipGeometry = new THREE.BoxGeometry(0.8, 0.8, 0.05);
    const chipMaterial = new THREE.MeshStandardMaterial({
        color: 0xd4af37,
        metalness: 1,
        roughness: 0.2
    });
    
    const chip = new THREE.Mesh(chipGeometry, chipMaterial);
    chip.position.set(-1.5, 0.5, 0.1);
    card.add(chip);
    
    // Posición de la cámara
    camera.position.z = 5;
    
    // Animación
    function animate() {
        requestAnimationFrame(animate);
        
        // Rotación suave de la tarjeta
        card.rotation.y = Math.sin(Date.now() * 0.001) * 0.2;
        card.rotation.x = Math.cos(Date.now() * 0.001) * 0.1;
        
        renderer.render(scene, camera);
    }
    
    animate();
    
    // Responsive
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / (window.innerHeight * 0.6);
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight * 0.6);
    });
}

// Animaciones avanzadas para el header al scrollear
function initHeaderAnimation() {
    gsap.registerPlugin(ScrollTrigger);
    
    // Paralaje avanzado para la sección hero
    gsap.to('.parallax-bg', {
        y: '30%',
        ease: 'none',
        scrollTrigger: {
            trigger: '.hero-section',
            start: 'top top',
            end: 'bottom top',
            scrub: true
        }
    });
    
    // Animación de las tarjetas flotantes
    gsap.to('.floating-card.card-gold', {
        y: '-20%',
        x: '5%',
        rotationZ: -5,
        ease: 'none',
        scrollTrigger: {
            trigger: '.hero-section',
            start: 'top top',
            end: 'bottom top',
            scrub: true
        }
    });
    
    gsap.to('.floating-card.card-platinum', {
        y: '-15%',
        x: '-5%',
        rotationZ: 5,
        ease: 'none',
        scrollTrigger: {
            trigger: '.hero-section',
            start: 'top top',
            end: 'bottom top',
            scrub: true
        }
    });
    
    gsap.to('.floating-card.card-black', {
        y: '-10%',
        scale: 1.1,
        ease: 'none',
        scrollTrigger: {
            trigger: '.hero-section',
            start: 'top top',
            end: 'bottom top',
            scrub: true
        }
    });
    
    // Animación para sección de beneficios
    const benefitItems = document.querySelectorAll('.benefit-item');
    benefitItems.forEach((item, index) => {
        gsap.from(item, {
            opacity: 0,
            y: 50,
            duration: 0.8,
            ease: 'power2.out',
            scrollTrigger: {
                trigger: item,
                start: 'top 80%',
                toggleActions: 'play none none reverse'
            },
            delay: index * 0.2
        });
    });
}

// Función mejorada para el slider de testimonios
function initTestimonialsSlider() {
    const slider = document.querySelector('.testimonials-slider');
    if (!slider) return;
    
    const items = slider.querySelectorAll('.testimonial-item');
    const prevBtn = document.querySelector('.prev-testimonial');
    const nextBtn = document.querySelector('.next-testimonial');
    const indicators = document.querySelectorAll('.testimonial-indicator');
    let currentIndex = 0;
    
    // Mostrar el primer testimonio al cargar
    items[0].classList.add('active');
    
    // Función para mostrar un testimonio específico
    function showTestimonial(index) {
        // Actualizar clases active
        items.forEach(item => item.classList.remove('active'));
        items[index].classList.add('active');
        
        // Actualizar indicadores
        indicators.forEach(indicator => indicator.classList.remove('active'));
        indicators[index].classList.add('active');
    }
    
    // Event listeners para botones de navegación
    nextBtn.addEventListener('click', () => {
        currentIndex = (currentIndex + 1) % items.length;
        showTestimonial(currentIndex);
    });
    
    prevBtn.addEventListener('click', () => {
        currentIndex = (currentIndex - 1 + items.length) % items.length;
        showTestimonial(currentIndex);
    });
    
    // Event listeners para indicadores
    indicators.forEach((indicator, index) => {
        indicator.addEventListener('click', () => {
            currentIndex = index;
            showTestimonial(currentIndex);
        });
    });
    
    // Rotación automática cada 5 segundos
    setInterval(() => {
        currentIndex = (currentIndex + 1) % items.length;
        showTestimonial(currentIndex);
    }, 5000);
}