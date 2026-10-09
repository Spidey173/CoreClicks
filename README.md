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

CoreClicks is a full-stack developer and daily productivity hub built with Flask and PostgreSQL. It combines 11 self-contained utilities—from developer essentials like an anti-SSRF REST API tester and webhook inspector to everyday productivity tools like a Kanban board and CSV analytics—into a unified, session-authenticated web platform.

### 🎯 Key Architectural Highlights
- **Application Factory Pattern & Modular Blueprints**: Each tool is implemented as an isolated Flask blueprint with dedicated services for separation of concerns.
- **Security-First Utility Design**: Built-in protection against SSRF in outbound API testing and safe AST parsing for mathematical evaluation instead of insecure `eval()`.
- **Relational Data Modeling**: Powered by SQLAlchemy with Postgres (Neon Serverless) and connection pooling.
- **Production-Ready Deployment**: Pre-configured for serverless WSGI deployment on Vercel with automated test coverage via `pytest`.

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

## 🌟 Built-In Developer & Productivity Tools

CoreClicks brings together 11 utility modules in one clean, unified workspace:

1. 🧮 **Calculator (`/calculator`)**
   - Standard arithmetic and scientific operations (trig functions, powers, logarithms, factorials) with safe sandboxed evaluation using Python's `ast` parsing.
   - Per-user calculation history.

2. 🔐 **Password Auditor & Generator (`/password-security`)**
   - Password strength analysis and Shannon entropy computation.
   - Cryptographically secure password and passphrase generator (`secrets` module).

3. 📋 **Task Manager & Kanban Board (`/tasks`)**
   - Drag-and-drop Kanban workflow (`To Do`, `In Progress`, `Review`, `Done`).
   - Priority levels, category filtering, and status updates.

4. 📝 **Markdown Notes (`/notes`)**
   - Note-taking workspace with live split Markdown preview.
   - Folder categorization, pinned notes, and export options (`.md`, `.html`).

5. 🌐 **REST API Tester (`/api-tester`)**
   - Browser HTTP client supporting standard methods (`GET`, `POST`, `PUT`, `DELETE`, `PATCH`).
   - Request history, header inspection, latency timing, and SSRF validation protecting internal network boundaries.

6. 📊 **CSV Analytics (`/analytics`)**
   - Tabular dataset upload for statistical summaries, missing value detection, and Chart.js visualizations using Pandas.

7. 💰 **Expense Tracker (`/expenses`)**
   - Income and expense logging with merchant tags and category breakdowns.
   - Monthly summaries and budget threshold tracking.

8. 📁 **File & Document Converter (`/file-tools`)**
   - **Images**: Resize, compress, rotate, and format conversion (PNG, JPG, WebP) powered by Pillow.
   - **PDFs**: Document merging and custom page range extraction powered by PyPDF.

9. 🎨 **Color Palette & Accessibility Tool (`/color-tools`)**
   - Color harmony generation (Complementary, Triadic, Analogous, Monochromatic).
   - WCAG 2.1 contrast ratio calculator for accessibility checks.

10. 🔗 **URL Shortener & QR Generator (`/url-shortener`)**
    - High-performance Base62 unique short-code generation (Snowflake ID inspired).
    - In-memory Bloom Filter (with optional Redis support) as a fast pre-lookup to avoid unnecessary database queries on invalid codes.
    - High-resolution QR code generation (PNG / SVG).

11. 🛰️ **Webhook Inspector & Mock Endpoint (`/webhooks`)**
    - Temporary endpoints (`/hook/<token>`) to capture and test incoming webhooks (Stripe, GitHub, etc.).
    - Inspection of request headers, HMAC signatures, query params, and raw JSON payloads.

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
