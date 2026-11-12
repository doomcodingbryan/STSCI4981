# One-time setup instructions for Claude Code

Bryan: copy the contents of this folder into the root of your GitHub repo, open Claude Code in the repo, and say:

> Read SETUP.md and CLAUDE.md, then follow SETUP.md.

---

## Instructions for Claude Code

The repo should already contain these files and folders, copied in by hand: `CLAUDE.md`, `README.md`, `requirements.txt`, `.gitignore`, `raw/`, `data/`, `scripts/`, `notebooks/`, `figures/` and `reports/`. Read `CLAUDE.md` first; it holds all project decisions. Do not change cleaning logic or re-download data during setup.

1. **Check the files.**
   - Confirm the three CSVs in `raw/`, the analysis CSV in `data/`, and both scripts in `scripts/`.
   - If the repo already had other files (for example an old Kaggle/Ohio State notebook or a default README), list them for Bryan and ask whether to keep, move into `archive/`, or delete them. Do not delete anything without asking.

2. **Set up the environment.**
   - Create a virtual environment: `python -m venv .venv` (Python 3.11 or newer; 3.13 was used to build the data).
   - Activate it and run `pip install -r requirements.txt`.
   - If a pinned version fails to install on this machine, install the nearest available version and note it for Bryan.

3. **Rebuild from the committed raw snapshot and verify.**
   - Run `python scripts/build_dataset.py`. It must print `analysis table: (3096, 55), picks without combine: 292`.
   - Run `python scripts/data_quality_report.py > data/quality/report_tables.md`.
   - Then check these values in `data/combine_draft_outcomes_2016_2024.csv`:
     - `drafted.sum()` = 2016
     - `made_nfl.sum()` = 2359
     - `pfr_id.isna().sum()` = 214
     - `pfr_id_source` counts: combine 2735, name_match_draft_picks 88, name_match_snap_counts 44, lastname_college_match_draft_picks 13, manual 2, none 214
   - If anything differs, stop and report it. Do not "fix" it by changing the data.
   - If the rebuilt CSV matches these checks, keep it. Small formatting differences in git diff are fine.

4. **Create `notebooks/01_eda.ipynb`** as a starter. It should:
   - load the clean CSV with a path relative to the repo root;
   - exclude `pos_group == "ST"`;
   - show counts by class and position group;
   - plot 40 time by position group (box plot);
   - plot y2_snap_share against forty, faceted by position group;
   - save figures to `figures/` at 300 dpi.

   Keep it short and well commented. Run it top to bottom to confirm it works. Then pin the installed versions of jupyter, matplotlib, statsmodels and scikit-learn in `requirements.txt`.

5. **Commit and push.**
   - Make sure `.venv/` and checkpoints are ignored.
   - Commit with a message like "Add nflverse data pipeline, clean dataset, project docs and EDA starter".
   - Push to the default branch, or to a branch if Bryan prefers.

6. **Finish.**
   - Delete this `SETUP.md` in a final commit (CLAUDE.md keeps the context).
   - Give Bryan a short summary: what was verified, any version differences, and the next step listed in CLAUDE.md.

Remember the writing rule in CLAUDE.md: no em dashes in anything written for Bryan.
