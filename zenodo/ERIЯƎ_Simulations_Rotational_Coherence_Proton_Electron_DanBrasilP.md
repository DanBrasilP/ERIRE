# ERIЯƎ Simulations — Rotational Coherence in the Proton-Electron System

**Author:** DanBrasilP  
**GitHub Repository:** [https://github.com/DanBrasilP/ERIRE](https://github.com/DanBrasilP/ERIRE)  
**License:** GNU GPLv3 and CC BY-SA 4.0

---

## Overview

This report presents a consolidated analysis of two foundational computational experiments within the ERIЯƎ theoretical model—**Theoretical Expansion 19** and **20**—each exploring the rotational interaction between proton and electron beyond conventional QED and electrostatics.

The ERIЯƎ framework (Exponentialization and Rationalization of Imaginary Rotational Evolution) provides a geometric and rotational interpretation of atomic-scale interactions. These studies aim to replace the postulate of discrete quantization with a **dynamical loss of phase coherence**, manifested through **rotational projection** of the interaction space.

---

## Scope of Experiments

### Expansion 19 — ERIЯƎ Dynamic Projection Model

- Simulates the rotational coherence between proton and electron as a function of radial distance.
- Introduces the **|Z_total|** factor to represent the projectional alignment of rotational momenta.
- Calculates ERIЯƎ forces and potential energies and compares them against the classical Coulomb model and CODATA/NIST values.
- Demonstrates that when |Z_total| = 1, ERIЯƎ yields classical results; when |Z_total| ≈ 0.5, it reproduces the *experimental energy levels* precisely.

### Expansion 20 — Coherence Scaling and Quantized Levels

- Extends the simulation for excited states (n = 2 to 5).
- Derives the **radial scaling law** for coherence, where |Z_total| ∝ 1/n.
- Compares energy levels from ERIЯƎ with both Bohr’s model and measured values.
- Shows that rotational coherence decays progressively as n increases, accounting for energy quantization naturally.

---

## Key Distinctions in the ERIЯƎ Model

- **Radial Coherence vs Linear Radius:**  
  Unlike the Bohr model which treats radius as a static scalar (r ∝ n²), the ERIЯƎ model treats it as a **dynamic radial projection**, evolving geometrically and influencing the observed energy through **phase alignment**.

- **No Discrete Quantization Assumed:**  
  Quantized behavior **emerges** from coherence degradation rather than being imposed.

- **Rotational Field Geometry:**  
  The interaction is analyzed via imaginary rotational projection, not merely scalar distance. This leads to results that align with experiments while offering a different physical interpretation.

---

## Numerical Alignment Summary

| n | Radius (nm) | Classical Energy (eV) | Experimental Energy (eV) | ERIЯƎ Z_total |
|---|-------------|------------------------|---------------------------|------------------|
| 1 |  0.0529     |     -27.2114           |       -13.6057            |     ≈ 0.5000     |
| 2 |  0.212      |      -6.8028           |        -3.4014            |     ≈ 0.5000     |
| 3 |  0.476      |      -3.0235           |        -1.5117            |     ≈ 0.5000     |
| 4 |  0.847      |      -1.7007           |        -0.8504            |     ≈ 0.5000     |
| 5 |  1.323      |      -1.0885           |        -0.5442            |     ≈ 0.5000     |

---

## Core Interpretations

- The ground state coherence |Z_total| ≈ 0.5 implies that only **50% of the classical interaction energy** is effectively realized due to phase misalignment.
- Higher energy levels follow the Bohr energy law (1/n²) **without enforcing discrete transitions**, indicating that **dephasing dynamics are sufficient** to explain quantization.
- The model reinterprets potential energy as a result of **rotational deviation**, not electrostatic potential, unifying geometry and resonance in a single field structure.

---

## Access and Reproducibility

All experiment data and simulation scripts are available in the public GitHub repository:  
**[https://github.com/DanBrasilP/ERIRE](https://github.com/DanBrasilP/ERIRE)**

Explore the directory `/python/` for runnable examples of the experiments described above.

---

## Conclusions

The ERIЯƎ model provides a novel framework for understanding atomic interactions through a geometric and dynamic approach. The results presented here:

- Reproduce key physical constants and energy levels from first principles.
- Reveal quantization as a continuous outcome of coherence dynamics, rather than discrete assumptions.
- Offer a compelling basis for further development in unifying electromagnetic and gravitational interactions through rotational coherence.

---

> “It is not charge that binds the atom — it is coherence.”  
