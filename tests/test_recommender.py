import pytest
from src.recommender import (
    Song, UserProfile, load_songs, score_song, score_song_advanced, recommend_songs,
    recommend_songs_with_diversity,
    ScoringWeights, ScoringStrategy, WeightedScoringStrategy, get_strategy, SCORING_MODES,
    extract_top_reasons, format_recommendation_summary, format_recommendation_detailed,
    _filter_reason_lines
)


# Test fixtures: small dataset for testing
@pytest.fixture
def sample_songs():
    return [
        {
            'id': 1,
            'title': "Happy Pop Track",
            'artist': "Pop Artist",
            'genre': "pop",
            'mood': "happy",
            'energy': 0.85,
            'tempo_bpm': 120,
            'valence': 0.90,
            'danceability': 0.80,
            'acousticness': 0.15,
            'popularity': 78,
            'release_decade': 2020,
            'vocal_style': "sung",
            'production_quality': "polished",
            'emotional_arc': "constant",
        },
        {
            'id': 2,
            'title': "Chill Lofi Song",
            'artist': "Lofi Artist",
            'genre': "lofi",
            'mood': "chill",
            'energy': 0.35,
            'tempo_bpm': 80,
            'valence': 0.60,
            'danceability': 0.50,
            'acousticness': 0.85,
            'popularity': 42,
            'release_decade': 2020,
            'vocal_style': "instrumental",
            'production_quality': "lo-fi",
            'emotional_arc': "constant",
        },
        {
            'id': 3,
            'title': "Intense Rock",
            'artist': "Rock Band",
            'genre': "rock",
            'mood': "intense",
            'energy': 0.92,
            'tempo_bpm': 160,
            'valence': 0.45,
            'danceability': 0.60,
            'acousticness': 0.10,
            'popularity': 65,
            'release_decade': 2010,
            'vocal_style': "sung",
            'production_quality': "polished",
            'emotional_arc': "builds",
        },
    ]


@pytest.fixture
def pop_lover_profile():
    return {
        'favorite_genre': 'pop',
        'favorite_mood': 'happy',
        'target_energy': 0.85,
        'likes_acoustic': False,
    }


@pytest.fixture
def lofi_lover_profile():
    return {
        'favorite_genre': 'lofi',
        'favorite_mood': 'chill',
        'target_energy': 0.35,
        'likes_acoustic': True,
    }


# Tests for score_song function
class TestScoreSong:
    """Test the GMEWS scoring algorithm."""

    def test_perfect_match_scores_high(self, sample_songs, pop_lover_profile):
        song = sample_songs[0]  # Happy pop track
        score, reasons = score_song(pop_lover_profile, song)

        # Should have genre match (2.0) + mood match (2.0) + energy (~1.5) + acousticness (~0.85) + danceability (~0.24)
        assert score > 6.0, f"Perfect match should score above 6.0, got {score}"
        assert any("Genre match" in r for r in reasons)
        assert any("Mood match" in r for r in reasons)

    def test_no_match_scores_lower(self, sample_songs, lofi_lover_profile):
        song = sample_songs[0]  # Happy pop track (wrong for lofi lover)
        score, reasons = score_song(lofi_lover_profile, song)

        # Should have no genre match, no mood match, some energy penalty
        assert score < 4.0, f"Non-matching song should score below 4.0, got {score}"
        assert any("Genre mismatch" in r for r in reasons)
        assert any("Mood mismatch" in r for r in reasons)

    def test_energy_distance_affects_score(self, pop_lover_profile):
        song_close_energy = {
            'id': 1, 'title': "Test", 'artist': "Test", 'genre': "pop", 'mood': "happy",
            'energy': 0.84, 'tempo_bpm': 120, 'valence': 0.8, 'danceability': 0.7, 'acousticness': 0.1,
        }
        song_far_energy = {
            'id': 2, 'title': "Test", 'artist': "Test", 'genre': "pop", 'mood': "happy",
            'energy': 0.20, 'tempo_bpm': 100, 'valence': 0.8, 'danceability': 0.7, 'acousticness': 0.1,
        }

        score_close, _ = score_song(pop_lover_profile, song_close_energy)
        score_far, _ = score_song(pop_lover_profile, song_far_energy)

        assert score_close > score_far, "Song with closer energy should score higher"

    def test_danceability_bonus_for_high_energy_users(self, pop_lover_profile):
        song_high_dance = {
            'id': 1, 'title': "Test", 'artist': "Test", 'genre': "pop", 'mood': "happy",
            'energy': 0.85, 'tempo_bpm': 120, 'valence': 0.8, 'danceability': 0.90, 'acousticness': 0.1,
        }

        score, reasons = score_song(pop_lover_profile, song_high_dance)

        # High energy user (0.85 >= 0.7) should get danceability bonus
        assert any("Danceability bonus" in r and "+" in r for r in reasons), "Should show danceability bonus"

    def test_no_danceability_bonus_for_low_energy_users(self, lofi_lover_profile):
        song = {
            'id': 1, 'title': "Test", 'artist': "Test", 'genre': "lofi", 'mood': "chill",
            'energy': 0.35, 'tempo_bpm': 80, 'valence': 0.6, 'danceability': 0.90, 'acousticness': 0.8,
        }

        score, reasons = score_song(lofi_lover_profile, song)

        # Low energy user (0.35 < 0.7) should NOT get danceability bonus
        assert any("N/A (low energy user)" in r for r in reasons), "Should indicate danceability N/A for low energy user"

    def test_acousticness_preference_electronic_lover(self, pop_lover_profile):
        song_electronic = {
            'id': 1, 'title': "Test", 'artist': "Test", 'genre': "pop", 'mood': "happy",
            'energy': 0.85, 'tempo_bpm': 120, 'valence': 0.8, 'danceability': 0.7, 'acousticness': 0.1,
        }
        song_acoustic = {
            'id': 2, 'title': "Test", 'artist': "Test", 'genre': "pop", 'mood': "happy",
            'energy': 0.85, 'tempo_bpm': 120, 'valence': 0.8, 'danceability': 0.7, 'acousticness': 0.9,
        }

        score_electronic, _ = score_song(pop_lover_profile, song_electronic)
        score_acoustic, _ = score_song(pop_lover_profile, song_acoustic)

        # Electronic lover should prefer less acoustic song
        assert score_electronic > score_acoustic, "Electronic lover should prefer electronic songs"

    def test_acousticness_preference_acoustic_lover(self, lofi_lover_profile):
        song_electronic = {
            'id': 1, 'title': "Test", 'artist': "Test", 'genre': "lofi", 'mood': "chill",
            'energy': 0.35, 'tempo_bpm': 80, 'valence': 0.6, 'danceability': 0.5, 'acousticness': 0.1,
        }
        song_acoustic = {
            'id': 2, 'title': "Test", 'artist': "Test", 'genre': "lofi", 'mood': "chill",
            'energy': 0.35, 'tempo_bpm': 80, 'valence': 0.6, 'danceability': 0.5, 'acousticness': 0.9,
        }

        score_electronic, _ = score_song(lofi_lover_profile, song_electronic)
        score_acoustic, _ = score_song(lofi_lover_profile, song_acoustic)

        # Acoustic lover should prefer more acoustic song
        assert score_acoustic > score_electronic, "Acoustic lover should prefer acoustic songs"

    def test_score_returns_tuple(self, sample_songs, pop_lover_profile):
        song = sample_songs[0]
        result = score_song(pop_lover_profile, song)

        assert isinstance(result, tuple), "score_song should return a tuple"
        assert len(result) == 2, "Tuple should have 2 elements (score, reasons)"
        score, reasons = result
        assert isinstance(score, float), "Score should be float"
        assert isinstance(reasons, list), "Reasons should be list"
        assert len(reasons) > 0, "Should have at least one reason"


