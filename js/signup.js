document.getElementById("signup-form").addEventListener("submit", async function(e) {
    e.preventDefault(); // stop the page from refreshing
    let username = document.getElementById("username").value.trim();
    let password = document.getElementById("password").value;
    let confirmPassword = document.getElementById("confirm-password").value;
    if (username.length < 3) {
        alert("Username must be at least 3 characters");
        return;
    }
    let errors = validatePassword(password);
    if (errors.length > 0) {
        alert("Password problem:\n" + errors.join("\n")); // show all the issues at once
        return;
    }
    if (password != confirmPassword) {
        alert("Passwords do not match");
        return;
    }
    try {
        // send the username and password to the server
        const response = await fetch("/api/signup", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: username, password: password })
        });
        const result = await response.json();
        if (result.success) {
            alert("Account created successfully! You can now log in.");
            window.location.href = "login.html"; // go to login after signup
        } else {
            alert("Signup failed: " + (result.error || "Unknown error"));
        }
    } catch (error) {
        alert("Could not reach the server. Is it running?");
    }
});

// returns a list of everything wrong with the password (empty = all good)
function validatePassword(password) {
    let errors = [];
    if (password.length < 8) errors.push("- At least 8 characters");
    if (!/[A-Z]/.test(password)) errors.push("- At least one uppercase letter");
    if (!/[a-z]/.test(password)) errors.push("- At least one lowercase letter");
    if (!/[0-9]/.test(password)) errors.push("- At least one digit");
    if (!/[!@#$%^&*]/.test(password)) errors.push("- At least one special character (!@#$%^&*)");
    return errors;
}

// http://127.0.0.1:8083/signup.html
// http://127.0.0.1:8083/login.html
// python -c "import sqlite3; conn = sqlite3.connect('users.db'); [print(r) for r in conn.execute('SELECT * FROM users')]; conn.close()"