# 03. SRAM Datasets & Waveform Catalog

This directory contains the consolidated master dataset, raw Cadence Spectre simulation waveforms, and schema definitions.

---

## Master Unified Dataset
- **File:** [`sram_master_unified_dataset.csv`](sram_master_unified_dataset.csv)
- **Configurations:** 1,200 rows (150 geometries × 8 supply voltages: 0.7V, 0.8V, 0.9V, 1.0V, 1.1V, 1.2V, 1.3V, 1.4V)
- **Features Extracted:** 62 continuous and discrete electrical parameters across static stability, dynamic read, dynamic write, and standby leakage.
- **Data Dictionary:** See [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md) for full column definitions, units, and extraction methods.

---

## Raw Cadence Spectre Waveform Catalog (`raw_waveforms/`)
Archived raw simulation CSV files for the four golden design points (6 CSVs per profile: HSNM, RSNM, WTP, Write_Hold, Read0, Read1):
- 📁 **`raw_waveforms/balanced/`**: Balanced Reference (1/1/1 @ 1.2V)
- 📁 **`raw_waveforms/low_power/`**: Low-Power Profile (1/1/1 @ 0.9V)
- 📁 **`raw_waveforms/fast_sram/`**: Fast SRAM Profile (5/2/4 @ 1.2V)
- 📁 **`raw_waveforms/cr_enhanced/`**: CR-Enhanced Stability Profile (2/3/2 @ 1.2V)

---

## Dataset Consolidation Pipeline
- **Script:** [`scripts/merge_and_build_master_dataset.py`](scripts/merge_and_build_master_dataset.py)  
  Merges static DC sweeps and transient dynamic CSVs into the 1,200-row unified master dataset.
