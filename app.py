from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

app.secret_key = "d4b9"
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "Srinivas@1920"
app.config["MYSQL_DB"] = "admin_panel"

mysql = MySQL(app)

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "LoggedIn" in session and session["LoggedIn"]:
        return render_template("dashboard.html", user=session["username"])
    else:
        return redirect(url_for("home"))

@app.route("/login", methods=["POST", "GET"])
def login():
    message = ""
    if request.method == "POST" and "username" in request.form and "password" in request.form:
        username = request.form["username"]
        password = request.form["password"]
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cur.fetchone()
        if user:
            session["LoggedIn"] = True
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))
        else:
            message = "Invalid Username or Password"
    return render_template("login.html", msg=message)

@app.route("/signup", methods=["POST", "GET"])
def signup():
    message = ""
    if request.method == "POST" and "username" in request.form and "password" in request.form and "repassword" in request.form:
        username = request.form["username"]
        password = request.form["password"]
        repassword = request.form["repassword"]

        if password != repassword:
            message = "Passwords do not match. Please re-enter your password."
        elif not re.match("^[A-Za-z]", username):
            message = "Username must start with a letter (a-z or A-Z)."
        else:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            
            cur.execute("SELECT * FROM users WHERE username=%s", (username,))
            existing_user = cur.fetchone()
            
            if existing_user:
                message = "Username already exists. Please choose a different one."
            else:
                cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
                mysql.connection.commit()
                
                return redirect(url_for("login"))
    
    return render_template("signup.html", msg=message) 


@app.route("/update", methods=["POST", "GET"])
def update():
    message = ""
    message_type = ""  
    if request.method == "POST" and "username" in session:
        username = session["username"]
        password = request.form["password"]
        re_password = request.form["re_password"]
        
        if password == re_password:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("UPDATE users SET password = %s WHERE username = %s", (password, username))
            mysql.connection.commit()
            message = "Successfully updated your Password."
            message_type = "success"
        else:
            message = "Passwords do not match. Please try again."
            message_type = "error"
    elif "username" not in session:
        return redirect(url_for("login"))
    return render_template("update.html", msg=message, msg_type=message_type)



@app.route("/delete", methods=["POST", "GET"])
def delete():
    message = ""
    message_type = ""
    if request.method == "POST" and "username" in session:
        username = session["username"]
        password = request.form["password"]
        
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        
        if user:
            cur.execute("DELETE FROM users WHERE username = %s AND password = %s", (username, password))
            mysql.connection.commit()
            message = "Successfully deleted your account."
            message_type = "success"
            session.clear()  
            return redirect(url_for("login", msg=message))
        else:
            message = "Invalid username or password."
            message_type = "error"
    elif "username" not in session:
        return redirect(url_for("login"))
    return render_template("delete.html", msg=message, msg_type=message_type)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
