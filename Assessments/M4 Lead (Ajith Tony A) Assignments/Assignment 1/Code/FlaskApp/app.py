from flask import Flask, render_template, url_for, request
import pandas as px
import numpy as np 
import pyramid as py
from django import *

app = Flask(__name__)
app.secret_key = "917719C121"

@app.route("/")
def root():
    return render_template("index.html")


if __name__=="__main__":
    app.run(debug=True)