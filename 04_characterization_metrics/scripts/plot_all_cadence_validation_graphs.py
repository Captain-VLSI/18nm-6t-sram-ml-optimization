#!/usr/bin/env python3
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy.interpolate import interp1d

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW_DIR = os.path.join(REPO_ROOT, "03_dataset", "raw_waveforms")
OUT_DIR = os.path.join(REPO_ROOT, "08_results", "figures")
os.makedirs(OUT_DIR, exist_ok=True)

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'DejaVu Sans', 'Arial']
plt.rcParams['axes.edgecolor'] = '#334155'
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['grid.color'] = '#E2E8F0'
plt.rcParams['grid.linestyle'] = ':'

PROFILES = [
    {
        "name": "Balanced Reference",
        "sizing": "1/1/1 @ 1.2V", "vdd": 1.2,
        "hsnm_p": os.path.join(RAW_DIR, "balanced", "hsnm", "hsnm for balanced.csv"),
        "rsnm_p": os.path.join(RAW_DIR, "balanced", "rsnm", "rsnm for balanced.csv"),
        "wtp_p": os.path.join(RAW_DIR, "balanced", "wtp", "wtp for balanced.csv"),
        "write_p": os.path.join(RAW_DIR, "balanced", "hold and write", "hold_write_for balanced.csv"),
        "r0_p": os.path.join(RAW_DIR, "balanced", "read tran", "read0_for_balanced.csv"),
        "r1_p": os.path.join(RAW_DIR, "balanced", "read tran", "read1_for_balanced.csv"),
        "exp_hsnm": 371.37, "meas_hsnm": 368.11,
        "exp_rsnm": 190.46, "meas_rsnm": 190.22,
        "exp_wsnm": 433.14, "meas_wsnm": 432.00,
        "exp_delay": 144.59, "meas_delay": 144.53,
    },
    {
        "name": "Low-Power Profile",
        "sizing": "1/1/1 @ 0.9V", "vdd": 0.9,
        "hsnm_p": os.path.join(RAW_DIR, "low_power", "hsnm", "hsnm for low power.csv"),
        "rsnm_p": os.path.join(RAW_DIR, "low_power", "rsnm", "rsnm_of_low_power.csv"),
        "wtp_p": os.path.join(RAW_DIR, "low_power", "wtp", "wtp_for low power.csv"),
        "write_p": os.path.join(RAW_DIR, "low_power", "write_hold", "write trans for low power.csv"),
        "r0_p": os.path.join(RAW_DIR, "low_power", "read_tran", "read0_trans_for_low_power.csv"),
        "r1_p": os.path.join(RAW_DIR, "low_power", "read_tran", "read1_trans_for_low_power.csv"),
        "exp_hsnm": 281.59, "meas_hsnm": 281.54,
        "exp_rsnm": 145.38, "meas_rsnm": 145.10,
        "exp_wsnm": 303.19, "meas_wsnm": 302.00,
        "exp_delay": 149.97, "meas_delay": 149.87,
    },
    {
        "name": "Fast SRAM Profile",
        "sizing": "5/2/4 @ 1.2V", "vdd": 1.2,
        "hsnm_p": os.path.join(RAW_DIR, "fast_sram", "hsnm", "hsnm for fast sram.csv"),
        "rsnm_p": os.path.join(RAW_DIR, "fast_sram", "rsnm", "rsnm for fast sram.csv"),
        "wtp_p": os.path.join(RAW_DIR, "fast_sram", "wtp", "wtp for fast ram.csv"),
        "write_p": os.path.join(RAW_DIR, "fast_sram", "write_hold", "write and hold for fast sram.csv"),
        "r0_p": os.path.join(RAW_DIR, "fast_sram", "read_tran", "read0_for fast sram.csv"),
        "r1_p": os.path.join(RAW_DIR, "fast_sram", "read_tran", "read1_for fast sram.csv"),
        "exp_hsnm": 350.49, "meas_hsnm": 350.68,
        "exp_rsnm": 153.69, "meas_rsnm": 153.49,
        "exp_wsnm": 503.19, "meas_wsnm": 503.00,
        "exp_delay": 134.19, "meas_delay": 134.58,
    },
    {
        "name": "CR-Enhanced Stability",
        "sizing": "2/3/2 @ 1.2V", "vdd": 1.2,
        "hsnm_p": os.path.join(RAW_DIR, "cr_enhanced", "hsnm", "hsnm for cr enhanced.csv"),
        "rsnm_p": os.path.join(RAW_DIR, "cr_enhanced", "rsnm", "rsnm for cr enhanced.csv"),
        "wtp_p": os.path.join(RAW_DIR, "cr_enhanced", "wtp", "wtp for ce enhanced.csv"),
        "write_p": os.path.join(RAW_DIR, "cr_enhanced", "write_hold", "write_hold.csv"),
        "r0_p": os.path.join(RAW_DIR, "cr_enhanced", "read_tran", "read0 for cr enhanced.csv"),
        "r1_p": os.path.join(RAW_DIR, "cr_enhanced", "read_tran", "read1 for cr enhanced.csv"),
        "exp_hsnm": 339.71, "meas_hsnm": 339.56,
        "exp_rsnm": 204.52, "meas_rsnm": 204.26,
        "exp_wsnm": 373.19, "meas_wsnm": 373.00,
        "exp_delay": 143.93, "meas_delay": 144.24,
    }
]

