# 03. SRAM Dataset Data Dictionary

This document details the schema, column definitions, physical units, and extraction methodologies for the master SRAM dataset (`sram_master_unified_dataset.csv`) across the 18nm FinFET design space (1,200 SPICE configurations).

---

## 1. Geometric & Operating Features (Input Variables)

| Column Name | Description | Units | Range / Discrete Values |
| :--- | :--- | :---: | :---: |
| `nfin_pu` | Number of vertical fins for Pull-Up PMOS (P1, P2) | fins | 1, 2, 3, 4, 5 |
| `nfin_pd` | Number of vertical fins for Pull-Down NMOS (N1, N2) | fins | 1, 2, 3, 4, 5, 6 |
| `nfin_acc` | Number of vertical fins for Access NMOS (AX1, AX2) | fins | 1, 2, 3, 4, 5 |
| `vdd` | Supply Voltage | V | 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4 |
| `temp` | Operating Temperature | °C | 27 (Nominal Room Temperature) |
| `cr` | Cell Ratio: `nfin_pd / nfin_acc` | dimensionless | 0.20 to 6.00 |
| `pr` | Pull-Up Ratio: `nfin_pu / nfin_acc` | dimensionless | 0.20 to 5.00 |

---

## 2. Static Stability & Noise Margins (DC Sweeps)

| Column Name | Description | Units | Extraction Method |
| :--- | :--- | :---: | :--- |
| `hsnm_mv` | Hold Static Noise Margin | mV | Maximum square inscribed in hold-mode VTC butterfly curve (WL = 0V) |
| `rsnm_mv` | Read Static Noise Margin | mV | Maximum square inscribed in read-mode VTC butterfly curve (WL = VDD, BL = BLB = VDD) |
| `wsnm_mv` | Write Static Noise Margin (WTP) | mV | Bitline voltage at internal storage node crossing point during write |
| `wnm_mv` | Write Noise Margin | mV | Margin between internal node peak voltage and trip voltage |

---

## 3. Dynamic Read Mode (Transient Simulations)

| Column Name | Description | Units | Extraction Method |
| :--- | :--- | :---: | :--- |
| `read0_q_node_disturb_mv` | Low storage node voltage disturb bump during Read-0 | mV | Peak voltage reached by node Q during wordline pulse |
| `read0_read_energy_fj` | Dynamic energy dissipated during Read-0 operation | fJ | Time integral of supply current: `integral(VDD * I_VDD dt)` |
| `read0_read_power_uw` | Dynamic power dissipated during Read-0 operation | uW | Average active power over the read sensing window |
| `read0_average_read_current_ua` | Average current drawn from bitlines during read | uA | Integrated charge divided by read pulse duration |
| `read0_peak_read_current_ua` | Peak instantaneous current during read access | uA | Maximum current spike on supply rail |
| `read0_read_success` | Read operational integrity flag | binary | `1` = Data retained without flipping; `0` = Read disturb failure |

---

## 4. Dynamic Write Mode (Transient Simulations)

| Column Name | Description | Units | Extraction Method |
| :--- | :--- | :---: | :--- |
| `worst_write_delay_ps` | Maximum propagation delay across Write-0 and Write-1 | ps | Time difference from 50% WL rise to 50% storage node crossing |
| `write0_cell_write_delay_ps` | 50%-to-50% switching delay for writing '0' | ps | `t(V_Q = 0.5*VDD) - t(V_WL = 0.5*VDD)` |
| `write1_cell_write_delay_ps` | 50%-to-50% switching delay for writing '1' | ps | `t(V_QB = 0.5*VDD) - t(V_WL = 0.5*VDD)` |
| `worst_write_energy_fj` | Maximum dynamic write energy per bit transition | fJ | Time integral of total supply current during full write window |
| `worst_write_power_uw` | Peak dynamic power dissipation during write switching | uW | Maximum active power during internal latch flipping |
| `write0_peak_write_current_ua` | Peak instantaneous current during write-0 access | uA | Maximum current spike drawn from VDD / bitlines |
| `write0_write_success` | Write operational integrity flag | binary | `1` = Internal latch successfully flipped; `0` = Write failure |

---

## 5. Standby & Static Leakage

| Column Name | Description | Units | Extraction Method |
| :--- | :--- | :---: | :--- |
| `hold0_hold_leakage_current_na` | Standby quiescent leakage current (holding '0') | nA | Average quiescent current drawn from VDD with WL = 0V |
| `hold0_hold_power_uw` | Static standby power consumption | uW | `VDD * hold0_hold_leakage_current_na` |
| `hold0_hold_success` | Data retention flag in standby mode | binary | `1` = Bit retained across hold duration; `0` = State lost |
