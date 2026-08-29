# CoreClicks — All-in-One Full Stack Web Utility Hub

<p align="center">
  <a href="https://coreclicks.onrender.com" target="_blank">
    <img src="https://img.shields.io/badge/🚀_LIVE_DEMO-coreclicks.onrender.com-4f46e5?style=for-the-badge&logo=render&logoColor=white" alt="Live Demo" height="38">
  </a>
</p>

<p align="center">
  <a href="https://coreclicks.onrender.com"><strong>🌐 https://coreclicks.onrender.com</strong></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/Flask-3.x-000000?style=flat-square&logo=flask&logoColor=white" alt="Flask 3">
  <img src="https://img.shields.io/badge/Database-Neon%20PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Frontend-Bootstrap%205%20%2B%20JS-7952B3?style=flat-square&logo=bootstrap&logoColor=white" alt="Bootstrap 5">
  <img src="https://img.shields.io/badge/Deployment-Render-46E3B7?style=flat-square&logo=render&logoColor=black" alt="Render">
</p>

---

## ⚡ Quick Try (Live App)

Experience the live app right now:
👉 **[Launch CoreClicks Live Demo](https://coreclicks.onrender.com)**

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

10. 🔗 **URL Shortener & QR Studio (`/url-shortener`)**
    - Generate short links with custom aliases and click-rate analytics.
    - Export downloadable high-resolution QR codes in PNG and SVG.

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

### Deploying to Render
This repository includes a [`render.yaml`](render.yaml) blueprint ready for continuous deployment.

1. Create a **Web Service** on [Render](https://render.com) connected to this repository.
2. Set the build and start commands:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app --workers 4 --threads 2 --timeout 60`
3. Configure Environment Variables:
   - `FLASK_ENV`: `production`
   - `SECRET_KEY`: *(generate a secure random secret)*
   - `DATABASE_URL`: `postgresql://<user>:<password>@<host>/<database>?sslmode=require`

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
├── render.yaml               # Cloud deployment blueprint
├── requirements.txt          # Python dependencies
├── run.py                    # Local development runner
├── run.sh                    # Automated setup script
└── wsgi.py                   # Production WSGI entry point
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
- **Database**: PostgreSQL (Production) / SQLite (Local fallback)
- **Data & Processing**: Pandas, NumPy, Pillow, PyPDF, Qrcode, Requests
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5, Chart.js

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.
