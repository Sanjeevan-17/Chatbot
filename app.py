from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import requests
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # For production, store in environment variable

# Replace with your actual OpenRouter API key
OPENROUTER_API_KEY = "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"

# In-memory user store (temporary; replace with DB in production)
users = {}

# -------------------- Routes --------------------

@app.route("/")
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template("index.html", username=session['username'])


@app.route("/ask", methods=["POST"])
def ask():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_msg = request.json.get("message")
    if not user_msg:
        return jsonify({"error": "No message provided"}), 400

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "Referer": "http://localhost:5000",
                "X-Title": "FlaskChatApp"
            },
            json={
                "model": "mistralai/mistral-7b-instruct:free",
                "messages": [
                    {"role": "user", "content": user_msg}
                ]
            },
            timeout=30  # prevent hanging requests
        )

        data = response.json()
        print("OpenRouter API response:", data)  # Debugging

        # Try to extract reply safely
        reply = "⚠️ No response received"
        if "choices" in data and len(data["choices"]) > 0:
            choice = data["choices"][0]
            # Depending on API version, content might be under message->content or text
            if "message" in choice and "content" in choice["message"]:
                reply = choice["message"]["content"]
            elif "text" in choice:
                reply = choice["text"]

        return jsonify({"reply": reply})

    except Exception as e:
        print("Error calling OpenRouter API:", e)
        return jsonify({"error": str(e)}), 500


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
