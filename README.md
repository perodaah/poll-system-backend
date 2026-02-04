# ALX PROJECT NEXUS

# Poll System Backend API

A Django REST API for creating and managing online polls with real-time voting and results.


## 🚀 Features

- **Poll Management**: Create, read, update, and delete polls with multiple options
- **Voting System**: Support for both authenticated and anonymous voting
- **Real-time Results**: Live vote counting with percentage calculations
- **Duplicate Prevention**: Database-level constraints prevent duplicate votes
- **JWT Authentication**: Secure token-based authentication
- **Privacy Protection**: Anonymous voter IP addresses are hashed
- **REST API**: Full CRUD operations with Django REST Framework
- **Interactive Docs**: Swagger UI and ReDoc API documentation
- **Query Optimization**: Efficient database queries with select_related and prefetch_related

## 📋 Table of Contents

- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [API Endpoints](#api-endpoints)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

## 🛠 Tech Stack

- **Backend**: Django 5.0.1
- **API Framework**: Django REST Framework 3.14.0
- **Database**: PostgreSQL 15+
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Documentation**: drf-spectacular
- **Language**: Python 3.12

## 📦 Installation

### Prerequisites

- Python 3.12+
- PostgreSQL 15+
- pip
- virtualenv (recommended)

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/perodaah/poll-system-backend.git
cd poll-system-backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
cd pollsystem
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

## 🔐 Environment Variables

Create a `.env` file in the `pollsystem` directory:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DB_NAME=poll_system_db
DB_USER=poll_admin
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

**Generate a secret key:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 🗄 Database Setup

1. **Create PostgreSQL database and user**
```sql
CREATE DATABASE poll_system_db;
CREATE USER poll_admin WITH PASSWORD 'your_secure_password';
ALTER DATABASE poll_system_db OWNER TO poll_admin;
GRANT ALL PRIVILEGES ON DATABASE poll_system_db TO poll_admin;
GRANT ALL ON SCHEMA public TO poll_admin;
```

2. **Run migrations**
```bash
python manage.py migrate
```

3. **Create superuser (optional)**
```bash
python manage.py createsuperuser
```

## 🚀 Running the Application

### Development Server
```bash
python manage.py runserver
```

The API will be available at: `http://localhost:8000/api/`

### Access Points

- **API Root**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/
- **Swagger Docs**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/

## 📖 API Documentation

Interactive API documentation is available at:

- **Swagger UI**: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- **ReDoc**: [http://localhost:8000/api/redoc/](http://localhost:8000/api/redoc/)

## 🔌 API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register/` | Register new user | No |
| POST | `/api/auth/login/` | Login and get JWT tokens | No |
| POST | `/api/auth/refresh/` | Refresh access token | No |
| GET | `/api/auth/profile/` | Get user profile | Yes |

### Polls

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/polls/` | List all active polls | No |
| POST | `/api/polls/` | Create new poll | Yes |
| GET | `/api/polls/{id}/` | Get poll details | No |
| PUT/PATCH | `/api/polls/{id}/` | Update poll | Yes (Owner) |
| DELETE | `/api/polls/{id}/` | Delete poll | Yes (Owner) |

### Voting

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/polls/{id}/vote/` | Cast a vote | No |
| GET | `/api/polls/{id}/results/` | Get poll results | No |

## 📝 API Usage Examples

### Register a User
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "SecurePass123!"
  }'
```

### Create a Poll
```bash
curl -X POST http://localhost:8000/api/polls/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "title": "Favorite Programming Language?",
    "description": "Vote for your favorite language",
    "options": [
      {"text": "Python", "order_index": 1},
      {"text": "JavaScript", "order_index": 2},
      {"text": "Go", "order_index": 3}
    ]
  }'
```

### Cast a Vote
```bash
curl -X POST http://localhost:8000/api/polls/1/vote/ \
  -H "Content-Type: application/json" \
  -d '{"option_id": 1}'
```

### Get Results
```bash
curl http://localhost:8000/api/polls/1/results/
```

## 🧪 Running Tests

### Run all tests
```bash
python manage.py test
```

### Run specific test file
```bash
python manage.py test polls.tests
```

### Run integration tests
```bash
python test_auth.py
python test_polls.py
python test_voting.py
```

### Test coverage
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## 📁 Project Structure
```
poll-system-backend/
├── pollsystem/                 # Main Django project
│   ├── pollsystem/
│   │   ├── settings.py        # Project settings
│   │   ├── urls.py            # Main URL configuration
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── polls/                 # Polls app
│   │   ├── models.py          # Database models
│   │   ├── serializers.py     # DRF serializers
│   │   ├── views.py           # API views
│   │   ├── permissions.py     # Custom permissions
│   │   ├── urls.py            # App URL routing
│   │   ├── admin.py           # Admin configuration
│   │   ├── tests.py           # Unit tests
│   │   └── migrations/        # Database migrations
│   ├── manage.py
│   ├── requirements.txt
│   └── .env
├── test_auth.py               # Authentication tests
├── test_polls.py              # Poll API tests
├── test_voting.py             # Voting system tests
├── .gitignore
└── README.md
```

## 🗃 Database Schema

### Models

- **User**: Django's built-in user model
- **Poll**: Poll questions with title, description, creator, and expiry
- **Option**: Poll answer choices
- **Vote**: Individual votes with duplicate prevention

### Relationships
```
User (1) ──── (Many) Poll
Poll (1) ──── (Many) Option
Poll (1) ──── (Many) Vote
Option (1) ──── (Many) Vote
```

## 🔒 Security Features

- JWT token-based authentication
- Password hashing with PBKDF2
- Database-level duplicate vote prevention
- IP address hashing for anonymous voters
- Owner-only permissions for poll updates/deletes
- CORS configuration
- SQL injection protection (Django ORM)

## 🚀 Deployment

This project can be deployed to:
- Railway
- Render
- Heroku
- AWS/Azure/GCP

See deployment documentation for platform-specific instructions.

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Perodaah**
- GitHub: [@perodaah](https://github.com/perodaah)

## 🙏 Acknowledgments

- Django Documentation
- Django REST Framework
- ALX Africa - Project Nexus

[![Django](https://img.shields.io/badge/Django-5.0.1-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.14.0-red.svg)](https://www.django-rest-framework.org/)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)

---
