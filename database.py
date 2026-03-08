import sqlite3
from encryption import encrypt_password, decrypt_password

conn = sqlite3.connect("passwords.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY,
username TEXT UNIQUE,
password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS passwords(
id INTEGER PRIMARY KEY,
username TEXT,
password TEXT
)
""")

conn.commit()


def create_user(username,password):

    cursor.execute(
        "INSERT INTO users(username,password) VALUES(?,?)",
        (username,password)
    )
    conn.commit()


def validate_user(username,password):

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username,password)
    )

    return cursor.fetchone()


def save_password(username,password):

    encrypted = encrypt_password(password)

    cursor.execute(
        "INSERT INTO passwords(username,password) VALUES(?,?)",
        (username,encrypted)
    )

    conn.commit()


def get_passwords(username):

    cursor.execute(
        "SELECT id,password FROM passwords WHERE username=?",
        (username,)
    )

    rows = cursor.fetchall()

    return [(row[0], decrypt_password(row[1])) for row in rows]


def delete_password(password_id):

    cursor.execute(
        "DELETE FROM passwords WHERE id=?",
        (password_id,)
    )

    conn.commit()
def create_user(username,password):

    import sqlite3

    try:

        cursor.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username,password)
        )

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False