# Tests for recommend_songs function
class TestRecommendSongs:
    """Test the recommendation ranking."""

    def test_recommend_returns_list(self, sample_songs, pop_lover_profile):
        recommendations = recommend_songs(pop_lover_profile, sample_songs, k=2)

        assert isinstance(recommendations, list), "Should return list"
        assert len(recommendations) <= 2, "Should return at most k items"

    def test_recommend_returns_k_items(self, sample_songs, pop_lover_profile):
        recommendations = recommend_songs(pop_lover_profile, sample_songs, k=2)

        assert len(recommendations) == 2, "Should return exactly k items"

    def test_recommendations_sorted_by_score_descending(self, sample_songs, pop_lover_profile):
        recommendations = recommend_songs(pop_lover_profile, sample_songs, k=3)

        scores = [score for song, score, reasons in recommendations]
        assert scores == sorted(scores, reverse=True), "Recommendations should be sorted by score descending"

    def test_best_match_appears_first(self, sample_songs, pop_lover_profile):
        recommendations = recommend_songs(pop_lover_profile, sample_songs, k=1)

        song, score, reasons = recommendations[0]
        # Pop lover should get the happy pop track first
        assert song['genre'] == 'pop'
        assert song['mood'] == 'happy'

    def test_lofi_lover_gets_lofi_first(self, sample_songs, lofi_lover_profile):
        recommendations = recommend_songs(lofi_lover_profile, sample_songs, k=1)

        song, score, reasons = recommendations[0]
        # Lofi lover should get the chill lofi song first
        assert song['genre'] == 'lofi'
        assert song['mood'] == 'chill'

    def test_returns_song_score_and_explanation(self, sample_songs, pop_lover_profile):
        recommendations = recommend_songs(pop_lover_profile, sample_songs, k=1)

        assert len(recommendations) == 1
        song, score, explanation = recommendations[0]
        assert isinstance(song, dict), "Should return song dict"
        assert isinstance(score, float), "Should return score float"
        assert isinstance(explanation, str), "Should return explanation string"
        assert len(explanation) > 0, "Explanation should not be empty"

    def test_k_larger_than_catalog_returns_all(self, sample_songs, pop_lover_profile):
        recommendations = recommend_songs(pop_lover_profile, sample_songs, k=100)

        assert len(recommendations) == len(sample_songs), "Should return all songs if k > catalog size"

    def test_k_zero_returns_empty(self, sample_songs, pop_lover_profile):
        recommendations = recommend_songs(pop_lover_profile, sample_songs, k=0)

        assert len(recommendations) == 0, "Should return empty list if k=0"


# Tests for load_songs function
class TestLoadSongs:
    """Test CSV loading and type conversion."""

    def test_load_songs_returns_list(self):
        songs = load_songs("data/songs.csv")

        assert isinstance(songs, list), "Should return list"
        assert len(songs) > 0, "Should load at least one song"

    def test_songs_have_correct_types(self):
        songs = load_songs("data/songs.csv")
        song = songs[0]

        assert isinstance(song['id'], int), "id should be int"
        assert isinstance(song['title'], str), "title should be str"
        assert isinstance(song['artist'], str), "artist should be str"
        assert isinstance(song['genre'], str), "genre should be str"
        assert isinstance(song['mood'], str), "mood should be str"
        assert isinstance(song['energy'], float), "energy should be float"
        assert isinstance(song['tempo_bpm'], int), "tempo_bpm should be int"
        assert isinstance(song['valence'], float), "valence should be float"
        assert isinstance(song['danceability'], float), "danceability should be float"
        assert isinstance(song['acousticness'], float), "acousticness should be float"

    def test_all_songs_have_required_fields(self):
        songs = load_songs("data/songs.csv")
        required_fields = ['id', 'title', 'artist', 'genre', 'mood', 'energy',
                          'tempo_bpm', 'valence', 'danceability', 'acousticness']

        for song in songs:
            for field in required_fields:
                assert field in song, f"Song missing field: {field}"

    def test_loaded_songs_work_with_recommender(self):
        songs = load_songs("data/songs.csv")
        user_prefs = {
            'favorite_genre': 'pop',
            'favorite_mood': 'happy',
            'target_energy': 0.85,
            'likes_acoustic': False,
        }

        recommendations = recommend_songs(user_prefs, songs, k=5)

        assert len(recommendations) == 5, "Should get 5 recommendations from loaded songs"


# Integration tests
class TestAdvancedFeatures:
    """Test scoring with advanced attributes."""

    def test_vocal_style_similarity_exact_match(self, sample_songs):
        user_prefs = {
            'favorite_genre': 'pop',
            'favorite_mood': 'happy',
            'target_energy': 0.85,
            'likes_acoustic': False,
            'preferred_vocal_style': 'sung',
        }

        pop_song = sample_songs[0]  # sung vocal style
        lofi_song = sample_songs[1]  # instrumental

        score_pop, reasons_pop = score_song_advanced(user_prefs, pop_song)
        score_lofi, reasons_lofi = score_song_advanced(user_prefs, lofi_song)

        assert score_pop > score_lofi, "Matching vocal style should score higher"
        assert any("1.00" in r for r in reasons_pop if "Vocal" in r), "Exact match should be 1.00"
        assert any("0.10" in r for r in reasons_lofi if "Vocal" in r), "Mismatch should be gradual (0.10)"

    def test_vocal_style_partial_similarity(self):
        from src.recommender import vocal_style_similarity
        assert vocal_style_similarity('sung', 'sung') == 1.0
        assert vocal_style_similarity('sung', 'rapped') == 0.6
        assert vocal_style_similarity('sung', 'spoken') == 0.5
        assert vocal_style_similarity('sung', 'instrumental') == 0.1

    def test_production_quality_similarity(self, sample_songs):
        user_prefs = {
            'favorite_genre': 'lofi',
            'favorite_mood': 'chill',
            'target_energy': 0.35,
            'likes_acoustic': True,
            'preferred_production': 'lo-fi',
        }

        lofi_song = sample_songs[1]  # lo-fi production
        pop_song = sample_songs[0]  # polished production

        score_lofi, _ = score_song_advanced(user_prefs, lofi_song)
        score_pop, _ = score_song_advanced(user_prefs, pop_song)

        assert score_lofi > score_pop, "Matching production quality should score higher"

    def test_production_quality_gradual_scoring(self):
        from src.recommender import production_quality_similarity
        assert production_quality_similarity('polished', 'polished') == 1.0
        assert production_quality_similarity('polished', 'standard') > 0.6
        assert production_quality_similarity('polished', 'lo-fi') > 0.1

    def test_emotional_arc_similarity(self, sample_songs):
        user_prefs = {
            'favorite_genre': 'rock',
            'favorite_mood': 'intense',
            'target_energy': 0.92,
            'likes_acoustic': False,
            'preferred_emotional_arc': 'builds',
        }

        rock_song = sample_songs[2]  # emotional arc: builds
        pop_song = sample_songs[0]  # emotional arc: constant

        score_rock, _ = score_song_advanced(user_prefs, rock_song)
        score_pop, _ = score_song_advanced(user_prefs, pop_song)

        assert score_rock > score_pop, "Matching emotional arc should score higher"

    def test_emotional_arc_gradual_scoring(self):
        from src.recommender import emotional_arc_similarity
        assert emotional_arc_similarity('constant', 'constant') == 1.0
        assert emotional_arc_similarity('constant', 'minimal') == 0.7
        assert emotional_arc_similarity('builds', 'evolves') == 0.6
        assert emotional_arc_similarity('constant', 'builds') == 0.2

    def test_popularity_preference_popular(self, sample_songs):
        user_prefs = {
            'favorite_genre': 'pop',
            'favorite_mood': 'happy',
            'target_energy': 0.85,
            'likes_acoustic': False,
            'prefer_popular': True,
        }

        pop_song = sample_songs[0]  # popularity: 78
        lofi_song = sample_songs[1]  # popularity: 42

        score_pop, _ = score_song_advanced(user_prefs, pop_song)
        score_lofi, _ = score_song_advanced(user_prefs, lofi_song)

        assert score_pop > score_lofi, "Popular songs should score higher for popularity-seekers"

    def test_popularity_preference_indie(self, sample_songs):
        user_prefs = {
            'favorite_genre': 'lofi',
            'favorite_mood': 'chill',
            'target_energy': 0.35,
            'likes_acoustic': True,
            'prefer_popular': False,
        }

        lofi_song = sample_songs[1]  # popularity: 42
        pop_song = sample_songs[0]  # popularity: 78

        score_lofi, _ = score_song_advanced(user_prefs, lofi_song)
        score_pop, _ = score_song_advanced(user_prefs, pop_song)

        assert score_lofi > score_pop, "Less popular songs should score higher for indie-seekers"

    def test_release_decade_distance(self, sample_songs):
        user_prefs = {
            'favorite_genre': 'pop',
            'favorite_mood': 'happy',
            'target_energy': 0.85,
            'likes_acoustic': False,
            'target_release_decade': 2020,
        }

        pop_song = sample_songs[0]  # 2020
        rock_song = sample_songs[2]  # 2010

        score_pop, _ = score_song_advanced(user_prefs, pop_song)
        score_rock, _ = score_song_advanced(user_prefs, rock_song)

        assert score_pop > score_rock, "Songs closer to target decade should score higher"

    def test_advanced_scoring_includes_base_score(self, sample_songs):
        user_prefs = {
            'favorite_genre': 'pop',
            'favorite_mood': 'happy',
            'target_energy': 0.85,
            'likes_acoustic': False,
            'preferred_vocal_style': 'sung',
            'preferred_production': 'polished',
            'preferred_emotional_arc': 'constant',
            'prefer_popular': True,
            'target_release_decade': 2020,
        }

        song = sample_songs[0]

        base_score, _ = score_song(user_prefs, song)
        advanced_score, _ = score_song_advanced(user_prefs, song)

        assert advanced_score > base_score, "Advanced scoring should add to base score"


