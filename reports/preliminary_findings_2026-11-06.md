# Preliminary Findings (Week 2 draft)

## Data source change

We replaced the Kaggle and Ohio State combine files with nflverse, an open, maintained data project sourced from Pro Football Reference (PFR). It provides combine drills, draft results and career outcomes that join on a shared PFR player ID, plus game-level snap counts for every NFL player since 2012. This removes the fuzzy name matching and fills the 2020 to 2024 draft gap. It also gives us post-draft production, which we did not have before.

## Sample

- **3,096 combine participants** across the 2016 to 2024 draft classes (319 to 337 per year, except 464 in 2021). The 2024 class is included (321 players).
- **2,016 were drafted (65.1%) and 1,080 went undrafted (34.9%).** Of the 2,308 players drafted in those years, 87.3% appear in the combine data. The 292 who do not are mostly round 6 and 7 picks (220 of 292).
- **2,359 participants (76.2%) played at least one regular-season NFL snap through 2025:** 95.4% of drafted players and 40.3% of undrafted players.
- PFR IDs link 93.1% of participants to NFL outcomes. The source combine table left 103 drafted players without an ID or draft info, and we recovered them with name, class and college checks. The remaining 214 unlinked players (all undrafted) never appear in NFL snap data and are coded as never having played.

## Drill coverage

| Drill | Filled (all years) | 2016 to 2021 | 2022 to 2024 |
|---|---|---|---|
| 40-yard dash | 79.9% | 84.2% (range 78% to 100%) | 70.3% |
| Vertical | 77.5% | 80.5% | 70.9% |
| Broad jump | 75.7% | 78.6% | 69.2% |
| Bench | 57.9% | 72.5% | 25.5% |
| Shuttle | 53.0% | 63.4% | 29.9% |
| 3-cone | 50.0% | 61.0% | 25.7% |

- The 40-yard dash is the most complete drill and is available for at least 68% of every class, so it is a workable primary predictor. Shuttle coverage collapses after 2021, so any shuttle analysis will rest mainly on the 2016 to 2021 classes.
- 50.3% of participants have both a 40 and a shuttle time.
- **Missing drills are not random.** First-round picks have the lowest fill rates for bench (49%), 3-cone (43%) and shuttle (45%), because top prospects often skip drills. A complete-case analysis will under-represent the best players, and we will need to account for this.
- **2021 is a special case.** The 2021 Combine was cancelled because of COVID-19, so 2021 values are pro day results for a larger pool. We flag these rows and will test sensitivity to excluding them.

## Measuring NFL value with unequal career lengths

With 2025 as the last complete season, the 2016 class has 10 seasons and the 2024 class has 2. Career totals are therefore not comparable (median career AV for drafted non-specialists: 12 for 2016, 3 for 2024). We built two normalized outcomes:

1. **AV per eligible season** (career weighted Approximate Value divided by seasons since the draft). The class means are fairly stable, from 2.0 to 3.0, but this outcome exists only for drafted players.
2. **Two-year snap share**: the share of team snaps a player was on the field for over their first two NFL seasons, counting missed games as 0. It is available for all nine classes and for undrafted players. Class means for drafted non-specialists range from 0.28 to 0.34.

Two-year snap share tracks AV closely. The Spearman correlation with AV per eligible season is 0.85, and for the 2016 to 2019 classes, two-year snap share against eventual career AV is 0.83. We therefore propose two-year snap share as the primary outcome, with AV per eligible season as a secondary outcome for drafted players.

## First look at speed (descriptive only)

40 times differ sharply by position (median 4.50 for WR and DB, 5.21 for OL), so all comparisons are within position group. The within-position rank correlations between 40 time and two-year snap share are all negative (faster players played more) for all eight non-specialist groups:

| Position group | n | Spearman (40 vs 2-yr snap share) |
|---|---|---|
| LB | 244 | -0.46 |
| TE | 136 | -0.44 |
| WR | 376 | -0.36 |
| OL | 405 | -0.34 |
| DB | 498 | -0.33 |
| RB | 240 | -0.33 |
| DL | 422 | -0.23 |
| QB | 108 | -0.04 |

These are unadjusted correlations. Speed also drives draft position, and draft position drives playing time, so part of this association likely runs through draft capital. Our next step is to model outcomes on 40 time while controlling for draft slot and position, which tests whether speed predicts value **beyond** what teams already price into the draft.