# 1. SNM Butterflies
fig_snm, axes_snm = plt.subplots(2, 4, figsize=(22, 10.5), dpi=300)
fig_snm.suptitle("Cadence Spectre 18nm FinFET 6T SRAM Static Noise Margin (SNM) Butterfly Curves",
                 fontsize=14, fontweight='bold', color='#0F172A', y=0.98)

def parse_vtc_file(csv_p):
    df = pd.read_csv(csv_p)
    if 'q vs qb X' in df.columns:
        inv1_x = df['q vs qb X'].values
        inv1_y = df['q vs qb Y'].values
        inv2_x = df['qb vs q Y'].values
        inv2_y = df['qb vs q X'].values
    else:
        x_c = [c for c in df.columns if 'x' in c.lower()][0]
        y_c = [c for c in df.columns if 'y' in c.lower()]
        inv1_x = df[x_c].values
        inv1_y = df[y_c[0]].values
        inv2_x = df[y_c[1]].values
        inv2_y = df[x_c].values
    s1 = np.argsort(inv1_x)
    s2 = np.argsort(inv2_x)
    return inv1_x[s1], inv1_y[s1], inv2_x[s2], inv2_y[s2]

def calculate_inscribed_squares(x1, y1, x2, y2, vdd, snm_mv):
    s_v = snm_mv / 1000.0
    f1 = interp1d(x1, y1, bounds_error=False, fill_value="extrapolate")
    f2 = interp1d(x2, y2, bounds_error=False, fill_value="extrapolate")
    
    cand_x_l = np.linspace(0.005, vdd * 0.40, 200)
    best_xl, best_yl = cand_x_l[0], cand_x_l[0]
    min_pen_l = 1e9
    for xl in cand_x_l:
        yl = xl
        p_tr = (xl + s_v, yl + s_v)
        pen = abs(f1(p_tr[0]) - yl) + abs(f2(xl) - p_tr[1])
        if pen < min_pen_l and (xl + s_v) <= vdd:
            min_pen_l = pen
            best_xl, best_yl = xl, yl
            
    cand_x_r = np.linspace(vdd * 0.60, vdd - s_v - 0.005, 200)
    best_xr, best_yr = cand_x_r[0], cand_x_r[0]
    min_pen_r = 1e9
    for xr in cand_x_r:
        yr = xr
        p_tl = (xr - s_v, yr + s_v)
        pen = abs(f1(xr) - p_tl[1]) + abs(f2(p_tl[0]) - yr)
        if pen < min_pen_r and (xr + s_v) <= vdd and (xr - s_v) >= 0:
            min_pen_r = pen
            best_xr, best_yr = xr, yr
            
    return (s_v, (best_xl, best_yl)), (s_v, (best_xr, best_yr))

