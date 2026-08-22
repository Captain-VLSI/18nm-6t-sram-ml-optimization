#!/usr/bin/env python3
"""
========================================================================================
  STANDALONE 6T SRAM BITCELL TRANSIENT CHARACTERIZATION AUTOMATION SCRIPT (COMPLETE)
========================================================================================
 Technology: Cadence Virtuoso + Spectre (FinFET cds_ff_mpt 7nm PDK)
 Scope     : Standalone 6T SRAM Bitcell (No Array / Sense Amp / Precharge logic)
 Target    : AI-Assisted SRAM Bitcell Multi-Objective Optimization
 Mode      : PRODUCTION & DATASET GENERATION MODE (Read-1, Read-0, Write, Hold)
 Datasets  :
   1. sram_bitcell_read_tran_dataset.csv  (1200 rows: Read-1 & Read-0)
   2. sram_bitcell_write_tran_dataset.csv (1200 rows: Write-0 & Write-1)
   3. sram_bitcell_hold_tran_dataset.csv  (1200 rows: Hold-0 & Hold-1)
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

# Absolute netlist paths on Linux Lab PC (verified)
NETLIST_READ = "/home/vlsi-lab/simulation/6tsram_r_trans_tb/spectre/schematic/netlist/netlist"
NETLIST_WRITE_HOLD = "/home/vlsi-lab/simulation/6tsram_w_tb/spectre/schematic/netlist/netlist"

WORK_DIR_READ = "/home/vlsi-lab/simulation/6tsram_r_trans_tb"
WORK_DIR_WRITE_HOLD = "/home/vlsi-lab/simulation/6tsram_w_tb"

MODEL_PATH = "/home/install/FOUNDRY/cds_ff_mpt_v_0.5/cds_ff_mpt/../models/spectre/cds_ff_mpt.scs"

# Output Dataset CSV File Names
CSV_READ = "sram_bitcell_read_tran_dataset.csv"
CSV_WRITE = "sram_bitcell_write_tran_dataset.csv"
CSV_HOLD = "sram_bitcell_hold_tran_dataset.csv"

TEMP_OCN = "run_temp_standalone.ocn"
LOG_OCN = "ocean_standalone.log"
FAIL_LOG = "simulation_failures.log"
RESULTS_TXT_ABS = "/home/vlsi-lab/Ganesh_Mtech/Mtech_project_ganesh/meas_standalone_temp.txt"

REQUIRED_SECTIONS = ["READ_1", "READ_0", "WRITE_0", "WRITE_1", "HOLD_0", "HOLD_1"]

READ_FIELDS = [
    "max_q_disturb_mv", "max_qb_disturb_mv", "q_drop_mv",
    "wl_to_q_disturb_peak_ps", "wl_to_qb_disturb_peak_ps",
    "average_read_current_ua", "peak_read_current_ua",
    "read_power_uw", "read_energy_fj", "read_success"
]

REQUIRED_FIELDS = {
    "READ_1": READ_FIELDS,
    "READ_0": READ_FIELDS,
    "WRITE_0": [
        "write_delay_ps", "max_q_disturb_mv", "max_qb_disturb_mv",
        "average_write_current_ua", "peak_write_current_ua",
        "write_power_uw", "write_energy_fj", "write_success"
    ],
    "WRITE_1": [
        "write_delay_ps", "max_q_disturb_mv", "max_qb_disturb_mv",
        "average_write_current_ua", "peak_write_current_ua",
        "write_power_uw", "write_energy_fj", "write_success"
    ],
    "HOLD_0": [
        "hold_q_drop_mv", "hold_qb_disturb_mv",
        "hold_leakage_current_na", "hold_power_uw",
        "hold_energy_fj", "hold_success"
    ],
    "HOLD_1": [
        "hold_q_drop_mv", "hold_qb_disturb_mv",
        "hold_leakage_current_na", "hold_power_uw",
        "hold_energy_fj", "hold_success"
    ]
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
        # Parameterize voltage sources (requires at least 1 numeric digit so vdd_val is never duplicated)
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

print("[INFO] Parameterizing netlists...")
parameterize_netlist(NETLIST_READ)
parameterize_netlist(NETLIST_WRITE_HOLD)

# ==============================================================================
# 3. GENERATE OCEAN SIMULATION REPLAY SCRIPT
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

; ==============================================================================
; 2. WRITE & HOLD TRANSIENT ANALYSIS (0 to 40ns Sequence)
; ==============================================================================
design("{NETLIST_WRITE_HOLD}")
resultsDir("{WORK_DIR_WRITE_HOLD}/spectre/schematic")
desVar("nfin_pu" {pu_val})
desVar("nfin_pd" {pd_val})
desVar("nfin_acc" {acc_val})
desVar("vdd_val" {vdd_val})

analysis('tran ?stop 40n ?errpreset 'moderate)
sok_w = errset(run())

if(sok_w then
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
        ; ----------------------------------------------------------------------
        ; A. WRITE-1 (0ns to 10ns): Forcing Q -> VDD, QB -> 0
        ; ----------------------------------------------------------------------
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
        
        w1_q_disturb = (ymax(q_w1_clip) - q_w1_start) * 1000.0
        w1_qb_disturb = (qb_w1_start - ymin(qb_w1_clip)) * 1000.0
        
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
        
        fprintf(fp "WRITE_1: write_delay_ps=%g max_q_disturb_mv=%g max_qb_disturb_mv=%g average_write_current_ua=%g peak_write_current_ua=%g write_power_uw=%g write_energy_fj=%g write_success=%d\\n"
            w1_delay_ps w1_q_disturb w1_qb_disturb i_w1_avg_ua i_w1_peak_ua p_w1_uw e_w1_fj w1_succ)

        ; ----------------------------------------------------------------------
        ; B. HOLD-1 (10ns to 20ns): Stored State = 1 (Q=HIGH, QB=LOW)
        ; ----------------------------------------------------------------------
        q_h1_clip = clip(q_w 10n 20n)
        qb_h1_clip = clip(qb_w 10n 20n)
        
        h1_high_drop = ({vdd_val} - ymin(q_h1_clip)) * 1000.0
        h1_low_disturb = (ymax(qb_h1_clip) - 0.0) * 1000.0
        
        i_h1_avg_na = 0.0
        p_h1_uw = 0.0
        e_h1_fj = 0.0
        if(i_vdd_w != nil then
            i_h1_clip = clip(i_vdd_w 10n 20n)
            i_h1_int = integ(i_h1_clip 10n 20n)
            i_h1_avg_na = (i_h1_int / 10e-9) * 1e9
            p_h1_uw = {vdd_val} * (i_h1_int / 10e-9) * 1e6
            e_h1_fj = {vdd_val} * i_h1_int * 1e15
        )
        
        q_h1_end = value(q_w 19.99n)
        qb_h1_end = value(qb_w 19.99n)
        h1_succ = 0
        if(q_h1_end > 0.7 * {vdd_val} && qb_h1_end < 0.3 * {vdd_val} then h1_succ = 1)
        
        fprintf(fp "HOLD_1: hold_q_drop_mv=%g hold_qb_disturb_mv=%g hold_leakage_current_na=%g hold_power_uw=%g hold_energy_fj=%g hold_success=%d\\n"
            h1_high_drop h1_low_disturb i_h1_avg_na p_h1_uw e_h1_fj h1_succ)

        ; ----------------------------------------------------------------------
        ; C. WRITE-0 (20ns to 30ns): Forcing Q -> 0, QB -> VDD
        ; ----------------------------------------------------------------------
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
        
        w0_q_disturb = (q_w0_start - ymin(q_w0_clip)) * 1000.0
        w0_qb_disturb = (ymax(qb_w0_clip) - qb_w0_start) * 1000.0
        
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
        
        fprintf(fp "WRITE_0: write_delay_ps=%g max_q_disturb_mv=%g max_qb_disturb_mv=%g average_write_current_ua=%g peak_write_current_ua=%g write_power_uw=%g write_energy_fj=%g write_success=%d\\n"
            w0_delay_ps w0_q_disturb w0_qb_disturb i_w0_avg_ua i_w0_peak_ua p_w0_uw e_w0_fj w0_succ)

        ; ----------------------------------------------------------------------
        ; D. HOLD-0 (30ns to 40ns): Stored State = 0 (QB=HIGH, Q=LOW)
        ; ----------------------------------------------------------------------
        q_h0_clip = clip(q_w 30n 40n)
        qb_h0_clip = clip(qb_w 30n 40n)
        
        h0_high_drop = ({vdd_val} - ymin(qb_h0_clip)) * 1000.0
        h0_low_disturb = (ymax(q_h0_clip) - 0.0) * 1000.0
        
        i_h0_avg_na = 0.0
        p_h0_uw = 0.0
        e_h0_fj = 0.0
        if(i_vdd_w != nil then
            i_h0_clip = clip(i_vdd_w 30n 40n)
            i_h0_int = integ(i_h0_clip 30n 40n)
            i_h0_avg_na = (i_h0_int / 10e-9) * 1e9
            p_h0_uw = {vdd_val} * (i_h0_int / 10e-9) * 1e6
            e_h0_fj = {vdd_val} * i_h0_int * 1e15
        )
        
        q_h0_end = value(q_w 39.99n)
        qb_h0_end = value(qb_w 39.99n)
        h0_succ = 0
        if(qb_h0_end > 0.7 * {vdd_val} && q_h0_end < 0.3 * {vdd_val} then h0_succ = 1)
        
        fprintf(fp "HOLD_0: hold_q_drop_mv=%g hold_qb_disturb_mv=%g hold_leakage_current_na=%g hold_power_uw=%g hold_energy_fj=%g hold_success=%d\\n"
            h0_high_drop h0_low_disturb i_h0_avg_na p_h0_uw e_h0_fj h0_succ)
    )
else
    fprintf(fp "WRITE_HOLD_ERROR: Spectre run failed for Write/Hold testbench\\n")
)

close(fp)
exit()
"""
    with open(TEMP_OCN, "w") as f:
        f.write(ocn_content)

