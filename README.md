# Movie-Recommendation-Program
This is a program that asks the user a series of questions in order to recomend them the right movie. 

Main.py — User interface side of the project. Run this in order to start the program. Apon starting, it will give the user a rundown on the nature of
the program and then proceed with a series of questions in order to gauge the user's intrest. Only limited to user interaction, user inputs and pritns mostly. Face of the project. 

recommender.py — This is the file that does the actual thinking and logic of the project. It uses the MovieRecommender class which is the bulk of sorting. Main.py calls this, reccomender.py does the calculations, and feeds it back so it can be displayed. This is the brains of the project. 

test_recommender.py — Simple unittest file, not much to note here. 

## How it works
The app asks up to seven questions in order of importance

1. **Genres** (e.g. Action, Comedy)
2. **Keywords / themes** (searched across the `theme` *and* `description` columns)
3. **Directors**
4. **Actors**
5. **Minimum rating** (0-5)
6. **Preferred runtime** (minutes)
7. **Release year range** (e.g. `2010-2026`)

## Additonal available features
1. **Ability to skip questions** — Press enter in order to skip a question, ranking is adjusted accordinly.  
2. **Deal breaker** — Users can note if a question is a deal breaker or not. For example if a users stricly only wants Nolan movies, they will respond Yes to the quesiton being a deal breaker. If it's just a slight preference, they can respond no.  
3. **Ranking System** - At the end users receive up to 5 movies ranked by a percentage score that represents how close the movie correlates with their interest. 
4. **Hierarchy of importance** - For a better user experience, some questions are weighted heavier than others. For example genres have more weight than runtime. 
Weightage Hierarchy:
| Genres | 32 |
| Themes / keywords | 23 |
| Directors | 15 |
| Actors | 12 |
| Min rating | 6 |
| Runtime | 6 |
| Year range | 6 |
