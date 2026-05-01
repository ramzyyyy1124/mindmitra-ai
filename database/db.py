import sqlite3

def init_db():
    conn = sqlite3.connect("mindmitra.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS child_profile (
        username TEXT,
        name TEXT,
        age INTEGER,
        grade TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        mood TEXT,
        sleep INTEGER,
        screen INTEGER,
        activity TEXT,
        stress TEXT
    )
    """)

    conn.commit()
    conn.close()


def insert_user(username, password):
    conn = sqlite3.connect("mindmitra.db")
    c = conn.cursor()
    c.execute("INSERT INTO users VALUES (?,?)", (username, password))
    conn.commit()
    conn.close()


def check_user(username, password):
    conn = sqlite3.connect("mindmitra.db")
    c = conn.cursor()
    c.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )
    result = c.fetchone()
    conn.close()
    return result


def save_profile(username, name, age, grade):
    conn = sqlite3.connect("mindmitra.db")
    c = conn.cursor()

    c.execute("DELETE FROM child_profile WHERE username=?", (username,))
    c.execute(
        "INSERT INTO child_profile VALUES (?,?,?,?)",
        (username, name, age, grade)
    )

    conn.commit()
    conn.close()


def load_profile(username):
    conn = sqlite3.connect("mindmitra.db")
    c = conn.cursor()

    c.execute(
        "SELECT name, age, grade FROM child_profile WHERE username=?",
        (username,)
    )

    data = c.fetchone()
    conn.close()
    return data


def insert_log(mood, sleep, screen, activity, stress):
    conn = sqlite3.connect("mindmitra.db")
    c = conn.cursor()

    c.execute(
        "INSERT INTO logs VALUES (?,?,?,?,?)",
        (mood, sleep, screen, activity, stress)
    )

    conn.commit()
    conn.close()