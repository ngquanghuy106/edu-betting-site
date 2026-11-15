import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from pathlib import Path
from typing import TypedDict
import re


BASE_DIR = Path(__file__).parent

RESERVED_USERNAMES = [
    "owner",
	"admin",
	"moderator"
]


def validate_username(username: str) -> tuple[bool, str]:

	if len(username) < 5:
		return False, "Username must contain at least 5 characters"

	if len(username) > 50:
		return False, "Username cannot exceed 50 characters"

	if not re.fullmatch(r"[a-zA-Z0-9_]+", username):
		return False, "Only letters, numbers, and underscores are allowed"

	return True, "Username accepted"

def validate_password(password: str) -> tuple[bool, str]:

	if len(password) < 8:
		return False, "Password must contain at least 8 characters"

	if len(password) > 128:
		return False, "Password cannot exceed 128 characters"

	if not re.search(r"[a-z]", password):
		return False, "Password must contain a lowercase letter"

	if not re.search(r"[A-Z]", password):
		return False, "Password must contain an uppercase letter"

	if not re.search(r"\d", password):
		return False, "Password must contain a number"

	if not re.search(r"[^a-zA-Z0-9\s]", password):
		return False, "Password must contain a special character"

	return True, "Password accepted"


class UserData(TypedDict):
	id: int
	username: str
	balance: int


class Data:

    def __init__(self, db_path = BASE_DIR / "database" / "users.db"):
        self.db_path = db_path
        self.initialize_database()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def initialize_database(self):

        with self.connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    balance INTEGER NOT NULL DEFAULT 0
                )
            """)

    # REGISTER ==========================

    def register(self, username, password):

        if not username or not password:
            return False, "Missing credentials"

        valid, message = validate_username(username)

        if not valid:
            return False, message

        valid, message = validate_password(password)

        if not valid:
            return False, message

        username_lower = username.lower()

        if any(word in username_lower for word in RESERVED_USERNAMES):
            return False, "This username contains a reserved keyword"

        password_hash = generate_password_hash(password)

        try:
            with self.connect() as conn:
                conn.execute(
                    """
                    INSERT INTO users (username, password_hash)
                    VALUES (?, ?)
                    """,
                    (username, password_hash)
                )

            return True, "Registration successful"

        except sqlite3.IntegrityError:
            return False, "Username already exists"

    # LOGIN =============================

    def login(self, username: str, password: str) -> tuple[bool, UserData | str]:

        with self.connect() as conn:
            user = conn.execute(
                """
                SELECT id, username, password_hash, balance
                FROM users
                WHERE username = ?
                """,
                (username,)
            ).fetchone()

        if user is None:
            return False, "Invalid credentials"

        if not check_password_hash(user[2], password):
            return False, "Invalid credentials"

        return True, {
            "id": user[0],
            "username": user[1],
            "balance": user[3]
        }
