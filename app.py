from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import requests
import secrets
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Load API key securely
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Temporary in-memory user store
users = {}

# -------------------- Routes --------------------

@app.route("/")
def home():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", username=session["username"])


@app.route("/ask", methods=["POST"])
def ask():
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    user_msg = data.get("message") if data else None

    if not user_msg:
        return jsonify({"error": "No message provided"}), 400

    if not OPENROUTER_API_KEY:
        return jsonify({"reply": "API key not configured. Check your .env file."})

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:5000",
                "X-Title": "ChatX"
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {"role": "user", "content": user_msg}
                ]
            },
            timeout=30
        )

        print("STATUS:", response.status_code)
        print("RAW RESPONSE:", response.text)

        if response.status_code != 200:
            return jsonify({
                "reply": f"API Error ({response.status_code}): {response.text}"
            })

        result = response.json()

        if "choices" not in result or len(result["choices"]) == 0:
            return jsonify({"reply": "No response from AI."})

        reply = result["choices"][0]["message"]["content"]

        return jsonify({"reply": reply})

    except requests.exceptions.RequestException as e:
        return jsonify({"reply": f"Network Error: {str(e)}"})

    except Exception as e:
        return jsonify({"reply": f"Server Error: {str(e)}"})


# -------------------- Authentication --------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if users.get(username) == password:
            session["username"] = username
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in users:
            return render_template("register.html", error="Username already exists")

        users[username] = password
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


# -------------------- Run App --------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
