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
    Asks users their preferences and stores them in varibles
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

    print("Total movies loaded:", len(movies))

    print("Keys in a movie entry:")
    print(list(movies[0].keys()))

    print("Random movie sample:")
    print(movies[random.randint(1,len(movies))])


if __name__ == "__main__":
    #display_unit_tests(ask_user_preferences())
    movies = load_movies()
    test_movies_list(movies)
