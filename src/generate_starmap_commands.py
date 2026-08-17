from pathlib import Path
import pandas as pd

IN_CSV = Path(__file__).parent / "minecraft_star_coords.csv"

OUT_PATH = Path(r"C:\Users\Albert\Desktop\Programs\place.mcfunction")
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

LABEL_MAG_LIMIT = 999  # only label bright stars

STAR_CROSS = [
    (0,0,0),
    (1,0,0),(-1,0,0),
    (0,1,0),(0,-1,0),
    (0,0,1),(0,0,-1)
]

CUBE_3 = [(dx,dy,dz) for dx in (-1,0,1) for dy in (-1,0,1) for dz in (-1,0,1)]

def shape_offsets(cat):
    cat = str(cat).lower()
    if cat == "cube_3": return CUBE_3
    if cat == "star_cross": return STAR_CROSS
    return [(0,0,0)]

df = pd.read_csv(IN_CSV)

commands = []
occupied = {}

for _, row in df.iterrows():

    x = int(row["x"])
    y = int(row["y"]) + 136 # off set by 136
    z = int(row["z"])
    block = row["block"]
    label = str(row["label"])
    size = row["size_category"]
    mag = float(row["magnitude"])

    base = (x,y,z)
    k = occupied.get(base,0)
    occupied[base] = k+1

    x += k  # sideways offset for binaries

    # place star blocks
    for dx,dy,dz in shape_offsets(size):
        commands.append(f"setblock {x+dx} {y+dy} {z+dz} {block} replace")

    # floating label (SAFE)
    if mag <= LABEL_MAG_LIMIT and label:
        commands.append(
            f"summon text_display {x} {y+2} {z} "
            f'{{text:"\\"{label}\\"", billboard:"center", view_range:0.23f, scale:[0.7f,0.7f,0.7f]}}'
        )
        

OUT_PATH.write_text("\n".join(commands) + "\n", encoding="utf-8")
print("Wrote:", OUT_PATH)
