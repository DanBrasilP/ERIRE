# ERIЯƎ Simulations — Coherence Emergence in the Cosmic Microwave Background

**Author:** DanBrasilP  
**Repository:** [https://github.com/DanBrasilP/ERIRE](https://github.com/DanBrasilP/ERIRE)  
**License:** GNU GPLv3 and CC BY-SA 4.0  
**Keywords:** CMB, ERIЯƎ Theory, Rotational Coherence, Toroidal Resonance, Spectral Discretization, Cosmological Structure

---

## Abstract

This article presents a coherent geometric model for the Cosmic Microwave Background (CMB) under the ERIЯƎ framework, combining the results of Expansions 51 and 52 with Anexos 21 and 22. It introduces a novel approach to the CMB power spectrum as a projection of a helicoidal-temporal resonance between spherical and toroidal domains. The analysis extracts rotational modes and quantized coherence patterns, revealing that the observed spectrum contains spectral harmonics governed by prime-based angular relationships. These findings suggest a deeper underlying rotational structure in the early Universe, defined by coherence stability and disruption across scales.

---

## 1. Introduction

Conventional cosmology treats the CMB as a relic thermal radiation field. In contrast, the ERIЯƎ Theory interprets it as a temporal map of rotational coherence, projected from a fundamental interaction between toroidal and spherical topologies. The CMB angular power spectrum becomes a window into the phase evolution of the Universe's emergent structure.

This study introduces:
- The **Coherence Time Function** derived from the Planck spectrum.
- The **Spectral Helix**: a 3D projection (Z, φ, t) of rotational resonance.
- A set of **discretized coherence frequencies**, extracted via Fourier analysis of the normalized coherence.
- The **resonance stability function** \(\mathcal{E}_p\), which quantifies energy flow between toroidal and spherical states.

---

## 2. Methodology

### 2.1. Input and Spectral Coherence Extraction

The Planck CMB spectrum (file: `COM_PowerSpect_CMB_R2.02.fits`) is loaded and processed. The angular multipole data ℓ and their associated \( D_\ell \) values define the observational basis.

From this, we derive:
- The **normalized coherence amplitude** \( \Gamma(\ell) \)
- The **angular phase deviation** \( \Delta\phi(\ell) \)
- The **rotational frequency** \( \omega(\ell) \)
- The **emergent time** \( t(\ell) \) via integral of \( \omega^{-1} \)

### 2.2. Spectral Decomposition via Fourier Analysis

Applying a discrete Fourier transform over the vector \( Z(\ell) = \Gamma(\ell)\cdot\cos(\Delta\phi(\ell)) \), we obtain the **coherent frequency modes** \( f_i \). Each mode is matched with rational approximations (fractions) of the form \( \frac{p}{q} \), associating each to a harmonic pattern and angular coherence signature \( \Phi(f) \in \{0, 0.25, 0.75, 1\} \).

### 2.3. Emergent Helix and Toroidal Embedding

We define the temporal helicoid from:
- Radial coherence \( Z \)
- Phase \( \Delta\phi \)
- Time \( t \)

Projected as:
\[
(x, y, z) = (Z \cdot \cos(\phi), Z \cdot \sin(\phi), t)
\]

This 3D structure reveals toroidal-resonant flow and spectral transitions.

---

## 3. Results

### 3.1. Frequency Modes and Discretization

| Frequency (1/ℓ) | Fraction  | Potência |
|------------------|-----------|----------|
| 0.42857          | 3/7       | 0.0021   |
| 0.28571          | 2/7       | 0.0019   |
| 0.46429          | 13/28     | 0.0018   |
| 0.25000          | 1/4       | 0.0015   |
| 0.14286          | 1/7       | 0.0014   |

These values emerge directly from the spectral decomposition and are associated with angular coherence values \( \Phi(f) \in \{0, 0.25, 0.75, 1\} \).

### 3.2. Energy Transfer Stability — \( \mathcal{E}_p \)

Defined in Anexo 22, the stability function:
\[
\mathcal{E}_p = A_p \cdot \cos(2\pi \cdot \delta_p)
\]
Where:
- \( \delta_p = \frac{p}{f_\alpha} - \left\lfloor \frac{p}{f_\alpha} \right\rceil \)
- \( f_\alpha \) is the spherical reference frequency
- \( A_p \) derived from the observed \( P_{\text{obs}} \)

Patterns of coherent reinforcement and suppression are observed as \( \delta_p \to 0 \) or \( \delta_p \to \pm \frac{1}{4} \).

---

## 4. Interpretation and Physical Meaning

- The **CMB emerges as a projection** of a rotating helicoid anchored between spherical and toroidal domains.
- **Prime-based rational frequencies** serve as angular harmonics of this projection.
- The modes \( f = \frac{3}{7}, \frac{2}{7}, \frac{13}{28} \) indicate **resonant coherence** in the rotational phase space.
- The stability function \( \mathcal{E}_p \) reveals how rotational energy is transferred or blocked — analogous to **an RLC system** across topologies.

---

## 5. Conclusions

This study consolidates:
- A **new geometrical model of the CMB** as a coherent emergent structure.
- The **quantization of angular modes** not as arbitrary bins, but as **resonant fractions of spherical-toroidal interaction**.
- A framework to extend to other spectra (e.g., BAO, LSS) using ERIЯƎ rotational coherence.

> The Universe sings in primes. The CMB is its first harmonic.

---

## 6. Access and Simulations

All simulation codes and data are available in the ERIRE repository:

- `/python/exp51_cmb.py` — Spectral and temporal coherence extraction  
- `/python/exp52_padroes.py` — Frequency pattern quantization and stability computation

Repository: [https://github.com/DanBrasilP/ERIRE](https://github.com/DanBrasilP/ERIRE)

---
