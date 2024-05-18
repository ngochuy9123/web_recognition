from flask import Blueprint, render_template
from .extensions import mysql
views = Blueprint('views',__name__)

@views.route('/')
def home():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM account")
    data = cur.fetchall()
    print(data)
    cur.close()
    return render_template("home.html")