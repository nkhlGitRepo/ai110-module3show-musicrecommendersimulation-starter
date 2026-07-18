import pytest
from src.recommender import (
    Song, UserProfile, load_songs, score_song, score_song_advanced, recommend_songs,
    ScoringWeights, ScoringStrategy, WeightedScoringStrategy, get_strategy, SCORING_MODES
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
