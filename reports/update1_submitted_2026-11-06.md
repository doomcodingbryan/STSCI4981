# Update 1, as actually submitted to Canvas on November 6, 2026

This is the version Prof. Wells received. `update1_revised_2026-11-06.md` is a longer draft
that was NOT submitted. When writing later updates, assume the reader has only seen this text.

---

Bryan Chae (byc27) & Matthew Manno (mjm752)
STSCI 4981/4982 - Sports Analytics in Practice / Sports Strategy Capstone
Prof. Martin Wells
November 5, 2026
Update 1 - November 6

## Progress Since the Previous Submission

The main objective of our project's opening week is data collection and cleaning. We collected the data from the sources outlined in the proposal. We used nflverse, an open, actively maintained data project sourced from Pro Football Reference (PFR). We use three of its tables: combine results, draft picks with career outcomes such as Approximate Value (AV), games, starts and Pro Bowls, and game level snap counts for every NFL player. We built a single analysis table of 3,096 combine participants from the 2016-2024 draft classes, linking each player to their draft result and NFL playing time through the 2025 season.

## Preliminary Findings

Of the 3,096 combine participants, 2,016 (65%) were drafted and 1,080 were not. Of the 2,308 players drafted from 2016 to 2024, 87% attended the Combine. Through the 2025 season, 76% of participants played at least one regular-season NFL snap (95% of drafted players and 40% of undrafted players). The 40-yard dash is our most complete drill, recorded for 80% of participants.

## Challenges and Revisions

The nflverse combine table was missing player IDs for 361 participants, 103 of whom were drafted. We recovered the drafted players by matching on name, draft year and college. The remaining 214 were all undrafted and never appear in NFL snap data, so we treat them as never having played. The 2021 Combine was cancelled because of COVID-19, so 2021 measurements are pro day results, which tend to be faster. We flag these players and will check whether results change without them.

## Next Steps

By the next written update, we expect to have our data sets finished cleaning, and ready for analysis. We will deliberate our method of analysis, and also have that decided upon next week. We should be able to begin analyzing the data next week, and have preliminary findings to report.
