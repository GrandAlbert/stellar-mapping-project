from pathlib import Path
import numpy as np
import math
import pandas as pd
import re

BASE = Path(__file__).parent
IN_CSV  = BASE / "hyg_within_500ly_named.csv"
OUT_CSV = BASE / "minecraft_star_coords.csv"

# IMPORTANT:
# If you want Alpha Cen ~ <3,-3,0>, DO NOT scale down.
# Keep SCALE = 1.0 for now.
SCALE = 1.0

R_matrix = np.array([
    [-0.05487556, -0.87343709, -0.48383502],
    [ 0.49410943, -0.44482963,  0.74698224],
    [-0.86766615, -0.19807637,  0.45598378]
], dtype=float)

BLOCK_MAP = {
    "M": "minecraft:redstone_block",
    "K": "minecraft:shroomlight",
    "G": "minecraft:glowstone",
    "F": "minecraft:ochre_froglight",
    "A": "minecraft:pearlescent_froglight",
    "B": "minecraft:sea_lantern",
}
WHITE_DWARF_BLOCK = "minecraft:blue_ice"
DEFAULT_BLOCK = "minecraft:amethyst_block"

def normalize_spec(s) -> str:
    return (s if isinstance(s, str) else "").strip()

def is_white_dwarf(spec: str) -> bool:
    return normalize_spec(spec).upper().startswith("D")

def spectral_letter(spec: str) -> str:
    s = normalize_spec(spec).upper()
    # dM / sdM / esdM etc -> M
    m = re.match(r"^(?:E?SD)?D?([OBAFGKM])", s)
    if m:
        return m.group(1)
    m2 = re.match(r"^([OBAFGKM])", s)
    return m2.group(1) if m2 else ""

def choose_block(spec: str) -> str:
    if is_white_dwarf(spec):
        return WHITE_DWARF_BLOCK
    return BLOCK_MAP.get(spectral_letter(spec), DEFAULT_BLOCK)

def luminosity_class(spec: str) -> str:
    s = normalize_spec(spec).upper()
    if "IA" in s: return "IA"
    if "IB" in s: return "IB"
    for cls in ["II", "III", "IV", "V"]:
        if cls in s: return cls
    return ""

def size_category(spec: str) -> str:
    # V -> single
    # IV-III-II -> star_cross (center + 6 directions)
    # Ib-Ia -> cube_3 (3x3x3)
    lc = luminosity_class(spec)
    if lc in ("IA", "IB"): return "cube_3"
    if lc in ("II", "III", "IV"): return "star_cross"
    return "single"

def get_distance_ly(df: pd.DataFrame) -> pd.Series:
    if "distance_ly" in df.columns:
        return pd.to_numeric(df["distance_ly"], errors="coerce")
    if "distance_pc" in df.columns:
        pc = pd.to_numeric(df["distance_pc"], errors="coerce")
        return pc * 3.26156
    raise ValueError("No distance_ly or distance_pc column found.")

def radec_to_vraw(ra_deg: float, dec_deg: float, dist_ly: float) -> np.ndarray:
    # EXACTLY your formula
    x = dist_ly * math.cos(math.radians(dec_deg)) * math.cos(math.radians(ra_deg))
    y = dist_ly * math.cos(math.radians(dec_deg)) * math.sin(math.radians(ra_deg))
    z = dist_ly * math.sin(math.radians(dec_deg))
    return np.array([x, y, z], dtype=float)

df = pd.read_csv(IN_CSV)

RA_COL = "RA_deg"
DEC_COL = "DEC_deg"
SPEC_COL = "spect"
MAG_COL = "mag"

dist_ly = get_distance_ly(df)

# keep only valid rows
mask = (
    pd.to_numeric(df[RA_COL], errors="coerce").notna()
    & pd.to_numeric(df[DEC_COL], errors="coerce").notna()
    & dist_ly.notna()
)
df = df[mask].copy()
dist_ly = dist_ly[mask].copy()

xs, ys, zs, blocks, sizes = [], [], [], [], []

for idx, row in df.iterrows():
    ra = float(row[RA_COL])
    dec = float(row[DEC_COL])
    d = float(dist_ly.loc[idx])
    spec = row.get(SPEC_COL, "")

    v_raw = radec_to_vraw(ra, dec, d)
    v_finish = R_matrix @ v_raw

    # EXACTLY your rounding stage (after rotation)
    v_block = np.round(v_finish * SCALE).astype(int)

    Xin, Ypro, Zup = v_block
    mc_x = int(Xin)
    mc_y = int(Zup)
    mc_z = int(Ypro)

    xs.append(mc_x); ys.append(mc_y); zs.append(mc_z)
    blocks.append(choose_block(spec))
    sizes.append(size_category(spec))

out = pd.DataFrame({
    "x": xs, "y": ys, "z": zs,
    "block": blocks,
    # single = 1 block
    # star_cross = center + 6 directions (IV-III-II)
    # cube_3 = 3x3x3 cube (Ib-Ia)
    "size_category": sizes,

    # keep metadata
    "label": df.get("label", ""),
    "proper": df.get("proper", ""),
    "aliases": df.get("aliases", ""),
    "hip": df.get("hip", ""),
    "spect": df.get("spect", ""),
    "magnitude": df.get("mag", ""),
})

out.to_csv(OUT_CSV, index=False)
print("Saved:", OUT_CSV.resolve())
print("Rows:", len(out))
