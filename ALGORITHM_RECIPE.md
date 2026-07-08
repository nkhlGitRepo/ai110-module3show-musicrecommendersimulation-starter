# Algorithm Recipe: Content-Based Music Recommender

## Overview
**Name:** Genre-Mood-Energy Weighted Scorer (GMEWS)

**Strategy:** Content-based filtering that scores each song by matching its features to a user's taste profile.

**Philosophy:** A user will enjoy a song if:
1. It matches their favorite genre (highest priority)
2. It matches their favorite mood (highest priority)
3. Its energy level is close to their target energy (medium priority)
4. Its acoustic properties align with their preference (medium priority)
5. It has good danceability for upbeat moods (low priority)

---

## Scoring Formula

### Core Score Calculation
```
SCORE = G + M + (E × 1.5) + (A × 1.0) + (D × 0.3)

Where:
G = 2.0 if genre matches, else 0.0
M = 2.0 if mood matches, else 0.0
E = 1 - |song.energy - user.target_energy|
A = acousticness preference score
D = danceability bonus (conditional)
```

**Maximum possible score:** 6.0
**Minimum possible score:** 0.0

---

## Component Details

### 1. Genre Component (G = 2.0 or 0.0)

**Rule:** Award 2.0 points for exact genre match; 0.0 otherwise.

```
IF song.genre == user.favorite_genre:
    G = 2.0
ELSE:
    G = 0.0
```

**Rationale:** Genre is a user's primary filter. If they like "pop", a "rock" song won't appeal to them, even if mood/energy match.

**Example:**
- User: favorite_genre = "pop"
- Song A: genre = "pop" → G = 2.0 ✓
- Song B: genre = "indie pop" → G = 0.0 (exact match only)
- Song C: genre = "rock" → G = 0.0 ✗

---

### 2. Mood Component (M = 2.0 or 0.0)

**Rule:** Award 2.0 points for exact mood match; 0.0 otherwise.

```
IF song.mood == user.favorite_mood:
    M = 2.0
ELSE:
    M = 0.0
```

**Rationale:** A user in "chill" mood won't want "intense" music, regardless of other factors.

**Example:**
- User: favorite_mood = "chill"
- Song A: mood = "chill" → M = 2.0 ✓
- Song B: mood = "relaxed" → M = 0.0 (close but not exact)
- Song C: mood = "intense" → M = 0.0 ✗

---

### 3. Energy Component (E × 1.5)

**Rule:** Score based on distance between song energy and user's target energy (0-1 scale), then multiply by 1.5.

```
E = 1.0 - |song.energy - user.target_energy|

# Clamp to [0, 1]
IF E < 0: E = 0
IF E > 1: E = 1

# Then in final score: E × 1.5
```

**Rationale:** Energy is continuous. A user preferring 0.8 energy should get songs in range [0.6-1.0], not just exactly 0.8. The 1.5× weight gives energy more importance.

**Example:**
- User: target_energy = 0.8
- Song A: energy = 0.80 → E = 1.0 - 0.0 = 1.0 → contributes 1.5 ✓
- Song B: energy = 0.70 → E = 1.0 - 0.1 = 0.9 → contributes 1.35
- Song C: energy = 0.40 → E = 1.0 - 0.4 = 0.6 → contributes 0.9
- Song D: energy = 0.10 → E = 1.0 - 0.7 = 0.3 → contributes 0.45

---

### 4. Acousticness Component (A × 1.0)

**Rule:** Match acousticness preference; penalize if user prefers acoustic but song isn't, or vice versa.

```
IF user.likes_acoustic == TRUE:
    # User prefers acoustic: reward high acousticness
    A = song.acousticness
ELSE:
    # User prefers NOT acoustic: reward low acousticness
    A = 1.0 - song.acousticness
```

**Rationale:** Acoustic vs electric is a binary preference that strongly affects enjoyment.

**Example A - User likes acoustic:**
- User: likes_acoustic = True
- Song A: acousticness = 0.85 → A = 0.85 ✓
- Song B: acousticness = 0.50 → A = 0.50 (neutral)
- Song C: acousticness = 0.05 → A = 0.05 ✗

**Example B - User dislikes acoustic:**
- User: likes_acoustic = False
- Song A: acousticness = 0.85 → A = 0.15 ✗
- Song B: acousticness = 0.50 → A = 0.50 (neutral)
- Song C: acousticness = 0.05 → A = 0.95 ✓

---

### 5. Danceability Component (D × 0.3)

**Rule:** If user is upbeat/energetic, include danceability bonus. Otherwise, skip it.

```
IF user.target_energy >= 0.7:
    # High energy users: include danceability
    D = song.danceability
ELSE:
    # Low/medium energy users: no bonus
    D = 0
```

**Rationale:** Danceability correlates with upbeat mood. Only applies to energetic users; a "chill" user doesn't need danceability.

