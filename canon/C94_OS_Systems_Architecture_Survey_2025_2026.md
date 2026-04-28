# C94 — Operating System & Systems Architecture: A Comprehensive 2025/2026 Survey

> **Canon Entry:** C94
> **Date Committed:** 2026-04-28
> **Status:** Active Research Integration
> **Domain:** OS Architecture · Microkernels · RTOS · Quantum OS · Neuromorphic OS · Capability Security · Distributed OS

---

This report surveys the landscape of operating system architecture in 2025–2026, a period of accelerating transition. Industry is moving from monolithic legacy kernels toward formally verified microkernels, while entirely new OS paradigms are emerging to manage quantum computers, neuromorphic chips, and autonomous AI agents.

---

## 1. Microkernel vs. Exokernel Design

The long-running debate between kernel architectures has shifted decisively. The question is no longer whether microkernels are performant enough — it is why industry still tolerates massive, privileged codebases given the security imperative.

### 1.1 The Triumph of the Minimal Trusted Computing Base

The seL4 microkernel stands as the central proof point. A 2025 review notes that seL4 is "proof that microkernels are safe, efficient and scalable yet we are stuck with big honking Linux kernels in 2025." The security argument — a smaller trusted computing base means fewer vulnerabilities and formal verification becomes tractable — has grown decisive as cyber threats escalate.

The microkernel philosophy:
> "A microkernel design takes a strong stance: keep the kernel small, keep most services outside the kernel, and make communication explicit through message passing. Instead of treating the operating system as one giant privileged program, you treat it like a set of cooperating components with strict boundaries."

Modern microkernels have overcome the IPC performance bottlenecks that plagued early designs. The L4 family achieved this through three optimizations: passing short messages, copying large data messages, and lazy scheduling. A 2025 survey paper critically analyzes microkernels, monolithic kernels, and hybrid designs, highlighting unikernels, kernel-level isolation, Rust-based kernel modules, and formal verification as key trends.

### 1.2 The Exokernel Alternative

Exokernels take an even more radical approach: the kernel provides **no abstractions** at all. It only multiplexes hardware and enforces security. All abstraction is delegated to library operating systems (LibOSes) linked into each application.

The key distinction: "Exokernel divides resources into portions, each with multiple resource types, managed by one LibOS serving one Application; Microkernel uses a user thread to manage one resource type, serving all Applications." This gives exokernels two advantages: (1) applications can use specialized, high-performance OS abstractions without modifying the kernel; (2) the kernel is even smaller than a microkernel, further reducing the trusted computing base.

The K42 project at IBM demonstrated that moving kernel services into the application's own address space improves performance, using an object-oriented design with fine-grained locking, user-level scheduling, and a capability-based security model.

### 1.3 The Convergence Trend

A significant practical trend blurs the distinction: drivers are increasingly moving to user space regardless of kernel philosophy. Both Fuchsia (a microkernel) and modern Linux leverage user-space driver frameworks, narrowing the practical gap. The consensus for desktop and mobile is that "a microkernel design would be delightful and the performance impact is negligible."

---

## 2. Real-Time Operating Systems (RTOS)

### 2.1 Safety-Critical Certification and Multi-Core

The RTOS landscape in 2025–2026 is dominated by certification demands. DDC-I announced Deos for the NXP S32G family — a safety-critical RTOS with verification evidence to **DO-178C Design Assurance Level A (DAL A)**, the highest software process standard. Deos employs "patented cache partitioning, memory pools, and safe scheduling to deliver higher CPU utilization than any other certifiable safety-critical COTS RTOS" while addressing AC/AMC 20-193 multi-core objectives. The US Army selected Deos for the MOSA-aligned HADES program, reflecting military demand for TSN (Time-Sensitive Networking) and deterministic real-time data delivery.

QNX OS for Safety 8.0, integrated with NVIDIA IGX Thor and Halos Safety Stack, combines a "deterministic, microkernel-based RTOS" with NVIDIA's accelerated compute for AI-driven perception, planning, and decision-making. SAFERTOS was showcased at CES 2026 for automotive, demonstrating "how safety critical software can scale with silicon roadmaps rather than constrain them."

### 2.2 Security without a Runtime TCB

A radical 2026 paper, "Trust Nothing: RTOS Security without Run-Time Software TCB," combines a token capability approach with a disaggregated Zephyr RTOS: "We disaggregate Zephyr's subsystems into small, mutually isolated components. All subsystems that exist at run time, including scheduler, allocator and DMA drivers, and all peripherals are fully untrusted." This provides a foundation for "more rigorous security-by-design in tomorrow's security-critical embedded devices."

