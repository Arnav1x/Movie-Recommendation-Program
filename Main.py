"""
This is the User facing side of the project.
Run this to start the project in entirety.
Calls apon recomender, which does the actual thinking.
What this file does is handle all the inputs and prints for the user, while also handing of the files.
"""

import csv

from recommender import MovieRecommender

DATASET_PATH = "Datasets/MovieDataset.csv"
TOP_N = 5


def load_movies(path=DATASET_PATH):
    """Loads the movie dataset from a CSV file into a list of dicts.

    Args:
        path (str): path to the CSV file. Defaults to DATASET_PATH. The
            file must have a header row with these collumns, in this particuar order:
            id, name, date, minute, rating, genre, theme, description,
            actors, director.

    Returns:
        list of dict: one dict per movie, keyed by CSV column name. All
        values are strings 
    """
    movies = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            movies.append(row)
    return movies


def parse_list(raw):
    """This function splits a comma-separated user input into a clean list of items

    Args:
        raw (str): the raw input string from the user.

    Returns:
        list of str: the items with surrounding whitespace stripped and
        empty entries dropped. Returns an empty list if `raw` is empty
        or None.
    """
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def parse_year_range(raw):
    """This function parses a year-range input into a tuple of ints in the format (start, end) 
    Very flexible, accepts a single year or range. ex. 2016- reads as 2016-onwrds. 2016-2020 reads as a range. 

    Args:
        raw (str): the raw input from the user.

    Returns:
        tuple of (int or None, int or None): the inclusive start and
        end years. (None, None) is returned for blank or unparseable
        input and signals "no year filter".
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


def parse_float(raw):
    """Parses a user input string into a float.

    Args:
        raw (str): the raw input from the user.

    Returns:
        float or None: the parsed value, or None if `raw` is blank or
        cannot be interpreted as a float.
    """
    if not raw or not raw.strip():
        return None
    try:
        return float(raw.strip())
    except ValueError:
        return None


def parse_int(raw):
    """Parses a user input string into an int.

    Args:
        raw (str): the raw input from the user.

    Returns:
        int or None: the parsed value, or None if `raw` is blank or
        cannot be interpreted as an int.
    """
    if not raw or not raw.strip():
        return None
    try:
        return int(raw.strip())
    except ValueError:
        return None


def ask_deal_breaker(label):
    """Asks the user whether a preference should be a deal breaker.

    If it's a deal-breaker, it makes the preference excludes ALL movies that does not match
    If its not a a non-deal-breaker, the preference only influences the score and ranking

    Args:
        label (str): a short, human-readable name for the preference
            (e.g. "genres") that will be shown to the user in the
            prompt.

    Returns:
        bool: True if the user answered "y" or "yes" (case-insensitive),
        False otherwise. Defaults to False on a blank answer.

    Side effects:
        Prints a prompt to the console and reads one line from stdin.
    """
    response = input(f"   -> Make '{label}' a deal breaker? (y/N): ").strip().lower()
    return response in ("y", "yes")


def ask_user_preferences():
    """Asks the user for all movie-preference inputs and returns them.

    Questions are presented in this order:
        1. genres
        2. keywords / themes
        3. directors
        4. actors
        5. minimum rating (0-5)
        6. preferred runtime in minutes
        7. release year range
    Any question can be skipped with a blank line. After each non-empty
    answer the user is asked whether that answer is a deal breaker.

    Returns:
        dict: a preferences dict meant for MovieRecommender.rank()

    Side effects:
        Prints to console 
    """
    print("=" * 60)
    print("           Welcome to the Movie Recommender!")
    print("=" * 60)
    print("Answer each question to get a ranked list of movies.")
    print("Press Enter to skip any question.")
    print("After each non-empty answer you'll be asked if it's a 'deal breaker':")
    print("  - Deal breaker = movies that don't match are excluded entirely.")
    print("  - Otherwise   = it just affects the score and ranking.\n")

    # Most important questions in terms hierarchy; genres and themes(through keywords)
    genres_raw = input("1) What genres are you interested in?\n   (e.g. Action, Comedy, Drama): ")
    genres = parse_list(genres_raw)
    genres_db = ask_deal_breaker("genres") if genres else False

    themes_raw = input("\n2) Any keywords, themes, or plot elements?\n   (e.g. family drama, time travel, heist): ")
    themes = parse_list(themes_raw)
    themes_db = ask_deal_breaker("keywords/themes") if themes else False

    # Pretty big gap in terms of weightage 
    print("\n" + "-" * 60 + "\n")

    directors_raw = input("3) Any preferred directors?\n   (e.g. Christopher Nolan, Greta Gerwig): ")
    directors = parse_list(directors_raw)
    directors_db = ask_deal_breaker("directors") if directors else False

    actors_raw = input("\n4) Any preferred actors or actresses?\n   (e.g. Margot Robbie, Tom Hanks): ")
    actors = parse_list(actors_raw)
    actors_db = ask_deal_breaker("actors") if actors else False

    rating_raw = input("\n5) Minimum rating? (0-5, e.g. 4.5): ")
    min_rating = parse_float(rating_raw)
    rating_db = ask_deal_breaker("minimum rating") if min_rating is not None else False

    runtime_raw = input("\n6) Preferred runtime in minutes? (e.g. 120): ")
    runtime = parse_int(runtime_raw)
    runtime_db = ask_deal_breaker("runtime") if runtime is not None else False

    year_raw = input("\n7) What release year range? (e.g. 2010-2026): ")
    year_range = parse_year_range(year_raw)
    year_db = ask_deal_breaker("year range") if year_range != (None, None) else False

    return {
        "genres":     {"values": genres,    "deal_breaker": genres_db},
        "themes":     {"values": themes,    "deal_breaker": themes_db},
        "directors":  {"values": directors, "deal_breaker": directors_db},
        "actors":     {"values": actors,    "deal_breaker": actors_db},
        "min_rating": {"value":  min_rating, "deal_breaker": rating_db},
        "runtime":    {"value":  runtime,    "deal_breaker": runtime_db},
        "year_range": {"value":  year_range, "deal_breaker": year_db},
    }


def display_recommendations(ranked):
    """
    Prints the ranked recommendations.
    Format:
        #1  95% Match: Interstellar (2014)
              Director: Christopher Nolan
              Genre: Sci-Fi|Adventure
              Runtime: 169 min  |  Rating: 4.36 / 5
    """
    print("\n" + "=" * 60)
    print("                  Your Recommendations")
    print("=" * 60)

    if not ranked:
        print("No movies matched your preferences.")
        print("Try removing some deal breakers or loosening your criteria.")
        return

    for rank, (score, movie) in enumerate(ranked, start=1):
        print(f"#{rank}  {score:.0f}% Match: {movie.get('name', '?')} ({movie.get('date', '?')})")
        print(f"      Director: {movie.get('director', 'N/A')}")
        print(f"      Genre: {movie.get('genre', 'N/A')}")
        print(f"      Runtime: {movie.get('minute', 'N/A')} min  |  Rating: {movie.get('rating', 'N/A')} / 5")
        print()


if __name__ == "__main__":
    movies = load_movies()
    preferences = ask_user_preferences()
    recommender = MovieRecommender(movies)
    ranked = recommender.rank(preferences, top_n=TOP_N)
    display_recommendations(ranked)