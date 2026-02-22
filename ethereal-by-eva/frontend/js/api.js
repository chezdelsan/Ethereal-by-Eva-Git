/**
 * Ethereal by Eva - API Client
 * 
 * DEPLOYMENT: Change baseUrl to your Render backend URL
 * Example: 'https://ethereal-api.onrender.com'
 */

const API = {
    // ⚠️ CHANGE THIS FOR PRODUCTION
    baseUrl: 'http://localhost:8000',
    
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: { 'Content-Type': 'application/json', ...options.headers },
            ...options,
        };
        
        try {
            const response = await fetch(url, config);
            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.detail || `HTTP ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    },
    
    // Pieces
    async getPieces(params = {}) {
        const query = new URLSearchParams();
        if (params.category) query.set('category', 'painting');
        if (params.featured !== undefined) query.set('featured', params.featured);
        if (params.available !== undefined) query.set('available', params.available);
        if (params.sort) query.set('sort', params.sort);
        if (params.page) query.set('page', params.page);
        if (params.per_page) query.set('per_page', params.per_page);
        const queryString = query.toString();
        return this.request(`/api/pieces${queryString ? '?' + queryString : ''}`);
    },
    
    async getFeaturedPieces(limit = 6) {
        return this.request(`/api/pieces/featured?limit=${limit}`);
    },
    
    async getNewPieces(limit = 6) {
        return this.request(`/api/pieces/new?limit=${limit}`);
    },
    
    async getPiece(id) {
        return this.request(`/api/pieces/${id}`);
    },
    
    async getCategories() {
        return this.request('/api/pieces/categories');
    },
    
    // Cart
    async validateCart(pieceIds) {
        return this.request('/api/cart/validate', {
            method: 'POST',
            body: JSON.stringify(pieceIds),
        });
    },
    
    async checkAvailability(pieceId) {
        return this.request(`/api/cart/check/${pieceId}`);
    },
    
    // Checkout
    async getShippingRates(address, pieceIds) {
        return this.request('/api/shipping/rates', {
            method: 'POST',
            body: JSON.stringify({ address, piece_ids: pieceIds }),
        });
    },
    
    async createCheckout(data) {
        return this.request('/api/checkout', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },
};

window.API = API;
