# PostgreSQL Integration for User Authentication and Course Schedules

This document describes the isolated PostgreSQL integration that has been added to the 18Mart Portal application.

## Overview

The PostgreSQL integration is **completely isolated** from the existing database functionality and does not modify any existing code, endpoints, or data flow.

## Architecture

### Isolated Components

1. **Database Connection**: `app/postgres_db.py`
   - Separate PostgreSQL connection for authentication and schedules
   - Uses `POSTGRES_URL` environment variable
   - Independent from existing `database.py`

2. **Models**: `app/postgres_models.py`
   - `User` model for authentication
   - `CourseSchedule` model for user schedules
   - Uses UUID primary keys

3. **Schemas**: `app/postgres_schemas.py`
   - Pydantic models for request/response validation
   - Separate from existing schemas

4. **Services**: `app/postgres_services.py`
   - Business logic for user authentication and CRUD operations
   - Password hashing with bcrypt
   - JWT token generation and validation

5. **Routers**: `app/postgres_routers.py`
   - API endpoints for authentication and schedule management
   - JWT-based authentication
   - Separate from existing routers

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Course Schedules Table
```sql
CREATE TABLE course_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_name VARCHAR(255) NOT NULL,
    day_of_week VARCHAR(20) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    location VARCHAR(255)
);
```

## API Endpoints

### Authentication (`/api/v1/auth`)
- `POST /register` - User registration
- `POST /login` - User login (returns JWT token)
- `GET /me` - Get current user info (requires authentication)

### Course Schedules (`/api/v1/schedules`)
- `POST /` - Create schedule (requires authentication)
- `GET /` - Get user schedules (requires authentication)
- `GET /{schedule_id}` - Get specific schedule (requires authentication)
- `PUT /{schedule_id}` - Update schedule (requires authentication)
- `DELETE /{schedule_id}` - Delete schedule (requires authentication)
- `GET /user/with-schedules` - Get user with all schedules (requires authentication)

## Environment Variables

Add to your `.env` file:

```env
# PostgreSQL connection for authentication and schedules
POSTGRES_URL=postgresql://username:password@localhost/mart_portal_auth

# JWT secret key (use a strong secret in production)
SECRET_KEY=your-secure-secret-key-here

# Debug mode (optional)
DEBUG=false
```

## Installation

1. Install additional dependencies:
```bash
pip install psycopg2-binary passlib python-jose[cryptography] email-validator
```

2. Create PostgreSQL database:
```sql
CREATE DATABASE mart_portal_auth;
```

3. Run migration:
```bash
psql -d mart_portal_auth -f migrations/001_create_postgres_auth_tables.sql
```

Or use the Python script:
```bash
python scripts/create_postgres_tables.py
```

## Usage Examples

### Register a new user
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

### Create a course schedule
```bash
curl -X POST "http://localhost:8000/api/v1/schedules/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "course_name": "Mathematics",
    "day_of_week": "Monday",
    "start_time": "09:00:00",
    "end_time": "10:30:00",
    "location": "Room 101"
  }'
```

## Security Features

- Password hashing with bcrypt
- JWT-based authentication
- User-specific schedule isolation
- Input validation with Pydantic
- SQL injection protection with SQLAlchemy

## Isolation Guarantees

✅ **No existing code was modified**
✅ **No existing database connections were changed**
✅ **No existing API endpoints were affected**
✅ **No existing UI components were modified**
✅ **Separate database connection and models**
✅ **Independent router prefixes**

The PostgreSQL integration is completely backward-compatible and can be safely deployed without affecting existing functionality.
