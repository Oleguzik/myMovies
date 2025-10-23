from sqlalchemy import create_engine, text

# Define the database URL
DB_URL = "sqlite:///data/movies.db"

# Create the engine
engine = create_engine(DB_URL, echo=True)

def list_movies():
    """Retrieve all movies from the database."""
    with engine.connect() as connection:
        result = connection.execute(text("SELECT title, year, rating, image_url FROM movies"))
        movies = result.fetchall()

    return {row[0]: {"year": row[1], "rating": row[2], "image_url": row[3]} for row in movies}

def add_movie(title, year, rating, image_url):
    """Add a new movie to the database, including the poster URL."""
    if image_url == "N/A":
        image_url = None  # Use NULL for missing URLs
    with engine.connect() as connection:
        try:
            connection.execute(text("INSERT INTO movies (title, year, rating, image_url) VALUES (:title, :year, :rating, :image_url)"), 
                               {"title": title, "year": year, "rating": rating, "image_url": image_url})
            connection.commit()
            print(f"Movie '{title}' added successfully.")
        except Exception as e:
            print(f"Error: {e}")

def delete_movie(title):
    """Delete a movie from the database."""
    with engine.connect() as connection:
        result = connection.execute(text("DELETE FROM movies WHERE title = :title"), {"title": title})
        connection.commit()
        if result.rowcount:
            print(f"Movie '{title}' deleted successfully.")
        else:
            print(f"Movie '{title}' not found.")

def update_movie(title, rating):
    """Update the rating of an existing movie in the database."""
    with engine.connect() as connection:
        result = connection.execute(text("UPDATE movies SET rating = :rating WHERE title = :title"), 
                                   {"rating": rating, "title": title})
        connection.commit()
        if result.rowcount:
            print(f"Movie '{title}' updated successfully.")
        else:
            print(f"Movie '{title}' not found.")




# Create the movies table if it does not exist
with engine.connect() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL,
            image_url TEXT
        )
    """))
    connection.commit()


