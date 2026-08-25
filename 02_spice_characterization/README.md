# 02. SPICE Characterization & Cadence Virtuoso Testbenches

This directory documents the Cadence Virtuoso ADE testbench environments, DC sweeps, transient dynamic responses, and automated dataset generation scripts across all 150 FinFET geometries and 8 supply voltages (1,200 SPICE simulation runs) in the Cadence Generic 18nm FinFET PDK (`cds_ff_mpt`).

---

## 1. DC Static Margins Characterization

### A. Hold Static Noise Margin (HSNM)
- **Simulation Type:** DC Voltage Sweep (`0V -> VDD`, 1 mV step) on internal storage nodes with `WL = 0V` (Access transistors OFF).
- **Circuit Behavior:** Overlays the back-to-back Inverter Voltage Transfer Curves (`q vs qb` and `qb vs q`). The side length of the maximum inscribed square inside the butterfly eyes quantifies the static noise immunity in standby hold mode (`HSNM = 281.54 mV @ 0.9V`).

<p align="center">
  <img src="cadence_hsnm_dc_butterfly_0.9v.png" alt="Cadence ADE Hold SNM DC Butterfly Waveform" width="850"/>
</p>

---

### B. Read Static Noise Margin (RSNM)
- **Simulation Type:** DC Voltage Sweep (`0V -> VDD`, 1 mV step) with `WL = VDD` and bitlines precharged to `VDD`.
- **Circuit Behavior:** Access transistors conduct, creating a resistive voltage divider between the pull-down NMOS and access NMOS. This elevates the low-node voltage and narrows the butterfly opening. The non-zero inscribed square verifies non-destructive read stability without state flipping (`RSNM = 145.10 mV @ 0.9V`).

<p align="center">
  <img src="cadence_rsnm_dc_butterfly_0.9v.png" alt="Cadence ADE Read SNM DC Butterfly Waveform" width="850"/>
</p>

---

### C. Write Trip Point (WTP) & Write Static Margin (WSNM)
- **Simulation Type:** DC Voltage Sweep on Bitline-Bar (`VBLB: 0V -> VDD`, 1 mV step) with `WL = VDD` and initial state `Q = 0, QB = VDD`.
- **Circuit Behavior:** As `VBLB` decreases, the access transistor pulls node `QB` low. At `V_trip = 302.0 mV` (for the 0.9V profile), regenerative inverter feedback triggers and flips the storage nodes (`Q -> 0.9V, QB -> 0V`), defining the writeability margin.

<p align="center">
  <img src="cadence_wtp_wsnm_dc_sweep_0.9v.png" alt="Cadence ADE Write Trip Point DC Sweep Waveform" width="850"/>
</p>

---

## 2. Dynamic Transient Response Characterization

### A. Dynamic Read-1 Transient Response & QB Disturb Bump
- **Simulation Type:** Time-domain transient simulation (0 to 100 ns) with periodic wordline pulses (20 ns period) and bitlines precharged to `0.9V` holding data '1' (`Q = 0.9V, QB = 0V`).
- **Circuit Behavior:** When `WL` pulses HIGH, charge flows from precharged `BLB` through access transistor `AX2` into node `QB`, creating a small transient disturb bump (~125 mV). The bump remains safely below the inverter threshold, confirming stable, non-destructive read access.

<p align="center">
  <img src="cadence_read1_transient_disturb_0.9v.png" alt="Cadence ADE Read-1 Dynamic Transient Response" width="850"/>
</p>

---

### B. Dynamic Read-0 Transient Response & Q Disturb Bump
- **Simulation Type:** Complementary time-domain read transient simulation (0 to 100 ns) holding data '0' (`Q = 0V, QB = 0.9V`).
- **Circuit Behavior:** Upon `WL` assertion, bitline charge sharing produces a bounded voltage bump on node `Q` (~125 mV). Symmetrical disturb suppression across both nodes confirms robust cell ratio (CR) sizing under 18nm FinFET quantization.

<p align="center">
  <img src="cadence_read0_transient_disturb_0.9v.png" alt="Cadence ADE Read-0 Dynamic Transient Response" width="850"/>
</p>

---

### C. Dynamic Multi-Cycle Write Switching Response
- **Simulation Type:** Time-domain multi-cycle transient simulation (0 to 100 ns) applying alternating Write-0 (`BL = 0V, BLB = 0.9V`) and Write-1 (`BL = 0.9V, BLB = 0V`) pulses with synchronous 10 ns `WL` strobes.
- **Circuit Behavior:** Demonstrates rapid, rail-to-rail dynamic flipping of internal nodes `Q` and `QB` within < 150 ps of wordline activation, verifying robust write switching and clean state retention during hold cycles.

<p align="center">
  <img src="cadence_write_multicycle_transient_0.9v.png" alt="Cadence ADE Multi-Cycle Write Transient Response" width="850"/>
</p>

---

## 3. Dataset Generation Python Scripts (`dataset_generation_scripts/`)

- [`generate_snm_dataset.py`](dataset_generation_scripts/generate_snm_dataset.py): Automates DC butterfly sweeps and extracts Hold, Read, and Write SNMs via Seevinck rotation.
- [`generate_standalone_sram_hold_dataset.py`](dataset_generation_scripts/generate_standalone_sram_hold_dataset.py): Automates standby leakage current (I_leak) and static power (P_leak) characterization.
- [`generate_standalone_sram_read_dataset.py`](dataset_generation_scripts/generate_standalone_sram_read_dataset.py): Automates dynamic Read-0/Read-1 sensing and disturb bump measurements.
- [`generate_standalone_sram_write_dataset.py`](dataset_generation_scripts/generate_standalone_sram_write_dataset.py): Automates transient Write-0/Write-1 switching delays and dynamic write energies.
