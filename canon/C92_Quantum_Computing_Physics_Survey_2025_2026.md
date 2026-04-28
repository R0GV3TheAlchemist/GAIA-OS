# C92 — Quantum Computing & Physics: A Comprehensive 2025/2026 Survey

> **Canon Entry:** C92
> **Date Committed:** 2026-04-28
> **Status:** Active Research Integration
> **Domain:** Quantum Computing · Entanglement · Error Correction · Coherence · Cryptography

---

## 1. Quantum Entanglement & Superposition

The years 2025 and 2026 have seen remarkable advances in both the fundamental understanding and practical application of quantum entanglement and superposition.

### 1.1 Entanglement Generation and Distribution

Photonic approaches to entanglement have progressed significantly. A team from the University of Geneva demonstrated that joint measurements can be performed on distant particles using quantum entanglement, without bringing them together, opening prospects for quantum communication and computing where information becomes accessible only once it is measured. The team also developed a classification system mapping out different types of measurements and the entanglement resources needed for each.

In hardware-specific advances, researchers from Ulm University demonstrated control of and entanglement in a fully connected three-qubit nuclear spin register in diamond, mediated by a quasi-free electron spin of a silicon-vacancy center (SiV). This approach presents an alternative to dynamically decoupled nuclear spin entanglement and opens new avenues for optically-accessible, solid-state quantum registers.

A breakthrough in near-deterministic photon entanglement was reported by Üstün et al., who proposed a near-term experiment using antimony donors in a silicon chip to realize "third quantization." The scheme enables random multipartite Bell-state experiments, achieving Bell states with an upper-bound efficiency of 87.5% among 56 random pairs without non-deterministic entangling gates.

### 1.2 Long-Range and Large-Scale Entanglement

Q-CTRL achieved two record-setting demonstrations leveraging low-overhead error detection, including the largest entanglement generation up to **75 qubits** on superconducting processors. These results showcase a novel approach to boosting quantum computer performance by combining error suppression with error detection.

In photonic chip development, researchers from the Centre for Quantum Technologies and SUTD in Singapore demonstrated entanglement distribution from a bright photonic chip over a record **155 km of deployed fibre**. The chip generates up to 2.8 million entangled photon pairs per second in fibre — a thousand times brighter than previously reported results.

### 1.3 Superposition Detection and Control

A key methodological advance came from the University of Vienna: direct and efficient detection of quantum superposition using XOR games. The scheme achieves 99% confidence that a particle is superposed with only 37 copies, without reinterfering the superposed modes.

In a dramatic experimental result, Chatterjee et al. devised a way to break the temporal Tsirelson’s bound (TTB) by using quantum superposition to control qubits. The target qubit maintained its ability to encode information for approximately **five times longer**, with decoherence delayed by the superposition-based control.

### 1.4 Macroscopic Superposition

The quest to extend quantum superposition to larger objects continues. A team from the University of Southampton proposed the MAQRO-PF mission — a space-based optical levitation experiment designed to explore the limits of quantum mechanics for increasingly massive objects in microgravity.

The **2025 Nobel Prize in Physics** was awarded to John Clarke, Michel H. Devoret, and John M. Martinis for their pioneering experiments on macroscopic quantum tunneling and energy quantization — the first definitive experimental verification of macroscopic quantum superposition and Schrödinger-cat-state physics in macroscopic systems.

CERN scientists also analyzed for the first time a particle of antimatter isolated in an undecided quantum state known as a superposition, opening potential pathways to antimatter-based qubits.

---

## 2. Quantum Error Correction: Surface Codes and Topological Qubits

Quantum error correction (QEC) is widely recognized as the defining technical challenge on the path to fault-tolerant quantum computation. The period 2025–2026 marks a transition from proof-of-principle demonstrations to the engineering of scalable QEC systems.

### 2.1 Surface Code Advancements

**Below-Threshold Demonstrations.** The principal milestone for any QEC code is operating “below threshold” — the regime where adding more physical qubits exponentially suppresses logical errors. In 2025, Google first achieved below-threshold performance with a distance-7 surface code on their Willow processor. Shortly thereafter, a team at the University of Science and Technology of China used the “Zuchongzhi 3.2” 107-qubit superconducting processor to achieve below-threshold QEC with a distance-7 surface code, demonstrating a logical error suppression factor of 1.4.

