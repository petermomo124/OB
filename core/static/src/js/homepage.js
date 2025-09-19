document.addEventListener('DOMContentLoaded', function() {
    // Initialize the hero slider if it exists on the page
    const heroSlider = document.querySelector('.hero-slider');
    if (heroSlider) {
        initHeroSlider();
    }

    // Initialize the testimonial slider if it exists on the page
    const testimonialSlider = document.querySelector('.testimonial-slider');
    if (testimonialSlider) {
        initTestimonialSlider();
    }

    // Initialize the counter animation if counters exist on the page
    const counters = document.querySelectorAll('.counter');
    if (counters.length > 0) {
        initCounterAnimation();
    }

    // Initialize the scroll reveal animation
    initScrollReveal();
});

/**
 * Initialize the hero slider with autoplay and navigation
 */
function initHeroSlider() {
    const slides = document.querySelectorAll('.hero-slide');
    const dotsContainer = document.querySelector('.slider-dots');
    let currentSlide = 0;
    let slideInterval;
    const slideIntervalTime = 5000; // 5 seconds

    // Create dots for navigation
    if (dotsContainer) {
        slides.forEach((_, index) => {
            const dot = document.createElement('button');
            dot.classList.add('slider-dot');
            if (index === 0) dot.classList.add('active');
            dot.setAttribute('data-slide', index);
            dot.addEventListener('click', () => goToSlide(index));
            dotsContainer.appendChild(dot);
        });
    }

    // Next/previous controls
    const prevBtn = document.querySelector('.slider-prev');
    const nextBtn = document.querySelector('.slider-next');

    if (prevBtn) prevBtn.addEventListener('click', prevSlide);
    if (nextBtn) nextBtn.addEventListener('click', nextSlide);

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') prevSlide();
        if (e.key === 'ArrowRight') nextSlide();
    });

    // Auto slide
    function startSlideShow() {
        slideInterval = setInterval(nextSlide, slideIntervalTime);
    }

    // Pause on hover
    const slider = document.querySelector('.hero-slider');
    if (slider) {
        slider.addEventListener('mouseenter', () => clearInterval(slideInterval));
        slider.addEventListener('mouseleave', startSlideShow);
    }

    // Start the slideshow
    startSlideShow();

    // Go to a specific slide
    function goToSlide(n) {
        slides.forEach(slide => slide.classList.remove('active'));
        const dots = document.querySelectorAll('.slider-dot');
        dots.forEach(dot => dot.classList.remove('active'));
        
        currentSlide = (n + slides.length) % slides.length;
        slides[currentSlide].classList.add('active');
        if (dots[currentSlide]) dots[currentSlide].classList.add('active');
    }

    // Next slide
    function nextSlide() {
        goToSlide(currentSlide + 1);
    }

    // Previous slide
    function prevSlide() {
        goToSlide(currentSlide - 1);
    }
}

/**
 * Initialize the testimonial slider
 */
function initTestimonialSlider() {
    const testimonials = document.querySelectorAll('.testimonial');
    let currentTestimonial = 0;
    let testimonialInterval;
    const testimonialIntervalTime = 8000; // 8 seconds

    // Show the first testimonial
    function showTestimonial(n) {
        testimonials.forEach(testimonial => testimonial.classList.remove('active'));
        currentTestimonial = (n + testimonials.length) % testimonials.length;
        testimonials[currentTestimonial].classList.add('active');
    }

    // Auto-rotate testimonials
    function startTestimonialRotation() {
        testimonialInterval = setInterval(() => {
            showTestimonial(currentTestimonial + 1);
        }, testimonialIntervalTime);
    }

    // Pause on hover
    const testimonialContainer = document.querySelector('.testimonial-slider');
    if (testimonialContainer) {
        testimonialContainer.addEventListener('mouseenter', () => clearInterval(testimonialInterval));
        testimonialContainer.addEventListener('mouseleave', startTestimonialRotation);
    }

    // Navigation dots
    const dotsContainer = document.querySelector('.testimonial-dots');
    if (dotsContainer) {
        testimonials.forEach((_, index) => {
            const dot = document.createElement('button');
            dot.classList.add('testimonial-dot');
            if (index === 0) dot.classList.add('active');
            dot.addEventListener('click', () => {
                clearInterval(testimonialInterval);
                showTestimonial(index);
                startTestimonialRotation();
            });
            dotsContainer.appendChild(dot);
        });
    }

    // Start the testimonial rotation
    startTestimonialRotation();
}

/**
 * Animate counters when they come into view
 */
function initCounterAnimation() {
    const counters = document.querySelectorAll('.counter');
    const speed = 200; // The lower the slower
    let animated = [];

    function animateCounter(counter) {
        const target = +counter.getAttribute('data-target');
        const count = +counter.innerText;
        const increment = target / speed;

        if (count < target) {
            counter.innerText = Math.ceil(count + increment);
            setTimeout(() => animateCounter(counter), 10);
        } else {
            counter.innerText = target.toLocaleString();
        }
    }

    // Check if element is in viewport
    function isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }

    // Check all counters on scroll
    function checkCounters() {
        counters.forEach((counter, index) => {
            if (isInViewport(counter) && !animated.includes(index)) {
                animated.push(index);
                animateCounter(counter);
            }
        });
    }

    // Initial check
    checkCounters();

    // Check on scroll
    window.addEventListener('scroll', checkCounters);
}

/**
 * Initialize scroll reveal animations
 */
function initScrollReveal() {
    // Check if ScrollReveal is loaded
    if (typeof ScrollReveal !== 'undefined') {
        const sr = ScrollReveal({
            origin: 'bottom',
            distance: '20px',
            duration: 1000,
            delay: 200,
            reset: false,
            mobile: true
        });

        // Reveal elements with the 'reveal' class
        sr.reveal('.reveal', {
            interval: 200
        });

        // Custom reveal for different directions
        sr.reveal('.reveal-left', { origin: 'left' });
        sr.reveal('.reveal-right', { origin: 'right' });
        sr.reveal('.reveal-top', { origin: 'top' });
        sr.reveal('.reveal-bottom', { origin: 'bottom' });

        // Staggered reveal for grid items
        sr.reveal('.reveal-stagger', {
            interval: 100
        });
    }
}

/**
 * Debounce function to limit the rate at which a function can fire
 */
function debounce(func, wait = 20, immediate = true) {
    let timeout;
    return function() {
        const context = this, args = arguments;
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}
