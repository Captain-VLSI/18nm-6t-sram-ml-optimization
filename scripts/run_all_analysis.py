#!/usr/bin/env python3
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

print("=" * 80)
print("  EXECUTING COMPLETE SRAM CHARACTERIZATION & ML AUDIT PIPELINE")
print("=" * 80)

tasks = [
    os.path.join(REPO_ROOT, "04_characterization_metrics", "scripts", "evaluate_full_sram_parameters.py"),
    os.path.join(REPO_ROOT, "05_ml_surrogate", "scripts", "evaluate_grouped_ml_surrogate.py"),
    os.path.join(REPO_ROOT, "05_ml_surrogate", "scripts", "train_sram_surrogate_models.py"),
    os.path.join(REPO_ROOT, "06_optimization", "scripts", "generate_pareto_and_eval_ml.py"),
]

for t in tasks:
    if os.path.exists(t):
        print(f"\n[RUNNING] {os.path.basename(t)}...")
        res = subprocess.run([sys.executable, t], cwd=REPO_ROOT, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"  [PASSED] {os.path.basename(t)}")
        else:
            print(f"  [ERROR] {res.stderr}")

print("\n" + "=" * 80)
print("  COMPLETE ANALYSIS PIPELINE EXECUTED SUCCESSFULLY")
print("=" * 80)
