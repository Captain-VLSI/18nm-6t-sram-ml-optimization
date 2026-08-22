# 04. Characterization Metrics & Mathematical Formulations

## Mathematical Definitions

### 1. Seevinck Rotated Coordinate Static Noise Margin (SNM)
`u = (V_Q - V_QB) / sqrt(2)`
`v = (V_Q + V_QB) / sqrt(2)`
`SNM = max_{u} [ (1/sqrt(2)) * (v_inv1(u) - v_inv2(u)) ]`

### 2. Write Trip Point (WTP) & Write Noise Margin (WNM)
`V_trip = V_BL | (V_Q(V_BL) = V_QB(V_BL))`
`WNM = max_{V_BL >= V_trip} (V_QB(V_BL)) - V_trip`

### 3. 50%-to-50% Write Switching Delay (T_write)
`T_write = t(V_Q = 0.5 * VDD) - t(V_WL = 0.5 * VDD)`

### 4. Dynamic Write Energy Integration
`E_write = integral_{t_start}^{t_end} VDD * I_VDD(t) dt`

### 5. Standby Static Leakage & Power
`I_leak = (1 / T) * integral_{0}^{T} I_VDD,hold(t) dt`
`P_leak = VDD * I_leak`
