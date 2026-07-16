"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from .recommender import load_songs, recommend_songs


# User preference profiles for testing
USER_PROFILES = {
    "high_energy_pop": {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.85,
        "likes_acoustic": False,
    },
    "chill_lofi": {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.38,
        "likes_acoustic": True,
    },
    "deep_intense_rock": {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.91,
        "likes_acoustic": False,
    },
}

# Adversarial/Edge case profiles to test algorithm limits
ADVERSARIAL_PROFILES = {
    "conflicting_energy_mood": {
        "favorite_genre": "indie",
        "favorite_mood": "melancholic",
        "target_energy": 0.90,
        "likes_acoustic": False,
    },
    "extreme_low_energy": {
        "favorite_genre": "classical",
        "favorite_mood": "meditative",
        "target_energy": 0.10,
        "likes_acoustic": True,
    },
    "acoustic_rock_contradiction": {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.88,
        "likes_acoustic": True,
    },
    "niche_genre_nomatch": {
        "favorite_genre": "synthwave",
        "favorite_mood": "moody",
        "target_energy": 0.75,
        "likes_acoustic": False,
    },
    "all_preference_mismatches": {
        "favorite_genre": "country",
        "favorite_mood": "nostalgic",
        "target_energy": 0.15,
        "likes_acoustic": False,
    },
    "extreme_high_energy_danceability": {
        "favorite_genre": "electronic",
        "favorite_mood": "uplifting",
        "target_energy": 0.95,
        "likes_acoustic": False,
    },
}

# Combine all profiles
USER_PROFILES.update(ADVERSARIAL_PROFILES)


def main(profile_name: str = "high_energy_pop") -> None:
    songs = load_songs("data/songs.csv")
    print(f"Successfully loaded {len(songs)} songs.\n")

    # Load selected user profile
    if profile_name not in USER_PROFILES:
        print(f"Profile '{profile_name}' not found. Available profiles:")
        for name in USER_PROFILES.keys():
            print(f"  - {name}")
        return

    user_prefs = USER_PROFILES[profile_name]
    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\n" + "="*70)
    print(f"TOP RECOMMENDATIONS FOR: {profile_name.upper().replace('_', ' ')}")
    print(f"Profile: genre={user_prefs['favorite_genre']}, mood={user_prefs['favorite_mood']}, " +
          f"energy={user_prefs['target_energy']}, acoustic={'yes' if user_prefs['likes_acoustic'] else 'no'}")
    print("="*70)

    if recommendations:
        for idx, rec in enumerate(recommendations, 1):
            song, score, explanation = rec
            print(f"\n{idx}. {song['title'].upper()}")
            print(f"   Artist: {song['artist']} | Genre: {song['genre']}")
            print(f"   Score: {score:.2f} / 6.0")
            print(f"\n   Why you'll like it:")
            for reason in explanation.split('\n'):
                print(f"   • {reason}")
            print(f"\n   {'-'*66}")
    else:
        print("No recommendations found.")


if __name__ == "__main__":
    main()
