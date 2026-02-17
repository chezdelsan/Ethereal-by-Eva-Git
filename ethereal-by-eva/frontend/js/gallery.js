/**
 * Ethereal by Eva - Image Gallery
 * Handles the image gallery on piece detail pages.
 */

const Gallery = {
    mainImage: null,
    thumbsContainer: null,
    images: [],
    currentIndex: 0,
    
    /**
     * Initialize gallery with images
     * @param {string} mainSelector - Selector for main image container
     * @param {string} thumbsSelector - Selector for thumbnails container
     * @param {Array} images - Array of image objects with image_url, is_primary, alt_text
     */
    init(mainSelector, thumbsSelector, images) {
        this.mainImage = document.querySelector(mainSelector);
        this.thumbsContainer = document.querySelector(thumbsSelector);
        this.images = images || [];
        
        if (!this.mainImage || !this.images.length) {
            console.warn('Gallery: Missing elements or images');
            return;
        }
        
        // Sort images: primary first, then by display_order
        this.images.sort((a, b) => {
            if (a.is_primary && !b.is_primary) return -1;
            if (!a.is_primary && b.is_primary) return 1;
            return (a.display_order || 0) - (b.display_order || 0);
        });
        
        this.render();
        this.bindEvents();
    },
    
    /**
     * Render the gallery
     */
    render() {
        // Set main image
        this.setMainImage(0);
        
        // Render thumbnails if more than one image
        if (this.thumbsContainer && this.images.length > 1) {
            this.thumbsContainer.innerHTML = this.images.map((img, index) => `
                <button 
                    class="piece-gallery-thumb ${index === 0 ? 'active' : ''}" 
                    data-index="${index}"
                    aria-label="View image ${index + 1}"
                >
                    <img src="${img.image_url}" alt="${img.alt_text || 'Thumbnail'}">
                </button>
            `).join('');
        } else if (this.thumbsContainer) {
            this.thumbsContainer.style.display = 'none';
        }
    },
    
    /**
     * Set the main displayed image
     * @param {number} index
     */
    setMainImage(index) {
        if (index < 0 || index >= this.images.length) return;
        
        this.currentIndex = index;
        const image = this.images[index];
        
        this.mainImage.innerHTML = `
            <img src="${image.image_url}" alt="${image.alt_text || 'Art piece'}">
        `;
        
        // Update thumbnail active states
        if (this.thumbsContainer) {
            const thumbs = this.thumbsContainer.querySelectorAll('.piece-gallery-thumb');
            thumbs.forEach((thumb, i) => {
                thumb.classList.toggle('active', i === index);
            });
        }
    },
    
    /**
     * Go to next image
     */
    next() {
        const nextIndex = (this.currentIndex + 1) % this.images.length;
        this.setMainImage(nextIndex);
    },
    
    /**
     * Go to previous image
     */
    prev() {
        const prevIndex = (this.currentIndex - 1 + this.images.length) % this.images.length;
        this.setMainImage(prevIndex);
    },
    
    /**
     * Bind event listeners
     */
    bindEvents() {
        // Thumbnail clicks
        if (this.thumbsContainer) {
            this.thumbsContainer.addEventListener('click', (e) => {
                const thumb = e.target.closest('.piece-gallery-thumb');
                if (thumb) {
                    const index = parseInt(thumb.dataset.index, 10);
                    this.setMainImage(index);
                }
            });
        }
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight') {
                this.next();
            } else if (e.key === 'ArrowLeft') {
                this.prev();
            }
        });
        
        // Click on main image to go to next (optional)
        this.mainImage.addEventListener('click', () => {
            if (this.images.length > 1) {
                this.next();
            }
        });
        
        this.mainImage.style.cursor = this.images.length > 1 ? 'pointer' : 'default';
    }
};

// Make Gallery available globally
window.Gallery = Gallery;
