/**
 * Ethereal by Eva - Shopping Cart
 * Client-side cart management using localStorage.
 */

const Cart = {
    STORAGE_KEY: 'ethereal_by_eva_cart',
    OLD_STORAGE_KEY: 'daisy_designs_cart',
    
    /**
     * Migrate from old storage key if needed
     */
    migrate() {
        const oldData = localStorage.getItem(this.OLD_STORAGE_KEY);
        const newData = localStorage.getItem(this.STORAGE_KEY);
        
        if (oldData && !newData) {
            localStorage.setItem(this.STORAGE_KEY, oldData);
            localStorage.removeItem(this.OLD_STORAGE_KEY);
            console.log('Migrated cart from old storage key');
        }
    },
    
    /**
     * Get cart items from localStorage
     */
    getItems() {
        try {
            const data = localStorage.getItem(this.STORAGE_KEY);
            return data ? JSON.parse(data) : [];
        } catch (e) {
            console.error('Error reading cart:', e);
            return [];
        }
    },
    
    /**
     * Save cart items to localStorage
     */
    saveItems(items) {
        try {
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(items));
            this.updateCartCount();
            this.dispatchUpdate();
        } catch (e) {
            console.error('Error saving cart:', e);
        }
    },
    
    /**
     * Add a piece to cart
     */
    addItem(piece) {
        const items = this.getItems();
        
        if (items.some(item => item.piece_id === piece.id)) {
            return { success: false, message: 'This piece is already in your cart' };
        }
        
        let imageUrl = null;
        if (piece.images && piece.images.length > 0) {
            const primary = piece.images.find(img => img.is_primary);
            imageUrl = primary ? primary.image_url : piece.images[0].image_url;
        }
        
        // Use sale price if available
        let finalPrice = piece.price;
        if (typeof piece.sale_price === 'number' && piece.sale_price > 0 && !piece.is_sold) {
            finalPrice = piece.sale_price;
        }
        items.push({
            piece_id: piece.id,
            title: piece.title,
            price: finalPrice,
            image_url: imageUrl,
            added_at: new Date().toISOString(),
        });
        
        this.saveItems(items);
        return { success: true, message: 'Added to cart' };
    },
    
    /**
     * Remove a piece from cart
     */
    removeItem(pieceId) {
        const items = this.getItems();
        const filtered = items.filter(item => item.piece_id !== pieceId);
        
        if (filtered.length === items.length) {
            return { success: false, message: 'Item not found in cart' };
        }
        
        this.saveItems(filtered);
        return { success: true, message: 'Removed from cart' };
    },
    
    /**
     * Check if a piece is in cart
     */
    hasItem(pieceId) {
        return this.getItems().some(item => item.piece_id === pieceId);
    },
    
    /**
     * Get cart count
     */
    getCount() {
        return this.getItems().length;
    },
    
    /**
     * Get cart subtotal (in cents)
     */
    getSubtotal() {
        return this.getItems().reduce((sum, item) => sum + item.price, 0);
    },
    
    /**
     * Clear the cart
     */
    clear() {
        this.saveItems([]);
    },
    
    /**
     * Get piece IDs in cart
     */
    getPieceIds() {
        return this.getItems().map(item => item.piece_id);
    },
    
    /**
     * Update cart count display in header
     */
    updateCartCount() {
        const countElements = document.querySelectorAll('.cart-count');
        const count = this.getCount();
        
        countElements.forEach(el => {
            el.textContent = count;
            el.setAttribute('data-count', count);
        });
    },
    
    /**
     * Dispatch custom event when cart updates
     */
    dispatchUpdate() {
        window.dispatchEvent(new CustomEvent('cartUpdated', {
            detail: {
                count: this.getCount(),
                subtotal: this.getSubtotal(),
                items: this.getItems(),
            }
        }));
    },
    
    /**
     * Initialize cart (call on page load)
     */
    init() {
        this.migrate();
        this.updateCartCount();
    }
};

// Initialize cart on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    Cart.init();
});

// Make Cart available globally
window.Cart = Cart;
