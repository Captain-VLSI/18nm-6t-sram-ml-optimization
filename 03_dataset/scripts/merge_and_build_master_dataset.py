import os
import csv
from collections import defaultdict

DATA_DIR = r"c:\VS CODE C PROGRAM\SRAM\New dataset"
OUTPUT_MASTER_CSV = os.path.join(DATA_DIR, "sram_master_unified_dataset.csv")

print("=" * 80)
print("BUILDING 1,200-ROW MASTER UNIFIED SRAM DATASET")
print("=" * 80)

# Master key: (pu_fins, pd_fins, acc_fins, vdd_val, temp_val)
master_dict = defaultdict(dict)

# 1. Load Static SNM Dataset (1,200 rows)
snm_file = os.path.join(DATA_DIR, "sram_snm_dataset.csv")
with open(snm_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        key = (int(r['nfin_pu']), int(r['nfin_pd']), int(r['nfin_acc']), float(r['vdd']), int(float(r['temp'])))
        master_dict[key]['hsnm_mv'] = float(r['hsnm_mv'])
        master_dict[key]['rsnm_mv'] = float(r['rsnm_mv'])
        master_dict[key]['wsnm_mv'] = float(r['wsnm_mv'])

print(f"[1] Static SNM loaded: {len(master_dict)} base parameter keys.")

# 2. Load and Pivot Read Dataset (2,400 rows: READ_0 and READ_1)
read_file = os.path.join(DATA_DIR, "sram_bitcell_read_tran_dataset.csv")
with open(read_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        key = (int(r['pu_fins']), int(r['pd_fins']), int(r['acc_fins']), float(r['vdd_val']), int(float(r['temp_val'])))
        rtype = r['read_type'] # 'read_0' or 'read_1'
        prefix = "r0_" if rtype == 'read_0' else "r1_"
        
        master_dict[key][prefix + 'max_q_disturb_mv'] = float(r['max_q_disturb_mv'])
        master_dict[key][prefix + 'max_qb_disturb_mv'] = float(r['max_qb_disturb_mv'])
        master_dict[key][prefix + 'q_drop_mv'] = float(r['q_drop_mv'])
        master_dict[key][prefix + 'wl_to_q_disturb_peak_ps'] = float(r['wl_to_q_disturb_peak_ps'])
        master_dict[key][prefix + 'wl_to_qb_disturb_peak_ps'] = float(r['wl_to_qb_disturb_peak_ps'])
        master_dict[key][prefix + 'avg_current_ua'] = float(r['average_read_current_ua'])
        master_dict[key][prefix + 'peak_current_ua'] = float(r['peak_read_current_ua'])
        master_dict[key][prefix + 'power_uw'] = float(r['read_power_uw'])
        master_dict[key][prefix + 'energy_fj'] = float(r['read_energy_fj'])
        master_dict[key][prefix + 'success'] = int(float(r['read_success']))

print(f"[2] Read Dataset pivoted: {len(master_dict)} keys updated.")

# 3. Load and Pivot Write Dataset (2,400 rows: WRITE_0 and WRITE_1)
write_file = os.path.join(DATA_DIR, "sram_bitcell_write_tran_dataset_clean.csv")
if not os.path.exists(write_file):
    write_file = os.path.join(DATA_DIR, "sram_bitcell_write_tran_dataset.csv")

with open(write_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        key = (int(r['pu_fins']), int(r['pd_fins']), int(r['acc_fins']), float(r['vdd_val']), int(float(r['temp_val'])))
        wtype = r['write_type'] # 'write_0' or 'write_1'
        prefix = "w0_" if wtype == 'write_0' else "w1_"
        
        master_dict[key][prefix + 'delay_ps'] = float(r['write_delay_ps'])
        master_dict[key][prefix + 'q_disturb_mv'] = float(r['max_q_disturb_mv'])
        master_dict[key][prefix + 'qb_disturb_mv'] = float(r['max_qb_disturb_mv'])
        master_dict[key][prefix + 'avg_current_ua'] = float(r['average_write_current_ua'])
        master_dict[key][prefix + 'peak_current_ua'] = float(r['peak_write_current_ua'])
        master_dict[key][prefix + 'power_uw'] = float(r['write_power_uw'])
        master_dict[key][prefix + 'energy_fj'] = float(r['write_energy_fj'])
        master_dict[key][prefix + 'success'] = int(float(r['write_success']))

print(f"[3] Write Dataset pivoted: {len(master_dict)} keys updated.")

# 4. Load and Pivot Hold Dataset (2,400 rows: HOLD_0 and HOLD_1)
hold_file = os.path.join(DATA_DIR, "sram_bitcell_hold_tran_dataset.csv")
with open(hold_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        key = (int(r['pu_fins']), int(r['pd_fins']), int(r['acc_fins']), float(r['vdd_val']), int(float(r['temp_val'])))
        htype = r['hold_type'] # 'hold_0' or 'hold_1'
        prefix = "h0_" if htype == 'hold_0' else "h1_"
        
        master_dict[key][prefix + 'q_drop_mv'] = float(r['hold_q_drop_mv'])
        master_dict[key][prefix + 'qb_disturb_mv'] = float(r['hold_qb_disturb_mv'])
        master_dict[key][prefix + 'leakage_current_na'] = float(r['hold_leakage_current_na'])
        master_dict[key][prefix + 'power_uw'] = float(r['hold_power_uw'])
        master_dict[key][prefix + 'energy_fj'] = float(r['hold_energy_fj'])
        master_dict[key][prefix + 'success'] = int(float(r['hold_success']))

print(f"[4] Hold Dataset pivoted: {len(master_dict)} keys updated.")

# 5. Composite Metrics & Functional Feasibility Label
master_rows = []
for key in sorted(master_dict.keys()):
    pu, pd_fin, acc, vdd, temp = key
    d = master_dict[key]
    
    # Worst-case / aggregated metrics
    # Write delay = max of w0 and w1 delays (if both > 0, else -1 sentinel)
    w0_d = d.get('w0_delay_ps', -1.0)
    w1_d = d.get('w1_delay_ps', -1.0)
    if w0_d > 0 and w1_d > 0:
        worst_write_delay_ps = max(w0_d, w1_d)
    else:
        worst_write_delay_ps = -1.0 # sentinel failure
        
    avg_hold_leakage_na = (d.get('h0_leakage_current_na', 0.0) + d.get('h1_leakage_current_na', 0.0)) / 2.0
    avg_hold_power_uw = (d.get('h0_power_uw', 0.0) + d.get('h1_power_uw', 0.0)) / 2.0
    avg_write_energy_fj = (d.get('w0_energy_fj', 0.0) + d.get('w1_energy_fj', 0.0)) / 2.0
    worst_read_disturb_mv = max(d.get('r0_max_q_disturb_mv', 0.0), d.get('r1_max_qb_disturb_mv', 0.0))
    
    # Feasibility Criteria:
    # 1. RSNM > 0.0 mV (open butterfly lobe)
    # 2. HSNM > 0.0 mV
    # 3. WSNM > 0.0 mV (not -1.0 failure sentinel)
    # 4. Write success = 1 for both w0 and w1
    # 5. Read success = 1 for both r0 and r1
    # 6. Hold success = 1 for both h0 and h1
    is_feasible = (
        d.get('rsnm_mv', 0.0) > 0.0 and
        d.get('hsnm_mv', 0.0) > 0.0 and
        d.get('wsnm_mv', 0.0) > 0.0 and
        d.get('w0_success', 0) == 1 and
        d.get('w1_success', 0) == 1 and
        d.get('r0_success', 0) == 1 and
        d.get('r1_success', 0) == 1 and
        d.get('h0_success', 0) == 1 and
        d.get('h1_success', 0) == 1 and
        worst_write_delay_ps > 0.0
    )
    feasible_label = 1 if is_feasible else 0

    row = {
        'pu_fins': pu,
        'pd_fins': pd_fin,
        'acc_fins': acc,
        'vdd_val': vdd,
        'temp_val': temp,
        'is_feasible': feasible_label,
        'worst_write_delay_ps': round(worst_write_delay_ps, 4),
        'avg_hold_leakage_na': round(avg_hold_leakage_na, 6),
        'avg_hold_power_uw': round(avg_hold_power_uw, 6),
        'avg_write_energy_fj': round(avg_write_energy_fj, 6),
        'worst_read_disturb_mv': round(worst_read_disturb_mv, 4),
        **d
    }
    master_rows.append(row)

# Fieldnames
fieldnames = list(master_rows[0].keys())

with open(OUTPUT_MASTER_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(master_rows)

print(f"\n[SUCCESS] Master Unified Dataset created at: {OUTPUT_MASTER_CSV}")
print(f"Total Unified Rows: {len(master_rows)}")
print(f"Total Columns: {len(fieldnames)}")
feasible_count = sum(1 for r in master_rows if r['is_feasible'] == 1)
print(f"Feasible Operating Points: {feasible_count} / {len(master_rows)} ({feasible_count/len(master_rows)*100:.2f}%)")
print(f"Infeasible / Extreme Corner Failures: {len(master_rows) - feasible_count} / {len(master_rows)}")
