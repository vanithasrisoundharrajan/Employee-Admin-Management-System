
CREATE DATABASE IF NOT EXISTS employee_db;
USE employee_db;

CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    department VARCHAR(100) NOT NULL,
    salary DECIMAL(10,2) NOT NULL DEFAULT 0.00
);

INSERT IGNORE INTO employees (name, email, department, salary)
VALUES
('Arun Kumar', 'arun@example.com', 'IT', 25000.00),
('Priya Devi', 'priya@example.com', 'HR', 30000.00),
('Rahul Raj', 'rahul@example.com', 'Finance', 35000.00);

SELECT * FROM employees;
    