from astroquery.gaia import Gaia
from astroquery.xmatch import XMatch
from astropy import units as u
import pandas as pd

# ----------------------------
# SETTINGS
# ----------------------------
R_LY = 500
PARALLAX_SNR_MIN = 10

G_MAX_BIG = 10
MAX_ROWS_BIG = 200000
OUT_BIG = "gaia_within_500ly.csv"

G_MAX_NAMED = 8
MAX_NAME_TRIES = 20000
CHUNK = 2000
XMATCH_ARCSEC = 1.0
OUT_NAMED = "gaia_within_500ly_named.csv"

# ----------------------------
# GAIA QUERY
# ----------------------------
R_PC = R_LY / 3.26156
PLX_MIN = 1000 / R_PC

query = f"""
SELECT TOP {MAX_ROWS_BIG}
  source_id, ra, dec,
  parallax, parallax_error,
  phot_g_mean_mag, bp_rp, teff_gspphot
FROM gaiadr3.gaia_source
WHERE parallax >= {PLX_MIN}
  AND phot_g_mean_mag <= {G_MAX_BIG}
  AND parallax_over_error >= {PARALLAX_SNR_MIN}
"""

print("Querying Gaia...")
job = Gaia.launch_job_async(query)
df = job.get_results().to_pandas()
print("Gaia rows:", len(df))

# IMPORTANT: keep source_id as string (prevents merge/excel issues)
df["source_id"] = df["source_id"].astype("string")

# distance
df["dist_pc"] = 1000.0 / df["parallax"]
df["dist_ly"] = df["dist_pc"] * 3.26156

df.to_csv(OUT_BIG, index=False)
print("Saved big dataset:", OUT_BIG)

# ----------------------------
# BRIGHT SUBSET FOR NAMING
# ----------------------------
df_named = df[df["phot_g_mean_mag"] <= G_MAX_NAMED].copy()
df_named = df_named.sort_values("phot_g_mean_mag").reset_index(drop=True)

print("Rows to attempt naming:", len(df_named))
if len(df_named) > MAX_NAME_TRIES:
    df_named = df_named.head(MAX_NAME_TRIES).copy()
    print("Capped naming rows to:", len(df_named))

# ----------------------------
# XMATCH TO SIMBAD (MAIN_ID)
# ----------------------------
all_matches = []

for start in range(0, len(df_named), CHUNK):
    end = min(start + CHUNK, len(df_named))
    chunk = df_named.iloc[start:end][["source_id", "ra", "dec"]].copy()
    chunk = chunk.rename(columns={"ra": "RA", "dec": "DEC"})

    print(f"XMatch chunk {start}:{end} ...")

    try:
        xm = XMatch.query(
            cat1=chunk,
            cat2="simbad",
            max_distance=XMATCH_ARCSEC * u.arcsec,
            colRA1="RA",
            colDec1="DEC",
        )
        xm_df = xm.to_pandas()
    except Exception as e:
        print("Chunk failed:", e)
        xm_df = pd.DataFrame({"source_id": chunk["source_id"], "main_id": ""})

    # Normalize types
    if "source_id" in xm_df.columns:
        xm_df["source_id"] = xm_df["source_id"].astype("string")

    if xm_df.empty:
        xm_df = pd.DataFrame({"source_id": chunk["source_id"], "main_id": ""})
    else:
        # find the SIMBAD main id column
        main_col = None
        for c in xm_df.columns:
            if "main" in c.lower() and "id" in c.lower():
                main_col = c
                break

        if main_col is None:
            print("XMatch returned columns:", list(xm_df.columns))
            xm_df = pd.DataFrame({"source_id": chunk["source_id"], "main_id": ""})
        else:
            xm_df = xm_df.rename(columns={main_col: "main_id"})
            xm_df = xm_df[["source_id", "main_id"]].drop_duplicates("source_id")

    all_matches.append(xm_df)

names_df = pd.concat(all_matches, ignore_index=True)
names_df["source_id"] = names_df["source_id"].astype("string")
names_df["main_id"] = names_df["main_id"].fillna("").astype(str)

out = df_named.merge(names_df, on="source_id", how="left")
out["main_id"] = out["main_id"].fillna("").astype(str)

# Debug: match rate
match_rate = (out["main_id"].str.strip() != "").mean()
print(f"SIMBAD match rate: {match_rate*100:.2f}%")

# Label fallback
out["label"] = out["main_id"]
mask = out["label"].str.strip() == ""
out.loc[mask, "label"] = "Gaia DR3 " + out.loc[mask, "source_id"].astype(str)

out.to_csv(OUT_NAMED, index=False)
print("Saved named subset:", OUT_NAMED)
print(out[["source_id", "phot_g_mean_mag", "main_id", "label"]].head(30))
