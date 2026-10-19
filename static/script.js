
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

async function readApiResponse(response) {
    const contentType = response.headers.get("content-type") || "";

    if (!contentType.includes("application/json")) {
        const body = await response.text();
        console.error("Unexpected API response:", response.status, body);
        throw new Error(`Unexpected server response (HTTP ${response.status}).`);
    }

    return response.json();
}

function resetForm() {
    form.reset();
    employeeId.value = "";
    formTitle.textContent = "Add Employee";
    saveButton.textContent = "Add Employee";
    cancelButton.hidden = true;
}

async function loadEmployees() {
    tableBody.replaceChildren();
    showMessage("Loading employees...");

    try {
        const response = await fetch("/api/employees", {
            credentials: "same-origin",
            headers: { Accept: "application/json" }
        });

        const employees = await readApiResponse(response);

        if (!response.ok) {
            throw new Error(employees.error || "Could not load employees.");
        }

        if (!Array.isArray(employees)) {
            throw new Error("Unexpected employee data.");
        }

        if (employees.length === 0) {
            const row = document.createElement("tr");
            const cell = document.createElement("td");
            cell.colSpan = 6;
            cell.textContent = "No employee records yet.";
            row.appendChild(cell);
            tableBody.appendChild(row);
            showMessage("No employee records found.");
            return;
        }

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
            editButton.type = "button";
            editButton.textContent = "Edit";

            editButton.addEventListener("click", () => {
                employeeId.value = employee.id;
                document.getElementById("name").value = employee.name;
                document.getElementById("email").value = employee.email;
                document.getElementById("department").value = employee.department;
                document.getElementById("salary").value = employee.salary;

                formTitle.textContent = "Edit Employee";
                saveButton.textContent = "Update Employee";
                cancelButton.hidden = false;
                showMessage("");
                form.scrollIntoView({ behavior: "smooth" });
            });

            const deleteButton = document.createElement("button");
            deleteButton.type = "button";
            deleteButton.textContent = "Delete";

            deleteButton.addEventListener("click", async () => {
                if (!confirm("Delete this employee?")) return;

                try {
                    const result = await fetch(`/api/employees/${employee.id}`, {
                        method: "DELETE",
                        credentials: "same-origin",
                        headers: { Accept: "application/json" }
                    });

                    const data = await readApiResponse(result);
                    if (!result.ok) throw new Error(data.error || "Delete failed.");

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

        showMessage(`Loaded ${employees.length} employee record(s).`);

    } catch (error) {
        console.error("Load employees error:", error);
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

    if (!employee.name || !employee.email ||
        !employee.department || employee.salary === "") {
        showMessage("Please fill in all fields.");
        return;
    }

    saveButton.disabled = true;

    try {
        const response = await fetch(
            id ? `/api/employees/${id}` : "/api/employees",
            {
                method: id ? "PUT" : "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json",
                    Accept: "application/json"
                },
                body: JSON.stringify(employee)
            }
        );

        const data = await readApiResponse(response);
        if (!response.ok) throw new Error(data.error || "Could not save employee.");

        resetForm();
        showMessage(data.message);
        await loadEmployees();

    } catch (error) {
        showMessage(error.message);
    } finally {
        saveButton.disabled = false;
    }
});

cancelButton.addEventListener("click", () => {
    resetForm();
    showMessage("");
});

loadEmployees();
