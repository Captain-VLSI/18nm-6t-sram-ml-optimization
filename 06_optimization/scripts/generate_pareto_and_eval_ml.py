#!/usr/bin/env python3
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
DATASET_PATH = os.path.join(REPO_ROOT, "03_dataset", "sram_master_unified_dataset.csv")
OUT_DIR = os.path.join(REPO_ROOT, "08_results", "figures")
os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(DATASET_PATH)
df['cr'] = df['nfin_pd'] / df['nfin_acc']
df['pr'] = df['nfin_pu'] / df['nfin_acc']
df_12v = df[df['vdd'] == 1.2].copy()

golden_pts = [
    {"name": "Balanced (1/1/1 @ 1.2V)", "pu": 1, "pd": 1, "acc": 1, "color": "#1E40AF", "marker": "o"},
    {"name": "Low-Power (1/1/1 @ 0.9V)", "pu": 1, "pd": 1, "acc": 1, "color": "#16A34A", "marker": "s"},
    {"name": "Fast SRAM (5/2/4 @ 1.2V)", "pu": 5, "pd": 2, "acc": 4, "color": "#DC2626", "marker": "^"},
    {"name": "CR-Enhanced (2/3/2 @ 1.2V)", "pu": 2, "pd": 3, "acc": 2, "color": "#9333EA", "marker": "D"}
]

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'DejaVu Sans', 'Arial']
plt.rcParams['axes.edgecolor'] = '#334155'
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['grid.color'] = '#E2E8F0'
plt.rcParams['grid.linestyle'] = ':'
plt.rcParams['grid.alpha'] = 0.85

fig, axes = plt.subplots(1, 3, figsize=(20, 6.0), dpi=300)
fig.suptitle("18nm FinFET 6T SRAM Multi-Objective Pareto-Optimal Tradeoffs (150 Geometries @ 1.2V)",
             fontsize=14, fontweight='bold', color='#0F172A', y=0.98)

# Panel 1: RSNM vs Write Delay
ax1 = axes[0]
sc1 = ax1.scatter(df_12v['worst_write_delay_ps'], df_12v['rsnm_mv'],
                  c=df_12v['hold0_hold_leakage_current_na'], cmap='viridis_r', s=45, alpha=0.6, edgecolors='none', label='All 150 Bitcell Geometries')
cbar1 = plt.colorbar(sc1, ax=ax1)
cbar1.set_label('Hold Leakage (nA)', fontsize=9, fontweight='bold')

for g in golden_pts:
    if "@ 0.9V" in g['name']:
        row = df[(df['vdd'] == 0.9) & (df['nfin_pu'] == 1) & (df['nfin_pd'] == 1) & (df['nfin_acc'] == 1)].iloc[0]
    else:
        row = df_12v[(df_12v['nfin_pu'] == g['pu']) & (df_12v['nfin_pd'] == g['pd']) & (df_12v['nfin_acc'] == g['acc'])].iloc[0]
    ax1.scatter(row['worst_write_delay_ps'], row['rsnm_mv'], color=g['color'], s=150, marker=g['marker'],
                edgecolors='black', linewidth=1.5, zorder=5, label=g['name'])

ax1.set_title("Read Stability vs. Write Delay Tradeoff", fontsize=11, fontweight='bold', color='#0F172A')
ax1.set_xlabel("Worst Write Delay (ps)", fontsize=10, fontweight='bold')
ax1.set_ylabel("Read Static Noise Margin (RSNM) [mV]", fontsize=10, fontweight='bold')
ax1.axhline(150, color='red', linestyle='--', linewidth=1.2, alpha=0.7, label='RSNM Floor (150 mV)')
ax1.axvline(150, color='orange', linestyle='--', linewidth=1.2, alpha=0.7, label='Delay Target (150 ps)')
ax1.grid(True)
ax1.legend(loc='lower left', fontsize=8.0, frameon=True)

# Panel 2: RSNM vs Hold Leakage
ax2 = axes[1]
sc2 = ax2.scatter(df_12v['hold0_hold_leakage_current_na'], df_12v['rsnm_mv'],
                  c=df_12v['worst_write_delay_ps'], cmap='plasma_r', s=45, alpha=0.6, edgecolors='none', label='All 150 Bitcell Geometries')
cbar2 = plt.colorbar(sc2, ax=ax2)
cbar2.set_label('Write Delay (ps)', fontsize=9, fontweight='bold')

for g in golden_pts:
    if "@ 0.9V" in g['name']:
        row = df[(df['vdd'] == 0.9) & (df['nfin_pu'] == 1) & (df['nfin_pd'] == 1) & (df['nfin_acc'] == 1)].iloc[0]
    else:
        row = df_12v[(df_12v['nfin_pu'] == g['pu']) & (df_12v['nfin_pd'] == g['pd']) & (df_12v['nfin_acc'] == g['acc'])].iloc[0]
    ax2.scatter(row['hold0_hold_leakage_current_na'], row['rsnm_mv'], color=g['color'], s=150, marker=g['marker'],
                edgecolors='black', linewidth=1.5, zorder=5, label=g['name'])

ax2.set_title("Read Stability vs. Hold Leakage Tradeoff", fontsize=11, fontweight='bold', color='#0F172A')
ax2.set_xlabel("Hold Leakage Current (nA)", fontsize=10, fontweight='bold')
ax2.set_ylabel("Read Static Noise Margin (RSNM) [mV]", fontsize=10, fontweight='bold')
ax2.axhline(150, color='red', linestyle='--', linewidth=1.2, alpha=0.7)
ax2.grid(True)
ax2.legend(loc='lower right', fontsize=8.0, frameon=True)

# Panel 3: Write Delay vs Write Energy
ax3 = axes[2]
sc3 = ax3.scatter(df_12v['worst_write_energy_fj'], df_12v['worst_write_delay_ps'],
                  c=df_12v['rsnm_mv'], cmap='viridis', s=45, alpha=0.6, edgecolors='none', label='All 150 Bitcell Geometries')
cbar3 = plt.colorbar(sc3, ax=ax3)
cbar3.set_label('RSNM (mV)', fontsize=9, fontweight='bold')

for g in golden_pts:
    if "@ 0.9V" in g['name']:
        row = df[(df['vdd'] == 0.9) & (df['nfin_pu'] == 1) & (df['nfin_pd'] == 1) & (df['nfin_acc'] == 1)].iloc[0]
    else:
        row = df_12v[(df_12v['nfin_pu'] == g['pu']) & (df_12v['nfin_pd'] == g['pd']) & (df_12v['nfin_acc'] == g['acc'])].iloc[0]
    ax3.scatter(row['worst_write_energy_fj'], row['worst_write_delay_ps'], color=g['color'], s=150, marker=g['marker'],
                edgecolors='black', linewidth=1.5, zorder=5, label=g['name'])

ax3.set_title("Write Speed vs. Write Energy Tradeoff", fontsize=11, fontweight='bold', color='#0F172A')
ax3.set_xlabel("Dynamic Write Energy (fJ)", fontsize=10, fontweight='bold')
ax3.set_ylabel("Worst Write Delay (ps)", fontsize=10, fontweight='bold')
ax3.axhline(150, color='orange', linestyle='--', linewidth=1.2, alpha=0.7)
ax3.grid(True)
ax3.legend(loc='upper right', fontsize=8.0, frameon=True)

plt.tight_layout(rect=[0, 0, 1, 0.94])
pareto_out = os.path.join(OUT_DIR, "fig_pareto_front_tradeoffs.png")
plt.savefig(pareto_out)
plt.close()
print(f"[SUCCESS] Pareto plot saved to: {pareto_out}")
