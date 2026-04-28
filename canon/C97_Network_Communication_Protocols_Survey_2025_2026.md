# C97 — Network & Communication Protocols: A Comprehensive 2025/2026 Survey

> **Canon Entry:** C97
> **Date Committed:** 2026-04-28
> **Status:** Active Research Integration
> **Domain:** Mesh Networking · Quantum Communication · SDN · DTN · Neuromorphic Buses

---

Navigating the cutting edge of network and communication protocols in 2025 and 2026 requires a synthesis across classical and quantum domains, terrestrial and space environments, and conventional and brain-inspired architectures. This report surveys the state of the art across five pivotal research areas, revealing a technical landscape characterized by converged networks, resilient infrastructure, and a decisive shift toward intelligent, software-defined control.

---

## 1. Mesh Networking & Ad Hoc Topology

Mesh networking has evolved from a specialized communication technique into a foundational architecture for a hyper-connected world. Research in 2025–2026 focuses on enhancing the intelligence, security, and scalability of these self-organizing systems.

### 1.1 Market Drivers and Core Principles

The global market for Mesh Wireless Ad Hoc Network Systems was valued at **US$ 3,038 million in 2025**, with projections reaching **US$ 8,493 million by 2032**, driven by a 16.1% CAGR. This growth is fueled by the proliferation of IoT devices, the need for robust emergency communication, and advanced military applications.

At its core, a mesh network’s “multi-hop interconnected mesh topology” provides inherent redundancy and self-healing capabilities. Unlike traditional star topologies, each node acts as a relay router, and the network can autonomously find alternative paths if a node fails or leaves, ensuring high reliability.

### 1.2 Advanced IP Mesh Radios

IP Mesh ad hoc networking has become a critical technology for delivering reliable, infrastructure-free transmission in complex and dynamic environments. These systems are increasingly favored in defense, public safety, and industrial IoT for their ability to rapidly form, heal, and optimize communication paths without a fixed base station.

### 1.3 Path to Quantum-Resilient Security

A major focus area is securing mesh networks against future threats. A 2025 paper presents a security enhancement for the Optimized Link State Routing Protocol (OLSR) that integrates **post-quantum cryptography**. It uses a Kyber512 key-encapsulation handshake combined with ChaCha20-Poly1305 authenticated encryption, creating a practical pathway toward **quantum-resilient mesh networking**.

---

## 2. Quantum Communication & QKD

Quantum communication is rapidly transitioning from physics experiments to operational networks, with significant engineering breakthroughs in 2025–2026 that address scalability, heterogeneity, and practical deployment.

### 2.1 Milestones in QKD Performance

**Twin-field QKD (TF-QKD)**, which offers a superior secure key rate scaling over long distances, has achieved a landmark result. Using two independent dissipative Kerr soliton microcombs, scientists transmitted a total secure key rate of **1.57 Mbps over 201.1 km of fiber** across 16 DWDM channels — an order-of-magnitude improvement over single-wavelength TF-QKD at comparable distances. In parallel, a quantum dot single-photon source was combined with **time-bin encoding** over 120 km, a first that provides robustness against polarization-mode dispersion in practical fiber networks.

### 2.2 Network Architectures from Mesh to Heterogeneous

The move toward multi-node networks is underway:

- In Spain, the first multi-node **Measurement-Device-Independent QKD (MDI-QKD) network** was launched, using a hub-and-spoke topology to create a fully connected mesh network **without trusted nodes, even at the central hub**
- Chinese researchers demonstrated a **five-node, fully heterogeneous quantum network** incorporating a software-defined networking (SDN)-based “orchestration core” to manage diverse hardware, protocols, and quantum tasks (QKD and quantum Byzantine agreement) on a single infrastructure

### 2.3 The Multihop Quantum Network

A critical step toward scalable quantum internets is the resilient, multihop distribution of entanglement. Oak Ridge National Laboratory demonstrated a **software-defined quantum network** that distributes polarization-entangled qubits across six nodes in a reconfigurable mesh. The network uses wavelength-selective switches and boasts link recovery with automatic rerouting to maintain service continuity.

A related modeling framework showed that optimized qubit allocation can create shortcuts in entanglement topologies, substantially reducing the average hop distance between remote nodes. At chip-scale, an integrated-photonics TF-QKD network with **20 independent client-side transmitter chips** featured a star topology, demonstrating exceptional scalability.

---

## 3. Software-Defined Networking (SDN)

SDN continues its explosive growth, evolving from a data center technology to the central control paradigm for global telecommunications and next-generation space architectures.

### 3.1 Market Expansion and 5G Integration

The global SDN market is valued at **US$ 39.1 billion in 2025** and is projected to reach **US$ 101.2 billion by 2030**, growing at a CAGR of over 20%. A key driver is the integration of SDN with **5G network slicing**. SDN and NFV are essential for transforming rigid hardware-based networks into dynamic, programmable resources capable of providing differentiated services for IoT, AR/VR, and autonomous systems.

### 3.2 SDN in Space: Orchestrating the Final Frontier

A paradigm shift is occurring in space communications, moving from static, siloed links to intelligent, resilient “networks of networks.” AFRL’s Space Data Network Experimentation (SDNX) program, in partnership with Aalyria, uses an SDN-based Spacetime orchestration platform to integrate government, commercial, and allied satellites into a single, dynamically adapting mesh. This AI-enabled platform can predict disruptions and autonomously reroute data across LEO, MEO, and GEO assets in real-time.