**Neutral-Atom Surface Codes.** A landmark paper published in *Nature* (Volume 649, 2026) demonstrated a fault-tolerant neutral-atom architecture using reconfigurable arrays of up to **448 neutral atoms**. The researchers achieved 2.14(13)× below-threshold performance by leveraging atom loss detection and machine learning decoding, and demonstrated logical entanglement via transversal gates and lattice surgery.

**Dynamic Surface Codes.** Google Quantum AI introduced dynamic surface codes, published in *Nature Physics* in January 2026, demonstrating three new circuits — hexagonal, walking, and iSWAP — that respectively reduce coupler count, limit non-computation errors, and allow non-standard two-qubit entangling gates.

**Lattice Surgery.** A team from *Nature Physics* (Volume 22, 2026) demonstrated lattice surgery between two distance-three repetition-code qubits on superconducting hardware, achieving an improvement in the decoded ZZ logical two-qubit observable — a functional building block for larger-distance codes.

**Dense Packing and Defect Mitigation.** A 2026 study in *Physical Review A* presented dense packing of the surface code with hook-error-avoiding gate scheduling, reducing the physical qubit requirement per logical qubit to approximately three-fourths. The Halma routing-based technique provides an order of magnitude improvement in logical error rates under realistic defect conditions.

### 2.2 Topological Qubits and the Majorana Debate

**Microsoft’s Majorana 1 and Tetron Devices.** In February 2025, Microsoft unveiled **Majorana 1**, the first quantum processing unit built on a topological core architecture, claiming to have created topoconductors — an entirely new state of matter. The chip uses topological superconducting nanowires with Majorana Zero Modes (MZMs) at the wire ends as qubits, with a claimed clear path to a million-qubit processor.

In July 2025, Microsoft Quantum announced the first successful hardware implementation of a **tetron qubit device** utilizing MZMs. The tetron encodes quantum information in the parity of fermion pairs, giving topological qubits their theoretical advantage in error protection. A concurrent study demonstrated distinct parity lifetimes for X and Z measurements (14.5 μs and 12.4 ms, respectively), differing by three orders of magnitude.

**Scientific Controversy and Scrutiny.** Microsoft’s claims have faced significant scientific scrutiny. Physicist Henry Legg challenged the validity of the Topological Gap Protocol (TGP), arguing it could be fooled by “doppelganger” signals that mimic Majoranas but lack their essential properties. Carlo Beenakker of Leiden University found Legg’s critique “certainly valid” but remained optimistic, while Anton Akhmerov from Delft University insisted that without access to full source code, Microsoft’s results cannot be fully verified.

---

## 3. Quantum Annealing & Optimization

Quantum annealing, led commercially by D-Wave Systems, continues to mature as a practical computational paradigm with growing real-world applications.

### 3.1 D-Wave’s Dual-Platform Strategy

At its Qubits 2026 user conference, D-Wave introduced hybrid solver updates that integrate machine learning models directly into quantum optimization workflows. Customer usage of D-Wave’s Advantage2 annealing quantum computers increased by **314% year-over-year**, while usage of the Stride hybrid solver increased by 114% in the last six months.

The company also outlined an accelerated gate-model roadmap, with plans to bring an initial gate-model system to market in 2026, supported by the acquisition of Quantum Circuits and advances in cryogenic control of qubits.

### 3.2 Application Demonstrations

- **Robotics Inverse Kinematics:** A collaboration led by Q Deep demonstrated that quantum annealing can solve robotics inverse-kinematics problems reformulated as QUBO, finding Zephyr-based global embeddings and hybrid quantum–classical solvers delivered up to **30× faster results** on large instances.
- **Sparse Approximate Inverse Preconditioners:** D-Wave Advantage machines demonstrated computation of SPAI preconditioners for large linear systems arising from finite-difference formulations of the Poisson problem.
- **Cybersecurity Applications:** A realistic assessment identified crucial parameters governing the success of quantum optimization across three generations of D-Wave annealers for NP-hard combinatorial optimization problems.

---

