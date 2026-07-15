# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Explain your design in plain language.

Some prompts to answer:

- What features does each `Song` use in your system
  - For example: genre, mood, energy, tempo
- What information does your `UserProfile` store
- How does your `Recommender` compute a score for each song
- How do you choose which songs to recommend

You can include a simple diagram or bullet list if helpful.


Phase 1 Step 4, Summarize you comcept:
Real-world recommenders like Spotify use multiple signals including what similar users enjoy, song characteristics like tempo and mood, and engagement patterns like skips and saves. The system I am designing uses content-based filtering that matches song features to what users tell us they prefer. Genre and mood are prioritized as the strongest signals because they are fundamentally all or nothing deal breakers for a recommendation. The system's formula will then prioritize numerical features like energy using distance-based scoring where songs closer to a user's preference score higher. Acousticness and danceability are also considered as secondary factors.

Phase 2 Step 5, Document your plan:

Algorithm Recipe (GMEWS - Genre-Mood-Energy Weighted Scorer):
For each song, calculate: SCORE = G + M + (E × 1.5) + (A × 1.0) + (D × 0.3)
- G: 2.0 if genre matches, else 0.0
- M: 2.0 if mood matches, else 0.0  
- E: 1.0 - |song.energy - target_energy| (distance-based)
- A: acousticness if user likes acoustic, else 1.0 - acousticness
- D: danceability × 0.3 if target_energy ≥ 0.7, else 0.0

Rank songs by score (highest first), return top-K with explanations.

Test Profiles:
1. Chill Listener: lofi/chill/0.35/acoustic
2. Gym Enthusiast: pop/intense/0.90/electronic
3. Indie Romantic: indie/nostalgic/0.60/acoustic
4. Electronic Producer: electronic/uplifting/0.87/electronic
5. Classical Introvert: classical/meditative/0.15/acoustic
6. Hip-Hop Head: hip-hop/energetic/0.85/electronic

Expected Biases: Genre/mood mismatches create hard ceilings (4.0 score) that limit discovery across genres. Acoustic preference is heavily weighted and reduces recommendations for synthetic music. Energy distance penalizes extreme preferences. Danceability bonus only applies to high-energy users. No collaborative filtering means niche genres unrecommended unless the user explicitly prefers them.


---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

User Profile: pop, happy, 0.80 energy, electronic preference

```
======================================================================
TOP RECOMMENDATIONS FOR YOU
======================================================================

1. SUNRISE CITY
   Artist: Neon Echo | Genre: pop
   Score: 6.53 / 6.0

   Why you'll like it:
   • Genre match: pop (+2.0)
   • Mood match: happy (+2.0)
   • Energy: 0.82 vs target 0.80 (1.47)
   • Acousticness: 0.82 (electronic)
   • Danceability bonus: 0.79 (+0.24)

   ------------------------------------------------------------------

2. GYM HERO
   Artist: Max Pulse | Genre: pop
   Score: 4.52 / 6.0

   Why you'll like it:
   • Genre match: pop (+2.0)
   • Mood mismatch: intense vs happy (0.0)
   • Energy: 0.93 vs target 0.80 (1.30)
   • Acousticness: 0.95 (electronic)
   • Danceability bonus: 0.88 (+0.26)

   ------------------------------------------------------------------

3. ROOFTOP LIGHTS
   Artist: Indigo Parade | Genre: indie pop
   Score: 4.34 / 6.0

   Why you'll like it:
   • Genre mismatch: indie pop vs pop (0.0)
   • Mood match: happy (+2.0)
   • Energy: 0.76 vs target 0.80 (1.44)
   • Acousticness: 0.65 (electronic)
   • Danceability bonus: 0.82 (+0.25)

   ------------------------------------------------------------------

4. ELECTRIC DREAMS
   Artist: Pulse Collective | Genre: electronic
   Score: 2.59 / 6.0

   Why you'll like it:
   • Genre mismatch: electronic vs pop (0.0)
   • Mood mismatch: uplifting vs happy (0.0)
   • Energy: 0.87 vs target 0.80 (1.40)
   • Acousticness: 0.92 (electronic)
   • Danceability bonus: 0.91 (+0.27)

   ------------------------------------------------------------------

5. GLITCH GARDEN
   Artist: Experimental Labs | Genre: experimental
   Score: 2.51 / 6.0

   Why you'll like it:
   • Genre mismatch: experimental vs pop (0.0)
   • Mood mismatch: intense vs happy (0.0)
   • Energy: 0.79 vs target 0.80 (1.48)
   • Acousticness: 0.81 (electronic)
   • Danceability bonus: 0.73 (+0.22)

   ------------------------------------------------------------------
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



