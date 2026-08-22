#!/usr/bin/env python3
"""
========================================================================================
  STANDALONE 6T SRAM BITCELL WRITE (WRITE-0 & WRITE-1) TRANSIENT CHARACTERIZATION SCRIPT
========================================================================================
  Technology: Cadence Virtuoso + Spectre (FinFET cds_ff_mpt 7nm PDK)
  Scope     : Standalone 6T SRAM Bitcell Write-0 (Q->0, QB->VDD) and Write-1 (Q->VDD, QB->0)
  Target    : AI-Assisted SRAM Bitcell Multi-Objective Optimization
  Design Space: 150 Unique Fin Configurations (5 PU x 6 PD x 5 ACC)

  **FIX APPLIED**: Two INDEPENDENT Spectre run() calls per corner with explicit ic():
    - Run 1: ic(Q=0, QB=VDD) -> Write-1 measures genuine Q: 0->VDD transition
    - Run 2: ic(Q=VDD, QB=0) -> Write-0 measures genuine Q: VDD->0 transition
  This eliminates the delay=-1 / success=1 contradiction caused by missing ic().

  FEATURE: AUTO-RESUME CHECKPOINTING (Safe to interrupt & restart anytime!)
  Usage  : python3 generate_standalone_sram_write_dataset.py          (auto-resumes)
           python3 generate_standalone_sram_write_dataset.py --fresh  (delete old data & restart)

  Datasets Exported:
    1. sram_bitcell_write_0_tran_dataset.csv (1200 Write-0 rows)
    2. sram_bitcell_write_1_tran_dataset.csv (1200 Write-1 rows)
    3. sram_bitcell_write_tran_dataset.csv   (2400 Combined Write rows)
========================================================================================
"""

import os
import sys
import subprocess
import itertools
import pandas as pd

# Prevent UnicodeEncodeError on Linux terminals with non-UTF-8 locales
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# ==============================================================================
# 1. ENVIRONMENT & PATH DEFINITIONS (COPIED FROM WORKING SCRIPT)
# ==============================================================================
CSH_SETUP = "source /home/install/cshrc"

OCEAN_EXEC = "ocean"
possible_ocean_paths = [
    "/home/install/IC618/tools/dfII/bin/ocean",
    "/home/install/IC618/bin/ocean",
    "/home/install/IC618/tools/bin/ocean"
]
for path in possible_ocean_paths:
    if os.path.exists(path):
        OCEAN_EXEC = path
        break

print(f"[INFO] Using Cadence setup: {CSH_SETUP}")
print(f"[INFO] Using OCEAN binary path: {OCEAN_EXEC}")

# Absolute netlist paths on Linux Lab PC (COPIED FROM WORKING SCRIPT)
NETLIST_WRITE_HOLD = "/home/vlsi-lab/simulation/6tsram_w_tb/spectre/schematic/netlist/netlist"
WORK_DIR_WRITE_HOLD = "/home/vlsi-lab/simulation/6tsram_w_tb"

MODEL_PATH = "/home/install/FOUNDRY/cds_ff_mpt_v_0.5/cds_ff_mpt/../models/spectre/cds_ff_mpt.scs"

# Output Dataset CSV File Names
CSV_WRITE_0 = "sram_bitcell_write_0_tran_dataset.csv"
CSV_WRITE_1 = "sram_bitcell_write_1_tran_dataset.csv"
CSV_WRITE_COMBINED = "sram_bitcell_write_tran_dataset.csv"

TEMP_OCN = "run_temp_standalone.ocn"
LOG_OCN = f"ocean_write_{os.getpid()}.log"
RESULTS_TXT_ABS = "/home/vlsi-lab/Ganesh_Mtech/Mtech_project_ganesh/meas_standalone_temp.txt"

# Clean up any stale OCEAN log/lock files from previous runs
import glob
for stale in glob.glob("ocean_standalone.log*") + glob.glob("ocean_write_*.log*"):
    try:
        os.remove(stale)
    except:
        pass