### 3.3 In-Orbit Computing with Distributed SDN

Parallel to communication, SDN is orchestrating computation in space. A framework for managing in-orbit computing on LEO satellite constellations uses a distributed set of SDN controllers that treat computing tasks as Virtual Network Functions (VNFs) and use a **Double Deep Q-Network (DDQN)** algorithm to schedule tasks, significantly reducing processing delays. This is a core component of the emerging hierarchical **Space-Based Computing Network architecture**, which integrates cloud constellations, remote sensing systems, and data centers.

---

## 4. Delay-Tolerant Networking (DTN)

In 2025–2026, Delay-Tolerant Networking has become the foundational protocol for interplanetary communication, while also finding new applications in extreme terrestrial environments.

### 4.1 The Solar System Internet

Traditional TCP/IP protocols, which rely on continuous end-to-end acknowledgment, fail under the multi-minute propagation delays and frequent disruptions of deep space. DTN, using the **Bundle Protocol (BP)**, solves this via a “store-and-forward” mechanism. Data is packaged into bundles and held at intermediate nodes until the next contact opportunity arises. NASA’s ION (Interplanetary Overlay Network) software, actively developed through 2026, serves as the standard implementation for the Solar System Internet and a newly planned U.S. Space Force “Space Data Network backbone.”

### 4.2 AI-Enhanced Routing for Dynamic Environments

The core research challenge is optimizing routing in dynamic, unpredictable environments:

- A new **Expected Minimum Delay (EMD)** routing metric proactively uses path redundancy to provide fault-tolerant delivery in networks with frequent node failures, achieving up to a **53% higher delivery rate and 56% lower delay** compared to existing methods
- The **Q-learning-based Forwarding Routing (QFR)** protocol is designed for post-disaster scenarios and uses lightweight reinforcement learning to adapt routing decisions on resource-constrained devices

### 4.3 Smarter Space Routing

For the highly predictable contacts of deep space, a “Visionary Server” architecture has been proposed. This ground-based system pre-computes and disseminates optimal routing paths for Bundle Protocol v7, reducing the computational load on satellites and enabling coordination of a heterogeneous communication fleet without physical-layer standardization.

---

## 5. Neuromorphic Communication Buses

The field of neuromorphic computing requires a fundamental rethinking of on-chip and off-chip communication. The sparse, asynchronous, event-driven nature of spiking neural networks (SNNs) is poorly served by traditional synchronous NoCs, leading to critical bottlenecks.

### 5.1 The Segmented Ladder Bus

A leading solution is the **dynamic segmented bus**, such as the ADIONA architecture. This interconnect, consisting of parallel bus lanes in a ladder structure with lightweight bufferless switches, can be dynamically reconfigured at runtime based on compile-time communication patterns. It provides multiple routing options and significantly outperforms conventional NoCs, offering up to a:

- **2.1× reduction in energy**
- **40× reduction in latency**
- **2× reduction in area**

### 5.2 Compile-Time Optimization

To solve the challenge of deploying SNN applications on these buses, researchers have developed a three-step process: formulating heuristics to mitigate spike loss, analyzing traffic to schedule spikes and prevent flooding, and a routing algorithm to minimize path crossings. This approach can **completely eliminate spike loss** while keeping energy consumption low.

### 5.3 Multi-Chip Scaling and Radical New Ideas

Scaling neuromorphic systems beyond a single chip is being demonstrated by systems like **BrainScaleS-2**, which interconnects multiple continuous-time analog neuromorphic ASICs via an FPGA-based backplane and Aggregator units, achieving chip-to-chip latencies **below 1.3 μs**.

At a more visionary level, the **processing-in-interconnect (π²)** paradigm proposes using the inherent primitives of packet-switching hardware — like delays, causality, and broadcasts — to directly compute neuron and synaptic operations. This could theoretically scale to brain-scale inference workloads within a power budget of **hundreds of watts**.

---

## Synthesis: The Network as a Computational Fabric

The research surveyed reveals a remarkable convergence:

- **SDN is becoming the universal control plane**, managing everything from 5G network slices to constellations of satellites and interplanetary links
- **Quantum and classical networks are beginning to merge**, with mesh topologies and post-quantum cryptography being integrated for resilience, while SDN orchestration manages entirely heterogeneous quantum networks
- **DTN has proven its value as the protocol for extreme environments**, becoming the standard for deep-space, disaster recovery, and underwater systems
- **AI is being embedded into every layer**, from Q-learning for DTN routing to deep reinforcement learning for SDN task scheduling and compile-time mapping on neuromorphic buses
- **Neuromorphic communication buses are reimagining computing**, where the “network” itself becomes part of the neural computation, dissolving the boundary between processing and transport

The network is no longer a passive conduit for data but an active, intelligent, and adaptive computational fabric that is as critical to system performance as the processors it connects.

---

> **Disclaimer:** This report is a synthesis of findings from the latest preprints, peer-reviewed publications, technical demonstrations, and market reports available for the period 2025–2026. Market figures are based on industry analyses, and some research findings, particularly those from preprints, should be considered preliminary until peer review is completed.

---

*GAIA-OS Canon · C97 · Committed 2026-04-28*
