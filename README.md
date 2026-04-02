# Password Manager

**Password Manager** is a small, self‑hosted password manager built with plain Python and basic web pages. You can sign up, save passwords for different services, and pull them back when you need them. It’s meant for learning and personal tinkering—not production use.

---

## 🚀 What it does

- Lets people sign up and log in (simple SQLite database)
- Stores service/username/password entries
- Encrypts passwords with a basic XOR cipher (just for fun)
- Can generate a random password for you
- Lets you view or delete each entry, or wipe everything
- Runs on a lightweight Python HTTP server
- Uses vanilla HTML/CSS/JS on the frontend

## 🛠️ Tech overview

- **Backend:** Python 3 (`server.py` + `crypto.py`)
- **Frontend:** Static HTML (`index.html`, `signup.html`, `login.html`), CSS, and JavaScript (`js/app.js`)
- **Storage:**
  - `users.db` (SQLite) for accounts
  - `passwords_data.json` for the saved passwords

## 📁 Layout

```
Cyber-main/
├── crypto.py              # encryption helpers & password generator
├── server.py              # server logic
├── index.html             # main UI
├── signup.html            # registration page
├── login.html             # login page
├── css/style.css          # styling
├── js/app.js              # frontend logic
├── passwords_data.json    # holds the passwords (created at runtime)
├── users.db               # SQLite database (created at runtime)
└── ...
```

## ⚙️ Getting started

1. Clone the repo:
   ```bash
   git clone https://github.com/YourUsername/Cyber.git
   cd Cyber
   ```

2. Make sure you have Python 3 installed.

3. Start the server:
   ```bash
   python server.py
   ```
   It runs on `http://127.0.0.1:8083` by default.

4. Point your browser there and use the app:
   - Sign up (`signup.html`), then log in (`login.html`).
   - The main page lets you add, view, or delete passwords.

## 🔒 A few warnings

- The “encryption” is a simple XOR with a hard‑coded key. Don’t rely on it.
- Passwords are kept in a plain JSON file, so anyone with access can read them.
- There’s no real auth on the API; it’s just `user_id` in the request.

Use this project as a learning tool, not as a secure product.

## 📦 Requirements

Nothing extra – it uses only the Python standard library.

## 👥 Want to help?

Fork it, raise issues, or send PRs. Improvements to security, features, and UI are all welcome.

## 📄 License

MIT (you can add a `LICENSE` file if you like).

---

*Made by the Cyber project team.*