# ==============================================================================
# 4. EXECUTION LOOP WITH SYSTEMATIC DIAGNOSTICS & VERIFIED SETUP
# ==============================================================================
# Full Dataset Sweep Mode (600 Simulation Combinations)
pu_fins   = [1, 2, 3, 4, 5]
pd_fins   = [1, 2, 3, 4, 5, 6]
acc_fins  = [1, 2, 3, 4, 5]
vdd_vals  = [0.6, 0.7, 0.8, 0.9]
temp_vals = [27]

param_combinations = list(itertools.product(pu_fins, pd_fins, acc_fins, vdd_vals, temp_vals))
print(f"[INFO] Running Full Dataset Generation Sweep with {len(param_combinations)} Combinations...")

read_dataset = []
write_dataset = []
hold_dataset = []

failed_runs = []

for idx, (pu_val, pd_val, acc_val, vdd_val, temp_val) in enumerate(param_combinations, 1):
    print(f"\n================================================================================")
    print(f" [SEARCH] DIAGNOSTIC SIMULATION RUN [{idx}/{len(param_combinations)}]")
    print(f" Parameters: PU={pu_val}, PD={pd_val}, ACC={acc_val}, VDD={vdd_val}V, Temp={temp_val}C")
    print(f"================================================================================")
    
    if os.path.exists(RESULTS_TXT_ABS):
        os.remove(RESULTS_TXT_ABS)
        
    create_ocean_script(pu_val, pd_val, acc_val, vdd_val, temp_val)
    print(f"[DIAGNOSTIC] Generated OCEAN Replay Script: '{TEMP_OCN}'")
    
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
            for line in log_lines[-30:]:
                print("  [OCEAN LOG]:", line.strip())
    else:
        print(f"\n[CRITICAL DIAGNOSTIC ERROR] OCEAN Log File '{LOG_OCN}' WAS NOT CREATED by OCEAN!")

    meas_data = {}
    if os.path.exists(RESULTS_TXT_ABS):
        print(f"\n[DIAGNOSTIC] Measurement File '{RESULTS_TXT_ABS}' Exists ({os.path.getsize(RESULTS_TXT_ABS)} bytes):")
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

    # Append parsed measurements into dataset rows
    # 1. READ DATASET (Append both Read-1 and Read-0 rows)
    if "READ_1" in meas_data:
        r1_row = {"pu_fins": pu_val, "pd_fins": pd_val, "acc_fins": acc_val, "vdd_val": vdd_val, "temp_val": temp_val, "read_type": "read_1"}
        r1_row.update(meas_data["READ_1"])
        read_dataset.append(r1_row)
    if "READ_0" in meas_data:
        r0_row = {"pu_fins": pu_val, "pd_fins": pd_val, "acc_fins": acc_val, "vdd_val": vdd_val, "temp_val": temp_val, "read_type": "read_0"}
        r0_row.update(meas_data["READ_0"])
        read_dataset.append(r0_row)

    # 2. WRITE DATASET (Write-0 & Write-1)
    if "WRITE_0" in meas_data:
        w0_row = {"pu_fins": pu_val, "pd_fins": pd_val, "acc_fins": acc_val, "vdd_val": vdd_val, "temp_val": temp_val, "write_type": "write_0"}
        w0_row.update(meas_data["WRITE_0"])
        write_dataset.append(w0_row)
    if "WRITE_1" in meas_data:
        w1_row = {"pu_fins": pu_val, "pd_fins": pd_val, "acc_fins": acc_val, "vdd_val": vdd_val, "temp_val": temp_val, "write_type": "write_1"}
        w1_row.update(meas_data["WRITE_1"])
        write_dataset.append(w1_row)

    # 3. HOLD DATASET (Hold-0 & Hold-1)
    if "HOLD_0" in meas_data:
        h0_row = {"pu_fins": pu_val, "pd_fins": pd_val, "acc_fins": acc_val, "vdd_val": vdd_val, "temp_val": temp_val, "hold_type": "hold_0"}
        h0_row.update(meas_data["HOLD_0"])
        hold_dataset.append(h0_row)
    if "HOLD_1" in meas_data:
        h1_row = {"pu_fins": pu_val, "pd_fins": pd_val, "acc_fins": acc_val, "vdd_val": vdd_val, "temp_val": temp_val, "hold_type": "hold_1"}
        h1_row.update(meas_data["HOLD_1"])
        hold_dataset.append(h1_row)

# ==============================================================================
# 5. DATASET DEDUPLICATION, VALIDATION & CSV EXPORT
# ==============================================================================
df_read = pd.DataFrame(read_dataset).drop_duplicates()
df_write = pd.DataFrame(write_dataset).drop_duplicates()
df_hold = pd.DataFrame(hold_dataset).drop_duplicates()

df_read.to_csv(CSV_READ, index=False)
df_write.to_csv(CSV_WRITE, index=False)
df_hold.to_csv(CSV_HOLD, index=False)

print("\n================================================================================")
print(" [SUCCESS] TRANSIENT CHARACTERIZATION SWEEP COMPLETE!")
print(f" Saved Read Dataset  : '{CSV_READ}' ({len(df_read)} rows)")
print(f" Saved Write Dataset : '{CSV_WRITE}' ({len(df_write)} rows)")
print(f" Saved Hold Dataset  : '{CSV_HOLD}' ({len(df_hold)} rows)")
print("================================================================================")
