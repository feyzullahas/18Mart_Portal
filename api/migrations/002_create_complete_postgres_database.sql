-- Complete PostgreSQL database setup for 18Mart Portal
-- This migration creates all necessary tables for the application
-- Includes user authentication, course schedules, meal menus, and academic calendar

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================
-- USER AUTHENTICATION TABLES
-- =============================================

-- Create users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    student_id VARCHAR(20) UNIQUE,
    department VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Create index for faster email lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_student_id ON users(student_id);

-- =============================================
-- COURSE SCHEDULES TABLES
-- =============================================

-- Create course_schedules table
CREATE TABLE IF NOT EXISTS course_schedules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_name VARCHAR(255) NOT NULL,
    course_code VARCHAR(20),
    instructor VARCHAR(100),
    day_of_week VARCHAR(20) NOT NULL CHECK (day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    location VARCHAR(255),
    semester VARCHAR(20) DEFAULT 'guz',
    academic_year VARCHAR(9), -- Format: 2024-2025
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_course_schedules_user_id ON course_schedules(user_id);
CREATE INDEX IF NOT EXISTS idx_course_schedules_day_of_week ON course_schedules(day_of_week);
CREATE INDEX IF NOT EXISTS idx_course_schedules_semester ON course_schedules(semester);

-- =============================================
-- MEAL MENU TABLES
-- =============================================

-- Create daily_menus table
CREATE TABLE IF NOT EXISTS daily_menus (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    menu_date DATE UNIQUE NOT NULL,
    breakfast_items TEXT[], -- Array of breakfast items
    dinner_items TEXT[], -- Array of dinner items
    total_calories_breakfast INTEGER DEFAULT 0,
    total_calories_dinner INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create osem_menus table (for OSEM cafeteria)
CREATE TABLE IF NOT EXISTS osem_menus (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    menu_date DATE UNIQUE NOT NULL,
    menu_items TEXT[], -- Array of menu items
    total_calories INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for meal menus
CREATE INDEX IF NOT EXISTS idx_daily_menus_date ON daily_menus(menu_date);
CREATE INDEX IF NOT EXISTS idx_osem_menus_date ON osem_menus(menu_date);

-- =============================================
-- ACADEMIC CALENDAR TABLES
-- =============================================

-- Create academic_events table
CREATE TABLE IF NOT EXISTS academic_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE NOT NULL,
    end_date DATE,
    event_type VARCHAR(20) NOT NULL CHECK (event_type IN ('kayit', 'sinav', 'ders', 'tatil', 'onemli')),
    semester VARCHAR(10) NOT NULL CHECK (semester IN ('guz', 'bahar', 'yaz')),
    academic_year VARCHAR(9), -- Format: 2024-2025
    is_important BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for academic events
CREATE INDEX IF NOT EXISTS idx_academic_events_start_date ON academic_events(start_date);
CREATE INDEX IF NOT EXISTS idx_academic_events_type ON academic_events(event_type);
CREATE INDEX IF NOT EXISTS idx_academic_events_semester ON academic_events(semester);

-- =============================================
-- BUS SCHEDULES TABLES (Optional - for caching)
-- =============================================

-- Create bus_schedules_cache table for caching PDF links
CREATE TABLE IF NOT EXISTS bus_schedules_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    schedule_type VARCHAR(20) NOT NULL CHECK (schedule_type IN ('weekday', 'weekend')),
    pdf_url TEXT NOT NULL,
    label VARCHAR(255),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Create index for bus schedules
CREATE INDEX IF NOT EXISTS idx_bus_schedules_type ON bus_schedules_cache(schedule_type);

-- =============================================
-- TRIGGERS FOR UPDATED_AT
-- =============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for all tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_course_schedules_updated_at BEFORE UPDATE ON course_schedules FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_daily_menus_updated_at BEFORE UPDATE ON daily_menus FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_osem_menus_updated_at BEFORE UPDATE ON osem_menus FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_academic_events_updated_at BEFORE UPDATE ON academic_events FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================
-- COMMENTS FOR DOCUMENTATION
-- =============================================

COMMENT ON TABLE users IS 'User authentication and profile information';
COMMENT ON TABLE course_schedules IS 'Individual user course schedules';
COMMENT ON TABLE daily_menus IS 'Daily meal menus for main cafeteria';
COMMENT ON TABLE osem_menus IS 'Daily meal menus for OSEM cafeteria';
COMMENT ON TABLE academic_events IS 'Academic calendar events and important dates';
COMMENT ON TABLE bus_schedules_cache IS 'Cache for bus schedule PDF links';

-- =============================================
-- SAMPLE DATA (Optional - can be removed for production)
-- =============================================

-- Insert sample academic events (optional)
INSERT INTO academic_events (title, description, start_date, end_date, event_type, semester, academic_year, is_important) VALUES
('2024-2025 Güz Dönemi Kayıtları', 'Güz dönemi ders kayıtlarının başlangıcı', '2024-09-16', '2024-09-20', 'kayit', 'guz', '2024-2025', true),
('Ara Sınavlar', 'Güz dönemi ara sınavları', '2024-11-18', '2024-11-29', 'sinav', 'guz', '2024-2025', true),
('Final Sınavları', 'Güz dönemi final sınavları', '2025-01-13', '2025-01-24', 'sinav', 'guz', '2024-2025', true),
('Yarıyıl Tatili', 'Güz dönemi yarıyıl tatili', '2025-01-27', '2025-02-07', 'tatil', 'guz', '2024-2025', false)
ON CONFLICT DO NOTHING;