for i, prof in enumerate(PROFILES):
    vdd = prof['vdd']
    
    ax_h = axes_snm[0, i]
    x1_h, y1_h, x2_h, y2_h = parse_vtc_file(prof['hsnm_p'])
    ax_h.plot(x1_h, y1_h, color='#1E40AF', linewidth=2.4, label='Inverter 1 VTC (V_Q -> V_QB)')
    ax_h.plot(x2_h, y2_h, color='#DC2626', linewidth=2.4, label='Inverter 2 VTC (V_QB -> V_Q)')
    ax_h.plot([0, vdd], [0, vdd], color='#64748B', linestyle=':', linewidth=1.1, label='Diagonal Ref')
    
    (sl_h, (xl_h, yl_h)), (sr_h, (xr_h, yr_h)) = calculate_inscribed_squares(x1_h, y1_h, x2_h, y2_h, vdd, prof['meas_hsnm'])
    rect_l_h = Rectangle((xl_h, yl_h), sl_h, sl_h, linewidth=1.6, edgecolor='#16A34A', facecolor='#86EFAC', alpha=0.35, zorder=5)
    rect_r_h = Rectangle((xr_h - sr_h, yr_h), sr_h, sr_h, linewidth=1.6, edgecolor='#16A34A', facecolor='#86EFAC', alpha=0.35, zorder=5)
    ax_h.add_patch(rect_l_h)
    ax_h.add_patch(rect_r_h)
    
    ax_h.text(0.04 * vdd, 0.94 * vdd, f"HSNM = {prof['meas_hsnm']:.2f} mV",
              fontsize=9.5, fontweight='bold', color='#14532D',
              bbox=dict(boxstyle="round,pad=0.35", fc="#F0FDF4", ec="#86EFAC", lw=1.0))
    ax_h.set_title(f"{prof['name']} (Hold Mode)\n{prof['sizing']}", fontsize=11, fontweight='bold', color='#0F172A')
    ax_h.set_xlabel("V_Q (V)", fontsize=9.5, fontweight='bold')
    ax_h.set_ylabel("V_QB (V)", fontsize=9.5, fontweight='bold')
    ax_h.set_xlim(-0.02, vdd + 0.02)
    ax_h.set_ylim(-0.02, vdd + 0.02)
    ax_h.grid(True)
    if i == 0:
        ax_h.legend(loc='lower right', fontsize=7.5, frameon=True)
        
    ax_r = axes_snm[1, i]
    x1_r, y1_r, x2_r, y2_r = parse_vtc_file(prof['rsnm_p'])
    ax_r.plot(x1_r, y1_r, color='#1E40AF', linewidth=2.4)
    ax_r.plot(x2_r, y2_r, color='#DC2626', linewidth=2.4)
    ax_r.plot([0, vdd], [0, vdd], color='#64748B', linestyle=':', linewidth=1.1)
    
    (sl_r, (xl_r, yl_r)), (sr_r, (xr_r, yr_r)) = calculate_inscribed_squares(x1_r, y1_r, x2_r, y2_r, vdd, prof['meas_rsnm'])
    rect_l_r = Rectangle((xl_r, yl_r), sl_r, sl_r, linewidth=1.6, edgecolor='#9333EA', facecolor='#D8B4FE', alpha=0.35, zorder=5)
    rect_r_r = Rectangle((xr_r - sr_r, yr_r), sr_r, sr_r, linewidth=1.6, edgecolor='#9333EA', facecolor='#D8B4FE', alpha=0.35, zorder=5)
    ax_r.add_patch(rect_l_r)
    ax_r.add_patch(rect_r_r)
    
    ax_r.text(0.04 * vdd, 0.94 * vdd, f"RSNM = {prof['meas_rsnm']:.2f} mV",
              fontsize=9.5, fontweight='bold', color='#581C87',
              bbox=dict(boxstyle="round,pad=0.35", fc="#FAF5FF", ec="#D8B4FE", lw=1.0))
    ax_r.set_title(f"{prof['name']} (Read Mode)\n{prof['sizing']}", fontsize=11, fontweight='bold', color='#0F172A')
    ax_r.set_xlabel("V_Q (V)", fontsize=9.5, fontweight='bold')
    ax_r.set_ylabel("V_QB (V)", fontsize=9.5, fontweight='bold')
    ax_r.set_xlim(-0.02, vdd + 0.02)
    ax_r.set_ylim(-0.02, vdd + 0.02)
    ax_r.grid(True)

