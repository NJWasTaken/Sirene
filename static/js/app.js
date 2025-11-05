document.addEventListener('DOMContentLoaded', () => {
    // Search overlay functionality
    const searchOpenBtn = document.getElementById('search-open-button');
    const searchCloseBtn = document.getElementById('search-close-button');
    const searchOverlay = document.getElementById('search-overlay');
    const searchInput = document.getElementById('search-input');
    const searchResultsList = document.getElementById('search-results-list');
    let searchTimeout = null;

    if (searchOpenBtn && searchOverlay) {
        searchOpenBtn.addEventListener('click', () => {
            // Don't open overlay if we're already on the search page
            if (window.location.pathname === '/search') {
                return;
            }
            searchOverlay.classList.remove('hidden');
            searchOverlay.style.display = 'block';
            searchOverlay.style.pointerEvents = 'auto';
            if (searchInput) searchInput.focus();
        });
    }

    if (searchCloseBtn && searchOverlay) {
        searchCloseBtn.addEventListener('click', () => {
            searchOverlay.classList.add('hidden');
            searchOverlay.style.display = 'none';
            searchOverlay.style.pointerEvents = 'none';
            if (searchInput) searchInput.value = '';
            if (searchResultsList) searchResultsList.innerHTML = '';
        });
    }

    // Close search overlay on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && searchOverlay && !searchOverlay.classList.contains('hidden')) {
            searchOverlay.classList.add('hidden');
            searchOverlay.style.display = 'none';
            searchOverlay.style.pointerEvents = 'none';
            if (searchInput) searchInput.value = '';
            if (searchResultsList) searchResultsList.innerHTML = '';
        }
    });

    // Search autocomplete functionality
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            
            // Clear previous timeout
            if (searchTimeout) {
                clearTimeout(searchTimeout);
            }

            // If query is too short, clear results
            if (query.length < 2) {
                if (searchResultsList) searchResultsList.innerHTML = '';
                return;
            }

            // Show loading state
            if (searchResultsList) {
                searchResultsList.innerHTML = '<div class="text-center text-gray-400 py-4">Searching...</div>';
            }

            // Debounce search requests
            searchTimeout = setTimeout(() => {
                fetch(`/api/search?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(results => {
                        displaySearchResults(results);
                    })
                    .catch(error => {
                        console.error('Search error:', error);
                        if (searchResultsList) {
                            searchResultsList.innerHTML = '<div class="text-center text-red-400 py-4">Error loading results</div>';
                        }
                    });
            }, 300); // Wait 300ms after user stops typing
        });

        // Handle Enter key to go to full search results
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const query = searchInput.value.trim();
                if (query) {
                    // Navigate to search page with query
                    window.location.href = `/search?q=${encodeURIComponent(query)}`;
                } else {
                    e.preventDefault();
                }
            }
        });
    }

    // Completely remove search overlay on page load if we're on the search page
    function hideSearchOverlay() {
        if (searchOverlay) {
            searchOverlay.classList.add('hidden');
            searchOverlay.style.display = 'none';
            searchOverlay.style.visibility = 'hidden';
            searchOverlay.style.pointerEvents = 'none';
            searchOverlay.style.opacity = '0';
            searchOverlay.style.zIndex = '-9999';
        }
    }
    
    function removeSearchOverlay() {
        if (searchOverlay && searchOverlay.parentNode) {
            searchOverlay.parentNode.removeChild(searchOverlay);
        }
    }
    
    if (window.location.pathname === '/search' || window.location.pathname.startsWith('/search')) {
        // Immediately hide it
        hideSearchOverlay();
        // Then completely remove it from DOM
        setTimeout(removeSearchOverlay, 10);
        setTimeout(removeSearchOverlay, 100);
        window.addEventListener('load', removeSearchOverlay);
    }
    
    // Also ensure the form in the search overlay properly submits and redirects
    if (searchInput) {
        const searchForm = searchInput.closest('form');
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => {
                // Let the form submit naturally, but ensure overlay closes
                if (searchOverlay) {
                    setTimeout(() => {
                        hideSearchOverlay();
                    }, 10);
                }
            });
        }
    }

    // Display search results in dropdown
    function displaySearchResults(results) {
        if (!searchResultsList) return;

        if (results.length === 0) {
            searchResultsList.innerHTML = '<div class="text-center text-gray-400 py-4">No results found</div>';
            return;
        }

        searchResultsList.innerHTML = results.map(item => `
            <a href="/media/${item.id}" class="search-result-link flex items-start gap-4 p-4 bg-brand-gray rounded-lg hover:bg-brand-light-gray transition group">
                <div class="flex-shrink-0 w-16 h-24 bg-brand-light-gray rounded overflow-hidden">
                    ${item.poster_url 
                        ? `<img src="${item.poster_url}" alt="${item.title}" class="w-full h-full object-cover">`
                        : `<div class="w-full h-full flex items-center justify-center text-gray-500">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                        </div>`
                    }
                </div>
                <div class="flex-1 min-w-0">
                    <h3 class="font-semibold text-white group-hover:text-brand-red transition truncate">${item.title}</h3>
                    <div class="flex items-center gap-2 text-sm text-gray-400 mt-1">
                        <span class="px-2 py-0.5 bg-brand-red/20 text-brand-red rounded text-xs">${item.media_type}</span>
                        ${item.release_date ? `<span>${item.release_date.split('-')[0]}</span>` : ''}
                        ${item.avg_rating > 0 ? `<span>⭐ ${item.avg_rating.toFixed(1)}</span>` : ''}
                    </div>
                    ${item.synopsis ? `<p class="text-sm text-gray-400 mt-2 line-clamp-2">${item.synopsis}</p>` : ''}
                </div>
            </a>
        `).join('');

        // Add click event listeners to close overlay when clicking suggestions
        document.querySelectorAll('.search-result-link').forEach(link => {
            link.addEventListener('click', () => {
                if (searchOverlay) {
                    searchOverlay.classList.add('hidden');
                    searchOverlay.style.display = 'none';
                    searchOverlay.style.pointerEvents = 'none';
                }
            });
        });
    }

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