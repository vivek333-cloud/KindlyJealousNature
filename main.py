from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
from datetime import datetime

app = Flask(__name__)  # Moved to the top
app.secret_key = "vivek@265"

# Load data from JSON file
def load_data():
    if os.path.exists("rates.json"):
        with open("rates.json", "r") as file:
            try:
                data = json.load(file)
                if isinstance(data, dict):
                    return data.get("rates", []), data.get("last_updated", "Unknown")
                return [], "Unknown"  # If structure is incorrect, return empty data
            except json.JSONDecodeError:
                return [], "Unknown"  # Handle corrupted JSON files
    return [], "Unknown"

# Save data to JSON file
def save_data(rates):
    data = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "rates": rates
    }
    with open("rates.json", "w") as file:
        json.dump(data, file, indent=4)

@app.route("/")
def index():
    rates, last_updated = load_data()
    return render_template("index.html", rates=rates, last_updated=last_updated)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "logged_in" not in session or not session["logged_in"]:
        return redirect(url_for("login"))

    rates, last_updated = load_data()

    if request.method == "POST":
        new_id = max([r["id"] for r in rates], default=0) + 1  # Generate new ID safely
        new_rate = {
            "id": new_id,
            "date": request.form["date"],
            "quality": request.form["quality"],
            "price": request.form["price"]
        }
        rates.append(new_rate)
        save_data(rates)
        return redirect("/admin")

    return render_template("admin.html", rates=rates, last_updated=last_updated)

@app.route("/edit/<int:rate_id>", methods=["GET", "POST"])
def edit(rate_id):
    rates, last_updated = load_data()
    rate = next((r for r in rates if r["id"] == rate_id), None)

    if not rate:
        return "Error: Rate not found.", 404  # Proper error handling

    if request.method == "POST":
        rate["date"] = request.form["date"]
        rate["quality"] = request.form["quality"]
        rate["price"] = request.form["price"]
        save_data(rates)
        return redirect("/admin")

    return render_template("edit.html", rate=rate, cache_buster=datetime.now().timestamp())

@app.route("/delete/<int:rate_id>")
def delete(rate_id):
    rates, last_updated = load_data()
    rates = [r for r in rates if r["id"] != rate_id]
    save_data(rates)
    return redirect("/admin")

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "poha123"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("admin"))
        else:
            return render_template("login.html", error="Invalid username or password.")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)