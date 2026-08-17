#fetch hipparcos dataset
from pathlib import Path
import pandas as pd
import requests

# ----------------------------
# SETTINGS
# ----------------------------
R_LY = 500.0
R_PC = R_LY / 3.26156

# HYG "CURRENT" CSV (v4.1 file in archived GitHub mirror)
# If this ever moves, search "hygdata_v41.csv raw" and update the URL.
HYG_URL = "https://raw.githubusercontent.com/astronexus/HYG-Database/main/hyg/CURRENT/hygdata_v41.csv"

CACHE_CSV = Path("hygdata_v41.csv")
OUT_CSV = Path(__file__).parent / "hyg_within_500ly_named.csv"

# ----------------------------
# DOWNLOAD (cached)
# ----------------------------
def download_if_needed(url: str, path: Path) -> None:
    if path.exists() and path.stat().st_size > 10_000_000:
        print("Using cached:", path)
        return

    print("Downloading HYG CSV...")
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
    print("Saved:", path, "bytes:", path.stat().st_size)

# ----------------------------
# MAIN
# ----------------------------
def main():
    download_if_needed(HYG_URL, CACHE_CSV)

    print("Reading HYG...")
    df = pd.read_csv(CACHE_CSV)

    # Expected HYG columns include:
    # id, hip, hd, hr, gl, bf, proper, ra, dec, dist, mag, spect, ...
    # (HYG docs list proper/ra/dec/dist and other identifiers) 
    # https://astronexus.com/projects/at-hyg-details :contentReference[oaicite:1]{index=1}

    # Force numeric dist
    df["dist_pc"] = pd.to_numeric(df.get("dist"), errors="coerce")

    # Filter within 500 ly
    df = df[df["dist_pc"].notna() & (df["dist_pc"] <= R_PC)].copy()

    # RA in HYG is hours; convert to degrees
    df["RA_deg"] = pd.to_numeric(df.get("ra"), errors="coerce") * 15.0
    df["DEC_deg"] = pd.to_numeric(df.get("dec"), errors="coerce")

    # Distances
    df["distance_pc"] = df["dist_pc"]
    df["distance_ly"] = df["distance_pc"] * 3.26156

    # Build aliases string (HIP/HD/HR/Gliese/BayerFlamsteed)
    def mk_alias(row) -> str:
        parts = []
        if pd.notna(row.get("hip")): parts.append(f"HIP {int(row['hip'])}")
        if pd.notna(row.get("hd")):  parts.append(f"HD {int(row['hd'])}")
        if pd.notna(row.get("hr")):  parts.append(f"HR {int(row['hr'])}")
        if isinstance(row.get("gl"), str) and row["gl"].strip(): parts.append(row["gl"].strip())
        if isinstance(row.get("bf"), str) and row["bf"].strip(): parts.append(row["bf"].strip())
        return " | ".join(parts)

    df["aliases"] = df.apply(mk_alias, axis=1)

    # Proper name (can be blank); make a final label:
    df["proper"] = df.get("proper", "").fillna("").astype(str)
    df["label"] = df["proper"]
    missing = df["label"].str.strip() == ""
    # fallback: Bayer/Flamsteed (bf) if present, else HIP, else id
    df.loc[missing & df["bf"].notna(), "label"] = df.loc[missing & df["bf"].notna(), "bf"].astype(str)
    missing = df["label"].str.strip() == ""
    df.loc[missing & df["hip"].notna(), "label"] = "HIP " + df.loc[missing & df["hip"].notna(), "hip"].astype(int).astype(str)
    missing = df["label"].str.strip() == ""
    df.loc[missing, "label"] = "HYG " + df.loc[missing, "id"].astype(int).astype(str)

    # Star "type": use HYG spectral type string (e.g., A0V, B2III)
    df["spect"] = df.get("spect", "").fillna("").astype(str)

    # Output columns
    out = df[[
        "id", "hip", "label", "proper", "aliases",
        "RA_deg", "DEC_deg",
        "distance_pc", "distance_ly",
        "spect",
        "mag"
    ]].copy()

    out.to_csv(OUT_CSV, index=False)

print("\n==============================")
print("FILE WRITTEN TO:")
print(OUT_CSV.resolve())
print("Exists?:", OUT_CSV.exists())
print("==============================\n")


if __name__ == "__main__":
    main()

