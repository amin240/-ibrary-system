from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base, relationship

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

DATABASE_URL = 'sqlite:///library.db'
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

Base = declarative_base()
Session = scoped_session(sessionmaker(bind=engine))

# Models
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    mobile = Column(String)
    username = Column(String, unique=True)
    password = Column(String)
    is_admin = Column(Integer, default=0)


class Book(Base):
    __tablename__ = 'books' 
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    cost = Column(Float, default=0.0)
    available = Column(Integer, default=1)
    copies = Column(Integer, default=1)


class Log(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    book_id = Column(Integer, ForeignKey('books.id'))
    borrowed_at = Column(DateTime)
    due_at = Column(DateTime)
    returned_at = Column(DateTime, nullable=True)
    fine = Column(Float, default=0.0)
    fine_paid = Column(Integer, default=0)

    user = relationship('User')
    book = relationship('Book')


Base.metadata.create_all(engine)

# Helpers
def get_db():
    return Session()


def create_admin_if_missing():
    db = get_db()
    if not db.query(User).filter_by(username='admin').first():
        admin = User(
            first_name='Admin',
            last_name='User',
            email='admin@example.com',
            mobile='0000000000',
            username='admin',
            password='admin123',
            is_admin=1
        )
        db.add(admin)
        db.commit()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin'):
            flash("Access denied", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# Routes
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    db = get_db()
    if request.method == 'POST':
        try:
            user = User(
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                email=request.form['email'],
                mobile=request.form['mobile'],
                username=request.form['username'],
                password=request.form['password']
            )
            db.add(user)
            db.commit()
            flash("Registration successful!", "success")
            return redirect(url_for('login'))
        except:
            db.rollback()
            flash("Username already exists.", "danger")
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    db = get_db()
    if request.method == 'POST':
        user = db.query(User).filter_by(
            username=request.form['username'],
            password=request.form['password']
        ).first()
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            return redirect(url_for('admin_dashboard' if user.is_admin else 'dashboard'))
        flash("Invalid credentials", "danger")
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    user_id = session['user_id']
    user = db.query(User).get(user_id)

    books = db.query(Book).all()
    logs = db.query(Log).filter_by(user_id=user_id).all()

    # حساب الغرامات
    book_fines = {}
    for log in logs:
        if not log.returned_at and log.due_at < datetime.now():
            delay = datetime.now() - log.due_at
            minutes_late = int((delay.total_seconds() - 60) // 60) + 1
            book_fines[log.id] = minutes_late * 1.0 if minutes_late > 0 else 0.0
        else:
            book_fines[log.id] = 0.0

    borrowed_book_users = {
        log.book_id: [log.user_id]  # Store as a list for safe 'in' checks in template
        for log in logs
    }

    return render_template(
        "dashboard.html",
        user=user,
        books=books,
        logs=logs,
        borrowed_book_users=borrowed_book_users,
        book_fines=book_fines  # ✅ هنا التمرير المهم
    )



@app.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    db = get_db()
    users = db.query(User).all()
    books = db.query(Book).all()
    logs = db.query(Log).all()
    return render_template('admin.html', users=users, books=books, logs=logs)


@app.route('/borrow/<int:book_id>')
@login_required
def borrow(book_id):
    db = get_db()
    book = db.query(Book).filter_by(id=book_id).first()
    if book and book.copies > 0:
        borrowed_at = datetime.now()
        due_at = borrowed_at + timedelta(days=7)
        log = Log(user_id=session['user_id'], book_id=book.id,
                  borrowed_at=borrowed_at, due_at=due_at)
        book.copies -= 1
        db.add(log)
        db.commit()
        flash("Book borrowed successfully!", "success")
    else:
        flash("Book unavailable.", "danger")
    return redirect(url_for('dashboard'))


@app.route('/return/<int:log_id>')
@login_required
def return_book(log_id):
    db = get_db()
    log = db.query(Log).filter_by(id=log_id, user_id=session['user_id']).first()
    if log and not log.returned_at:
        now = datetime.now()
        log.returned_at = now
        delay = now - log.due_at
        if delay.total_seconds() > 60:  # fine starts after 1 minute late
            minutes_late = int((delay.total_seconds() - 60) // 60) + 1
            log.fine = minutes_late * 1.0  # 1 EGP per minute after 1 min
        db.query(Book).filter_by(id=log.book_id).update({Book.copies: Book.copies + 1})
        db.commit()
        flash("Book returned.", "success")
    return redirect(url_for('dashboard'))


@app.route('/my_fines')
@login_required
def my_fines():
    db = get_db()
    logs = db.query(Log).filter_by(user_id=session['user_id']).all()
    return render_template("my_fines.html", logs=logs)


@app.route('/pay_fine/<int:log_id>', methods=['GET'])
@login_required
def pay_fine(log_id):
    db = get_db()
    log = db.query(Log).filter_by(id=log_id, user_id=session['user_id']).first()
    return render_template("pay_fine.html", log=log)


@app.route('/confirm_payment/<int:log_id>', methods=['POST'])
@login_required
def confirm_payment(log_id):
    db = get_db()
    log = db.query(Log).filter_by(id=log_id, user_id=session['user_id']).first()
    if log and log.fine > 0 and not log.fine_paid:
        log.fine_paid = 1
        db.commit()
        flash("Fine paid successfully!", "success")
    return redirect(url_for('my_fines'))


@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
