-- Database Schema for Career Guidance AI

-- 1. Users table
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    gender VARCHAR(50),
    date_of_birth DATE,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Student Profiles table
CREATE TABLE IF NOT EXISTS student_profiles (
    user_id INTEGER PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    education_level VARCHAR(100),
    class_or_degree VARCHAR(100),
    stream VARCHAR(100),
    marks DECIMAL(5, 2),
    category VARCHAR(50),
    interest_area VARCHAR(255),
    location_preference VARCHAR(255),
    career_goal TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Courses table
CREATE TABLE IF NOT EXISTS courses (
    course_id SERIAL PRIMARY KEY,
    course_name VARCHAR(255) UNIQUE NOT NULL,
    stream VARCHAR(100),
    degree VARCHAR(100)
);

-- 4. Colleges table
CREATE TABLE IF NOT EXISTS colleges (
    college_id SERIAL PRIMARY KEY,
    college_name VARCHAR(255) UNIQUE NOT NULL,
    location VARCHAR(255)
);

-- 5. Cutoffs table
CREATE TABLE IF NOT EXISTS cutoffs (
    cutoff_id SERIAL PRIMARY KEY,
    college_id INTEGER REFERENCES colleges(college_id) ON DELETE CASCADE,
    course_id INTEGER REFERENCES courses(course_id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    category VARCHAR(50) NOT NULL,
    cutoff_mark DECIMAL(10, 2) NOT NULL
);

-- 6. Placements table
CREATE TABLE IF NOT EXISTS placements (
    placement_id SERIAL PRIMARY KEY,
    college_id INTEGER REFERENCES colleges(college_id) ON DELETE CASCADE,
    course_id INTEGER REFERENCES courses(course_id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    avg_package_lpa DECIMAL(10, 2),
    placement_percentage DECIMAL(5, 2)
);

-- 7. Careers table
CREATE TABLE IF NOT EXISTS careers (
    career_id SERIAL PRIMARY KEY,
    career_name VARCHAR(255) UNIQUE NOT NULL,
    avg_salary_lpa DECIMAL(10, 2)
);

-- 8. Course-Careers mapping
CREATE TABLE IF NOT EXISTS course_careers (
    course_id INTEGER REFERENCES courses(course_id) ON DELETE CASCADE,
    career_id INTEGER REFERENCES careers(career_id) ON DELETE CASCADE,
    PRIMARY KEY (course_id, career_id)
);

-- 9. Skills table
CREATE TABLE IF NOT EXISTS skills (
    skill_id SERIAL PRIMARY KEY,
    skill_name VARCHAR(100) UNIQUE NOT NULL
);

-- 10. Career-Skills mapping
CREATE TABLE IF NOT EXISTS career_skills (
    career_id INTEGER REFERENCES careers(career_id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES skills(skill_id) ON DELETE CASCADE,
    importance_level INTEGER DEFAULT 1,
    PRIMARY KEY (career_id, skill_id)
);

-- 11. Chat Sessions
CREATE TABLE IF NOT EXISTS chat_sessions (
    session_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    title VARCHAR(255) DEFAULT 'New Chat',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 12. Chat Messages
CREATE TABLE IF NOT EXISTS chat_messages (
    message_id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL, -- 'user' or 'assistant'
    message TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
