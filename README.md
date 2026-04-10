# Kwabre Gold Project — RC Drill Hole Analysis

A Python-based data pipeline simulating RC drill hole data from a 
Birimian greenstone belt gold project in Ghana, West Africa.

## What this project does

Generates and analyses a synthetic but geologically realistic drill 
hole dataset, including:
- Collar locations across a 5-line, 45-hole drill grid
- Downhole lithological logging (phyllite, graphitic phyllite, 
  quartz-carbonate veins and more)
- 1-metre gold assay intervals (6,388 samples)
- Mineralised composite calculation at 0.5 g/t Au cutoff
- QA/QC outlier flagging using 3-sigma lognormal method

## Geological context

The dataset is modelled on the Birimian greenstone belt, the same 
geological setting as major Ghanaian gold mines including Tarkwa, 
Asanko, and Bibiani. Rock types, alteration assemblages, grade 
distributions, and drill geometry are all calibrated to this setting.

## Files

| File | Description |
|------|-------------|
| `generate_data.py` | Main script — run this to generate all datasets |
| `collar.csv` | Drill hole collar locations and orientations |
| `lithology.csv` | Downhole lithology and alteration logging |
| `assay.csv` | 1-metre gold assay results with QA/QC flags |
| `composites.csv` | Mineralised intervals above 0.5 g/t Au cutoff |

## How to run

```bash
pip install numpy pandas
python generate_data.py
```

## Tools used
- Python 3.10+
- numpy, pandas
- Tableau Public (visualisation dashboard)

## Author
Emmanuel Ako-Addo | Geological Engineer & Data Analyst
[LinkedIn](https://linkedin.com/in/eakoaddo)
