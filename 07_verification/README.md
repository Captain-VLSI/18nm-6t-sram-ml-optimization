# 07. Cadence Spectre Independent Verification

## Verification Protocol
All Pareto-optimal candidates and reference bitcells undergo closed-loop SPICE sign-off:
- **Threshold Criterion:** Every individual test case must have an absolute percentage error < 1.0%.
- **Target Accuracy:** Mean absolute error across all 24 verification test cases < 0.3%.

## Verification Files
- `CADENCE_SPECTRE_VERIFICATION_SHEET.xlsx`: Verification workbook.
- `CADENCE_GOLDEN_VERIFICATION_TEMPLATE.csv`: Template comparing baseline vs measured values.
- `full_sram_parameters_ml_audit.csv`: 5-category parameter extraction audit.