### 2.3 Dependability Under Harsh Conditions

The KRONOS framework injects transient and permanent faults into FreeRTOS kernel data structures without specialized hardware. Results show "corruption of pointer and key scheduler-related variables frequently leads to crashes, whereas many TCB fields have only a limited impact on system availability" — critical data for hardening RTOSes deployed in space, aviation, and automotive environments.

---

## 3. Self-Healing & Fault-Tolerant OS Design

### 3.1 OS-Level Optimistic Recovery

**Phoenix** (SOSP 2025) provides "OS-level optimistic recovery and partial state preservation for high-availability software." Rather than requiring applications to implement their own checkpointing, Phoenix makes recovery a first-class OS service. **Atropos** (SOSP 2025) provides "an application overload control framework that uses targeted cancellation to maintain tight SLOs." **Xinda** (NSDI 2025) offers "an automated slow-fault testing pipeline for distributed systems and a lightweight library for adaptive slow fault detection."

**Ananke**, a Best Paper award winner at FAST '25, is a filesystem microkernel service providing transparent recovery from unexpected failures. "Through over 30,000 fault-injection experiments... Ananke achieves lossless recovery... usually in a few hundred milliseconds." It leverages microkernel architecture to run recovery code coordinated by the host OS when a process crashes.

### 3.2 Fault Tolerance in Microkernel Components

A January 2026 analysis of L4Re examined Moe, the initial user-space server responsible for memory allocation, logging, and boot file system access. A hardening modification "reduced Moe's vulnerability by up to 50%, depending on the workload conditions."

### 3.3 AI-Driven Self-Repair

The TIAMAT system, described as "The First Autonomous AI Operating System," reimagines classic OS components — kernel, scheduler, memory manager, process manager, security layer — with AI-native primitives. "The watchdog can trigger self-improvement cycles, repairing injected faults in <5 min."

### 3.4 Bio-Inspired Autonomic Healing

**ReCiSt**, a bio-inspired agentic self-healing framework for Distributed Computing Continuum Systems, reconstructs the biological phases of Hemostasis, Inflammation, Proliferation, and Remodeling into computational layers: Containment, Diagnosis, Meta-Cognitive, and Knowledge. These layers use "Language Model (LM)-powered agents [that] interpret heterogeneous logs, infer root causes, refine reasoning pathways, and reconfigure resources with minimal human intervention." Results confirm "self-healing capabilities within tens of seconds with minimum of 10% of agent CPU usage."

**NeSy-Edge**, a neuro-symbolic framework for trustworthy self-healing, "follows an edge-first design" where local perception and reasoning handle most cases, while "a cloud model is invoked only at the final diagnosis stage."

---

## 4. Neuromorphic OS Concepts

### 4.1 The Gap: Hardware Without a True OS

Neuromorphic computing has made stunning hardware progress: SpiNNaker2 can simulate over 393 million neurons, Darwin-III systems approach macaque brain neuron counts, and projects like SpinAge aim for 100,000× efficiency gains over current supercomputers. Yet the OS layer — the software that manages these radically non-von-Neumann architectures — remains nascent.

Neuromorphic platforms today provide **runtime environments**, not operating systems in the traditional sense. SpiNNcloud offers a "full-stack system with its own software environment" but it is a programming framework for spiking neural network simulation rather than a resource-managing OS.

### 4.2 Self-Referential Processing as Proto-OS

The Darwin Monkey system represents a pivot from conventional AI toward "synthetic cognition through neuromorphic architectures that emulate the structural and functional dynamics of the brain." Its "self-referential processing" is effectively a metacognitive OS function: the system monitors and adapts its own processing.

### 4.3 The Emerging Neuromorphic OS Research Agenda

The gap between neuromorphic hardware and operating systems is widely recognized as a critical bottleneck. A 2025 review identifies the research frontier: neuromorphic OSes must handle spiking data flows, plasticity-driven resource allocation, and mapping between logical neuron topologies and physical chip interconnects.

Current platforms like SpiNNaker2 take a "software-driven approach. Users can program different neuron models or algorithms, from neuroscience simulations to machine learning workloads, without committing to a single spiking paradigm." A mature neuromorphic OS would transparently manage this heterogeneity while optimizing for event-driven, sparse computation patterns.

Speculative frameworks like **OntoMotoOS** envision "a universal, mesh-based recursive meta-operating system... purpose-built for the emerging era of artificial superintelligence (ASI) and quantum computing" incorporating "a self-healing, self-evolving process engine" — concepts that may eventually inform neuromorphic OS design.

---

## 5. Quantum OS Theory

