#!/usr/bin/python

import psycopg2

class db():
    DATABASE="postgresctf"
    USER="postgres"
    PASSWORD="postgresctfpasswd"
    HOST="127.0.0.1"
    PORT="5432"


def connectArticleDB():
    try:
        conn = psycopg2.connect(database = db.DATABASE, user = db.USER, password = db.PASSWORD, host = db.HOST, port = db.PORT)
    except psycopg2.OperationalError:
        print(f'database: {db.DATABASE} ; user: {db.USER} ; host: {db.HOST}')
        print("Cannot open database.")
        return None
    else:
        print("Opened database successfully")
    return conn


def generateArticleDatabase(conn):
    cur = conn.cursor()

    cur.execute('''DROP TABLE IF EXISTS articles''')
    cur.execute('''CREATE TABLE IF NOT EXISTS articles
          (ID INT PRIMARY KEY     NOT NULL,
          TITLE           TEXT    NOT NULL,
          CONTENT         TEXT     NOT NULL);''')

    cur.execute('''INSERT INTO articles(id, title, content)
                 VALUES(1, 'Article title', '...'), (2, 'Article title2', '...');''')
    conn.commit()


def queryArticle(title: str):
    conn = connectArticleDB()
    if not conn:
        return { 'error': 'cannot connect to the database' }

    generateArticleDatabase(conn)

    query = f'''SELECT * FROM articles WHERE title = '{title}';'''

    cur = conn.cursor()
    try:
        cur.execute(query)
    except:
        return {'error': 'QueryError: this incident will be reported.'}
    rows = cur.fetchall()

    result = []
    for r in rows:
        result.append({
            'id': r[0],
            'title': r[1],
            'content': r[2],
        })

    conn.commit()
    conn.close()
    return result



if __name__ == "__main__":
    import json
    entry = "Article titl'e"
    entry = "Article title42"
    entry = "Article title' OR 1=1;--"
    
    resp = queryArticle(title=entry)
    print(json.dumps(resp, indent=4))
