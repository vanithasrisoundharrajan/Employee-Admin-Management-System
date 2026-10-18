
const form = document.getElementById("employee-form");
const tableBody = document.getElementById("employee-table-body");
const message = document.getElementById("message");
const employeeId = document.getElementById("employee-id");
const formTitle = document.getElementById("form-title");
const saveButton = document.getElementById("save-button");
const cancelButton = document.getElementById("cancel-button");

function showMessage(text) {
    message.textContent = text;
}

function resetForm() {
    form.reset();
    employeeId.value = "";
    formTitle.textContent = "Add Employee";
    saveButton.textContent = "Add Employee";
    cancelButton.hidden = true;
}

async function loadEmployees() {
    try {
        const response = await fetch("/api/employees");

        if (!response.ok) {
            throw new Error(
                response.status === 401
                    ? "Please log in again."
                    : "Could not load employees."
            );
        }

        const employees = await response.json();
        tableBody.replaceChildren();

        employees.forEach(employee => {
            const row = document.createElement("tr");

            [
                employee.id,
                employee.name,
                employee.email,
                employee.department,
                employee.salary
            ].forEach(value => {
                const cell = document.createElement("td");
                cell.textContent = value ?? "";
                row.appendChild(cell);
            });

            const actions = document.createElement("td");

            const editButton = document.createElement("button");
            editButton.textContent = "Edit";
            editButton.type = "button";
            editButton.addEventListener("click", () => {
                employeeId.value = employee.id;
                document.getElementById("name").value = employee.name;
                document.getElementById("email").value = employee.email;
                document.getElementById("department").value =
                    employee.department;
                document.getElementById("salary").value = employee.salary;

                formTitle.textContent = "Edit Employee";
                saveButton.textContent = "Update Employee";
                cancelButton.hidden = false;
                showMessage("");
                form.scrollIntoView({ behavior: "smooth" });
            });

            const deleteButton = document.createElement("button");
            deleteButton.textContent = "Delete";
            deleteButton.type = "button";
            deleteButton.addEventListener("click", async () => {
                if (!confirm("Delete this employee?")) return;

                try {
                    const result = await fetch(
                        `/api/employees/${employee.id}`,
                        { method: "DELETE" }
                    );

                    const data = await result.json();

                    if (!result.ok) {
                        throw new Error(data.error || "Delete failed.");
                    }

                    showMessage(data.message);
                    await loadEmployees();
                } catch (error) {
                    showMessage(error.message);
                }
            });

            actions.append(editButton, deleteButton);
            row.appendChild(actions);
            tableBody.appendChild(row);
        });

        if (employees.length === 0) {
            const row = document.createElement("tr");
            const cell = document.createElement("td");
            cell.colSpan = 6;
            cell.textContent = "No employee records yet.";
            row.appendChild(cell);
            tableBody.appendChild(row);
        }
    } catch (error) {
        showMessage(error.message);
    }
}

form.addEventListener("submit", async event => {
    event.preventDefault();

    const id = employeeId.value;
    const employee = {
        name: document.getElementById("name").value.trim(),
        email: document.getElementById("email").value.trim(),
        department: document.getElementById("department").value.trim(),
        salary: document.getElementById("salary").value
    };

    try {
        const response = await fetch(
            id ? `/api/employees/${id}` : "/api/employees",
            {
                method: id ? "PUT" : "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(employee)
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Could not save employee.");
        }

        showMessage(data.message);
        resetForm();
        await loadEmployees();
    } catch (error) {
        showMessage(error.message);
    }
});

cancelButton.addEventListener("click", resetForm);

loadEmployees();
