# Copyright (c) 2024 Vinod Kumar Mishra
# This file is part of Visitorinout.
# Visitorinout is released under the MIT License.
# See the License file for more details.

import mysql.connector
from flask import g

def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host='localhost',
            database='libraryvisitor',            # Your new database for visitors
            user='koha_readonly',           # Replace with your MariaDB username
            password='readonly_password'            # Replace with your MariaDB password
        )
    return g.db

def get_koha_db():
    if 'koha_db' not in g:
        g.koha_db = mysql.connector.connect(
            host='localhost',
            database='koha_library',              # Your Koha database
            user='koha_readonly',           # Replace with your MariaDB username
            password='readonly_password'            # Replace with your MariaDB password
        )
    return g.koha_db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

    koha_db = g.pop('koha_db', None)
    if koha_db is not None:
        koha_db.close()
