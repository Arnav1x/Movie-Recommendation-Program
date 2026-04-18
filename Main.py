import csv
import random

def load_movies():
    """
    Loads movies from dataset and stores into list of dictionaries

    Returns: movies(list) 
    
    """
    movies = []

    with open("movies_dataset_simple.csv", "r", encoding="cp1252", errors="replace") as file:
        reader = csv.DictReader(file)

        for row in reader:
            movies.append(row)

    return movies

def ask_user_preferences():
    """
    Collects user preferences for movie recommendations and stores in a dictionary. 

    Returns: Preferences(dict) containing genres, date_range, and actors as keys. Values will be taken from user input. 
    """
    Preferences = {}

    #Currently stores all user preferences into a dictionary. For the time being, they will remain strings, types may be adjusted later. 
    Preferences["genres"] = input("What genres are you looking for:") #may be changed to a list using .lower().split(',')
    Preferences["date_range"] = input("What is your prefered release date range?") #may be changed to a tuple
    Preferences["actors"] = input("Do you have any prefered actors or actresses?") #may be changed to a list using .lower().split(',')

    return Preferences

def display_unit_tests(Preferences):
    """Unit test to verify that the user's preferences were correctly stored"""
    
    print(f'Genres: {Preferences["genres"]}')
    print(f'Date Range: {Preferences["date_range"]}')
    print(f'Actors/Actresses: {Preferences["actors"]}')

def test_movies_list(movies):
    """Unit test to verify that the csv was correctly read"""

    print("Total movies loaded:", len(movies) - 1)

    print("Keys in a movie entry:")
    print(list(movies[0].keys()))

    print("Random movie test:")
    print(movies[random.randint(1,len(movies))])


if __name__ == "__main__":
    # Run user preferences unit test 
    display_unit_tests(ask_user_preferences())
    # Load csv
    movies = load_movies()
    # Run moives csv unit test
    test_movies_list(movies)
