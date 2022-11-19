from flask import Flask, render_template, request, redirect, url_for, session
import ibm_db
import re
from logging import error
from jinja2.utils import select_autoescape
import bcrypt
import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


app = Flask(__name__, template_folder='template')
app.secret_key = 'a'
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=6667d8e9-9d4d-4ccb-ba32-21da3bb5aafc.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30376;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=gpz48320;PWD=I0QehUSLbAE3oquc;", "", "")


@app.route("/", methods=['POST', 'GET'])
def login():
    global Userid
    msg = ''

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        sql = "SELECT * FROM users WHERE EMAIL=? AND PASSWORD=?"  # from db2 sql table
        stmt = ibm_db.prepare(conn, sql)

        # this username & password is should be same as db-2 details & order also
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            session['Loggedin'] = True
            session['id'] = account['EMAIL']
            Userid = account['EMAIL']
            session['email'] = account['EMAIL']
            msg = "logged in successfully !"
            return render_template('home.html', msg=msg, user=email)
        else:
            msg = "Incorrect Email/password"
    return render_template('login.html', msg=msg)


@app.route("/signup", methods=['POST', 'GET'])
def signup():
    msg = ''
    if request.method == 'POST':
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        sql = "SELECT* FROM users WHERE name= ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, name)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            return render_template('signup.html', error=True)
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = "Invalid Email Address!"
        else:
            insert_sql = "INSERT INTO users VALUES (?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            # this username & password is should be same as db-2 details & order also
            ibm_db.bind_param(prep_stmt, 1, name)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, password)
            ibm_db.execute(prep_stmt)
            msg = "You have successfully registered !"
    return render_template('signup.html', msg=msg)


@app.route("/home", methods=["POST", "GET"])
def home():

    if (request.method == "POST"):
        LAT = request.form["lat"]
        LONG = request.form["lon"]
        VISITED = 0
        if (LAT == "" or LONG == ""):
            return render_template('home.html', success=0)
        else:
            insert_sql = "INSERT INTO geodata VALUES (?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, LAT)
            ibm_db.bind_param(prep_stmt, 2, LONG)
            ibm_db.bind_param(prep_stmt, 3, VISITED)
            ibm_db.execute(prep_stmt)
            return render_template('home.html', success=True)
    return render_template('home.html')


@app.route('/data')
def data():

    finaldata = []
    sql = "SELECT * FROM geodata"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_assoc(stmt)

    while dictionary != False:
        location = []
        location.append(dictionary["LAT"])
        location.append(dictionary["LONG"])
        location.append(dictionary["VISITED"])
        finaldata.append(location)
        print(location)
        dictionary = ibm_db.fetch_assoc(stmt)
    print(finaldata)
    return render_template('data.html', responses=finaldata)

# chechk this function for errors


@app.route("/android_sign_up", methods=["POST"])
def upload():
    if (request.method == "POST"):

        # get the data from the form
        name = request.json['name']
        email = request.json['email']
        password = request.json['password']

        sql = "SELECT * FROM user WHERE email =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if account:
            return {'status': 'failure'}
        else:
            insert_sql = "INSERT INTO user VALUES (?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, name)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, password)

            ibm_db.execute(prep_stmt)
            return {"id": "1"}


@app.route("/location_data")
def location_data():
    locationdata = []
    sql = "select * from location"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary != False:
        #  print ("The Name is : ",  dictionary)
        locationdata.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)
    return json.dumps(locationdata)


@app.route("/post_user_location_data", methods=["POST"])
def post_user_location():
    if (request.method == "POST"):
        lat = request.json['lat']
        lon = request.json['long']
        id = request.json['id']
        ts = request.json['timestamp']

        insert_sql = "INSERT INTO USER_LOCATION VALUES (?,?,?,?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, lat)
        ibm_db.bind_param(prep_stmt, 2, lon)
        ibm_db.bind_param(prep_stmt, 3, id)
        ibm_db.bind_param(prep_stmt, 4, ts)

        ibm_db.execute(prep_stmt)
        return {"response": "success"}


@app.route("/send_trigger", methods=["POST"])
def send_trigger():
    if (request.method == "POST"):
        # get the data from the form
        email = request.json['email']
        location_id = request.json['id']

        sql = "SELECT vis FROM Location WHERE SNO =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, location_id)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if account:
            visited = account[0]
            visited = visited+1
            sql = "UPDATE LOCATION SET vis = ? WHERE SNO=?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, visited)
            ibm_db.bind_param(stmt, 1, location_id)
            ibm_db.execute(stmt)

            send_mail(email)
            return {"response": "success"}
        else:
            return {"response": "failure"}


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)
    return render_template('login.html')


def send_mail(email):
    print(email)
    message = Mail(
        from_email='ajithtony@student.tce.edu',
        to_emails=email,
        subject='Containment Zone Alert!!!',
        html_content='<img src="https://cdn-icons-png.flaticon.com/512/4329/4329979.png" height="30px" width="30px"><br><strong> Alert!! You are currently entering a Containment Zone. Please turn back immediately </strong>')
    try:
        sg = SendGridAPIClient(
            "")
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)


def create_bcrypt_hash(password):
    # convert the string to bytes
    password_bytes = password.encode()
    # generate a salt
    salt = bcrypt.gensalt(14)
    # calculate a hash as bytes
    password_hash_bytes = bcrypt.hashpw(password_bytes, salt)
    # decode bytes to a string
    password_hash_str = password_hash_bytes.decode()
    return password_hash_str


def verify_password(password, hash_from_database):
    password_bytes = password.encode()
    hash_bytes = hash_from_database.encode()

    # this will automatically retrieve the salt from the hash,
    # then combine it with the password (parameter 1)
    # and then hash that, and compare it to the user's hash
    does_match = bcrypt.checkpw(password_bytes, hash_bytes)

    return does_match


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=False)