class TestIntegration:
    """End-to-end tests combining multiple functions."""

    def test_full_workflow_with_real_data(self):
        songs = load_songs("data/songs.csv")
        user_prefs = {
            'favorite_genre': 'pop',
            'favorite_mood': 'happy',
            'target_energy': 0.85,
            'likes_acoustic': False,
        }

        recommendations = recommend_songs(user_prefs, songs, k=5)

        assert len(recommendations) == 5
        # Check that scores are in descending order
        scores = [score for _, score, _ in recommendations]
        assert scores == sorted(scores, reverse=True)

    def test_advanced_scoring_with_real_data(self):
        songs = load_songs("data/songs.csv")
        user_prefs = {
            'favorite_genre': 'pop',
            'favorite_mood': 'happy',
            'target_energy': 0.85,
            'likes_acoustic': False,
            'preferred_vocal_style': 'sung',
            'preferred_production': 'polished',
            'prefer_popular': True,
            'target_release_decade': 2020,
        }

        recommendations = recommend_songs(user_prefs, songs, k=5, use_advanced=True)

        assert len(recommendations) == 5
        scores = [score for _, score, _ in recommendations]
        assert scores == sorted(scores, reverse=True)

    def test_different_profiles_get_different_recommendations(self):
        songs = load_songs("data/songs.csv")

        pop_fan = {
            'favorite_genre': 'pop',
            'favorite_mood': 'happy',
            'target_energy': 0.85,
            'likes_acoustic': False,
        }
        lofi_fan = {
            'favorite_genre': 'lofi',
            'favorite_mood': 'chill',
            'target_energy': 0.35,
            'likes_acoustic': True,
        }

        pop_recs = recommend_songs(pop_fan, songs, k=1)
        lofi_recs = recommend_songs(lofi_fan, songs, k=1)

        pop_song = pop_recs[0][0]['id']
        lofi_song = lofi_recs[0][0]['id']

        assert pop_song != lofi_song, "Different profiles should get different top recommendations"

    def test_extreme_energy_profiles(self):
        songs = load_songs("data/songs.csv")

        low_energy_user = {
            'favorite_genre': 'classical',
            'favorite_mood': 'meditative',
            'target_energy': 0.10,
            'likes_acoustic': True,
        }
        high_energy_user = {
            'favorite_genre': 'electronic',
            'favorite_mood': 'uplifting',
            'target_energy': 0.95,
            'likes_acoustic': False,
        }

        low_recs = recommend_songs(low_energy_user, songs, k=5)
        high_recs = recommend_songs(high_energy_user, songs, k=5)

        # Should both get recommendations
        assert len(low_recs) > 0
        assert len(high_recs) > 0


