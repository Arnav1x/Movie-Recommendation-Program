



def ask_user_preferences():
    "Asks users their preferences and stores them in varibles"
    Preferences = {}

    Preferences[genres] = input("What genres are you looking for:")
    Preferences[date_range] = input("What is your prefered release date range?")
    prefereed_actors = input("Do you have any prefered actors or actresses?")


    return prefered_genre, prefereed_date_range, prefereed_actors

def display_user_preferences(prefered_genre, prefereed_date_range, prefereed_actors):
    "Unit test to verify that the user's preferences were correctly stored and are the corerct type"
    
    print(f'Genres: {prefered_genre}')
    print(f'Date Range: {prefereed_date_range}')
    print(f'Actors/Actresses: {prefereed_actors}')

display_user_preferences(*ask_user_preferences())