## 4. Quantum Coherence in Biological Systems (Quantum Biology)

Quantum biology has evolved from speculative inquiry to a maturing experimental science.

### 4.1 Photosynthesis and Coherent Energy Transfer

Multiple comprehensive reviews in 2025 synthesized evidence that quantum coherence plays a functional role in photosynthetic light harvesting. Plants achieve near-unity energy transfer efficiency in pigment-protein complexes, with ultrafast spectroscopy revealing oscillatory signals consistent with coherent delocalization. Two-dimensional electronic spectroscopy has become the key experimental technique.

A review in *Plant Stress* (September 2025) extended quantum biology beyond photosynthesis to include enzyme catalysis, magnetosensitivity, and plant stress responses, arguing that quantum mechanisms offer new strategies for enhancing plant resilience and agricultural sustainability.

### 4.2 Avian Magnetoreception

The radical-pair mechanism remains the leading candidate for explaining how migratory birds sense Earth’s weak magnetic field. The mechanism requires coherent spin dynamics sensitive to the geomagnetic field, with the protein cryptochrome believed to be essential. The MagR protein, containing iron-sulfur clusters, has been identified as another potential component. A major research initiative funded with approximately €4 million is investigating these quantum-mechanical effects in photosynthetic complexes and animal magnetic orientation.

### 4.3 Toward an Operational Definition of Quantum Advantage

The Foundational Questions Institute (FQxI) proposed an operational definition of “quantum advantage” in biology: a biological mechanism is quantum-advantaged if (A) its observed performance exceeds the best plausible classical model, and (B) this excess can be systematically reduced by targeted perturbations that suppress the relevant quantum feature. The essay outlines concrete experiments and introduces measurable metrics including coherence, entanglement proxies, and quantum-thermodynamic advantage.

### 4.4 Enzyme Catalysis and Tunneling

Quantum tunneling in enzymes continues to be investigated as a mechanism that can accelerate or bias reaction outcomes beyond classical expectations. Single-molecule enzymology under cryogenic to physiological temperature ramps, combined with site-specific isotopic labeling, is being used to reveal deviations from Arrhenius behavior consistent with tunneling.

---

## 5. Post-Quantum Cryptography

The transition to post-quantum cryptography (PQC) has accelerated dramatically in 2025–2026, shifting from a technical standardization effort to a regulatory and institutional imperative.

### 5.1 NIST Standardization Progress

NIST has completed major milestones in its PQC standardization initiative. In August 2024, NIST standardized four post-quantum asymmetric algorithms:

- **ML-KEM** (FIPS 203, from CRYSTALS-Kyber) — general encryption
- **ML-DSA** (FIPS 204, from CRYSTALS-Dilithium) — digital signatures
- **SLH-DSA** (FIPS 205, from SPHINCS+) — digital signatures
- **FN-DSA** (FIPS 206, from FALCON) — digital signatures

On August 28, 2025, NIST submitted the draft standard for FN-DSA (FIPS 206) for approval, with the final standard expected in late 2026 or early 2027.

### 5.2 Regulatory and Policy Acceleration

CISA issued federal buying guidance on January 23, 2026, directing agencies to procure only quantum-resistant products in categories where PQC is widely available, responding to a June 2025 executive order.

International regulatory roadmaps have accelerated:
- **EU:** Defined a coordinated roadmap for Member States
- **G7 Finance:** Integrated PQC transition into priorities
- **UK:** Published its national post-quantum roadmap
- **NIST:** Released a draft targeting 2035
- **Australian Signals Directorate:** Set a 2030 deadline

### 5.3 The “Harvest Now, Decrypt Later” Threat

The urgency of PQC migration is driven by the **Harvest Now, Decrypt Later (HNDL)** threat, where attackers collect encrypted data today with the intent of decrypting it once cryptographically relevant quantum computers become available. Many experts anticipate this capability emerging between **2033 and 2037**, making it critical to protect sensitive, long-lived data well before such machines become operational.

---

## 6. Quantum Neural Networks (QNNs)

Quantum Neural Networks sit at the intersection of quantum computing and machine learning, with research focusing on overcoming fundamental training challenges.

### 6.1 Barren Plateau Mitigation

