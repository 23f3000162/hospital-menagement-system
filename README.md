# 🏥 Hospital Management System (HMS)

<div align="center">

![Vue.js](https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vue.js&logoColor=4FC08D)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-CC2927?style=for-the-badge&logo=databricks&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=JSON%20web%20tokens&logoColor=white)

**A full-stack web application for managing hospital operations — doctors, patients, appointments, and more.**

</div>

---

## Table of Contents

- [Project Description](#-project-description)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Architecture](#-project-architecture)
- [Folder Structure](#-folder-structure)
- [Installation Steps](#-installation-steps)
- [Running the Application](#-running-the-application)
- [API Overview](#-api-overview)
- [Security Features](#-security-features)
- [Future Improvements](#-future-improvements)
- [Author](#-author)

---

## Project Description

The **Hospital Management System (HMS)** is a modern, full-stack web application built to digitize and streamline core hospital operations. It provides a secure, role-based platform for **Admins**, **Doctors**, and **Patients** to manage appointments, medical records, and hospital resources efficiently.

The application is built on a **Vue.js SPA frontend** and a **Flask REST API backend**, with **JWT-based authentication**, **Redis caching**, and **Celery** for handling background tasks asynchronously.

> 🎓 Developed as a University Project — demonstrating full-stack development, REST API design, and secure authentication practices.

---

## ✨ Features

### 🖥️ Admin Dashboard
- Overview of total doctors, patients, and appointments at a glance
- Add, update, search, and remove doctor profiles
- Manage all appointments across the hospital

### Doctor Management
- Create and update doctor profiles with specialization and department
- View assigned appointments and patient history

### Patient Management
- Search patients by name or contact number
- View patient details and appointment records

### ppointment Management
- Book, view, update, and cancel appointments
- Filter appointments by doctor, patient, or date

###  Authentication & Authorization
- Secure login with **JWT tokens**
- Role-based access control: **Admin**, **Doctor**, **Patient**
- Protected routes on both frontend and backend

### Performance & Background Tasks
- **Redis caching** for frequently accessed data
- **Celery** for async tasks (e.g., email notifications, report generation)

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Vue.js 3, Vue Router |
| **Backend** | Flask (Python) |
| **Database** | SQLAlchemy ORM (SQLite / PostgreSQL) |
| **Authentication** | JWT (JSON Web Tokens) |
| **Cache / Broker** | Redis |
| **Task Queue** | Celery |
| **API Style** | RESTful |

---

##  Project Architecture

```
┌─────────────────────────────────────────────────────┐
│                    CLIENT LAYER                      │
│           Vue.js SPA  +  Vue Router                  │
│     Admin Dashboard | Doctor Pages | Patient Pages   │
└────────────────────┬────────────────────────────────┘
                     │  HTTP / REST API calls
                     ▼
┌─────────────────────────────────────────────────────┐
│                   BACKEND LAYER                      │
│              Flask REST API (Python)                 │
│   JWT Auth  |  Role-Based Access  |  API Routes      │
└──────┬──────────────────────┬───────────────────────┘
       │                      │
       ▼                      ▼
┌─────────────┐      ┌────────────────────┐
│  SQLAlchemy │      │   Redis (Cache +   │
│  ORM / DB   │      │   Message Broker)  │
│  (Doctors,  │      └────────┬───────────┘
│  Patients,  │               │
│  Appts...)  │      ┌────────▼───────────┐
└─────────────┘      │   Celery Workers   │
                     │  (Async Tasks)     │
                     └────────────────────┘
```

---

## Folder Structure

```
hospital-management-system/
│
├── frontend/                        # Vue.js Frontend
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── assets/                  # Images, fonts, global CSS
│   │   ├── components/              # Reusable Vue components
│   │   │   ├── Navbar.vue
│   │   │   ├── Sidebar.vue
│   │   │   └── StatsCard.vue
│   │   ├── views/                   # Page-level views
│   │   │   ├── Dashboard.vue
│   │   │   ├── Doctors.vue
│   │   │   ├── Patients.vue
│   │   │   ├── Appointments.vue
│   │   │   └── Login.vue
│   │   ├── router/
│   │   │   └── index.js             # Vue Router config
│   │   ├── store/                   # State management
│   │   ├── services/
│   │   │   └── api.js               # Axios API calls
│   │   └── App.vue
│   └── package.json
│
├── backend/                         # Flask Backend
│   ├── app/
│   │   ├── __init__.py              # App factory
│   │   ├── models/                  # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── doctor.py
│   │   │   ├── patient.py
│   │   │   └── appointment.py
│   │   ├── routes/                  # API route blueprints
│   │   │   ├── auth.py
│   │   │   ├── doctors.py
│   │   │   ├── patients.py
│   │   │   └── appointments.py
│   │   ├── tasks/
│   │   │   └── celery_tasks.py      # Celery async tasks
│   │   └── utils/
│   │       ├── auth_helpers.py      # JWT utilities
│   │       └── cache.py             # Redis cache helpers
│   ├── config.py                    # App configuration
│   ├── celery_worker.py             # Celery entry point
│   ├── requirements.txt
│   └── run.py                       # Flask entry point
│
├── .env                             # Environment variables
└── README.md
```

---

##  Installation Steps

### Prerequisites

Make sure the following are installed on your system:

- Python 3.9+
- Node.js 16+ & npm
- Redis Server
- Git

---

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/hospital-management-system.git
cd hospital-management-system
```

---

### 2️⃣ Backend Setup

```bash
# Navigate to backend folder
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env and set your SECRET_KEY, DATABASE_URL, REDIS_URL
```

**`.env` example:**
```env
SECRET_KEY=your_super_secret_key
DATABASE_URL=sqlite:///hms.db
REDIS_URL=redis://localhost:6379/0
JWT_EXPIRY_HOURS=24
```

```bash
# Initialize the database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

---

### 3️⃣ Frontend Setup

```bash
# Navigate to frontend folder
cd ../frontend

# Install dependencies
npm install
```

---

## 🚀 Running the Application

Open **4 separate terminals** and run each of the following:

**Terminal 1 — Flask Backend**
```bash
cd backend
source venv/bin/activate
python run.py
# Runs at: http://localhost:5000
```

**Terminal 2 — Redis Server**
```bash
redis-server
# Runs at: redis://localhost:6379
```

**Terminal 3 — Celery Worker**
```bash
cd backend
source venv/bin/activate
celery -A celery_worker.celery worker --loglevel=info
```

**Terminal 4 — Vue.js Frontend**
```bash
cd frontend
npm run dev
# Runs at: http://localhost:5173
```

---

## 📡 API Overview

Base URL: `http://localhost:5000/api`

### 🔐 Auth Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `POST` | `/auth/login` | Login and receive JWT token | Public |
| `POST` | `/auth/logout` | Invalidate token | Authenticated |
| `GET` | `/auth/me` | Get current user info | Authenticated |

### 👨‍⚕️ Doctor Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `GET` | `/doctors` | Get all doctors | Admin |
| `POST` | `/doctors` | Add a new doctor | Admin |
| `GET` | `/doctors/:id` | Get doctor by ID | Admin, Doctor |
| `PUT` | `/doctors/:id` | Update doctor info | Admin |
| `DELETE` | `/doctors/:id` | Remove a doctor | Admin |

### 🧑‍🤝‍🧑 Patient Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `GET` | `/patients` | Get all patients | Admin |
| `GET` | `/patients/search?q=name` | Search by name/contact | Admin |
| `GET` | `/patients/:id` | Get patient by ID | Admin, Doctor |
| `DELETE` | `/patients/:id` | Remove patient record | Admin |

### 📅 Appointment Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `GET` | `/appointments` | Get all appointments | Admin |
| `POST` | `/appointments` | Book an appointment | Admin, Patient |
| `PUT` | `/appointments/:id` | Update appointment | Admin, Doctor |
| `DELETE` | `/appointments/:id` | Cancel appointment | Admin |

> All protected endpoints require the header: `Authorization: Bearer <token>`

---

## 🔒 Security Features

- **JWT Authentication** — Stateless, token-based login system with configurable expiry
- **Role-Based Access Control (RBAC)** — Admin, Doctor, and Patient roles with route-level protection
- **Password Hashing** — Passwords stored using `bcrypt` (never in plaintext)
- **Protected Vue Routes** — Frontend routes guarded with navigation guards
- **Redis Token Blacklisting** — Logged-out tokens are invalidated via Redis
- **Environment Variables** — All secrets managed via `.env`, never hardcoded

---

## 🔮 Future Improvements

- [ ] 📧 Email notifications for appointment confirmations (via Celery)
- [ ] 📊 Analytics dashboard with charts and reports
- [ ] 📱 Mobile-responsive UI improvements
- [ ] 🧾 PDF report generation for patient records
- [ ] 🔔 Real-time notifications using WebSockets
- [ ] 🌐 Multi-language support (i18n)
- [ ] 🐳 Docker containerization for easy deployment
- [ ] ☁️ Cloud deployment (AWS / Render / Railway)

---

## 👨‍💻 Author

<div align="center">

**[Your Name]**
*BS in data Science — [iit madras]*
*[2027]*

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/23f3000162)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/your-profile)

</div>

---

<div align="center">


</div>
