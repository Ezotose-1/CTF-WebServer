#! /usr/bin/env python3

from flask import *
from flask_cors import CORS

import hashlib

from loading import init, loadConfig
from SQL import articleQuery, loginQuery

app = Flask(__name__)

FLAGS = None
CONFIG = None

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
        - Favicon
    
    :return: Built response
    """
    global FLAGS
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
                        commentFlag=FLAGS['source-comment']))

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
    global FLAGS
    if  ('HTTP_ORIGIN' in request.environ) and \
        (request.environ['HTTP_SEC_FETCH_SITE'] == 'cross-site'):
        return FLAGS['xsrf']

    if 'name' in request.form:
        return redirect( f'/article?title={request.form["name"]}' )
    return redirect('/')


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
    global FLAGS, CONFIG

    uname, passwd = request.form.get("username", ""), request.form.get("password", "")
    # Login to Allow SQL injection #
    try:
        data = loginQuery(username=uname, password=passwd)
    except Exception as e:
        return redirect('/user/login')
    
    # Connect user by adding a 'admin' token in cookies
    if (data):
        response = make_response(redirect('/admin'))
        response.set_cookie("token", CONFIG.get('adminToken'))
        return response    
    return redirect('/user/login')


@app.route('/user/login', methods = ['GET'])
def login_get():
    """ GET Route to admin login page '/user/login' to render the template. """
    global FLAGS
    return render_template('user/login.html')


@app.route('/static/')
def static_dir():
    """ Route to '/static/' page to render a fake directory listing """
    global FLAGS
    return render_template('static-listing.html')


@app.route('/ctf-rules')
def rules():
    """ Route to 'ctf-rules'.
    Render the template.
    No flags in this page.
    """
    global FLAGS
    return render_template('rules.html', title="rules", flagCount = len(FLAGS))


@app.route('/admin')
def admin():
    """Route to '/admin' page.
    Check the validity of the admin cookie.
    Check if the 'User-Agent' header is from an 'Admin Browser'.

    Flags:
        - Result of the SQL injection on the html page.
        - 'User-Agent' to fake admin browser. 
    """
    global FLAGS, CONFIG
    # Check admin token or redirect 
    token = request.cookies.get('token')
    if (token != CONFIG.get('adminToken')):
        return redirect('/user/login')
    
    # Check userAgent for Admin browser
    userAgent = request.headers.get('User-Agent')
    if (userAgent.startswith("Admin/18.2")):
        return render_template('/admin.html', code=FLAGS['user-agent'], flag=FLAGS['admin-page'], ssh=CONFIG['sshAccess'])
    return render_template('/admin.html', code="__WRONG_BROWSER__", flag=FLAGS['admin-page'], ssh=CONFIG['sshAccess'])


@app.route('/admin', methods = ['POST'])
def logout():
    """ POST route to '/admin' page.
    Remote admin token and redirect user.
    """
    global FLAGS
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
    global FLAGS
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
    global FLAGS
    title = request.args.get("title", "\'")
    
    # Whitelist default title
    if (title in ['Article title', 'Article title2']):
        return { 'api_flag1': FLAGS['hidden-form-index'] }
    try:
        data = articleQuery(title)
    except:
        return {'error': "SQL Error please contact administrator. This incident will be reported."}, 500
    if (data == False):
        return {'error': "No data found in database"}, 404
    if (data == True): # Injection sucess
        return { 'api_flag2': FLAGS['url-sql-inject']}
    return { 'api_flag1': FLAGS['hidden-form-index']}


@app.route('/contact')
def contact():
    """ Route to '/contact' that show redirection """
    global FLAGS
    URL = CONFIG.get('contact')

    twitterLink =  hashlib.md5(URL.get('twitter').encode()).hexdigest()
    instaLink =  hashlib.md5(URL.get('insta').encode()).hexdigest()
    googleLink =  hashlib.md5(URL.get('google').encode()).hexdigest()

    return render_template('contact.html',
        title='contact',
        email = URL.get('mail'),
        hash = {
            '1': twitterLink,
            '2': instaLink,
            '3': googleLink,
        },
        links = {
            '1': URL.get('twitter'),
            '2': URL.get('insta'),
            '3': URL.get('google'),
        },
    )


@app.route('/redirect/<sum>')
def href_redirect(sum):
    """ Route to 'redirect' page
    /redirect/<SUM>?=href<URL>
    Check if hash(URL) == sum.
    Redirect the user to the URL

    Flags:
        - Correct fake redirection
    """
    global FLAGS
    URL = CONFIG.get('contact')
    link = request.args.get("href", "www.votaite.st")
    hash = hashlib.md5(link.encode()).hexdigest()
    if (sum != hash):
        return "Error hash invalid."
    if link not in [URL.get('twitter'), URL.get('insta'), URL.get('google')]:
        return f"<h3>Nice job good redirection.</h3> {FLAGS['href-redirect']}"
    return redirect(link)


@app.route('/votai')
def votai():
    name = "".join(request.args)
    for bde in ['Kraken']:
        name = name.replace(bde, "Test.")    
    name = name.replace('document.cookie', f"'AdminSession={FLAGS['XSS']}'")
    return render_template('vote.html', title='votai', value=name, hasvote=request.cookies.get('hasVotai', False))


@app.route('/votai/ok')
def a_votai():
    resp = make_response(redirect('/votai?Test.'))
    resp.set_cookie('hasVotai', "Test.")
    return resp


FLAGS, CONFIG = loadConfig()
init(FLAGS)

if (__name__ == "__main__"):
    app.run(debug = True,
            host=CONFIG.get('host'),
            port=CONFIG.get('port'))
