# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

SoundRadar 1.0

---



## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

SoundRadar 1.0 is designed to recommend songs based on a user's stated preferences for genre, mood, energy level, and acoustic/electronic instrumentation.  It uses content based filtering to match song characteristics against user profiles.  When doing this, the recommender makes the assumption that user can articulate what they like and that these preferences predict how much they will enjoy a given song.  It utilizes different weightings through a formula in order to create various recommendation outcomes.  This leads to the revelation of both strengths and biases in algorithmic systems.  The recommender is built for classroom exploration and learning about how recommendation algorithms work, not for production use with real users.

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

SoundRadar rates each song by comparing it against what you tell us you like, using five key features: genre, mood, energy level.  It also checks whether you prefer acoustic or electronic instruments, and danceability.  For genre and mood, we check if the song matches exactly.  If it is a match, it gets bonus points and if not, it starts at zero for that feature.  For energy, we measure how close the song's energy is to your target.  This means a song at 0.8 energy scores high if you want 0.8 energy, but lower if you want something mellow.  Your acoustic preference works like a slider, so if you like acoustic music then acoustic songs score higher.  However, if you prefer electronic then the electronic songs win out.  Finally, there is a bonus to danceable songs, but only if you're looking for high-energy music.  We combine all these scores together to create a total ranking, with genre and mood getting the most weight because they're usually deal-breakers for whether a song feels right to you.  The starter code had placeholder implementations, so I built a complete working system with the Genre-Mood-Energy weighted scorer that assigns specific weights to each feature.  I also implemented an experimental weight-shift version to test how changing priorities affects recommendations.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

The SoundRadar catalog contains 20 songs across 16 genres (pop, rock, lofi, electronic, classical, indie, jazz, synthwave, hip-hop, country, reggae, soul, blues, ambient, experimental, and dubstep) and 12 distinct moods (happy, intense, chill, meditative, energetic, uplifting, nostalgic, melancholic, relaxed, focused, moody, and dark).  We expanded the original starter dataset by adding 10 new songs to ensure broader genre and mood representation and to test the algorithm against diverse user preferences.  Each song includes numerical features like energy (0.15 to 0.93), tempo, valence, danceability, and acousticness, which allow us to measure similarity across multiple dimensions.  However, the dataset has significant limitations in that most genres are represented by only 1-2 songs.  This means that lyrics and semantic meaning are missing and there is no information about artist popularity or user engagement history.  These gaps mean the recommender cannot handle learning from what similar users like.  It is also unable to understand lyrical themes and how cultural significance would play a role in a songs appeal to the user.

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

SoundRadar works best for users with mainstream genre and mood preferences (pop/happy, lofi/chill, rock/intense).  This is because the catalog has multiple songs in these categories, giving them several high-scoring options.  The energy distance based scoring is particularly effective.  Users looking for mellow music reliably get slower songs, while high-energy seekers get fast and danceable tracks.  This is accurate to what one would imagine real listening behavior to be.  The acoustic/electronic preference slider also captures an important musical distinction well.  Users who state they like acoustic music consistently receive acoustic songs, while electronic music enthiusiasts get recommended synthesized and electronic-sounding tracks.  The danceability bonus for high-energy users is intuitive because energetic music and danceability have a strong correlation with one another. For this reason, adding this bonus feels justified for the purpose of making sure high energy enjoyers are happy.  Testing confirmed that users with clear, coherent preferences like someone who wants pop AND happy AND high energy tend to get excellent recommendations that match my intuition.  Finally, the content only approach allows the recommender to suggest songs to new users without needing their listening history which is outside of the scope of this project.

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



In evaluating the recommendations, I focused on whether the top-ranked songs matched stated preferences and whether scores reflected intuitive quality differences between perfect matches and mismatches.  I also tracked how the algorithm handled contradictory preferences and whether it could discover songs outside a user's stated genre. These factors became key indicators of fairness and flexibility.

The most surprising discovery was that the algorithm creates a two-tier system where mainstream users get abundant choices and high scores while niche genre users hit a hard ceiling immediately.  I ran several comparative tests including edge case profiles with conflicting preferences and extreme energy values to understand how different user types rank the same songs.  These tests revealed that weight choices have dramatic impacts on recommendation fairness and which users benefit from the system.

---

## 8. Intended and Non-Intended Use

SoundRadar is used for testing different user profiles and comparing  algorithm variants on a small scale.  Do not use it for large scale music recommendations, as it lacks collaborative filtering, user feedback learning, and the large catalogs that real recommenders need.

---

## 9. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

The first priority would be adding lyrical and semantic song similarity to deal with the very limiting genre filter bubble.  Right now the system recommends songs from different genres only if energy matches perfectly.  However, adding emotional or thematic analysis would allow for the recommendation of an indie song if it captures the same intensity a user wants from rock.  Better explanations could display each feature visually and include insights from similar users, like showing that fans of a certain artist also enjoyed these songs.  In order to gain diversity in results, a new ranking algorithm could ensure the top five doesn't return several songs by the same artist or subgenre.  This would give users significantly more variety to explore.  Finally, adding collaborative filtering would help the system learn patterns from groups of similar users, which would reduce reliance on users' ability to articulate exactly what they want.

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

Building this project taught me that small design choices in algorithms have huge impacts on what songs different users will experience.  What surprised me most was discovering how quickly a simple rule like matching genre exactly creates significant unfairness.  While mainstream users got great recommendations, and niche users got more dubious suggestions.  It became clear that every weight I assign is actually a choice about which users I want to favor.  After building this, when I use Spotify I try to gain an understanding of the algorithmic decisions that created my recommendations.  It is clear that building a good recommender is about fairness and understanding how your algorithm design affects people's listening experience.

AI helped me brainstorm test cases and generate sample data quickly, but I had to carefully check that the tests actually made sense and tested what I wanted to test.  My AI assistant was good for quickly implementing logic but this logic often required multiple revisions as it would have unnecessary complexity.  I was very surpirsed by how simple the algorithm ended up being.  All it did was counting matches and measuring distances but it still felt like it had a decent understanding of music choices.  If I extended this project, I would try to implement lyrical analysis to add depth to recommendations and build a visual interface so users could use the recommender in the browser properly while also getting more feedback on each recommendation.