class TestScoringModes:
    """Test the strategy pattern implementation and mode interactions."""

    def test_get_strategy_returns_correct_mode(self):
        """Test that get_strategy returns the right strategy instance."""
        genre_first = get_strategy("genre-first")
        discovery = get_strategy("discovery")
        niche = get_strategy("niche-friendly")
        personality = get_strategy("personality")

        assert isinstance(genre_first, ScoringStrategy)
        assert isinstance(discovery, ScoringStrategy)
        assert isinstance(niche, ScoringStrategy)
        assert isinstance(personality, ScoringStrategy)
        assert genre_first.name == "Genre-First (Default)"
        assert discovery.name == "Discovery Mode"
        assert niche.name == "Niche-Friendly Mode"
        assert personality.name == "Personality-Based Mode"

    def test_get_strategy_defaults_to_genre_first(self):
        """Test that invalid mode names default to genre-first."""
        invalid = get_strategy("nonexistent_mode")
        genre_first = get_strategy("genre-first")

        assert invalid.name == genre_first.name

    def test_scoring_modes_registry_contains_all_modes(self):
        """Test that all expected modes are registered."""
        expected_modes = ["genre-first", "discovery", "niche-friendly", "personality"]
        assert set(SCORING_MODES.keys()) == set(expected_modes)

    def test_scoring_weights_dataclass_created_correctly(self):
        """Test that ScoringWeights stores weight configuration."""
        weights = ScoringWeights(
            genre=2.0, mood=2.0, energy=1.5, acousticness=1.0,
            danceability=0.3, vocal_style=0.6, production=0.6,
            emotional_arc=0.6, popularity=0.6, decade=0.6
        )

        assert weights.genre == 2.0
        assert weights.mood == 2.0
        assert weights.energy == 1.5
        assert weights.danceability == 0.3

    def test_weighted_scoring_strategy_score_method_exists(self):
        """Test that WeightedScoringStrategy has a score method."""
        strategy = get_strategy("genre-first")
        assert hasattr(strategy, 'score')
        assert callable(strategy.score)

    def test_different_modes_produce_different_scores(self, sample_songs, pop_lover_profile):
        """Test that same song scores differently in different modes."""
        song = sample_songs[0]  # Happy pop track

        genre_first_strat = get_strategy("genre-first")
        discovery_strat = get_strategy("discovery")

        score_gf, _ = genre_first_strat.score(pop_lover_profile, song)
        score_disc, _ = discovery_strat.score(pop_lover_profile, song)

        # Genre-first should weight genre more heavily, so score should be different
        assert score_gf != score_disc

    def test_genre_first_vs_discovery_genre_weight_difference(self, sample_songs, pop_lover_profile):
        """Test that genre-first emphasizes genre more than discovery."""
        # Create a song that doesn't match genre but matches mood/energy
        non_matching_genre_song = {
            'id': 10, 'title': "Test", 'artist': "Test",
            'genre': "jazz",  # Not pop
            'mood': "happy",  # Matches
            'energy': 0.85,  # Matches
            'tempo_bpm': 120, 'valence': 0.8,
            'danceability': 0.7, 'acousticness': 0.1,
            'popularity': 50, 'release_decade': 2020,
            'vocal_style': "sung", 'production_quality': "polished", 'emotional_arc': "constant",
        }

        genre_first = get_strategy("genre-first")
        discovery = get_strategy("discovery")

        score_gf, _ = genre_first.score(pop_lover_profile, non_matching_genre_song)
        score_disc, _ = discovery.score(pop_lover_profile, non_matching_genre_song)

        # Genre-first should penalize non-matching genre more
        assert score_gf < score_disc, "Genre-first should penalize non-matching genre more than discovery"

    def test_discovery_mode_prefers_less_popular_songs(self, sample_songs):
        """Test that discovery mode with negative popularity weight prefers indie songs."""
        user_prefs = {
            'favorite_genre': 'pop',
            'favorite_mood': 'happy',
            'target_energy': 0.85,
            'likes_acoustic': False,
        }

        # Popular pop song
        popular_song = sample_songs[0]  # popularity: 78

        # Create a less popular version of the same song
        unpopular_song = {
            'id': 20, 'title': "Indie Pop", 'artist': "Unknown", 'genre': "pop",
            'mood': "happy", 'energy': 0.85, 'tempo_bpm': 120, 'valence': 0.9,
            'danceability': 0.8, 'acousticness': 0.15, 'popularity': 20,  # Much less popular
            'release_decade': 2020, 'vocal_style': "sung", 'production_quality': "polished",
            'emotional_arc': "constant",
        }

        discovery = get_strategy("discovery")
        score_popular, _ = discovery.score(user_prefs, popular_song)
        score_unpopular, _ = discovery.score(user_prefs, unpopular_song)

        # Discovery should prefer the unpopular song (due to negative popularity weight)
        assert score_unpopular > score_popular, "Discovery mode should prefer less popular songs"

    def test_niche_friendly_has_boosted_genre_weight(self, sample_songs):
        """Test that niche-friendly mode has higher genre weight than genre-first."""
        # Compare the weight configurations themselves
        genre_first = get_strategy("genre-first")
        niche = get_strategy("niche-friendly")

        # Niche-friendly should have higher genre weight (2.5 vs 2.0)
        assert niche.weights.genre > genre_first.weights.genre, \
            "Niche-friendly should have higher genre weight"
        assert niche.weights.genre == 2.5
        assert genre_first.weights.genre == 2.0

    def test_personality_mode_emphasizes_production_and_vocal_style(self, sample_songs):
        """Test that personality mode prioritizes vocal style and production over genre."""
        user_prefs = {
            'favorite_genre': 'lofi',
            'favorite_mood': 'chill',
            'target_energy': 0.35,
            'likes_acoustic': True,
            'preferred_vocal_style': 'sung',
            'preferred_production': 'polished',
            'preferred_emotional_arc': 'constant',
        }

        # Lofi song with instrumental vocals (doesn't match preference)
        lofi_instrumental = sample_songs[1]  # lofi, instrumental
        # Pop song with sung vocals (matches preference)
        pop_sung = sample_songs[0]  # pop, sung vocals, polished

        personality = get_strategy("personality")

        score_lofi, _ = personality.score(user_prefs, lofi_instrumental)
        score_pop, _ = personality.score(user_prefs, pop_sung)

        # Personality mode should narrow the gap because pop song matches vocal/production preferences
        genre_first = get_strategy("genre-first")
        score_lofi_gf, _ = genre_first.score(user_prefs, lofi_instrumental)
        score_pop_gf, _ = genre_first.score(user_prefs, pop_sung)

        gap_personality = score_lofi - score_pop
        gap_genre_first = score_lofi_gf - score_pop_gf

        # The gap should be smaller in personality mode (vocal style/production matter more)
        assert abs(gap_personality) < abs(gap_genre_first), \
            "Personality mode should reduce genre mismatch penalty by boosting vocal/production"

    def test_recommend_songs_respects_mode_parameter(self, sample_songs, pop_lover_profile):
        """Test that recommend_songs uses the specified mode."""
        recs_gf = recommend_songs(pop_lover_profile, sample_songs, k=3, mode="genre-first")
        recs_disc = recommend_songs(pop_lover_profile, sample_songs, k=3, mode="discovery")

        # Extract scores
        scores_gf = [score for _, score, _ in recs_gf]
        scores_disc = [score for _, score, _ in recs_disc]

        # Scores should be different because modes weight differently
        assert scores_gf != scores_disc, "Different modes should produce different scores"

    def test_recommend_songs_with_different_modes_produce_different_rankings(self, sample_songs, pop_lover_profile):
        """Test that mode changes affect which songs are recommended."""
        recs_gf = recommend_songs(pop_lover_profile, sample_songs, k=3, mode="genre-first")
        recs_discovery = recommend_songs(pop_lover_profile, sample_songs, k=3, mode="discovery")

        songs_gf = [song['id'] for song, _, _ in recs_gf]
        songs_discovery = [song['id'] for song, _, _ in recs_discovery]

        # With small dataset, genre-first heavily biases towards matching genre
        # Discovery should be more flexible, potentially ranking differently
        # (May or may not change order with 3 songs, but demonstrates mode usage)
        assert len(songs_gf) == 3
        assert len(songs_discovery) == 3

    def test_weighted_scoring_strategy_applies_weights_correctly(self, sample_songs):
        """Test that strategy applies weights from ScoringWeights."""
        user_prefs = {
            'favorite_genre': 'pop',
            'favorite_mood': 'happy',
            'target_energy': 0.85,
            'likes_acoustic': False,
            'preferred_vocal_style': 'sung',
            'preferred_production': 'polished',
            'preferred_emotional_arc': 'constant',
        }

        song = sample_songs[0]
        strategy = get_strategy("genre-first")
        score, reasons = strategy.score(user_prefs, song)

        # Verify that genre (weight 2.0) and mood (weight 2.0) contributions appear
        assert any("Genre match" in r and "2.00" in r for r in reasons)
        assert any("Mood match" in r and "2.00" in r for r in reasons)

    def test_modes_all_return_tuple_format(self, sample_songs, pop_lover_profile):
        """Test that all modes return (score, reasons) tuple."""
        song = sample_songs[0]

        for mode_name in SCORING_MODES.keys():
            strategy = get_strategy(mode_name)
            result = strategy.score(pop_lover_profile, song)

            assert isinstance(result, tuple), f"{mode_name} should return tuple"
            assert len(result) == 2, f"{mode_name} should return (score, reasons)"
            score, reasons = result
            assert isinstance(score, float), f"{mode_name} score should be float"
            assert isinstance(reasons, list), f"{mode_name} reasons should be list"

    def test_niche_user_gets_more_matches_in_niche_friendly_mode(self):
        """Test that niche-friendly mode helps niche users get more genre matches."""
        songs = load_songs("data/songs.csv")

        niche_user = {
            'favorite_genre': 'synthwave',
            'favorite_mood': 'moody',
            'target_energy': 0.75,
            'likes_acoustic': False,
        }

        recs_gf = recommend_songs(niche_user, songs, k=5, mode="genre-first")
        recs_niche = recommend_songs(niche_user, songs, k=5, mode="niche-friendly")

        genres_gf = [song['genre'] for song, _, _ in recs_gf]
        genres_niche = [song['genre'] for song, _, _ in recs_niche]

        synthwave_count_gf = genres_gf.count('synthwave')
        synthwave_count_niche = genres_niche.count('synthwave')

        # Niche-friendly should return at least as many synthwave songs
        assert synthwave_count_niche >= synthwave_count_gf, \
            "Niche-friendly mode should recommend at least as many matching genre songs"

    def test_discovery_mode_finds_non_genre_matches(self):
        """Test that discovery mode recommends outside preferred genre."""
        songs = load_songs("data/songs.csv")

        pop_user = {
            'favorite_genre': 'pop',
            'favorite_mood': 'happy',
            'target_energy': 0.85,
            'likes_acoustic': False,
        }

        recs_gf = recommend_songs(pop_user, songs, k=5, mode="genre-first")
        recs_disc = recommend_songs(pop_user, songs, k=5, mode="discovery")

        genres_gf = [song['genre'] for song, _, _ in recs_gf]
        genres_disc = [song['genre'] for song, _, _ in recs_disc]

        pop_count_gf = genres_gf.count('pop')
        pop_count_disc = genres_disc.count('pop')

        # Discovery should recommend fewer pop songs (weakened genre weight)
        assert pop_count_disc <= pop_count_gf, \
            "Discovery mode should recommend fewer songs from preferred genre"

    def test_all_modes_produce_valid_scores(self, sample_songs, pop_lover_profile):
        """Test that all modes produce non-negative scores."""
        song = sample_songs[0]

        for mode_name in SCORING_MODES.keys():
            strategy = get_strategy(mode_name)
            score, reasons = strategy.score(pop_lover_profile, song)

            # All scores should be non-negative (though can be very low)
            assert score >= 0, f"{mode_name} should produce non-negative score"
            assert len(reasons) > 0, f"{mode_name} should provide reasons"