# ==============================================================================
# 2. NETLIST PARAMETERIZATION (COPIED FROM WORKING SCRIPT)
# ==============================================================================
def parameterize_netlist(netlist_path):
    if not os.path.exists(netlist_path):
        print(f"[ERROR] Netlist not found at: {netlist_path}")
        return False
        
    bak = netlist_path + ".bak"
    if not os.path.exists(bak):
        subprocess.run(f"cp {netlist_path} {bak}", shell=True)
    else:
        subprocess.run(f"cp {bak} {netlist_path}", shell=True)

    cmds = [
        f"sed -i '/^include /d' {netlist_path}",
        f"sed -i '1a include \"{MODEL_PATH}\" section=tt' {netlist_path}",
        # Parameterize transistor fin counts
        f"sed -i 's/\\(NM0.*nfin=\\)[0-9][0-9]*/\\1nfin_pd/' {netlist_path}",
        f"sed -i 's/\\(NM1.*nfin=\\)[0-9][0-9]*/\\1nfin_pd/' {netlist_path}",
        f"sed -i 's/\\(NM2.*nfin=\\)[0-9][0-9]*/\\1nfin_acc/' {netlist_path}",
        f"sed -i 's/\\(NM3.*nfin=\\)[0-9][0-9]*/\\1nfin_acc/' {netlist_path}",
        f"sed -i 's/\\(PM0.*nfin=\\)[0-9][0-9]*/\\1nfin_pu/' {netlist_path}",
        f"sed -i 's/\\(PM1.*nfin=\\)[0-9][0-9]*/\\1nfin_pu/' {netlist_path}",
        # Parameterize voltage sources (COPIED FROM WORKING SCRIPT)
        f"sed -i 's/\\(V0 (net6 0).*dc=\\)[0-9][0-9.]*m*/\\1vdd_val/' {netlist_path}",
        f"sed -i 's/\\(V3 (net1 0).*dc=\\)[0-9][0-9.]*m*/\\1vdd_val/' {netlist_path}",
        f"sed -i 's/\\(V3 (net6 0).*dc=\\)[0-9][0-9.]*m*/\\1vdd_val/' {netlist_path}",
        f"sed -i 's/\\(V1 (bl 0).*dc=\\)[0-9][0-9.]*m*/\\1vdd_val/' {netlist_path}",
        f"sed -i 's/\\(V2 (blb 0).*dc=\\)[0-9][0-9.]*m*/\\1vdd_val/' {netlist_path}",
        f"sed -i 's/\\(V5 (w 0).*val1=\\)[0-9][0-9.]*m*/\\1vdd_val/' {netlist_path}",
        f"sed -i 's/\\(V0 (w 0).*val1=\\)[0-9][0-9.]*m*/\\1vdd_val/' {netlist_path}",
        f"sed -i 's/\\(V1 (bl 0).*val1=\\)[0-9][0-9.]*m*/\\1vdd_val/' {netlist_path}",
        f"sed -i 's/\\(V2 (blb 0).*val0=\\)[0-9][0-9.]*m*/\\1vdd_val/' {netlist_path}",
        # Parameterize initial condition
        f"sed -i 's/ic qb=0 q=[0-9][0-9.]*m*/ic qb=0 q=vdd_val/' {netlist_path}"
    ]
        
    for cmd in cmds:
        subprocess.run(cmd, shell=True)
    return True

print("[INFO] Parameterizing Write netlist...")
parameterize_netlist(NETLIST_WRITE_HOLD)

