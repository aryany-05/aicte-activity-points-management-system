-- =============================================================================
-- AICTE Activity & Points Management System
-- MySQL Database Schema
-- =============================================================================

-- Create database
CREATE DATABASE IF NOT EXISTS aicte_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE aicte_db;

-- =============================================================================
-- USERS TABLE
-- Stores students, clubs, and admins in a single table with role differentiation
-- =============================================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('student', 'club', 'admin') NOT NULL DEFAULT 'student',
    full_name VARCHAR(150) NOT NULL,
    department VARCHAR(100) DEFAULT NULL,       -- For students
    roll_number VARCHAR(50) DEFAULT NULL,       -- For students
    club_name VARCHAR(150) DEFAULT NULL,        -- For clubs
    club_description TEXT DEFAULT NULL,          -- For clubs
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_role (role),
    INDEX idx_email (email)
) ENGINE=InnoDB;

-- =============================================================================
-- EVENTS TABLE
-- Stores all events created by clubs, with approval workflow
-- =============================================================================
CREATE TABLE IF NOT EXISTS events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category ENUM('technical', 'cultural', 'social', 'sports') NOT NULL,
    event_date DATE NOT NULL,
    event_time TIME NOT NULL,
    venue VARCHAR(200) NOT NULL,
    points INT NOT NULL CHECK (points > 0 AND points <= 20),
    max_participants INT NOT NULL CHECK (max_participants > 0),
    club_id INT NOT NULL,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    qr_token VARCHAR(100) DEFAULT NULL,         -- Unique token for QR-based attendance
    qr_code_path VARCHAR(255) DEFAULT NULL,     -- Path to generated QR image
    rejection_reason TEXT DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (club_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_category (category),
    INDEX idx_status (status),
    INDEX idx_club (club_id),
    INDEX idx_date (event_date)
) ENGINE=InnoDB;

-- =============================================================================
-- REGISTRATIONS TABLE
-- Many-to-many relationship between students and events
-- Tracks attendance and points awarded
-- =============================================================================
CREATE TABLE IF NOT EXISTS registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    event_id INT NOT NULL,
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    attended TINYINT(1) DEFAULT 0,
    points_awarded INT DEFAULT 0,
    attendance_marked_at DATETIME DEFAULT NULL,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    UNIQUE KEY unique_registration (student_id, event_id),
    INDEX idx_student (student_id),
    INDEX idx_event (event_id),
    INDEX idx_attended (attended)
) ENGINE=InnoDB;


-- =============================================================================
-- SAMPLE DATA
-- =============================================================================

-- Admin account (password: admin123)
INSERT INTO users (username, email, password_hash, role, full_name)
VALUES ('admin', 'admin@aicte.edu', '$2b$12$hyt44YYRt4pw7Gfkxvw5AexMNXuPB8XOpaH7q/Qfl4hj8QZ1DfYMe', 'admin', 'System Administrator');

-- Club accounts (password: club123)
INSERT INTO users (username, email, password_hash, role, full_name, club_name, club_description)
VALUES 
('techclub', 'tech@college.edu', '$2b$12$9pHi.dr2r9HQd/IrOusBMOWhM5iGBeq0aWXuscEqwgvdcF8SHNDUO', 'club', 'Tech Club Lead', 'Technical Club', 'Promoting technology and innovation among students'),
('artclub', 'arts@college.edu', '$2b$12$9pHi.dr2r9HQd/IrOusBMOWhM5iGBeq0aWXuscEqwgvdcF8SHNDUO', 'club', 'Arts Club Lead', 'Cultural Arts Club', 'Celebrating art, music, and cultural diversity'),
('sportsclub', 'sports@college.edu', '$2b$12$9pHi.dr2r9HQd/IrOusBMOWhM5iGBeq0aWXuscEqwgvdcF8SHNDUO', 'club', 'Sports Club Lead', 'Sports Club', 'Encouraging physical fitness and sportsmanship');

-- Student accounts (password: student123)
INSERT INTO users (username, email, password_hash, role, full_name, department, roll_number)
VALUES 
('rahul', 'rahul@student.edu', '$2b$12$PZHP4v.xryoasd5sdjbE3ux6jVmx2JuR.GCqyBI3vCNiEcoiNUDXi', 'student', 'Rahul Sharma', 'Computer Science', 'CS2024001'),
('priya', 'priya@student.edu', '$2b$12$PZHP4v.xryoasd5sdjbE3ux6jVmx2JuR.GCqyBI3vCNiEcoiNUDXi', 'student', 'Priya Patel', 'Electronics', 'EC2024002'),
('amit', 'amit@student.edu', '$2b$12$PZHP4v.xryoasd5sdjbE3ux6jVmx2JuR.GCqyBI3vCNiEcoiNUDXi', 'student', 'Amit Kumar', 'Mechanical', 'ME2024003');

-- Sample events (3 fresh upcoming active events after October 3, 2026)
INSERT INTO events (id, title, description, category, event_date, event_time, venue, points, max_participants, club_id, status, qr_token)
VALUES 
(1, 'Full Stack Web Development Workshop', 'Comprehensive hands-on workshop covering modern full-stack web development, responsive frontend interfaces, RESTful API design, and database integration.', 'technical', '2026-10-06', '10:00:00', 'Seminar Hall', 10, 60, 2, 'approved', 'webdev2026'),
(2, 'Inter-College Cultural Showcase', 'Annual inter-college cultural fest celebrating music, dance, theatrical performances, and visual arts competitions across campus.', 'cultural', '2026-10-10', '14:00:00', 'Open Air Theatre', 8, 100, 3, 'approved', 'cultural2026'),
(3, 'Inter-Department Cricket Tournament', 'Inter-departmental cricket championship promoting athletic excellence, sportsmanship, and collaborative team spirit across departments.', 'sports', '2026-10-15', '09:00:00', 'College Ground', 10, 80, 4, 'approved', 'cricket2026');

-- Sample registrations
INSERT INTO registrations (id, student_id, event_id, attended, points_awarded, attendance_marked_at)
VALUES 
-- Event 1: Full Stack Web Development Workshop (Points: 10)
(1, 5, 1, 1, 10, '2026-10-02 11:30:00'), -- Rahul Sharma: attended
(2, 6, 1, 1, 10, '2026-10-02 11:35:00'), -- Priya Patel: attended
(3, 7, 1, 0, 0, NULL),                  -- Amit Kumar: registered

-- Event 2: Inter-College Cultural Showcase (Points: 8)
(4, 5, 2, 0, 0, NULL),                  -- Rahul Sharma: registered
(5, 6, 2, 1, 8, '2026-10-02 15:45:00'),  -- Priya Patel: attended
(6, 7, 2, 0, 0, NULL),                  -- Amit Kumar: registered

-- Event 3: Inter-Department Cricket Tournament (Points: 10)
(7, 5, 3, 1, 10, '2026-10-02 16:00:00'), -- Rahul Sharma: attended
(8, 7, 3, 0, 0, NULL);                  -- Amit Kumar: registered
