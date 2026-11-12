Bryan Chae (byc27) & Matthew Manno (mjm752)
STSCI 4981/4982 - Sports Analytics in Practice / Sports Strategy Capstone
Prof. Martin Wells
Update 1 - November 6, 2026

1. Progress Since the Previous Submission

The main objective of our opening week was data collection and cleaning. We began with the two sources outlined in our proposal: a Kaggle combine data set (2009-2019), which includes draft information but not the shuttle run, and an Ohio State data set (2004-2023), which includes the shuttle but not draft information. Combining them proved difficult. The 2020-2023 records had no draft information, some earlier records did not match cleanly on player name, neither source covered the 2024 class, and neither contained any measure of NFL production after the draft.

We therefore switched to nflverse, an open, actively maintained data project sourced from Pro Football Reference (PFR). We use three of its tables: combine results (including the shuttle), draft picks with career outcomes such as Approximate Value (AV), games, starts and Pro Bowls, and game-level snap counts for every NFL player. The tables share a PFR player ID, so most records join directly without matching on names. We built a single analysis table of 3,096 combine participants from the 2016-2024 draft classes, linking each player to their draft result and NFL playing time through the 2025 season. This keeps the 2024 class in our timeframe.

2. Preliminary Findings

No modeling has been done yet, but the data build gives us a clear picture of the sample.

Of the 3,096 combine participants, 2,016 (65%) were drafted and 1,080 were not. Of the 2,308 players drafted from 2016 to 2024, 87% attended the Combine; most of those who did not were sixth- or seventh-round picks. Through the 2025 season, 76% of participants played at least one regular-season NFL snap (95% of drafted players and 40% of undrafted players).

The 40-yard dash is our most complete drill, recorded for 80% of participants (84% for 2016-2021 and 70% for 2022-2024). The shuttle is recorded for 53% overall but only 30% for 2022-2024, and the bench press and 3-cone show the same drop after 2021. Missing drills are not random: first-round picks have the lowest completion rates for the shuttle (45%), 3-cone (43%) and bench (49%), likely because top prospects choose to skip drills.

Because the 2016 class has ten NFL seasons and the 2024 class only two, career totals are not comparable across classes. We created two normalized outcomes: AV per season since the draft (drafted players only), and two-year snap share, the fraction of team snaps a player was on the field for over their first two seasons, with missed games counted as zero. Two-year snap share is available for every class and for undrafted players, and it tracks AV closely (Spearman correlation of 0.85). For the 2016-2019 classes, it correlates at 0.83 with eventual career AV, which supports using it as an early measure of value.

As a first descriptive look, faster 40 times are associated with higher two-year snap share within every position group except quarterbacks (Spearman correlations of -0.23 to -0.46). These correlations are unadjusted. Faster players also tend to be drafted earlier, and earlier picks receive more playing time, so part of this association likely reflects draft position rather than speed itself.

3. Challenges and Revisions

The data source change resolved the three problems from our proposal: missing draft information after 2019, unreliable name matching, and the lack of post-draft production and 2024 data. Several new issues came up during cleaning:

- The nflverse combine table was missing player IDs for 361 participants, 103 of whom were drafted. We recovered the drafted players by matching on name, draft year and college. The remaining 214 were all undrafted and never appear in NFL snap data, so we treat them as never having played. Each record notes how it was matched so we can test whether these recovered records affect results.
- The 2021 Combine was cancelled because of COVID-19, so 2021 measurements are pro day results, which tend to be faster. We flag these players and will check whether results change without them.
- Nearly every 2016 participant has a 40 time, compared with about 80% in later years, which suggests the source recorded that year differently. We will run a sensitivity check excluding 2016.
- PFR's position labels change from year to year (for example, "EDGE" versus "DE" or "OLB"), so we grouped positions into nine consistent categories.
- Low shuttle coverage after 2021 means any shuttle analysis will rely mainly on the 2016-2021 classes.

4. Next Steps

Next week we will finalize our outcome measures, with two-year snap share as the primary outcome and AV per season as a secondary outcome for drafted players. We will then model these outcomes on 40 time within position groups, controlling for draft position, to test whether speed predicts NFL value beyond what teams already account for on draft day. We also plan to compare a size-adjusted speed measure with the raw 40 time, decide how to handle players who skipped drills, and run the sensitivity checks described above.
