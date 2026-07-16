# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users


Phase 4 Step 4: Identify Limitations and Bias

The algorithm creates a severe genre filter bubble due to binary genre matching (0.0 or 2.0 points in my algorithm). With 14 out of 16 genres represented by only a single song, users preferring niche genres like synthwave or jazz get exactly one matching recommendation before hitting a hard ceiling where non-matching songs max out at 3.5 score. This eliminates discovery across genre entirely since there is no way to recommend similar genres. During testing, users with common genre preferences consistently received higher-scoring and more diverse recommendations than users with niche preferences. This reveals the issue that hard preference matching can trap users into isolated bubbles.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

I tested six user profiles across the spectrum: high-energy pop fans, chill lofi listeners, intense rock fans, and four adversarial edge cases (extreme low energy, conflicting mood/energy, niche genres, acoustic-rock contradiction). What surprised me was how severely the algorithm penalizes users outside the mainstream. A synthwave fan got one perfect match (6.5 score) then everything else capped at 2.5. However, a pop fan had three viable options all above 4.0. I also ran a weight-shift experiment (halving genre importance, doubling energy importance) which revealed that energy matching could override genre in some cases, but this helped some users while hurting others. Energy focused users discovered cross-genre options like hip-hop with ideal energy. Additionally, genre focused users saw non-matching genres get ranked higher showing that weight choices reflect what the system prioritizes. 

Profile Comparisons:

High-Energy Pop vs. Chill Lofi: Energy level is the biggest difference—they get almost completely different songs. Pop fan gets upbeat dance songs, lofi fan gets mellow acoustic ones. Energy matters more than anything else.

High-Energy Pop vs. Deep Intense Rock: Both like fast music, but the pop fan gets happy songs while the rock fan gets dark, intense songs. Same energy, different mood—the mood preference changes which songs appear at the top.

High-Energy Pop vs. Niche Genre (Synthwave): Pop fan has many good choices. Synthwave fan has one perfect match, then nothing else scores well. Mainstream genres get more variety than niche ones.

Chill Lofi vs. Extreme Low Energy (Classical): Both like quiet music, but classical fan wants even quieter. The tiny energy difference (0.38 vs 0.10) matters a lot—perfect matches vs. good-enough matches.

Deep Intense Rock vs. Acoustic Rock Contradiction: Same rock and intensity, but one likes acoustic and one likes electric. Both still rank the electric rock song first—acousticness doesn't override the stronger signals of genre and mood.

Conflicting Energy and Mood vs. Normal Pop Fan: Wanting high energy AND sad mood is a contradiction that tanks the scores. Pop fan gets 6.53 for their top song, conflicting fan only gets 3.84. The system doesn't handle conflicting signals well.

Extreme Low Energy vs. Extreme High Energy: Complete opposites. One gets quiet classical songs, the other gets heavy electronic bangers. Zero overlap—energy divides the catalog completely.

Niche Synthwave vs. Mainstream Pop: Pop genre has multiple songs in the catalog. Synthwave has one. The recommendation system is unfair to users who like rare genres because there simply isn't much to recommend.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