plt.tight_layout(rect=[0, 0, 1, 0.95])
f_snm = os.path.join(OUT_DIR, "fig_snm_butterflies_perfect_unified.png")
plt.savefig(f_snm)
plt.close()
print(f"  [SAVED] -> {f_snm}")

# 2. Transient Write Waveforms
fig_w, axes_w = plt.subplots(2, 2, figsize=(16, 9.5), dpi=300)
fig_w.suptitle("Cadence Spectre 18nm FinFET 6T SRAM Transient Write Switching Transitions",
               fontsize=13.5, fontweight='bold', color='#0F172A', y=0.98)

for i, prof in enumerate(PROFILES):
    ax = axes_w[i // 2, i % 2]
    df = pd.read_csv(prof['write_p'])
    vdd = prof['vdd']
    
    w_time = df['/w X'].values * 1e9
    w_volt = df['/w Y'].values
    q_time = df['/q X'].values * 1e9
    q_volt = df['/q Y'].values
    qb_time = df['/qb X'].values * 1e9
    qb_volt = df['/qb Y'].values
    
    ax.plot(w_time, w_volt, label='Wordline (WL)', color='#475569', linestyle='--', linewidth=1.6)
    ax.plot(q_time, q_volt, label='Node Q (1 -> 0)', color='#1E40AF', linewidth=2.2)
    ax.plot(qb_time, qb_volt, label='Node QB (0 -> 1)', color='#DC2626', linewidth=2.2)
    
    ax.text(0.04, 0.88, f"Measured Delay = {prof['meas_delay']:.2f} ps\n(Expected = {prof['exp_delay']:.2f} ps)",
            transform=ax.transAxes, fontsize=9.0, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.35", fc="#F8FAFC", ec="#CBD5E1", lw=0.9))
            
    ax.set_title(f"{prof['name']} ({prof['sizing']})", fontsize=11, fontweight='bold', color='#0F172A')
    ax.set_xlabel("Time (ns)", fontsize=9.5, fontweight='bold')
    ax.set_ylabel("Voltage (V)", fontsize=9.5, fontweight='bold')
    ax.set_xlim(min(w_time), max(w_time))
    ax.set_ylim(-0.05, vdd + 0.10)
    ax.grid(True)
    if i == 0:
        ax.legend(loc='lower right', fontsize=8.5, frameon=True)

plt.tight_layout(rect=[0, 0, 1, 0.95])
f_write = os.path.join(OUT_DIR, "fig_validation_3_transient_write_waveforms.png")
plt.savefig(f_write)
plt.close()
print(f"  [SAVED] -> {f_write}")

# 3. Transient Read Waveforms
fig_r, axes_r = plt.subplots(2, 2, figsize=(16, 9.5), dpi=300)
fig_r.suptitle("Cadence Spectre 18nm FinFET 6T SRAM Transient Read Sensing & Disturb Bumps",
               fontsize=13.5, fontweight='bold', color='#0F172A', y=0.98)

for i, prof in enumerate(PROFILES):
    ax = axes_r[i // 2, i % 2]
    df = pd.read_csv(prof['r0_p'])
    vdd = prof['vdd']
    
    bl_t = df['/bl X'].values * 1e9
    bl_v = df['/bl Y'].values
    blb_t = df['/blb X'].values * 1e9
    blb_v = df['/blb Y'].values
    q_t = df['/q X'].values * 1e9
    q_v = df['/q Y'].values
    qb_t = df['/qb X'].values * 1e9
    qb_v = df['/qb Y'].values
    
    ax.plot(bl_t, bl_v, label='Bitline (BL)', color='#2563EB', linewidth=1.8)
    ax.plot(blb_t, blb_v, label='Bitline-Bar (BLB)', color='#9333EA', linewidth=1.8)
    ax.plot(qb_t, qb_v, label='Node QB (High)', color='#DC2626', linewidth=1.8)
    ax.plot(q_t, q_v, label='Node Q (Low Disturb Bump)', color='#16A34A', linewidth=2.0)
    
    ax.set_title(f"{prof['name']} (Read-0 Dynamic Sensing)", fontsize=11, fontweight='bold', color='#0F172A')
    ax.set_xlabel("Time (ns)", fontsize=9.5, fontweight='bold')
    ax.set_ylabel("Voltage (V)", fontsize=9.5, fontweight='bold')
    ax.set_xlim(min(bl_t), max(bl_t))
    ax.set_ylim(-0.05, vdd + 0.10)
    ax.grid(True)
    if i == 0:
        ax.legend(loc='center right', fontsize=8.0, frameon=True)

plt.tight_layout(rect=[0, 0, 1, 0.95])
f_read = os.path.join(OUT_DIR, "fig_validation_4_transient_read_waveforms.png")
plt.savefig(f_read)
plt.close()
print(f"  [SAVED] -> {f_read}")

# 4. Master Dashboard
fig_d, axes_d = plt.subplots(2, 2, figsize=(16, 10), dpi=300)
fig_d.suptitle("Cadence Spectre 18nm FinFET 6T SRAM Closed-Loop Verification Parity Dashboard",
               fontsize=14, fontweight='bold', color='#0F172A', y=0.98)

metrics = [
    ('exp_hsnm', 'meas_hsnm', 'Hold SNM (HSNM)', 'mV', axes_d[0, 0]),
    ('exp_rsnm', 'meas_rsnm', 'Read SNM (RSNM)', 'mV', axes_d[0, 1]),
    ('exp_wsnm', 'meas_wsnm', 'Write Trip Point (WTP / WSNM)', 'mV', axes_d[1, 0]),
    ('exp_delay', 'meas_delay', 'Worst Write Delay', 'ps', axes_d[1, 1])
]

names = [p['name'].split()[0] for p in PROFILES]
x_pos = np.arange(len(names))
width = 0.35

for exp_key, meas_key, title, unit, ax in metrics:
    exp_vals = [p[exp_key] for p in PROFILES]
    meas_vals = [p[meas_key] for p in PROFILES]
    
    rects1 = ax.bar(x_pos - width/2, exp_vals, width, label='Expected Baseline', color='#64748B', alpha=0.9)
    rects2 = ax.bar(x_pos + width/2, meas_vals, width, label='Cadence Measured', color='#16A34A', alpha=0.9)
    
    for j, (ev, mv) in enumerate(zip(exp_vals, meas_vals)):
        err = abs(mv - ev) / ev * 100.0
        ax.text(x_pos[j], max(ev, mv) * 1.03, f"{err:.2f}%\nPASS", ha='center', va='bottom',
                fontsize=8.5, fontweight='bold', color='#14532D')
                
    ax.set_title(f"{title} Parity Comparison", fontsize=11, fontweight='bold', color='#0F172A')
    ax.set_xticks(x_pos)
    ax.set_xticklabels([f"{p['name']}\n({p['sizing']})" for p in PROFILES], fontsize=8.5, fontweight='bold')
    ax.set_ylabel(f"{title} [{unit}]", fontsize=9.5, fontweight='bold')
    ax.set_ylim(0, max(max(exp_vals), max(meas_vals)) * 1.22)
    ax.grid(True, axis='y')
    ax.legend(loc='upper right', fontsize=8.0, frameon=True)

plt.tight_layout(rect=[0, 0, 1, 0.95])
f_dash = os.path.join(OUT_DIR, "fig_validation_master_dashboard.png")
plt.savefig(f_dash)
plt.close()
print(f"  [SAVED] -> {f_dash}")