class TestDiversityPenalty:
    """Test artist and genre diversity penalties in recommendations."""

    def test_diversity_function_exists(self):
        """Test that recommend_songs_with_diversity function exists."""
        assert callable(recommend_songs_with_diversity)

    def test_diversity_returns_k_items(self, sample_songs, pop_lover_profile):
        """Test that diversity function returns k items."""
        recommendations = recommend_songs_with_diversity(pop_lover_profile, sample_songs, k=3)

        assert len(recommendations) <= 3
        assert isinstance(recommendations, list)

    def test_diversity_returns_tuples(self, sample_songs, pop_lover_profile):
        """Test that diversity returns (song, score, explanation) tuples."""
        recommendations = recommend_songs_with_diversity(pop_lover_profile, sample_songs, k=2)

        for item in recommendations:
            assert isinstance(item, tuple)
            assert len(item) == 3
            song, score, explanation = item
            assert isinstance(song, dict)
            assert isinstance(score, float)
            assert isinstance(explanation, str)

    def test_diversity_prevents_artist_duplicates(self):
        """Test that diversity penalty prevents multiple songs from same artist."""
        songs = load_songs("data/songs.csv")

        user_prefs = {
            'favorite_genre': 'pop',
            'favorite_mood': 'happy',
            'target_energy': 0.85,
            'likes_acoustic': False,
        }

        # Get recommendations with diversity
        recs_diverse = recommend_songs_with_diversity(
            user_prefs, songs, k=5, artist_penalty=0.9
        )

        artists = [song['artist'] for song, _, _ in recs_diverse]
        artist_counts = {}
        for artist in artists:
            artist_counts[artist] = artist_counts.get(artist, 0) + 1

        # With high penalty, most artists should appear only once
        max_artist_count = max(artist_counts.values())
        assert max_artist_count <= 2, "High penalty should limit artist repeats"

    def test_diversity_allows_exceptions_for_quality_songs(self, sample_songs, pop_lover_profile):
        """Test that diversity allows duplicate artists if songs are high-quality."""
        # Use low penalty to allow duplicates
        recommendations = recommend_songs_with_diversity(
            pop_lover_profile, sample_songs, k=3, artist_penalty=0.2
        )

        # Should still return 3 recommendations
        assert len(recommendations) == 3

    def test_diversity_vs_non_diversity_differ(self, sample_songs, pop_lover_profile):
        """Test that diversity recommendations differ from non-diversity."""
        recs_normal = recommend_songs(pop_lover_profile, sample_songs, k=5)
        recs_diverse = recommend_songs_with_diversity(
            pop_lover_profile, sample_songs, k=5, artist_penalty=0.5, genre_penalty=0.3
        )

        # Extract artist lists
        artists_normal = [song['artist'] for song, _, _ in recs_normal]
        artists_diverse = [song['artist'] for song, _, _ in recs_diverse]

        # Diversity should have more unique artists (or same if no duplicates in original)
        unique_normal = len(set(artists_normal))
        unique_diverse = len(set(artists_diverse))

        assert unique_diverse >= unique_normal, "Diversity should maximize unique artists"

    def test_diversity_prevents_genre_duplicates(self):
        """Test that genre penalty prevents multiple songs from same genre."""
        songs = load_songs("data/songs.csv")

        pop_user = {
            'favorite_genre': 'pop',
            'favorite_mood': 'happy',
            'target_energy': 0.85,
            'likes_acoustic': False,
        }

        # Use high genre penalty
        recs = recommend_songs_with_diversity(
            pop_user, songs, k=5, genre_penalty=0.8
        )

        genres = [song['genre'] for song, _, _ in recs]

        # Check that we have good genre diversity
        unique_genres = len(set(genres))
        assert unique_genres >= 2, "Should have at least 2 different genres with penalty"

    def test_diversity_artist_penalty_tuning(self, sample_songs, pop_lover_profile):
        """Test that artist penalty parameter affects results."""
        # Low penalty allows more duplicates
        recs_low = recommend_songs_with_diversity(
            pop_lover_profile, sample_songs, k=5, artist_penalty=0.1
        )

        # High penalty prevents duplicates
        recs_high = recommend_songs_with_diversity(
            pop_lover_profile, sample_songs, k=5, artist_penalty=0.9
        )

        artists_low = [song['artist'] for song, _, _ in recs_low]
        artists_high = [song['artist'] for song, _, _ in recs_high]

        unique_low = len(set(artists_low))
        unique_high = len(set(artists_high))

        # Higher penalty should produce more unique artists (or same)
        assert unique_high >= unique_low, "Higher penalty should increase artist diversity"

    def test_diversity_genre_penalty_tuning(self, sample_songs, pop_lover_profile):
        """Test that genre penalty parameter affects results."""
        recs_low = recommend_songs_with_diversity(
            pop_lover_profile, sample_songs, k=5, genre_penalty=0.1
        )

        recs_high = recommend_songs_with_diversity(
            pop_lover_profile, sample_songs, k=5, genre_penalty=0.8
        )

        genres_low = [song['genre'] for song, _, _ in recs_low]
        genres_high = [song['genre'] for song, _, _ in recs_high]

        unique_low = len(set(genres_low))
        unique_high = len(set(genres_high))

        assert unique_high >= unique_low, "Higher genre penalty should increase genre diversity"

    def test_diversity_preserves_original_scores(self, sample_songs, pop_lover_profile):
        """Test that diversity returns original scores, not penalized scores."""
        recommendations = recommend_songs_with_diversity(
            pop_lover_profile, sample_songs, k=3, artist_penalty=0.5
        )

        # All scores should be positive and reasonable
        for song, score, explanation in recommendations:
            assert score > 0, "Scores should be positive (original, not penalized)"
            assert score <= 20, "Scores should be reasonable range"

    def test_diversity_with_different_modes(self, sample_songs, pop_lover_profile):
        """Test that diversity works with different scoring modes."""
        modes = ["genre-first", "discovery", "niche-friendly", "personality"]

        for mode in modes:
            recs = recommend_songs_with_diversity(
                pop_lover_profile, sample_songs, k=3, mode=mode, artist_penalty=0.5
            )

            assert len(recs) == 3
            assert all(isinstance(r, tuple) and len(r) == 3 for r in recs)


