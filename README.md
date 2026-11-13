# NFL Combine Speed and NFL Value: Data Build (2016 to 2024 draft classes)

STSCI 4981/4982 capstone, Bryan Chae (byc27) and Matthew Manno (mjm752). Data pulled 2026-11-06.

## Files

| Path | What it is |
|---|---|
| `data/combine_draft_outcomes_2016_2024.csv` | **Analysis table.** One row per combine participant, 2016 to 2024 (3,096 rows, 55 columns). |
| `data/draft_picks_without_combine_2016_2024.csv` | 292 drafted players with no combine record (reference only). |
| `data/quality/*.csv`, `data/quality/report_tables.md` | Coverage, missingness and descriptive tables. |
| `raw/` | Unmodified nflverse downloads (combine, draft picks, snap counts). |
| `scripts/build_dataset.py` | Builds the analysis table from `raw/` (downloads if missing). |
| `scripts/data_quality_report.py` | Rebuilds every table in `data/quality/`. |
| `notebooks/` | Exploration, models and paper figures. Notebooks read the clean CSV only. |
| `figures/` | Figures saved by notebooks for the updates and paper. |
| `reports/` | Text of the weekly updates and findings drafts. |
| `CLAUDE.md` | Project context for Claude Code sessions. |

## Run the notebooks in your browser (no install)

Both notebooks open and run in Google Colab. Click a badge, then Runtime > Run all.
The first cell downloads this repo so the data is there; nothing needs to be installed.

| Notebook | Open |
|---|---|
| `notebooks/01_eda.ipynb` (distributions and scatters) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/doomcodingbryan/STSCI4981/blob/main/notebooks/01_eda.ipynb) |
| `notebooks/02_models.ipynb` (speed vs draft position) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/doomcodingbryan/STSCI4981/blob/main/notebooks/02_models.ipynb) |

A Colab session is your own scratch copy: running cells changes nothing in this repo.
To send changes back, use File > Save a copy in GitHub, which needs write access to the repo.

Rebuild everything from scratch:

```bash
pip install -r requirements.txt
python scripts/build_dataset.py && python scripts/data_quality_report.py > data/quality/report_tables.md
```

`nfl_data_py` has been archived, so this uses `nflreadpy`. It reads the same nflverse release files.

## Sources (all nflverse, sourced from Pro Football Reference)

- `load_combine()`: drills, plus draft round, pick and team for drafted players.
- `load_draft_picks()`: career outcomes (AV, games, starts, Pro Bowls, All-Pro).
- `load_snap_counts()`: per-game offense, defense and special teams snaps, 2016 to 2026 week 8. This is the only per-season source, and it covers undrafted players too.

## How the join works

1. **PFR ID join** (`combine.pfr_id = draft_picks.pfr_player_id`): 2,735 rows, which includes 1,913 drafted players. All picks agree exactly with the combine table's `draft_ovr`.
2. **The combine table has gaps.** 361 rows had no `pfr_id`, and 103 of them were actually drafted, with blank draft fields too. Examples: Asante Samuel Jr., Tre'Quan Smith, Olu Fashanu, Lukas Van Ness, Byron Murphy II. These were recovered by:
   - exact normalized name plus class year, with college similarity as a tiebreak (88 rows);
   - last name plus class year plus college similarity of 0.8 or higher (13 rows, e.g. "Olumuyiwa" Fashanu, "Theodore" Johnson);
   - 2 hand-verified nicknames (Chris/Christian Campbell, Trey/Tracy Walker).
3. **Undrafted players who played** were linked to snap counts on exact normalized name, keeping only a unique match whose first NFL snap came within 2 seasons of the class year. IDs belonging to any drafted player were excluded (44 rows).
4. **214 rows remain without an ID.** None appear in snap counts under their name, so they are coded as never playing (`outcome_zero_imputed = True`).

The source of every ID is in `pfr_id_source`. To run a robustness check, drop the rows whose source is not `combine`.

## Outcome definitions (handling short careers)

