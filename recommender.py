"""
This is the brains of the project, while Main is the face of the project.

All the thinking is found here, including filtering, deal-breakers,
scoring, sorting, and ranking.
"""


def _split_multi(value):
    """
    Splits a field on both '|' and ',' and returns a lowercased set.
    Genres/themes use '|'; actors/directors use ',' so this handles both.
    """
    if not value:
        return set()
    tokens = value.replace("|", ",").split(",")
    return {t.strip().lower() for t in tokens if t.strip()}


_split_field = _split_multi


def _normalize_terms(terms):
    """Strips and lowercases search terms gotten from the user."""
    return [t.strip().lower() for t in terms if t and t.strip()]


class MovieRecommender:
    """
    Takes a list of movies (each a dict with keys like
    'name', 'date', 'minute', 'rating', 'genre', 'theme', 'description',
    'actors', 'director') and ranks them by how well they match a user's
    preferences.

    The 'preferences' dict has this shape:
        {
            "genres":     {"values": list[str], "deal_breaker": bool},
            "themes":     {"values": list[str], "deal_breaker": bool},
            "directors":  {"values": list[str], "deal_breaker": bool},
            "actors":     {"values": list[str], "deal_breaker": bool},
            "min_rating": {"value":  float|None, "deal_breaker": bool},
            "runtime":    {"value":  int|None,   "deal_breaker": bool},
            "year_range": {"value":  (int|None, int|None), "deal_breaker": bool},
        }
    """

    # Order of importance/Hierarchy is this: genres > themes >(substancial gap)> directors > actors > rating/runtime > year
    # Genres + themes together carry over half the score; there's a decent
    # gap before directors/actors; rating/runtime/year are tiebreakers.
    CATEGORY_WEIGHTS = {
        "genres":     32, #Genres and themes make sense to be the strongest, it's typically the first questions asked when searching for a movie. 
        "themes":     23,
        # gap 
        "directors":  15,
        "actors":     12,
        "min_rating":  6, #Thought to make the "specifics" less important. These should just be a small bonus, not a defining factor. All these only get 6
        "runtime":     6, #For example if a user puts in the year range 2000-2026, there may be a movie from 1999 that matches the rest of the criteria perfectly. 
        "year_range":  6, #It would be unfair for that movie to get docked too low
    }
    #Threshold for how much lenience to give for movie runtimes
    RUNTIME_SCORE_FALLOFF = 60          # minutes: score drops to 0 at this distance
    RUNTIME_DEAL_BREAKER_TOLERANCE = 30  # +/- minutes when runtime is a deal breaker

    def __init__(self, movies):
        self.movies = list(movies)

    # Filtering Section 
    def filter_by_genres(self, movies, genres):
        """Returns movies whose genre field overlaps with any wanted genre. 

        Args:
            movies (list[dict]): the movies to filter.
            genres (list[str]): genres the user wants (case-insensitive, OR semantics).

        Returns:
            list[dict]: movies that match at least one genre, or all of them if 'genres' is empty.
        """
        wanted = set(_normalize_terms(genres))
        if not wanted:
            return list(movies)
        return [m for m in movies if wanted & _split_multi(m.get("genre", ""))]

    def filter_by_themes(self, movies, themes):
        """Filters movies by string matching keywords inside of the collums "theme" and "description" in the dataset

        Args:
            movies (list[dict]): the movies to filter.
            themes (list[str]): keywords or short phrases to look for (case-insensitive).

        Returns:
            list[dict]: movies where at least one keyword appears in either the theme or description field, or all of them if 'themes' is empty.
        """
        wanted = _normalize_terms(themes)
        if not wanted:
            return list(movies)
        result = []
        for movie in movies:
            haystack = (movie.get("theme", "") + " " + movie.get("description", "")).lower()
            if any(term in haystack for term in wanted):
                result.append(movie)
        return result

    def filter_by_directors(self, movies, directors):
        """Filters movies whose director matches any of the requested ones.

        Args:
            movies (list[dict]): the movies to filter.
            directors (list[str]): preferred director names (case-insensitive).

        Returns:
            list[dict]: movies directed by one of the requested directors, or all of them if 'directors' is empty.
        """
        wanted = set(_normalize_terms(directors))
        if not wanted:
            return list(movies)
        return [m for m in movies if wanted & _split_multi(m.get("director", ""))]

    def filter_by_actors(self, movies, actors):
        """Filters movies that include at least one of the requested actors.

        Args:
            movies (list[dict]): the movies to filter.
            actors (list[str]): preferred actor names (case-insensitive).

        Returns:
            list[dict]: movies with a matching actor, or all of them if 'actors' is empty.
        """
        wanted = set(_normalize_terms(actors))
        if not wanted:
            return list(movies)
        return [m for m in movies if wanted & _split_multi(m.get("actors", ""))]

    def filter_by_min_rating(self, movies, min_rating):
        """Filters out movies whose rating falls below 'min_rating'.

        Args:
            movies (list[dict]): the movies to filter.
            min_rating (float | None): minimum acceptable rating on the 0-5 scale.

        Returns:
            list[dict]: movies that meet or exceed the threshold, or all of them if 'min_rating' is None. Movies with an unparseable rating are dropped.
        """
        if min_rating is None:
            return list(movies)
        result = []
        for m in movies:
            try:
                if float(m.get("rating", "")) >= min_rating:
                    result.append(m)
            except (ValueError, TypeError):
                continue
        return result

    def filter_by_runtime(self, movies, runtime, tolerance=None):
        """Filters movies whose runtime is within 'tolerance' minutes of the target.

        Args:
            movies (list[dict]): the movies to filter.
            runtime (int | None): preferred runtime in minutes.
            tolerance (int | None): allowed deviation in minutes. Defaults to RUNTIME_DEAL_BREAKER_TOLERANCE.

        Returns:
            list[dict]: movies whose runtime is within 'tolerance' minutes of 'runtime', or all of them if 'runtime' is None.
        """
        if runtime is None:
            return list(movies)
        if tolerance is None:
            tolerance = self.RUNTIME_DEAL_BREAKER_TOLERANCE
        result = []
        for m in movies:
            try:
                mr = int(m.get("minute", ""))
            except (ValueError, TypeError):
                continue
            if abs(mr - runtime) <= tolerance:
                result.append(m)
        return result

    def filter_by_year_range(self, movies, start, end):
        """Filters movies whose release year falls within [start, end] inclusive.

        Args:
            movies (list[dict]): the movies to filter.
            start (int | None): earliest acceptable year, or None for no lower bound.
            end (int | None): latest acceptable year, or None for no upper bound.

        Returns:
            list[dict]: movies within the year range, or all of them if both bounds are None. Movies with an unparseable date are dropped.
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

    # Scoring Section

    def score_movie(self, movie, preferences):
        """Scores how well a movie matches the user's preferences on a 0-100 percentage based scale

        Handles what happenes if the user leaves a question blank and adjusts accordingly, so that the score still is out of 100. 
        
        Args:
            movie (dict): the movie to score.
            preferences (dict): the full preferences dict from ask_user_preferences().

        Returns:
            float: a score between 0 and 100. Falls back to the movie's own rating (scaled to 0-100) if the user filled in no preferences.
        """
        active = [c for c in self.CATEGORY_WEIGHTS
                  if self._category_is_set(preferences, c)]
        if not active:
            return self._rating_as_score(movie)

        total_weight = sum(self.CATEGORY_WEIGHTS[c] for c in active)
        scale = 100.0 / total_weight
        w = {c: self.CATEGORY_WEIGHTS[c] * scale for c in active}

        total = 0.0

        if "genres" in w:
            total += w["genres"] * self._overlap_ratio(
                _normalize_terms(preferences["genres"]["values"]),
                _split_multi(movie.get("genre", "")),
            )

        if "themes" in w:
            haystack = (movie.get("theme", "") + " " + movie.get("description", "")).lower()
            total += w["themes"] * self._theme_match_ratio(
                _normalize_terms(preferences["themes"]["values"]),
                haystack,
            )

        if "directors" in w:
            total += w["directors"] * self._overlap_ratio(
                _normalize_terms(preferences["directors"]["values"]),
                _split_multi(movie.get("director", "")),
            )

        if "actors" in w:
            total += w["actors"] * self._overlap_ratio(
                _normalize_terms(preferences["actors"]["values"]),
                _split_multi(movie.get("actors", "")),
            )

        if "min_rating" in w:
            min_r = preferences["min_rating"]["value"]
            try:
                if float(movie.get("rating", "")) >= min_r:
                    total += w["min_rating"]
            except (ValueError, TypeError):
                pass

        if "runtime" in w:
            target = preferences["runtime"]["value"]
            try:
                mr = int(movie.get("minute", ""))
                diff = abs(mr - target)
                if diff < self.RUNTIME_SCORE_FALLOFF:
                    total += w["runtime"] * (1 - diff / self.RUNTIME_SCORE_FALLOFF)
            except (ValueError, TypeError):
                pass

        if "year_range" in w:
            start, end = preferences["year_range"]["value"]
            if self._year_in_range(movie, start, end):
                total += w["year_range"]

        return total

    def rank(self, preferences, top_n=5):
        """
        Applies any deal-breaker filters, then scores the survivors and
        returns the top N as a list of (score, movie) tuples. Ties broken
        by raw movie rating so the order is deterministic.
        """
        movies = self._apply_deal_breakers(self.movies, preferences)
        scored = [(self.score_movie(m, preferences), m) for m in movies]
        scored.sort(
            key=lambda pair: (pair[0], self._rating_as_score(pair[1])),
            reverse=True,
        )
        return scored[:top_n]

    # Helper Functions Below

    def _apply_deal_breakers(self, movies, preferences):
        """Removes movies that fail any of the user's deal-breaker filters.

        Args:
            movies (list[dict]): the candidate movies.
            preferences (dict): the full preferences dict from ask_user_preferences().

        Returns:
            list[dict]: movies that survive every active deal-breaker. Categories that the user didn't toggle as deal-breakers are ignored here.
        """
        result = list(movies)
        if self._is_deal_breaker(preferences, "genres"):
            result = self.filter_by_genres(result, preferences["genres"]["values"])
        if self._is_deal_breaker(preferences, "themes"):
            result = self.filter_by_themes(result, preferences["themes"]["values"])
        if self._is_deal_breaker(preferences, "directors"):
            result = self.filter_by_directors(result, preferences["directors"]["values"])
        if self._is_deal_breaker(preferences, "actors"):
            result = self.filter_by_actors(result, preferences["actors"]["values"])
        if self._is_deal_breaker(preferences, "min_rating"):
            result = self.filter_by_min_rating(result, preferences["min_rating"]["value"])
        if self._is_deal_breaker(preferences, "runtime"):
            result = self.filter_by_runtime(result, preferences["runtime"]["value"])
        if self._is_deal_breaker(preferences, "year_range"):
            start, end = preferences["year_range"]["value"]
            result = self.filter_by_year_range(result, start, end)
        return result

    @staticmethod
    def _category_is_set(preferences, category):
        """Checks whether the user actually filled in a given preference category.

        Args:
            preferences (dict): the full preferences dict.
            category (str): the category name to check (e.g. "genres", "year_range").

        Returns:
            bool: True if the user provided a value for this category. Empty lists, (None, None) year ranges, and None scalars all count as unset.
        """
        cat = preferences.get(category) or {}
        if category in ("genres", "themes", "directors", "actors"):
            return bool(cat.get("values"))
        if category == "year_range":
            start, end = cat.get("value", (None, None))
            return start is not None or end is not None
        if category in ("min_rating", "runtime"):
            return cat.get("value") is not None
        return False

    @staticmethod
    def _is_deal_breaker(preferences, category):
        """Reports whether a category was both filled in and flagged as a deal breaker.

        Args:
            preferences (dict): the full preferences dict.
            category (str): the category name to check.

        Returns:
            bool: True if the category is set and the user toggled deal-breaker on. A deal-breaker flag on an empty category is ignored.
        """
        cat = preferences.get(category) or {}
        if not cat.get("deal_breaker"):
            return False
        # Only treat as a deal breaker if the user actually filled it in.
        return MovieRecommender._category_is_set(preferences, category)

    @staticmethod
    def _overlap_ratio(wanted, available):
        """|wanted ∩ available| / |wanted|, or 0 if 'wanted' is empty."""
        if not wanted:
            return 0.0
        wanted_set = set(wanted)
        return len(wanted_set & available) / len(wanted_set)

    @staticmethod
    def _theme_match_ratio(wanted_terms, haystack):
        """Fraction of 'wanted_terms' that appear in 'haystack'."""
        if not wanted_terms:
            return 0.0
        hits = sum(1 for term in wanted_terms if term in haystack)
        return hits / len(wanted_terms)

    @staticmethod
    def _year_in_range(movie, start, end):
        """Checks whether a movie's release year falls within [start, end].

        Args:
            movie (dict): a single movie dict; the 'date' key is read as the year.
            start (int | None): earliest acceptable year, or None for no lower bound.
            end (int | None): latest acceptable year, or None for no upper bound.

        Returns:
            bool: True if the year is within range. False if the year is unparseable or out of range.
        """
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
        """Converts a 0-5 rating into a 0-100 score, or 0 if missing."""
        try:
            return float(movie.get("rating", "")) / 5.0 * 100.0
        except (ValueError, TypeError):
            return 0.0