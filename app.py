from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from datetime import datetime, timedelta
import hashlib


app = Flask(__name__)
app.secret_key = 'library_secret_key_2024'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "library.db")


# Database initialization
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Books table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT UNIQUE,
            available_copies INTEGER DEFAULT 1,
            total_copies INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Issued books table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS issued_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            book_id INTEGER,
            issue_date DATE,
            return_date DATE,
            returned BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (book_id) REFERENCES books (id)
        )
    ''')
    
    # Insert admin user if not exists
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        admin_password = hashlib.md5('admin123'.encode()).hexdigest()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                      ('admin', admin_password, 'admin'))
    
    conn.commit()
    conn.close()

# Helper functions
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                           (username, password)).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid credentials')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                        (username, password))
            conn.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists')
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books ORDER BY title').fetchall()
    users = conn.execute('SELECT COUNT(*) as count FROM users WHERE role = "user"').fetchone()
    issued = conn.execute('SELECT COUNT(*) as count FROM issued_books WHERE returned = FALSE').fetchone()
    conn.close()
    
    return render_template('admin_dashboard.html', books=books, 
                         user_count=users['count'], issued_count=issued['count'])

@app.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books WHERE available_copies > 0 ORDER BY title').fetchall()
    issued_books = conn.execute('''
        SELECT b.title, b.author, ib.issue_date, ib.return_date, ib.returned, b.id as book_id
        FROM issued_books ib
        JOIN books b ON ib.book_id = b.id
        WHERE ib.user_id = ?
        ORDER BY ib.issue_date DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template('user_dashboard.html', books=books, issued_books=issued_books)

@app.route('/add_book', methods=['POST'])
def add_book():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    title = request.form['title']
    author = request.form['author']
    isbn = request.form['isbn']
    copies = int(request.form['copies'])
    
    conn = get_db_connection()
    conn.execute('INSERT INTO books (title, author, isbn, available_copies, total_copies) VALUES (?, ?, ?, ?, ?)',
                (title, author, isbn, copies, copies))
    conn.commit()
    conn.close()
    
    flash('Book added successfully!')
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_book/<int:book_id>')
def delete_book(book_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    conn.execute('DELETE FROM books WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()
    
    flash('Book deleted successfully!')
    return redirect(url_for('admin_dashboard'))

@app.route('/issue_book/<int:book_id>')
def issue_book(book_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM books WHERE id = ? AND available_copies > 0', (book_id,)).fetchone()
    
    if book:
        issue_date = datetime.now().date()
        return_date = issue_date + timedelta(days=14)
        
        conn.execute('INSERT INTO issued_books (user_id, book_id, issue_date, return_date) VALUES (?, ?, ?, ?)',
                    (session['user_id'], book_id, issue_date, return_date))
        conn.execute('UPDATE books SET available_copies = available_copies - 1 WHERE id = ?', (book_id,))
        conn.commit()
        flash('Book issued successfully!')
    else:
        flash('Book not available!')
    
    conn.close()
    return redirect(url_for('user_dashboard'))

@app.route('/return_book/<int:book_id>')
def return_book(book_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    conn.execute('UPDATE issued_books SET returned = TRUE WHERE user_id = ? AND book_id = ? AND returned = FALSE',
                (session['user_id'], book_id))
    conn.execute('UPDATE books SET available_copies = available_copies + 1 WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()
    
    flash('Book returned successfully!')
    return redirect(url_for('user_dashboard'))

@app.route('/search')
def search():
    query = request.args.get('q', '')
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books WHERE title LIKE ? OR author LIKE ?',
                        (f'%{query}%', f'%{query}%')).fetchall()
    conn.close()
    
    return render_template('search.html', books=books, query=query)

init_db()

if __name__ == '__main__':
    app.run()
