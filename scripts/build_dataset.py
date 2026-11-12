"""
Build the analysis-ready combine + draft + early-career table (2016 to 2024 classes).

Sources (nflverse, via nflreadpy; raw copies saved in ../raw/):
  - combine      : load_combine()
  - draft picks  : load_draft_picks()
  - snap counts  : load_snap_counts()   (per game, keyed by PFR player id)

Run:  python scripts/build_dataset.py   (from /home/user)
"""
import re
from difflib import SequenceMatcher
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, OUT = ROOT / "raw", ROOT / "data"
OUT.mkdir(exist_ok=True)

FIRST_CLASS, LAST_CLASS = 2016, 2024
LAST_COMPLETE_SEASON = 2025          # 2026 season is in progress as of Nov 2026


def load_raw():
    """Use saved raw files if present, otherwise download from nflverse."""
    files = {
        "combine": RAW / "nflverse_combine_all.csv",
        "picks": RAW / "nflverse_draft_picks_all.csv",
        "snaps": RAW / "nflverse_snap_counts_2016_2026.csv",
    }
    if not all(f.exists() for f in files.values()):
        import nflreadpy as nfl
        RAW.mkdir(exist_ok=True)
        nfl.load_combine().to_pandas().to_csv(files["combine"], index=False)
        nfl.load_draft_picks().to_pandas().to_csv(files["picks"], index=False)
        nfl.load_snap_counts(seasons=list(range(FIRST_CLASS, 2027))).to_pandas().to_csv(
            files["snaps"], index=False)
    return {k: pd.read_csv(v) for k, v in files.items()}


POS_GROUP = {
    "QB": "QB", "RB": "RB", "FB": "RB", "WR": "WR", "TE": "TE",
    "OT": "OL", "OG": "OL", "G": "OL", "C": "OL", "OL": "OL",
    "DT": "DL", "DE": "DL", "DL": "DL", "EDGE": "DL",
    "LB": "LB", "ILB": "LB", "OLB": "LB",
    "CB": "DB", "S": "DB", "SAF": "DB", "DB": "DB",
    "K": "ST", "P": "ST", "LS": "ST",
}


def ht_to_inches(h):
    if pd.isna(h) or "-" not in str(h):
        return np.nan
    ft, inch = str(h).split("-")
    return int(ft) * 12 + int(inch)


def norm_name(x):
    x = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b\.?", "", str(x).lower())
    return re.sub(r"[^a-z]", "", x)


def college_sim(a, b):
    return SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio()


# Hand-verified links where the combine name is a nickname of the PFR name (same class/school/pos)
MANUAL_IDS = {
    (2018, "Chris Campbell"): "CampCh01",   # Christian Campbell, CB, Penn St.
    (2018, "Trey Walker"): "WalkTr01",      # Tracy Walker, S, Louisiana
}


def recover_ids(c, p, snaps, all_pick_ids):
    """Fill missing pfr_id in the combine table.

    Step 1: match to draft picks not already matched, on class year + normalized name.
            Ties are broken by college string similarity. This also restores missing
            draft fields (the combine table leaves them blank for these players).
            A second pass matches on last name with college similarity >= 0.8.
    Step 2: remaining rows: match to players in snap counts on normalized name, requiring
            exactly one candidate whose first REG-season snap is within 2 years of the class.
    """
    c = c.copy()
    c["pfr_id_source"] = np.where(c.pfr_id.notna(), "combine", None)
    c["key"] = c.player_name.map(norm_name)

    abbr_to_full = (c.dropna(subset=["pfr_id", "draft_team"])
                    .merge(p, left_on="pfr_id", right_on="pfr_player_id")
                    .groupby("team").draft_team.agg(lambda s: s.mode()[0]))
    for (yr, name), pid in MANUAL_IDS.items():
        idx = c.index[(c.draft_class == yr) & (c.player_name == name) & c.pfr_id.isna()]
        pk = p[p.pfr_player_id == pid].iloc[0]
        c.loc[idx, ["pfr_id", "pfr_id_source", "draft_year", "draft_round", "draft_ovr", "draft_team"]] = [
            pid, "manual", pk.season, pk["round"], pk.pick, abbr_to_full.get(pk.team, pk.team)]

    # step 1: draft picks (1a exact normalized name; 1b last name + strong college match)
    c["last"] = c.player_name.map(lambda x: norm_name(str(x).split(" ", 1)[-1]))
    for label, keys, min_sim in [("name_match_draft_picks", ["draft_class", "key"], 0.5),
                                 ("lastname_college_match_draft_picks", ["draft_class", "last"], 0.8)]:
        up = p[~p.pfr_player_id.isin(c.pfr_id)].copy()
        up["key"] = up.pfr_player_name.map(norm_name)
        up["last"] = up.pfr_player_name.map(lambda x: norm_name(str(x).split(" ", 1)[-1]))
        up = up.rename(columns={"season": "draft_class"})
        cand = c[c.pfr_id.isna()].reset_index().merge(up, on=keys, suffixes=("", "_p"))
        cand["csim"] = [college_sim(a, b) for a, b in zip(cand.school, cand.college)]
        cand = cand[cand.csim >= min_sim].sort_values("csim", ascending=False)
        cand = cand.drop_duplicates("pfr_player_id").drop_duplicates("index").set_index("index")
        c.loc[cand.index, "pfr_id"] = cand.pfr_player_id
        c.loc[cand.index, "draft_year"] = c.loc[cand.index, "draft_class"]
        c.loc[cand.index, "draft_round"] = cand["round"]
        c.loc[cand.index, "draft_ovr"] = cand.pick
        c.loc[cand.index, "draft_team"] = cand.team.map(abbr_to_full).fillna(cand.team)
        c.loc[cand.index, "pfr_id_source"] = label

    # step 2: snap counts (undrafted players who reached the NFL)
    s = snaps[snaps.game_type == "REG"]
    first = s.groupby("pfr_player_id").agg(first_season=("season", "min"), name=("player", "first"))
    # never assign an id that belongs to any drafted player (any year)
    first = first[~first.index.isin(c.pfr_id) & ~first.index.isin(all_pick_ids)].reset_index()
    first["key"] = first.name.map(norm_name)
    rows = c[c.pfr_id.isna()].reset_index()
    m = rows.merge(first, on="key")
    m = m[(m.first_season >= m.draft_class) & (m.first_season <= m.draft_class + 2)]
    m = m[~m.duplicated("index", keep=False) & ~m.duplicated("pfr_player_id", keep=False)]
    m = m.set_index("index")
    c.loc[m.index, "pfr_id"] = m.pfr_player_id
    c.loc[m.index, "pfr_id_source"] = "name_match_snap_counts"
    c["pfr_id_source"] = c.pfr_id_source.fillna("none")
    return c.drop(columns=["key", "last"])


