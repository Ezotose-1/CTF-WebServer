from flask import *

import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    response = make_response(render_template('index.html'))
    response.headers['X-HFlags'] = 'Integer-luctus-felis'
    return response

@app.route('/user/login', methods = ['POST'])
def login():
    uname, passwd = request.form['username'], request.form['password']

    # Login to Allow SQL injection #
    con = sqlite3.connect("sqlite3.db")
    cur = con.cursor()
    cmd = "SELECT CASE WHEN 'pib'='"+ passwd +"' AND 'pib'='"+ uname +"' THEN True ELSE False END;"
    print("[DEBUG] Login page :", cmd)
    try:
        data = cur.execute(cmd).fetchone()[0] == 1
    except:
        return redirect('/user/login')
    if (data):
        return "Mauris-fermentum-massa"
    return redirect('/user/login')

@app.route('/user/login', methods = ['GET'])
def login_post():
    return render_template('user/login.html')

@app.route('/static')
def static_dir():
    return render_template('static-listing.html')

@app.route('/admin')
def admin():
    return redirect('/user/login')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if (__name__ == "__main__"):
    app.run(debug = True, host="0.0.0.0")