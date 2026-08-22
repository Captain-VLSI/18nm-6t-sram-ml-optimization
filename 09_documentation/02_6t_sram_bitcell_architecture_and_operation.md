# 6T SRAM Bitcell Architecture, Operation, and Sizing Fundamentals

A **6T SRAM (6-Transistor Static Random Access Memory) bitcell** is the fundamental memory element used in static RAM arrays. It stores **1 bit of data** using **six MOS transistors** and retains the stored value as long as power is supplied without requiring periodic refresh cycles (unlike DRAM).

---

## 1. Structure of a 6T SRAM Bitcell

```text
               VDD
                |
           P1         P2
            |          |
   Q -------+          +------- QB
            |          |
           N1         N2
            |          |
           GND        GND

            |          |
           AX1        AX2
            |          |
           BL         BLB
             \        /
                WL
```

### Transistor Breakdown

| Transistor | Name | Type | Function |
| :--- | :--- | :--- | :--- |
| **P1** | Pull-Up PMOS | PMOS | Pulls storage node Q up to VDD |
| **P2** | Pull-Up PMOS | PMOS | Pulls complementary storage node QB up to VDD |
| **N1** | Pull-Down NMOS | NMOS | Pulls storage node Q down to GND (0V) |
| **N2** | Pull-Down NMOS | NMOS | Pulls complementary storage node QB down to GND (0V) |
| **AX1** | Access NMOS | NMOS | Connects node Q to Bitline (BL) when Wordline (WL) is High |
| **AX2** | Access NMOS | NMOS | Connects node QB to Bitline Bar (BLB) when Wordline (WL) is High |

- **Total Transistors:** 2 PMOS + 4 NMOS = **6 Transistors (6T)**

---

## 2. Cross-Coupled Inverter Storage Element

The core bistable storage element is formed by two CMOS inverters connected back-to-back in a positive feedback loop:

### Left Inverter (Inv1)
```text
       VDD
        |
       P1
        |
        +---- Output: Q
        |
       N1
        |
       GND

Input (Gate of P1 & N1) = QB
```

### Right Inverter (Inv2)
```text
       VDD
        |
       P2
        |
        +---- Output: QB
        |
       N2
        |
       GND

Input (Gate of P2 & N2) = Q
```

Because the output of each inverter drives the input of the other, the circuit exhibits **two stable states**:
- **State 1 (Storing '1'):** `Q = 1 (VDD)`, `QB = 0 (GND)`
- **State 2 (Storing '0'):** `Q = 0 (GND)`, `QB = 1 (VDD)`

These complementary voltage levels represent the stored digital bit.

---

## 3. Access Transistors & Wordline Control

The access NMOS transistors connect the internal storage nodes to the external bitlines:

```text
BL  ---- AX1 ---- Q
BLB ---- AX2 ---- QB
```

Both access transistor gates are driven by the **Wordline (WL)** signal:
- **WL = 0 (Low):** AX1 and AX2 are OFF. The internal storage nodes are isolated from the bitlines (Hold Mode).
- **WL = 1 (High):** AX1 and AX2 turn ON. The internal nodes connect to BL and BLB for Read or Write operations.

---

## 4. Fundamental Control Signals

| Signal | Full Name | Description |
| :--- | :--- | :--- |
| **WL** | Wordline | Row-select control signal enabling the access transistors |
| **BL** | Bitline | Column data line transferring true data |
| **BLB** | Bitline Bar | Column data line transferring complementary inverted data |
| **Q** | True Internal Node | True stored data voltage state |
| **QB** | Complementary Node | Inverted stored data voltage state |

---

## 5. Hold Operation (Data Retention)

In hold mode, the bitcell is idle and maintains data without external access.

### Operating Conditions:
- `WL = 0` (Access transistors AX1 and AX2 are fully OFF)
- `BL = Precharged / Floating (Don't Care)`
- `BLB = Precharged / Floating (Don't Care)`

### Mechanism:
Suppose the cell stores a logic '1' (`Q = VDD`, `QB = 0V`):
- Node `QB = 0V` turns PMOS `P1` ON and NMOS `N1` OFF, actively pulling node `Q` to VDD.
- Node `Q = VDD` turns PMOS `P2` OFF and NMOS `N2` ON, actively pulling node `QB` to GND.
- The two inverters continuously reinforce each other's voltage levels against subthreshold leakage currents as long as power supply VDD is maintained.

