from flask import *
from flask_cors import CORS
import yaml

import sqlite3
import hashlib
from pathlib import Path

from steganography import hideTextInImage

app = Flask(__name__)

FLAGS = None

# Allow Cross-origin resource sharing
CORS(app)

@app.route('/')
def index():
    """Route to index page '/'.
    Flags:
        - Cookie modification
        - Header value
        - Header modification
        - Hidden 'WIP' code with a http form
        - HTML display none 
        - HTML comment
    
    :return: Built response
    """
    # Check and set isAdmin cookie
    adminCookie = request.cookies.get('isAdmin') == "True"
    if (adminCookie == True):
        response = make_response( FLAGS['cookie'] )
        response.set_cookie('isAdmin', 'False')
        return response
    
    # Check request header flag
    flagFound = request.headers.get('X-HFlags-found')
    if (flagFound == "True"):
        return FLAGS['request-header']

    # Build classic response
    response = make_response(render_template('index.html',
                        title="home",
                        hideFlag=FLAGS['source-hide'],
                        commentFlag=FLAGS['source-comment']
                    ))
    response.headers['X-HFlags'] = FLAGS['response-header']
    response.headers['X-HFlags-found'] = 'False'
    response.set_cookie('isAdmin', 'False')
    return response


@app.route('/', methods = ["POST"])
def index_POST():
    """ POST Route to index page '/' from the hidden form
    Door to redirect page.

    Flags:
        - XSRF 
    """    
    if  ('HTTP_ORIGIN' in request.environ) and \
        (request.environ['HTTP_SEC_FETCH_SITE'] == 'cross-site'):
        return FLAGS['xsrf']

    if not('name' in request.form):
        return redirect('/')
    return redirect('/article?title=%s' % request.form['name'])


@app.route('/user/login', methods = ['POST'])
def login_post():
    """POST Route to admin login page '/user/login'.
    Create an empty fake data base to launch SQL commands.
    Compare with admin name and password without SQL escaping.
    Set an admin cookie to valid connection.
    
    Flags:
        - SQL Injection
    
    :return: Built response
    """
    if ('username' in request.form and 'password' in request.form ):
        uname, passwd = request.form['username'], request.form['password']
    else:
        uname, passwd = "", ""

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
def login_get():
    """ GET Route to admin login page '/user/login' to render the template. """
    return render_template('user/login.html')


@app.route('/static/')
def static_dir():
    """ Route to '/static/' page to render a fake directory listing """
    return render_template('static-listing.html')


@app.route('/ctf-rules')
def rules():
    """ Route to 'ctf-rules'.
    Render the template.
    No flags in this page.
    """
    return render_template('rules.html', title="rules")


@app.route('/admin')
def admin():
    """Route to '/admin' page.
    Check the validity of the admin cookie.
    Check if the 'User-Agent' header is from an 'Admin Browser'.

    Flags:
        - Result of the SQL injection on the html page.
        - 'User-Agent' to fake admin browser. 
    """
    # Check admin token or redirect 
    token = request.cookies.get('token')
    if (token != "q5vpeVphHnaMxQ2eh5brGkaGjUsOk87f"):
        return redirect('/user/login')
    
    # Check userAgent for Admin browser
    userAgent = request.headers.get('User-Agent')
    if (userAgent == "Admin/18.2"):
        return render_template('/admin.html', code=FLAGS['user-agent'], flag=FLAGS['admin-page'])
    return render_template('/admin.html', code="@;]pb(:kR[>'(&l[L)V&", flag=FLAGS['admin-page'])


@app.route('/admin', methods = ['POST'])
def logout():
    """ POST route to '/admin' page.
    Remote admin token and redirect user.
    """
    response = make_response(redirect('/admin'))
    response.set_cookie("token", "", expires=0)
    return response


@app.errorhandler(404)
def page_not_found(e):
    """ Route for 404 error page.
    Render the template.

    Flags:
        - Source code
    """
    return render_template('404.html', flag=FLAGS['not-found']), 404


@app.route('/article', methods = ["GET"])
def article():
    """Route for '/article' page
    Get the param to select an article.
    Create and fake database with default articles.
    Select an article by title. Allow SQL injection.

    Flags:
        - Default flag for getting this hidden page.
        - SQL injected flag.

    :param title: Seached article title
    """
    title = request.args.get("title", "\'")
    
    # Whitelist default title
    if (title in ['Article title', 'Article title2']):
        return FLAGS['hidden-form-index'] 
    # Create Table with data
    SQLcon = sqlite3.connect("sqlite3.db")
    SQLcur = SQLcon.cursor()
    SQLcmd = "CREATE TABLE IF NOT EXISTS 'articles' ('title' varchar(50) NOT NULL DEFAULT 'Article title');"
    SQLcur.execute(SQLcmd)
    SQLcmd = "INSERT INTO 'articles' ('title') VALUES ('Article Title'), ('Article Title2');"
    SQLcur.execute(SQLcmd)
    # Injection
    SQLcmd = "SELECT * FROM articles WHERE title='"+ title +"';"
    app.logger.debug(SQLcmd)
    try:
        data = SQLcur.execute(SQLcmd).fetchone() != None
    except:
        return "SQL Error please contact administrator. This incident will be reported.", 500
    if (data == False):
        return "No data found in database"
    if (data == True): # Injection sucess
        return FLAGS['url-sql-inject']
    return FLAGS['hidden-form-index']


@app.route('/contact')
def contact():
    """ Route to '/contact' that show redirection """
    return render_template('contact.html', title='contact')


@app.route('/redirect/<sum>')
def href_redirect(sum):
    """ Route to 'redirect' page
    /redirect/<SUM>?=href<URL>
    Check if hash(URL) == sum.
    Redirect the user to the URL

    Flags:
        - Correct fake redirection
    """
    link = request.args.get("href")
    hash = hashlib.md5(link.encode()).hexdigest()
    if (sum != hash):
        return "Error hash invalid."
    if not(link in ["https://twitter.com", "https://www.instagram.com", "https://www.google.com/"]):
        return "<h3>Nice job good redirection.</h3> " + FLAGS['href-redirect']
    return redirect(link)


def loadConfig(path='./config.yml'):
    with open(path, 'r') as fp:
        global FLAGS
        obj = yaml.safe_load(fp.read())
        FLAGS = obj['flags']
        assert (FLAGS is not None)
        print(f' * Config file loaded: {path}')


if (__name__ == "__main__"):
    loadConfig()
    hiddenBasedPath = Path(__file__).parent.resolve().joinpath('static/hidden_based.png')
    hideTextInImage(FLAGS['image'], hiddenBasedPath)
    app.run(debug = True, host="0.0.0.0")