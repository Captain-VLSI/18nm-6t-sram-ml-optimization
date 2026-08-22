#!/usr/bin/env python3
import os
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_squared_error

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
DATASET_PATH = os.path.join(REPO_ROOT, "03_dataset", "sram_master_unified_dataset.csv")

df = pd.read_csv(DATASET_PATH)
df['cr'] = df['nfin_pd'] / df['nfin_acc']
df['pr'] = df['nfin_pu'] / df['nfin_acc']

feature_cols = ['vdd', 'nfin_pu', 'nfin_pd', 'nfin_acc', 'cr', 'pr']
targets = ['rsnm_mv', 'hsnm_mv', 'wsnm_mv', 'worst_write_delay_ps', 'hold0_hold_leakage_current_na', 'worst_write_energy_fj']

print("=" * 80)
print("  TRAINING SRAM SURROGATE REGRESSION MODELS (80/20 SPLIT)")
print("=" * 80)

for tgt in targets:
    sub = df.dropna(subset=[tgt])
    X = sub[feature_cols].values
    y = sub[tgt].values
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)
    
    rf = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42).fit(X_train, y_train)
    gb = GradientBoostingRegressor(n_estimators=120, max_depth=5, learning_rate=0.08, random_state=42).fit(X_train, y_train)
    
    r2_rf = r2_score(y_test, rf.predict(X_test))
    r2_gb = r2_score(y_test, gb.predict(X_test))
    
    print(f"Target: {tgt:<28} | RF Test R2: {r2_rf:.4f} | GB Test R2: {r2_gb:.4f}")

print("\n[SUCCESS] Surrogate model training complete.")
