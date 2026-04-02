// Mobile Navigation Toggle
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('active');
    navMenu.classList.toggle('active');
});

// Close mobile menu when clicking on a link
document.querySelectorAll('.nav-menu a').forEach(link => {
    link.addEventListener('click', () => {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
    });
});

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const targetId = this.getAttribute('href').substring(1);
        const element = document.getElementById(targetId);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// Navbar background on scroll
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.style.background = 'linear-gradient(135deg, #27ae60 0%, #2980b9 100%)';
        navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.2)';
    } else {
        navbar.style.background = 'linear-gradient(135deg, #2ecc71 0%, #3498db 100%)';
        navbar.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
    }
});

// Animate elements on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe elements for animation
document.addEventListener('DOMContentLoaded', () => {
    // Animate stat cards
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`;
        observer.observe(card);
    });

    // Animate awareness cards
    const awarenessCards = document.querySelectorAll('.awareness-card');
    awarenessCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`;
        observer.observe(card);
    });

    // Animate process steps
    const steps = document.querySelectorAll('.step');
    steps.forEach((step, index) => {
        step.style.opacity = '0';
        step.style.transform = 'translateY(30px)';
        step.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`;
        observer.observe(step);
    });

    // Animate testimonials
    const testimonials = document.querySelectorAll('.testimonial-card');
    testimonials.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`;
        observer.observe(card);
    });

    // Animate hero content
    const heroContent = document.querySelector('.hero-content');
    if (heroContent) {
        heroContent.style.opacity = '0';
        heroContent.style.transform = 'translateY(30px)';
        heroContent.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
        
        setTimeout(() => {
            heroContent.style.opacity = '1';
            heroContent.style.transform = 'translateY(0)';
        }, 300);
    }

    // Animate hero image
    const heroImage = document.querySelector('.hero-image');
    if (heroImage) {
        heroImage.style.opacity = '0';
        heroImage.style.transform = 'translateX(30px)';
        heroImage.style.transition = 'opacity 0.8s ease 0.3s, transform 0.8s ease 0.3s';
        
        setTimeout(() => {
            heroImage.style.opacity = '1';
            heroImage.style.transform = 'translateX(0)';
        }, 600);
    }
});

// Counter animation for statistics
function animateCounter(element, target, duration = 2000) {
    let start = 0;
    const increment = target / (duration / 16);
    const timer = setInterval(() => {
        start += increment;
        if (start >= target) {
            element.textContent = target.toLocaleString();
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(start).toLocaleString();
        }
    }, 16);
}

// Initialize counters when they come into view
document.addEventListener('DOMContentLoaded', () => {
    const statNumbers = document.querySelectorAll('.stat-number');
    
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = parseInt(entry.target.textContent.replace(/,/g, ''));
                animateCounter(entry.target, target);
                counterObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    statNumbers.forEach(stat => {
        counterObserver.observe(stat);
    });
});

// Form validation helper functions
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function validatePhone(phone) {
    const phoneRegex = /^[\d\s\-\+\(\)]+$/;
    return phoneRegex.test(phone) && phone.replace(/\D/g, '').length >= 10;
}

function validateForm(formData) {
    const errors = [];
    
    if (formData.name && formData.name.length < 3) {
        errors.push('Name must be at least 3 characters long');
    }
    
    if (formData.email && !validateEmail(formData.email)) {
        errors.push('Please enter a valid email address');
    }
    
    if (formData.phone && !validatePhone(formData.phone)) {
        errors.push('Please enter a valid phone number');
    }
    
    return errors;
}

// Show notification function
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
        max-width: 300px;
    `;
    
    if (type === 'success') {
        notification.style.background = '#27ae60';
    } else if (type === 'error') {
        notification.style.background = '#e74c3c';
    } else if (type === 'warning') {
        notification.style.background = '#f39c12';
    } else {
        notification.style.background = '#3498db';
    }
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 4 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 4000);
}

// Loading spinner
function showLoading(element) {
    const spinner = document.createElement('div');
    spinner.className = 'loading-spinner';
    spinner.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    spinner.style.cssText = `
        display: inline-block;
        margin-left: 10px;
        color: #3498db;
    `;
    element.appendChild(spinner);
}

function hideLoading(element) {
    const spinner = element.querySelector('.loading-spinner');
    if (spinner) {
        element.removeChild(spinner);
    }
}

// Handle window resize
window.addEventListener('resize', () => {
    // Close mobile menu on window resize
    if (window.innerWidth > 768) {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
    }
});

// Add keyboard navigation support
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        // Close mobile menu on Escape key
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
    }
});

// Performance optimization - Debounce scroll events
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Apply debounce to scroll events
const debouncedScroll = debounce(() => {
    // Scroll-related functions here
}, 100);

window.addEventListener('scroll', debouncedScroll);

// Utility function to generate unique IDs
function generateUniqueId(prefix, type) {
    const timestamp = Date.now();
    const random = Math.floor(Math.random() * 10000);
    return `${prefix}-${type}-${timestamp}${random}`;
}

// Example usage for generating registration IDs
function generateDonorId() {
    return generateUniqueId('OD', 'DON');
}

function generateRecipientId() {
    return generateUniqueId('OD', 'REC');
}

// Prevent browser back button after logout
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is logged out and prevent back navigation
    function preventBackNavigation() {
        // Push a new state to the history when page loads
        history.pushState(null, null, location.href);
        
        // Listen for popstate events (back/forward buttons)
        window.addEventListener('popstate', function(event) {
            // Check if user is not authenticated by looking for logout link or dashboard link
            const hasLogoutLink = document.querySelector('a[href*="logout"]') !== null;
            const hasDashboardLink = document.querySelector('a[href*="dashboard"]') !== null;
            const isLoggedIn = hasLogoutLink || hasDashboardLink;
            
            if (!isLoggedIn) {
                // User is not logged in, redirect to login page
                window.location.href = '/login/';
            } else {
                // User is logged in, push state again to prevent going back to login page
                history.pushState(null, null, location.href);
            }
        });
    }
    
    // Initialize the prevention
    preventBackNavigation();
    
    // Also handle page visibility changes (when user switches tabs and comes back)
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            // Page is hidden, check authentication when it becomes visible again
            setTimeout(function() {
                const hasLogoutLink = document.querySelector('a[href*="logout"]') !== null;
                const hasDashboardLink = document.querySelector('a[href*="dashboard"]') !== null;
                const isLoggedIn = hasLogoutLink || hasDashboardLink;
                
                // If we're on a protected page but not logged in, redirect
                const isProtectedPage = window.location.pathname.includes('dashboard') || 
                                     window.location.pathname.includes('profile');
                
                if (isProtectedPage && !isLoggedIn) {
                    window.location.href = '/login/';
                }
            }, 100);
        }
    });
    
    // Handle browser storage events (for multi-tab scenarios)
    window.addEventListener('storage', function(e) {
        if (e.key === 'user_logout') {
            // User logged out in another tab
            window.location.href = '/login/';
        }
    });
});

// Function to call when logging out to notify other tabs
function notifyLogout() {
    localStorage.setItem('user_logout', Date.now());
    setTimeout(function() {
        localStorage.removeItem('user_logout');
    }, 1000);
}

// Export functions for use in other pages
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        validateEmail,
        validatePhone,
        validateForm,
        showNotification,
        showLoading,
        hideLoading,
        generateDonorId,
        generateRecipientId,
        notifyLogout
    };
}
