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

Phase 4 Step 1: Adversarial Profile Test Results

Profile: Extreme Low Energy (classical/meditative at 0.10 energy)
```
======================================================================
TOP RECOMMENDATIONS FOR: EXTREME LOW ENERGY
Profile: genre=classical, mood=meditative, energy=0.1, acoustic=yes
======================================================================

1. BACH SUITE NO.1
   Artist: Classical Ensemble | Genre: classical
   Score: 6.40 / 6.0

   Why you'll like it:
   • Genre match: classical (+2.0)
   • Mood match: meditative (+2.0)
   • Energy: 0.15 vs target 0.10 (1.42)
   • Acousticness: 0.98 (acoustic)
   • Danceability: N/A (low energy user)

2. SPACEWALK THOUGHTS
   Artist: Orbit Bloom | Genre: ambient
   Score: 2.15 / 6.0

3. LIBRARY RAIN
   Artist: Paper Lanterns | Genre: lofi
   Score: 1.98 / 6.0

4. COFFEE SHOP STORIES
   Artist: Slow Stereo | Genre: jazz
   Score: 1.98 / 6.0

5. FOCUS FLOW
   Artist: LoRoom | Genre: lofi
   Score: 1.83 / 6.0
```

Profile: Niche Genre No-Match (synthwave preference)
```
======================================================================
TOP RECOMMENDATIONS FOR: NICHE GENRE NOMATCH
Profile: genre=synthwave, mood=moody, energy=0.75, acoustic=no
======================================================================

1. NIGHT DRIVE LOOP
   Artist: Neon Echo | Genre: synthwave
   Score: 6.50 / 6.0

   Why you'll like it:
   • Genre match: synthwave (+2.0)
   • Mood match: moody (+2.0)
   • Energy: 0.75 vs target 0.75 (1.50)
   • Acousticness: 0.78 (electronic)
   • Danceability bonus: 0.73 (+0.22)

2. ELECTRIC DREAMS
   Artist: Pulse Collective | Genre: electronic
   Score: 2.51 / 6.0

3. GLITCH GARDEN
   Artist: Experimental Labs | Genre: experimental
   Score: 2.47 / 6.0

4. SUNRISE CITY
   Artist: Neon Echo | Genre: pop
   Score: 2.45 / 6.0

5. GYM HERO
   Artist: Max Pulse | Genre: pop
   Score: 2.44 / 6.0
```

Profile: Conflicting Energy/Mood (0.90 energy + melancholic mood)
```
======================================================================
TOP RECOMMENDATIONS FOR: CONFLICTING ENERGY MOOD
Profile: genre=indie, mood=melancholic, energy=0.9, acoustic=no
======================================================================

1. NEON THOUGHTS
   Artist: Indie Void | Genre: indie
   Score: 3.84 / 6.0

   Why you'll like it:
   • Genre match: indie (+2.0)
   • Mood mismatch: nostalgic vs melancholic (0.0)
   • Energy: 0.61 vs target 0.90 (1.06)
   • Acousticness: 0.57 (electronic)
   • Danceability bonus: 0.68 (+0.20)

2. DUSTY ROADS
   Artist: The Wanderers | Genre: country
   Score: 3.38 / 6.0

3. MIDNIGHT BLUES
   Artist: The Rooters | Genre: blues
   Score: 3.34 / 6.0

4. GYM HERO
   Artist: Max Pulse | Genre: pop
   Score: 2.67 / 6.0

5. ELECTRIC DREAMS
   Artist: Pulse Collective | Genre: electronic
   Score: 2.65 / 6.0
```

Profile: Acoustic/Rock Contradiction (rock + acoustic preference)
```
======================================================================
TOP RECOMMENDATIONS FOR: ACOUSTIC ROCK CONTRADICTION
Profile: genre=rock, mood=intense, energy=0.88, acoustic=yes
======================================================================

1. STORM RUNNER
   Artist: Voltline | Genre: rock
   Score: 5.75 / 6.0

   Why you'll like it:
   • Genre match: rock (+2.0)
   • Mood match: intense (+2.0)
   • Energy: 0.91 vs target 0.88 (1.46)
   • Acousticness: 0.10 (electronic)
   • Danceability bonus: 0.66 (+0.20)

2. GLITCH GARDEN
   Artist: Experimental Labs | Genre: experimental
   Score: 3.77 / 6.0

3. GYM HERO
   Artist: Max Pulse | Genre: pop
   Score: 3.74 / 6.0

4. ISLAND VIBES
   Artist: Reggae Kings | Genre: reggae
   Score: 2.09 / 6.0

5. MIDNIGHT BLUES
   Artist: The Rooters | Genre: blues
   Score: 1.99 / 6.0
```



---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

The catalog has only 20 songs, which makes recommendations limited and therefore unrealistic for getting truly accurate results.  Most genres are represented by just one or two songs, so users with niche preferences get stuck while mainstream users thrive.  Another issue with the algorithm is that it cannot understand lyrics to judge a song's appeal beyond its basic features.  Finally, the binary genre matching creates filter bubbles that prevent discovering songs outside a user's stated preferences.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this

While working on this project, I learned that recommenders work by converting song features into a numerical score that ranks items for each user.  This is achieved through weighted math, where each feature becomes a number that gets combined with others based on weights chosen.  The algorithm just applies the patterns we define and ranks items accordingly.  This means a recommender is only as good as the data we are able to acquire and the algorithm that purposes that data to deliver accurate results.

I also learned how easily bias creeps in through design choices that seem inconsequential on the surface.  Binary genre matching appears to be fair until you realize it creates unfairness by hacing mainstream users get multiple recommendations while fans of more niche content can get stuck with only one.  When setting the weights, it is important to choose whether energy matters more than genre and if danceability deserves a bonus.  


