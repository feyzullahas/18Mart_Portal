-- PostgreSQL migration for user authentication and course schedules
-- This migration creates isolated tables for the new PostgreSQL integration

-- Create users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster email lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Create course_schedules table
CREATE TABLE IF NOT EXISTS course_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_name VARCHAR(255) NOT NULL,
    day_of_week VARCHAR(20) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    location VARCHAR(255)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_course_schedules_user_id ON course_schedules(user_id);
CREATE INDEX IF NOT EXISTS idx_course_schedules_day_of_week ON course_schedules(day_of_week);

-- Add comments for documentation
COMMENT ON TABLE users IS 'User authentication table - isolated from existing database';
COMMENT ON TABLE course_schedules IS 'User course schedules - isolated from existing database';
