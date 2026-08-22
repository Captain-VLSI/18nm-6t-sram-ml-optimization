#!/usr/bin/env python3
import os
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
DATASET_PATH = os.path.join(REPO_ROOT, "03_dataset", "sram_master_unified_dataset.csv")

df = pd.read_csv(DATASET_PATH)
df['geom_id'] = df['nfin_pu'].astype(str) + "_" + df['nfin_pd'].astype(str) + "_" + df['nfin_acc'].astype(str)
df['cr'] = df['nfin_pd'] / df['nfin_acc']
df['pr'] = df['nfin_pu'] / df['nfin_acc']

feature_cols = ['vdd', 'nfin_pu', 'nfin_pd', 'nfin_acc', 'cr', 'pr']
targets = [
    ('rsnm_mv', 'RSNM (mV)'),
    ('hold0_hold_leakage_current_na', 'Hold Leakage (nA)'),
    ('worst_write_energy_fj', 'Write Energy (fJ)'),
    ('worst_write_delay_ps', 'Worst Write Delay (ps)'),
    ('hsnm_mv', 'HSNM (mV)'),
    ('wsnm_mv', 'WSNM (mV)')
]

gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
train_idx, test_idx = next(gss.split(df, groups=df['geom_id']))

train_df = df.iloc[train_idx]
test_df = df.iloc[test_idx]

print("=" * 95)
print("  UNSEEN GEOMETRY GENERALIZATION BENCHMARK (GROUPED 80/20 SPLIT)")
print("=" * 95)
print(f"Total Geometries: {df['geom_id'].nunique()} | Train Geometries: {train_df['geom_id'].nunique()} | Test Geometries: {test_df['geom_id'].nunique()}")
print(f"Total Samples   : {len(df)} | Train Samples   : {len(train_df)} | Test Samples   : {len(test_df)}\n")

for tgt_col, tgt_name in targets:
    sub_tr = train_df.dropna(subset=[tgt_col])
    sub_te = test_df.dropna(subset=[tgt_col])
    
    X_train = sub_tr[feature_cols].values
    y_train = sub_tr[tgt_col].values
    X_test = sub_te[feature_cols].values
    y_test = sub_te[tgt_col].values
    
    rf = RandomForestRegressor(n_estimators=120, max_depth=12, random_state=42).fit(X_train, y_train)
    gb = GradientBoostingRegressor(n_estimators=140, max_depth=5, learning_rate=0.08, random_state=42).fit(X_train, y_train)
    
    y_pred_rf = rf.predict(X_test)
    y_pred_gb = gb.predict(X_test)
    
    r2_rf = r2_score(y_test, y_pred_rf)
    r2_gb = r2_score(y_test, y_pred_gb)
    
    print(f"[{tgt_name}]")
    print(f"  Random Forest   -> Unseen Geom Test R2: {r2_rf:.4f} | RMSE: {np.sqrt(mean_squared_error(y_test, y_pred_rf)):.3f} | MAE: {mean_absolute_error(y_test, y_pred_rf):.3f}")
    print(f"  Gradient Boost  -> Unseen Geom Test R2: {r2_gb:.4f} | RMSE: {np.sqrt(mean_squared_error(y_test, y_pred_gb)):.3f} | MAE: {mean_absolute_error(y_test, y_pred_gb):.3f}")

print("\n" + "=" * 95)