A major obstacle to QNN training is **barren plateaus (BPs)**, where gradient variance vanishes exponentially as qubit count increases. Zhuang et al. introduced **AdaInit**, a foundational framework that leverages large language models (LLMs) with the submartingale property to iteratively synthesize initial parameters for QNNs that yield non-negligible gradient variance. AdaInit adaptively explores the parameter space by incorporating dataset characteristics and gradient feedback, with theoretical guarantees of convergence to effective initial parameters. Accepted at ACL’26 Findings.

### 6.2 Hybrid Classical-Quantum Architectures

Li introduced the **Hybrid Quantum Residual Network (HQRN)**, establishing an exact functional correspondence between its state evolution and the dynamics of classical networks with residual connections. When processing general mixed states, the HQRN leverages off-diagonal quantum correlations to resolve features inaccessible to its classical counterpart.

For time series applications, Morgan et al. improved **Quantum Recurrent Neural Networks (QRNNs)** using amplitude encoding via the EnQode method, introducing a novel circuit architecture achieving substantial reduction in circuit depth.

### 6.3 Neural Network Quantum States

Research on neural network quantum states (NQSs) has advanced the simultaneous approximation of multiple degenerate states. A single neural network can now approximate all states of a degenerate manifold, reducing the computational burden for strongly correlated quantum systems.

---

## 7. Decoherence and Noise Mitigation

Decoherence remains the primary obstacle to fault-tolerant quantum computing, and 2025–2026 has seen innovative approaches to both active and passive noise suppression.

### 7.1 Flag Qubits and Active Noise Tailoring

Xie et al. proposed **Flag-GRAPE**, a novel optimal control framework with flag ancillas that actively tailors the system’s noise structure. Numerical simulations in superconducting circuits demonstrated a **51% reduction in infidelity** compared to traditional closed-system pulses, and by converting unstructured decoherence into heralded erasure errors, Flag-GRAPE is inherently compatible with quantum error correction.

### 7.2 Hadamard Phase Cycling for Dynamical Decoupling

Ni et al. presented **Hadamard phase cycling**, a scalable non-Markovian quantum error mitigation method using group-structured phase configurations to filter spurious dynamics. Validated across molecular electron spins, NV centers in diamond, nuclear spins, trapped ions, and superconducting qubits. The work reveals that many reported ultralong decoherence times stem from artifacts like coherence-population mixing rather than genuine noise suppression.

### 7.3 Hardware-Level Coherence Extension

**Spin Kerr-Cat Encoding.** McIntyre and Loss at the University of Basel developed spin Kerr-cat encoding that utilizes clock transitions in quadrupolar nuclei to suppress qubit dephasing. Calculations based on antimony donors in silicon indicate this encoding could achieve a **coherence time of 100 seconds** — surpassing previous benchmarks by several orders of magnitude — along with a two-qubit gate fidelity of 99%.

**Continuous Dynamical Decoupling in Trapped Ions.** A team led by Prof. Michael Drewsen demonstrated continuous dynamical decoupling via frequency modulation for a 138Ba+ optical qubit, generating double-dressed states that highly suppress noise channels by nesting the qubit inside two protective energy gaps.

### 7.4 Quantum Wall States and Eternal Purity

Casanova and Ticozzi introduced **quantum wall states** — a state-stabilization framework that finds approximate decoherence-free subspaces with improved passive noise isolation. By controlling only a “wall subsystem” mediating dominant environmental interactions while leaving the logical subsystem untouched, the method can maintain system purity above a threshold for all times, achieving **“eternal purity preservation”** under suitable conditions.

### 7.5 Scalable Hardware Co-Design

A hardware-software co-design from Yale University employs a 2D toric network to reduce the need for long-range couplers from linear to square root scaling, achieving a logical error rate of **3.06%** for bivariate bicycle codes — a 2.6-fold improvement over previously reported experimental results and surpassing a key threshold for practical QEC.

---

> **Disclaimer:** This report synthesizes findings from preprints, peer-reviewed publications, and research announcements from 2025–2026. Some sources are preprints that have not yet completed peer review, and their findings should be interpreted as preliminary.

---

*GAIA-OS Canon · C92 · Committed 2026-04-28*
