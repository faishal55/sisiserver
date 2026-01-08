# Simple LMS - Quick Start Guide

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Step 1: Setup Environment
```powershell
# Run the setup script
.\setup.ps1
```

Or manually:
```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
Copy-Item .env.example .env
```

### Step 2: Configure Database
Edit `.env` file with your database credentials:
```env
DB_NAME=simple_lms
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### Step 3: Start Services
Make sure PostgreSQL and Redis are running:
```powershell
# Check if services are running
# PostgreSQL should be on port 5432
# Redis should be on port 6379
```

Or use Docker:
```powershell
docker-compose up -d
```

### Step 4: Initialize Database
```powershell
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Seed database with test data
python manage.py seed_data
```

### Step 5: Run Server
```powershell
python manage.py runserver
```

### Step 6: Test the API
Open your browser and go to:
- **API Documentation**: http://localhost:8000/api/lms/docs
- **Django Admin**: http://localhost:8000/admin

## 🔑 Test Accounts

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@lms.com | admin123 |
| Dosen | dosen1@lms.com | dosen123 |
| Mahasiswa | student1@lms.com | student123 |

## 📝 Common Tasks

### Create Superuser
```powershell
python manage.py createsuperuser
```

### Run Tests
```powershell
python manage.py test lms
```

### Check Performance
```powershell
python manage.py performance_test
```

### Test Redis Cache
```powershell
.\test_redis.ps1
```

### Clear Cache
```powershell
# In Python shell
python manage.py shell

>>> from django.core.cache import cache
>>> cache.clear()
```

## 🧪 Testing with Postman

1. Import `postman_collection.json` into Postman
2. Set environment variable `base_url` to `http://localhost:8000`
3. Login to get token (automatically saved)
4. Test other endpoints

## 🔧 Troubleshooting

### "No module named 'lms'"
Make sure you're in the project directory and virtual environment is activated.

### "Could not connect to database"
Check PostgreSQL is running and credentials in `.env` are correct.

### "Redis connection failed"
Make sure Redis is running on port 6379.

### "Port 8000 already in use"
Stop other Django servers or use a different port:
```powershell
python manage.py runserver 8001
```

## 📚 Next Steps

1. Read [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete API reference
2. Check [README.md](README.md) for detailed documentation
3. Explore the code in `lms/` directory
4. Customize models and add features

## 🎯 Key Features to Explore

### 1. JWT Authentication
```bash
# Login
curl -X POST http://localhost:8000/api/lms/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"student1@lms.com","password":"student123"}'
```

### 2. Create Course (as Dosen)
```bash
curl -X POST http://localhost:8000/api/lms/courses \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"New Course","slug":"new-course","description":"Test","category":"Programming","level":"beginner"}'
```

### 3. Enroll in Course (as Mahasiswa)
```bash
curl -X POST http://localhost:8000/api/lms/enrollments \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"course_id":1}'
```

### 4. Submit Assignment
```bash
curl -X POST http://localhost:8000/api/lms/submissions \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"assignment_id":1,"content":"My submission"}'
```

## 🎓 Learning Resources

- Django Documentation: https://docs.djangoproject.com/
- Django Ninja: https://django-ninja.rest-framework.com/
- Redis Documentation: https://redis.io/docs/
- JWT: https://jwt.io/

## 💡 Tips

1. Use Django Debug Toolbar to analyze queries (enabled in DEBUG mode)
2. Check Redis monitor to see cache operations: `redis-cli monitor`
3. Use Django shell for quick testing: `python manage.py shell`
4. Enable logging to track API usage (configured in settings.py)

## 🤝 Support

If you encounter issues:
1. Check the logs in `logs/django.log`
2. Verify all services are running
3. Make sure migrations are up to date
4. Clear cache and restart server

Happy coding! 🎉
