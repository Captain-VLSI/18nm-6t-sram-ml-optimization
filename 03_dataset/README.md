# 03. SRAM Characterization Datasets

## Master Unified Dataset
- **File:** `sram_master_unified_dataset.csv`
- **Total Configurations:** 1,200 rows (150 geometries × 8 supply voltages: 0.7V to 1.4V)
- **Extracted Metrics (62 Features):**
  - Static Noise Margins: HSNM, RSNM, WSNM, Write Trip Point (WTP), Write Noise Margin (WNM)
  - Dynamic Write Parameters: 50%-50% Write Delays (T_write0, T_write1), Write Energies, Peak Currents
  - Dynamic Read Parameters: Read Disturb Bumps, Read Access Energies, Read Powers
  - Standby & Leakage: Static Leakage Currents (I_leak), Static Hold Powers (P_hold)

## Raw Cadence Spectre Waveform Catalog
All raw simulation CSV waveforms for the four golden design points are archived under `raw_waveforms/`:
- `balanced/`: Balanced Reference (1/1/1 @ 1.2V)
- `low_power/`: Low-Power Profile (1/1/1 @ 0.9V)
- `fast_sram/`: Fast SRAM Profile (5/2/4 @ 1.2V)
- `cr_enhanced/`: CR-Enhanced Stability Profile (2/3/2 @ 1.2V)
