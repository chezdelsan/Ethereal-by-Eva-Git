# Ethereal by Eva

One-of-a-kind art e-commerce platform.

## Tech Stack

- **Frontend**: HTML, CSS, Vanilla JavaScript
- **Backend**: Python, FastAPI, SQLAlchemy
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Payments**: Stripe
- **Shipping**: Shippo
- **Email**: Resend
- **Hosting**: Render

---

## Local Development

### 1. Backend Setup

```bash
cd backend
python -m venv venv

# Windows (Git Bash)
source venv/Scripts/activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
python seed.py
uvicorn main:app --reload
```

Backend runs at: `http://localhost:8000`

### 2. Frontend Setup

```bash
cd frontend
python -m http.server 5500
```

Frontend runs at: `http://localhost:5500`

### 3. Test Payment

Use Stripe test card: `4242 4242 4242 4242`

---

## Deployment to Render

### Step 1: Verify .gitignore

Make sure these are in `.gitignore` (they should be):
```
.env
*.db
```

### Step 2: Push to GitHub

```bash
git add .
git commit -m "Ready for deployment"
git push
```

### Step 3: Create PostgreSQL Database

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New** → **PostgreSQL**
3. Name: `ethereal-db`
4. Plan: Free
5. Click **Create Database**
6. Copy the **Internal Database URL**

### Step 4: Deploy Backend (Web Service)

1. Click **New** → **Web Service**
2. Connect your GitHub repo
3. Settings:
   - **Name**: `ethereal-api`
   - **Root Directory**: `ethereal-by-eva/backend`
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. Add **Environment Variables**:
   | Key | Value |
   |-----|-------|
   | `DATABASE_URL` | (paste Internal Database URL) |
   | `STRIPE_SECRET_KEY` | sk_test_... |
   | `RESEND_API_KEY` | re_... |
   | `ADMIN_EMAIL` | your@email.com |
   | `ADMIN_PASSWORD` | (choose a strong password) |
   | `SHIPPO_API_KEY` | shippo_test_... |
   | `FRONTEND_URL` | (your frontend URL, add after Step 5) |

5. Click **Create Web Service**
6. Copy your backend URL (e.g., `https://ethereal-api.onrender.com`)

### Step 5: Deploy Frontend (Static Site)

1. Click **New** → **Static Site**
2. Connect same GitHub repo
3. Settings:
   - **Name**: `ethereal-frontend`
   - **Root Directory**: `ethereal-by-eva/frontend`
   - **Build Command**: (leave empty)
   - **Publish Directory**: `.`

4. Click **Create Static Site**
5. Copy your frontend URL

### Step 6: Update URLs

1. **Frontend**: Edit `frontend/js/api.js`
   ```javascript
   baseUrl: 'https://ethereal-api.onrender.com'  // Your backend URL
   ```

2. **Backend**: In Render, add environment variable:
   - `FRONTEND_URL` = `https://ethereal-frontend.onrender.com`

3. Push changes to GitHub (Render auto-deploys)

### Step 7: Initialize Database

1. In Render, go to your backend service
2. Click **Shell** tab
3. Run: `python seed.py`

### Step 8: Set Up Stripe Webhook

1. Go to [Stripe Webhooks](https://dashboard.stripe.com/test/webhooks)
2. Click **Add endpoint**
3. URL: `https://ethereal-api.onrender.com/api/webhooks/stripe`
4. Events: Select `checkout.session.completed`
5. Copy the **Signing secret**
6. Add to Render environment variables:
   - `STRIPE_WEBHOOK_SECRET` = whsec_...

---

## Project Structure

```
ethereal-by-eva/
├── backend/
│   ├── routers/
│   │   ├── admin.py      # Admin CRUD
│   │   ├── cart.py       # Cart validation
│   │   ├── checkout.py   # Stripe + emails
│   │   └── pieces.py     # Public browsing
│   ├── config.py         # Settings
│   ├── database.py       # DB connection
│   ├── email_service.py  # Resend integration
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic schemas
│   ├── seed.py           # Sample data
│   └── main.py           # FastAPI app
│
├── frontend/
│   ├── js/
│   │   ├── api.js        # API client
│   │   ├── cart.js       # Cart logic
│   │   ├── gallery.js    # Image gallery
│   │   └── main.js       # Utilities
│   ├── css/styles.css
│   ├── index.html        # Homepage
│   ├── browse.html       # Shop page
│   ├── piece.html        # Detail page
│   ├── cart.html         # Cart
│   ├── checkout.html     # Checkout form
│   └── success.html      # Order confirmation
│
├── render.yaml           # Render blueprint (optional)
└── README.md
```

---

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | postgres://... |
| `STRIPE_SECRET_KEY` | Stripe API key | sk_test_... |
| `STRIPE_WEBHOOK_SECRET` | Webhook signing secret | whsec_... |
| `RESEND_API_KEY` | Resend email API key | re_... |
| `FROM_EMAIL` | Sender email | onboarding@resend.dev |
| `ADMIN_EMAIL` | Your notification email | you@email.com |
| `ADMIN_PASSWORD` | Admin panel password | (secure password) |
| `SHIPPO_API_KEY` | Shippo shipping key | shippo_test_... |
| `FRONTEND_URL` | Frontend URL for redirects | https://... |

---

## Going Live Checklist

- [ ] Switch Stripe to live mode (get live keys)
- [ ] Verify domain in Resend for custom sender email
- [ ] Set strong ADMIN_PASSWORD
- [ ] Add real art pieces (delete seed data)
- [ ] Set up custom domain (optional)
- [ ] Enable Stripe live webhook
