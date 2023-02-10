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
    1. Connection using weak username (no SQL injection possible)
       add userToken.
    2. Create an empty fake data base to launch SQL commands.
       Compare with admin name and password without SQL escaping.
       Set an admin cookie to valid connection.
    
    Flags:
        - SQL Injection
    
    :return: Built response
    """
    global FLAGS, CONFIG

    # weakUser connect: no SQL injection
    uname, passwd = request.form.get("username", ""), request.form.get("password", "")
    if uname == CONFIG['weakUserName']:
        if passwd == "saucisson2008":
            response = make_response(redirect('/admin'))
            response.set_cookie("token", CONFIG.get('userToken'))
            return response
        else:
            return redirect('/user/login')

    
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
    token = request.cookies.get('token')
    
    # Not Admin logged user
    if (token == CONFIG.get('userToken')):
        return render_template('/admin/loggedUser.html', name=CONFIG['weakUserName'], flag=FLAGS['weak-old-db'])

    # Check admin token or redirect 
    if (token != CONFIG.get('adminToken')):
        return redirect('/user/login')
    
    # Check userAgent for Admin browser
    userAgent = request.headers.get('User-Agent')
    if (userAgent.startswith("Admin/18.2")):
        return render_template('/admin/admin.html', code=FLAGS['user-agent'], flag=FLAGS['admin-page'], ssh=CONFIG['sshAccess'], weakUsername=CONFIG['weakUserName'])
    return render_template('/admin/admin.html', code="__WRONG_BROWSER__", flag=FLAGS['admin-page'], ssh=CONFIG['sshAccess'], weakUsername=CONFIG['weakUserName'])


@app.route('/.passwd')
def passwd():
    return """
root:x:0:0:root:/root:/bin/ash <br>
bin:x:1:1:bin:/bin:/sbin/nologin <br>
daemon:x:2:2:daemon:/sbin:/sbin/nologin <br>
adm:x:3:4:adm:/var/adm:/sbin/nologin <br>
lp:x:4:7:lp:/var/spool/lpd:/sbin/nologin <br>
sync:x:5:0:sync:/sbin:/bin/sync <br>
shutdown:x:6:0:shutdown:/sbin:/sbin/shutdown <br>
halt:x:7:0:halt:/sbin:/sbin/halt <br>
mail:x:8:12:mail:/var/mail:/sbin/nologin <br>
news:x:9:13:news:/usr/lib/news:/sbin/nologin <br>
uucp:x:10:14:uucp:/var/spool/uucppublic:/sbin/nologin <br>
operator:x:11:0:operator:/root:/sbin/nologin <br>
man:x:13:15:man:/usr/man:/sbin/nologin <br>
postmaster:x:14:12:postmaster:/var/mail:/sbin/nologin <br>
cron:x:16:16:cron:/var/spool/cron:/sbin/nologin <br>
ftp:x:21:21::/var/lib/ftp:/sbin/nologin <br>
sshd:x:22:22:sshd:/dev/null:/sbin/nologin <br>
at:x:25:25:at:/var/spool/cron/atjobs:/sbin/nologin <br>
squid:x:31:31:Squid:/var/cache/squid:/sbin/nologin <br>
xfs:x:33:33:X Font Server:/etc/X11/fs:/sbin/nologin <br>
games:x:35:35:games:/usr/games:/sbin/nologin <br>
cyrus:x:85:12::/usr/cyrus:/sbin/nologin <br>
vpopmail:x:89:89::/var/vpopmail:/sbin/nologin <br>
ntp:x:123:123:NTP:/var/empty:/sbin/nologin <br>
smmsp:x:209:209:smmsp:/var/spool/mqueue:/sbin/nologin <br>
guest:x:405:100:guest:/dev/null:/sbin/nologin <br>
nobody:x:65534:65534:nobody:/:/sbin/nologin <br>
vnstat:x:101:102:vnstat:/var/lib/vnstat:/bin/false <br>
user:x:1002:1002:,,,:/home/user:/bin/42sh <br>
"""


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
    Create and fake database with default articles and flags.
    Select an article by title. Allow SQL injection.

    Flags:
        - Easy injection ('OR 1=1;--)
        - SQLmap injection in 'flag' table

    :param title: Seached article title
    :return: json throw dictionary 
    """
    global FLAGS
    title = request.args.get("title", "\'")
    if 'sleep' in title.lower():
        return {'error': 'sql not valid'}
    data = articleQuery(title, FLAGS)
    return data


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
init(FLAGS, CONFIG)

if (__name__ == "__main__"):
    app.run(debug = True,
            host=CONFIG.get('host'),
            port=CONFIG.get('port'))
