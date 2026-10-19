
import os
from decimal import Decimal

import mysql.connector
from flask import Flask, render_template, request, redirect, session, jsonify

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]

ADMIN_USERNAME = os.environ["ADMIN_USERNAME"]
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]


def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST", "127.0.0.1"),
        port=int(os.environ.get("MYSQL_PORT", "3306")),
        user=os.environ.get("MYSQL_USER", "root"),
        password=os.environ["MYSQL_ROOT_PASSWORD"],
        database="employee_db"
    )


def is_admin():
    return "admin" in session


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
            session.clear()
            session["admin"] = username
            return redirect("/dashboard")

        error = "Invalid username or password"

    return render_template("login.html", error=error)


@app.route("/dashboard")
def dashboard():
    if not is_admin():
        return redirect("/login")
    return render_template("dashboard.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


def read_employee_data():
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    department = str(data.get("department", "")).strip()

    try:
        salary = Decimal(str(data.get("salary", "")))
        if not salary.is_finite() or salary < 0 or salary > Decimal("99999999.99"):
            raise ValueError
    except Exception:
        return None, (jsonify({"error": "Enter a valid non-negative salary"}), 400)

    if not name or not email or not department:
        return None, (jsonify({"error": "All fields are required"}), 400)

    if len(name) > 100 or len(email) > 150 or len(department) > 100:
        return None, (jsonify({"error": "One or more fields are too long"}), 400)

    return {
        "name": name,
        "email": email,
        "department": department,
        "salary": salary
    }, None


def handle_db_error(action):
    app.logger.exception("Database error: %s", action)
    return jsonify({"error": "Database error. Check the Flask terminal."}), 500


@app.route("/api/employees", methods=["GET"])
def get_employees():
    if not is_admin():
        return jsonify({"error": "Unauthorized. Please log in."}), 401

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, name, email, department, salary "
            "FROM employees ORDER BY id DESC"
        )
        employees = cursor.fetchall()

        for employee in employees:
            employee["salary"] = float(employee["salary"])

        return jsonify(employees)

    except mysql.connector.Error:
        return handle_db_error("loading employees")

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


@app.route("/api/employees", methods=["POST"])
def add_employee():
    if not is_admin():
        return jsonify({"error": "Unauthorized. Please log in."}), 401

    employee, error = read_employee_data()
    if error:
        return error

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO employees (name, email, department, salary) "
            "VALUES (%s, %s, %s, %s)",
            (employee["name"], employee["email"],
             employee["department"], employee["salary"])
        )
        conn.commit()
        return jsonify({
            "message": "Employee added successfully",
            "id": cursor.lastrowid
        }), 201

    except mysql.connector.IntegrityError:
        if conn is not None:
            conn.rollback()
        return jsonify({"error": "That email already exists"}), 409

    except mysql.connector.Error:
        if conn is not None:
            conn.rollback()
        return handle_db_error("adding employee")

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


@app.route("/api/employees/<int:employee_id>", methods=["PUT"])
def update_employee(employee_id):
    if not is_admin():
        return jsonify({"error": "Unauthorized. Please log in."}), 401

    employee, error = read_employee_data()
    if error:
        return error

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE employees SET name=%s, email=%s, department=%s, salary=%s "
            "WHERE id=%s",
            (employee["name"], employee["email"],
             employee["department"], employee["salary"], employee_id)
        )

        if cursor.rowcount == 0:
            cursor.execute("SELECT id FROM employees WHERE id=%s", (employee_id,))
            if cursor.fetchone() is None:
                return jsonify({"error": "Employee not found"}), 404

        conn.commit()
        return jsonify({"message": "Employee updated successfully"})

    except mysql.connector.IntegrityError:
        if conn is not None:
            conn.rollback()
        return jsonify({"error": "That email already exists"}), 409

    except mysql.connector.Error:
        if conn is not None:
            conn.rollback()
        return handle_db_error("updating employee")

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


@app.route("/api/employees/<int:employee_id>", methods=["DELETE"])
def delete_employee(employee_id):
    if not is_admin():
        return jsonify({"error": "Unauthorized. Please log in."}), 401

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM employees WHERE id=%s", (employee_id,))

        if cursor.rowcount == 0:
            return jsonify({"error": "Employee not found"}), 404

        conn.commit()
        return jsonify({"message": "Employee deleted successfully"})

    except mysql.connector.Error:
        if conn is not None:
            conn.rollback()
        return handle_db_error("deleting employee")

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    