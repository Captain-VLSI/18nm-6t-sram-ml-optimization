#!/usr/bin/env python3
"""
========================================================================================
  STANDALONE 6T SRAM BITCELL READ (READ-1 & READ-0) TRANSIENT CHARACTERIZATION SCRIPT
========================================================================================
 Technology: Cadence Virtuoso + Spectre (FinFET cds_ff_mpt 7nm PDK)
 Scope     : Standalone 6T SRAM Bitcell Read-1 (Q=VDD, QB=0) and Read-0 (Q=0, QB=VDD)
 Target    : AI-Assisted SRAM Bitcell Multi-Objective Optimization
 Mode      : PRODUCTION & DATASET GENERATION MODE (Merged Read-1 & Read-0 Dataset)
 Datasets  :
   1. sram_bitcell_read_tran_dataset.csv (1200 rows total: 600 Read-1 + 600 Read-0)
========================================================================================
"""

import os
import sys
import subprocess
import itertools
import pandas as pd

# Prevent UnicodeEncodeError on Linux terminals with non-UTF-8 locales (e.g. latin-1 / ASCII)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# ==============================================================================
# 1. ENVIRONMENT & PATH DEFINITIONS (VERIFIED WORKING CADENCE SETUP)
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

# Absolute netlist paths on Linux Lab PC (reusing existing Read testbench)
NETLIST_READ = "/home/vlsi-lab/simulation/6tsram_r_trans_tb/spectre/schematic/netlist/netlist"
WORK_DIR_READ = "/home/vlsi-lab/simulation/6tsram_r_trans_tb"

MODEL_PATH = "/home/install/FOUNDRY/cds_ff_mpt_v_0.5/cds_ff_mpt/../models/spectre/cds_ff_mpt.scs"

# Output Merged Dataset CSV File Name
CSV_READ = "sram_bitcell_read_tran_dataset.csv"

TEMP_OCN = "run_temp_standalone_read.ocn"
LOG_OCN = "ocean_standalone_read.log"
FAIL_LOG = "simulation_failures_read.log"
RESULTS_TXT_ABS = "/home/vlsi-lab/Ganesh_Mtech/Mtech_project_ganesh/meas_standalone_read_temp.txt"

REQUIRED_SECTIONS = ["READ_1", "READ_0"]

READ_FIELDS = [
    "max_q_disturb_mv", "max_qb_disturb_mv", "q_drop_mv",
    "wl_to_q_disturb_peak_ps", "wl_to_qb_disturb_peak_ps",
    "average_read_current_ua", "peak_read_current_ua",
    "read_power_uw", "read_energy_fj", "read_success"
]

REQUIRED_FIELDS = {
    "READ_1": READ_FIELDS,
    "READ_0": READ_FIELDS
}

# ==============================================================================
# 2. NETLIST PARAMETERIZATION
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
        # Parameterize voltage sources (requires at least 1 numeric digit)
        f"sed -i 's/\\(V0 (net6 0).*dc=\\)[0-9][0-9.]*m*/\\1vdd_val/' {netlist_path}",
        f"sed -i 's/\\(V3 (net1 0).*dc=\\)[0-9][0-9.]*m*/\\1vdd_val/' {netlist_path}",
        f"sed -i 's/\\(V3 (net6 0).*dc=\\)[0-9][0-9.]*m*/\\1vdd_val/' {netlist_path}",
        f"sed -i 's/\\(V1 (bl 0).*dc=\\)[0-9][0-9.]*m*/\\1vdd_val/' {netlist_path}",
        f"sed -i 's/\\(V2 (blb 0).*dc=\\)[0-9][0-9.]*m*/\\1vdd_val/' {netlist_path}",
        f"sed -i 's/\\(V5 (w 0).*val1=\\)[0-9][0-9.]*m*/\\1vdd_val/' {netlist_path}",
        f"sed -i 's/\\(V0 (w 0).*val1=\\)[0-9][0-9.]*m*/\\1vdd_val/' {netlist_path}",
        f"sed -i 's/\\(V1 (bl 0).*val1=\\)[0-9][0-9.]*m*/\\1vdd_val/' {netlist_path}",
        f"sed -i 's/\\(V2 (blb 0).*val0=\\)[0-9][0-9.]*m*/\\1vdd_val/' {netlist_path}",
        # Remove netlist fixed IC so OCEAN ic() dynamically sets Q and QB for Read-1 and Read-0
        f"sed -i '/ic qb=/d' {netlist_path}",
        f"sed -i '/ic q=/d' {netlist_path}"
    ]
        
    for cmd in cmds:
        subprocess.run(cmd, shell=True)
    return True

