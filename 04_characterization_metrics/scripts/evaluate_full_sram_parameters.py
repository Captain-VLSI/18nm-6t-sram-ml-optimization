#!/usr/bin/env python3
import os
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit, train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
DATASET_PATH = os.path.join(REPO_ROOT, "03_dataset", "sram_master_unified_dataset.csv")
OUT_CSV = os.path.join(REPO_ROOT, "07_verification", "full_sram_parameters_ml_audit.csv")

df = pd.read_csv(DATASET_PATH)
df['geom_id'] = df['nfin_pu'].astype(str) + "_" + df['nfin_pd'].astype(str) + "_" + df['nfin_acc'].astype(str)
df['cr'] = df['nfin_pd'] / df['nfin_acc']
df['pr'] = df['nfin_pu'] / df['nfin_acc']

feature_cols = ['vdd', 'nfin_pu', 'nfin_pd', 'nfin_acc', 'cr', 'pr']

PARAM_CATEGORIES = {
    "1. Static Stability Margins": [
        ('rsnm_mv', 'Read Static Noise Margin (RSNM)', 'mV'),
        ('hsnm_mv', 'Hold Static Noise Margin (HSNM)', 'mV'),
        ('wsnm_mv', 'Write Static Noise Margin (WSNM / WTP)', 'mV'),
    ],
    "2. Dynamic Read Mode": [
        ('read0_q_node_disturb_mv', 'Worst Read Disturb Voltage', 'mV'),
        ('read0_read_energy_fj', 'Read Access Energy', 'fJ'),
        ('read0_read_power_uw', 'Read Operation Power', 'uW'),
    ],
    "3. Standby & Leakage": [
        ('hold0_hold_power_uw', 'Static Standby Power', 'uW'),
        ('hold0_hold_leakage_current_na', 'Average Hold Leakage Current', 'nA'),
    ],
    "4. Dynamic Write Mode": [
        ('write0_peak_write_current_ua', 'Peak Write Current', 'uA'),
        ('worst_write_energy_fj', 'Average Dynamic Write Energy', 'fJ'),
        ('worst_write_delay_ps', 'Worst Write Switching Delay', 'ps'),
    ]
}

gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
tr_idx, te_idx = next(gss.split(df, groups=df['geom_id']))
train_df, test_df = df.iloc[tr_idx], df.iloc[te_idx]

print("=" * 105)
print("  RUNNING FULL 5-CATEGORY SRAM PARAMETER AUDIT")
print("=" * 105)

all_results = []

for cat_name, param_list in PARAM_CATEGORIES.items():
    print(f"\n--- {cat_name} ---")
    for col, name, unit in param_list:
        sub_tr = train_df.dropna(subset=[col])
        sub_te = test_df.dropna(subset=[col])
        sub_all = df.dropna(subset=[col])
        
        X_tr = sub_tr[feature_cols].values
        y_tr = sub_tr[col].values
        X_te = sub_te[feature_cols].values
        y_te = sub_te[col].values
        
        X_tr_r, X_te_r, y_tr_r, y_te_r = train_test_split(sub_all[feature_cols].values, sub_all[col].values, test_size=0.20, random_state=42)
        
        rf = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42).fit(X_tr, y_tr)
        gb = GradientBoostingRegressor(n_estimators=120, max_depth=5, learning_rate=0.08, random_state=42).fit(X_tr, y_tr)
        
        rf_r = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42).fit(X_tr_r, y_tr_r)
        gb_r = GradientBoostingRegressor(n_estimators=120, max_depth=5, learning_rate=0.08, random_state=42).fit(X_tr_r, y_tr_r)
        
        pred_rf_geom = rf.predict(X_te)
        pred_gb_geom = gb.predict(X_te)
        pred_rf_row = rf_r.predict(X_te_r)
        pred_gb_row = gb_r.predict(X_te_r)
        
        r2_rf_g = r2_score(y_te, pred_rf_geom)
        r2_gb_g = r2_score(y_te, pred_gb_geom)
        
        if r2_gb_g >= r2_rf_g:
            best_model_g = "Gradient Boost"
            best_r2_g = r2_gb_g
            best_rmse_g = np.sqrt(mean_squared_error(y_te, pred_gb_geom))
            best_mae_g = mean_absolute_error(y_te, pred_gb_geom)
        else:
            best_model_g = "Random Forest"
            best_r2_g = r2_rf_g
            best_rmse_g = np.sqrt(mean_squared_error(y_te, pred_rf_geom))
            best_mae_g = mean_absolute_error(y_te, pred_rf_geom)
            
        r2_rf_r = r2_score(y_te_r, pred_rf_row)
        r2_gb_r = r2_score(y_te_r, pred_gb_row)
        best_r2_r = max(r2_rf_r, r2_gb_r)
        
        all_results.append({
            'Category': cat_name,
            'Parameter': name,
            'Unit': unit,
            'Min_Val': f"{sub_all[col].min():.2f}",
            'Max_Val': f"{sub_all[col].max():.2f}",
            'Best_Model': best_model_g,
            'Unseen_Geom_R2': f"{best_r2_g:.4f}",
            'Unseen_Geom_MAE': f"{best_mae_g:.3f} {unit}",
            'Interpolation_R2': f"{best_r2_r:.4f}"
        })
        
        print(f"• {name} [{unit}]: Unseen Geom R2 = {best_r2_g:.4f} | MAE = {best_mae_g:.3f} {unit} | Interp R2 = {best_r2_r:.4f}")

res_df = pd.DataFrame(all_results)
os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
res_df.to_csv(OUT_CSV, index=False)
print(f"\n[SUCCESS] Audit saved to: {OUT_CSV}")
