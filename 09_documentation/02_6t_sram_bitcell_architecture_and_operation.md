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
- `BL = VDD`
- `BLB = VDD`

### Step 2: Wordline Assertion
- `WL = 1 (VDD)` (Access transistors AX1 and AX2 turn ON).

### Step 3: Circuit Physics of Read Disturb (Why Node Q Rises)
Assume the cell stores a logic '0' at node Q (`Q = 0V`) and '1' at node QB (`QB = VDD`).

When WL is asserted:
- **Gate terminal:** `WL = VDD` -> Transistor turns ON.
- **Drain/Source terminal 1:** Connected to precharged bitline `BL = VDD`.
- **Drain/Source terminal 2:** Connected to internal node `Q = initially 0V`.

Therefore:
```text
V_GS,AX = VDD - 0 = VDD
```
So the access NMOS strongly conducts.

Because BL is at a higher potential (VDD) than Q (0V), conventional current flows from the precharged bitline into internal node Q:
```text
BL -> AX1 -> Q
```
This current charges the internal parasitic node capacitance at Q ($C_Q$), causing the voltage at node Q to rise:
```text
Q: 0V -> some positive voltage (Read Disturb Bump)
```

#### Is the Access Transistor in Saturation?
**Initially, yes.**

For NMOS saturation:
```text
V_DS >= V_GS - V_T
```
At the exact moment of wordline activation ($t = 0^+$):
- `V_BL = VDD`
- `V_Q ~ 0V`

Therefore:
```text
V_DS,AX = VDD - 0 = VDD
V_GS,AX = VDD - 0 = VDD
```
The saturation condition is:
```text
VDD >= VDD - V_T  (which is always TRUE)
```
So initially, the access transistor AX operates in the **saturation region**.

#### What Happens as Node Q Rises?
As AX supplies current to charge node Q, voltage $V_Q$ increases ($Q \uparrow$):
- `V_DS,AX = VDD - V_Q`
- `V_GS,AX = VDD - V_Q` (with the source defined at the lower-potential Q node)

As $V_Q$ rises, $V_{DS,AX}$ and $V_{GS,AX}$ both decrease, and the operating region of AX can transition toward the linear/triode region.

**Key Insight:** AX does not raise Q simply because it is in saturation; it raises Q because it is ON and provides a low-resistance conductive path from the precharged bitline (VDD) to node Q, injecting charge into the Q-node capacitance.

### Step 4: The Voltage Divider & Fighting Transistors
This is the core stability mechanism in 6T SRAM bitcells:

As node Q rises ($Q \uparrow$), the Pull-Down NMOS (N1) connected between Q and GND also sees its gate voltage (held at $QB = VDD$) and drain voltage ($V_Q$) conducting current:
```text
BL -> AX1 -> Q -> N1 -> GND
```
Two transistors are actively fighting over node Q:
1. **Access NMOS (AX1):** Pulls current from precharged BL (VDD), trying to raise $V_Q$.
2. **Pull-Down NMOS (N1):** Sinks current to GND, trying to keep $V_Q$ at 0V.

The peak disturb voltage reached at node Q represents a resistive voltage divider between AX1 and N1:
```text
V_Q,bump ~ VDD * [ R_N1 / (R_N1 + R_AX1) ]
```

To prevent a **destructive read flip**, the voltage bump at node Q must remain safely below the switching threshold ($V_{th,N2}$) of the opposite inverter:
```text
V_Q,bump < V_th,N2
```
This is why the **Cell Ratio (CR = W_PD / W_AX = Nfin,PD / Nfin,ACC >= 1.0)** is strictly enforced: the Pull-Down NMOS must be wider/stronger than the Access NMOS so that $R_{N1} \ll R_{AX1}$, keeping $V_Q$ clamped near ground.

### Step 5: Sense Amplification
- Current continuing through `BL -> AX1 -> N1 -> GND` discharges the bitline capacitance ($C_{BL}$), pulling BL down slightly below VDD.
- Meanwhile, bitline BLB remains fully at VDD because node QB is at VDD (no voltage difference across AX2).
- A small differential voltage ($\Delta V_{BL} = 50\text{ mV to } 100\text{ mV}$) develops between BL and BLB.
- The Sense Amplifier is triggered by `SAEN`, amplifying this differential delta into a full rail-to-rail logic '0' output without waiting for full bitline discharge.

---

## 🎯 Interview-Quality Question & Answer (ARM Memory Design)

**Question:** *"Why does the access transistor increase node Q during a read operation, and what determines bitcell stability?"*

**Answer:**
> "During a read operation, both bitlines are precharged to VDD while node Q stores a logic 0 (0V). When the wordline is asserted to VDD, the access NMOS turns on with V_GS = VDD and creates a low-impedance conductive path between BL and Q. The resulting potential difference drives current from BL toward Q, charging the parasitic capacitance at node Q and causing its voltage to rise—this is the dynamic read disturb bump. 
> 
> Initially, because V_DS = VDD and V_GS = VDD, the access transistor operates in saturation (V_DS >= V_GS - V_T), though its operating point shifts as Q rises. Simultaneously, the pull-down NMOS conducts to sink this current to ground. The bitcell essentially forms a resistive voltage divider between the access transistor and the pull-down transistor (BL -> AX -> Q -> PD -> GND). 
> 
> To ensure non-destructive read stability, the cell ratio (CR = W_PD / W_AX) is sized greater than 1.0, ensuring the pull-down device is sufficiently stronger than the access device to clamp the peak Q disturb voltage well below the switching threshold of the opposing cross-coupled inverter."


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