print("[INFO] Parameterizing netlist for Read-1 & Read-0...")
parameterize_netlist(NETLIST_READ)

# ==============================================================================
# 3. GENERATE OCEAN SIMULATION REPLAY SCRIPT (Sequential Read-1 & Read-0)
# ==============================================================================
def create_ocean_script(pu_val, pd_val, acc_val, vdd_val, temp_val):
    ocn_content = f"""
simulator('spectre)
temp({temp_val})

fp = outfile("{RESULTS_TXT_ABS}" "w")

; ==============================================================================
; REUSABLE READ MEASUREMENT PROCEDURE (For Read-1 and Read-0)
; ==============================================================================
procedure(measure_read(tag expected_q_high vdd_val fp)
    let((q_w qb_w wl_w q_clip qb_clip q_start qb_start t_wl50 q_end qb_end
         q_disturb qb_disturb q_drop t_q_peak t_qb_peak read_succ
         dt_q_ps dt_qb_ps i_vdd_r i_clip i_read_int i_read_avg_ua i_read_peak_ua
         p_read_uw e_read_fj q_min_val qb_max_val q_max_val qb_min_val)
        
        selectResult('tran)
        q_w = v("/q")
        qb_w = v("/qb")
        wl_w = v("/w")
        
        ; Fail-proof terminal current detection for V0 or V3 supply source
        i_vdd_r = i("/V0/PLUS")
        if(i_vdd_r == nil then i_vdd_r = i("V0:p"))
        if(i_vdd_r == nil then i_vdd_r = i("/V0"))
        if(i_vdd_r == nil then i_vdd_r = i("V0"))
        if(i_vdd_r == nil then i_vdd_r = i("/V3/PLUS"))
        if(i_vdd_r == nil then i_vdd_r = i("V3:p"))
        if(i_vdd_r == nil then i_vdd_r = i("/V3"))
        if(i_vdd_r == nil then i_vdd_r = i("V3"))
        if(i_vdd_r != nil then i_vdd_r = -i_vdd_r)
        
        if(q_w != nil && qb_w != nil then
            q_clip = clip(q_w 0 10n)
            qb_clip = clip(qb_w 0 10n)
            
            q_start = value(q_w 0)
            if(q_start == nil then q_start = value(q_clip 0))
            qb_start = value(qb_w 0)
            if(qb_start == nil then qb_start = value(qb_clip 0))
            
            t_wl50 = cross(wl_w 0.5*vdd_val 1 "rising")
            if(t_wl50 == nil then t_wl50 = 0.05n)
            
            q_end = value(q_clip 9.99n)
            qb_end = value(qb_clip 9.99n)
            
            if(expected_q_high == 1 then
                ; READ-1 Analysis (Stored state Q=VDD, QB=0)
                q_min_val = ymin(q_clip)
                q_drop = (vdd_val - q_min_val) * 1000.0
                q_disturb = q_drop
                
                qb_max_val = ymax(qb_clip)
                qb_disturb = (qb_max_val - qb_start) * 1000.0
                
                t_q_peak = xmin(q_clip)
                if(t_q_peak == nil then t_q_peak = t_wl50)
                
                t_qb_peak = xmax(qb_clip)
                if(t_qb_peak == nil then t_qb_peak = t_wl50)
                
                read_succ = 1
                if(q_end < 0.5 * vdd_val || qb_end > 0.5 * vdd_val then read_succ = 0)
            else
                ; READ-0 Analysis (Stored state Q=0, QB=VDD)
                q_max_val = ymax(q_clip)
                q_disturb = (q_max_val - q_start) * 1000.0
                if(q_disturb < 0 then q_disturb = 0.0)
                
                qb_min_val = ymin(qb_clip)
                q_drop = (qb_start - qb_min_val) * 1000.0
                if(q_drop < 0 then q_drop = 0.0)
                qb_disturb = q_drop
                
                t_q_peak = xmax(q_clip)
                if(t_q_peak == nil then t_q_peak = t_wl50)
                
                t_qb_peak = xmin(qb_clip)
                if(t_qb_peak == nil then t_qb_peak = t_wl50)
                
                read_succ = 1
                if(q_end > 0.5 * vdd_val || qb_end < 0.5 * vdd_val then read_succ = 0)
            )
            
            dt_q_ps = (t_q_peak - t_wl50) * 1e12
            if(dt_q_ps < 0 then dt_q_ps = 0.0)
            
            dt_qb_ps = (t_qb_peak - t_wl50) * 1e12
            if(dt_qb_ps < 0 then dt_qb_ps = 0.0)
            
            i_read_avg_ua = 0.0
            i_read_peak_ua = 0.0
            p_read_uw = 0.0
            e_read_fj = 0.0
            
            if(i_vdd_r != nil then
                i_clip = clip(i_vdd_r 0 10n)
                i_read_int = integ(i_clip 0 10n)
                i_read_avg_ua = (i_read_int / 10e-9) * 1e6
                i_read_peak_ua = ymax(i_clip) * 1e6
                p_read_uw = vdd_val * i_read_avg_ua
                e_read_fj = vdd_val * i_read_int * 1e15
            )
            
            fprintf(fp "%s: max_q_disturb_mv=%g max_qb_disturb_mv=%g q_drop_mv=%g wl_to_q_disturb_peak_ps=%g wl_to_qb_disturb_peak_ps=%g average_read_current_ua=%g peak_read_current_ua=%g read_power_uw=%g read_energy_fj=%g read_success=%d\\n"
                tag q_disturb qb_disturb q_drop dt_q_ps dt_qb_ps i_read_avg_ua i_read_peak_ua p_read_uw e_read_fj read_succ)
        )
    )
)

; ==============================================================================
; 1. READ TRANSIENT ANALYSIS (Sequential Read-1 and Read-0 Execution)
; ==============================================================================
design("{NETLIST_READ}")
resultsDir("{WORK_DIR_READ}/spectre/schematic")
desVar("nfin_pu" {pu_val})
desVar("nfin_pd" {pd_val})
desVar("nfin_acc" {acc_val})
desVar("vdd_val" {vdd_val})

analysis('tran ?stop 20n ?errpreset 'moderate)

; --- A. READ-1 SIMULATION (Initial condition: Q=VDD, QB=0) ---
ic("/q" {vdd_val} "/qb" 0.0)
sok_r1 = errset(run())
if(sok_r1 then
    measure_read("READ_1" 1 {vdd_val} fp)
else
    fprintf(fp "READ_1_ERROR: Spectre run failed for Read-1 testbench\\n")
)

; --- B. READ-0 SIMULATION (Initial condition: Q=0, QB=VDD) ---
ic("/q" 0.0 "/qb" {vdd_val})
sok_r0 = errset(run())
if(sok_r0 then
    measure_read("READ_0" 0 {vdd_val} fp)
else
    fprintf(fp "READ_0_ERROR: Spectre run failed for Read-0 testbench\\n")
)

close(fp)
exit()
"""
    with open(TEMP_OCN, "w") as f:
        f.write(ocn_content)

