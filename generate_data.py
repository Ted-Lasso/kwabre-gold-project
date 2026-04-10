"""
RC Drill Hole Data Generator & Analyser
Birimian Greenstone Belt Gold Project (Synthetic Dataset)
Author: Emmanuel Ako-Addo
Note: This is a synthetic dataset modelled on Birimian greenstone belt geology
(SW Ghana), consistent with geological settings at Tarkwa, Asanko, and Bibiani.
"""

import numpy as np
import pandas as pd
import json
import random
 
np.random.seed(42)
random.seed(42)

# ── Project parameters ──────────────────────────────────────────────────────
PROJECT_NAME = "Kwabre Gold Project"
REGION = "Ashanti Region, Ghana"
BELT = "Birimian Greenstone Belt"
N_HOLES = 45
GRID_SPACING = 50   # metres
MAX_DEPTH = 200     # metres
SAMPLE_INTERVAL = 1 # metre
 
# ── Geology definitions ─────────────────────────────────────────────────────
LITHOLOGIES = [
    "Phyllite",
    "Graphitic Phyllite",
    "Greywacke",
    "Carbonaceous Shale",
    "Quartz-Carbonate Vein",
    "Felsic Volcanic",
    "Mafic Volcanic",
    "Saprolite",
]
 
ALTERATION_TYPES = {
    "Phyllite":             ["Weak Sericite", "Moderate Sericite", "Strong Sericite"],
    "Graphitic Phyllite":   ["Carbon Alteration", "Strong Carbon", "Silicification"],
    "Greywacke":            ["Weak Chlorite", "Moderate Chlorite", "Silicification"],
    "Carbonaceous Shale":   ["Carbon Alteration", "Moderate Silicification"],
    "Quartz-Carbonate Vein":["Silicification", "Carbonate Alteration", "Strong Silicification"],
    "Felsic Volcanic":      ["Moderate Sericite", "Silicification"],
    "Mafic Volcanic":       ["Chlorite", "Epidote", "Weak Chlorite"],
    "Saprolite":            ["Oxidised", "Partial Oxidation"],
}
 
OXIDATION = ["Fresh", "Fresh", "Fresh", "Transitional", "Oxidised"]

# Gold grade profiles: background vs vein-hosted
# Birimian gold: background ~0.05–0.15 g/t; mineralised zones 1–15+ g/t
BACKGROUND_MEAN = 0.08
BACKGROUND_STD  = 0.05
VEIN_MEAN       = 2.5
VEIN_STD        = 2.0


# ── Helper functions ─────────────────────────────────────────────────────────
 
def assign_lithology_column(total_depth):
    """
    Build a realistic stratigraphic column for one hole.
    Top 10-25m: saprolite / oxide
    Then alternating phyllite / greywacke packages
    Occasional vein intervals (mineralised zones)
    """
    column = []
    depth = 0
    sap_depth = random.randint(10, 25)
 
    # Saprolite cap
    while depth < sap_depth and depth < total_depth:
        column.append(("Saprolite", depth))
        depth += 1
 
    # Bedrock sequence
    packages = []
    while depth < total_depth:
        lith = random.choices(
            ["Phyllite", "Graphitic Phyllite", "Greywacke",
             "Carbonaceous Shale", "Felsic Volcanic", "Mafic Volcanic"],
            weights=[30, 20, 20, 10, 10, 10]
        )[0]
        thickness = random.randint(5, 40)
        packages.append((lith, thickness))
        depth += thickness
 
    depth = sap_depth
    for lith, thickness in packages:
        for _ in range(thickness):
            if depth >= total_depth:
                break
            # Randomly inject vein intervals
            if random.random() < 0.04:
                column.append(("Quartz-Carbonate Vein", depth))
            else:
                column.append((lith, depth))
            depth += 1
 
    return column[:total_depth]
 
 
