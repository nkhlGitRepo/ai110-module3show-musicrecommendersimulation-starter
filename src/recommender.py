from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
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

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5, use_advanced: bool = False) -> List[Tuple[Dict, float, str]]:
    """Score all songs and return top-K ranked by score descending."""
    score_func = score_song_advanced if use_advanced else score_song
    scored_songs = [
        (song, score, "\n".join(reasons))
        for song in songs
        for score, reasons in [score_func(user_prefs, song)]
    ]

    return sorted(scored_songs, key=lambda x: x[1], reverse=True)[:k]