# ==============================================================================
# 4. EXECUTION LOOP WITH SYSTEMATIC DIAGNOSTICS & VERIFIED SETUP
# ==============================================================================
# Full Read-1 & Read-0 Dataset Sweep Mode (600 Simulation Combinations)
pu_fins   = [1, 2, 3, 4, 5]
pd_fins   = [1, 2, 3, 4, 5, 6]
acc_fins  = [1, 2, 3, 4, 5]
vdd_vals  = [0.6, 0.7, 0.8, 0.9]
temp_vals = [27]

param_combinations = list(itertools.product(pu_fins, pd_fins, acc_fins, vdd_vals, temp_vals))
print(f"[INFO] Running Merged Read-1 & Read-0 Dataset Sweep with {len(param_combinations)} Combinations...")

read_dataset = []

for idx, (pu_val, pd_val, acc_val, vdd_val, temp_val) in enumerate(param_combinations, 1):
    print(f"\n================================================================================")
    print(f" [SEARCH] READ (1 & 0) SIMULATION RUN [{idx}/{len(param_combinations)}]")
    print(f" Parameters: PU={pu_val}, PD={pd_val}, ACC={acc_val}, VDD={vdd_val}V, Temp={temp_val}C")
    print(f"================================================================================")
    
    if os.path.exists(RESULTS_TXT_ABS):
        os.remove(RESULTS_TXT_ABS)
        
    create_ocean_script(pu_val, pd_val, acc_val, vdd_val, temp_val)
    print(f"[DIAGNOSTIC] Generated OCEAN Script: '{TEMP_OCN}'")
    
    csh_cmd = f'csh -c "source /home/install/cshrc; {OCEAN_EXEC} -log {LOG_OCN} -replay {TEMP_OCN}"'
    print(f"[DIAGNOSTIC] Executing Command Line:\n  {csh_cmd}\n")
    
    proc = subprocess.run(
        csh_cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    
    if proc.returncode != 0:
        print("\n[CRITICAL ERROR] OCEAN execution failed!")
        print(f"  Return Code: {proc.returncode}")
        if proc.stderr:
            print(f"  STDERR Output:\n{proc.stderr}")
        if proc.stdout:
            print(f"  STDOUT Output:\n{proc.stdout}")
        sys.exit(1)
    
    print(f"--------------------------------------------------------------------------------")
    print(f" [STATS] SUBPROCESS DIAGNOSTIC OUTPUT")
    print(f"--------------------------------------------------------------------------------")
    print(f" Return Code: {proc.returncode}")
    print(f" STDOUT Output:\n{proc.stdout if proc.stdout.strip() else '  [EMPTY STDOUT]'}")
    print(f" STDERR Output:\n{proc.stderr if proc.stderr.strip() else '  [EMPTY STDERR]'}")
    print(f"--------------------------------------------------------------------------------")

    if os.path.exists(LOG_OCN):
        print(f"\n[DIAGNOSTIC] OCEAN Log File '{LOG_OCN}' Exists ({os.path.getsize(LOG_OCN)} bytes):")
        with open(LOG_OCN, "r") as lf:
            log_lines = lf.readlines()
            for line in log_lines[-20:]:
                print("  [OCEAN LOG]:", line.strip())
    else:
        print(f"\n[CRITICAL DIAGNOSTIC ERROR] OCEAN Log File '{LOG_OCN}' WAS NOT CREATED!")

    meas_data = {}
    if os.path.exists(RESULTS_TXT_ABS):
        print(f"\n[DIAGNOSTIC] Measurement File '{RESULTS_TXT_ABS}' Exists ({os.path.getsize(RESULTS_TXT_ABS)} bytes):")
        with open(RESULTS_TXT_ABS, "r") as f:
            lines = f.readlines()
            print("".join(lines))
            for line in lines:
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
    else:
        print(f"\n[CRITICAL DIAGNOSTIC ERROR] Measurement File '{RESULTS_TXT_ABS}' WAS NOT CREATED!")

    missing_sections = [sec for sec in REQUIRED_SECTIONS if sec not in meas_data]
    if missing_sections:
        print(f"[DIAGNOSTIC FAILURE] Missing Required Measurement Sections: {missing_sections}")

    missing_fields = {}
    for sec in REQUIRED_SECTIONS:
        if sec in meas_data:
            mf = [f for f in REQUIRED_FIELDS[sec] if f not in meas_data[sec]]
            if mf:
                missing_fields[sec] = mf
    if missing_fields:
        print(f"[DIAGNOSTIC FAILURE] Missing Required Measurement Fields: {missing_fields}")

    if proc.returncode != 0 or not os.path.exists(RESULTS_TXT_ABS) or missing_sections or missing_fields:
        print("\n" + "=" * 80)
        print(" [HALT] DIAGNOSTIC HALT TRIGGERED: OCEAN / Spectre Failed to produce valid output!")
        print("=" * 80)
        sys.exit(1)

    # 1. READ DATASET (Append both Read-1 and Read-0 rows)
    if "READ_1" in meas_data:
        r1_row = {"pu_fins": pu_val, "pd_fins": pd_val, "acc_fins": acc_val, "vdd_val": vdd_val, "temp_val": temp_val, "read_type": "read_1"}
        r1_row.update(meas_data["READ_1"])
        read_dataset.append(r1_row)
    if "READ_0" in meas_data:
        r0_row = {"pu_fins": pu_val, "pd_fins": pd_val, "acc_fins": acc_val, "vdd_val": vdd_val, "temp_val": temp_val, "read_type": "read_0"}
        r0_row.update(meas_data["READ_0"])
        read_dataset.append(r0_row)

# ==============================================================================
# 5. DATASET DEDUPLICATION, VALIDATION & CSV EXPORT
# ==============================================================================
df_read = pd.DataFrame(read_dataset).drop_duplicates()
df_read.to_csv(CSV_READ, index=False)

print("\n================================================================================")
print(" [SUCCESS] MERGED READ-1 & READ-0 SWEEP COMPLETE!")
print(f" Saved Read Dataset : '{CSV_READ}' ({len(df_read)} rows)")
print("================================================================================")
