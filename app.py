import statistics
import data.movie_storage_sql as storage
import requests
import os
import re
from fuzzywuzzy import process
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get("OMDB_API_KEY")
OMDB_API_URL = "https://www.omdbapi.com/"

def select_user():
    """"
     Allows user to select an existing user or create a new one.
     Returns the selected user's ID and username.
    """
    while True:
        users = storage.list_users()
        print("\nSelect a user:")
        for idx, user in enumerate(users, 1):
            print(f"{idx}. {user[1]}")
        print(f"{len(users)+1}. Create new user")
        try:
            choice = int(input("Enter choice: "))
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue
        if 1 <= choice <= len(users):
            user_id, username = users[choice-1]
            print(f"\nWelcome, {username}!")
            return user_id, username
        elif choice == len(users)+1:
            new_name = input("Enter new username: ").strip()
            if not new_name:
                print("Username cannot be empty.")
                continue
            if storage.get_user_by_name(new_name):
                print("That username already exists.")
                continue
            storage.create_user(new_name)
            user = storage.get_user_by_name(new_name)
            print(f"\nWelcome, {new_name}! 🎬")
            return user[0], user[1]
        else:
            print("Invalid choice. Try again.")



def command_list_movies(user_id):
    """List all movies for the given user."""
    movies = storage.list_movies(user_id)
    print(f"{len(movies)} movies in total")
    for movie, data in movies.items():
        print(f"{movie} ({data['year']}): {data['rating']}")


def filter_movies(user_id):
    """
    Filters movies based on user input for minimum rating, start year, and end year.
    Blank input means no filter for that criterion.
    """
    movies = storage.list_movies(user_id)
    if not movies:
        print("No movies found.")
        return

    # Get filter criteria from user
    min_rating_input = input("Enter minimum rating (leave blank for no minimum rating): ").strip()
    start_year_input = input("Enter start year (leave blank for no start year): ").strip()
    end_year_input = input("Enter end year (leave blank for no end year): ").strip()

    # Convert inputs to appropriate types or None
    min_rating = float(min_rating_input) if min_rating_input else None
    start_year = int(start_year_input) if start_year_input else None
    end_year = int(end_year_input) if end_year_input else None

    # Filter movies
    filtered = []
    for title, info in movies.items():
        rating = info.get('rating', 0)
        year = info.get('year', 0)
        if min_rating is not None and rating < min_rating:
            continue
        if start_year is not None and year < start_year:
            continue
        if end_year is not None and year > end_year:
            continue
        filtered.append((title, year, rating))

    # Display results
    if filtered:
        print("Filtered Movies:")
        for title, year, rating in filtered:
            print(f"{title} ({year}): {rating}")
    else:
        print("No movies match the given criteria.")

def show_stats(user_id):
    """Displays statistics about the movies."""
    movies = storage.list_movies(user_id)
    if not movies:
        print("No movies found.")
        return
    ratings = [info.get('rating', 0) for info in movies.values()]
    if not ratings:
        print("No ratings found.")
        return
    average = sum(ratings) / len(ratings)
    median = statistics.median(ratings)
    best_title, best_info = max(movies.items(), key=lambda item: item[1].get('rating', 0))
    worst_title, worst_info = min(movies.items(), key=lambda item: item[1].get('rating', 0))
    print(f"{'-'*20}")
    print(f"Average rating: {average:.1f}")
    print(f"Median rating: {median:.1f}")
    print(f"Best movie: {best_title}, {best_info.get('rating', 0):.1f}")
    print(f"Worst movie: {worst_title}, {worst_info.get('rating', 0):.1f}")

def list_movies(user_id):
    """List all movies for the given user"""
    movies = storage.list_movies(user_id)
    if not movies:
        print("No movies found.")
        return
    for title, info in movies.items():
        print(f"{title}: Year {info.get('year')}, Rating {info.get('rating')}")

def list_movies_by_year(user_id):
    """List all movies for the given user by year."""
    movies = storage.list_movies(user_id)
    if not movies:
        print("No movies found.")
        return
    while True:
        order = input("Show latest movies first? (y/n): ").strip().lower()
        if order in ('y', 'n'):
            break
        print("Please enter 'y' or 'n'.")
    reverse = True if order == 'y' else False
    sorted_movies = sorted(movies.items(), key=lambda item: item[1].get('year', 0), reverse=reverse)
    for title, info in sorted_movies:
        print(f"{title}: Year {info.get('year')}, Rating {info.get('rating')}")

