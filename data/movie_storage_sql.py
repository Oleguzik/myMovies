
from sqlalchemy import create_engine, text

# --- DATABASE SETUP ---
DB_URL = "sqlite:///data/movies.db"
engine = create_engine(DB_URL, echo=True)

# --- USER MANAGEMENT ---
def create_user(username):
    """Create a new user in the database."""
    with engine.connect() as connection:
        try:
            connection.execute(text("INSERT INTO users (username) VALUES (:username)"), {"username": username})
            connection.commit()
            print(f"User '{username}' created successfully.")
        except Exception as e:
            print(f"Error creating user: {e}")

def list_users():
    """List all users in the database."""
    with engine.connect() as connection:
        result = connection.execute(text("SELECT id, username FROM users"))
        return result.fetchall()

def get_user_by_id(user_id):
    """Retrieve a user by their ID."""
    with engine.connect() as connection:
        result = connection.execute(text("SELECT id, username FROM users WHERE id = :id"), {"id": user_id})
        return result.fetchone()

def get_user_by_name(username):
    """Retrieve a user by their username."""
    with engine.connect() as connection:
        result = connection.execute(text("SELECT id, username FROM users WHERE username = :username"), {"username": username})
        return result.fetchone()

def list_movies(user_id):
    """Retrieve all movies for a specific user from the database."""
    with engine.connect() as connection:
        result = connection.execute(text("SELECT title, year, rating, image_url FROM movies WHERE user_id = :user_id"), {"user_id": user_id})
        movies = result.fetchall()
    return {row[0]: {"year": row[1], "rating": row[2], "image_url": row[3]} for row in movies}

def add_movie(title, year, rating, image_url, user_id):
    """Add a new movie to the database, including the poster URL, for a specific user."""
    if image_url == "N/A":
        image_url = None  # Use NULL for missing URLs
    with engine.connect() as connection:
        try:
            connection.execute(text("INSERT INTO movies (title, year, rating, image_url, user_id) VALUES (:title, :year, :rating, :image_url, :user_id)"), 
                               {"title": title, "year": year, "rating": rating, "image_url": image_url, "user_id": user_id})
            connection.commit()
            print(f"Movie '{title}' added successfully.")
        except Exception as e:
            print(f"Error: {e}")

def delete_movie(title, user_id):
    """Delete a movie for a specific user from the database."""
    with engine.connect() as connection:
        result = connection.execute(text("DELETE FROM movies WHERE title = :title AND user_id = :user_id"), {"title": title, "user_id": user_id})
        connection.commit()
        if result.rowcount:
            print(f"Movie '{title}' deleted successfully.")
        else:
            print(f"Movie '{title}' not found.")

def update_movie(title, rating, user_id):
    """Update the rating of an existing movie for a specific user in the database."""
    with engine.connect() as connection:
        result = connection.execute(text("UPDATE movies SET rating = :rating WHERE title = :title AND user_id = :user_id"), 
                                   {"rating": rating, "title": title, "user_id": user_id})
        connection.commit()
        if result.rowcount:
            print(f"Movie '{title}' updated successfully.")
        else:
            print(f"Movie '{title}' not found.")



# Create the users and movies tables if they do not exist
with engine.connect() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL
        )
    """))
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL,
            image_url TEXT,
            user_id INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """))
    connection.commit()


