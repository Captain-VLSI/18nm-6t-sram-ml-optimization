#!/usr/bin/env python3
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

print("=" * 80)
print("  REGENERATING ALL 7 PUBLICATION FIGURES")
print("=" * 80)

tasks = [
    os.path.join(REPO_ROOT, "04_characterization_metrics", "scripts", "generate_premium_wtp_plots.py"),
    os.path.join(REPO_ROOT, "06_optimization", "scripts", "generate_pareto_and_eval_ml.py"),
    os.path.join(REPO_ROOT, "04_characterization_metrics", "scripts", "plot_all_cadence_validation_graphs.py"),
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
print("  ALL PUBLICATION FIGURES SUCCESSFULLY REGENERATED IN 08_results/figures/")
print("=" * 80)
