# 02. SPICE Characterization & Testbenches

This directory documents the Cadence Virtuoso testbench environments, simulation setups, and dataset generation scripts used across all 150 FinFET geometries and 8 supply voltages (1,200 SPICE simulations).

---

## 1. Hold Static Noise Margin (HSNM) Characterization
- **Simulation Type:** DC Voltage Sweep
- **Wordline:** Held at `WL = 0V` (Access transistors OFF).
- **Sweep:** Internal storage node voltage swept from `0V` to `VDD` (1 mV resolution) to extract back-to-back Inverter Voltage Transfer Curves (VTCs).

<p align="center">
  <img src="hsnm_cadence_waveform_graph.png" alt="Cadence ADE DC Butterfly Waveform" width="750"/>
</p>

---

## 2. Transient Write & Hold Characterization
- **Simulation Type:** Transient Dynamic Response (0 to 100 ns, maxstep = 1 ps)
- **Wordline (WL):** Pulsed HIGH (`0V -> VDD`, tr = tf = 10 ps) for write cycles, held LOW (`0V`) for hold retention.
- **Bitlines (BL / BLB):** Driven differentially (`BL = 0V, BLB = VDD` for Write-0; `BL = VDD, BLB = 0V` for Write-1).
- **Measurement:** 50%-to-50% switching propagation delay (T_write) and dynamic energy integration.

<p align="center">
  <img src="write_hold_cadence_waveform_graph.png" alt="Cadence ADE Transient Response Waveforms" width="750"/>
</p>

---

## 3. Dataset Generation Python Scripts (`dataset_generation_scripts/`)
- `generate_snm_dataset.py`: Automates DC butterfly sweeps and extracts Hold, Read, and Write SNMs.
- `generate_standalone_sram_hold_dataset.py`: Automates standby leakage ($I_{leak}$) and static power ($P_{leak}$) characterization.
- `generate_standalone_sram_read_dataset.py`: Automates dynamic Read-0/Read-1 sensing and disturb bump measurements.
- `generate_standalone_sram_write_dataset.py`: Automates transient Write-0/Write-1 switching delays and dynamic write energies.
