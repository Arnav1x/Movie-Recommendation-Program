



def ask_user_preferences():
    "Asks users their preferences and stores them in varibles"
    Preferences = {}

    #Currently stores all user preferences into a dictionary. For the time being, they will remain strings, types may be adjusted later. 
    Preferences["genres"] = input("What genres are you looking for:") #may be changed to a list using .lower().split(',')
    Preferences["date_range"] = input("What is your prefered release date range?") #may be changed to a tuple
    Preferences["actors"] = input("Do you have any prefered actors or actresses?") #may be changed to a list using .lower().split(',')

    return Preferences

def display_user_preferences(Preferences):
    "Unit test to verify that the user's preferences were correctly stored"

    print(f'Genres: {Preferences["genres"]}')
    print(f'Date Range: {Preferences["date_range"]}')
    print(f'Actors/Actresses: {Preferences["actors"]}')

display_user_preferences(ask_user_preferences())