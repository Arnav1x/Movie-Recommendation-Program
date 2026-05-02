"""

This is the User facing side of the project. 
Run this to start the project in entirety. 
Calls apon recomender, which does the actual thinking.
What this file does is handle all the inputs and prints for the user, while also handing of the files. 

"""

import csv

from recommender import MovieRecommender

#Shortcut to make it easier to call the path repeatedly
DATASET_PATH = "Datasets/movies_dataset_enriched.csv"
TOP_N = 5

def load_movies(path=DATASET_PATH):
    """
    This reads the movie CSV and returns a list of dictionaruies, with per movie).
    The CSV is expected to have at least the columns:
        id, name, date, genre, rating, minute, actors, theme
    """
    movies = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            movies.append(row)
    return movies


def parse_list(raw):
    """
    This splits the comma separated input string from the user  into a clean looking list of items
    Also removes empty or random spaces around items which tends to cause errors

    """
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def parse_year_range(raw):
    """
    This parses a the year range the user game into a tuple of int formated as (start, end)
    Example of what it should look like: 
        "2010-2020"  -> (2010, 2020)
        "2015"       -> (2015, 2015)
        ""           -> (None, None) # handles blanks
        "abc"        -> (None, None) # anything that isn't a year or number 
    """
    if not raw or not raw.strip():
        return (None, None)
    text = raw.strip()
    if "-" in text:
        left, right = text.split("-", 1)
        try:
            start = int(left.strip()) if left.strip() else None
            end = int(right.strip()) if right.strip() else None
            return (start, end)
        except ValueError:
            return (None, None)
    try:
        year = int(text)
        return (year, year)
    except ValueError:
        return (None, None)

def ask_user_preferences():
    """
    This asks the user for movie preferences and returns a dict in
    the fomat MovieRecommender(found in recomender) wants.
    Made so that it could be left blank if the users wants
    """
    print("=" * 50)
    print("        Welcome to the Movie Recommender!")
    print("=" * 50)
    print("Answer the following questions to get a ranked list of movies.")
    print("Press Enter to skip any question.\n")

    genres_raw = input("What genres are you interested in?\n  (e.g. Action, Comedy, Drama): ")
    year_raw   = input("What release year range?\n  (e.g. 2010-2020): ")
    actors_raw = input("Any preferred actors or actresses?\n  (e.g. Margot Robbie, Tom Hanks): ")
    themes_raw = input("Any keywords or themes?\n  (e.g. family drama, dark thriller): ")

    return {
        "genres":     parse_list(genres_raw),
        "year_range": parse_year_range(year_raw),
        "actors":     parse_list(actors_raw),
        "themes":     parse_list(themes_raw),
    }


def display_recommendations(ranked):
    """
    This prints a list of (score, movie) tuples to the console in that format 
    ex. (Ideal)
        #1  95% Match: Interstellar (2014)
              Genre: Science Fiction|Adventure
              Rating: 4.36 / 5
    """
    print("\n" + "=" * 50)
    print("              Your Recommendations")
    print("=" * 50)

    if not ranked:
        print("No movies matched your preferences.")
        return

    for rank, (score, movie) in enumerate(ranked, start=1):
        print(f"#{rank}  {score:.0f}% Match: {movie['name']} ({movie['date']})")
        print(f"      Genre: {movie['genre']}")
        print(f"      Rating: {movie['rating']} / 5")
        print()


if __name__ == "__main__":
    movies = load_movies()
    preferences = ask_user_preferences()
    recommender = MovieRecommender(movies)
    ranked = recommender.rank(preferences, top_n=TOP_N)
    display_recommendations(ranked)