---

## 6. Read Operation

A read operation non-destructively senses the stored state by generating a small differential voltage on the bitlines.

### Step 1: Bitline Precharge
Before reading, the precharge circuit pulls both bitlines to the supply voltage:
- `BL = VDD` (e.g., 0.90 V)
- `BLB = VDD` (e.g., 0.90 V)

### Step 2: Wordline Assertion
- `WL = 1` (AX1 and AX2 turn ON).

### Step 3: Differential Discharge
Assume the stored bit is `Q = 0 (GND)` and `QB = 1 (VDD)`:
- Since node `Q` is at 0V and `BL` is at VDD, a discharge current path is established:
  `BL -> AX1 -> Q -> N1 -> GND`
- Bitline `BL` discharges downward slightly (e.g., from 0.90 V down to 0.84 V).
- Bitline `BLB` remains at VDD because node `QB` is at VDD (no voltage delta across AX2).

### Step 4: Sense Amplification
- A small differential voltage (typically Delta_V = 50 mV to 100 mV) develops between BL and BLB.
- The Sense Amplifier is triggered by the `SAEN` clock, amplifying this small differential into a full rail-to-rail digital logic output ('0').

---

## 7. Write Operation

A write operation forces new complementary data onto the bitlines to overpower the existing state of the cross-coupled inverters.

### Example: Writing a Logic '0'
1. **Drive Bitlines:** The write driver forces:
   - `BL = 0V` (GND)
   - `BLB = VDD`
2. **Assert Wordline:** `WL = 1` (AX1 and AX2 turn ON).
3. **Overpowering the Stored State:**
   - If the cell previously held a '1' (`Q = VDD, QB = 0V`), access transistor `AX1` strongly pulls node `Q` downward toward 0V through `BL`.
   - As node `Q` drops below the switching threshold of the right inverter (`P2/N2`), PMOS `P2` turns ON and pulls node `QB` up to VDD.
   - Node `QB` rising to VDD turns NMOS `N1` ON and PMOS `P1` OFF, latching the new state:
     `Q -> 0`, `QB -> 1`
4. **De-assert Wordline:** `WL = 0` (The cell isolates and holds the new value).

---

## 8. Why Use Differential Bitlines (BL and BLB)?

1. **High Speed:** Small voltage swings (50–100 mV) can be detected immediately by differential sense amplifiers without waiting for full rail-to-rail bitline discharge.
2. **Common-Mode Noise Rejection:** Noise coupled simultaneously to both adjacent bitlines (supply bounce, substrate noise) is cancelled out by differential sensing.
3. **Lower Dynamic Power:** Discharging bitlines by only 50–100 mV consumes significantly less dynamic power than full 0-to-VDD swings.

---

## 9. Transistor Sizing Trade-Offs & Ratios

To ensure both non-destructive reads and reliable writes, relative transistor strengths must be carefully balanced:

```text
========================================================================================
CLASSICAL SIZING RULES:
  1. Read Stability  : PD must be stronger than AX (Cell Ratio CR = PD / AX >= 1.0)
     Prevents node Q from bumping above threshold during read access.
  2. Write Stability : AX must be stronger than PU (Pull-up Ratio PR = PU / AX <= 1.0)
     Allows AX to overpower PU when pulling node Q to 0V during write.
========================================================================================
```

- **Cell Ratio (CR = PD / AX):** Governs Read Static Noise Margin (RSNM). Higher CR increases read stability.
- **Pull-Up Ratio (PR = PU / AX):** Governs Write Static Noise Margin (WSNM). Lower PR makes writing easier.

---

## 10. Summary Table of Operations

| Operation | Wordline (WL) | Bitline (BL) | Bitline Bar (BLB) | Internal Storage Node Behavior |
| :--- | :---: | :---: | :---: | :--- |
| **Hold** | 0 | Don't Care | Don't Care | Cross-coupled inverters actively retain stored state |
| **Read** | 1 | Precharged (VDD) | Precharged (VDD) | Node holding '0' creates differential delta on bitline |
| **Write 0** | 1 | 0 V (GND) | VDD | BL forces node Q to 0, latching cell into '0' |
| **Write 1** | 1 | VDD | 0 V (GND) | BLB forces node QB to 0, latching cell into '1' |