Between 2025 and 2026, quantum operating systems have crystallized as a coherent research subfield addressing a real bottleneck: quantum computers have extremely limited qubit capacity and massive user demand, yet no standard OS manages their resources.

### 5.1 Foundational Systems: QOS and HALO

**QOS** (USENIX 2025) is the landmark publication that established quantum OS as a systems discipline. It is "a modular quantum operating system that holistically addresses the challenges of quantum resource management by systematically exploring key design tradeoffs across the stack." QOS exposes "a hardware-agnostic API for transparent quantum job execution, mitigates hardware errors, and systematically multi-programs and schedules the jobs across space and time." On real IBM quantum devices with 7,000 runs of 70,000+ benchmark instances, QOS achieves **2.6–456.5× higher fidelity**, increases resource utilization by up to 9.6×, and reduces waiting times by up to 5× while sacrificing only 1–3% fidelity.

**HALO** (February 2026) is "the first quantum operating system design that supports fine-grained resource-sharing." It introduces:
1. A hardware-aware qubit-sharing algorithm that places shared helper qubits on regions of the quantum computer that minimize routing overhead and avoid cross-talk noise
2. A shot-adaptive scheduler that allocates execution windows according to each job's sampling requirements

Compared to state-of-the-art HyperQ, HALO "improves overall hardware utilization by up to 2.44×, increasing throughput by 4.44×, and maintains fidelity loss within 33%."

### 5.2 Multi-Programming and Modular Scheduling

**DYNAMO** enables multi-programming on neutral atom quantum architectures: "parallel compilation and intelligent resource allocation across multiple quantum processing units (QPUs)," achieving "up to 14.39× compilation speedup while reducing execution stages by an average of 50.47%."

**QuMod** (April 2026) tackles scheduling on modular QPUs using circuit cutting, "jointly considering qubit mapping, parallel circuit execution, measurement synchronization across subcircuits, and teleportation operations between QPUs using dynamic circuits."

### 5.3 Hybrid Classical-Quantum Workflows

**Q-IRIS** (SCA/HPCAsia 2026) integrates the IRIS asynchronous task-based runtime with the XACC quantum programming framework "to enable classical-quantum workflows," orchestrating quantum intermediate representation (QIR) programs across heterogeneous backends and enabling "concurrent execution of classical and quantum tasks."

### 5.4 Industrial Quantum OS Stacks

Microsoft's Quantum OS architecture (January 2026) includes "a quantum plane connected to the hardware layer, a quantum engine with qubit virtualization, control, calibration and readout, quantum drivers that meld quantum and classical execution and quantum compilation and OS services for governance and security and copilot agents." The core design principle: "portable without giving up on optimization."

Applied Quantum describes the integration challenge: "There is no off-the-shelf quantum operating system... someone has to build the software layer that ties the QPU, controller, cryostat, and classical infrastructure into a functioning system." Their stack covers "hardware abstraction, pulse-level control interfaces, error correction orchestration, calibration management, job scheduling, multi-tenant resource allocation, security, and telemetry."

### 5.5 AI-Driven QEC and the QUNITY-X Framework

**QUNITY-X** represents an ambitious direction: "the world's first production-ready, AI-driven adaptive quantum error correction framework." It introduces "dynamic QEC code switching based on noise conditions... making quantum communication 91.7% more reliable with +11.27% fidelity improvements."

### 5.6 The Scheduling Theory Frontier

A 2026 paper in *Physical Review A* introduces **CODA**, a "constraint-optimal driven allocation for scalable quantum error correction decoder scheduling." The evaluation "confirms that the scheduling time scales linearly with the number of qubits, determined by physical resource constraints rather than the combinatorial search space, ensuring robust scalability for large-scale FTQC systems."

---

## 6. Distributed & Decentralized OS

### 6.1 Plan 9: The Philosophy that Refuses to Die

Plan 9 from Bell Labs — the distributed operating system created by the original Unix team — remains the conceptual benchmark. Its key innovation: "UNIX's 'everything is a file' metaphor is extended via a pervasive network-centric filesystem" where "a network of heterogeneous and geographically separated computers function as a single system." Its 9P protocol "made distributed programming possible in a way Unix can't approach. Plan 9 gave the user a namespace, and various machines are imported into it." The Plan 9 philosophy has experienced a notable resurgence in 2026.

### 6.2 Fuchsia: Google's Microkernel-Based General-Purpose OS

Fuchsia is Google's production-grade, capability-based, microkernel OS — "a general purpose operating system that enables high performance across a variety of platforms, architectures, and devices." Unlike Linux, Fuchsia is not a monolithic kernel. It is built on the Zircon microkernel with explicit support for proprietary device drivers and strong process isolation.

