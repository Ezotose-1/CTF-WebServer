from flask import *

import sqlite3
import hashlib

app = Flask(__name__)


@app.route('/')
def index():
    # Check and set isAdmin cookie    
    adminCookie = request.cookies.get('isAdmin') == "True"
    if (adminCookie == True):
        response = make_response('Morbi-mollis-bibendum')
        response.set_cookie('isAdmin', 'False')
        return response
    # Check request header flag
    flagFound = request.headers.get('X-HFlags-found')
    if (flagFound == "True"):
        return "Quisque-placerat-commodo"
    # Build classic response
    response = make_response(render_template('index.html', title="home"))
    response.headers['X-HFlags'] = 'Integer-luctus-felis'
    response.headers['X-HFlags-found'] = 'False'
    response.set_cookie('isAdmin', 'False')
    return response

@app.route('/user/login', methods = ['POST'])
def login():
    uname, passwd = request.form['username'], request.form['password']
    # Login to Allow SQL injection #
    SQLcon = sqlite3.connect("sqlite3.db")
    SQLcur = SQLcon.cursor()
    SQLcmd = "SELECT CASE WHEN 'pib'='"+ passwd +"' AND 'pib'='"+ uname +"' THEN True ELSE False END;"
    try:
        data = SQLcur.execute(SQLcmd).fetchone()[0] == 1
    except:
        return redirect('/user/login')
    # Connect user by adding a 'admin' token in cookies
    if (data):
        response = make_response(redirect('/admin'))
        response.set_cookie("token", "q5vpeVphHnaMxQ2eh5brGkaGjUsOk87f")
        return response
    return redirect('/user/login')

@app.route('/user/login', methods = ['GET'])
def login_post():
    return render_template('user/login.html')

# Render a directory listing for /static/ files
@app.route('/static/')
def static_dir():
    return render_template('static-listing.html')

@app.route('/ctf-rules')
def rules():
    return render_template('rules.html', title="rules")

@app.route('/admin')
def admin():
    # Check admin token or redirect 
    token = request.cookies.get('token')
    if (token != "q5vpeVphHnaMxQ2eh5brGkaGjUsOk87f"):
        return redirect('/user/login')
    # Check userAgent for Admin browser
    userAgent = request.headers.get('User-Agent')
    if (userAgent == "Admin/18.2"):
        return render_template('/admin.html', code="Morbi-at-turpis")
    return render_template('/admin.html', code="@;]pb(:kR[>'(&l[L)V&")

@app.route('/admin', methods = ['POST'])
def logout():
    response = make_response(redirect('/admin'))
    response.set_cookie("token", "", expires=0)
    return response

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/', methods = ["POST"])
def index_POST():
    return redirect('/article?title=%s' % request.form['name'])

@app.route('/article', methods = ["GET"])
def article():
    title = request.args.get("title")
    print(title)
    if (title in ['Article title', 'Article title2']):
        return "Aliquam-eleifend-ornare" 
    # Allow SQL injection in URL #
    SQLcon = sqlite3.connect("sqlite3.db")
    SQLcur = SQLcon.cursor()
    # Create Table with data
    SQLcmd = "CREATE TABLE IF NOT EXISTS 'articles' ('title' varchar(50) NOT NULL DEFAULT 'Article title');"
    SQLcur.execute(SQLcmd)
    SQLcmd = "INSERT INTO 'articles' ('title') VALUES ('Article Title'), ('Article Title2');"
    SQLcur.execute(SQLcmd)
    # Injection
    SQLcmd = "SELECT * FROM articles WHERE title='"+ title +"';"
    print(SQLcmd)
    try:
        data = SQLcur.execute(SQLcmd).fetchone() != None
    except:
        return "SQL Error please contact administrator. This incident will be reported.", 500
    print(data)
    if (data == False):
        return "No data found in database"
    if (data == True):
        return "In-vitae-laoreet"
    return "Aliquam-eleifend-ornare" 

@app.route('/contact')
def contact():
    return render_template('contact.html', title='contact')

@app.route('/redirect/<sum>')
def href_redirect(sum):
    link = request.args.get("href")
    hash = hashlib.md5(link.encode()).hexdigest()
    if (sum != hash):
        return "Error hash invalid."
    if not(link in ["https://twitter.com", "https://www.instagram.com", "https://www.google.com"]):
        return "<h3>Nice job good redirection.</h3> Aliquam-erat-volutpat"
    return redirect(link)


if (__name__ == "__main__"):
    app.run(debug = True, host="0.0.0.0")