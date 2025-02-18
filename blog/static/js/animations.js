// Animaciones Globales
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar AOS (Animate On Scroll)
    AOS.init({
        duration: 800,
        once: true,
        offset: 100
    });

    // Inicializar animaciones de entrada
    initializeEntryAnimations();
    
    // Inicializar efectos parallax
    initializeParallax();
    
    // Inicializar animaciones de hover
    initializeHoverEffects();
});

// Función para animaciones de entrada
function initializeEntryAnimations() {
    const elements = document.querySelectorAll('.animate-on-entry');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in');
                observer.unobserve(entry.target);
            }
        });
    });

    elements.forEach(element => observer.observe(element));
}

// Función para efectos parallax
function initializeParallax() {
    const parallaxElements = document.querySelectorAll('.parallax');
    
    window.addEventListener('mousemove', (e) => {
        const { clientX, clientY } = e;
        const centerX = window.innerWidth / 2;
        const centerY = window.innerHeight / 2;
        
        parallaxElements.forEach(element => {
            const speed = element.getAttribute('data-speed') || 0.1;
            const x = (centerX - clientX) * speed;
            const y = (centerY - clientY) * speed;
            
            element.style.transform = `translate(${x}px, ${y}px)`;
        });
    });
}

// Función para efectos de hover
function initializeHoverEffects() {
    const cards = document.querySelectorAll('.card-hover-effect');
    
    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const { left, top } = card.getBoundingClientRect();
            const x = e.clientX - left;
            const y = e.clientY - top;
            
            card.style.setProperty('--x', `${x}px`);
            card.style.setProperty('--y', `${y}px`);
        });
    });
}

// Función para animaciones de botones
function initializeButtonAnimations() {
    const buttons = document.querySelectorAll('.btn-animated');
    
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const circle = document.createElement('div');
            circle.classList.add('ripple');
            
            this.appendChild(circle);
            
            const diameter = Math.max(this.clientWidth, this.clientHeight);
            circle.style.width = circle.style.height = `${diameter}px`;
            
            const rect = this.getBoundingClientRect();
            circle.style.left = `${e.clientX - rect.left - diameter/2}px`;
            circle.style.top = `${e.clientY - rect.top - diameter/2}px`;
            
            circle.addEventListener('animationend', () => circle.remove());
        });
    });
} 