from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Initialize database
def init_db():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS books (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT,
                        author TEXT,
                        quantity INTEGER
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS members (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        email TEXT
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS issued_books (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        book_id INTEGER,
                        member_id INTEGER,
                        issue_date TEXT,
                        return_date TEXT,
                        FOREIGN KEY(book_id) REFERENCES books(id),
                        FOREIGN KEY(member_id) REFERENCES members(id)
                    )''')

    conn.commit()
    conn.close()

init_db()

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# ------------------ BOOK ROUTES --------------------
@app.route('/books')
def books():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    conn.close()
    return render_template('books.html', books=books)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        quantity = request.form['quantity']
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO books (title, author, quantity) VALUES (?, ?, ?)",
                       (title, author, quantity))
        conn.commit()
        conn.close()
        return redirect('/books')
    return render_template('add_book.html')

# ------------------ MEMBER ROUTES --------------------
@app.route('/members')
def members():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members")
    members = cursor.fetchall()
    conn.close()
    return render_template('members.html', members=members)

@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO members (name, email) VALUES (?, ?)", (name, email))
        conn.commit()
        conn.close()
        return redirect('/members')
    return render_template('add_member.html')

# ------------------ ISSUE / RETURN ROUTES --------------------
@app.route('/issue_book', methods=['GET', 'POST'])
def issue_book():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books WHERE quantity > 0")
    books = cursor.fetchall()
    cursor.execute("SELECT * FROM members")
    members = cursor.fetchall()

    if request.method == 'POST':
        book_id = request.form['book_id']
        member_id = request.form['member_id']
        issue_date = datetime.now().strftime("%Y-%m-%d")

        cursor.execute("INSERT INTO issued_books (book_id, member_id, issue_date) VALUES (?, ?, ?)",
                       (book_id, member_id, issue_date))
        cursor.execute("UPDATE books SET quantity = quantity - 1 WHERE id = ?", (book_id,))
        conn.commit()
        conn.close()
        return redirect('/issued_books')

    conn.close()
    return render_template('issue_book.html', books=books, members=members)

@app.route('/issued_books')
def issued_books():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT issued_books.id, books.title, members.name, issued_books.issue_date, issued_books.return_date
                      FROM issued_books
                      JOIN books ON issued_books.book_id = books.id
                      JOIN members ON issued_books.member_id = members.id''')
    issued = cursor.fetchall()
    conn.close()
    return render_template('issued_books.html', issued=issued)

@app.route('/return_book/<int:issue_id>')
def return_book(issue_id):
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    return_date = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("SELECT book_id FROM issued_books WHERE id = ?", (issue_id,))
    book_id = cursor.fetchone()[0]

    cursor.execute("UPDATE issued_books SET return_date = ? WHERE id = ?", (return_date, issue_id))
    cursor.execute("UPDATE books SET quantity = quantity + 1 WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    return redirect('/issued_books')

if __name__ == '__main__':
    app.run(debug=True)



