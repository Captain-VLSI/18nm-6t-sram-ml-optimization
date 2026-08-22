# ⚡ 6T SRAM Bitcell Characterization, Validation, and ML-Assisted Design-Space Optimization in 18nm FinFET

[![Cadence Spectre](https://img.shields.io/badge/Cadence-Spectre_Verification-red.svg)](https://www.cadence.com)
[![Process](https://img.shields.io/badge/Technology-18nm_FinFET-blue.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Verification](https://img.shields.io/badge/Verification-24%2F24_Passed-brightgreen.svg)](#)

A comprehensive multi-objective design, machine learning surrogate modeling, and Cadence Spectre independent verification framework for sub-nanosecond 6T SRAM bitcells in an advanced 18nm FinFET process.

---

## 📊 Verification Dashboard & Multi-Objective Tradeoffs

| Closed-Loop Parity Dashboard | Multi-Objective Pareto-Front Projections |
| :---: | :---: |
| ![Master Dashboard](08_results/figures/fig_validation_master_dashboard.png) | ![Pareto Frontiers](08_results/figures/fig_pareto_front_tradeoffs.png) |

---

## 🏛️ Cadence Virtuoso 6T SRAM Bitcell & Testbenches

| 18nm FinFET 6T Bitcell Schematic | Hold SNM DC Testbench |
| :---: | :---: |
| ![6T Bitcell Schematic](01_bitcell_design/6t_sram_bitcell_schematic.png) | ![HSNM Testbench](02_spice_characterization/hsnm_testbench_schematic.png) |

| Transient Write & Hold Testbench | Cadence ADE Transient Multi-Cycle Response |
| :---: | :---: |
| ![Write Hold Testbench](02_spice_characterization/write_hold_testbench_schematic.png) | ![Write Hold Waveform](08_results/figures/write_hold_cadence_waveform_graph.png) |

---

## 🏆 4 Golden Verified Design Profiles

| Design Profile | Transistor Sizing (PU / PD / ACC) | Supply Voltage (VDD) | RSNM (mV) | WTP (mV) | Write Delay (ps) | Hold Leakage (nA) | Verification Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Balanced Reference** | **1 / 1 / 1 fins** | **1.2 V** | 190.22 | 432.00 | 144.53 | 47.92 | **PASS (< 0.13% error)** |
| **Low-Power Profile** | **1 / 1 / 1 fins** | **0.9 V** | 145.10 | 302.00 | 149.87 | 17.56 | **PASS (< 0.19% error)** |
| **Fast SRAM Profile** | **5 / 2 / 4 fins** | **1.2 V** | 153.49 | 503.00 | 134.58 | 58.74 | **PASS (< 0.04% error)** |
| **CR-Enhanced Stability** | **2 / 3 / 2 fins** | **1.2 V** | 204.26 | 373.00 | 144.24 | 49.31 | **PASS (< 0.13% error)** |

---

## 🦋 Static Noise Margin (SNM) Butterfly Characterization

| Seevinck Rotated Butterfly Curves (Inscribed Squares) | Cadence Virtuoso ADE DC Transfer Waves |
| :---: | :---: |
| ![SNM Butterfly Curves](08_results/figures/fig_snm_butterflies_perfect_unified.png) | ![Cadence DC Butterfly](08_results/figures/hsnm_cadence_waveform_graph.png) |

---

## ⚡ Dynamic Write & Read Switching Waveforms

| Dynamic Write Switching Transitions (50%-50% Delay) | Write Trip Point (WTP) & Write Noise Margin (WNM) |
| :---: | :---: |
| ![Write Delay Waveforms](08_results/figures/fig_validation_3_transient_write_waveforms.png) | ![WTP & WNM Dashboard](08_results/figures/fig_wtp_wnm_premium_4panel.png) |

---

## 🔄 End-to-End Engineering Methodology Flow

The project follows a rigorous circuit design, characterization, surrogate modeling, and verification hierarchy:
- **The 6T SRAM Bitcell is the Design Under Test (DUT)**
- **SPICE Simulation is the Characterization Mechanism**
- **Machine Learning is the Fast Design-Space Optimization Mechanism**
- **Spectre Re-Simulation is the Independent Verification Mechanism**

```text
STAGE 1: 6T SRAM BITCELL ARCHITECTURE & PARAMETER DEFINITION
         Define 6T topology, transistor roles (P1/P2 PU, N1/N2 PD, AX1/AX2 ACC),
         and FinFET sizing boundaries: PU = 1–5 fins, PD = 1–6 fins, ACC = 1–5 fins.
         Complete Cartesian design space = 5 × 6 × 5 = 150 geometries.
                    ↓
STAGE 2: CADENCE SCHEMATICS & TESTBENCH SETUP
         Configure Hold (WL=0), Read (WL=VDD, precharged BL/BLB), Write (BL pulsed low),
         and Standby Leakage testbenches.
                    ↓
STAGE 3: AUTOMATED SPICE DESIGN-SPACE SWEEP
         Execute 1,200 Cadence Spectre netlist sweeps (150 Cartesian geometries × 8 VDD levels).
                    ↓
STAGE 4: ELECTRICAL CHARACTERIZATION & FEATURE EXTRACTION
         Extract static margins (HSNM, RSNM, WSNM), dynamic write trip points (WTP, WNM),
         50%-to-50% switching delays, dynamic energy, and standby leakage.
                    ↓
STAGE 5: UNIFIED MASTER DATASET CONSOLIDATION
         Structure 1,200 SPICE-characterized configurations across 60+ electrical metrics.
                    ↓
STAGE 6: ML SURROGATE MODELING & RIGOROUS EVALUATION
         Train Random Forest & Gradient Boosted regressors; evaluate under both
         Unseen-Geometry Generalization (Grouped 80/20) and Voltage Interpolation.
                    ↓
STAGE 7: CONSTRAINT FILTERING
         Screen for Nominal 1.2V boundaries (RSNM >= 150 mV, Delay <= 150 ps, Leakage <= 80 nA)
         and Multi-VDD Robustness (RSNM > 0 mV across all 8 simulated VDD levels).
                    ↓
STAGE 8: MULTI-OBJECTIVE PARETO DOMINANCE ANALYSIS
         Identify non-dominated solutions across RSNM (maximize), Write Delay (minimize),
         Hold Leakage (minimize), and Dynamic Energy (minimize).
                    ↓
STAGE 9: SELECTION OF 4 REPRESENTATIVE DESIGN PROFILES
         Select Balanced Reference, Low-Power, Fast SRAM, and CR-Enhanced bitcells.
                    ↓
STAGE 10: INDEPENDENT CADENCE SPECTRE RE-SIMULATION & VERIFICATION
          Re-simulate golden candidates in Spectre; 24/24 verification test cases passed
          the < 1.0% individual-error threshold (mean absolute error < 0.3%).
                    ↓
STAGE 11: PUBLICATION ARTIFACTS & GITHUB PRESENTATION
          Generate publication-grade waveform plots, design notes, and documentation.
```

---

## 🤖 Comprehensive Multi-Parameter ML Surrogate Audit

| Parameter Category | Characterized Parameter | Unit | Range [Min, Max] | Best Model Architecture | Unseen Geometry Test (R2) | Unseen Geometry MAE | Voltage Interpolation (R2) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Static Stability** | Read Static Noise Margin (RSNM) | mV | [24.12, 281.87] | Random Forest | **0.9903** | 4.65 mV | 0.9984 |
| | Hold Static Noise Margin (HSNM) | mV | [112.45, 412.30] | Random Forest | **0.9854** | 6.82 mV | 0.9972 |
| | Write Static Noise Margin (WSNM / WTP) | mV | [180.20, 580.40] | Gradient Boost | **0.9912** | 5.14 mV | 0.9989 |
| **Dynamic Read** | Worst Read Disturb Voltage | mV | [12.40, 148.90] | Random Forest | **0.9876** | 2.31 mV | 0.9978 |
| | Read Access Energy | fJ | [0.045, 0.482] | Gradient Boost | **0.9998** | 0.003 fJ | 0.9999 |
| | Read Operation Power | uW | [0.220, 2.410] | Gradient Boost | **0.9996** | 0.015 uW | 0.9999 |
| **Standby & Leakage** | Static Standby Power | uW | [0.008, 0.145] | Gradient Boost | **0.8912** | 0.006 uW | 0.9915 |
| | Average Hold Leakage Current | nA | [7.12, 118.45] | Gradient Boost | **0.8861** | 10.37 nA | 0.9908 |
| **Dynamic Write** | Peak Write Current | uA | [18.50, 94.20] | Random Forest | **0.9945** | 1.12 uA | 0.9992 |
| | Average Dynamic Write Energy | fJ | [0.082, 0.612] | Gradient Boost | **0.9989** | 0.005 fJ | 0.9998 |
| | Worst Write Switching Delay | ps | [118.20, 198.50] | Gradient Boost | **0.1524** (cliff) | 9.85 ps | **0.8696** (MAE 4.53 ps) |

---

## 🚀 Quick Start & Reproducibility

```bash
# Clone the repository
git clone https://github.com/Captain-VLSI/18nm-6t-sram-ml-optimization.git
cd 18nm-6t-sram-ml-optimization

# Install dependencies
pip install -r requirements.txt

# Regenerate all publication figures
python scripts/generate_all_figures.py

# Execute full ML training and parameter audit
python scripts/run_all_analysis.py
```

---

## 📜 License & Citation
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.  
Created and maintained by **Captain-VLSI** (`ganeshs78gani@gmail.com`).
