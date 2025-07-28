// Initialize AOS (Animate On Scroll)
AOS.init({
    duration: 1000,
    easing: 'ease-out-cubic',
    once: false,
    mirror: true
});
document.addEventListener('DOMContentLoaded', function() {
    AOS.init({
        duration: 800,
        easing: 'ease-in-out',
        once: true
    });
    
    // Mobile menu toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.navbar-nav');
    
    menuToggle.addEventListener('click', () => {
        navLinks.classList.toggle('active');
    });
});
// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { 
            opacity: 0;
            transform: translateY(10px);
        }
        to { 
            opacity: 1;
            transform: translateY(0);
        }
    }

    .card, .hero, .skill-tag {
        --mouse-x: 50%;
        --mouse-y: 50%;
    }
`;
document.head.appendChild(style);

// Main initialization
document.addEventListener('DOMContentLoaded', () => {
    // Get DOM elements
    const hero = document.querySelector('.hero');
    const heroContent = document.querySelector('.hero-content');
    const cards = document.querySelectorAll('.card');
    const skillTags = document.querySelectorAll('.skill-tag');
    const heroTitle = document.querySelector('.hero-text');
    const navbar = document.querySelector('.navbar');
    let lastScroll = 0;

    // Update CSS variables based on cursor position
    const handleMouseMove = (element, event) => {
        const rect = element.getBoundingClientRect();
        const x = ((event.clientX - rect.left) / rect.width) * 100;
        const y = ((event.clientY - rect.top) / rect.height) * 100;
        element.style.setProperty('--mouse-x', `${x}%`);
        element.style.setProperty('--mouse-y', `${y}%`);
    };

    // Add mouse move effects
    if (hero) {
        hero.addEventListener('mousemove', (e) => handleMouseMove(hero, e));
    }

    if (heroContent) {
        heroContent.addEventListener('mousemove', (e) => handleMouseMove(heroContent, e));
    }

    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => handleMouseMove(card, e));
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0) scale(1)';
        });
    });

    skillTags.forEach(tag => {
        tag.addEventListener('mousemove', (e) => handleMouseMove(tag, e));
    });

    // Scroll effects
    window.addEventListener('scroll', () => {
        const scroll = window.pageYOffset;
        
        // Parallax effect
        if (hero) {
            hero.style.backgroundPositionY = `${scroll * 0.5}px`;
        }

        // Navbar scroll effect
        const currentScroll = window.pageYOffset;
        
        if (currentScroll <= 0) {
            navbar.classList.remove('scroll-up');
            return;
        }
        
        if (currentScroll > lastScroll && !navbar.classList.contains('scroll-down')) {
            navbar.classList.remove('scroll-up');
            navbar.classList.add('scroll-down');
            navbar.style.transform = 'translateY(-100%)';
        } else if (currentScroll < lastScroll && navbar.classList.contains('scroll-down')) {
            navbar.classList.remove('scroll-down');
            navbar.classList.add('scroll-up');
            navbar.style.transform = 'translateY(0)';
        }
        
        lastScroll = currentScroll;
    });

    // Form input animation
    const formInputs = document.querySelectorAll('.form-group input, .form-group textarea');
    formInputs.forEach(input => {
        input.addEventListener('focus', () => {
            input.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', () => {
            if (!input.value) {
                input.parentElement.classList.remove('focused');
            }
        });
    });
}); 