# ==============================================================================
# 3. GENERATE OCEAN SCRIPT: TWO INDEPENDENT run() CALLS WITH EXPLICIT ic()
# ==============================================================================
#
# WHY TWO INDEPENDENT SIMULATIONS:
#   The write TB (6tsram_w_tb) has a 40ns stimulus sequence:
#     0-10ns:  Write-1 stimulus (BL=VDD, BLB=0, WL pulse)
#     10-20ns: Hold-1 (WL low)
#     20-30ns: Write-0 stimulus (BL=0, BLB=VDD, WL pulse)
#     30-40ns: Hold-0 (WL low)
#
#   BUG IN PREVIOUS VERSION:
#     No ic() was set. Netlist had "ic qb=0 q=vdd_val" so Q started at VDD.
#     Write-1 (Q->VDD) saw no 0->VDD transition -> delay=-1 but success=1.
#
#   FIX:
#     Run 1: ic(Q=0, QB=VDD), tran 10ns -> Write-1 sees genuine Q: 0->VDD
#     Run 2: ic(Q=VDD, QB=0), tran 30ns -> Write-0 at 20-30ns sees genuine Q: VDD->0
#            (0-10ns Write-1 is a no-op since Q is already VDD, which is harmless)
#
def create_ocean_script(pu_val, pd_val, acc_val, vdd_val, temp_val):
    ocn_content = f"""
simulator('spectre)
temp({temp_val})

fp = outfile("{RESULTS_TXT_ABS}" "w")

design("{NETLIST_WRITE_HOLD}")
resultsDir("{WORK_DIR_WRITE_HOLD}/spectre/schematic")
desVar("nfin_pu" {pu_val})
desVar("nfin_pd" {pd_val})
desVar("nfin_acc" {acc_val})
desVar("vdd_val" {vdd_val})

; ======================================================================
; SIMULATION 1: WRITE-1 (Starting state: Q=0, QB=VDD)
;   -> Measures genuine Q: 0 -> VDD transition in 0-10ns window
; ======================================================================
ic("/q" 0.0 "/qb" {vdd_val})
analysis('tran ?stop 10n ?errpreset 'moderate)
sok_w1 = errset(run())

if(sok_w1 then
    selectResult('tran)
    q_w = v("/q")
    qb_w = v("/qb")
    wl_w = v("/w")
    
    i_vdd_w = i("/V3/PLUS")
    if(i_vdd_w == nil then i_vdd_w = i("V3:p"))
    if(i_vdd_w == nil then i_vdd_w = i("/V3"))
    if(i_vdd_w == nil then i_vdd_w = i("V3"))
    if(i_vdd_w != nil then i_vdd_w = -i_vdd_w)
    
    if(q_w != nil && qb_w != nil then
        q_w1_clip = clip(q_w 0 10n)
        qb_w1_clip = clip(qb_w 0 10n)
        
        q_w1_start = value(q_w 0)
        qb_w1_start = value(qb_w 0)
        
        t_w1_wl50 = cross(wl_w 0.5*{vdd_val} 1 "rising")
        if(t_w1_wl50 == nil then t_w1_wl50 = 0.05n)
        
        t_w1_q50 = cross(q_w1_clip 0.5*{vdd_val} 1 "rising")
        w1_delay_ps = -1.0
        if(t_w1_q50 != nil then
            w1_delay_ps = (t_w1_q50 - t_w1_wl50) * 1e12
            if(w1_delay_ps < 0 then w1_delay_ps = 0.0)
        )
        
        w1_q_excursion = (ymax(q_w1_clip) - q_w1_start) * 1000.0
        w1_qb_excursion = (qb_w1_start - ymin(qb_w1_clip)) * 1000.0
        
        i_w1_avg_ua = 0.0
        i_w1_peak_ua = 0.0
        p_w1_uw = 0.0
        e_w1_fj = 0.0
        if(i_vdd_w != nil then
            i_w1_clip = clip(i_vdd_w 0 10n)
            i_w1_int = integ(i_w1_clip 0 10n)
            i_w1_avg_ua = (i_w1_int / 10e-9) * 1e6
            i_w1_peak_ua = ymax(i_w1_clip) * 1e6
            p_w1_uw = {vdd_val} * i_w1_avg_ua
            e_w1_fj = {vdd_val} * i_w1_int * 1e15
        )
        
        q_w1_end = value(q_w 9.99n)
        qb_w1_end = value(qb_w 9.99n)
        w1_succ = 0
        if(q_w1_end > 0.8 * {vdd_val} && qb_w1_end < 0.2 * {vdd_val} then w1_succ = 1)
        
        fprintf(fp "WRITE_1: cell_write_delay_ps=%g q_node_voltage_excursion_mv=%g qb_node_voltage_excursion_mv=%g average_write_current_ua=%g peak_write_current_ua=%g write_power_uw=%g write_energy_fj=%g write_success=%d\\n"
            w1_delay_ps w1_q_excursion w1_qb_excursion i_w1_avg_ua i_w1_peak_ua p_w1_uw e_w1_fj w1_succ)
    )
else
    fprintf(fp "WRITE_1_ERROR: Spectre run failed for Write-1\\n")
)

; ======================================================================
; SIMULATION 2: WRITE-0 (Starting state: Q=VDD, QB=0)
;   -> At 0-10ns Write-1 stimulus is a no-op (Q already at VDD)
;   -> At 20-30ns Write-0 measures genuine Q: VDD -> 0 transition
; ======================================================================
ic("/q" {vdd_val} "/qb" 0.0)
analysis('tran ?stop 30n ?errpreset 'moderate)
sok_w0 = errset(run())

if(sok_w0 then
    selectResult('tran)
    q_w = v("/q")
    qb_w = v("/qb")
    wl_w = v("/w")
    
    i_vdd_w = i("/V3/PLUS")
    if(i_vdd_w == nil then i_vdd_w = i("V3:p"))
    if(i_vdd_w == nil then i_vdd_w = i("/V3"))
    if(i_vdd_w == nil then i_vdd_w = i("V3"))
    if(i_vdd_w != nil then i_vdd_w = -i_vdd_w)
    
    if(q_w != nil && qb_w != nil then
        q_w0_clip = clip(q_w 20n 30n)
        qb_w0_clip = clip(qb_w 20n 30n)
        
        q_w0_start = value(q_w 20n)
        qb_w0_start = value(qb_w 20n)
        
        t_w0_wl50 = cross(wl_w 0.5*{vdd_val} 2 "rising")
        if(t_w0_wl50 == nil then t_w0_wl50 = 20.05n)
        
        t_w0_q50 = cross(q_w0_clip 0.5*{vdd_val} 1 "falling")
        w0_delay_ps = -1.0
        if(t_w0_q50 != nil then
            w0_delay_ps = (t_w0_q50 - t_w0_wl50) * 1e12
            if(w0_delay_ps < 0 then w0_delay_ps = 0.0)
        )
        
        w0_q_excursion = (q_w0_start - ymin(q_w0_clip)) * 1000.0
        w0_qb_excursion = (ymax(qb_w0_clip) - qb_w0_start) * 1000.0
        
        i_w0_avg_ua = 0.0
        i_w0_peak_ua = 0.0
        p_w0_uw = 0.0
        e_w0_fj = 0.0
        if(i_vdd_w != nil then
            i_w0_clip = clip(i_vdd_w 20n 30n)
            i_w0_int = integ(i_w0_clip 20n 30n)
            i_w0_avg_ua = (i_w0_int / 10e-9) * 1e6
            i_w0_peak_ua = ymax(i_w0_clip) * 1e6
            p_w0_uw = {vdd_val} * i_w0_avg_ua
            e_w0_fj = {vdd_val} * i_w0_int * 1e15
        )
        
        q_w0_end = value(q_w 29.99n)
        qb_w0_end = value(qb_w 29.99n)
        w0_succ = 0
        if(q_w0_end < 0.2 * {vdd_val} && qb_w0_end > 0.8 * {vdd_val} then w0_succ = 1)
        
        fprintf(fp "WRITE_0: cell_write_delay_ps=%g q_node_voltage_excursion_mv=%g qb_node_voltage_excursion_mv=%g average_write_current_ua=%g peak_write_current_ua=%g write_power_uw=%g write_energy_fj=%g write_success=%d\\n"
            w0_delay_ps w0_q_excursion w0_qb_excursion i_w0_avg_ua i_w0_peak_ua p_w0_uw e_w0_fj w0_succ)
    )
else
    fprintf(fp "WRITE_0_ERROR: Spectre run failed for Write-0\\n")
)

close(fp)
exit()
"""
    with open(TEMP_OCN, "w") as f:
        f.write(ocn_content)

