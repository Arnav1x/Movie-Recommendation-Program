import unittest
from recommender import MovieRecommender
from Main import parse_list, parse_year_range

#Example to test from
SAMPLE_MOVIES = [
    {
        "id": "1", "name": "Action Hero", "date": "2015",
        "genre": "Action|Thriller", "rating": "4.0",
        "actors": "Tom Cruise|Emily Blunt",
        "theme": "high-octane action",
    },
    {
        "id": "2", "name": "Romance Tale", "date": "2005",
        "genre": "Romance|Drama", "rating": "3.5",
        "actors": "Margot Robbie",
        "theme": "moving relationship stories",
    },
    {
        "id": "3", "name": "Sci-Fi Epic", "date": "2020",
        "genre": "Science Fiction|Adventure", "rating": "4.8",
        "actors": "Tom Cruise",
        "theme": "spectacular sci-fi epic",
    },
]

"""
The tests below are mostly just checking that the filtering works good. 
We still need to make more tests regarding how the ranking system works well.
Since Main.Py only interacts with the user, and raises ValueErrors immediatley, we haven't done any main tests, only recomender so far.  
We felt that most of the errors would be found within the logic part of the program, so focused on testing this first. 
"""

class TestFilterByGenres(unittest.TestCase):
    """`filter_by_genres` should match any-of (OR), case-insensitive."""

    def setUp(self):
        self.r = MovieRecommender(SAMPLE_MOVIES)

    def test_single_genre_matches_one_movie(self):
        result = self.r.filter_by_genres(SAMPLE_MOVIES, ["Action"])
        self.assertEqual([m["name"] for m in result], ["Action Hero"])

    #made a bunch of random caps to check if cases worked fine
    def test_match_is_case_insensitive(self):
        result = self.r.filter_by_genres(SAMPLE_MOVIES, ["aCtIoN"])
        self.assertEqual(len(result), 1)

    def test_or_semantics_across_genres(self):
        # Hopefully any movie with Romance OR Action should match (2 movies).
        result = self.r.filter_by_genres(SAMPLE_MOVIES, ["Romance", "Action"])
        self.assertEqual(len(result), 2)

    def test_empty_list_returns_all(self):
        self.assertEqual(len(self.r.filter_by_genres(SAMPLE_MOVIES, [])), 3)

    def test_unknown_genre_returns_empty(self):
        self.assertEqual(self.r.filter_by_genres(SAMPLE_MOVIES, ["Western"]), [])

    def test_does_not_mutate_input(self):
        original = list(SAMPLE_MOVIES)
        self.r.filter_by_genres(SAMPLE_MOVIES, ["Action"])
        self.assertEqual(SAMPLE_MOVIES, original)


class TestFilterByYearRange(unittest.TestCase):
    """`filter_by_year_range` shoukd be  inclusive on both ends sides, either bound may/can be None."""

    def setUp(self):
        self.r = MovieRecommender(SAMPLE_MOVIES)

    def test_inclusive_range(self):
        result = self.r.filter_by_year_range(SAMPLE_MOVIES, 2010, 2020)
        names = sorted(m["name"] for m in result)
        self.assertEqual(names, ["Action Hero", "Sci-Fi Epic"])

    def test_open_upper_bound(self):
        result = self.r.filter_by_year_range(SAMPLE_MOVIES, 2010, None)
        self.assertEqual(len(result), 2)

    def test_open_lower_bound(self):
        result = self.r.filter_by_year_range(SAMPLE_MOVIES, None, 2010)
        self.assertEqual([m["name"] for m in result], ["Romance Tale"])

    def test_both_bounds_none_returns_all(self):
        self.assertEqual(len(self.r.filter_by_year_range(SAMPLE_MOVIES, None, None)), 3)

    def test_exact_boundary_year_is_included(self):
        result = self.r.filter_by_year_range(SAMPLE_MOVIES, 2015, 2015)
        self.assertEqual([m["name"] for m in result], ["Action Hero"])

    def test_unparseable_year_is_skipped(self):
        bad = SAMPLE_MOVIES + [{"name": "Mystery", "date": "??", "genre": "",
                                 "rating": "0", "actors": "", "theme": ""}]
        result = self.r.filter_by_year_range(bad, 1900, 2100)
        self.assertNotIn("Mystery", [m["name"] for m in result])


class TestFilterByActors(unittest.TestCase):
    def setUp(self):
        self.r = MovieRecommender(SAMPLE_MOVIES)

    def test_single_actor_match(self):
        result = self.r.filter_by_actors(SAMPLE_MOVIES, ["Tom Cruise"])
        names = sorted(m["name"] for m in result)
        self.assertEqual(names, ["Action Hero", "Sci-Fi Epic"])

    def test_actor_match_is_case_insensitive(self):
        self.assertEqual(len(self.r.filter_by_actors(SAMPLE_MOVIES, ["tom cruise"])), 2)

    def test_or_across_actors(self):
        result = self.r.filter_by_actors(SAMPLE_MOVIES, ["Margot Robbie", "Tom Cruise"])
        self.assertEqual(len(result), 3)

    def test_empty_list_returns_all(self):
        self.assertEqual(len(self.r.filter_by_actors(SAMPLE_MOVIES, [])), 3)


class TestFilterByThemes(unittest.TestCase):

    def setUp(self):
        self.r = MovieRecommender(SAMPLE_MOVIES)

    def test_substring_match(self):
        result = self.r.filter_by_themes(SAMPLE_MOVIES, ["sci-fi"])
        self.assertEqual([m["name"] for m in result], ["Sci-Fi Epic"])

    def test_substring_match_is_case_insensitive(self):
        result = self.r.filter_by_themes(SAMPLE_MOVIES, ["RELATIONSHIP"])
        self.assertEqual([m["name"] for m in result], ["Romance Tale"])

    def test_or_across_themes(self):
        result = self.r.filter_by_themes(SAMPLE_MOVIES, ["sci-fi", "action"])
        self.assertEqual(len(result), 2)

    def test_empty_list_returns_all(self):
        self.assertEqual(len(self.r.filter_by_themes(SAMPLE_MOVIES, [])), 3)

if __name__ == "__main__":
    unittest.main()
