# Ethereal by Eva - Art E-Commerce Site

A minimal, clean e-commerce site for selling one-of-a-kind art pieces.

## Tech Stack

- **Frontend**: HTML, CSS, Vanilla JavaScript
- **Backend**: Python + FastAPI
- **Database**: SQLite (development) / PostgreSQL (production)
- **Payments**: Stripe
- **Shipping**: Shippo
- **Hosting**: Render

## Local Development Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd ethereal-by-eva
```

### 2. Set up the backend

```bash
# Navigate to backend folder
cd backend

# Create a virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### 3. View API documentation

FastAPI auto-generates docs! Visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 4. Run the frontend

Option A: Use VS Code Live Server extension
- Install "Live Server" extension in VS Code
- Right-click `frontend/index.html` → "Open with Live Server"

Option B: Use Python's built-in server
```bash
cd frontend
python -m http.server 5500
```

Then visit `http://localhost:5500`

## Project Structure

```
ethereal-by-eva/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Environment variables
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── seed.py              # Sample data for testing
│   ├── routers/
│   │   ├── pieces.py        # Art piece endpoints
│   │   ├── cart.py          # Shopping cart
│   │   ├── checkout.py      # Payments & shipping
│   │   └── admin.py         # Admin management
│   └── requirements.txt
│
├── frontend/
│   ├── index.html           # Homepage
│   ├── browse.html          # Category browsing
│   ├── piece.html           # Single piece detail
│   ├── cart.html            # Shopping cart
│   ├── checkout.html        # Checkout flow
│   ├── success.html         # Order confirmation
│   ├── admin.html           # Admin panel
│   ├── css/
│   │   └── styles.css
│   └── js/
│       ├── api.js           # API communication
│       ├── main.js          # Shared utilities
│       ├── cart.js          # Cart logic
│       └── gallery.js       # Image gallery
│
├── .env.example             # Environment template
├── .gitignore
└── README.md
```

## Environment Variables

Copy `.env.example` to `.env` and fill in your API keys:

```
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
SHIPPO_API_KEY=shippo_test_...
ADMIN_PASSWORD=your-secure-password
```

## Deployment

See deployment guide in `/docs/deployment.md` (coming soon)
