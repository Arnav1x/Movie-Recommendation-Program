import unittest
from recommender import MovieRecommender
from Main import parse_list, parse_year_range, parse_float, parse_int

# Sample movies for filter tests
SAMPLE_MOVIES = [
    {
        "id": "1", "name": "Action Hero", "date": "2015", "minute": "110",
        "genre": "Action|Thriller", "rating": "4.0",
        "actors": "Tom Cruise|Emily Blunt",
        "director": "John Smith",
        "theme": "high-octane action",
        "description": "A spy saves the world.",
    },
    {
        "id": "2", "name": "Romance Tale", "date": "2005", "minute": "95",
        "genre": "Romance|Drama", "rating": "3.5",
        "actors": "Margot Robbie",
        "director": "Jane Doe",
        "theme": "moving relationship stories",
        "description": "Two people fall in love in Paris.",
    },
    {
        "id": "3", "name": "Sci-Fi Epic", "date": "2020", "minute": "150",
        "genre": "Science Fiction|Adventure", "rating": "4.8",
        "actors": "Tom Cruise",
        "director": "Greta Gerwig",
        "theme": "spectacular sci-fi epic",
        "description": "Astronauts travel through wormholes to save Earth.",
    },
]


def _pref(genres=None, themes=None, directors=None, actors=None,
          min_rating=None, runtime=None, year_range=None,
          db_genres=False, db_themes=False, db_directors=False,
          db_actors=False, db_min_rating=False, db_runtime=False,
          db_year_range=False):
    """Tiny helper to build a preferences dict for the tests."""
    return {
        "genres":     {"values": genres or [],    "deal_breaker": db_genres},
        "themes":     {"values": themes or [],    "deal_breaker": db_themes},
        "directors":  {"values": directors or [], "deal_breaker": db_directors},
        "actors":     {"values": actors or [],    "deal_breaker": db_actors},
        "min_rating": {"value":  min_rating,      "deal_breaker": db_min_rating},
        "runtime":    {"value":  runtime,         "deal_breaker": db_runtime},
        "year_range": {"value":  year_range or (None, None), "deal_breaker": db_year_range},
    }


"""
Tests cover all filtering methods and the deal-breaker / scoring flow.
Filters take simple lists, so the older-style calls still work; rank()
uses the new structured preference dict.
"""


class TestFilterByGenres(unittest.TestCase):
    """`filter_by_genres` should match any-of (OR), case-insensitive."""

    def setUp(self):
        self.r = MovieRecommender(SAMPLE_MOVIES)

    def test_single_genre_matches_one_movie(self):
        result = self.r.filter_by_genres(SAMPLE_MOVIES, ["Action"])
        self.assertEqual([m["name"] for m in result], ["Action Hero"])

    def test_match_is_case_insensitive(self):
        result = self.r.filter_by_genres(SAMPLE_MOVIES, ["aCtIoN"])
        self.assertEqual(len(result), 1)

    def test_or_semantics_across_genres(self):
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

    def test_comma_separated_actors_also_match(self):
        """Real dataset uses commas — make sure that works too."""
        movie = [{"name": "X", "actors": "Margot Robbie, Ryan Gosling",
                  "genre": "", "theme": "", "date": "2023", "rating": "4"}]
        r = MovieRecommender(movie)
        self.assertEqual(len(r.filter_by_actors(movie, ["Ryan Gosling"])), 1)


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

    def test_searches_description_column_too(self):
        """Keyword "wormholes" only appears in description, not theme."""
        result = self.r.filter_by_themes(SAMPLE_MOVIES, ["wormholes"])
        self.assertEqual([m["name"] for m in result], ["Sci-Fi Epic"])

    def test_searches_description_case_insensitive(self):
        result = self.r.filter_by_themes(SAMPLE_MOVIES, ["paris"])
        self.assertEqual([m["name"] for m in result], ["Romance Tale"])


class TestFilterByDirectors(unittest.TestCase):

    def setUp(self):
        self.r = MovieRecommender(SAMPLE_MOVIES)

    def test_single_director_match(self):
        result = self.r.filter_by_directors(SAMPLE_MOVIES, ["Greta Gerwig"])
        self.assertEqual([m["name"] for m in result], ["Sci-Fi Epic"])

    def test_director_match_case_insensitive(self):
        result = self.r.filter_by_directors(SAMPLE_MOVIES, ["greta gerwig"])
        self.assertEqual(len(result), 1)

    def test_or_across_directors(self):
        result = self.r.filter_by_directors(SAMPLE_MOVIES, ["John Smith", "Jane Doe"])
        self.assertEqual(len(result), 2)

    def test_empty_returns_all(self):
        self.assertEqual(len(self.r.filter_by_directors(SAMPLE_MOVIES, [])), 3)


