-- Create and select database
CREATE DATABASE IF NOT EXISTS emp_mgmt;
USE emp_mgmt;

-- Departments table (no manager_id yet, added after users)
CREATE TABLE departments (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users table
CREATE TABLE users (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    email           VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role            ENUM('manager', 'employee') NOT NULL DEFAULT 'employee',
    department_id   INT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL
);

-- Add manager_id to departments after users table exists
ALTER TABLE departments ADD COLUMN manager_id INT;
ALTER TABLE departments ADD FOREIGN KEY (manager_id) REFERENCES users(id) ON DELETE SET NULL;

-- Attendance table
CREATE TABLE attendance (
    id      INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    date    DATE NOT NULL,
    status  ENUM('present', 'absent', 'half_day', 'leave') NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_attendance (user_id, date)
);

-- Tasks table
CREATE TABLE tasks (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    title       VARCHAR(200) NOT NULL,
    description TEXT,
    assigned_to INT NOT NULL,
    assigned_by INT NOT NULL,
    status      ENUM('pending', 'in_progress', 'completed') DEFAULT 'pending',
    due_date    DATE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users(id) ON DELETE CASCADE
);

-- Performance table
CREATE TABLE performance (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    score       DECIMAL(4,2) NOT NULL,
    notes       TEXT,
    reviewed_by INT NOT NULL,
    period      ENUM('weekly', 'monthly', 'quarterly') NOT NULL,
    review_date DATE NOT NULL,
    FOREIGN KEY (user_id)     REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE CASCADE
);