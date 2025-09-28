# 🗳️ Online Poll System

An **online polling platform** with a **Django REST API backend**.
Users can create polls, vote in real-time, and view live results with dynamic visualizations.

---

## 🚀 Features

### Backend (Django + PostgreSQL)

* User authentication (JWT with refresh & access tokens).
* Create polls with multiple options.
* Secure voting system (no duplicate votes per user).
* Real-time results computation (optimized queries).
* API documentation using **Swagger**.
* CORS-enabled for frontend integration.

---

## 🛠️ Tech Stack

* **Backend:** Django, Django REST Framework, PostgreSQL, SimpleJWT, drf-yasg, django-filters
* **Deployment:** Render (backend + PostgreSQL)

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Tsegaw-Mao/online_poll_backend.git
cd online_poll_backend
```

### 2. Backend Setup

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

* Create a `.env` file:

```env
DJANGO_SECRET_KEY=your-secret-key
DEBUG=False
POSTGRES_DB=online_poll
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

* Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

* Start the backend:

```bash
python manage.py runserver
```

API will be available at:
`http://localhost:8000/api/`
Swagger docs: `http://localhost:8000/api/docs/`

---

### 3. Deployment

#### Backend on Render

* Create a **Render PostgreSQL** instance.
* Update `.env` with Render database credentials.
* Deploy Django backend on Render.
* Add your frontend domain to `CORS_ALLOWED_ORIGINS` in `settings.py`.


## 🔑 API Endpoints

### Authentication

* `POST /api/auth/login/` → Get access & refresh tokens
* `POST /api/auth/refresh/` → Refresh access token
* `POST /api/auth/register/` → Registers Users

### Polls

* `GET /api/polls/` → List polls (filter, sort, paginate)
* `POST /api/polls/` → Create a new poll
* `GET /api/polls/{id}/` → Get poll details
* `POST /api/polls/{id}/vote/` → Vote on a poll
* `GET /api/polls/{id}/results/` → View results

---

## 🤝 Contributing

Pull requests are welcome! Please open an issue before making major changes.

---

## 📜 License

ALX License © 2025 Your Name

## Contact

 `Email` : tsegawjohnj@gmail.com
