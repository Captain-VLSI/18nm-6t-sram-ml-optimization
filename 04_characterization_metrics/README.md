# 04. Mathematical Formulations & Circuit Physics Handbook

This document provides the foundational circuit physics, FinFET device equations, extraction algorithms, and machine learning mathematical formulations used across the 18nm 6T SRAM optimization framework.

---

## 1. 6T SRAM Bitcell Operation Physics & Sizing Rules

A standard 6T SRAM cell stores a single binary bit using two cross-coupled inverters (P1/N1 and P2/N2) forming a bistable latch, accessed via two pass-gate access transistors (AX1, AX2) controlled by the Wordline (WL).

### Operational Modes:
1. **Hold Mode (WL = 0V):**
   - Access transistors are OFF (quiescent state).
   - The cross-coupled inverters continuously regenerate the stored logical values (`Q` and `QB`) against subthreshold leakage currents.

2. **Read Mode (WL = VDD, BL = BLB = VDD):**
   - Both Bitline (BL) and Bitline-Bar (BLB) are precharged to VDD.
   - When WL rises to VDD, the access transistor connected to the '0' node turns ON and forms a resistive voltage divider between the Access NMOS and Pull-Down NMOS.
   - Current flows from the precharged bitline through AX and PD to ground, discharging the bitline.
   - The node holding '0' rises to a bump voltage: `V_bump = VDD * (R_PD / (R_PD + R_ACC))`.

3. **Write Mode (WL = VDD, BL = 0V, BLB = VDD):**
   - To overwrite stored data '1' to '0', BL is pulled to GND and WL is pulsed HIGH.
   - The access transistor AX1 overpowers the Pull-Up PMOS P1, pulling node Q below the switching threshold of inverter 2 (P2/N2), triggering regenerative latch flipping.

### Critical Sizing Ratios:
- **Cell Ratio (CR - Read Stability Condition):**
  `CR = N_fin,PD / N_fin,ACC >= 1.0`  
  Ensures the pull-down NMOS is stronger than the access NMOS, keeping the read disturb voltage `V_bump` below the inverter switching threshold ($V_{th}$) to prevent destructive read flips.

- **Pull-Up Ratio (PR - Writeability Condition):**
  `PR = N_fin,PU / N_fin,ACC <= 1.5`  
  Ensures the access NMOS is strong enough to overpower the pull-up PMOS and force node Q low during write operations.

---

## 2. 18nm Tri-Gate FinFET Device Physics

In planar CMOS, short-channel effects (SCE) cause severe subthreshold leakage as gate length scales below 20nm. Tri-Gate FinFETs solve this by wrapping the gate around a thin 3D vertical silicon fin on three sides (top and two sidewalls).

### Effective Channel Width Quantization:
Because the silicon fin is 3D, the conductive channel width per fin is determined by the fin height ($H_{\text{fin}}$) and fin thickness ($T_{\text{fin}}$):
`W_eff,per_fin = 2 * H_fin + T_fin`

For a multi-fin transistor with `N_fin` parallel fins:
`W_total = N_fin * (2 * H_fin + T_fin)`
- Unlike planar CMOS where width $W$ is continuous, **FinFET width is strictly quantized to integer multiples of fins** ($N_{\text{fin}} = 1, 2, 3, \dots$).

### Electrostatic Advantages in 18nm:
1. **Subthreshold Swing Suppression:**  
   $S = (k_B T / q) * \ln(10) * (1 + C_d / C_{ox}) \approx 68\text{ mV/decade}$ (near ideal limit of 60 mV/dec at 27°C, compared to > 90 mV/dec in planar).
2. **DIBL Suppression:** Drain-Induced Barrier Lowering is heavily suppressed due to superior gate electrostatic control.
3. **Threshold Voltage Roll-off Immunity:** Stable $V_{th}$ across nominal channel lengths ($L = 18\text{nm}$).

---

## 3. Static Noise Margin (SNM) Formulations

The Static Noise Margin represents the maximum DC noise voltage that can be tolerated at the internal storage nodes before a state flip occurs.

### Seevinck Rotated Coordinate Method (HSNM & RSNM):
Standard butterfly plots overlay the Voltage Transfer Curve of Inverter 1 ($V_{QB} = f(V_Q)$) and the mirrored curve of Inverter 2 ($V_Q = f(V_{QB})$).

To find the maximum square that fits within the butterfly lobes, the coordinate axes are rotated by 45 degrees:
1. **Coordinate Transformation:**
   `u = (V_Q - V_QB) / sqrt(2)`
   `v = (V_Q + V_QB) / sqrt(2)`

2. **Diagonal Distance Function:**
   `d(u) = (1 / sqrt(2)) * [ v_inv1(u) - v_inv2(u) ]`

