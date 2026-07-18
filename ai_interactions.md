# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I asked the AI agent to enhance the music recommender with advanced song features and expand the catalog to improve accuracy.  First, I wanted five new complex attributes, popularity ratings, release decades, vocal style, production quality, and emotional arc added to the dataset.  I then asked it to fix logical issues in the scoring algorithm and finally generate 10 new songs targeting underrepresented genres to see if catalog expansion would improve recommendation quality for niche users.

**Prompts used:**

- "Introduce 5 complex attributes to your dataset that are not currently present in the baseline data"
- "Are there any logical issues with the new function you added in recommender.py?"
- "Change the decade distance, make the binary features gradual for consistency, and reweight the features more evenly"
- "Would adding more songs aid the accuracy?"
- "How many new songs would you suggest I add?"
- "Generate 10 new songs and run everything again to make sure the change was successful"

**What did the agent generate or change?**

The agent added 10 songs across underrepresented genres (synthwave, classical, jazz, country, blues, and ambient) to the CSV.  It also created similarity functions to make categorical feature scoring more gradual and fair.  It refactored the decade distance calculation to make sure the score did not swing too harshly and reweighted the advanced features to contribute equally.  The changes improved the recommender from 20 to 30 songs while maintaining backward compatibility with all existing code.

**What did you verify or fix manually?**

When I reviewed the agent's initial implementation, I spotted a number of issues worth addressing.  For the new decade comparison feature, the decade distance formula was made such that songs more than a century away got zero points.  The vocal, production, and emotional arc features were purely binary, which made them swing recommendations very significantly.  This meant that the weights weren't balanced, since the new binary features dominated overall importance.  I asked the agent to refactor these, creating similarity functions that reward partial matches.  This ensured that all five advanced features contributed equally.  After the revisions, I made sure all of the tests passed and verified the accuracy improvements, which were withing the expected range.

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

I chose the Hybrid Strategy Pattern combined with configuration objects.  Each scoring mode is implemented as a `WeightedScoringStrategy` that wraps a `ScoringWeights` configuration.  This lets the same scoring logic produce different results based on which weights are active.  This makes it easy to switch between modes without sacrificing modularity.

**How did AI help you brainstorm or implement it?**

After asking it to brainstorm, the AI agent presented me with four different design approaches.  Pure Strategy classes created too much repetition with minimal variation for the modes I wanted to implement.  Pure configuration dictionaries couldn't accommodate custom logic when a mode needed special behavior.  Enum mapping would have scattered the scoring logic across multiple separate functions, making it harder to maintain.  The hybrid approach offered the right balance between simplicity and flexibility.  After explaining why the hybrid approach balances simplicity with extensibility, the agent provided a working implementation that I integrated into the recommender.  The implementation included creating a `ScoringWeights` dataclass to store weight configurations, defining a `ScoringStrategy` base class for all modes to inherit from, and then registering four concrete mode instances that could be selected via command-line arguments.

**How does the pattern appear in your final code?**

In `src/recommender.py`:
- `ScoringWeights` dataclass (line ~50-60) holds weight configuration for each component
- `ScoringStrategy` ABC (line ~62-72) defines the interface all scoring strategies must implement
- `WeightedScoringStrategy` (line ~74-160) implements the scoring logic by applying weights from ScoringWeights
- Four mode definitions: `GENRE_FIRST`, `DISCOVERY`, `NICHE_FRIENDLY`, `PERSONALITY` (line ~162-225)
- `SCORING_MODES` registry dict (line ~227-232) maps mode names to strategy instances
- `get_strategy(mode_name)` function (line ~234-237) for clean mode lookup
- Updated `recommend_songs()` function (line ~362-375) accepts a `mode` parameter and delegates to the strategy's `score()` method

In `src/main.py`:
- Argument parser (line ~118-123) accepts `--mode` CLI parameter
- `main()` function (line ~82) accepts mode parameter and passes it to `recommend_songs()`
- Mode validation and help text display (line ~97-103)
