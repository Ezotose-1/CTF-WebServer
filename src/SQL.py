import sqlite3

def articleQuery(title: str):
    """ Run an SQL Query to an fake database to allow SQL injection
    on article listing query.
    SQLcmd with user input are never commited to the fake database.

    :param title: Searched article.
    :return: Boolean True if valid SQL value,
             None if there is not such article.
    :throw: Exception if SQL Error.
    """
    # Connect to the DB
    SQLcon = sqlite3.connect("sqlite3.db")
    SQLcur = SQLcon.cursor()

    # Create Table with data
    SQLcmd = "CREATE TABLE IF NOT EXISTS 'articles' ('title' varchar(50) NOT NULL DEFAULT 'Article title');"
    SQLcur.execute(SQLcmd)
    SQLcmd = "INSERT INTO 'articles' ('title') VALUES ('Article Title'), ('Article Title2');"
    SQLcur.execute(SQLcmd)

    # Injection
    SQLcmd = f"SELECT * FROM articles WHERE title='{title}';"
    data = SQLcur.execute(SQLcmd).fetchone() != None

    return data


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



def week_cypher(plaintext,n):
    ans = ""
    for i in range(len(plaintext)):
        ch = plaintext[i]
        if ch.isalpha() is False:
            ans+=ch
        elif (ch.isupper()):
            ans += chr((ord(ch) + n-65) % 26 + 65)      
        else:
            ans += chr((ord(ch) + n-97) % 26 + 97)
    return ans



def generateOldDatabase(flag: str, path="src/static/oldDb.sqlite3"):
    password = week_cypher(plaintext=flag, n=42)
    print(password)

    # Connect to the DB
    SQLcon = sqlite3.connect(path)
    SQLcur = SQLcon.cursor()

    # Create Table with data
    SQLcmd = "CREATE TABLE IF NOT EXISTS 'users' ('username' varchar(50), 'password' varchar(50));"
    SQLcur.execute(SQLcmd)
    SQLcmd = "DELETE FROM 'users';"
    SQLcur.execute(SQLcmd)
    SQLcmd = f"INSERT INTO 'users' ('username', 'password') VALUES ('Admin', '{password}');"
    SQLcur.execute(SQLcmd)
    
    # Save it
    SQLcon.commit()
    return True

if (__name__ == "__main__"):
    generateOldDatabase("Je Vote Test.")