def assign_gold_grade(lith, depth, vein_zone_depths):
    """Assign Au grade based on lithology and proximity to vein zones."""
    if lith == "Quartz-Carbonate Vein":
        grade = max(0, np.random.lognormal(mean=np.log(VEIN_MEAN), sigma=0.8))
    elif any(abs(depth - vz) <= 2 for vz in vein_zone_depths):
        # Halo enrichment around veins
        grade = max(0, np.random.lognormal(mean=np.log(0.8), sigma=0.7))
    elif lith in ("Graphitic Phyllite", "Carbonaceous Shale"):
        grade = max(0, np.random.lognormal(mean=np.log(0.15), sigma=0.6))
    else:
        grade = max(0, np.random.exponential(BACKGROUND_MEAN))
    return round(grade, 3)
 
 
def oxidation_state(depth, sap_base):
    if depth < sap_base:
        return "Oxidised"
    elif depth < sap_base + 10:
        return "Transitional"
    return "Fresh"
 
 
 # ── Generate collar table ────────────────────────────────────────────────────
 
def generate_collars(n_holes):
    collars = []
    hole_id = 1
    for row in range(5):
        for col in range(9):
            if hole_id > n_holes:
                break
            easting  = 650000 + col * GRID_SPACING + random.uniform(-5, 5)
            northing = 750000 + row * GRID_SPACING + random.uniform(-5, 5)
            elevation = 280 + random.uniform(-8, 8)
            depth = random.randint(100, MAX_DEPTH)
            dip    = random.choice([-60, -55, -50, -45])
            azimuth = random.choice([90, 270])  # E–W fences typical in Ghana
 
            collars.append({
                "HoleID":    f"KW{hole_id:03d}",
                "Easting":   round(easting, 1),
                "Northing":  round(northing, 1),
                "Elevation": round(elevation, 1),
                "TotalDepth_m": depth,
                "Dip":       dip,
                "Azimuth":   azimuth,
                "DrillType": "RC",
                "Company":   "Kwabre Exploration Ltd",
                "Year":      random.choice([2021, 2022, 2023]),
            })
            hole_id += 1
    return pd.DataFrame(collars)
 
 
 # ── Generate lithology / assay tables ───────────────────────────────────────
 
def generate_lithology_and_assay(collars_df):
    lith_rows  = []
    assay_rows = []
 
    for _, collar in collars_df.iterrows():
        hole_id = collar["HoleID"]
        total_depth = int(collar["TotalDepth_m"])
        sap_base = random.randint(10, 25)
 
        column = assign_lithology_column(total_depth)
        vein_depths = [d for lith, d in column if lith == "Quartz-Carbonate Vein"]
 
        prev_lith = None
        interval_from = 0
 
        for i, (lith, depth) in enumerate(column):
            # Close lithology interval when lith changes
            next_lith = column[i+1][0] if i+1 < len(column) else None
            if next_lith != lith or i == len(column) - 1:
                alteration = random.choice(ALTERATION_TYPES.get(lith, ["None"]))
                ox_state   = oxidation_state(depth, sap_base)
                lith_rows.append({
                    "HoleID":     hole_id,
                    "From_m":     interval_from,
                    "To_m":       depth + 1,
                    "Lithology":  lith,
                    "Alteration": alteration,
                    "Oxidation":  ox_state,
                })
                interval_from = depth + 1
 
            # Assay every 1m
            au_grade = assign_gold_grade(lith, depth, vein_depths)
            assay_rows.append({
                "HoleID":   hole_id,
                "From_m":   depth,
                "To_m":     depth + 1,
                "Au_ppm":   au_grade,
                "Lithology": lith,
            })
 
    lith_df  = pd.DataFrame(lith_rows)
    assay_df = pd.DataFrame(assay_rows)
    return lith_df, assay_df
 
 # ── Composite analysis ───────────────────────────────────────────────────────
 
