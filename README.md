# Movie-Recommendation-Program
This is a program that asks the user a series of questions in order to recomend them the right movie. 
There are three csvs, detailed has up to 5000 movies and far more keys like themes and descriptions, simple has only 100 movies and limited keys. We are currently using the enriched one, but that may be subject to change. 

In check-in 1, the entire program was in one file. As we went on, the project became far too long and convoluted so we decided it would best to split the project into seperate parts. One part is only dedicated to the only the user interaction, another part is dedicated to do all the logic and filtering, and then another is only for the testing. Keeping the files seperate made it easier to manage.

Main.py — This is the file that you're supposed to run in order for everything to word. It'll ask the user four questions, and then display the final list of movie recomendations. It doesn't do any of the filtering, it's just the user interface per se. 

recommender.py — This is the file that does the actual thinking and work of the project. It uses the MovieRecommender class which is the bulk of the project. Main.py calls this, reccomender.py does the calculations, and feeds it back so it can be displayed.

recommender.py — This is the file that does the actual thinking and work of the project. It uses the MovieRecommender class which is the bulk of the project. Main.py calls this, reccomender.py does the calculations, and feeds it back so it can be displayed.

test_recommender.py — We also split the tests into a new file. This runs around 20 small tests and the scoring and filtering to make sure everything is going on well. 

