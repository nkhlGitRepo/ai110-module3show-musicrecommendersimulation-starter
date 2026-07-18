from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import csv

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: float
    release_decade: int
    vocal_style: str
    production_quality: str
    emotional_arc: str

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    preferred_vocal_style: str = "sung"
    preferred_production: str = "polished"
    preferred_emotional_arc: str = "constant"
    prefer_popular: bool = True
    target_release_decade: int = 2020

@dataclass
class ScoringWeights:
    """Weight configuration for a scoring mode."""
    genre: float
    mood: float
    energy: float
    acousticness: float
    danceability: float
    vocal_style: float
    production: float
    emotional_arc: float
    popularity: float
    decade: float

class ScoringStrategy(ABC):
    """Base class for all scoring strategies."""

    def __init__(self, name: str, weights: ScoringWeights):
        self.name = name
        self.weights = weights

    @abstractmethod
    def score(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        """Score a song and return (score, reasons)."""
        pass

class WeightedScoringStrategy(ScoringStrategy):
    """Generic strategy that applies weights uniformly to all scoring components."""

    def score(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        """Score using weighted components with gradual features."""
        reasons = []
        score = 0.0

        # Genre: binary match
        if song['genre'] == user_prefs['favorite_genre']:
            genre_score = 1.0
            reasons.append(f"Genre match: {song['genre']} (+{self.weights.genre:.2f})")
        else:
            genre_score = 0.0
            reasons.append(f"Genre mismatch: {song['genre']} vs {user_prefs['favorite_genre']} (0.0)")
        score += genre_score * self.weights.genre

        # Mood: binary match
        if song['mood'] == user_prefs['favorite_mood']:
            mood_score = 1.0
            reasons.append(f"Mood match: {song['mood']} (+{self.weights.mood:.2f})")
        else:
            mood_score = 0.0
            reasons.append(f"Mood mismatch: {song['mood']} vs {user_prefs['favorite_mood']} (0.0)")
        score += mood_score * self.weights.mood

        # Energy: distance-based (0-1 range)
        energy_distance = abs(song['energy'] - user_prefs['target_energy'])
        energy_score = 1.0 - energy_distance
        energy_contribution = energy_score * self.weights.energy
        reasons.append(f"Energy: {song['energy']:.2f} vs target {user_prefs['target_energy']:.2f} ({energy_contribution:.2f})")
        score += energy_contribution

        # Acousticness: preference-based (0-1 range)
        if user_prefs['likes_acoustic']:
            acousticness_score = song['acousticness']
            reason_text = "acoustic" if song['acousticness'] > 0.5 else "electronic"
        else:
            acousticness_score = 1.0 - song['acousticness']
            reason_text = "electronic" if song['acousticness'] < 0.5 else "acoustic"
        acousticness_contribution = acousticness_score * self.weights.acousticness
        reasons.append(f"Acousticness: {acousticness_contribution:.2f} ({reason_text})")
        score += acousticness_contribution

        # Danceability: bonus only for high energy users (0-1 range)
        if user_prefs['target_energy'] >= 0.7:
            danceability_score = song['danceability']
            danceability_contribution = danceability_score * self.weights.danceability
            reasons.append(f"Danceability bonus: {danceability_contribution:.2f}")
            score += danceability_contribution
        else:
            reasons.append("Danceability: N/A (low energy user)")

        # Vocal style similarity (0-1 range via similarity function)
        vocal_style = user_prefs.get('preferred_vocal_style', 'sung')
        vocal_score = vocal_style_similarity(song['vocal_style'], vocal_style)
        vocal_contribution = vocal_score * self.weights.vocal_style
        reasons.append(f"Vocal style: {vocal_contribution:.2f}")
        score += vocal_contribution

        # Production quality similarity (0-1 range via similarity function)
        prod_quality = user_prefs.get('preferred_production', 'polished')
        prod_score = production_quality_similarity(song['production_quality'], prod_quality)
        prod_contribution = prod_score * self.weights.production
        reasons.append(f"Production: {prod_contribution:.2f}")
        score += prod_contribution

        # Emotional arc similarity (0-1 range via similarity function)
        arc_pref = user_prefs.get('preferred_emotional_arc', 'constant')
        arc_score = emotional_arc_similarity(song['emotional_arc'], arc_pref)
        arc_contribution = arc_score * self.weights.emotional_arc
        reasons.append(f"Emotional arc: {arc_contribution:.2f}")
        score += arc_contribution

        # Popularity scoring (0-1 range, inverted if negative weight)
        prefer_pop = user_prefs.get('prefer_popular', True)
        if self.weights.popularity >= 0:
            if prefer_pop:
                pop_score = song['popularity'] / 100.0
            else:
                pop_score = 1.0 - (song['popularity'] / 100.0)
        else:
            if prefer_pop:
                pop_score = 1.0 - (song['popularity'] / 100.0)
            else:
                pop_score = song['popularity'] / 100.0
        pop_contribution = pop_score * abs(self.weights.popularity)
        reasons.append(f"Popularity: {pop_contribution:.2f}")
        score += pop_contribution

        # Release decade (0-1 range with soft decay)
        target_decade = user_prefs.get('target_release_decade', 2020)
        decade_distance = abs(song['release_decade'] - target_decade) / 60.0
        decade_score = max(0.0, 1.0 - decade_distance)
        decade_contribution = decade_score * self.weights.decade
        reasons.append(f"Release decade: {decade_contribution:.2f}")
        score += decade_contribution

        return (score, reasons)

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Parse CSV file and return list of song dictionaries with typed numeric values."""
    print(f"Loading songs from {csv_path}...")
    songs = []

    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            song = {
                'id': int(row['id']),
                'title': row['title'],
                'artist': row['artist'],
                'genre': row['genre'],
                'mood': row['mood'],
                'energy': float(row['energy']),
                'tempo_bpm': int(row['tempo_bpm']),
                'valence': float(row['valence']),
                'danceability': float(row['danceability']),
                'acousticness': float(row['acousticness']),
                'popularity': float(row['popularity']),
                'release_decade': int(row['release_decade']),
                'vocal_style': row['vocal_style'],
                'production_quality': row['production_quality'],
                'emotional_arc': row['emotional_arc'],
            }
            songs.append(song)

    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a song using GMEWS: G + M + (E × 1.5) + (A × 1.0) + (D × 0.3); return (score, reasons)."""
    reasons = []
    score = 0.0

    # Genre component (G): 2.0 if match, else 0.0
    if song['genre'] == user_prefs['favorite_genre']:
        G = 2.0
        reasons.append(f"Genre match: {song['genre']} (+2.0)")
    else:
        G = 0.0
        reasons.append(f"Genre mismatch: {song['genre']} vs {user_prefs['favorite_genre']} (0.0)")

    # Mood component (M): 2.0 if match, else 0.0
    if song['mood'] == user_prefs['favorite_mood']:
        M = 2.0
        reasons.append(f"Mood match: {song['mood']} (+2.0)")
    else:
        M = 0.0
        reasons.append(f"Mood mismatch: {song['mood']} vs {user_prefs['favorite_mood']} (0.0)")

    # Energy component (E × 1.5): distance-based, 0-1 range
    energy_distance = abs(song['energy'] - user_prefs['target_energy'])
    E = 1.0 - energy_distance
    E_contribution = E * 1.5
    reasons.append(f"Energy: {song['energy']:.2f} vs target {user_prefs['target_energy']:.2f} ({E_contribution:.2f})")

    # Acousticness component (A): preference-based
    if user_prefs['likes_acoustic']:
        A = song['acousticness']
        reason_text = "acoustic" if song['acousticness'] > 0.5 else "electronic"
    else:
        A = 1.0 - song['acousticness']
        reason_text = "electronic" if song['acousticness'] < 0.5 else "acoustic"
    reasons.append(f"Acousticness: {A:.2f} ({reason_text})")

    # Danceability bonus (D × 0.3): only if high energy user
    if user_prefs['target_energy'] >= 0.7:
        D = song['danceability']
        D_contribution = D * 0.3
        reasons.append(f"Danceability bonus: {D:.2f} (+{D_contribution:.2f})")
    else:
        D = 0.0
        D_contribution = 0.0
        reasons.append("Danceability: N/A (low energy user)")

    # Total score
    score = G + M + E_contribution + A + D_contribution

    return (score, reasons)

def score_song_experiment_weight_shift(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """EXPERIMENT: Weight shift - double energy importance (3.0), halve genre importance (1.0)."""
    reasons = []
    score = 0.0

    # Genre component (G): 1.0 if match, else 0.0 (HALVED from 2.0)
    # Original: G = 2.0 if match, else 0.0
    if song['genre'] == user_prefs['favorite_genre']:
        # G = 2.0
        G = 1.0
        # reasons.append(f"Genre match: {song['genre']} (+2.0)")
        reasons.append(f"Genre match: {song['genre']} (+1.0)")
    else:
        G = 0.0
        # reasons.append(f"Genre mismatch: {song['genre']} vs {user_prefs['favorite_genre']} (0.0)")
        reasons.append(f"Genre mismatch: {song['genre']} vs {user_prefs['favorite_genre']} (0.0)")

    # Mood component (M): 2.0 if match, else 0.0 (UNCHANGED)
    if song['mood'] == user_prefs['favorite_mood']:
        M = 2.0
        reasons.append(f"Mood match: {song['mood']} (+2.0)")
    else:
        M = 0.0
        reasons.append(f"Mood mismatch: {song['mood']} vs {user_prefs['favorite_mood']} (0.0)")

    # Energy component (E × 3.0): distance-based, DOUBLED from 1.5
    energy_distance = abs(song['energy'] - user_prefs['target_energy'])
    E = 1.0 - energy_distance
    # E_contribution = E * 1.5
    E_contribution = E * 3.0
    reasons.append(f"Energy: {song['energy']:.2f} vs target {user_prefs['target_energy']:.2f} ({E_contribution:.2f})")

    # Acousticness component (A): preference-based (UNCHANGED)
    if user_prefs['likes_acoustic']:
        A = song['acousticness']
        reason_text = "acoustic" if song['acousticness'] > 0.5 else "electronic"
    else:
        A = 1.0 - song['acousticness']
        reason_text = "electronic" if song['acousticness'] < 0.5 else "acoustic"
    reasons.append(f"Acousticness: {A:.2f} ({reason_text})")

    # Danceability bonus (D × 0.3): only if high energy user (UNCHANGED)
    if user_prefs['target_energy'] >= 0.7:
        D = song['danceability']
        D_contribution = D * 0.3
        reasons.append(f"Danceability bonus: {D:.2f} (+{D_contribution:.2f})")
    else:
        D = 0.0
        D_contribution = 0.0
        reasons.append("Danceability: N/A (low energy user)")

    # Total score with new weights
    # Original: score = G + M + E_contribution + A + D_contribution
    # Max original: 2.0 + 2.0 + 1.5 + 1.0 + 0.3 = 6.8
    # New max: 1.0 + 2.0 + 3.0 + 1.0 + 0.3 = 7.3
    score = G + M + E_contribution + A + D_contribution

    return (score, reasons)

def vocal_style_similarity(style1: str, style2: str) -> float:
    """Calculate similarity between vocal styles (0.0 to 1.0)."""
    if style1 == style2:
        return 1.0
    if {style1, style2} == {'sung', 'rapped'}:
        return 0.6
    if {style1, style2} == {'sung', 'spoken'} or {style1, style2} == {'rapped', 'spoken'}:
        return 0.5
    return 0.1

def production_quality_similarity(prod1: str, prod2: str) -> float:
    """Calculate similarity between production qualities (0.0 to 1.0)."""
    if prod1 == prod2:
        return 1.0
    quality_order = {'lo-fi': 0, 'standard': 1, 'polished': 2, 'avant-garde': 1}
    distance = abs(quality_order.get(prod1, 1) - quality_order.get(prod2, 1))
    return max(0.1, 1.0 - distance * 0.35)

def emotional_arc_similarity(arc1: str, arc2: str) -> float:
    """Calculate similarity between emotional arcs (0.0 to 1.0)."""
    if arc1 == arc2:
        return 1.0
    if {arc1, arc2} == {'constant', 'minimal'}:
        return 0.7
    if {arc1, arc2} == {'builds', 'evolves'}:
        return 0.6
    return 0.2

# Scoring Mode Definitions
GENRE_FIRST = WeightedScoringStrategy(
    name="Genre-First (Default)",
    weights=ScoringWeights(
        genre=2.0,
        mood=2.0,
        energy=1.5,
        acousticness=1.0,
        danceability=0.3,
        vocal_style=0.6,
        production=0.6,
        emotional_arc=0.6,
        popularity=0.6,
        decade=0.6
    )
)

DISCOVERY = WeightedScoringStrategy(
    name="Discovery Mode",
    weights=ScoringWeights(
        genre=0.2,
        mood=2.0,
        energy=2.0,
        acousticness=0.5,
        danceability=0.5,
        vocal_style=0.5,
        production=0.8,
        emotional_arc=0.8,
        popularity=-0.5,
        decade=0.3
    )
)

NICHE_FRIENDLY = WeightedScoringStrategy(
    name="Niche-Friendly Mode",
    weights=ScoringWeights(
        genre=2.5,
        mood=2.0,
        energy=1.0,
        acousticness=0.8,
        danceability=0.2,
        vocal_style=0.6,
        production=0.6,
        emotional_arc=0.6,
        popularity=-0.5,
        decade=0.8
    )
)

PERSONALITY = WeightedScoringStrategy(
    name="Personality-Based Mode",
    weights=ScoringWeights(
        genre=1.0,
        mood=1.0,
        energy=1.0,
        acousticness=0.5,
        danceability=0.3,
        vocal_style=1.5,
        production=1.5,
        emotional_arc=1.0,
        popularity=0.4,
        decade=0.4
    )
)

SCORING_MODES = {
    "genre-first": GENRE_FIRST,
    "discovery": DISCOVERY,
    "niche-friendly": NICHE_FRIENDLY,
    "personality": PERSONALITY,
}

def get_strategy(mode_name: str) -> ScoringStrategy:
    """Get a scoring strategy by name, default to genre-first."""
    return SCORING_MODES.get(mode_name, GENRE_FIRST)

def score_song_advanced(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score using GMEWS plus advanced features with consistent gradual scoring."""
    base_score, base_reasons = score_song(user_prefs, song)

    advanced_bonuses = []
    advanced_score = 0.0

    # Vocal style similarity (gradual, 0.0-1.0)
    vocal_style = user_prefs.get('preferred_vocal_style', 'sung')
    vocal_score = vocal_style_similarity(song['vocal_style'], vocal_style)
    advanced_bonuses.append(f"Vocal style: {song['vocal_style']} vs {vocal_style} ({vocal_score:.2f})")
    advanced_score += vocal_score * 0.6

    # Production quality similarity (gradual, 0.0-1.0)
    prod_quality = user_prefs.get('preferred_production', 'polished')
    prod_score = production_quality_similarity(song['production_quality'], prod_quality)
    advanced_bonuses.append(f"Production: {song['production_quality']} vs {prod_quality} ({prod_score:.2f})")
    advanced_score += prod_score * 0.6

    # Emotional arc similarity (gradual, 0.0-1.0)
    arc_pref = user_prefs.get('preferred_emotional_arc', 'constant')
    arc_score = emotional_arc_similarity(song['emotional_arc'], arc_pref)
    advanced_bonuses.append(f"Emotional arc: {song['emotional_arc']} vs {arc_pref} ({arc_score:.2f})")
    advanced_score += arc_score * 0.6

    # Popularity scoring (distance-based, 0-1 range)
    prefer_pop = user_prefs.get('prefer_popular', True)
    if prefer_pop:
        pop_score = song['popularity'] / 100.0
        advanced_bonuses.append(f"Popularity (popularity-seeking): {song['popularity']:.0f}/100 ({pop_score:.2f})")
    else:
        pop_score = 1.0 - (song['popularity'] / 100.0)
        advanced_bonuses.append(f"Popularity (indie-seeking): {song['popularity']:.0f}/100 ({pop_score:.2f})")
    advanced_score += pop_score * 0.6

    # Release decade (softer distance decay, normalize by data range)
    target_decade = user_prefs.get('target_release_decade', 2020)
    decade_distance = abs(song['release_decade'] - target_decade) / 60.0
    decade_score = max(0.0, 1.0 - decade_distance)
    advanced_bonuses.append(f"Release decade: {song['release_decade']} vs {target_decade} ({decade_score:.2f})")
    advanced_score += decade_score * 0.6

    total_score = base_score + advanced_score
    all_reasons = base_reasons + advanced_bonuses

    return (total_score, all_reasons)

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5, mode: str = "genre-first", use_advanced: bool = False) -> List[Tuple[Dict, float, str]]:
    """Score all songs using the specified mode and return top-K ranked by score descending."""
    if use_advanced:
        score_func = score_song_advanced
    else:
        strategy = get_strategy(mode)
        score_func = strategy.score

    scored_songs = [
        (song, score, "\n".join(reasons))
        for song in songs
        for score, reasons in [score_func(user_prefs, song)]
    ]

    return sorted(scored_songs, key=lambda x: x[1], reverse=True)[:k]
