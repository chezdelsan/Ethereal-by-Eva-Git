/**
 * Ethereal by Eva - Main JavaScript
 * Shared utilities and helper functions.
 */

const Utils = {
    /**
     * Format price from cents to display string
     * @param {number} cents - Price in cents (e.g., 15000 = $150.00)
     * @returns {string} Formatted price (e.g., "$150.00")
     */
    formatPrice(cents) {
        const dollars = cents / 100;
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
        }).format(dollars);
    },
    
    /**
     * Get URL query parameters
     * @returns {URLSearchParams}
     */
    getQueryParams() {
        return new URLSearchParams(window.location.search);
    },
    
    /**
     * Get a specific query parameter
     * @param {string} name - Parameter name
     * @returns {string|null}
     */
    getQueryParam(name) {
        return this.getQueryParams().get(name);
    },
    
    /**
     * Create HTML element from string
     * @param {string} html - HTML string
     * @returns {HTMLElement}
     */
    createElement(html) {
        const template = document.createElement('template');
        template.innerHTML = html.trim();
        return template.content.firstChild;
    },
    
    /**
     * Show loading state in a container
     * @param {HTMLElement} container
     */
    showLoading(container) {
        container.innerHTML = '<div class="loading">Loading</div>';
    },
    
    /**
     * Show error state in a container
     * @param {HTMLElement} container
     * @param {string} message
     */
    showError(container, message) {
        container.innerHTML = `
            <div class="empty-state">
                <p>${message}</p>
                <a href="/" class="btn btn-secondary">Return Home</a>
            </div>
        `;
    },
    
    /**
     * Show empty state in a container
     * @param {HTMLElement} container
     * @param {string} message
     */
    showEmpty(container, message) {
        container.innerHTML = `<div class="empty-state"><p>${message}</p></div>`;
    },
    
    /**
     * Debounce function calls
     * @param {Function} func
     * @param {number} wait
     * @returns {Function}
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    /**
     * Get category display name
     * @param {string} slug
     * @returns {string}
     */
        getCategoryName(slug) {
            const names = {
                painting: 'Paintings',
            };
            return names[slug] || 'Art Pieces';
    },
};


/**
 * Piece Card Component
 * Renders a piece card for grid display.
 */
function renderPieceCard(piece) {
    // Get primary image or first image
    let imageUrl = 'https://via.placeholder.com/400x500?text=No+Image';
    if (piece.images && piece.images.length > 0) {
        const primary = piece.images.find(img => img.is_primary);
        imageUrl = primary ? primary.image_url : piece.images[0].image_url;
    }
    
    return `
        <a href="piece.html?id=${piece.id}" class="piece-card">
            <div class="piece-card-image">
                <img src="${imageUrl}" alt="${piece.title}" loading="lazy">
                ${piece.is_sold ? '<span class="piece-card-sold">Sold</span>' : ''}
            </div>
            <div class="piece-card-info">
                <h3 class="piece-card-title">${piece.title}</h3>
                <span class="piece-card-price">${Utils.formatPrice(piece.price)}</span>
            </div>
        </a>
    `;
}


/**
 * Render a grid of pieces
 * @param {HTMLElement} container
 * @param {Array} pieces
 */
function renderPieceGrid(container, pieces) {
    if (!pieces || pieces.length === 0) {
        Utils.showEmpty(container, 'No pieces found');
        return;
    }
    
    container.innerHTML = pieces.map(renderPieceCard).join('');
}


// Make utilities available globally
window.Utils = Utils;
window.renderPieceCard = renderPieceCard;
window.renderPieceGrid = renderPieceGrid;
