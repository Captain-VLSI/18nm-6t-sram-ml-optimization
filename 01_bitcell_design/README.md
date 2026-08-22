# 01. 6T SRAM Bitcell Architecture & FinFET Sizing Space

## 6T SRAM Bitcell Schematic (Cadence Virtuoso cds_ff_mpt PDK)
![6T SRAM Bitcell Schematic](6t_sram_bitcell_schematic.png)

## Overview & Transistor Roles
The 6T SRAM bitcell is the fundamental Design Under Test (DUT), composed of 6 FinFET devices categorized into 3 functional pairs:
- **Pull-Up Transistors (P1 / P2):** 18nm standard-threshold PMOS (`p1svt`) devices maintaining the HIGH logic state against leakage.
- **Pull-Down Transistors (N1 / N2):** 18nm standard-threshold NMOS (`n1svt`) devices pulling internal nodes to GND during read/write transitions.
- **Access Transistors (AX1 / AX2):** Pass-gate NMOS (`n1svt`) devices gating access to Bitline (`BL`) and Bitline-Bar (`BLB`) controlled by Wordline (`WL`).
- **Internal Storage Latch (`Q` / `QB`):** Cross-coupled inverters forming the bistable storage element.

## 18nm FinFET Transistor Sizing Space
In modern FinFET nodes, transistor width is quantized by discrete vertical fins:
`W = N_fin * (2 * H_fin + T_fin)`

### Sizing Boundaries (Complete Cartesian Product = 5 × 6 × 5 = 150 Geometries):
- **Pull-Up PMOS (PU):** 1 to 5 fins (5 values)
- **Pull-Down NMOS (PD):** 1 to 6 fins (6 values)
- **Access NMOS (ACC):** 1 to 5 fins (5 values)
- **Total Discrete Geometries:** 5 × 6 × 5 = **150 physical bitcell configurations**.

### Essential Design Rules:
1. **Cell Ratio (CR - Read Stability Condition):**  
   `CR = N_fin,PD / N_fin,ACC >= 1.0` (Ensures the pull-down NMOS is stronger than the access NMOS, preventing destructive read disturb flips).
2. **Pull-Up Ratio (PR - Writeability Condition):**  
   `PR = N_fin,PU / N_fin,ACC <= 1.5` (Ensures the access NMOS can overpower the pull-up PMOS to force node Q low during write).