**Example - Energetic user (target_energy=0.85):**
- Song A: danceability = 0.88 → D = 0.88 → contributes 0.88 × 0.3 = 0.264 ✓
- Song B: danceability = 0.50 → D = 0.50 → contributes 0.50 × 0.3 = 0.15

**Example - Chill user (target_energy=0.35):**
- Song A: danceability = 0.88 → D = 0.0 (ignored)
- Song B: danceability = 0.50 → D = 0.0 (ignored)

---

## End-to-End Example

### Scenario
```
User Profile:
  favorite_genre = "pop"
  favorite_mood = "happy"
  target_energy = 0.8
  likes_acoustic = False

Song 1: "Sunrise City" (pop, happy, 0.82 energy, 0.18 acousticness, 0.79 danceability)
Song 2: "Library Rain" (lofi, chill, 0.35 energy, 0.86 acousticness, 0.58 danceability)
Song 3: "Rooftop Lights" (indie pop, happy, 0.76 energy, 0.35 acousticness, 0.82 danceability)
```

### Scoring Song 1
```
G = 2.0 (pop == pop)
M = 2.0 (happy == happy)
E = 1.0 - |0.82 - 0.8| = 0.98 → 0.98 × 1.5 = 1.47
A = 1.0 - 0.18 = 0.82 (not acoustic, which user prefers)
D = 0.79 × 0.3 = 0.237 (energy >= 0.7, so apply bonus)

SCORE = 2.0 + 2.0 + 1.47 + 0.82 + 0.237
      = 6.527 ⭐ EXCELLENT
```

### Scoring Song 2
```
G = 0.0 (lofi ≠ pop)
M = 0.0 (chill ≠ happy)
E = 1.0 - |0.35 - 0.8| = 0.55 → 0.55 × 1.5 = 0.825
A = 1.0 - 0.86 = 0.14 (too acoustic)
D = 0.0 (energy < 0.7, no bonus)

SCORE = 0.0 + 0.0 + 0.825 + 0.14 + 0.0
      = 0.965 ✗ POOR
```

### Scoring Song 3
```
G = 0.0 (indie pop ≠ pop, exact match only)
M = 2.0 (happy == happy)
E = 1.0 - |0.76 - 0.8| = 0.96 → 0.96 × 1.5 = 1.44
A = 1.0 - 0.35 = 0.65
D = 0.82 × 0.3 = 0.246

SCORE = 0.0 + 2.0 + 1.44 + 0.65 + 0.246
      = 4.336 ⭐ GOOD (but not as good as Song 1)
```

### Ranking
1. Song 1: 6.527 (best match)
2. Song 3: 4.336 (secondary match)
3. Song 2: 0.965 (poor match)

---

## Implementation Notes

### Edge Cases

**1. No exact genre match**
- Current: score = 0.0 for genre
- Alternative: Could implement genre similarity (future enhancement)
- For now: Songs with non-matching genre rarely score high

**2. Multiple songs with same score**
- Stable tie-breaking: Sort by song ID (song order in CSV)
- Alternative: Could use secondary criteria (e.g., danceability)

**3. User prefers medium energy (e.g., 0.5)**
- Energy component works well: songs near 0.5 score high
- Danceability bonus doesn't apply (< 0.7), which is correct

### Normalization
- **No need for score normalization** if recommending top-K songs
- Just rank by raw score (highest first)
- If needed later: divide by 6.8 to get 0-1 range

### Explanation Generation
For each recommended song, explain:
- ✓ Matches your favorite genre: {genre}
- ✓ Matches your mood: {mood}
- ✓ Energy level: {energy} (your preference: {target_energy})
- ✓ Acoustic match: {acousticness}
- (Optional) High danceability: {danceability}

---

## Future Enhancements

1. **Genre fuzzy matching** (indie pop ≈ pop)
2. **Mood similarity** (relaxed ≈ chill)
3. **Valence weighting** (capture happiness separately from mood)
4. **Temporal weighting** (prefer newer songs)
5. **Popularity penalty** (discover underrated songs)
6. **A/B testing** different weight configurations

---

## Summary

| Component | Points | Type | Range |
|-----------|--------|------|-------|
| Genre (G) | 2.0 or 0.0 | Binary (match/no match) | 0-2.0 |
| Mood (M) | 2.0 or 0.0 | Binary (match/no match) | 0-2.0 |
| Energy (E × 1.5) | 0-1.5 | Continuous (distance) | 0-1.5 |
| Acousticness (A) | 0-1.0 | Preference-based | 0-1.0 |
| Danceability (D × 0.3) | 0-0.3 | Conditional bonus | 0-0.3 |
| **Total Score** | **0-6.0** | **Weighted sum** | **0-6.0** |

**Key Insight:** Binary features (genre, mood) worth 4.0 combined dominate → matching these is necessary but not sufficient. Continuous features (energy, acousticness) worth 2.0 combined provide fine-grained differentiation.