class TestFilterByMinRating(unittest.TestCase):

    def setUp(self):
        self.r = MovieRecommender(SAMPLE_MOVIES)

    def test_min_rating_excludes_lower(self):
        result = self.r.filter_by_min_rating(SAMPLE_MOVIES, 4.0)
        names = sorted(m["name"] for m in result)
        self.assertEqual(names, ["Action Hero", "Sci-Fi Epic"])

    def test_none_returns_all(self):
        self.assertEqual(len(self.r.filter_by_min_rating(SAMPLE_MOVIES, None)), 3)

    def test_high_threshold_returns_few(self):
        result = self.r.filter_by_min_rating(SAMPLE_MOVIES, 4.5)
        self.assertEqual([m["name"] for m in result], ["Sci-Fi Epic"])


class TestFilterByRuntime(unittest.TestCase):

    def setUp(self):
        self.r = MovieRecommender(SAMPLE_MOVIES)

    def test_runtime_within_tolerance(self):
        # Target 100, tolerance 30 -> 70..130 -> Action Hero (110) + Romance Tale (95)
        result = self.r.filter_by_runtime(SAMPLE_MOVIES, 100, tolerance=30)
        names = sorted(m["name"] for m in result)
        self.assertEqual(names, ["Action Hero", "Romance Tale"])

    def test_runtime_none_returns_all(self):
        self.assertEqual(len(self.r.filter_by_runtime(SAMPLE_MOVIES, None)), 3)


class TestDealBreakers(unittest.TestCase):
    """rank() should exclude movies failing any deal breaker before scoring."""

    def setUp(self):
        self.r = MovieRecommender(SAMPLE_MOVIES)

    def test_genre_deal_breaker_excludes_non_matches(self):
        prefs = _pref(genres=["Romance"], db_genres=True)
        ranked = self.r.rank(prefs, top_n=5)
        self.assertEqual([m["name"] for _, m in ranked], ["Romance Tale"])

    def test_genre_preference_keeps_non_matches_with_lower_score(self):
        prefs = _pref(genres=["Romance"], db_genres=False)
        ranked = self.r.rank(prefs, top_n=5)
        # Romance Tale should be top because it actually matches
        self.assertEqual(ranked[0][1]["name"], "Romance Tale")
        self.assertEqual(len(ranked), 3)  # nothing filtered out

    def test_min_rating_deal_breaker(self):
        prefs = _pref(min_rating=4.5, db_min_rating=True)
        ranked = self.r.rank(prefs, top_n=5)
        self.assertEqual([m["name"] for _, m in ranked], ["Sci-Fi Epic"])

    def test_director_deal_breaker(self):
        prefs = _pref(directors=["Greta Gerwig"], db_directors=True)
        ranked = self.r.rank(prefs, top_n=5)
        self.assertEqual([m["name"] for _, m in ranked], ["Sci-Fi Epic"])

    def test_runtime_deal_breaker(self):
        prefs = _pref(runtime=150, db_runtime=True)
        ranked = self.r.rank(prefs, top_n=5)
        self.assertEqual([m["name"] for _, m in ranked], ["Sci-Fi Epic"])


class TestScoring(unittest.TestCase):

    def setUp(self):
        self.r = MovieRecommender(SAMPLE_MOVIES)

    def test_no_preferences_falls_back_to_rating(self):
        prefs = _pref()
        ranked = self.r.rank(prefs, top_n=5)
        # Sorted by rating descending: 4.8, 4.0, 3.5
        self.assertEqual([m["name"] for _, m in ranked],
                         ["Sci-Fi Epic", "Action Hero", "Romance Tale"])

    def test_perfect_match_scores_100(self):
        prefs = _pref(genres=["Romance", "Drama"])
        ranked = self.r.rank(prefs, top_n=5)
        top_score, top_movie = ranked[0]
        self.assertEqual(top_movie["name"], "Romance Tale")
        self.assertAlmostEqual(top_score, 100.0, places=1)

    def test_genres_outweigh_year_range(self):
        # Romance Tale matches genre, Action Hero matches the year range.
        # Genre weight (32) > year_range weight (6), so Romance should win.
        prefs = _pref(genres=["Romance"], year_range=(2015, 2015))
        ranked = self.r.rank(prefs, top_n=5)
        self.assertEqual(ranked[0][1]["name"], "Romance Tale")


class TestInputParsers(unittest.TestCase):

    def test_parse_year_range_pair(self):
        self.assertEqual(parse_year_range("2010-2020"), (2010, 2020))

    def test_parse_year_range_single(self):
        self.assertEqual(parse_year_range("2015"), (2015, 2015))

    def test_parse_year_range_blank(self):
        self.assertEqual(parse_year_range(""), (None, None))

    def test_parse_year_range_garbage(self):
        self.assertEqual(parse_year_range("abc"), (None, None))

    def test_parse_list_trims_and_drops_blanks(self):
        self.assertEqual(parse_list("Action,  Comedy, , Drama"),
                         ["Action", "Comedy", "Drama"])

    def test_parse_float_valid(self):
        self.assertEqual(parse_float("4.5"), 4.5)

    def test_parse_float_invalid(self):
        self.assertIsNone(parse_float("abc"))
        self.assertIsNone(parse_float(""))

    def test_parse_int_valid(self):
        self.assertEqual(parse_int("120"), 120)

    def test_parse_int_invalid(self):
        self.assertIsNone(parse_int("abc"))
        self.assertIsNone(parse_int(""))


if __name__ == "__main__":
    unittest.main()