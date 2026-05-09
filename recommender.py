"""

This is the brains of the project, while Main is the face of the project.

All the thinking is found here, inclduing fitlering, sorting, ranking, and score generation.

"""


def _split_field(value, separator="|"):
    """This splits into a lowercased, stripped set."""
    if not value:
        return set()
    return {item.strip().lower() for item in value.split(separator) if item.strip()}


def _normalize_terms(terms):
    """This strips and lowercase it to a list of search terms gotten from the user from before"""
    return [t.strip().lower() for t in terms if t and t.strip()]


class MovieRecommender:
    """
    This takes a list of movies (each represented as a dict with the keys
    `name`, `date`, `genre`, `rating`, `actors`, `theme`) and then it gives methods
    to filter and rank them based on user preferences.

    A "preferences" dict (should) have the shape:
        {
            "genres":     list[str],                  # e.g. ["Action", "Comedy"]
            "year_range": (int|None, int|None),       # e.g. (2010, 2020)
            "actors":     list[str],                  # e.g. ["Tom Cruise"]
            "themes":     list[str],                  # e.g. ["family drama"]
        }
    """


    SCORED_CATEGORIES = ("genres", "year_range", "actors", "themes")

    # Hierarchy: genres > themes > (gap) > actors > year_range.
    # Genres + themes carry 75% of the score; actors/year are tiebreakers.
    CATEGORY_WEIGHTS = {
        "genres":     45,
        "themes":     30,
        "actors":     15,
        "year_range": 10,
    }

    def __init__(self, movies):
        self.movies = list(movies)

    def filter_by_genres(self, movies, genres):
        """
        This returns movies whose `genre` field overlaps with any of the requested
        genres (OR semantics, case-insensitive).
        """
        wanted = set(_normalize_terms(genres))
        if not wanted:
            return list(movies)
        return [m for m in movies if wanted & _split_field(m.get("genre", ""))]

    def filter_by_year_range(self, movies, start, end):
        """
        This filters movies whose release year falls within [start, end] (inclusive).
        """
        if start is None and end is None:
            return list(movies)
        result = []
        for movie in movies:
            try:
                year = int(movie.get("date", ""))
            except (ValueError, TypeError):
                continue
            if start is not None and year < start:
                continue
            if end is not None and year > end:
                continue
            result.append(movie)
        return result

    def filter_by_actors(self, movies, actors):
        """
        This filters movies that include at least one of the requested actors
        """
        wanted = set(_normalize_terms(actors))
        if not wanted:
            return list(movies)
        return [m for m in movies if wanted & _split_field(m.get("actors", ""))]

    def filter_by_themes(self, movies, themes):
        """
        THis filters movies by themes
        """
        wanted = _normalize_terms(themes)
        if not wanted:
            return list(movies)
        result = []
        for movie in movies:
            haystack = movie.get("theme", "").lower()
            if any(term in haystack for term in wanted):
                result.append(movie)
        return result

    def score_movie(self, movie, preferences):
        """
        Returns a 0-100 score based on how well the movie matches the user's
        preferences. Categories are weighted by importance (genres > themes
        >> actors > year_range). Categories the user left blank are skipped
        and the remaining weights are renormalized so a perfect match across
        the active categories still scores 100.
        """
        active = [c for c in self.SCORED_CATEGORIES
                  if self._category_is_set(preferences, c)]
        if not active:
            return self._rating_as_score(movie)

        total_weight = sum(self.CATEGORY_WEIGHTS[c] for c in active)
        scale = 100.0 / total_weight
        w = {c: self.CATEGORY_WEIGHTS[c] * scale for c in active}

        total = 0.0

        if "genres" in w:
            total += w["genres"] * self._overlap_ratio(
                _normalize_terms(preferences["genres"]),
                _split_field(movie.get("genre", "")),
            )

        if "year_range" in w:
            start, end = preferences["year_range"]
            if self._year_in_range(movie, start, end):
                total += w["year_range"]

        if "actors" in w:
            total += w["actors"] * self._overlap_ratio(
                _normalize_terms(preferences["actors"]),
                _split_field(movie.get("actors", "")),
            )

        if "themes" in w:
            total += w["themes"] * self._theme_match_ratio(
                _normalize_terms(preferences["themes"]),
                movie.get("theme", "").lower(),
            )

        return total

    def rank(self, preferences, top_n=5):
        """
        This scores every movie in the dataset and return the top N as a list of
        (score, movie) tuples sorted by score descending. Ties are broken by
        the movie's own rating (highest first) so the order is deterministic.
        """
        scored = [(self.score_movie(m, preferences), m) for m in self.movies]
        scored.sort(
            key=lambda pair: (pair[0], self._rating_as_score(pair[1])),
            reverse=True,
        )
        return scored[:top_n]


    @staticmethod
    def _category_is_set(preferences, category):
        """
        True if the user actually filled this preference category in. Empty
        lists count as unset.
        """
        value = preferences.get(category)
        if not value:
            return False
        if category == "year_range":
            start, end = value
            return start is not None or end is not None
        return True

    @staticmethod
    def _overlap_ratio(wanted, available):
        """Return |wanted ∩ available| / |wanted|, or 0 if `wanted` is empty."""
        if not wanted:
            return 0.0
        wanted_set = set(wanted)
        return len(wanted_set & available) / len(wanted_set)

    @staticmethod
    def _theme_match_ratio(wanted_terms, theme_haystack):
        """Return the fraction of `wanted_terms` that appear in `theme_haystack`."""
        if not wanted_terms:
            return 0.0
        hits = sum(1 for term in wanted_terms if term in theme_haystack)
        return hits / len(wanted_terms)

    @staticmethod
    def _year_in_range(movie, start, end):
        """True if movie's release year is within [start, end] (inclusive)."""
        try:
            year = int(movie.get("date", ""))
        except (ValueError, TypeError):
            return False
        if start is not None and year < start:
            return False
        if end is not None and year > end:
            return False
        return True

    @staticmethod
    def _rating_as_score(movie):
        """Convert the movie's 0-5 rating into a 0-100 score, or 0.0 if missing."""
        try:
            return float(movie.get("rating", "")) / 5.0 * 100.0
        except (ValueError, TypeError):
            return 0.0