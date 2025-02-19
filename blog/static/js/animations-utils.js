// Utilidades de animación reutilizables
const AnimationUtils = {
    // Efecto de partículas interactivas
    initParticles: (containerId, options = {}) => {
        const defaults = {
            particleCount: 50,
            connectParticles: true,
            responsiveBreakpoint: 768,
            color: '#ffffff',
            minDistance: 120,
            speed: 1
        };

        const settings = { ...defaults, ...options };
        const container = document.getElementById(containerId);
        if (!container) return;

        particlesJS(containerId, {
            particles: {
                number: {
                    value: settings.particleCount,
                    density: {
                        enable: true,
                        value_area: 800
                    }
                },
                color: {
                    value: settings.color
                },
                shape: {
                    type: "circle"
                },
                opacity: {
                    value: 0.5,
                    random: false
                },
                size: {
                    value: 3,
                    random: true
                },
                line_linked: {
                    enable: settings.connectParticles,
                    distance: settings.minDistance,
                    color: settings.color,
                    opacity: 0.4,
                    width: 1
                },
                move: {
                    enable: true,
                    speed: settings.speed,
                    direction: "none",
                    random: true,
                    straight: false,
                    out_mode: "out",
                    bounce: false
                }
            },
            interactivity: {
                detect_on: "canvas",
                events: {
                    onhover: {
                        enable: true,
                        mode: "grab"
                    },
                    onclick: {
                        enable: true,
                        mode: "push"
                    },
                    resize: true
                },
                modes: {
                    grab: {
                        distance: 140,
                        line_linked: {
                            opacity: 1
                        }
                    },
                    push: {
                        particles_nb: 4
                    }
                }
            },
            retina_detect: true
        });
    },

    // Efecto de texto con revelación
    initTextReveal: (elements) => {
        const options = {
            root: null,
            threshold: 0.1
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('reveal-text');
                    observer.unobserve(entry.target);
                }
            });
        }, options);

        elements.forEach(el => observer.observe(el));
    },

    // Efecto de hover 3D
    init3DHover: (element) => {
        element.addEventListener('mousemove', (e) => {
            const { left, top, width, height } = element.getBoundingClientRect();
            const x = (e.clientX - left) / width;
            const y = (e.clientY - top) / height;
            
            const tiltX = (y - 0.5) * 20;
            const tiltY = (x - 0.5) * 20;
            
            element.style.transform = `perspective(1000px) rotateX(${tiltX}deg) rotateY(${tiltY}deg) scale3d(1.05, 1.05, 1.05)`;
        });

        element.addEventListener('mouseleave', () => {
            element.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)';
        });
    },

    // Efecto de carga progresiva
    initProgressiveLoad: () => {
        const images = document.querySelectorAll('.progressive-load');
        const options = {
            root: null,
            threshold: 0.1
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('loaded');
                    observer.unobserve(entry.target);
                }
            });
        }, options);

        images.forEach(img => observer.observe(img));
    },

    // Efecto de scroll suave
    initSmoothScroll: () => {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            });
        });
    }
};

// Exportar para uso en otros archivos
window.AnimationUtils = AnimationUtils; 