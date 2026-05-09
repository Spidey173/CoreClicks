# 🚀 CoreClicks — Interactive Web Applications Suite

CoreClicks is a modern Flask-powered web application suite featuring multiple interactive tools and mini-projects in a single dashboard-driven platform.

It combines productivity utilities, analytics, database integration, and responsive UI components into one clean portfolio-style application.

---

## ✨ Features

### 📱 Interactive Applications
- 🧮 Calculator
- 🔐 Password Strength Checker
- ✅ To-Do List Manager
- 📝 Notes Application
- ⏱ Stopwatch & Timer
- 💬 Random Quote Generator

### 📊 Analytics Dashboard
- Track project usage
- Monitor calculations performed
- View active tasks
- Store and analyze password strength history
- Database-powered statistics

### 💾 Persistent Storage
- SQLite database integration using SQLAlchemy
- CRUD operations for notes and tasks
- Password analysis history logging
- Project usage tracking

### 🎨 Modern UI
- Fully responsive design
- Bootstrap 5 styling
- Font Awesome icons
- Smooth animations and transitions
- Mobile-friendly layout

---

# 🛠 Tech Stack

## Backend
- Python
- Flask
- Flask-SQLAlchemy
- SQLite

## Frontend
- HTML5
- CSS3
- JavaScript
- Bootstrap 5
- Font Awesome

## Data & Analytics
- Pandas
- NumPy
- Matplotlib

---

# 📂 Project Structure

```bash
CoreClicks/
│
├── app.py
├── analytics.py
├── database.db
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   │
│   └── projects/
│       ├── calculator.html
│       ├── password_strength.html
│       ├── todo.html
│       ├── notes.html
│       ├── stopwatch.html
│       └── quotes.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── *.csv
└── README.md
