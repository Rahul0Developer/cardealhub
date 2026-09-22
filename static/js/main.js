document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuButton = document.querySelector('.md\\:hidden');
    const mobileMenu = document.createElement('div');
    
    if (mobileMenuButton) {
        mobileMenu.className = 'mobile-menu fixed inset-0 bg-white z-50 transform translate-x-full transition-transform duration-300 ease-in-out';
        mobileMenu.innerHTML = `
            <div class="h-16 flex items-center justify-between px-4 border-b">
                <a href="#" class="font-['Pacifico'] text-2xl text-primary">Car Deal Hub</a>
                <button class="close-menu w-10 h-10 flex items-center justify-center">
                    <i class="ri-close-line text-gray-700 text-xl"></i>
                </button>
            </div>
            <nav class="flex flex-col p-4">
                <a href="/" class="py-3 text-gray-700 hover:text-primary font-medium transition-colors">Home</a>
                <a href="/marketplace" class="py-3 text-gray-700 hover:text-primary font-medium transition-colors">Marketplace</a>
                <a href="/predict" class="py-3 text-gray-700 hover:text-primary font-medium transition-colors">Predict</a>
                <a href="/trends" class="py-3 text-gray-700 hover:text-primary font-medium transition-colors">Trends</a>
                <a href="/list-car" class="py-3 text-gray-700 hover:text-primary font-medium transition-colors">List Car</a>
                <a href="/contact" class="py-3 text-gray-700 hover:text-primary font-medium transition-colors">Contact Us</a>
                <div class="border-t my-3"></div>
                <a href="/login" class="py-3 text-gray-700 hover:text-primary font-medium transition-colors">Login</a>
                <a href="/register" class="py-3 bg-primary text-white px-4 rounded-button text-center font-medium">Register</a>
            </nav>
        `;
        
        document.body.appendChild(mobileMenu);
        
        // Toggle mobile menu
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('translate-x-full');
        });
        
        // Close mobile menu
        const closeMenuButton = mobileMenu.querySelector('.close-menu');
        if (closeMenuButton) {
            closeMenuButton.addEventListener('click', function() {
                mobileMenu.classList.add('translate-x-full');
            });
        }
    }
    
    // Toggle dark/light mode
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        // Check if user has a theme preference stored
        const savedTheme = localStorage.getItem('theme');
        const systemPrefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        // Set initial theme based on saved preference or system preference
        if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
            document.documentElement.classList.add('dark');
            themeToggle.querySelector('i').classList.remove('ri-sun-line');
            themeToggle.querySelector('i').classList.add('ri-moon-line');
        }
        
        themeToggle.addEventListener('click', function() {
            // Toggle between sun and moon icons
            const icon = themeToggle.querySelector('i');
            const isDark = document.documentElement.classList.contains('dark');
            
            if (isDark) {
                // Switch to light mode
                document.documentElement.classList.remove('dark');
                icon.classList.remove('ri-moon-line');
                icon.classList.add('ri-sun-line');
                localStorage.setItem('theme', 'light');
            } else {
                // Switch to dark mode
                document.documentElement.classList.add('dark');
                icon.classList.remove('ri-sun-line');
                icon.classList.add('ri-moon-line');
                localStorage.setItem('theme', 'dark');
            }
        });
    }
    
    // Handle flash messages
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        // Auto-dismiss flash messages after 5 seconds
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);
        
        // Allow manual dismiss
        const closeButton = message.querySelector('.close-flash');
        if (closeButton) {
            closeButton.addEventListener('click', () => {
                message.style.opacity = '0';
                setTimeout(() => {
                    message.remove();
                }, 300);
            });
        }
    });
    
    // Initialize price range sliders if present
    const priceRangeSliders = document.querySelectorAll('.price-range-slider');
    priceRangeSliders.forEach(slider => {
        if (slider) {
            const minPrice = slider.getAttribute('data-min') || 0;
            const maxPrice = slider.getAttribute('data-max') || 10000000;
            const step = slider.getAttribute('data-step') || 10000;
            
            // Initialize noUiSlider (if included in the page)
            if (window.noUiSlider) {
                noUiSlider.create(slider, {
                    start: [minPrice, maxPrice],
                    connect: true,
                    step: parseInt(step),
                    range: {
                        'min': parseInt(minPrice),
                        'max': parseInt(maxPrice)
                    },
                    format: {
                        to: value => Math.round(value),
                        from: value => Math.round(value)
                    }
                });
                
                // Update price display
                const minPriceDisplay = document.getElementById('min-price-display');
                const maxPriceDisplay = document.getElementById('max-price-display');
                
                if (minPriceDisplay && maxPriceDisplay) {
                    slider.noUiSlider.on('update', (values, handle) => {
                        if (handle === 0) {
                            minPriceDisplay.textContent = `₹${parseInt(values[0]).toLocaleString()}`;
                        } else {
                            maxPriceDisplay.textContent = `₹${parseInt(values[1]).toLocaleString()}`;
                        }
                    });
                }
            }
        }
    });
});

// Format currency for display
function formatCurrency(amount) {
    return '₹' + parseInt(amount).toLocaleString('en-IN');
}

// Format number with thousand separators
function formatNumber(num) {
    return parseInt(num).toLocaleString('en-IN');
}
