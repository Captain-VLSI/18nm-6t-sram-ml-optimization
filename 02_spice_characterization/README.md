# 02. SPICE Characterization & Cadence Virtuoso Testbenches

This directory documents the Cadence Virtuoso ADE testbench environments, DC sweeps, transient dynamic responses, and automated dataset generation scripts across all 150 FinFET geometries and 8 supply voltages (1,200 SPICE simulation runs) in the Cadence Generic 18nm FinFET PDK (`cds_ff_mpt`).

---

## 1. DC Static Margins Characterization

### A. Hold Static Noise Margin (HSNM)
- **Simulation Type:** DC Voltage Sweep (0V to VDD, 1 mV step) with `WL = 0V`.
- **Measurement:** Back-to-back Inverter Voltage Transfer Curves (VTCs) extracting the maximum square in the hold state.

<p align="center">
  <img src="cadence_hsnm_dc_butterfly_0.9v.png" alt="Cadence ADE HSNM DC Butterfly Waveform" width="750"/>
</p>

### B. Read Static Noise Margin (RSNM)
- **Simulation Type:** DC Voltage Sweep (0V to VDD, 1 mV step) with `WL = VDD`, `BL = BLB = VDD`.
- **Measurement:** Inverter VTCs under active wordline disturbance to determine read stability and prevent destructive state flipping.

<p align="center">
  <img src="cadence_rsnm_dc_butterfly_0.9v.png" alt="Cadence ADE RSNM DC Butterfly Waveform" width="750"/>
</p>

### C. Write Trip Point (WTP) & Write Static Margin (WSNM)
- **Simulation Type:** DC Voltage Sweep on bitline (`VBLB: 0V -> VDD`, 1 mV step) with `WL = VDD`, initial state `Q = 0, QB = VDD`.
- **Measurement:** Bitline voltage level at which the internal storage latch transitions state (Trip Point = 302.0 mV @ 0.9V).

<p align="center">
  <img src="cadence_wtp_wsnm_dc_sweep_0.9v.png" alt="Cadence ADE Write Trip Point DC Sweep Waveform" width="750"/>
</p>

---

## 2. Dynamic Transient Response Characterization

### A. Dynamic Read Sensing & Read Disturb Bump (Dual-Polarity)
- **Simulation Type:** Transient Dynamic Response (0 to 100 ns, maxstep = 0.5 ps) with `WL` pulse train and precharged bitlines (`BL = BLB = VDD`).
- **Read-1 Operation (`Q = VDD, QB = 0`):** Access transistor transfers bitline charge, producing a bounded voltage disturb bump on `QB` without destructive latch flipping.
- **Read-0 Operation (`Q = 0, QB = VDD`):** Verifies complementary read stability with bounded disturb bump on `Q`.

| Read-1 Dynamic Response (QB Disturb Bump) | Read-0 Dynamic Response (Q Disturb Bump) |
| :---: | :---: |
| ![Read-1 Dynamic Response](cadence_read1_transient_disturb_0.9v.png) | ![Read-0 Dynamic Response](cadence_read0_transient_disturb_0.9v.png) |

### B. Dynamic Multi-Cycle Write Switching Response
- **Simulation Type:** Transient Multi-Cycle Response (0 to 100 ns, maxstep = 1 ps).
- **Stimulus:** `WL` pulsed HIGH (10 ns width, 20 ns period), `BL` and `BLB` driven differentially with alternating Write-0 and Write-1 data.
- **Measurement:** 50%-to-50% write switching propagation delay (T_write) and dynamic switching energy integration.

<p align="center">
  <img src="cadence_write_multicycle_transient_0.9v.png" alt="Cadence ADE Transient Multi-Cycle Write Response" width="750"/>
</p>

---

## 3. Dataset Generation Python Scripts (`dataset_generation_scripts/`)

- [`generate_snm_dataset.py`](dataset_generation_scripts/generate_snm_dataset.py): Automates DC butterfly sweeps and extracts Hold, Read, and Write SNMs via Seevinck rotation.
- [`generate_standalone_sram_hold_dataset.py`](dataset_generation_scripts/generate_standalone_sram_hold_dataset.py): Automates standby leakage current (I_leak) and static power (P_leak) characterization.
- [`generate_standalone_sram_read_dataset.py`](dataset_generation_scripts/generate_standalone_sram_read_dataset.py): Automates dynamic Read-0/Read-1 sensing and disturb bump measurements.
- [`generate_standalone_sram_write_dataset.py`](dataset_generation_scripts/generate_standalone_sram_write_dataset.py): Automates transient Write-0/Write-1 switching delays and dynamic write energies.
