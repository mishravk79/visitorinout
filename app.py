from flask import Flask, request, render_template, redirect, url_for, session, flash
import bcrypt
from db import get_db, close_db, get_koha_db
import base64
import imghdr

app = Flask(__name__)
app.secret_key = 'supersecretkey'

@app.teardown_appcontext
def teardown_db(exception):
    close_db()

def verify_password(stored_password, input_password):
    input_password_bytes = input_password.encode('utf-8')
    return bcrypt.checkpw(input_password_bytes, stored_password.encode('utf-8'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_koha_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT password, flags FROM borrowers WHERE userid = %s', (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and (user['flags'] is not None and user['flags'] != 0) and verify_password(user['password'], password):
            session['username'] = username
            return redirect(url_for('check_in_out'))
        else:
            flash('You are not authorized or review your credentials again to access.')

    return render_template('login.html')

@app.route('/check_in_out', methods=['GET', 'POST'])
def check_in_out():
    if 'username' not in session:
        return redirect(url_for('login'))

    error = None
    visitor_name = None
    visitor_image = None
    visitor_image_format = None
    books_issued = []
    fetch_books = False

    if request.method == 'POST':
        cardnumber = request.form['card_number']
        fetch_books = 'fetch_books' in request.form  # Check if the checkbox is checked

        db = get_db()
        cursor = db.cursor(dictionary=True)

        # Retrieve member details
        cursor.execute('SELECT * FROM koha_library.borrowers WHERE cardnumber = %s', (cardnumber,))
        member = cursor.fetchone()

        if member:
            visitor_name = member['firstname'] + ' ' + member['surname']

            # Retrieve the image from the koha_library.patronimage table
            cursor.execute('SELECT imagefile FROM koha_library.patronimage WHERE borrowernumber = %s', (member['borrowernumber'],))
            image_record = cursor.fetchone()
            if image_record and image_record['imagefile']:
                visitor_image = base64.b64encode(image_record['imagefile']).decode('utf-8')
                visitor_image_format = imghdr.what(None, h=image_record['imagefile'])

            # Check if the visitor is currently checked in
            cursor.execute('SELECT * FROM visitorsdetail WHERE borrowernumber = %s AND checkout_time IS NULL', (member['borrowernumber'],))
            visit = cursor.fetchone()

            if visit:
                # If currently checked-in, process check-out
                cursor.execute('UPDATE visitorsdetail SET checkout_time = NOW(), staff_checkout = %s WHERE id = %s', (session['username'], visit['id']))
                flash('Thank you for visiting! We hope to see you again soon.')

                if fetch_books:
                    # Fetch books issued or renewed (conditionally based on toggle)
                    cursor.execute('''
                        SELECT b.title AS "Title of the Book", i.barcode AS "Barcode/Accession Number"
                        FROM koha_library.issues AS iss
                        JOIN koha_library.items AS i ON iss.itemnumber = i.itemnumber
                        JOIN koha_library.biblio AS b ON i.biblionumber = b.biblionumber
                        WHERE iss.borrowernumber = %s
                        AND (iss.issuedate > (
                                SELECT MAX(checkin_time) 
                                FROM visitorsdetail 
                                WHERE borrowernumber = %s 
                                AND checkout_time IS NOT NULL
                            ) OR iss.lastreneweddate > (
                                SELECT MAX(checkin_time) 
                                FROM visitorsdetail 
                                WHERE borrowernumber = %s 
                                AND checkout_time IS NOT NULL
                            ))
                        AND (iss.issuedate < NOW() OR iss.lastreneweddate < NOW())
                    ''', (member['borrowernumber'], member['borrowernumber'], member['borrowernumber']))
                    books_issued = cursor.fetchall()

            else:
                # If not checked-in, process check-in
                cursor.execute('INSERT INTO visitorsdetail (borrowernumber, checkin_time, staff_checkin) VALUES (%s, NOW(), %s)', (member['borrowernumber'], session['username']))
                flash('Thank you for coming in! If you need any help, just ask.')

            db.commit()
        else:
            error = "Visitor not found."

        cursor.close()

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Total check-in for today
    cursor.execute('SELECT COUNT(*) AS count FROM visitorsdetail WHERE DATE(checkin_time) = CURDATE()')
    total_check_in = cursor.fetchone()['count']

    # Total check-out for today
    cursor.execute('SELECT COUNT(*) AS count FROM visitorsdetail WHERE DATE(checkout_time) = CURDATE()')
    total_check_out = cursor.fetchone()['count']

    # Total currently available (checked-in but not checked-out)
    cursor.execute('SELECT COUNT(*) AS count FROM visitorsdetail WHERE checkout_time IS NULL')
    total_available = cursor.fetchone()['count']

    cursor.close()

    return render_template('check_in_out.html', total_check_in=total_check_in, total_check_out=total_check_out, total_available=total_available, error=error, visitor_name=visitor_name, visitor_image=visitor_image, visitor_image_format=visitor_image_format, books_issued=books_issued, fetch_books=fetch_books)

@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)