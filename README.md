# CoreClicks — All-in-One Full Stack Web Utility Hub

<p align="center">
  <a href="https://coreclicks.vercel.app" target="_blank">
    <img src="https://img.shields.io/badge/🚀_LIVE_DEMO-coreclicks.vercel.app-000000?style=for-the-badge&logo=vercel&logoColor=white" alt="Live Demo" height="38">
  </a>
</p>

<p align="center">
  <a href="https://coreclicks.vercel.app"><strong>🌐 https://coreclicks.vercel.app</strong></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/Flask-3.x-000000?style=flat-square&logo=flask&logoColor=white" alt="Flask 3">
  <img src="https://img.shields.io/badge/Database-Neon%20PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Frontend-Bootstrap%205%20%2B%20JS-7952B3?style=flat-square&logo=bootstrap&logoColor=white" alt="Bootstrap 5">
  <img src="https://img.shields.io/badge/Deployment-Vercel-000000?style=flat-square&logo=vercel&logoColor=white" alt="Vercel">
</p>

---

## ⚡ Quick Try (Live App)

Experience the live app right now:
👉 **[Launch CoreClicks Live Demo](https://coreclicks.vercel.app)**

### 🔑 Instant Demo Accounts:
| Account Type | Email | Password | Access Level |
|---|---|---|---|
| 👑 **Admin** | `admin@coreclicks.dev` | `Admin@12345` | Full Admin Panel & App Analytics |
| 👤 **User** | `user@coreclicks.dev` | `User@12345` | Standard User Dashboard & Tools |

*(Or register your own private account on the Sign Up page).*

---

## 🌟 Features & 10 Built-In Tools

CoreClicks brings together 10 robust tools in one unified, sleek dashboard:

1. 🧮 **Safe Calculator Engine (`/calculator`)**
   - Basic and scientific operations (trig functions, powers, logarithms, factorials) with safe sandboxed evaluation.
   - Saves calculation history per user account.

2. 🔐 **Password Security Auditor (`/password-security`)**
   - Password strength analyzer, Shannon entropy calculator, and vulnerability tips.
   - Built-in secure password and passphrase generator.

3. 📋 **Task Manager & Kanban Board (`/tasks`)**
   - Interactive drag-and-drop Kanban workflow (`To Do`, `In Progress`, `Review`, `Done`).
   - Priority tagging, category filtering, and progress tracking.

4. 📝 **Notes Workspace (`/notes`)**
   - Full-featured note-taking studio with live split Markdown preview.
   - Categorize by folders, pin essential notes, and export to `.md` or `.html`.

5. 🌐 **REST API Tester (`/api-tester`)**
   - Browser-based HTTP client (`GET`, `POST`, `PUT`, `DELETE`, `PATCH`).
   - Request history, JSON payload formatting, header inspection, and response timing.

6. 📊 **CSV Analytics Studio (`/analytics`)**
   - Upload tabular datasets for instant summary statistics, missing-value inspection, and Chart.js visualizations.

7. 💰 **Expense Tracker (`/expenses`)**
   - Income and expense tracking with category breakdowns and merchant tagging.
   - Real-time monthly balance calculations and budget limit monitoring.

8. 📁 **File Converter Studio (`/file-tools`)**
   - **Images**: Resize, compress, rotate, and convert formats (PNG, JPG, WebP).
   - **PDFs**: Merge multiple documents or extract/split custom page ranges.

9. 🎨 **Color Palette & Accessibility Studio (`/color-tools`)**
   - Color harmony generator (Complementary, Triadic, Analogous, Monochromatic).
   - WCAG 2.1 text contrast ratio auditor for accessibility compliance.

10. 🔗 **Distributed URL Shortener & QR Studio (`/url-shortener`)**
    - High-throughput 64-bit Twitter Snowflake Base62 ID engine (zero collision round-trips).
    - Probabilistic Bloom Filter shield against cache penetration & crawler scans.
    - Export downloadable high-resolution QR codes in PNG and SVG.

11. 🛰️ **Developer Webhook Interceptor & Mock Console (`/webhooks`)**
    - Live temporary endpoints (`/hook/<token>`) to capture external webhooks (Stripe, GitHub, Razorpay).
    - Inspect captured headers, HMAC signatures, query parameters, and raw JSON payloads.

---

## 🚀 Getting Started Locally

### Option 1: One-Step Quickstart (macOS / Linux)

```bash
./run.sh
```

`run.sh` will automatically create the virtual environment, install dependencies, prepare the database, and launch the server on **`http://127.0.0.1:5000`**.

---

### Option 2: Manual Setup

```bash
# 1. Clone the repository
git clone https://github.com/Spidey173/CoreClicks.git
cd CoreClicks

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install required packages
pip install -r requirements.txt

# 4. (Optional) Configure environment variables
cp .env.example .env

# 5. Launch the application
python3 run.py
```

Open your browser and navigate to: **`http://127.0.0.1:5000`**

---

## ☁️ Deployment

### Deploying to Vercel
This repository includes a [`vercel.json`](vercel.json) blueprint ready for continuous deployment.

1. Import this repository into [Vercel](https://vercel.com).
2. Configure Environment Variables in the Vercel dashboard:
   - `FLASK_ENV`: `production`
   - `SECRET_KEY`: *(generate a secure random secret)*
   - `DATABASE_URL`: `postgresql://<user>:<password>@<host>/<database>?sslmode=require` (e.g. Neon PostgreSQL)
3. Deploy! Vercel handles dependencies from `requirements.txt` and routes all requests via `wsgi.py`.

---

## 📁 Project Structure

```
CoreClicks/
├── app/
│   ├── config.py             # Environment & database configuration
│   ├── extensions.py         # SQLAlchemy, Bcrypt, and LoginManager initialization
│   ├── __init__.py           # Flask app factory & initial data seeding
│   ├── models/               # SQLAlchemy ORM models (User, Task, Note, Expense, etc.)
│   ├── routes/               # Modular Blueprint route controllers
│   ├── services/             # Core business logic for each utility
│   ├── static/               # CSS styles, assets, and modular JavaScript
│   └── templates/            # Jinja2 HTML templates & utility layouts
├── tests/                    # Pytest test suite & route coverage
├── .env.example              # Example environment configuration
├── vercel.json               # Vercel serverless deployment config
├── requirements.txt          # Python dependencies
├── run.py                    # Local development runner
├── run.sh                    # Automated setup script
└── wsgi.py                   # Production WSGI / Vercel entry point
```

---

## 🧪 Testing

Run the automated test suite with pytest:

```bash
python3 -m pytest
```

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11+, Flask, Flask-SQLAlchemy, Flask-Login, Flask-Bcrypt, Gunicorn
- **Database**: PostgreSQL (Neon Serverless PostgreSQL)
- **Data & Processing**: Pandas, NumPy, Pillow, PyPDF, Qrcode, Requests
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5, Chart.js

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.
