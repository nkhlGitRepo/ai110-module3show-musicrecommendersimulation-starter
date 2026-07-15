"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from .recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Successfully loaded {len(songs)} songs.\n")

    # Starter example profile (Gym Enthusiast)
    user_prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.80,
        "likes_acoustic": False
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\n" + "="*70)
    print("TOP RECOMMENDATIONS FOR YOU")
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
