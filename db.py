import mysql.connector
from flask import g

def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host='localhost',
            database='libraryvisitor',  # Your new database for visitors
            user='libraryvisitor_user',               # Replace with your MariaDB username
            password='secure_password'            # Replace with your MariaDB password
        )
    return g.db

def get_koha_db():
    if 'koha_db' not in g:
        g.koha_db = mysql.connector.connect(
            host='localhost',
            database='koha_library',    # Your Koha database
            user='libraryvisitor_user',                # Replace with your MariaDB username
            password='secure_password'            # Replace with your MariaDB password
        )
    return g.koha_db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

    koha_db = g.pop('koha_db', None)
    if koha_db is not None:
        koha_db.close()