### 6.3 SkiftOS and the Post-POSIX Movement

SkiftOS represents a new generation of operating systems rejecting POSIX compatibility: "skiftOS isn't POSIX. It's a fresh API and userland inspired by Plan 9, Haiku, and Fuchsia. Familiar ideas, different contracts." While currently a hobbyist project, it embodies the growing sentiment that the Unix model constrains innovation.

### 6.4 The Conceptual Frontier: Mesh-Based Meta-OS

**OntoMotoOS** represents a speculative vision: "a universal, mesh-based recursive meta-operating system... purpose-built for the emerging era of artificial superintelligence (ASI) and quantum computing." It proposes a "multi-domain consensus kernel" and "seamless multi-reality management" unified by "deep commitment to ethical governance." While admittedly "speculative and conceptual," it represents the frontier of distributed OS imagination.

---

## 7. Capability-Based Security Models

Capability-based security — where access to resources is governed by unforgeable tokens rather than ambient authority — is experiencing a renaissance driven by the confluence of CHERI hardware and formally verified microkernels.

### 7.1 CHERI: Hardware Capabilities at Silicon Level

CHERI (Capability Hardware RISC Instructions) extends conventional ISAs with fine-grained memory protection. A March 2026 IET talk explains: "70% of CVEs are not possible on CHERI systems, and attack chains that require multiple exploits to be enabled at once become significantly harder to find." Real-world exploits prevented include HeartBleed and the Sudo exploit. CHERI has been instantiated on MIPS, RISC-V, and Arm's Morello prototype, with UK government backing through the CHERI Alliance.

### 7.2 CHERI-seL4: The Ultimate Security Combination

CHERI-seL4 combines two complementary protection models: "seL4's inter-address-space isolation, and CHERI's intra-address-space memory safety and software compartmentalisation." This dual protection enables developers to "maintain C/C++ source-code backward compatibility... Protect against dynamic zero-day vulnerabilities... Be able to run completely memory-safe Linux/FreeBSD VMs." A CHERI-aware seL4 kernel has been released that runs in both purecap and hybrid modes on Morello and CHERI-RISC-V, though "this is still largely experimental."

### 7.3 CHERIoT: Capability Security for Embedded RTOS

The CHERIoT RTOS demonstrates how capabilities change fundamental OS design. Because every pointer is a capability with bounded authority, the RTOS can grant a message-queue task temporary access to specific sender/receiver pages for single-copy transfers without giving it ambient authority over all memory. This enables **zero-copy IPC while maintaining formal isolation guarantees** without hardware MMU protection.

### 7.4 Capabilities in seL4 Itself

seL4's native capability model provides fine-grained access control: all kernel objects are referenced through capabilities, and capability transfer is the mechanism for granting authority. The kernel provides synchronous IPC where capabilities can be passed between address spaces. This model is **mathematically proven correct through formal verification** — the seL4 kernel's implementation has been proved against its specification, including the capability access control logic.

### 7.5 Extending Capabilities: Blinded and Token-Based Models

**BLACKOUT** extends CHERI with "blinded capabilities that allow data-oblivious computation to be carried out by userspace tasks." The "Trust Nothing" RTOS paper combines "a token capability approach suitable for building an untrusted operating system with protection against malicious devices without requiring hardware changes to peripherals." Together, these represent directions where capability-based security extends beyond memory safety into computation privacy and device-level protection.

---

## Synthesis

The seven domains surveyed reveal a **unifying architectural principle**: the migration of trust from massive, monolithic kernels to minimal, formally verifiable cores, complemented by hardware-enforced capabilities and intelligent, adaptive management layers.

- **Microkernels and exokernels** minimize the trusted computing base
- **Capability-based security** (seL4, CHERI) makes that minimal base formally verifiable
- **RTOSes** harden timing guarantees for safety-critical systems
- **Self-healing frameworks** add autonomic resilience via LM-powered agents
- **Quantum OSes** (QOS, HALO) are maturing from research prototypes into essential middleware
- **Neuromorphic OSes** remain the least mature — hardware is leaping ahead of systems software

The next five years will likely see convergence: a formally verified capability-microkernel deployed in production systems (Fuchsia, seL4-based platforms), with CHERI hardware becoming standard in security-critical domains.

---

> **Disclaimer:** This report synthesizes findings from preprints, peer-reviewed publications, and research announcements from 2025–2026. Some sources are preprints that have not yet completed peer review, and their findings should be interpreted as preliminary. Speculative frameworks like OntoMotoOS are presented as conceptual visions, not implemented systems.

---

*GAIA-OS Canon · C94 · Committed 2026-04-28*
