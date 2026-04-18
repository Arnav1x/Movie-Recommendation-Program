



def ask_user_preferences():
    "Asks users their preferences and stores them in varibles"
    Preferences = {}

    #Currently stores all user preferences into a dictionary. For the time being, they will remain strings. Genres may be changed to be a list, date_range a tuple, and actors a string. 
    Preferences["genres"] = input("What genres are you looking for:")
    Preferences["date_range"] = input("What is your prefered release date range?")
    Preferences["actors"] = input("Do you have any prefered actors or actresses?")

    return Preferences

def display_user_preferences(Preferences):
    "Unit test to verify that the user's preferences were correctly stored and are the corerct type"

    print(f'Genres: {Preferences["genres"]}')
    print(f'Date Range: {Preferences["date_range"]}')
    print(f'Actors/Actresses: {Preferences["actors"]}')

display_user_preferences(ask_user_preferences())