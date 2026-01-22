import sqlite3
import hashlib

def add_sample_data():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    
    # Add sample users
    sample_users = [
        ('student1', 'password123', 'user'),
        ('student2', 'password123', 'user'),
        ('john_doe', 'mypass', 'user')
    ]
    
    for username, password, role in sample_users:
        hashed_password = hashlib.md5(password.encode()).hexdigest()
        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                          (username, hashed_password, role))
        except sqlite3.IntegrityError:
            print(f"User {username} already exists")
    
    # Add sample books
    sample_books = [
        ('Python Programming', 'John Smith', '978-0123456789', 3, 3),
        ('Web Development with Flask', 'Jane Doe', '978-0987654321', 2, 2),
        ('Database Systems', 'Bob Johnson', '978-0456789123', 4, 4),
        ('Data Structures and Algorithms', 'Alice Brown', '978-0789123456', 2, 2),
        ('Machine Learning Basics', 'Charlie Wilson', '978-0321654987', 1, 1),
        ('JavaScript Fundamentals', 'Diana Prince', '978-0654321789', 3, 3),
        ('HTML & CSS Guide', 'Peter Parker', '978-0147258369', 2, 2),
        ('Software Engineering', 'Tony Stark', '978-0963852741', 1, 1)
    ]
    
    for title, author, isbn, available, total in sample_books:
        try:
            cursor.execute("INSERT INTO books (title, author, isbn, available_copies, total_copies) VALUES (?, ?, ?, ?, ?)",
                          (title, author, isbn, available, total))
        except sqlite3.IntegrityError:
            print(f"Book {title} already exists")
    
    conn.commit()
    conn.close()
    print("Sample data added successfully!")

if __name__ == '__main__':
    add_sample_data()