- **Last complete season is 2025.** The 2026 season is in progress, and every snap-based column stops at 2025.
- PFR `w_av` and `dr_av` already stop at 2025 (all 2026 picks have AV = 0).
- PFR `games` *does* include 2026 partial games, so it is renamed `games_pfr_incl_2026`. Use `games_played` instead.

| Column | Definition | Comparable across classes? |
|---|---|---|
| `w_av`, `dr_av` | PFR career weighted AV, and AV with the drafting team, through 2025. Drafted only. Blank in PFR means the player never played, coded 0. | No, grows with career length |
| `seasons_eligible` | 2025 minus draft class plus 1 (2 for 2024, 10 for 2016) | |
| `w_av_per_eligible_season` | `w_av / seasons_eligible`. Busts count as 0. **Recommended AV outcome.** | Mostly |
| `w_av_per_season_played` | `w_av / seasons_played`. Conditional on making a roster. | Mostly |
| `y2_snap_share` | Over the player's first 2 NFL seasons: sum over games of max(offense %, defense %), divided by all team games (16 per season through 2020, 17 from 2021). Missed games count as 0. Covers undrafted players. **Recommended primary outcome.** | Yes, all 9 classes |
| `y3_snap_share` | The same over 3 seasons. Blank for 2024. | Yes, 2016 to 2023 |
| `y2_games`, `y2_games_50pct`, `y2_scrimmage_snaps` (and `y3_`) | Games with any snap, games with at least 50% of snaps (a starter proxy), and offense plus defense snaps | Yes |
| `seasons_played`, `games_played`, `games_50pct_snaps`, `scrimmage_snaps` | Career totals through 2025 from snap counts | No |
| `made_nfl` | At least one regular-season snap through 2025 | |

**Why snap share, and why not per-season AV:** nflverse publishes AV only as a career total. PFR has season-by-season AV on player pages but blocks automated scraping. Snap share over a fixed window is available for every class and for undrafted players. Snap share is not "value", but it measures how much NFL teams chose to play someone. It tracks AV closely: among drafted non-specialists, the Spearman correlation between `y2_snap_share` and `w_av_per_eligible_season` is 0.85. For the 2016 to 2019 classes, `y2_snap_share` against eventual career `w_av` is 0.83, so the 2-year window is a good early proxy for long-run value.

**Specialists:** K, P and LS (`pos_group == "ST"`) play almost only special teams snaps, so their snap share is near 0. Exclude them.

## Other columns

- `pos_group`: PFR position labels change by year (for example, 2019 to 2021 use "OL" and "DL" in place of OT/OG/C and DE/DT, and "EDGE" appears in 2018). Groups: QB, RB (with FB), WR, TE, OL, DL (DE, DT, DL, EDGE), LB (LB, ILB, OLB), DB (CB, S, SAF, DB), ST. EDGE players are split between DL and LB depending on the year's label.
- `forty_z_pos`: forty z-score within `pos_group`, pooled over 2016 to 2024 (negative means faster).
- `speed_score`: weight times 200, divided by forty to the fourth power (Barnwell).
- `pro_day_2021`: True for the 2021 class. **The 2021 Combine was cancelled**, so PFR lists pro day results, and the 2021 pool is larger (464 rows, 241 undrafted). Pro day times on fast tracks usually run faster than Combine times.

## Known data caveats

1. **Missing drills are not random.** First-round picks have the lowest fill rates for bench (49%), cone (43%) and shuttle (45%). Top prospects often skip drills. Treat this as a selection issue, not as noise.
2. **Shuttle and cone collapse after 2021:** shuttle fill went from 48% to 77% in 2016 to 2021 down to 28% to 31% in 2022 to 2024. Bench fell to 22% to 32%. A shuttle analysis will mostly rest on 2016 to 2021.
3. **2016 forty fill is 99.7%, versus about 80% in 2017.** Every class from 2010 to 2016 in the source is 98% to 100%, so the source likely changed how it handles players who skipped the Combine 40. Run a sensitivity check with 2016 dropped.
4. Combine values only. Pro day times are not in this data, except for 2021.
5. 292 picks (12.7%) have no combine record. Most are round 6 and 7 picks (220), so combine participants are slightly more highly drafted than the full draft.