def compute_composites(assay_df, cutoff=0.5, max_internal_waste=3):
    """
    Identify mineralised composites using a running window.
    Standard industry approach: include up to max_internal_waste metres
    of sub-cutoff material within a composite.
    """
    composites = []
    for hole_id, group in assay_df.groupby("HoleID"):
        group = group.sort_values("From_m").reset_index(drop=True)
        in_zone = False
        zone_from = None
        waste_count = 0
        zone_samples = []
 
        for _, row in group.iterrows():
            if row["Au_ppm"] >= cutoff:
                if not in_zone:
                    in_zone = True
                    zone_from = row["From_m"]
                    zone_samples = []
                    waste_count = 0
                waste_count = 0
                zone_samples.append(row["Au_ppm"])
            else:
                if in_zone:
                    waste_count += 1
                    zone_samples.append(row["Au_ppm"])
                    if waste_count > max_internal_waste:
                        # Close composite
                        length = row["From_m"] - zone_from - waste_count
                        if length > 0:
                            composites.append({
                                "HoleID":       hole_id,
                                "From_m":       zone_from,
                                "To_m":         row["From_m"] - waste_count,
                                "Width_m":      length,
                                "Au_g/t":       round(np.mean(zone_samples[:-waste_count]), 3),
                                "Au_g_m":       round(np.mean(zone_samples[:-waste_count]) * length, 2),
                            })
                        in_zone = False
                        waste_count = 0
                        zone_samples = []
 
        if in_zone and zone_samples:
            length = group.iloc[-1]["To_m"] - zone_from
            composites.append({
                "HoleID":   hole_id,
                "From_m":   zone_from,
                "To_m":     group.iloc[-1]["To_m"],
                "Width_m":  length,
                "Au_g/t":   round(np.mean(zone_samples), 3),
                "Au_g_m":   round(np.mean(zone_samples) * length, 2),
            })
 
    return pd.DataFrame(composites)
 
 
# ── QA/QC summary ───────────────────────────────────────────────────────────
 
def qaqc_summary(assay_df):
    """Flag anomalies: grades > 3 SD from mean (log-transformed)."""
    log_grades = np.log1p(assay_df["Au_ppm"])
    mu, sigma = log_grades.mean(), log_grades.std()
    assay_df["QAQC_Flag"] = np.where(
        np.abs(log_grades - mu) > 3 * sigma,
        "HIGH_OUTLIER", "OK"
    )
    return assay_df
 
 
# ── Main ─────────────────────────────────────────────────────────────────────
 
if __name__ == "__main__":
    print("Generating collar data...")
    collars = generate_collars(N_HOLES)
 
    print("Generating lithology and assay data...")
    lith_df, assay_df = generate_lithology_and_assay(collars)
 
    print("Computing composites...")
    composites = compute_composites(assay_df, cutoff=0.5)
 
    print("Running QA/QC flagging...")
    assay_df = qaqc_summary(assay_df)
 
    # Save CSVs
    collars.to_csv("./collar.csv", index=False)
    lith_df.to_csv("./lithology.csv", index=False)
    assay_df.to_csv("./assay.csv", index=False)
    composites.to_csv("./composites.csv", index=False)
 
    # Summary stats
    print("\n── Dataset Summary ───────────────────────────────────")
    print(f"Holes drilled:        {len(collars)}")
    print(f"Total assay samples:  {len(assay_df)}")
    print(f"Mineralised composites (>0.5 g/t Au): {len(composites)}")
    print(f"\nGrade statistics (Au g/t):")
    print(assay_df["Au_ppm"].describe().round(3))
    print(f"\nTop 5 composite intercepts:")
    print(composites.nlargest(5, "Au_g/t")[["HoleID","From_m","To_m","Width_m","Au_g/t"]].to_string(index=False))
    print(f"\nLithology distribution:")
    print(lith_df["Lithology"].value_counts().to_string())
    print(f"\nQA/QC: {(assay_df['QAQC_Flag']=='HIGH_OUTLIER').sum()} high outlier samples flagged")
    print("\nFiles saved: collar.csv, lithology.csv, assay.csv, composites.csv")