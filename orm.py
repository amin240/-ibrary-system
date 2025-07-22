from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------ Models ------------------

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    total_copies = db.Column(db.Integer, nullable=False)
    available_copies = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    author = db.relationship('Author', backref=db.backref('books', lazy=True))

# ------------------ Data Insertion ------------------

def insert_books():
    data = [
        ("The Alchemist", "Paulo Coelho", 5, 1, 70.0),
        ("1984", "George Orwell", 3, 1, 20.0),
        ("Book Title", "ahmed", 2, 1, 50.0),
        ("The Alchemist", "Paulo Coelho", 4, 1, 60.0),
        ("1984", "George Orwell", 2, 1, 70.0),
        ("Brave New World", "Aldous Huxley", 6, 1, 100.0),
        ("To Kill a Mockingbird", "Harper Lee", 4, 1, 80.0),
        ("The Catcher in the Rye", "J.D. Salinger", 3, 0, 60.0),
        ("Great Expectations", "Charles Dickens", 5, 1, 90.0),
        ("Moby Dick", "Herman Melville", 3, 1, 150.0),
        ("War and Peace", "Leo Tolstoy", 4, 1, 90.0),
        ("Crime and Punishment", "Fyodor Dostoevsky", 2, 1, 75.0),
        ("Pride and Prejudice", "Jane Austen", 4, 1, 100.0),
        ("track", "mohamed", 1, 1, None),
    ]

    for title, author_name, total, available, price in data:
        # Check if the author already exists
        author = Author.query.filter_by(name=author_name).first()
        if not author:
            author = Author(name=author_name)
            db.session.add(author)
            db.session.flush()  # Ensure author.id is available

        # Create book entry
        book = Book(
            title=title,
            total_copies=total,
            available_copies=available,
            price=price if price is not None else 0.0,
            author_id=author.id
        )
        db.session.add(book)

    db.session.commit()
    print("✅ Books and authors inserted successfully.")

# ------------------ Script Execution ------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        insert_books()
