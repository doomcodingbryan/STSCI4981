# CLAUDE.md: project context for Claude Code

Read this before doing anything in this repo. It records decisions made in earlier sessions so they are not redone or contradicted.

## Who and what

- **Team:** Bryan Chae (byc27) and Matthew Manno (mjm752), Cornell.
- **Course:** STSCI 4981/4982, Sports Analytics in Practice capstone, Prof. Martin Wells. Fall 2026, asynchronous.
- **Research question:** Does NFL Combine speed, especially the 40-yard dash, predict on-field value in the NFL? Draft classes 2016 to 2024.

## Deadlines and deliverables (from the syllabus)

| Due (11:59 PM, Canvas, PDF) | Deliverable |
|---|---|
| Nov 6 | Update 1 (done; text in `reports/`) |
| Nov 13 | Update 2 |
| Nov 29 | Update 3 |
| Dec 7 | Final project |

- **Weekly updates:** about 1 page plus figures, with four sections:
  1. Progress Since the Previous Submission
  2. Preliminary Findings (tables or figures encouraged)
  3. Challenges and Revisions
  4. Next Steps

  They should show substantive progress, not restate the proposal.
- **The final project has three parts:**
  - A 5 to 10 minute recorded presentation.
  - A 6 to 10 page paper with sections for Introduction and Research Question, Data Description, Methodology, Results, Discussion and Implications, and Conclusions and Limitations.
  - Supplementary code and data, organized and documented so others can reproduce the analysis.
- **Grading:** analytical rigor, appropriate use of data and methods, interpretation, **reproducibility**, and clarity. Updates count for 30% of the grade and the final project for 70%.

## Writing style (applies to everything written for Bryan)

- **Never use em dashes.** Use commas, colons, parentheses or separate sentences. Avoid en dashes in ranges too; write "2016 to 2024" or "2016-2024".
- Write in plain student voice ("we"), with concrete numbers, and don't overstate results. Call unadjusted correlations descriptive.
- Refer to players with "their", not "his".

## Repo layout and rules

```
raw/        nflverse snapshot pulled 2026-11-06. Do not edit or re-download.
data/       combine_draft_outcomes_2016_2024.csv = THE analysis table
            draft_picks_without_combine_2016_2024.csv, quality/ = coverage tables
scripts/    build_dataset.py (raw -> data), data_quality_report.py (data -> data/quality)
notebooks/  01_eda, 02_models, 03_figures_for_paper (to be created)
figures/    PNGs saved by notebooks (300 dpi) for updates and the paper
reports/    text of updates and findings drafts
```

- All cleaning happens in `scripts/build_dataset.py`. Notebooks only **read** `data/combine_draft_outcomes_2016_2024.csv`. If cleaning has to change, edit the script, rerun it, and rerun the quality report.
- **Never re-download the raw data.** nflverse updates weekly and AV changes as seasons progress, so a new pull would change numbers already reported. `build_dataset.py` downloads only if a `raw/` file is missing.
- Rebuild: `python scripts/build_dataset.py && python scripts/data_quality_report.py > data/quality/report_tables.md`
- Notebooks must pass "Restart and Run All" before anything is submitted. Each notebook has one owner, to avoid merge conflicts.
- Use Python, not R.

## Data sources and how the table was built

All data comes from nflverse (sourced from Pro Football Reference), loaded with `nflreadpy`. `nfl_data_py` has been archived, so don't use it.
- `load_combine()`: drills, plus draft round, pick and team.
- `load_draft_picks()`: career AV, games, starts, Pro Bowls, All-Pro.
- `load_snap_counts()`: per-game snaps, 2016 to 2026 week 8.

The original Kaggle (2009-2019) and Ohio State (2004-2023) combine files were **dropped**. They had no draft info after 2019, names that didn't match cleanly, no NFL production data, and no 2024 class.

**Join:** `combine.pfr_id = draft_picks.pfr_player_id`. The combine table was missing `pfr_id` for 361 rows, and 103 of them were drafted players with blank draft fields. They were recovered in this order:
1. Exact normalized name plus class year, with college similarity as a tiebreak (88 rows).
2. Last name plus class year plus college similarity of 0.8 or higher (13 rows).
3. Two manual nickname links (Chris/Christian Campbell, Trey/Tracy Walker).
4. Undrafted players matched to snap-count names: unique match only, first snap within 2 seasons of the class year, drafted IDs excluded (44 rows).

