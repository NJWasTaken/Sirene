document.addEventListener('DOMContentLoaded', () => {
    // Search overlay functionality
    const searchOpenBtn = document.getElementById('search-open-button');
    const searchCloseBtn = document.getElementById('search-close-button');
    const searchOverlay = document.getElementById('search-overlay');
    const searchInput = document.getElementById('search-input');

    if (searchOpenBtn && searchOverlay) {
        searchOpenBtn.addEventListener('click', () => {
            searchOverlay.classList.remove('hidden');
            if (searchInput) searchInput.focus();
        });
    }

    if (searchCloseBtn && searchOverlay) {
        searchCloseBtn.addEventListener('click', () => {
            searchOverlay.classList.add('hidden');
            if (searchInput) searchInput.value = '';
        });
    }

    // Close search overlay on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && searchOverlay && !searchOverlay.classList.contains('hidden')) {
            searchOverlay.classList.add('hidden');
            if (searchInput) searchInput.value = '';
        }
    });

    // Smooth scroll for anchor links
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

    // Lazy loading for images
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src || img.src;
                    img.classList.add('loaded');
                    observer.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }

    // Add hover effect to carousel items
    const carouselItems = document.querySelectorAll('.carousel-scrollbar a');
    carouselItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05)';
            this.style.zIndex = '10';
        });
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
            this.style.zIndex = '1';
        });
    });

    // Handle form submissions with loading states
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                const originalText = submitButton.textContent;
                submitButton.textContent = 'Loading...';
                
                // Re-enable after submission (for demo purposes)
                setTimeout(() => {
                    submitButton.disabled = false;
                    submitButton.textContent = originalText;
                }, 2000);
            }
        });
    });

    // Add animation to cards on scroll
    const animateOnScroll = () => {
        const cards = document.querySelectorAll('.animate-on-scroll');
        cards.forEach(card => {
            const cardTop = card.getBoundingClientRect().top;
            const cardBottom = card.getBoundingClientRect().bottom;
            
            if (cardTop < window.innerHeight && cardBottom > 0) {
                card.classList.add('animated');
            }
        });
    };

    window.addEventListener('scroll', animateOnScroll);
    animateOnScroll(); // Initial check

    // Toast notifications
    window.showToast = (message, type = 'info') => {
        const toast = document.createElement('div');
        toast.className = `fixed bottom-4 right-4 px-6 py-3 rounded-lg text-white z-50 transform transition-transform duration-300 translate-y-full`;
        
        switch(type) {
            case 'success':
                toast.classList.add('bg-green-600');
                break;
            case 'error':
                toast.classList.add('bg-red-600');
                break;
            default:
                toast.classList.add('bg-blue-600');
        }
        
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.remove('translate-y-full');
        }, 100);
        
        setTimeout(() => {
            toast.classList.add('translate-y-full');
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    };

    // Carousel keyboard navigation
    document.querySelectorAll('.carousel-scrollbar').forEach(carousel => {
        carousel.addEventListener('keydown', function(e) {
            const scrollAmount = 200;
            
            if (e.key === 'ArrowLeft') {
                this.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
            } else if (e.key === 'ArrowRight') {
                this.scrollBy({ left: scrollAmount, behavior: 'smooth' });
            }
        });
    });

    // Add loading skeleton while content loads
    const addLoadingSkeleton = (container, count = 3) => {
        for (let i = 0; i < count; i++) {
            const skeleton = document.createElement('div');
            skeleton.className = 'flex-shrink-0 w-poster-w h-poster-h rounded-lg bg-brand-gray animate-pulse';
            container.appendChild(skeleton);
        }
    };

    // Remove loading skeletons
    const removeLoadingSkeletons = (container) => {
        container.querySelectorAll('.animate-pulse').forEach(skeleton => {
            skeleton.remove();
        });
    };

    // Export functions for use in other scripts
    window.appUtils = {
        addLoadingSkeleton,
        removeLoadingSkeletons,
        showToast
    };
});