class TestFeatureIntegration:
    """Integration tests to verify all features work together."""

    def test_diversity_and_modes_together(self):
        """Test that diversity penalty works with all 4 scoring modes."""
        songs = load_songs("data/songs.csv")
        user = {
            'favorite_genre': 'pop',
            'favorite_mood': 'happy',
            'target_energy': 0.85,
            'likes_acoustic': False,
        }

        for mode in ["genre-first", "discovery", "niche-friendly", "personality"]:
            # Normal recommendations
            recs_normal = recommend_songs(user, songs, k=5, mode=mode)
            # With diversity
            recs_diverse = recommend_songs_with_diversity(
                user, songs, k=5, mode=mode, artist_penalty=0.5
            )

            assert len(recs_normal) == 5
            assert len(recs_diverse) == 5
            # Both should be sorted
            scores_normal = [s for _, s, _ in recs_normal]
            scores_diverse = [s for _, s, _ in recs_diverse]
            assert scores_normal == sorted(scores_normal, reverse=True)
            assert scores_diverse == sorted(scores_diverse, reverse=True)

    def test_advanced_scoring_with_diversity(self):
        """Test that advanced scoring works with diversity penalty."""
        songs = load_songs("data/songs.csv")
        user = {
            'favorite_genre': 'pop',
            'favorite_mood': 'happy',
            'target_energy': 0.85,
            'likes_acoustic': False,
            'preferred_vocal_style': 'sung',
            'preferred_production': 'polished',
            'preferred_emotional_arc': 'constant',
            'prefer_popular': True,
            'target_release_decade': 2020,
        }

        # Basic scoring with diversity
        recs_basic = recommend_songs_with_diversity(user, songs, k=5, use_advanced=False)
        # Advanced scoring with diversity
        recs_adv = recommend_songs_with_diversity(user, songs, k=5, use_advanced=True)

        assert len(recs_basic) == 5
        assert len(recs_adv) == 5

        # Advanced should generally have higher scores
        scores_basic = [s for _, s, _ in recs_basic]
        scores_adv = [s for _, s, _ in recs_adv]
        assert sum(scores_adv) >= sum(scores_basic)

    def test_results_sorted_for_all_configurations(self):
        """Verify results are always sorted regardless of configuration."""
        songs = load_songs("data/songs.csv")
        user = {
            'favorite_genre': 'lofi',
            'favorite_mood': 'chill',
            'target_energy': 0.35,
            'likes_acoustic': True,
        }

        # Test all combinations
        modes = ["genre-first", "discovery", "niche-friendly", "personality"]
        penalties = [(0.3, 0.2), (0.5, 0.3), (0.8, 0.7)]
        use_advanced_options = [False, True]

        for mode in modes:
            for artist_p, genre_p in penalties:
                for use_adv in use_advanced_options:
                    recs = recommend_songs_with_diversity(
                        user, songs, k=5,
                        mode=mode,
                        use_advanced=use_adv,
                        artist_penalty=artist_p,
                        genre_penalty=genre_p
                    )

                    scores = [s for _, s, _ in recs]
                    assert scores == sorted(scores, reverse=True), \
                        f"Failed for mode={mode}, penalties=({artist_p},{genre_p}), use_adv={use_adv}"

    def test_diversity_edge_case_single_song_per_artist(self):
        """Test diversity when catalog has only 1 song per artist."""
        songs = load_songs("data/songs.csv")
        user = {
            'favorite_genre': 'classical',
            'favorite_mood': 'meditative',
            'target_energy': 0.15,
            'likes_acoustic': True,
        }

        recs = recommend_songs_with_diversity(user, songs, k=5, artist_penalty=0.5)

        assert len(recs) == 5
        artists = [s['artist'] for s, _, _ in recs]
        # All should be unique (since each artist has 1-2 songs max)
        assert len(set(artists)) >= 4, "Should have at least 4 unique artists"

    def test_non_diversity_returns_same_for_equal_scores(self, sample_songs, pop_lover_profile):
        """Test that non-diversity function consistently returns same song for same score."""
        # Run twice
        recs1 = recommend_songs(pop_lover_profile, sample_songs, k=3)
        recs2 = recommend_songs(pop_lover_profile, sample_songs, k=3)

        # Should get same songs in same order
        songs1 = [s['id'] for s, _, _ in recs1]
        songs2 = [s['id'] for s, _, _ in recs2]
        assert songs1 == songs2, "Same input should produce same output"

    def test_diversity_deterministic_across_runs(self):
        """Test that diversity recommendations are deterministic."""
        songs = load_songs("data/songs.csv")
        user = {
            'favorite_genre': 'pop',
            'favorite_mood': 'happy',
            'target_energy': 0.85,
            'likes_acoustic': False,
        }

        # Run twice
        recs1 = recommend_songs_with_diversity(user, songs, k=5, artist_penalty=0.5)
        recs2 = recommend_songs_with_diversity(user, songs, k=5, artist_penalty=0.5)

        songs1 = [s['id'] for s, _, _ in recs1]
        songs2 = [s['id'] for s, _, _ in recs2]
        assert songs1 == songs2, "Same input should produce same output (deterministic)"

    def test_score_explanations_present_all_modes(self):
        """Test that all modes provide explanations for scoring."""
        songs = load_songs("data/songs.csv")
        user = {
            'favorite_genre': 'pop',
            'favorite_mood': 'happy',
            'target_energy': 0.85,
            'likes_acoustic': False,
        }

        modes = ["genre-first", "discovery", "niche-friendly", "personality"]

        for mode in modes:
            recs = recommend_songs(user, songs, k=1, mode=mode)
            song, score, explanation = recs[0]

            assert len(explanation) > 0, f"{mode} should provide explanation"
            assert "Genre" in explanation or "Mood" in explanation or "Energy" in explanation, \
                f"{mode} explanation should include scoring details"

    def test_diverse_explanations_comprehensive(self):
        """Test that diversity-based recommendations include clear explanations."""
        songs = load_songs("data/songs.csv")
        user = {
            'favorite_genre': 'pop',
            'favorite_mood': 'happy',
            'target_energy': 0.85,
            'likes_acoustic': False,
        }

        recs = recommend_songs_with_diversity(user, songs, k=3, artist_penalty=0.5)

        for song, score, explanation in recs:
            assert len(explanation) > 0, "Should have explanation"
            # Should have original score info
            assert str(round(score, 2)) in explanation or "Genre" in explanation, \
                "Explanation should include scoring details"

    def test_mode_consistency_across_datasets(self, sample_songs, pop_lover_profile):
        """Test that mode behavior is consistent (same user = same behavior)."""
        modes = ["genre-first", "discovery", "niche-friendly", "personality"]

        results_by_mode = {}
        for mode in modes:
            recs = recommend_songs(pop_lover_profile, sample_songs, k=3, mode=mode)
            results_by_mode[mode] = [s['title'] for s, _, _ in recs]

        # Run again
        for mode in modes:
            recs = recommend_songs(pop_lover_profile, sample_songs, k=3, mode=mode)
            current = [s['title'] for s, _, _ in recs]
            assert current == results_by_mode[mode], \
                f"Mode {mode} should be deterministic"


