# 01. 6T SRAM Bitcell Architecture & Design Space

## 6T SRAM Bitcell Schematic (Cadence Virtuoso)
![6T SRAM Bitcell Schematic](6t_sram_bitcell_schematic.png)

## Overview
The standard 6T SRAM bitcell is composed of:
- **Storage Element:** Two cross-coupled CMOS inverters (P1/N1 and P2/N2) forming a bistable latch.
- **Access Transistors:** Two pass-gate access NMOS transistors (AX1 and AX2) driven by the Wordline (WL).

## 18nm FinFET Transistor Sizing Space
In modern FinFET nodes, transistor width is quantized by the integer number of vertical fins:
`W = N_fins * (2 * H_fin + T_fin)`

### Sizing Boundaries (Complete Cartesian Product = 5 × 6 × 5 = 150 Geometries):
- **Pull-Up PMOS (PU):** 1 to 5 fins
- **Pull-Down NMOS (PD):** 1 to 6 fins
- **Access NMOS (ACC):** 1 to 5 fins

### Essential Design Rules:
1. **Cell Ratio (CR):** `CR = N_fin,PD / N_fin,ACC >= 1.0` (Maintains read stability against internal node disturbance).
2. **Pull-Up Ratio (PR):** `PR = N_fin,PU / N_fin,ACC <= 1.5` (Ensures access NMOS can overpower pull-up PMOS during write).