def add_movie(user_id):
    """Add a movie for the given user by fetching details from OMDb API."""
    title = input("Enter movie title: ").strip()
    if not title:
        print("Movie title cannot be empty. Please try again.")
        return

    # Fuzzy matching: suggest similar titles if the movie already exists or is similar
    movies = storage.list_movies(user_id)
    existing_titles = list(movies.keys())
    if existing_titles:
        best_match, score = process.extractOne(title, existing_titles)
        if score > 80:
            print(f"A similar movie already exists: '{best_match}' (similarity: {score}%)")
            confirm = input("Do you still want to add this movie? (y/n): ").strip().lower()
            if confirm != 'y':
                print("Movie not added.")
                return

    # Fetch movie details from OMDb API
    api_url = f"{OMDB_API_URL}?apikey={API_KEY}&t={title}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        movie_data = response.json()

        # Check if the movie was found
        if movie_data.get("Response") == "False":
            print(f"Movie '{title}' not found in OMDb database.")
            return

        # Extract relevant details
        movie_title = movie_data.get("Title", "Unknown")
        year_str = str(movie_data.get("Year", 0))
        match = re.search(r'\d{4}', year_str)
        if match:
            year = int(match.group())
        else:
            year = 0
        rating = float(movie_data.get("imdbRating", 0))
        poster_url = movie_data.get("Poster", "N/A")

        # Save movie details to the database
        storage.add_movie(movie_title, year, rating, poster_url, user_id)
        print(f"Movie '{movie_title}' added successfully!")

    except requests.exceptions.RequestException as e:
        print("Failed to connect to OMDb API. Please check your internet connection.")
        print(f"Error details: {e}")

def delete_movie(user_id):
    """Delete a movie for the given user."""
    movies = storage.list_movies(user_id)
    while True:
        title = input("Enter movie name to delete: ").strip()
        if not title:
            print("Movie title cannot be empty. Please try again.")
            continue
        if title not in movies:
            print(f"Movie {title} not found!")
            return
        break
    storage.delete_movie(title, user_id)
    print(f"Movie {title} deleted.")

def update_movie(user_id):
    """Update a movie for the given user."""
    movies = storage.list_movies(user_id)
    while True:
        title = input("Enter movie name to update: ").strip()
        if not title:
            print("Movie title cannot be empty. Please try again.")
            continue
        if title not in movies:
            print(f"Movie {title} not found!")
            return
        break
    while True:
        try:
            rating = int(input("Enter new rating: "))
            break
        except ValueError:
            print("Invalid rating. Please enter a valid number.")
    storage.update_movie(title, rating, user_id)
    print(f"Movie {title} updated.")

def generate_website(user_id, username):
    """Generate a static HTML website for the user's movie collection."""
    template_path = os.path.join("static", "index_template.html")
    with open(template_path, "r") as template_file:
        template_content = template_file.read()

    title = f"🎬 {username}'s Movies App"
    movies = storage.list_movies(user_id)
    movie_grid = ""
    if not movies:
        movie_grid = "<li>No movies available</li>"
    else:
        for movie, data in movies.items():
            image_url = data.get('image_url')
            if image_url and image_url != 'N/A':
                img_tag = f"<img class='movie-poster' src='{image_url}' alt='Poster'>"
            else:
                img_tag = "<div class='movie-poster poster-na'><span style='color:#ccc;'>No Image</span></div>"
            movie_grid += f"""
            <li class='movie'>
                {img_tag}
                <div class='movie-title'>{movie}</div>
                <div class='movie-year'>{data['year']}</div>
            </li>
            """
    html_content = template_content.replace("__TEMPLATE_TITLE__", title).replace("__TEMPLATE_MOVIE_GRID__", movie_grid)

    output_path = f"{username}.html"
    with open(output_path, "w") as output_file:
        output_file.write(html_content)

    print(f"Website was generated successfully as {output_path}.")

def main():
    user_id, username = select_user()
    while True:
        print(f"\n{username}'s Movie Database Menu:")
        print("1. List movies")
        print("2. Add movie")
        print("3. Delete movie")
        print("4. Update movie rating")
        print("5. List movies by year")
        print("6. Filter movies")
        print("7. Show statistics")
        print("8. Generate website")
        print("9. Switch user")
        print("0. Exit")
        choice = input("Choose an option: ")
        if choice == '1':
            list_movies(user_id)
        elif choice == '2':
            add_movie(user_id)
        elif choice == '3':
            delete_movie(user_id)
        elif choice == '4':
            update_movie(user_id)
        elif choice == '5':
            list_movies_by_year(user_id)
        elif choice == '6':
            filter_movies(user_id)
        elif choice == '7':
            show_stats(user_id)
        elif choice == '8':
            generate_website(user_id, username)
        elif choice == '9':
            user_id, username = select_user()
        elif choice == '0':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