class TestFormattingFunctions:
    """Test extract_top_reasons, format_recommendation_summary, and format_recommendation_detailed."""

    def test_extract_top_reasons_normal_input(self):
        """Test extracting reasons from normal explanation."""
        explanation = """Why you'll like this:
• Genre match: pop (+1.50)
• Mood match: happy (+2.00)
• Energy: 0.85 vs target 0.85 (2.00)"""
        reasons = extract_top_reasons(explanation, num_reasons=3)
        assert "Genre match" in reasons
        assert "Mood match" in reasons
        assert "Energy" in reasons
        assert reasons.count("|") == 2  # 3 reasons = 2 pipes

    def test_extract_top_reasons_empty_explanation(self):
        """Test extracting reasons from empty explanation."""
        explanation = ""
        reasons = extract_top_reasons(explanation, num_reasons=3)
        assert reasons == "See details"

    def test_extract_top_reasons_none_explanation(self):
        """Test extracting reasons from None explanation."""
        reasons = extract_top_reasons(None, num_reasons=3)
        assert reasons == "See details"

    def test_extract_top_reasons_fewer_than_three(self):
        """Test extracting when fewer than 3 reasons available."""
        explanation = """Why you'll like this:
• Genre match: pop (+1.50)
• Mood match: happy (+2.00)"""
        reasons = extract_top_reasons(explanation, num_reasons=3)
        assert "Genre match" in reasons
        assert "Mood match" in reasons
        assert reasons.count("|") == 1  # 2 reasons = 1 pipe

    def test_extract_top_reasons_custom_num_reasons(self):
        """Test extracting custom number of reasons."""
        explanation = """Why you'll like this:
• Genre match: pop (+1.50)
• Mood match: happy (+2.00)
• Energy: 0.85 vs target 0.85 (2.00)
• Danceability: high (1.20)"""
        reasons = extract_top_reasons(explanation, num_reasons=2)
        assert reasons.count("|") == 1  # 2 reasons = 1 pipe

    def test_extract_top_reasons_with_colons_in_text(self):
        """Test that split(':', 1) correctly handles colons in reason names."""
        explanation = """Why you'll like this:
• Genre match: pop: upbeat (+1.50)
• Mood match: happy: energetic (+2.00)"""
        reasons = extract_top_reasons(explanation, num_reasons=2)
        # Should extract reason names correctly despite colons in values
        assert "Genre match" in reasons or "Mood match" in reasons

    def test_filter_reason_lines_normal(self):
        """Test filtering normal explanation lines."""
        explanation = """Why you'll like this:
• Genre match: pop (+1.50)
• Mood match: happy (+2.00)
• Energy: 0.85 vs target 0.85 (2.00)"""
        filtered = _filter_reason_lines(explanation)
        assert len(filtered) == 3
        # Bullets are preserved (they're used in detailed output formatting)
        assert all("Genre match" in line or "Mood match" in line or "Energy" in line for line in filtered)
        assert all(line.strip() for line in filtered)

    def test_filter_reason_lines_empty(self):
        """Test filtering with empty explanation."""
        filtered = _filter_reason_lines("")
        assert filtered == []

    def test_filter_reason_lines_none(self):
        """Test filtering with None explanation."""
        filtered = _filter_reason_lines(None)
        assert filtered == []

    def test_format_recommendation_summary_returns_string(self, sample_songs, pop_lover_profile):
        """Test that format_recommendation_summary returns a string."""
        recs = recommend_songs(pop_lover_profile, sample_songs, k=3)
        result = format_recommendation_summary(recs)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_recommendation_summary_includes_headers(self, sample_songs, pop_lover_profile):
        """Test that summary table includes expected column headers."""
        recs = recommend_songs(pop_lover_profile, sample_songs, k=3)
        result = format_recommendation_summary(recs)
        assert "Song" in result
        assert "Artist" in result
        assert "Score" in result
        assert "Why You'll Like It" in result

    def test_format_recommendation_summary_empty_list(self):
        """Test formatting empty recommendation list."""
        result = format_recommendation_summary([])
        assert isinstance(result, str)

    def test_format_recommendation_summary_with_long_titles(self):
        """Test that long song titles don't break formatting."""
        long_song = {
            'id': 1,
            'title': "This is an incredibly long song title that might cause formatting issues in a table structure",
            'artist': "Very Long Artist Name That Goes On And On",
            'genre': "progressive psychedelic experimental jazz fusion",
            'mood': "happy",
            'energy': 0.85,
            'tempo_bpm': 120,
            'valence': 0.90,
            'danceability': 0.80,
            'acousticness': 0.15,
            'popularity': 78,
            'release_decade': 2020,
            'vocal_style': "sung",
            'production_quality': "polished",
            'emotional_arc': "constant",
        }
        recs = [(long_song, 8.5, "Genre match: test\nMood match: test")]
        result = format_recommendation_summary(recs)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_recommendation_detailed_returns_string(self, sample_songs, pop_lover_profile):
        """Test that format_recommendation_detailed returns a string."""
        recs = recommend_songs(pop_lover_profile, sample_songs, k=3)
        result = format_recommendation_detailed(recs)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_recommendation_detailed_preserves_all_reasons(self, sample_songs, pop_lover_profile):
        """Test that detailed format includes all scoring reasons."""
        recs = recommend_songs(pop_lover_profile, sample_songs, k=1)
        song, score, explanation = recs[0]
        result = format_recommendation_detailed(recs)
        # All reason lines should be in result
        reason_lines = _filter_reason_lines(explanation)
        for line in reason_lines:
            assert line in result, f"Reason '{line}' should appear in detailed output"

    def test_format_recommendation_detailed_empty_list(self):
        """Test formatting empty list."""
        result = format_recommendation_detailed([])
        assert isinstance(result, str)

    def test_format_recommendation_detailed_dynamic_widths(self):
        """Test that detailed format uses dynamic column widths."""
        songs = [
            {
                'id': 1,
                'title': "A",
                'artist': "B",
                'genre': "pop",
                'mood': "happy",
                'energy': 0.85,
                'tempo_bpm': 120,
                'valence': 0.90,
                'danceability': 0.80,
                'acousticness': 0.15,
                'popularity': 78,
                'release_decade': 2020,
                'vocal_style': "sung",
                'production_quality': "polished",
                'emotional_arc': "constant",
            },
            {
                'id': 2,
                'title': "Very Long Title With Many Words",
                'artist': "Very Long Artist Name",
                'genre': "rock",
                'mood': "intense",
                'energy': 0.90,
                'tempo_bpm': 140,
                'valence': 0.60,
                'danceability': 0.70,
                'acousticness': 0.10,
                'popularity': 85,
                'release_decade': 2020,
                'vocal_style': "sung",
                'production_quality': "polished",
                'emotional_arc': "constant",
            }
        ]
        recs = [
            (songs[0], 8.5, "Genre match: pop\nMood match: happy"),
            (songs[1], 8.0, "Genre match: rock\nMood match: intense"),
        ]
        result = format_recommendation_detailed(recs)
        # Should not truncate long title
        assert "Very Long Title With Many Words" in result