# ==============================================================================
# 4. EXECUTION LOOP WITH AUTO-RESUME CHECKPOINTING
# ==============================================================================
pu_fins   = [1, 2, 3, 4, 5]
pd_fins   = [1, 2, 3, 4, 5, 6]
acc_fins  = [1, 2, 3, 4, 5]
vdd_vals  = [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
temp_vals = [27]

# Check if --fresh flag is passed to force re-generation from scratch
FRESH_START = "--fresh" in sys.argv

param_combinations = list(itertools.product(pu_fins, pd_fins, acc_fins, vdd_vals, temp_vals))
print(f"[INFO] Total Simulation Corners: {len(param_combinations)} (150 sizings x 8 VDD levels)")
print(f"[INFO] Two independent run() calls per corner (Write-1 with ic Q=0, Write-0 with ic Q=VDD)")

write_0_dataset = []
write_1_dataset = []
write_combined_dataset = []
completed_corners = set()

# AUTO-RESUME CHECKPOINTING: Read existing CSVs if present (unless --fresh)
if FRESH_START:
    print("[FRESH START] --fresh flag detected. Deleting old CSV files and starting from scratch...")
    for f_csv in [CSV_WRITE_0, CSV_WRITE_1, CSV_WRITE_COMBINED]:
        if os.path.exists(f_csv):
            os.remove(f_csv)
            print(f"  Deleted: {f_csv}")
else:
    if os.path.exists(CSV_WRITE_0):
        try:
            df_old_w0 = pd.read_csv(CSV_WRITE_0)
            write_0_dataset = df_old_w0.to_dict('records')
            for r in write_0_dataset:
                completed_corners.add((int(r['pu_fins']), int(r['pd_fins']), int(r['acc_fins']),
                                       round(float(r['vdd_val']), 4), int(r['temp_val'])))
            print(f"[RESUME] Loaded {len(write_0_dataset)} existing Write-0 rows from '{CSV_WRITE_0}'")
        except Exception as e:
            print(f"[WARNING] Could not read existing {CSV_WRITE_0}: {e}")

    if os.path.exists(CSV_WRITE_1):
        try:
            df_old_w1 = pd.read_csv(CSV_WRITE_1)
            write_1_dataset = df_old_w1.to_dict('records')
            print(f"[RESUME] Loaded {len(write_1_dataset)} existing Write-1 rows from '{CSV_WRITE_1}'")
        except Exception as e:
            print(f"[WARNING] Could not read existing {CSV_WRITE_1}: {e}")

    if os.path.exists(CSV_WRITE_COMBINED):
        try:
            df_old_comb = pd.read_csv(CSV_WRITE_COMBINED)
            write_combined_dataset = df_old_comb.to_dict('records')
        except Exception as e:
            pass

remaining = len(param_combinations) - len(completed_corners)
print(f"[RESUME] {len(completed_corners)} corners already done. {remaining} remaining to simulate!")

def save_csvs_safe():
    """Safely flush current datasets to CSV on disk."""
    if write_0_dataset:
        pd.DataFrame(write_0_dataset).drop_duplicates().to_csv(CSV_WRITE_0, index=False)
    if write_1_dataset:
        pd.DataFrame(write_1_dataset).drop_duplicates().to_csv(CSV_WRITE_1, index=False)
    if write_combined_dataset:
        pd.DataFrame(write_combined_dataset).drop_duplicates().to_csv(CSV_WRITE_COMBINED, index=False)

simulated_count = 0

for idx, (pu_val, pd_val, acc_val, vdd_val, temp_val) in enumerate(param_combinations, 1):
    corner_key = (int(pu_val), int(pd_val), int(acc_val), round(float(vdd_val), 4), int(temp_val))
    
    if corner_key in completed_corners:
        continue

    simulated_count += 1
    print(f"\n================================================================================")
    print(f" [{idx}/{len(param_combinations)}] WRITE SIM: PU={pu_val} PD={pd_val} ACC={acc_val} VDD={vdd_val}V Temp={temp_val}C")
    print(f"================================================================================")
    
    if os.path.exists(RESULTS_TXT_ABS):
        os.remove(RESULTS_TXT_ABS)
        
    create_ocean_script(pu_val, pd_val, acc_val, vdd_val, temp_val)
    
    # Robust shell command execution (COPIED FROM WORKING SCRIPT)
    csh_cmd = f'csh -c "source /home/install/cshrc; {OCEAN_EXEC} -log {LOG_OCN} -replay {TEMP_OCN}"'
    
    proc = subprocess.run(
        csh_cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    
    # PROCESS EXIT CHECK
    if proc.returncode != 0:
        print(f"  [ERROR] OCEAN returned code {proc.returncode}")
        if proc.stderr:
            print(f"  STDERR: {proc.stderr[:300]}")
        continue

    # CHECK MEASUREMENT RESULTS FILE
    if not os.path.exists(RESULTS_TXT_ABS):
        print(f"  [ERROR] Measurement file '{RESULTS_TXT_ABS}' was NOT created!")
        if os.path.exists(LOG_OCN):
            with open(LOG_OCN, "r") as lf:
                log_lines = lf.readlines()
                for line in log_lines[-15:]:
                    print("  [OCEAN LOG]:", line.strip())
        continue

    # PARSE MEASUREMENTS
    meas_data = {}
    with open(RESULTS_TXT_ABS, "r") as f:
        for line in f:
            parts = line.strip().split(": ")
            if len(parts) == 2:
                tag = parts[0]
                keyvals = parts[1].split()
                d = {}
                for kv in keyvals:
                    if "=" in kv:
                        k, v = kv.split("=")
                        try:
                            d[k] = float(v)
                        except:
                            d[k] = v
                meas_data[tag] = d

    base_info = {"pu_fins": pu_val, "pd_fins": pd_val, "acc_fins": acc_val, "vdd_val": vdd_val, "temp_val": temp_val}

    # Parse WRITE-1 measurements
    if "WRITE_1" in meas_data:
        w1_row = {**base_info, "write_type": "write_1", **meas_data["WRITE_1"]}
        write_1_dataset.append(w1_row)
        write_combined_dataset.append(w1_row)
        d1 = meas_data["WRITE_1"]
        print(f"  -> W1: delay={d1.get('cell_write_delay_ps', -1):.2f}ps | Q_exc={d1.get('q_node_voltage_excursion_mv', 0):.2f}mV | QB_exc={d1.get('qb_node_voltage_excursion_mv', 0):.2f}mV | power={d1.get('write_power_uw', 0):.2f}uW | success={int(d1.get('write_success', 0))}")
    else:
        print(f"  [WARN] WRITE_1 section missing from measurement file!")

    # Parse WRITE-0 measurements
    if "WRITE_0" in meas_data:
        w0_row = {**base_info, "write_type": "write_0", **meas_data["WRITE_0"]}
        write_0_dataset.append(w0_row)
        write_combined_dataset.append(w0_row)
        d0 = meas_data["WRITE_0"]
        print(f"  -> W0: delay={d0.get('cell_write_delay_ps', -1):.2f}ps | Q_exc={d0.get('q_node_voltage_excursion_mv', 0):.2f}mV | QB_exc={d0.get('qb_node_voltage_excursion_mv', 0):.2f}mV | power={d0.get('write_power_uw', 0):.2f}uW | success={int(d0.get('write_success', 0))}")
    else:
        print(f"  [WARN] WRITE_0 section missing from measurement file!")

    # Mark corner completed
    completed_corners.add(corner_key)

    # Auto-Save after EVERY iteration for maximum data safety
    save_csvs_safe()
    print(f"  [SAVED] Progress: {len(completed_corners)}/{len(param_combinations)} corners done")

# ==============================================================================
# 5. FINAL DATASET CSV EXPORT & VERIFICATION
# ==============================================================================
save_csvs_safe()

abs_w0 = os.path.abspath(CSV_WRITE_0)
abs_w1 = os.path.abspath(CSV_WRITE_1)
abs_comb = os.path.abspath(CSV_WRITE_COMBINED)

print("\n================================================================================")
print(" [DONE] STANDALONE WRITE SWEEP COMPLETE!")
print(f" 1. Write-0 Dataset   : '{abs_w0}' ({len(write_0_dataset)} rows)")
print(f" 2. Write-1 Dataset   : '{abs_w1}' ({len(write_1_dataset)} rows)")
print(f" 3. Combined Write CSV: '{abs_comb}' ({len(write_combined_dataset)} rows)")
print("================================================================================")
