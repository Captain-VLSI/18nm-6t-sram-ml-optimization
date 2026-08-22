# 07. Cadence Spectre Independent Verification

This directory contains the closed-loop independent verification workbook, golden templates, and statistical parity audits.

---

## Verification Protocols & Acceptance Criteria:
- **Individual Test Threshold:** Absolute percentage error for every single test case must be `< 1.0%`.
- **Global Accuracy Criterion:** Mean absolute error across all 24 verification test cases must be `< 0.3%`.
- **Result:** **24/24 Test Cases PASSED** (Mean Absolute Error = 0.16%).

---

## Files in this Directory:
- [`CADENCE_SPECTRE_VERIFICATION_SHEET.xlsx`](CADENCE_SPECTRE_VERIFICATION_SHEET.xlsx): Complete verification workbook comparing expected baseline vs measured Cadence Spectre simulation values.
- [`CADENCE_GOLDEN_VERIFICATION_TEMPLATE.csv`](CADENCE_GOLDEN_VERIFICATION_TEMPLATE.csv): CSV template of golden verification metrics across the 4 bitcells.
- [`full_sram_parameters_ml_audit.csv`](full_sram_parameters_ml_audit.csv): Full 5-category parameter extraction audit comparing Unseen Geometry $R^2$ vs Voltage Interpolation $R^2$.
