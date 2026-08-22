# 06. Multi-Objective Pareto Optimization

This directory isolates the non-dominated Pareto-optimal frontiers balancing conflicting SRAM circuit design trade-offs across all 150 FinFET geometries at nominal 1.2V operation.

---

## Trade-off Projections:
1. **Read Stability vs. Write Delay:** Maximizing RSNM while minimizing $T_{write}$.
2. **Read Stability vs. Standby Leakage:** Maximizing RSNM while minimizing $I_{leak}$.
3. **Write Speed vs. Dynamic Energy:** Minimizing $T_{write}$ while minimizing dynamic write energy.

---

## Data Files in this Module:
- [`pareto_front.csv`](pareto_front.csv): 8 non-dominated optimal geometries at 1.2V.
- [`feasible_designs.csv`](feasible_designs.csv): 12 candidate bitcell geometries meeting nominal boundaries (RSNM >= 150 mV, Delay <= 150 ps, Leakage <= 80 nA).
- [`selected_profiles.csv`](selected_profiles.csv): Extracted data for the 4 golden design profiles.

---

## Scripts in this Module:
- `scripts/generate_pareto_and_eval_ml.py`: Generates the publication-grade 3-panel Pareto-front trade-off figure (`08_results/figures/fig_pareto_front_tradeoffs.png`).
