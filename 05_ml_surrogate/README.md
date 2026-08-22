# 05. Machine Learning Surrogate Modeling

This module implements ML surrogate regression models that map discrete 18nm FinFET bitcell geometries and supply voltages directly to continuous electrical performance metrics.

---

## Model Architectures & Hyperparameters

| Hyperparameter | Random Forest Regressor | Gradient Boosted Decision Trees |
| :--- | :---: | :---: |
| **Number of Estimators** | 100 - 120 trees | 120 - 140 stages |
| **Maximum Tree Depth** | 12 | 5 |
| **Learning Rate** | - | 0.08 |
| **Feature Set** | `vdd`, `nfin_pu`, `nfin_pd`, `nfin_acc`, `cr`, `pr` | `vdd`, `nfin_pu`, `nfin_pd`, `nfin_acc`, `cr`, `pr` |
| **Evaluation Split** | Grouped 80/20 (`GroupShuffleSplit`, random_state = 42) | Grouped 80/20 (`GroupShuffleSplit`, random_state = 42) |
| **Held-Out Groups** | 30 full physical bitcell geometries (240 unseen test points) | 30 full physical bitcell geometries (240 unseen test points) |

---

## Evaluation Protocols
1. **Grouped 80/20 Unseen-Geometry Generalization:**  
   Holds out 30 full bitcell geometries (240 unseen test points across all 8 voltages) to evaluate model performance on novel physical silicon sizing.
2. **Voltage Interpolation Benchmark:**  
   Standard 80/20 random split assessing operational voltage prediction across known geometries.

---

## Scripts in this Module
- `scripts/evaluate_grouped_ml_surrogate.py`: Executes the 80/20 unseen geometry generalization benchmark.
- `scripts/train_sram_surrogate_models.py`: Trains Random Forest and Gradient Boosted regression models on the master dataset.
