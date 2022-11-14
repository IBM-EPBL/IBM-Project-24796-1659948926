from flask import Flask, render_template, url_for, request, flash
import ibm_db  
  
app = Flask(__name__)
app.secret_key = "917719C121"

def connectDB():
    conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=6667d8e9-9d4d-4ccb-ba32-21da3bb5aafc.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30376;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=gpz48320;PWD=I0QehUSLbAE3oquc;","","")
    return conn

@app.route("/")
def root():
    return render_template("home.html", title="Home")

@app.route("/login", methods=('POST', 'GET'))
def signin():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        userDB = connectDB()
        sql = "SELECT username FROM users WHERE password = '{0}' AND email = '{1}'".format(password, email)
        stmt = ibm_db.exec_immediate(userDB, sql)
        findUser = ibm_db.fetch_assoc(stmt)

        if findUser == False:
            error = "Incorrect Username/Password."
        
        while findUser != False:
            success = "Hey " + findUser["USERNAME"]
            findUser = ibm_db.fetch_assoc(stmt)

        if error is None:
            return render_template('home.html', title="Home", success=success)
        flash(error)

    return render_template('login.html', title='Login', error=error)

@app.route("/register", methods=('POST', 'GET'))
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        rollno = request.form['rollno']
        
        userDB = connectDB()
        sql = "INSERT INTO users (email, username, rollno, password) VALUES ('{0}', '{1}', '{2}', '{3}');".format(email, username, rollno, password)
        ibm_db.exec_immediate(userDB, sql)
        return render_template('home.html', title="Home", success="Registration Successful")

    return render_template("register.html", title="Register")

if __name__ == '__main__':
    app.run(debug=True)