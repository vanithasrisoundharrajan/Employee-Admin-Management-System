
-- Employee Admin Management System
-- Database setup

CREATE DATABASE IF NOT EXISTS employee_db;

USE employee_db;

-- Create the employees table
CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    department VARCHAR(100) NOT NULL,
    salary DECIMAL(10, 2) NOT NULL DEFAULT 0.00
);

-- Display the table structure
DESCRIBE employees;

-- View all employee records
SELECT * FROM employees;
