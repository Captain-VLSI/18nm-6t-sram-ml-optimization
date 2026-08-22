# 05. Machine Learning Surrogate Models

This module implements ML surrogate models predicting SRAM metrics across the 18nm FinFET design space.

## Model Implementations
- **Random Forest Regressor:** 120 estimators, max depth 12.
- **Gradient Boosted Decision Trees:** 140 estimators, learning rate 0.08, max depth 5.

## Rigorous Evaluation Protocols
1. **Grouped 80/20 Unseen-Geometry Generalization:** Holds out 30 full bitcell geometries (240 test points across all voltages).
2. **Voltage Interpolation Benchmark:** Standard 80/20 random split assessing operational voltage prediction.
