# CoreClicks — All-in-One Full Stack Web Utility Hub

A clean, modern web application that combines 10 daily productivity, developer, and data utilities into a single, easy-to-use dashboard.

Built with **Python (Flask)**, **SQLAlchemy**, **Bootstrap 5**, and **JavaScript**.

---

## 🌟 Features & Included Tools

CoreClicks brings together 10 useful tools in one place:

1. **Safe Calculator Engine (`/calculator`)**
   - Perform basic and scientific calculations (trig functions, powers, logarithms, factorials).
   - Keeps your recent calculation history so you never lose track.

2. **Password Security Auditor (`/password-security`)**
   - Check password strength, calculate entropy, and get tips to make passwords safer.
   - Built-in secure password and passphrase generator.

3. **Task Manager & Kanban Board (`/tasks`)**
   - Organize your to-dos with an interactive drag-and-drop Kanban board (`To Do`, `In Progress`, `Review`, `Done`).
   - Filter by category and priority.

4. **Notes Workspace (`/notes`)**
   - Write notes with live Markdown formatting preview.
   - Categorize notes into folders, pin important notes, and export as `.md` or `.html`.

5. **REST API Tester (`/api-tester`)**
   - Test web APIs directly from your browser (`GET`, `POST`, `PUT`, `DELETE`).
   - Format JSON bodies, inspect headers, and measure response times.

6. **CSV Analytics Studio (`/analytics`)**
   - Upload any CSV dataset to instantly see row/column counts, missing data, summary stats, and visual charts.

7. **Expense Tracker (`/expenses`)**
   - Log income and expenses with categories.
   - View monthly balance summaries and category budgets.

8. **File Converter Studio (`/file-tools`)**
   - **Image Tools**: Resize, compress, rotate, and convert images (PNG, JPG, WebP).
   - **PDF Tools**: Merge multiple PDFs or split/extract specific page ranges.

9. **Color Palette & Accessibility Studio (`/color-tools`)**
   - Generate color combinations (Complementary, Triadic, etc.).
   - Check WCAG text contrast ratios for readability.

10. **URL Shortener & QR Studio (`/url-shortener`)**
    - Create clean short links with custom aliases.
    - Generate downloadable QR codes (PNG / SVG) and track link clicks.

---

## 🚀 How to Run the Project

### Option 1: One-Step Quickstart (Recommended)

Simply open your terminal in the project folder and run:

```bash
./run.sh
```

`run.sh` will automatically create the virtual environment, install all required dependencies, seed default accounts, and launch the server on **`http://127.0.0.1:5000`**.

---

### Option 2: Manual Setup

If you prefer to run the commands manually:

```bash
# 1. Create a virtual environment
python3 -m venv venv

# 2. Activate the virtual environment
# On macOS / Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the application
python3 run.py
```

Once running, open your web browser and go to:
👉 **`http://127.0.0.1:5000`**

---

## 🔑 Default Login Accounts

When you start the project for the first time, sample accounts are automatically created for you:

| Account Type | Email | Password |
|---|---|---|
| **Admin** | `admin@coreclicks.dev` | `Admin@12345` |
| **User** | `user@coreclicks.dev` | `User@12345` |

*(You can also register a new account anytime on the Sign Up page).*

---

## 📁 Project Structure

```
CoreClicks/
├── app/
│   ├── config.py         # App configuration settings
│   ├── extensions.py     # Database and authentication setup
│   ├── __init__.py       # Application factory & initial demo data
│   ├── models/           # Database models (User, Task, Note, Expense, etc.)
│   ├── routes/           # Web page and API route handlers
│   ├── services/         # Core business logic for each tool
│   ├── static/           # CSS stylesheets, images, and JavaScript files
│   └── templates/        # HTML templates for pages and tools
├── tests/                # Automated unit tests
├── requirements.txt      # Python dependencies list
├── run.py                # Python application runner
└── run.sh                # Automated setup & start script
```

---

## 🧪 Running Tests

To run the automated tests:

```bash
python3 -m pytest
```

---

## 🛠️ Built With

- **Backend**: Python 3, Flask, Flask-Login, Flask-Bcrypt, SQLAlchemy
- **Data & Processing**: Pandas, Pillow, PyPDF, Qrcode
- **Frontend**: HTML5, CSS3, Vanilla JavaScript, Bootstrap 5, Chart.js
