from sqlalchemy import create_engine, text

# SQLite database file (it will be created automatically)
DB_PATH = "users.db"

# Create the engine
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

def create_users_table():
    """Create the users table if it doesn't exist"""
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """))
        conn.commit()

def add_user(username, password):
    """Add a new user"""
    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO users (username, password) VALUES (:u, :p)"),
            {"u": username, "p": password}
        )
        conn.commit()

def get_user(username, password):
    """Verify if user exists"""
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM users WHERE username=:u AND password=:p"),
            {"u": username, "p": password}
        ).fetchone()
        return result
