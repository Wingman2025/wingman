// Add a from_json filter to Jinja2
if (typeof JSON.parse !== 'function') {
    JSON.parse = function(str) {
        return eval('(' + str + ')');
    };
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in');
        }, index * 100);
    });
    
    // Animate feature cards when they come into view
    const animateElements = document.querySelectorAll('.slide-up');
    
    if (animateElements.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animationPlayState = 'running';
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        animateElements.forEach(element => {
            element.style.animationPlayState = 'paused';
            observer.observe(element);
        });
    }
    
    // Add hover effect to CTA buttons
    const ctaButtons = document.querySelectorAll('.cta-button');
    ctaButtons.forEach(button => {
        button.addEventListener('mouseover', function() {
            this.style.transform = 'translateY(-3px)';
            this.style.boxShadow = '0 15px 30px rgba(0, 150, 199, 0.4)';
        });
        
        button.addEventListener('mouseout', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });
    
    // Add hover effect to feature icon wrappers
    const featureIconWrappers = document.querySelectorAll('.feature-icon-wrapper');
    featureIconWrappers.forEach(wrapper => {
        wrapper.addEventListener('mouseover', function() {
            this.style.transform = 'scale(1.1)';
            this.style.transition = 'transform 0.3s ease';
        });
        
        wrapper.addEventListener('mouseout', function() {
            this.style.transform = 'scale(1)';
        });
    });
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId !== '#') {
                document.querySelector(targetId).scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Add parallax effect to hero section
    const heroSection = document.querySelector('.hero-section');
    if (heroSection) {
        window.addEventListener('scroll', function() {
            const scrollPosition = window.scrollY;
            if (scrollPosition < 600) {
                heroSection.style.backgroundPosition = `center ${scrollPosition * 0.05}px`;
            }
        });
    }
    
    // Add wave animation interactivity
    const waveAnimation = document.querySelector('.wave-animation');
    if (waveAnimation) {
        heroSection.addEventListener('mousemove', function(e) {
            const xPos = e.clientX / window.innerWidth;
            const waves = document.querySelectorAll('.wave');
            
            waves.forEach((wave, index) => {
                const speed = 0.5 + (index * 0.1);
                const offset = 25 * xPos * speed;
                wave.style.transform = `translateX(-${offset}%)`;
            });
        });
        
        heroSection.addEventListener('mouseleave', function() {
            const waves = document.querySelectorAll('.wave');
            waves.forEach(wave => {
                wave.style.transform = '';
            });
        });
    }
});
