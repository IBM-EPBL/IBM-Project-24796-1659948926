from flask import Flask,render_template,url_for,redirect
import ibm_db

app = Flask(__name__)

@app.route("/")
def get_db():
    conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=6667d8e9-9d4d-4ccb-ba32-21da3bb5aafc.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30376;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=gpz48320;PWD=I0QehUSLbAE3oquc;","","")
    return render_template("connectsuccess.html")
if __name__ == "__main__":
    app.run(debug=True)