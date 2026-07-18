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

<!-- e.g., Strategy, Factory, Observer, etc. -->

**How did AI help you brainstorm or implement it?**

<!-- Describe the conversation or suggestions that led to your decision -->

**How does the pattern appear in your final code?**

<!-- Point to the relevant class or method -->
