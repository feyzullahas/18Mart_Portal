# PostgreSQL Integration - User Authentication & Course Schedule System

This document describes the complete PostgreSQL integration for the 18Mart Portal application with user authentication and course schedule management.

## 🚀 Features Implemented

### User Authentication
- **Secure password storage** using bcrypt hashing
- **JWT-based authentication** with configurable expiration
- **User registration** with email uniqueness validation
- **User profile management** with update capabilities
- **UUID-based user identification** for enhanced security

### Course Schedule Management
- **Personalized schedules** for each user
- **CRUD operations** (Create, Read, Update, Delete)
- **Time-based scheduling** with start/end times
- **Location management** for course venues
- **Day-of-week organization** (Monday-Sunday)

## 📁 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    student_id VARCHAR(20) UNIQUE NOT NULL,
    department VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

### Schedules Table
```sql
CREATE TABLE schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_name VARCHAR(100) NOT NULL,
    day_of_week VARCHAR(10) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    location VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

## 🔧 Setup Instructions

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure PostgreSQL
Create a PostgreSQL database:
```sql
CREATE DATABASE mart_portal;
CREATE USER mart_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE mart_portal TO mart_user;
```

### 3. Environment Configuration
Copy `.env.example` to `.env` and update:
```bash
cp .env.example .env
```

Update `.env` with your database credentials:
```env
DATABASE_URL=postgresql://mart_user:your_password@localhost:5432/mart_portal
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=false
```

### 4. Create Database Tables
```bash
python create_tables.py
```

### 5. Start the Application
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🛡️ Security Features

### Password Security
- **bcrypt hashing** with automatic salt generation
- **Never store plain text passwords**
- **Configurable hashing rounds** for enhanced security

### JWT Authentication
- **Bearer token authentication**
- **Configurable token expiration**
- **Secure token generation** with HS256 algorithm
- **User validation** on every protected route

### Input Validation
- **Email format validation** using Pydantic EmailStr
- **Unique constraint enforcement** on username, email, student_id
- **SQL injection prevention** through SQLAlchemy ORM
- **CORS configuration** for frontend integration

## 📚 API Endpoints

### Authentication
- `POST /auth/token` - User login (returns JWT token)
- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update current user profile
- `POST /users/` - Register new user

### Course Schedules
- `POST /schedules/` - Create new schedule entry
- `GET /schedules/my` - Get current user's schedules
- `GET /schedules/{schedule_id}` - Get specific schedule
- `PUT /schedules/{schedule_id}` - Update schedule
- `DELETE /schedules/{schedule_id}` - Delete schedule

## 🔍 Example Usage

### User Registration
```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "student_id": "123456789",
    "department": "Computer Engineering",
    "password": "secure_password"
  }'
```

### User Login
```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john_doe&password=secure_password"
```

### Create Schedule
```bash
curl -X POST "http://localhost:8000/schedules/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER_UUID_HERE",
    "course_name": "Database Systems",
    "day_of_week": "Monday",
    "start_time": "09:00:00",
    "end_time": "10:30:00",
    "location": "Room A101"
  }'
```

## 🔄 Database Migrations

The system uses SQLAlchemy for database management. To update the schema:

1. **Modify models** in `app/models/`
2. **Update schemas** in `app/schemas/`
3. **Run migration script**:
   ```bash
   python create_tables.py
   ```

## 🚨 Production Considerations

### Security
- Change `SECRET_KEY` in production
- Use environment variables for sensitive data
- Enable HTTPS in production
- Implement rate limiting
- Add input sanitization

### Performance
- Add database indexes on frequently queried fields
- Implement connection pooling
- Consider read replicas for high traffic
- Add caching for frequently accessed data

## 🛠️ Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check PostgreSQL service
sudo systemctl status postgresql

# Test connection
psql -h localhost -U mart_user -d mart_portal
```

**JWT Token Issues**
- Verify `SECRET_KEY` is consistent
- Check token expiration time
- Ensure proper token format in Authorization header

**UUID Validation Errors**
- Ensure UUID format is correct: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- Check that user_id exists in users table

---

**Note**: This implementation follows industry best practices for security, scalability, and maintainability. All passwords are hashed, authentication is token-based, and the database schema is optimized for performance.