def team_games(season):
    return 16 if season <= 2020 else 17


def snap_windows(snaps, players):
    """Per-player usage over first-k seasons and over the career through LAST_COMPLETE_SEASON.

    players: DataFrame with pfr_id and draft_class.
    Snap share per game = max(offense_pct, defense_pct). Window snap share is the sum of
    per-game shares divided by all team games in the window, so missed games count as 0.
    """
    s = snaps[(snaps.game_type == "REG") & (snaps.season <= LAST_COMPLETE_SEASON)].copy()
    s["share"] = s[["offense_pct", "defense_pct"]].max(axis=1)
    s["scrim"] = s.offense_snaps.fillna(0) + s.defense_snaps.fillna(0)
    s["any_snap"] = (s.scrim + s.st_snaps.fillna(0)) > 0
    s = s[s.any_snap]
    s = s.merge(players[["pfr_id", "draft_class"]], left_on="pfr_player_id",
                right_on="pfr_id", how="inner")
    s = s[s.season >= s.draft_class]
    s["yr"] = s.season - s.draft_class + 1          # 1 = rookie season

    out = players[["pfr_id", "draft_class"]].copy().set_index("pfr_id")

    # career through last complete season
    g = s.groupby("pfr_id")
    out["seasons_played"] = g.season.nunique()
    out["games_played"] = g.size()
    out["scrimmage_snaps"] = g.scrim.sum()
    out["games_50pct_snaps"] = g.share.apply(lambda x: (x >= 0.5).sum())

    for k in (2, 3):
        w = s[s.yr <= k].groupby("pfr_id")
        avail = out.draft_class.apply(
            lambda c: sum(team_games(c + i) for i in range(k)))
        complete = (out.draft_class + k - 1) <= LAST_COMPLETE_SEASON
        out[f"y{k}_games"] = w.size()
        out[f"y{k}_games_50pct"] = w.share.apply(lambda x: (x >= 0.5).sum())
        out[f"y{k}_scrimmage_snaps"] = w.scrim.sum()
        out[f"y{k}_snap_share"] = w.share.sum() / avail
        cols = [f"y{k}_games", f"y{k}_games_50pct", f"y{k}_scrimmage_snaps", f"y{k}_snap_share"]
        # players with a pfr_id and no snaps in a complete window get 0; incomplete window -> NaN
        out.loc[complete, cols] = out.loc[complete, cols].fillna(0)
        out.loc[~complete, cols] = np.nan

    career_cols = ["seasons_played", "games_played", "scrimmage_snaps", "games_50pct_snaps"]
    out[career_cols] = out[career_cols].fillna(0)
    return out.drop(columns="draft_class").reset_index()


