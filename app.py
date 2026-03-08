from flask import Flask, render_template, request, session, redirect, jsonify, send_file
import random
import string
import pandas as pd

from database import create_user, validate_user, save_password, get_passwords, delete_password


app = Flask(__name__)
app.secret_key = "industry_secret"


# HOME PAGE
@app.route("/")
def home():
    return render_template("login.html")


# SIGNUP PAGE
@app.route("/signup")
def signup():
    return render_template("signup.html")


# REGISTER USER (FIXED - ONLY ONE FUNCTION)
@app.route("/register", methods=["POST"])
def register():

    username = request.form["username"]
    password = request.form["password"]

    success = create_user(username, password)

    if success:

        return render_template(
            "signup.html",
            success="Account created successfully! You can now login."
        )

    else:

        return render_template(
            "signup.html",
            error="Username already exists"
        )


# LOGIN USER
@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    user = validate_user(username, password)

    if user:

        session["user"] = username
        return redirect("/dashboard")

    else:
        return render_template(
            "login.html",
            error="Invalid username or password"
        )


# DASHBOARD
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    return render_template("dashboard.html")


# GENERATE PASSWORD
@app.route("/generate", methods=["POST"])
def generate():

    if "user" not in session:
        return jsonify({"password":"Unauthorized"})

    data=request.json

    length=int(data["length"])
    strength=data["strength"]
    upperCount=int(data.get("upperCount",0))
    symbolCount=int(data.get("symbolCount",0))
    customWord=data.get("custom","").strip()

    lowercase=string.ascii_lowercase
    uppercase=string.ascii_uppercase
    digits=string.digits

    # ONLY allowed symbols
    allowed_symbols="!@#$_&"

    password=""

    # If custom word exists → use it directly
    if customWord:

        password=customWord

        # add required uppercase
        for _ in range(upperCount):
            password+=random.choice(uppercase)

        # add required symbols
        for _ in range(symbolCount):
            password+=random.choice(allowed_symbols)

        # fill remaining
        remaining=length-len(password)

        pool=lowercase+digits

        for _ in range(max(0,remaining)):
            password+=random.choice(pool)

    else:

        # strength based generation
        if strength=="weak":

            pool=lowercase

        elif strength=="medium":

            pool=lowercase+uppercase+digits

        elif strength=="strong":

            pool=lowercase+uppercase+digits+allowed_symbols

        else:

            pool=lowercase+uppercase+digits+allowed_symbols

        password="".join(random.choice(pool) for _ in range(length))


        # ensure uppercase count
        for _ in range(upperCount):
            password+=random.choice(uppercase)

        # ensure symbol count
        for _ in range(symbolCount):
            password+=random.choice(allowed_symbols)


        password=password[:length]


    save_password(session["user"],password)

    return jsonify({"password":password})
# PASSWORD HISTORY
@app.route("/history")
def history():

    if "user" not in session:
        return jsonify([])

    passwords = get_passwords(session["user"])

    return jsonify(passwords)


# DELETE PASSWORD
@app.route("/delete/<int:id>", methods=["DELETE"])
def delete(id):

    delete_password(id)

    return jsonify({"status": "deleted"})

# EXPORT PASSWORDS
@app.route("/export")
def export():

    if "user" not in session:
        return redirect("/")

    data = get_passwords(session["user"])

    df = pd.DataFrame(data, columns=["ID", "Password"])

    df.to_csv("passwords.csv", index=False)

    return send_file(
        "passwords.csv",
        as_attachment=True
    )


# LOGOUT
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# RUN APP
if __name__ == "__main__":
    app.run(debug=True)