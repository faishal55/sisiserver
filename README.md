# Simple LMS - Learning Management System

A complete Django-based Learning Management System with REST API, JWT authentication, Redis caching, and role-based access control.

## 🎯 Features

- **Custom User Model** with role-based access control (Admin, Dosen, Mahasiswa)
- **Course Management** with lessons, assignments, and enrollments
- **REST API** using Django Ninja with automatic Swagger documentation
- **JWT Authentication** for secure API access
- **Redis Caching** for improved performance
- **Django Admin** interface for easy management
- **Comprehensive Testing** with unit tests

## 📋 Requirements

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

## 🚀 Installation

### Option 1: Local Setup

1. **Clone the repository**
```bash
cd c:\laragon\www\tugasSS
```

2. **Create virtual environment**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

3. **Install dependencies**
```powershell
pip install -r requirements.txt
```

4. **Setup environment variables**
```powershell
Copy-Item .env.example .env
# Edit .env with your configuration
```

5. **Run PostgreSQL and Redis**
Make sure PostgreSQL and Redis are running locally.

6. **Run migrations**
```powershell
python manage.py makemigrations
python manage.py migrate
```

7. **Create superuser**
```powershell
python manage.py createsuperuser
```

8. **Seed database**
```powershell
python manage.py seed_data
```

9. **Run development server**
```powershell
python manage.py runserver
```

### Option 2: Docker Setup

1. **Build and run with Docker Compose**
```powershell
docker-compose up -d --build
```

2. **Run migrations**
```powershell
docker-compose exec web python manage.py migrate
```

3. **Seed database**
```powershell
docker-compose exec web python manage.py seed_data
```

## 📚 API Documentation

Once the server is running, access:
- **Swagger UI**: http://localhost:8000/api/lms/docs
- **Django Admin**: http://localhost:8000/admin

## 🔑 Test Accounts

After running `seed_data` command:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@lms.com | admin123 |
| Dosen | dosen1@lms.com | dosen123 |
| Mahasiswa | student1@lms.com | student123 |

## 🔧 API Endpoints

### Authentication
- `POST /api/lms/auth/register` - Register new user
- `POST /api/lms/auth/login` - Login and get JWT token
- `GET /api/lms/auth/me` - Get current user

### Users
- `GET /api/lms/users` - List all users (Admin only)
- `GET /api/lms/users/{id}` - Get user details
- `PUT /api/lms/users/{id}` - Update user
- `DELETE /api/lms/users/{id}` - Delete user (Admin only)

### Courses
- `GET /api/lms/courses` - List all courses
- `GET /api/lms/courses/{id}` - Get course details
- `POST /api/lms/courses` - Create course (Dosen/Admin)
- `PUT /api/lms/courses/{id}` - Update course
- `DELETE /api/lms/courses/{id}` - Delete course

### Enrollments
- `POST /api/lms/enrollments` - Enroll in course (Mahasiswa)
- `GET /api/lms/enrollments/my` - Get my enrollments

### Lessons
- `POST /api/lms/lessons` - Create lesson (Dosen/Admin)
- `PUT /api/lms/lessons/{id}` - Update lesson
- `DELETE /api/lms/lessons/{id}` - Delete lesson

### Assignments
- `POST /api/lms/assignments` - Create assignment (Dosen/Admin)
- `GET /api/lms/assignments/{id}` - Get assignment details

### Submissions
- `POST /api/lms/submissions` - Submit assignment (Mahasiswa)
- `GET /api/lms/submissions/my` - Get my submissions
- `POST /api/lms/submissions/{id}/grade` - Grade submission (Dosen/Admin)

## 🧪 Testing

### Run unit tests
```powershell
python manage.py test lms
```

### Run tests with coverage
```powershell
pip install coverage
coverage run manage.py test lms
coverage report
coverage html
```

## 🔥 Redis Cache Testing

### 1. Test Redis Cache
```powershell
# In terminal 1: Monitor Redis
redis-cli monitor

# In terminal 2: Make API request
curl http://localhost:8000/api/lms/courses
```
Watch for `SET courses_list` and `GET courses_list` in Redis monitor.

### 2. Test Redis Session
```powershell
# Make session request
curl http://localhost:8000/api/lms/test-session

# Check Redis
redis-cli
select 1
keys "*"
```

### 3. Test Cache Invalidation
```powershell
# Get courses (cached)
curl http://localhost:8000/api/lms/courses

# Create new course (invalidates cache)
curl -X POST http://localhost:8000/api/lms/courses \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title":"AI Course","slug":"ai-course","description":"Learn AI","category":"AI","level":"beginner"}'

# Watch Redis monitor for DEL courses_list
```

## 📊 Performance Optimization

The system includes several performance optimizations:

1. **Redis Caching**: Course lists cached for 5 minutes
2. **Database Indexing**: Indexes on frequently queried fields
3. **Query Optimization**: `select_related` and `prefetch_related` to reduce N+1 queries
4. **Custom Managers**: Optimized querysets for common operations

### Check Query Performance

Use Django Debug Toolbar:
```python
# Enabled in DEBUG mode
# Access at http://localhost:8000/__debug__/
```

## 🏗️ Project Structure

```
tugasSS/
├── simple_lms/           # Django project settings
│   ├── settings.py       # Main settings
│   ├── urls.py          # URL configuration
│   ├── wsgi.py          # WSGI config
│   └── asgi.py          # ASGI config
├── lms/                 # Main LMS app
│   ├── models.py        # Database models
│   ├── admin.py         # Admin configuration
│   ├── api.py           # API endpoints
│   ├── auth.py          # JWT authentication
│   ├── schemas.py       # Pydantic schemas
│   ├── tests.py         # Unit tests
│   └── management/      # Management commands
│       └── commands/
│           └── seed_data.py
├── requirements.txt     # Python dependencies
├── docker-compose.yml   # Docker setup
├── Dockerfile          # Docker image
├── .env.example        # Environment variables template
└── README.md           # This file
```

## 🔒 Security Features

- JWT-based authentication
- Role-based access control (RBAC)
- Password hashing with Django's built-in system
- CSRF protection
- SQL injection prevention via Django ORM
- XSS protection

## 📝 Database Schema

### Models
- **User**: Custom user with roles (admin, dosen, mahasiswa)
- **Course**: Course information with instructor
- **Lesson**: Course lessons/modules
- **Assignment**: Course assignments
- **Submission**: Student assignment submissions
- **Enrollment**: Many-to-many relationship between users and courses

## 🤝 Contributing

1. Create a new branch
2. Make your changes
3. Write tests
4. Run tests
5. Submit a pull request

## 📄 License

This project is created for educational purposes.

## 👨‍💻 Author

Simple LMS - Django Learning Management System

## 🆘 Troubleshooting

### Database connection error
Make sure PostgreSQL is running and credentials in `.env` are correct.

### Redis connection error
Make sure Redis is running on the specified port.

### Migration errors
```powershell
python manage.py migrate --run-syncdb
```

### Clear Redis cache
```powershell
redis-cli FLUSHALL
```

## 📞 Support

For issues and questions, please create an issue in the repository.
