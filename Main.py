"""
This is the User facing side of the project.
Run this to start the project in entirety.
Calls apon recomender, which does the actual thinking.
What this file does is handle all the inputs and prints for the user, while also handing of the files.
"""

import csv

from recommender import MovieRecommender

# Shortcut to make it easier to call the path repeatedly
DATASET_PATH = "Datasets/MovieDataset.csv"
TOP_N = 5


def load_movies(path=DATASET_PATH):
    """
    Reads the movie CSV and returns a list of dicts (one per movie).
    Columns: id, name, date, minute, rating, genre, theme, description, actors, director
    """
    movies = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            movies.append(row)
    return movies


def parse_list(raw):
    """Splits a comma separated input into a clean list, dropping blanks."""
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def parse_year_range(raw):
    """
    Parses the user's year range into (start, end).
        "2010-2020" -> (2010, 2020)
        "2015"      -> (2015, 2015)
        ""          -> (None, None)
        "abcHello"  -> (None, None)
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
    """Parses a float; returns None for blanks or garbage."""
    if not raw or not raw.strip():
        return None
    try:
        return float(raw.strip())
    except ValueError:
        return None


def parse_int(raw):
    """Parses an int; returns None for blanks or garbage."""
    if not raw or not raw.strip():
        return None
    try:
        return int(raw.strip())
    except ValueError:
        return None


def ask_deal_breaker(label):
    """
    Asks whether a question should be a deal breaker (exclusionary) or
    just preferential. Defaults to no (preferential).
    """
    response = input(f"   -> Make '{label}' a deal breaker? (y/N): ").strip().lower()
    return response in ("y", "yes")


def ask_user_preferences():
    """
    Asks the user a series of movie-preference questions in the order:
        genres > themes/keywords > directors > actors > rating > runtime > year
    After each non-empty answer, the user can flag it as a deal breaker.
    Returns a preferences dict that MovieRecommender.rank() understands.
    """
    print("=" * 60)
    print("           Welcome to the Movie Recommender!")
    print("=" * 60)
    print("Answer each question to get a ranked list of movies.")
    print("Press Enter to skip any question.")
    print("After each non-empty answer you'll be asked if it's a 'deal breaker':")
    print("  - Deal breaker = movies that don't match are excluded entirely.")
    print("  - Otherwise   = it just affects the score and ranking.\n")

    # --- top of hierarchy: genres + themes ---
    genres_raw = input("1) What genres are you interested in?\n   (e.g. Action, Comedy, Drama): ")
    genres = parse_list(genres_raw)
    genres_db = ask_deal_breaker("genres") if genres else False

    themes_raw = input("\n2) Any keywords, themes, or plot elements?\n   (e.g. family drama, time travel, heist): ")
    themes = parse_list(themes_raw)
    themes_db = ask_deal_breaker("keywords/themes") if themes else False

    # --- decent gap before the secondary tier ---
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