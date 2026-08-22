#!/usr/bin/env python3
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
RAW_DIR = os.path.join(REPO_ROOT, "03_dataset", "raw_waveforms")
OUT_DIR = os.path.join(REPO_ROOT, "08_results", "figures")
os.makedirs(OUT_DIR, exist_ok=True)

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'DejaVu Sans', 'Arial']
plt.rcParams['axes.edgecolor'] = '#475569'
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['grid.color'] = '#E2E8F0'
plt.rcParams['grid.linestyle'] = ':'
plt.rcParams['grid.alpha'] = 0.85

PROFILES = [
    {
        "name": "Balanced Reference",
        "sizing": "PU=1, PD=1, ACC=1",
        "vdd": 1.2, "pr": 1.00, "cr": 1.00,
        "wtp_p": os.path.join(RAW_DIR, "balanced", "wtp", "wtp for balanced.csv"),
    },
    {
        "name": "Low-Power Profile",
        "sizing": "PU=1, PD=1, ACC=1",
        "vdd": 0.9, "pr": 1.00, "cr": 1.00,
        "wtp_p": os.path.join(RAW_DIR, "low_power", "wtp", "wtp_for low power.csv"),
    },
    {
        "name": "Fast SRAM Profile",
        "sizing": "PU=5, PD=2, ACC=4",
        "vdd": 1.2, "pr": 1.25, "cr": 0.50,
        "wtp_p": os.path.join(RAW_DIR, "fast_sram", "wtp", "wtp for fast ram.csv"),
    },
    {
        "name": "CR-Enhanced Stability",
        "sizing": "PU=2, PD=3, ACC=2",
        "vdd": 1.2, "pr": 1.00, "cr": 1.50,
        "wtp_p": os.path.join(RAW_DIR, "cr_enhanced", "wtp", "wtp for ce enhanced.csv"),
    }
]

