┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                             │
│              HTML + CSS + Vanilla JavaScript                │
│                                                             │
│  Pages:                                                     │
│  • index.html      → Homepage (featured + new drops)        │
│  • browse.html     → Category filtering                     │
│  • piece.html      → Single piece detail + image gallery    │
│  • cart.html       → Shopping cart                          │
│  • checkout.html   → Shipping info → Stripe payment         │
│  • success.html    → Order confirmation                     │
│  • admin.html      → Your inventory management (protected)  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI)                         │
│                                                             │
│  Public Endpoints:                                          │
│  GET  /api/pieces              → List all (with filters)    │
│  GET  /api/pieces/{id}         → Single piece + images      │
│  GET  /api/categories          → List categories            │
│  POST /api/cart                → Add to cart (session-based)│
│  GET  /api/cart                → View cart                  │
│  DELETE /api/cart/{piece_id}   → Remove from cart           │
│  POST /api/shipping/rates      → Get shipping quotes        │
│  POST /api/checkout            → Create Stripe session      │
│  POST /api/webhooks/stripe     → Handle payment success     │
│                                                             │
│  Admin Endpoints (password-protected):                      │
│  GET/POST/PUT/DELETE /api/admin/pieces                      │
│  POST /api/admin/upload-image                               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                       DATABASE                              │
│              SQLite (dev) / PostgreSQL (prod)               │
│                                                             │
│  pieces                                                     │
│  ├── id (primary key)                                       │
│  ├── title                                                  │
│  ├── description                                            │
│  ├── price (cents, e.g., 15000 = $150.00)                   │
│  ├── category (painting|pastel|crayon|marker|paper_mache)   │
│  ├── is_sold (boolean)                                      │
│  ├── is_featured (boolean)                                  │
│  ├── dimensions (e.g., "24x36 inches")                      │
│  ├── weight_oz (for shipping calc)                          │
│  ├── created_at                                             │
│                                                             │
│  piece_images                                               │
│  ├── id                                                     │
│  ├── piece_id (foreign key)                                 │
│  ├── image_url                                              │
│  ├── is_primary (boolean)                                   │
│  ├── display_order                                          │
│                                                             │
│  orders                                                     │
│  ├── id                                                     │
│  ├── stripe_session_id                                      │
│  ├── customer_email                                         │
│  ├── customer_name                                          │
│  ├── shipping_address (JSON)                                │
│  ├── shipping_cost (cents)                                  │
│  ├── subtotal (cents)                                       │
│  ├── total (cents)                                          │
│  ├── status (pending|paid|shipped|delivered)                │
│  ├── tracking_number                                        │
│  ├── created_at                                             │
│                                                             │
│  order_items                                                │
│  ├── id                                                     │
│  ├── order_id (foreign key)                                 │
│  ├── piece_id (foreign key)                                 │
│  ├── price_at_purchase (cents)                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                        │
│                                                             │
│  Stripe          → Payment processing                       │
│  Shippo/EasyPost → Real-time shipping rates + labels        │
│  Cloudinary      → Image hosting & optimization (free tier) │
│  Resend          → Order confirmation emails (free tier)    │
└─────────────────────────────────────────────────────────────┘






art-shop/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Environment variables
│   ├── database.py             # DB connection + models
│   ├── models.py               # SQLAlchemy models
│   ├── routers/
│   │   ├── pieces.py           # Public piece endpoints
│   │   ├── cart.py             # Cart management
│   │   ├── checkout.py         # Stripe + shipping
│   │   └── admin.py            # Your admin endpoints
│   ├── services/
│   │   ├── stripe_service.py   # Stripe integration
│   │   ├── shipping_service.py # Shippo/EasyPost
│   │   └── email_service.py    # Order confirmations
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── browse.html
│   ├── piece.html
│   ├── cart.html
│   ├── checkout.html
│   ├── success.html
│   ├── admin.html
│   ├── css/
│   │   └── styles.css
│   └── js/
│       ├── main.js             # Shared utilities
│       ├── cart.js             # Cart logic
│       ├── gallery.js          # Image gallery
│       └── admin.js            # Admin panel
│
├── .env                        # API keys (never commit!)
├── .gitignore
└── README.md