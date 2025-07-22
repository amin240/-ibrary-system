from sqlalchemy import create_engine, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session

# قاعدة البيانات
engine = create_engine("sqlite:///library_curry.db", echo=True)

# الأساس لجميع الموديلات
class Base(DeclarativeBase):
    pass

# جدول المستخدمين
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True)
    phone: Mapped[str] = mapped_column(String)
    username: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    logs = relationship("Log", back_populates="user")


# جدول الكتب
class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    author: Mapped[str] = mapped_column(String)
    total_copies: Mapped[int] = mapped_column(Integer)
    available_copies: Mapped[int] = mapped_column(Integer)

    logs = relationship("Log", back_populates="book")


# جدول السجلات (الاستعارة والإرجاع والغرامات)
class Log(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    borrow_date: Mapped[str] = mapped_column(String)
    return_date: Mapped[str] = mapped_column(String, nullable=True)
    fine: Mapped[float] = mapped_column(Float, default=0.0)
    is_returned: Mapped[bool] = mapped_column(Boolean, default=False)
    fine_paid: Mapped[bool] = mapped_column(Boolean, default=False)

    user = relationship("User", back_populates="logs")
    book = relationship("Book", back_populates="logs")


# إنشاء الجداول
Base.metadata.create_all(engine)

# إدخال البيانات
with Session(engine) as session:
    # 🧑‍🤝‍🧑 إدخال المستخدمين
    users = [
        User( first_name="amin", last_name="ali", email="amin.ali@nagwa.com", phone="01119051101", username="aminali", password="123456", is_admin=False),
        User( first_name="Ali", last_name="Hassan", email="ali@example.com", phone="01012345678", username="aliuser", password="pass123", is_admin=False),
        User( first_name="Sara", last_name="Omar", email="sara@example.com", phone="01023456789", username="sarauser", password="pass123", is_admin=False),
        User( first_name="Ahmed", last_name="Mahmoud", email="ahmed@example.com", phone="01034567890", username="ahmeduser", password="pass123", is_admin=False),
        User( first_name="Mona", last_name="Youssef", email="mona@example.com", phone="01045678901", username="monauser", password="pass123", is_admin=False),
        User( first_name="Tarek", last_name="Adel", email="tarek@example.com", phone="01056789012", username="tarekuser", password="pass123", is_admin=False),
        User( first_name="Yasmine", last_name="Said", email="yasmine@example.com", phone="01067890123", username="yasmineuser", password="pass123", is_admin=False),
        User( first_name="Omar", last_name="Kamal", email="omar@example.com", phone="01078901234", username="omaruser", password="pass123", is_admin=False),
        User( first_name="Nour", last_name="Hani", email="nour@example.com", phone="01089012345", username="nouruser", password="pass123", is_admin=False),
        User( first_name="Hassan", last_name="Tamer", email="hassan@example.com", phone="01090123456", username="hassanuser", password="pass123", is_admin=False),
        User( first_name="bod", last_name="tito", email="bod@gimal.com", phone="0112987654", username="bod1", password="123456", is_admin=False),
        User( first_name="Admin", last_name="User", email="admin@example.com", phone="0000000000", username="admin", password="admin123", is_admin=True),
        User( first_name="amin", last_name="ali", email="amin@gmail.com", phone="011827382900", username="amin1", password="123456", is_admin=False),
    ]

    # 📚 إدخال الكتب
    books = [
        Book(title="The Alchemist", total_copies=1, available_copies=1, author="Paulo Coelho"),
        Book(title="1984", total_copies=1, available_copies=1, author="George Orwell"),
        Book(title="Book Title", total_copies=1, available_copies=1, author="ahmed"),
        Book(title="The Alchemist", total_copies=1, available_copies=1, author="Paulo Coelho"),
        Book(title="1984", total_copies=1, available_copies=1, author="George Orwell"),
        Book(title="Brave New World", total_copies=1, available_copies=1, author="Aldous Huxley"),
        Book(title="To Kill a Mockingbird", total_copies=1, available_copies=1, author="Harper Lee"),
        Book(title="The Catcher in the Rye", total_copies=0, available_copies=0, author="J.D. Salinger"),
        Book(title="Great Expectations", total_copies=1, available_copies=1, author="Charles Dickens"),
        Book(title="Moby Dick", total_copies=1, available_copies=1, author="Herman Melville"),
        Book(title="War and Peace", total_copies=1, available_copies=1, author="Leo Tolstoy"),
        Book(title="Crime and Punishment", total_copies=1, available_copies=1, author="Fyodor Dostoevsky"),
        Book(title="Pride and Prejudice", total_copies=1, available_copies=1, author="Jane Austen"),
        Book(title="track", total_copies=1, available_copies=1, author="mohamed"),
    ]

    # إضافة للسيشن
    session.add_all(users + books)
    session.commit()

print("✅ تم إنشاء الجداول وإدخال البيانات بنجاح.")
