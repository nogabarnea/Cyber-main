import http.server
import socketserver
import json
import os
import sqlite3  # for the users database
import hashlib
import base64
import secrets  # for cryptographically secure random salt generation
from urllib.parse import parse_qs, urlparse
from crypto import encrypt, decrypt, generate_password

PORT = 8082
HOST = "127.0.0.1"
DATA_FILE = "passwords_data.json"
DB_FILE = "users.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # creates the table on first run, does nothing if it already exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def hash_password(password, salt=None):
    # Generate random salt if not provided (happens at signup)
    if salt is None:
        salt = secrets.token_hex(16)  # 32-character random hex string
    # first encode to base64, then hash with SHA-256 (can't be reversed)
    b64 = base64.b64encode(password.encode('utf-8')).decode('utf-8')
    # Combine salt with password before hashing (salt makes each hash unique)
    hashed = hashlib.sha256((salt + b64).encode('utf-8')).hexdigest()
    # Return both the hash and the salt
    return hashed, salt


#bring passwords from json
def load_passwords():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

#save all passwords to jason
def save_passwords(passwords):
    with open(DATA_FILE, 'w') as f:
        json.dump(passwords, f, indent=2)


class PasswordManager(http.server.SimpleHTTPRequestHandler):    
    def do_GET(self):
        parsed = urlparse(self.path)
        #get all passwords (optionally filtered by user_id)
        if parsed.path == '/api/passwords':
            passwords = load_passwords()
            query = parse_qs(parsed.query)
            user_id = query.get('user_id', [None])[0]
            if user_id:
                passwords = [p for p in passwords if str(p.get('user_id')) == str(user_id)]
            self.send_json_response(passwords)
            return
        #generate password
        if parsed.path == '/api/generate':
            password = generate_password(12)
            self.send_json_response({"password": password})
            return
        super().do_GET()
    
    
    def do_POST(self):
        parsed = urlparse(self.path) #resolve path
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8') #convert to text
        try:
            if post_data:
                data = json.loads(post_data)
            else:   
                data = {}    
        except:
            data = {}

        # login - check username and password against the database
        if parsed.path == '/api/login':
            username = data.get('username', '').strip()
            password = data.get('password', '')
            if not username or not password:
                self.send_json_response({"error": "Missing fields"}, 400)
                return
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            # Fetch user record by username only (don't check password yet)
            cursor.execute(
                "SELECT user_id, username, password_hash, salt FROM users WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()
            conn.close()
            if row:
                # User found, now verify password using stored salt
                stored_user_id = row[0]
                stored_username = row[1]
                stored_hash = row[2]
                stored_salt = row[3]
                # Hash provided password with the SAME salt used at signup
                provided_hash, _ = hash_password(password, stored_salt)
                if provided_hash == stored_hash:
                    # Passwords match, login successful
                    self.send_json_response({"success": True, "user_id": stored_user_id, "username": stored_username})
                else:
                    # Password doesn't match
                    self.send_json_response({"error": "Wrong username or password"}, 401)
            else:
                # User not found
                self.send_json_response({"error": "Wrong username or password"}, 401)
            return

        # signup - create new user in SQLite
        if parsed.path == '/api/signup':
            username = data.get('username', '').strip()
            password = data.get('password', '')
            if not username or not password:
                self.send_json_response({"error": "Missing fields"}, 400)
                return
            # Generate hash and salt (returns both)
            password_hash, salt = hash_password(password)
            try:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                # Insert username, hash, AND salt
                cursor.execute(
                    "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
                    (username, password_hash, salt)
                )
                conn.commit()
                user_id = cursor.lastrowid  # the generated ID for this new user
                conn.close()
                self.send_json_response({"success": True, "user_id": user_id})
            except sqlite3.IntegrityError:
                # username taken - UNIQUE constraint failed
                conn.close()
                self.send_json_response({"error": "Username already exists"}, 400)
            return

        #add password
        if parsed.path == '/api/passwords':
            service = data.get('service', '')
            username = data.get('username', '')
            password = data.get('password', '')
            user_id = data.get('user_id', None)  # who this password belongs to
            if not service or not username or not password: #check if every data is there
                self.send_json_response({"error": "Missing fields"}, 400)
                return     
            encrypted = encrypt(password)        
            import time
            entry = {
                "id": int(time.time() * 1000), # id of pass is time * 1000
                "user_id": user_id,
                "service": service,
                "username": username,
                "password": encrypted,
                "createdAt": time.strftime("%m/%d/%Y") #date created
            }   
            passwords = load_passwords()
            passwords.append(entry)
            save_passwords(passwords)
            self.send_json_response({"success": True, "entry": entry})
            return
        
        if parsed.path == '/api/decrypt': # if I want to show password
            encrypted = data.get('encrypted', '')
            if encrypted:
                decrypted = decrypt(encrypted)
                self.send_json_response({"decrypted": decrypted})
            else:
                self.send_json_response({"error": "No data"}, 400) #has to be decrypted, return error
            return
        self.send_json_response({"error": "Not found"}, 404)
    
    def do_DELETE(self):
        parsed = urlparse(self.path) #resolve path
        if parsed.path.startswith('/api/passwords/'):
            try:
                entry_id = int(parsed.path.split('/')[-1])
                passwords = load_passwords()
                passwords = [p for p in passwords if p['id'] != entry_id] # load evrything but the deleted one
                save_passwords(passwords)
                self.send_json_response({"success": True})
            except:
                self.send_json_response({"error": "Invalid ID"}, 400)
            return
        if parsed.path == '/api/passwords': #clear every paaword
            save_passwords([])
            self.send_json_response({"success": True})
            return
        self.send_json_response({"error": "Not found"}, 404)
    
    #############################
    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    ###############################


#open TCP server - socket server - alawys on
def main():
    init_db()
    print(f"Starting server at http://{HOST}:{PORT}")
    print()
    with socketserver.TCPServer((HOST, PORT), PasswordManager) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(" Server stopped")


if __name__ == "__main__":
    main()