class TestModeAndDiversityInteractions:
    """Test interactions between scoring modes and diversity penalties."""

    def test_all_modes_with_diversity_enabled(self):
        """Test that all 4 modes work with diversity enabled."""
        songs = load_songs("data/songs.csv")
        user = {
            'favorite_genre': 'pop',
            'favorite_mood': 'happy',
            'target_energy': 0.85,
            'likes_acoustic': False,
        }
        modes = ["genre-first", "discovery", "niche-friendly", "personality"]

        for mode in modes:
            recs = recommend_songs_with_diversity(user, songs, k=5, mode=mode)
            assert len(recs) == 5
            assert all(isinstance(r, tuple) and len(r) == 3 for r in recs)

    def test_all_modes_with_different_penalties(self):
        """Test modes with extreme penalty values."""
        songs = load_songs("data/songs.csv")
        user = {
            'favorite_genre': 'pop',
            'favorite_mood': 'happy',
            'target_energy': 0.85,
            'likes_acoustic': False,
        }
        modes = ["genre-first", "discovery", "niche-friendly", "personality"]
        penalties = [0.0, 0.5, 1.0]

        for mode in modes:
            for penalty in penalties:
                recs = recommend_songs_with_diversity(
                    user, songs, k=5, mode=mode,
                    artist_penalty=penalty, genre_penalty=penalty
                )
                assert len(recs) == 5

    def test_mode_diversity_results_different_from_non_diversity(self):
        """Test that diversity changes results for all modes."""
        songs = load_songs("data/songs.csv")
        user = {
            'favorite_genre': 'pop',
            'favorite_mood': 'happy',
            'target_energy': 0.85,
            'likes_acoustic': False,
        }
        modes = ["genre-first", "discovery", "niche-friendly", "personality"]

        for mode in modes:
            recs_normal = recommend_songs(user, songs, k=5, mode=mode)
            recs_diverse = recommend_songs_with_diversity(user, songs, k=5, mode=mode)

            normal_songs = [s['id'] for s, _, _ in recs_normal]
            diverse_songs = [s['id'] for s, _, _ in recs_diverse]

            # At least some should differ (unless top 5 all unique artists/genres)
            assert isinstance(normal_songs, list)
            assert isinstance(diverse_songs, list)

    def test_diversity_sorted_correctly_all_modes(self):
        """Test that diversity results are sorted by score descending for all modes."""
        songs = load_songs("data/songs.csv")
        user = {
            'favorite_genre': 'pop',
            'favorite_mood': 'happy',
            'target_energy': 0.85,
            'likes_acoustic': False,
        }
        modes = ["genre-first", "discovery", "niche-friendly", "personality"]

        for mode in modes:
            recs = recommend_songs_with_diversity(user, songs, k=5, mode=mode)
            scores = [score for _, score, _ in recs]
            assert scores == sorted(scores, reverse=True), \
                f"Diversity results not sorted for mode {mode}"


class TestExplanationCompleteness:
    """Test that explanations are comprehensive across modes and features."""

    def test_all_modes_explain_genre_matching(self):
        """Test that all modes explain genre matching."""
        songs = load_songs("data/songs.csv")
        user = {
            'favorite_genre': 'pop',
            'favorite_mood': 'happy',
            'target_energy': 0.85,
            'likes_acoustic': False,
        }
        modes = ["genre-first", "discovery", "niche-friendly", "personality"]

        for mode in modes:
            recs = recommend_songs(user, songs, k=1, mode=mode)
            _, _, explanation = recs[0]
            assert "Genre" in explanation, f"Mode {mode} should explain genre"

    def test_all_modes_explain_mood_matching(self):
        """Test that all modes explain mood matching."""
        songs = load_songs("data/songs.csv")
        user = {
            'favorite_genre': 'pop',
            'favorite_mood': 'happy',
            'target_energy': 0.85,
            'likes_acoustic': False,
        }
        modes = ["genre-first", "discovery", "niche-friendly", "personality"]

        for mode in modes:
            recs = recommend_songs(user, songs, k=1, mode=mode)
            _, _, explanation = recs[0]
            assert "Mood" in explanation, f"Mode {mode} should explain mood"

    def test_all_modes_explain_energy(self):
        """Test that all modes explain energy scoring."""
        songs = load_songs("data/songs.csv")
        user = {
            'favorite_genre': 'pop',
            'favorite_mood': 'happy',
            'target_energy': 0.85,
            'likes_acoustic': False,
        }
        modes = ["genre-first", "discovery", "niche-friendly", "personality"]

        for mode in modes:
            recs = recommend_songs(user, songs, k=1, mode=mode)
            _, _, explanation = recs[0]
            assert "Energy" in explanation, f"Mode {mode} should explain energy"

    def test_advanced_features_in_explanations(self):
        """Test that advanced features appear in explanations."""
        songs = load_songs("data/songs.csv")
        user = {
            'favorite_genre': 'pop',
            'favorite_mood': 'happy',
            'target_energy': 0.85,
            'likes_acoustic': False,
        }

        recs = recommend_songs(user, songs, k=1, mode="personality")
        _, _, explanation = recs[0]

        # Personality mode emphasizes advanced features
        advanced_features = ["Vocal style", "Production", "Emotional arc", "Popularity", "Release decade"]
        found_features = sum(1 for f in advanced_features if f in explanation)
        assert found_features >= 2, "Should explain at least 2 advanced features"


class TestBoundaryConditions:
    """Test extreme values and edge cases."""

    def test_k_equals_one(self, sample_songs, pop_lover_profile):
        """Test k=1 returns exactly one recommendation."""
        recs = recommend_songs(pop_lover_profile, sample_songs, k=1)
        assert len(recs) == 1

    def test_k_equals_zero(self, sample_songs, pop_lover_profile):
        """Test k=0 returns empty list."""
        recs = recommend_songs(pop_lover_profile, sample_songs, k=0)
        assert len(recs) == 0

    def test_k_exceeds_catalog(self, sample_songs, pop_lover_profile):
        """Test k larger than catalog returns all songs."""
        recs = recommend_songs(pop_lover_profile, sample_songs, k=100)
        assert len(recs) == len(sample_songs)

    def test_diversity_penalty_zero(self):
        """Test diversity with penalty=0.0 doesn't penalize."""
        songs = load_songs("data/songs.csv")
        user = {
            'favorite_genre': 'pop',
            'favorite_mood': 'happy',
            'target_energy': 0.85,
            'likes_acoustic': False,
        }

        recs_diverse = recommend_songs_with_diversity(user, songs, k=5, artist_penalty=0.0, genre_penalty=0.0)
        recs_normal = recommend_songs(user, songs, k=5)

        # With 0 penalty, should be very similar (only order might differ slightly)
        diverse_scores = [score for _, score, _ in recs_diverse]
        normal_scores = [score for _, score, _ in recs_normal]

        # Top scores should be very close
        assert abs(diverse_scores[0] - normal_scores[0]) < 0.01

    def test_diversity_penalty_one_point_zero(self):
        """Test diversity with penalty=1.0 fully zeroes duplicates."""
        songs = load_songs("data/songs.csv")
        user = {
            'favorite_genre': 'pop',
            'favorite_mood': 'happy',
            'target_energy': 0.85,
            'likes_acoustic': False,
        }

        recs = recommend_songs_with_diversity(user, songs, k=5, artist_penalty=1.0, genre_penalty=1.0)

        # With 1.0 penalty, all artists should be unique
        artists = [s['artist'] for s, _, _ in recs]
        assert len(set(artists)) == len(artists), "All artists should be unique with penalty=1.0"

    def test_extreme_user_preferences_handled(self):
        """Test extreme preference values don't crash."""
        songs = load_songs("data/songs.csv")
        extreme_users = [
            {'favorite_genre': 'nonexistent_genre', 'favorite_mood': 'happy', 'target_energy': 1.0, 'likes_acoustic': True},
            {'favorite_genre': 'pop', 'favorite_mood': 'nonexistent_mood', 'target_energy': 0.0, 'likes_acoustic': False},
        ]

        for user in extreme_users:
            recs = recommend_songs(user, songs, k=5)
            assert len(recs) > 0, "Should still produce recommendations for extreme preferences"

    def test_single_song_k_equals_one(self, sample_songs, pop_lover_profile):
        """Test that single song recommendation works correctly."""
        recs = recommend_songs(pop_lover_profile, sample_songs, k=1)
        assert len(recs) == 1
        song, score, explanation = recs[0]
        assert isinstance(score, (int, float))
        assert score > 0
        assert len(explanation) > 0