3. **Maximum Inscribed Square Extraction:**
   `SNM = max_{u} [ d(u) ]`
   - **Hold SNM (HSNM):** Evaluated with access transistors OFF (`WL = 0V`).
   - **Read SNM (RSNM):** Evaluated with access transistors ON (`WL = VDD, BL = BLB = VDD`).

### Write Trip Point (WTP) & Write Noise Margin (WNM):
Write noise margins are measured by sweeping the write bitline voltage from VDD down to 0V while monitoring internal nodes Q and QB.

1. **Write Trip Point (WTP / V_trip):**
   The bitline voltage at which internal node voltages cross each other:
   `V_trip = V_BL | (V_Q(V_BL) = V_QB(V_BL))`
   - A higher WTP indicates easier and more robust writeability.

2. **Write Noise Margin (WNM):**
   The voltage difference between the internal peak node voltage and the trip point:
   `WNM = max_{V_BL >= V_trip} (V_QB(V_BL)) - V_trip`

---

## 4. Dynamic Timing, Energy & Leakage Formulations

### 1. 50%-to-50% Wordline-to-Node Switching Delay (T_write):
The propagation delay is measured from the 50% voltage level of the rising Wordline pulse to the 50% voltage crossing of the internal node:
- For Write-0 ($Q \to 0$):  
  `T_write0 = t(V_Q = 0.5 * VDD) - t(V_WL = 0.5 * VDD)`
- For Write-1 ($QB \to 0$):  
  `T_write1 = t(V_QB = 0.5 * VDD) - t(V_WL = 0.5 * VDD)`
- **Worst Write Delay:**  
  `Worst_Write_Delay = max(T_write0, T_write1)`

### 2. Dynamic Read Disturb Bump (Delta V_Q):
During read access, capacitive and resistive bitline coupling causes a transient voltage bump on the node holding '0':
`Delta V_Q = max_{t} [ V_Q(t) ] - 0.0`
- To maintain read non-destructiveness, `Delta V_Q < V_th,N2`.

### 3. Dynamic Energy Integration (E_write & E_read):
The total dynamic energy dissipated per operation is obtained by numerical trapezoidal integration of the instantaneous supply current $I_{\text{VDD}}(t)$ over the active switching window:
`E_dynamic = integral_{t_start}^{t_end} VDD * I_VDD(t) dt`

### 4. Standby Quiescent Leakage & Power (I_leak & P_leak):
In standby hold mode (WL = 0V), static leakage arises from subthreshold drain-source conduction and gate-dielectric tunneling:
- **Average Leakage Current:**  
  `I_leak = (1 / T) * integral_{0}^{T} I_VDD,hold(t) dt`
- **Static Standby Power:**  
  `P_leak = VDD * I_leak`

---

## 5. Machine Learning Surrogate Modeling Mathematics

ML surrogates replace expensive numerical SPICE differential equation solvers with fast mathematical mapping functions:  
`y = f(x)` where `x = [VDD, N_fin,PU, N_fin,PD, N_fin,ACC, CR, PR]`.

### 1. Random Forest Regressor (Bagging & Variance Reduction):
An ensemble of $B$ deep decision trees grown on bootstrap resamples:
`y_hat_RF = (1 / B) * sum_{b=1}^{B} T_b(x)`
- Reduces variance without increasing bias, highly robust against input noise and local fluctuations.

### 2. Gradient Boosted Decision Trees (Sequential Residual Fitting):
Iteratively builds shallow decision trees $h_m(x)$ to minimize a mean squared error loss function:
`f_m(x) = f_{m-1}(x) + eta * h_m(x)`
- Where $\eta = 0.08$ is the shrinkage learning rate.
- Excels at fitting smooth, continuous non-linear physical functions (e.g. read access energy, static power).

### 3. Model Performance Metrics:
- **Mean Absolute Error (MAE):**
  `MAE = (1 / N) * sum_{i=1}^{N} | y_i - y_hat_i |`
- **Root Mean Squared Error (RMSE):**
  `RMSE = sqrt( (1 / N) * sum_{i=1}^{N} (y_i - y_hat_i)^2 )`
- **Coefficient of Determination (R2 Score):**
  `R2 = 1 - [ sum_{i=1}^{N} (y_i - y_hat_i)^2 / sum_{i=1}^{N} (y_i - y_mean)^2 ]`
  - $R^2 = 1.0$ indicates perfect prediction.

### 4. Grouped Unseen-Geometry Generalization Protocol:
Rather than standard random row splitting (which leaks voltage-interpolated points of the same bitcell), samples are split using `GroupShuffleSplit`:
- **Grouping Variable:** `geom_id = (PU, PD, ACC)`
- **80% Training Geometries:** 120 bitcell geometries across all 8 voltages (960 samples).
- **20% Held-Out Test Geometries:** 30 complete physical bitcell geometries never seen during training (240 test samples).