def main():
    raw = load_raw()
    c = raw["combine"][raw["combine"].season.between(FIRST_CLASS, LAST_CLASS)].copy()
    p = raw["picks"][raw["picks"].season.between(FIRST_CLASS, LAST_CLASS)].copy()
    snaps = raw["snaps"]

    c = c.rename(columns={"season": "draft_class"})
    c = recover_ids(c, p, snaps, set(raw["picks"].pfr_player_id.dropna()))
    c["drafted"] = c.draft_round.notna()
    c["pos_group"] = c.pos.map(POS_GROUP)
    c["ht_in"] = c.ht.apply(ht_to_inches)
    c["pro_day_2021"] = c.draft_class == 2021   # 2021 Combine cancelled; PFR lists pro day results
    c["speed_score"] = c.wt * 200 / c.forty ** 4  # Barnwell speed score
    # within position group z-score of forty (lower = faster), pooled over 2016 to 2024
    c["forty_z_pos"] = c.groupby("pos_group").forty.transform(lambda x: (x - x.mean()) / x.std())

    pick_cols = ["pfr_player_id", "gsis_id", "round", "pick", "team", "position", "category",
                 "side", "age", "to", "w_av", "dr_av", "games", "seasons_started",
                 "probowls", "allpro", "hof"]
    df = c.merge(p[pick_cols], left_on="pfr_id", right_on="pfr_player_id", how="left")
    assert df.drafted.sum() == df.pfr_player_id.notna().sum(), "drafted players failed to match"
    assert (df.loc[df.drafted, "draft_ovr"] == df.loc[df.drafted, "pick"]).all()
    df = df.drop(columns=["pfr_player_id", "round", "pick", "team"])  # duplicates of combine cols
    df = df.rename(columns={"position": "draft_position", "to": "last_season",
                            "games": "games_pfr_incl_2026"})

    # early-career usage from snap counts (covers drafted AND undrafted players with a pfr_id)
    sw = snap_windows(snaps, df[df.pfr_id.notna()])
    df = df.merge(sw, on="pfr_id", how="left")

    # normalized AV outcomes (AV exists only for drafted players; it runs through 2025)
    df["seasons_eligible"] = LAST_COMPLETE_SEASON - df.draft_class + 1
    df["w_av_per_eligible_season"] = df.w_av / df.seasons_eligible
    df["dr_av_per_eligible_season"] = df.dr_av / df.seasons_eligible
    df["w_av_per_season_played"] = np.where(df.seasons_played > 0,
                                            df.w_av / df.seasons_played, np.nan)
    df["made_nfl"] = df.seasons_played.fillna(0) > 0

    # Zero-coding (documented in README):
    # (a) drafted players with blank PFR AV never played a REG-season game -> AV = 0.
    #     Blank dr_av with nonzero w_av means no AV for the drafting team -> 0.
    # (b) players with no pfr_id never appear in snap counts by name -> usage = 0.
    df["outcome_zero_imputed"] = (df.drafted & df.w_av.isna()) | df.pfr_id.isna()
    for col in ["w_av", "dr_av"]:
        df.loc[df.drafted, col] = df.loc[df.drafted, col].fillna(0)
    for col in ["seasons_started", "probowls", "allpro"]:
        df.loc[df.drafted, col] = df.loc[df.drafted, col].fillna(0)
    noid = df.pfr_id.isna()
    usage_cols = ["seasons_played", "games_played", "games_50pct_snaps", "scrimmage_snaps",
                  "y2_games", "y2_games_50pct", "y2_scrimmage_snaps", "y2_snap_share"]
    df.loc[noid, usage_cols] = 0
    y3 = [c for c in df.columns if c.startswith("y3_")]
    df.loc[noid & (df.draft_class + 2 <= LAST_COMPLETE_SEASON), y3] = 0
    df["seasons_eligible"] = LAST_COMPLETE_SEASON - df.draft_class + 1
    df["w_av_per_eligible_season"] = df.w_av / df.seasons_eligible
    df["dr_av_per_eligible_season"] = df.dr_av / df.seasons_eligible
    df["w_av_per_season_played"] = np.where(df.seasons_played > 0,
                                            df.w_av / df.seasons_played, np.nan)

    order = ["draft_class", "player_name", "pfr_id", "pfr_id_source", "cfb_id", "gsis_id", "pos", "pos_group",
             "draft_position", "category", "side", "school", "drafted", "draft_round",
             "draft_ovr", "draft_team", "age", "ht", "ht_in", "wt", "forty", "forty_z_pos",
             "speed_score", "bench", "vertical", "broad_jump", "cone", "shuttle", "pro_day_2021",
             "seasons_eligible", "made_nfl", "outcome_zero_imputed", "seasons_played", "games_played", "games_50pct_snaps",
             "scrimmage_snaps",
             "y2_games", "y2_games_50pct", "y2_scrimmage_snaps", "y2_snap_share",
             "y3_games", "y3_games_50pct", "y3_scrimmage_snaps", "y3_snap_share",
             "w_av", "dr_av", "w_av_per_eligible_season", "dr_av_per_eligible_season",
             "w_av_per_season_played", "seasons_started", "probowls", "allpro", "hof",
             "last_season", "games_pfr_incl_2026"]
    df = df[order].sort_values(["draft_class", "draft_ovr", "player_name"])
    df.to_csv(OUT / "combine_draft_outcomes_2016_2024.csv", index=False)

    # drafted players with no combine record (not in analysis table, kept for reference)
    no_combine = p[~p.pfr_player_id.isin(c.pfr_id)]
    no_combine.to_csv(OUT / "draft_picks_without_combine_2016_2024.csv", index=False)
    print(f"analysis table: {df.shape}, picks without combine: {len(no_combine)}")
    return df, p, no_combine


if __name__ == "__main__":
    main()