def render_premium_subplot(ax, prof, legend_on=False):
    df_wtp = pd.read_csv(prof['wtp_p'])
    
    bl_col = [c for c in df_wtp.columns if ('bl' in c.lower()) and ('y' in c.lower())][0]
    q_col = [c for c in df_wtp.columns if c.endswith('q Y') or c == '/q Y'][0]
    qb_col = [c for c in df_wtp.columns if c.endswith('qb Y') or c == '/qb Y'][0]
    
    df_sorted = df_wtp.sort_values(by=bl_col)
    bl_v = df_sorted[bl_col].values
    q_v = df_sorted[q_col].values
    qb_v = df_sorted[qb_col].values
    vdd = prof['vdd']
    
    dq_dbl = np.abs(np.gradient(q_v, bl_v))
    max_idx = np.argmax(dq_dbl)
    v_trip = bl_v[max_idx]
    v_qb_peak = np.max(qb_v[max_idx:])
    
    wtp_mv = v_trip * 1000.0
    wnm_mv = (v_qb_peak - v_trip) * 1000.0
    
    ax.axvspan(v_trip, v_trip + 0.08 * vdd, color='#FEF3C7', alpha=0.35, zorder=1)
    ax.plot([0, vdd], [0, vdd], color='#334155', linewidth=1.4, linestyle='-', label='Bitline Ref (V_BL)', zorder=2)
    ax.plot(bl_v, q_v, color='#0284C7', linewidth=2.4, label='Node Q (Inverting 1 -> 0)', zorder=3)
    ax.plot(bl_v, qb_v, color='#E11D48', linewidth=2.4, label='Node QB (Inverting 0 -> 1)', zorder=3)
    ax.axvline(v_trip, color='#16A34A', linestyle='--', linewidth=1.5, alpha=0.9, zorder=2)
    
    ax.scatter([v_trip], [v_trip], color='#86EFAC', s=160, zorder=4, alpha=0.6)
    ax.scatter([v_trip], [v_trip], color='#16A34A', s=60, zorder=5, edgecolors='#065F46', linewidth=1.2)
    
    arrow_x = v_trip + 0.04 * vdd
    ax.annotate('', xy=(arrow_x, v_qb_peak), xytext=(arrow_x, arrow_x),
                arrowprops=dict(arrowstyle='<|-|>', color='#0F172A', lw=1.8, mutation_scale=11), zorder=5)
    
    ax.text(arrow_x + 0.02 * vdd, (arrow_x + v_qb_peak) / 2.0, f"WNM\n{wnm_mv:.1f} mV",
            fontsize=8.5, fontweight='bold', va='center', color='#0F172A',
            bbox=dict(boxstyle="round,pad=0.25", fc="#FFFFFF", ec="#CBD5E1", lw=0.8, alpha=0.95), zorder=6)
    
    ax.annotate(f"Write-Trip Point\nV_trip = {v_trip:.3f} V\n(WTP = {wtp_mv:.1f} mV)",
                xy=(v_trip, v_trip), xytext=(v_trip + 0.13 * vdd, vdd * 0.72),
                arrowprops=dict(facecolor='#16A34A', edgecolor='#16A34A', shrink=0.08, width=1.2, headwidth=5),
                bbox=dict(boxstyle="round,pad=0.4", fc="#F0FDF4", ec="#86EFAC", lw=1.0),
                fontsize=8.5, fontweight='bold', color='#14532D', zorder=6)
                
    ax.text(0.04 * vdd, 0.94 * vdd, f"{prof['sizing']}\nPR = {prof['pr']:.2f} | CR = {prof['cr']:.2f}",
            fontsize=8.5, fontweight='bold', va='top', color='#334155',
            bbox=dict(boxstyle="round,pad=0.35", fc="#F8FAFC", ec="#E2E8F0", lw=0.9), zorder=6)
            
    ax.set_title(f"{prof['name']}\nWTP = {wtp_mv:.1f} mV  |  WNM = {wnm_mv:.1f} mV",
                 fontsize=10.5, fontweight='bold', color='#0F172A', pad=8)
    ax.set_xlabel("Write Bitline Voltage V_BL (V)", fontsize=9.5, fontweight='bold', color='#334155')
    ax.set_ylabel("Internal Node Voltage (V)", fontsize=9.5, fontweight='bold', color='#334155')
    
    ax.set_xlim(-0.02, vdd + 0.02)
    ax.set_ylim(-0.02, vdd + 0.04)
    ax.grid(True)
    if legend_on:
        ax.legend(loc='lower left', fontsize=8.0, frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1')

fig, axes = plt.subplots(1, 4, figsize=(22, 6.0), dpi=300)
fig.suptitle("Cadence Spectre 18nm FinFET 6T SRAM Write Trip Point (WTP) & Write Noise Margin (WNM)",
             fontsize=14, fontweight='bold', color='#0F172A', y=0.98)

for i, prof in enumerate(PROFILES):
    render_premium_subplot(axes[i], prof, legend_on=(i == 0))

plt.tight_layout(rect=[0, 0, 1, 0.94])
f_4panel = os.path.join(OUT_DIR, "fig_wtp_wnm_premium_4panel.png")
plt.savefig(f_4panel)
plt.close()
print(f"  [SAVED] -> {f_4panel}")

fig_s, ax_s = plt.subplots(figsize=(7.0, 5.8), dpi=300)
fig_s.suptitle("6T SRAM Bitcell Write-Trip Point & Write Noise Margin Characterization",
               fontsize=12.5, fontweight='bold', color='#0F172A', y=0.98)
render_premium_subplot(ax_s, PROFILES[0], legend_on=True)
plt.tight_layout(rect=[0, 0, 1, 0.95])
f_single = os.path.join(OUT_DIR, "fig_wtp_wnm_premium_single.png")
plt.savefig(f_single)
plt.close()
print(f"  [SAVED] -> {f_single}")
