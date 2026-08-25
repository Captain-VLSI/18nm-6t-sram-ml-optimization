# 08. Results & Publication Figure Gallery

This directory contains high-DPI publication figures, multi-objective Pareto-front projections, ML surrogate validation plots, and raw Cadence Virtuoso ADE verification waveforms across all 150 FinFET geometries and 8 supply voltages.

---

## 1. 1,200-Point Characterization Feasibility & Failure Analysis

<p align="center">
  <img src="figures/fig1_feasibility_and_failures.png" alt="Operating Point Feasibility Yield and Breakdown of Failure Mechanisms" width="850"/>
</p>

*Physical yield across supply voltages (0.6V to 1.3V) and occurrence breakdown of failure modes (write switching failure, WSNM sentinel, collapsed hold/read SNM, and read disturb flipping).*

---

## 2. GroupKFold ML Surrogate Generalization Parity Plots (Unseen Geometries)

<p align="center">
  <img src="figures/fig2_parity_plots_groupkfold.png" alt="GroupKFold Surrogate Parity Plots on Unseen Geometries" width="850"/>
</p>

*Parity verification comparing Cadence SPICE ground truth against ML surrogate predictions across 30 held-out physical bitcell geometries: (a) Static Read Margin (RSNM, R2 = 0.9892), (b) Static Write Margin (WSNM, R2 = 0.9127), (c) Worst Write Delay (MAE = 10.96 ps), and (d) Average Write Energy (MAE = 0.35 fJ).*

---

## 3. Computational Runtime Speedup Benchmark (SPICE vs. ML Surrogate)

<p align="center">
  <img src="figures/fig6_computational_speedup_benchmark.png" alt="Computational Runtime Comparison: Cadence Spectre SPICE vs. ML Surrogate" width="850"/>
</p>

*Quantifies the ~248,200x speedup achieved by the ML surrogate (65.27 ms for 1,200 points) compared to transistor-level Cadence Spectre SPICE (~4.50 hours).*

---

## 4. Multi-Objective Pareto-Optimal Tradeoff Frontiers

<p align="center">
  <img src="figures/fig_pareto_front_tradeoffs.png" alt="18nm FinFET 6T SRAM Multi-Objective Pareto-Optimal Tradeoffs" width="850"/>
</p>

*Multi-dimensional trade-off projections across all 150 geometries @ 1.2V: Read Stability vs. Write Delay, Read Stability vs. Hold Leakage Current, and Write Speed vs. Dynamic Write Energy.*

---

## 5. Pareto Frontier Projections & Ground-Truth SPICE Recovery

<p align="center">
  <img src="figures/fig3_pareto_frontier_projections.png" alt="Pareto Frontier Projections and Ground-Truth SPICE Recovery" width="850"/>
</p>

*Overlay of the NSGA-II discovered non-dominated front against the 435 ground-truth SPICE Pareto designs.*

---

## 6. NSGA-II Multi-Objective Convergence & Generational Distance

<p align="center">
  <img src="figures/fig4_nsga2_convergence_scaling.png" alt="NSGA-II Multi-Objective Convergence and Generational Distance" width="850"/>
</p>

*Evolutionary convergence scaling showing 100.0% Hypervolume (HV) coverage and rapid reduction in Inverted Generational Distance (IGD).*

---

## 7. Closed-Loop Cadence Transistor-Level Golden Validation Dashboard

<p align="center">
  <img src="figures/fig_validation_master_dashboard.png" alt="Cadence Spectre Transistor-Level Golden Re-Simulation Validation Dashboard" width="850"/>
</p>

*Transistor-level re-simulation parity check across all 4 golden application profiles showing absolute relative errors strictly below 1.0%.*

---

## 8. Unified Static Noise Margin (SNM) Butterfly Curves & Inscribed Squares

<p align="center">
  <img src="figures/fig_snm_butterflies_perfect_unified.png" alt="Unified SNM Butterfly Curves with Geometric Inscribed Squares" width="850"/>
</p>

*Hold SNM (top row) and Read SNM (bottom row) butterfly curves with exact geometric inscribed squares for Balanced, Low-Power, Fast, and CR-Enhanced profiles.*

---

## 9. Write Trip Point (WTP) & Write Noise Margin (WNM) 4-Panel Dashboard

<p align="center">
  <img src="figures/fig_wtp_wnm_premium_4panel.png" alt="Write Trip Point and Write Noise Margin 4-Panel Dashboard" width="850"/>
</p>

*DC write trip point transition sweeps displaying internal node voltages (Q and QB) and writeability margins.*

---

## 10. Dynamic Transient Write Delay Waveforms (50%-to-50% Switching)

<p align="center">
  <img src="figures/fig_validation_3_transient_write_waveforms.png" alt="Cadence Spectre Transient Write Delay Characterization" width="850"/>
</p>

*Time-domain dynamic write switching waveforms demonstrating sub-135 ps access delay for the Fast SRAM profile.*

---

## 11. Dynamic Transient Read Waveforms (Differential Sensing & Voltage Bump)

<p align="center">
  <img src="figures/fig_validation_4_transient_read_waveforms.png" alt="Cadence Spectre Transient Read Dynamic Waveforms and Disturb Bump" width="850"/>
</p>

*Time-domain read access sensing and internal node disturb bump suppression across all 4 design profiles.*
