from hashlib import sha256

import sqlite3
import psycopg2


class db():
    DATABASE="postgresctf"
    USER="postgres"
    PASSWORD="postgresctfpasswd"
    HOST="127.0.0.1"
    PORT="5432"


def connectArticleDB():
    """ Connect into the database and return the db connection object. """
    try:
        conn = psycopg2.connect(database = db.DATABASE, user = db.USER, password = db.PASSWORD, host = db.HOST, port = db.PORT)
    except psycopg2.OperationalError:
        print(f'database: {db.DATABASE} ; user: {db.USER} ; host: {db.HOST}')
        print("Cannot open database.")
        return None
    else:
        print("Opened database successfully")
    return conn


def generateArticleDatabase(conn, FLAGS):
    """ Wipe the db and add cleaned objects. """
    cur = conn.cursor()

    # articles TABLE
    cur.execute('''DROP TABLE IF EXISTS articles''')    
    cur.execute('''CREATE TABLE IF NOT EXISTS articles
          (ID INT PRIMARY KEY     NOT NULL,
          TITLE           TEXT    NOT NULL,
          CONTENT         TEXT     NOT NULL);''')
    cur.execute(f'''INSERT INTO articles(id, title, content)
                 VALUES(1, 'Article title', '...'), (2, 'Article title2', '...'), (42, 'flag', '{FLAGS["url-sql-inject"]}');''')

    # flag TABLE
    cur.execute('''DROP TABLE IF EXISTS flag''')
    cur.execute('''CREATE TABLE IF NOT EXISTS flag
          (VALUE          TEXT    NOT NULL);''')
    cur.execute(f'''INSERT INTO flag(value)
                 VALUES('{FLAGS["sqlmap"]}');''')

    conn.commit()
    return True


def articleQuery(title: str, FLAGS):
    """ Run an unsafe query into article table of the database.
    Connect to local postgreSQL database.
    Wipe and regenerate the db.
    Execute an unsafe query.
    Return all data found.

    :param title: User input.
    :param FLAGS: dictionary with all flags to add in the db.
    :return: Dictionary
    """
    conn = connectArticleDB()
    if not conn:
        return { 'error': 'cannot connect to the database' }

    generateArticleDatabase(conn, FLAGS)

    query = f'''SELECT * FROM articles WHERE title = '{title}';'''

    cur = conn.cursor()
    try:
        cur.execute(query)
    except:
        return {'error': 'QueryError: this incident will be reported.'}
    rows = cur.fetchall()

    result = {}
    for i, r in enumerate(rows):
        if (len(r) >= 3):
            result[i] = {
                'id': r[0],
                'title': r[1],
                'content': r[2],
            }
        result[i] = r

    conn.commit()
    conn.close()
    return result


def loginQuery(username: str, password: str):
    """ Run an SQL Query to an fake database to allow SQL injection
    on user login query.
    SQLcmd with user input are never commited to the fake database.

    :param username: Login username
    :param password: Login password
    :return: Boolean True if logged.
    """
    # Connect to the DB
    SQLcon = sqlite3.connect("sqlite3.db")
    SQLcur = SQLcon.cursor()

    # Create Table with data
    SQLcmd = "CREATE TABLE IF NOT EXISTS 'users' ('username' varchar(50), 'password' varchar(50));"
    SQLcur.execute(SQLcmd)
    SQLcmd = "INSERT INTO 'users' ('username', 'password') VALUES ('Admin', 'd64eced51fb64eb208ad1f74a086c8d8d724e7881');"
    SQLcur.execute(SQLcmd)
    
    # Injection
    SQLcmd = f"SELECT * FROM users WHERE username='{username}' AND password='{password}';"
    data = SQLcur.execute(SQLcmd).fetchone() != None
    return data



def week_cypher(plaintext):
    return sha256(plaintext.encode()).hexdigest()



def generateOldDatabase(username: str, password: str, path="src/static/oldDb.sqlite3"):
    password = week_cypher(plaintext=password)

    # Connect to the DB
    SQLcon = sqlite3.connect(path)
    SQLcur = SQLcon.cursor()

    # Create Table with data
    SQLcmd = "CREATE TABLE IF NOT EXISTS 'users' ('username' varchar(50), 'password' varchar(50));"
    SQLcur.execute(SQLcmd)
    SQLcmd = "DELETE FROM 'users';"
    SQLcur.execute(SQLcmd)
    SQLcmd = f"INSERT INTO 'users' ('username', 'password') VALUES ('{username}', '{password}');"
    SQLcur.execute(SQLcmd)
    SQLcmd = f"INSERT INTO 'users' ('username', 'password') VALUES ('Admin', 'cb54bf327a26a4595699574f27c6a3050b2964aa529363daf2d20c24fbaf587d');"
    SQLcur.execute(SQLcmd)
    
    # Save it
    SQLcon.commit()
    return True



if (__name__ == "__main__"):
    generateOldDatabase("Je Vote Test.")
