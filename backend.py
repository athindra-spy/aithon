from flask import Flask, request, jsonify, session
import sqlite3, os
from datetime import date
from flask_cors import CORS   # allow frontend HTML to talk to backend

app = Flask(__name__)
app.secret_key = "supersecretkey"
CORS(app)

DB_NAME = "wellness.sqlite"

# --- DB Setup ---
def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""CREATE TABLE users(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT,
                        name TEXT
                    )""")
        c.execute("""CREATE TABLE moods(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        mood TEXT,
                        sentiment TEXT,
                        recommendations TEXT,
                        entry_date TEXT
                    )""")
        conn.commit(); conn.close()

init_db()

# --- Sentiment Logic ---
def analyze_sentiment(mood):
    positives = ["happy", "joyful", "excited", "good", "great"]
    negatives = ["sad", "angry", "tired", "depressed", "bad"]

    if mood.lower() in positives:
        return "positive", "💡 Try a workout, a hobby, or connect with friends!"
    elif mood.lower() in negatives:
        return "negative", "💡 Take it easy. Try meditation, music, or a short walk."
    else:
        return "neutral", "💡 Keep balance. Maybe read or do light activity."

# --- API Routes ---

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    name, username, password = data.get("name"), data.get("username"), data.get("password")
    if not all([name, username, password]):
        return jsonify({"error":"Missing fields"}), 400

    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username,password,name) VALUES (?,?,?)",
                  (username,password,name))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error":"Username already exists"}), 400
    finally:
        conn.close()
    return jsonify({"message":"Account created successfully!"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username, password = data.get("username"), data.get("password")
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?",(username,password))
    user = c.fetchone(); conn
