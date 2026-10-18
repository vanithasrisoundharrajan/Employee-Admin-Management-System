
import os
from flask import Flask, render_template, request, redirect, session, jsonify
app = Flask(__name__)

# Read secret values from environment variables
app.secret_key = os.environ["SECRET_KEY"]

ADMIN_USERNAME = os.environ["ADMIN_USERNAME"]
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]

import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password=os.environ["MYSQL_ROOT_PASSWORD"],
        database="employee_db"
    )

# READ: Get all employees
@app.route("/api/employees", methods=["GET"])
def get_employees():
    if "admin" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT id, name, email, department, salary "
            "FROM employees ORDER BY id DESC"
        )
        employees = cursor.fetchall()
        return jsonify(employees)
    finally:
        cursor.close()
        conn.close()


# CREATE: Add a new employee
@app.route("/api/employees", methods=["POST"])
def add_employee():
    if "admin" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    department = str(data.get("department", "")).strip()

    try:
        salary = float(data.get("salary", 0))
        if salary < 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "Salary must be a non-negative number"}), 400

    if not name or not email or not department:
        return jsonify({"error": "All fields are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO employees (name, email, department, salary) "
            "VALUES (%s, %s, %s, %s)",
            (name, email, department, salary)
        )
        conn.commit()
        return jsonify({
            "message": "Employee added successfully",
            "id": cursor.lastrowid
        }), 201
    except mysql.connector.IntegrityError:
        conn.rollback()
        return jsonify({"error": "This email already exists"}), 409
    finally:
        cursor.close()
        conn.close()


# UPDATE: Edit an employee
@app.route("/api/employees/<int:employee_id>", methods=["PUT"])
def update_employee(employee_id):
    if "admin" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    department = str(data.get("department", "")).strip()

    try:
        salary = float(data.get("salary", 0))
        if salary < 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid salary"}), 400

    if not name or not email or not department:
        return jsonify({"error": "All fields are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "UPDATE employees SET name=%s, email=%s, department=%s, salary=%s "
            "WHERE id=%s",
            (name, email, department, salary, employee_id)
        )
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Employee not found or no changes made"}), 404

        return jsonify({"message": "Employee updated successfully"})
    except mysql.connector.IntegrityError:
        conn.rollback()
        return jsonify({"error": "This email already exists"}), 409
    finally:
        cursor.close()
        conn.close()


# DELETE: Remove an employee
@app.route("/api/employees/<int:employee_id>", methods=["DELETE"])
def delete_employee(employee_id):
    if "admin" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM employees WHERE id=%s",
            (employee_id,)
        )
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Employee not found"}), 404

        return jsonify({"message": "Employee deleted successfully"})
    finally:
        cursor.close()
        conn.close()


@app.route("/")
def home():
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = username
            return redirect("/dashboard")
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)


@app.route("/dashboard")
def dashboard():
    if "admin" not in session:
        return redirect("/login")

    return render_template("dashboard.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
