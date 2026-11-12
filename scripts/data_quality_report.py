"""Descriptive stats and data quality tables for the analysis table. Writes data/quality/*.csv
and prints markdown. Run after build_dataset.py."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "data" / "combine_draft_outcomes_2016_2024.csv")
picks = pd.read_csv(ROOT / "raw" / "nflverse_draft_picks_all.csv")
picks = picks[picks.season.between(2016, 2024)]
Q = ROOT / "data" / "quality"
Q.mkdir(exist_ok=True)
DRILLS = ["forty", "bench", "vertical", "broad_jump", "cone", "shuttle"]
pct = lambda s: (100 * s.notna().mean()).round(1)


def show(name, t):
    t.to_csv(Q / f"{name}.csv")
    print(f"\n### {name}\n")
    print(t.to_markdown())


# 1. rows by class
by_year = df.groupby("draft_class").agg(
    combine_rows=("player_name", "size"),
    drafted=("drafted", "sum"),
    undrafted=("drafted", lambda s: (~s).sum()),
    reached_nfl=("made_nfl", "sum"),
    undrafted_reached_nfl=("made_nfl", lambda s: (s & ~df.loc[s.index, "drafted"]).sum()),
    no_pfr_id=("pfr_id", lambda s: s.isna().sum()),
)
by_year["total_picks"] = picks.groupby("season").size()
by_year["picks_without_combine"] = by_year.total_picks - by_year.drafted
by_year["pct_picks_with_combine"] = (100 * by_year.drafted / by_year.total_picks).round(1)
by_year.loc["Total"] = by_year.sum(numeric_only=True)
by_year.loc["Total", "pct_picks_with_combine"] = round(
    100 * by_year.loc["Total", "drafted"] / by_year.loc["Total", "total_picks"], 1)
show("rows_by_class", by_year)

# 2. drill fill rates by class
show("drill_fill_pct_by_class",
     df.groupby("draft_class")[DRILLS].agg(pct).assign(n=df.groupby("draft_class").size()))

# 3. drill fill rates by position group
show("drill_fill_pct_by_pos_group",
     df.groupby("pos_group")[DRILLS].agg(pct).assign(n=df.groupby("pos_group").size())
       .sort_values("n", ascending=False))

# 4. forty and shuttle fill, class x pos group
for d in ["forty", "shuttle"]:
    show(f"{d}_fill_pct_class_x_pos", df.pivot_table(index="pos_group", columns="draft_class",
                                                     values=d, aggfunc=pct))

# 5. drill fill, drafted vs undrafted, and by round
show("drill_fill_pct_by_round",
     df.assign(rnd=df.draft_round.fillna(0).astype(int).astype(str).replace("0", "UDFA"))
       .groupby("rnd")[DRILLS].agg(pct).assign(n=df.assign(
           rnd=df.draft_round.fillna(0).astype(int).astype(str).replace("0", "UDFA")
       ).groupby("rnd").size()))

# 6. missingness of all columns
miss = pd.DataFrame({"n_missing": df.isna().sum(), "pct_missing": (100 * df.isna().mean()).round(1)})
show("missing_by_column", miss[miss.n_missing > 0])

# 7. pfr id source
show("pfr_id_source", pd.crosstab(df.pfr_id_source, df.drafted, margins=True))

# 8. outcome summaries by class (drafted only, skill/non-specialist)
d = df[df.drafted & (df.pos_group != "ST")]
show("outcomes_by_class_drafted_nonST", d.groupby("draft_class").agg(
    n=("player_name", "size"),
    seasons_eligible=("seasons_eligible", "first"),
    median_w_av=("w_av", "median"),
    mean_w_av=("w_av", "mean"),
    mean_w_av_per_elig_season=("w_av_per_eligible_season", "mean"),
    mean_w_av_per_season_played=("w_av_per_season_played", "mean"),
    mean_y2_snap_share=("y2_snap_share", "mean"),
    mean_y3_snap_share=("y3_snap_share", "mean"),
    pct_never_played=("made_nfl", lambda s: round(100 * (~s).mean(), 1)),
).round(2))

# 9. forty by position group
show("forty_by_pos_group", df.groupby("pos_group").forty.describe().round(2))

# 10. simple correlations (descriptive only) within position group: forty vs outcomes
rows = []
for g, x in df[df.pos_group != "ST"].groupby("pos_group"):
    for y in ["y2_snap_share", "w_av_per_eligible_season"]:
        sub = x[["forty", y]].dropna()
        rows.append({"pos_group": g, "outcome": y, "n": len(sub),
                     "spearman_rho": round(sub.forty.rank().corr(sub[y].rank()), 3)})
show("forty_outcome_spearman_by_pos", pd.DataFrame(rows).pivot(
    index="pos_group", columns="outcome", values=["n", "spearman_rho"]))