The remaining 214 rows (all undrafted) never appear in NFL snap data and are coded as never having played. Column `pfr_id_source` records the method for each row, and `outcome_zero_imputed` flags zero-coded outcomes.

## Key analysis decisions

- **Last complete season is 2025.** The 2026 season is in progress, so all snap-based outcomes stop at 2025.
- PFR `w_av` already stops at 2025. PFR `games` includes 2026 partial games, so it was renamed `games_pfr_incl_2026`; don't use it. Use `games_played`.
- **Primary outcome: `y2_snap_share`.** For each of the player's first two NFL seasons, take max(offense %, defense %) per game, sum it, and divide by all team games (16 per season through 2020, 17 from 2021). Missed games count as 0. It covers all 9 classes and undrafted players. `y3_snap_share` is the same for 2016 to 2023 only.
- **Secondary outcome: `w_av_per_eligible_season`** = career weighted AV divided by (2025 minus class plus 1). Drafted players only; busts count as 0. Blank PFR AV for drafted players means they never played, coded 0.
- **Validation:** among drafted non-specialists, Spearman(y2_snap_share, w_av_per_eligible_season) = 0.85. For the 2016 to 2019 classes, Spearman(y2_snap_share, career w_av) = 0.83.
- **Exclude specialists** (`pos_group == "ST"`: K, P, LS). Their snap share is about 0.
- **Positions:** always compare within `pos_group` (QB, RB, WR, TE, OL, DL, LB, DB, ST), because PFR labels change by year. EDGE players land in DL or LB depending on the year.
- **Extra speed columns:** `forty_z_pos` (within-group z-score, negative means faster) and `speed_score` = wt × 200 / forty^4.

## Known caveats (must appear in the paper's limitations)

1. **Missing drills are not random.** First-round picks have the lowest fill rates for bench (49%), 3-cone (43%) and shuttle (45%), because top prospects skip drills. Complete-case analysis under-represents the best players.
2. **2021 Combine was cancelled (COVID).** 2021 values are pro day results for a larger pool of 464 players. They are flagged by `pro_day_2021`; run a sensitivity check without them.
3. **2016 forty fill rate is 99.7%, versus about 80% from 2017 on.** The source likely recorded that year differently. Run a sensitivity check without 2016.
4. **Shuttle coverage drops after 2021** (about 30% for 2022 to 2024), so shuttle analysis relies mainly on 2016 to 2021.
5. **292 picks (12.7%) have no combine record**, mostly rounds 6 and 7.
6. Values are Combine results only; there is no pro day data except 2021.

## Numbers already reported (keep later write-ups consistent)

- 3,096 combine participants: 2,016 drafted (65.1%) and 1,080 undrafted.
- 87.3% of the 2,308 picks from 2016 to 2024 have combine data.
- 76.2% played at least one REG snap through 2025 (95.4% of drafted, 40.3% of undrafted).
- 93.1% of participants have a PFR ID.
- 40-yard dash fill: 79.9% overall, 84.2% for 2016 to 2021, 70.3% for 2022 to 2024.
- Shuttle fill: 53.0% overall, 63.4% for 2016 to 2021, 29.9% for 2022 to 2024.
- Within-position Spearman correlation between 40 time and y2 snap share, by group:

  | LB | TE | WR | OL | DB | RB | DL | QB |
  |---|---|---|---|---|---|---|---|
  | -0.46 | -0.44 | -0.36 | -0.34 | -0.33 | -0.33 | -0.23 | -0.04 |

  These are unadjusted, and draft position is a likely confounder.

## Status and next steps (as of 2026-11-12)

Done: data build, quality report, Update 1. The revised text is in `reports/`; check with Bryan which version was actually submitted.

Next, roughly in order:
1. Create `notebooks/01_eda.ipynb`: distributions of 40 time by position, outcome distributions, and a scatter of 40 time against y2 snap share by position.
2. `notebooks/02_models.ipynb`:
   - Regress y2_snap_share on forty within position group, then add draft pick (log of overall pick, or round) to test whether speed predicts value **beyond draft position**.
   - Compare forty, forty_z_pos and speed_score.
   - Consider a drafted-only AV model as the secondary analysis.
3. Decide how to handle players who skipped drills: compare drafted players with and without a 40, and consider a missingness indicator or imputation.
4. Run the sensitivity checks: drop 2021, drop 2016, keep only `pfr_id_source == "combine"`.
5. Shuttle analysis on 2016 to 2021.
6. Update 2 (due Nov 13): first model results plus the methodological decisions above.
