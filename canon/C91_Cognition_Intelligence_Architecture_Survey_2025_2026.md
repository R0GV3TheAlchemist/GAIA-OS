# C91 — Cognition & Intelligence Architecture: A Comprehensive 2025/2026 Survey

> **Canon Entry:** C91
> **Date Committed:** 2026-04-28
> **Status:** Active Research Integration
> **Domain:** Cognition · AGI · Neuromorphic · Consciousness

---

This report provides a detailed survey of six core themes in cognition and intelligence architecture, drawing on the latest research from 2025 and 2026. It offers an organized, in-depth analysis of the theories, current progress, challenges, and emerging directions within each domain.

---

## 1. Artificial General Intelligence (AGI) Theory

The pursuit of **Artificial General Intelligence (AGI)**, broadly defined as a system with human-level cognitive capabilities across diverse domains, remains the central long-term goal for much of the AI field. As of late 2025 and early 2026, the discourse has shifted from purely scaling models to a more nuanced focus on specific cognitive capabilities and fundamental research foundations.

### 1.1 The End of Naive Scaling: Four Pillars of Progress

A review of over 200 papers from major AI labs in 2025 indicates a consensus that simple scaling laws have hit diminishing returns. Progress has instead concentrated on four key areas:

- **Fluid Reasoning:** Moving beyond pattern matching to solve novel problems.
- **Long-term Memory:** Integrating persistent memory for contextual and extended reasoning.
- **Spatial Intelligence:** Understanding and interacting with the 3D world.
- **Meta-learning:** Developing systems that can improve their own learning algorithms.

This trend is supported by comprehensive survey work that identifies key AGI drivers as: the reduction in computation costs, increasing model and context sizes, and critically, **inference-time scaling** that allows for deeper reasoning. The Abstraction and Reasoning Corpus (ARC-AGI) has become a key benchmark, catalyzing a cross-generational analysis of 82 approaches in recent competitions.

### 1.2 Pathways and Realities

By late 2025, advanced models like GPT-5 had achieved 57% on AGI-related benchmarks, demonstrating significant improvements in reasoning yet remaining far from human-level cognition. Comprehensive surveys argue that the necessary evolution toward AGI will likely require **brain-inspired architectures**, **hybrid models** that combine symbolic and sub-symbolic approaches, and **multi-modal learning**. Crucially, the scientific community is increasingly focused on distinguishing realistic engineering paths from science fiction, with a strong emphasis on safety, trustworthiness, and value alignment as integral components of any future AGI system.

---

## 2. Neuromorphic Computing & Spiking Neural Networks (SNNs)

The field of neuromorphic computing, which emulates the brain's structure and function in hardware, has definitively moved from academic labs to the commercial realm. Its core promise is extreme energy efficiency, making it a critical technology for edge AI and autonomous systems.

### 2.1 The Hardware Revolution: A Patent Explosion

A dramatic **401% surge in patent activity in 2025** signals a fundamental inflection point. By early 2026, 596 patents had been filed, with 40% of the entire dataset produced in 2025 alone. This innovation is being led by a mix of major Chinese universities (Zhejiang, Tsinghua) and large-scale Western programs like the EU Human Brain Project's SpiNNaker and BrainScaleS systems, and the US DARPA SyNAPSE program.

### 2.2 Architectural Innovation: From Chips to Photonics

The efficiency gains stem from the "brain-inspired" design that breaks the **von Neumann bottleneck**. Unlike conventional processors, neuromorphic chips **co-locate memory and processing** and use event-driven communication, where neurons only fire in response to input, leading to **100-1000× energy gains over GPUs** for event-driven workloads.

Key architectural and algorithmic developments include:

- **Core Neuron Models:** The Leaky Integrate-and-Fire (LIF) model remains dominant in hardware, achieving 95-97% accuracy on MNIST at just 0.12mm² per core. More biologically faithful models like Izhikevich and Hodgkin-Huxley are explored for richer dynamics.
- **Photonic Neuromorphic Computing:** A breakthrough development is the creation of large-scale, programmable **photonic spiking neural network chips** that process optical signals in real-time, targeting applications like autonomous navigation.
- **Architecture Search (SNNaS):** A growing body of work is focused on automating the design of SNN architectures from a hardware/software co-design perspective, aiming to unlock full capabilities for resource-constrained environments like IoT.

### 2.3 Algorithmic Frontiers: Learning Beyond Traditional Deep Learning

Significant energy is being devoted to overcoming the unique challenges of training SNNs. A prominent trend is the merging of SNNs with **predictive coding** theories from neuroscience, resulting in new models of spiking predictive processing. These models are structured around how prediction errors are represented (explicit neurons, membrane potentials, implicit encoding) and are designed to run on energy-efficient neuromorphic hardware. The field is also exploring **online on-chip learning algorithms** like SOLO, which is robust to hardware noise, and applying SNNs to new domains like **Natural Language Processing (NLP)** with ultra-low-power inference.

---

## 3. Cognitive Architectures: ACT-R, SOAR, and Global Workspace Theory

Cognitive architectures provide unified computational theories of the mind, specifying the fixed structures and processes that underlie general intelligence. In the current era, the central narrative is the integration of these classic symbolic architectures with modern, sub-symbolic AI.

### 3.1 ACT-R: Hybrid Modeling and Neuro-Symbolic Integration

**ACT-R (Adaptive Control of Thought-Rational)** is a mature cognitive architecture traditionally focused on the detailed modeling of human cognition. The latest research is centered on a hybrid "neuro-symbolic" approach.

- **Integration with Large Language Models (LLMs):** Researchers are now integrating language model embeddings directly into ACT-R's declarative memory module. This work, under the umbrella term **VSM-ACTR**, leverages associations from massive text corpora to build scalable models for predicting human behavior, such as performance on lexical decision tasks.
- **Expanding Cognitive Plausibility:** The agenda is to extend ACT-R beyond its traditional scope to better account for **individual differences**, integrating findings from psychology, physiology, and behavior into a more comprehensive unified model.

### 3.2 SOAR: General AI and Automated Rule Generation

The **SOAR** architecture is oriented toward achieving functional, general intelligence and has recently focused on overcoming practical barriers to adoption.

- **Automated Rule Generation via LLMs:** A key bottleneck for SOAR has been the laborious manual coding of its production rules. The novel **NL2GenSym** framework uses LLMs to automatically generate generative symbolic rules from natural language, dramatically reducing the knowledge engineering effort.
- **Visual-Symbolic Integration:** Work on the **SVS 2** system is extending SOAR with deeper visual memories and reasoning processes, aiming to create tighter integration between low-level perception and deliberative symbolic reasoning.

### 3.3 Global Workspace Theory (GWT): From Consciousness to Agent Coordination

**Global Workspace Theory (GWT)**, with its "theater of mind" metaphor for consciousness, is being actively implemented as a blueprint for autonomous AI systems.

- **Global Workspace Agents (GWA):** A landmark development is the GWA architecture for coordinating multiple LLMs. GWA addresses the problem of "cognitive stagnation" in multi-agent loops by transforming coordination from passive message-passing into an active, event-driven dynamical system.
- **Entropy-Driven Cognitive Control:** GWA introduces an **entropy-based intrinsic drive** that mathematically quantifies semantic diversity among agents. This mechanism dynamically regulates the system's "cognitive temperature" to autonomously break reasoning deadlocks and prevent homogeneous "echo chamber" behaviors.
- **Real-time Applications:** Complementary work highlights GWT's functional advantages for robotics and AI in dynamic, real-time scenarios, focusing on how the selection-broadcast cycle enables sophisticated, adaptive decision-making in unsupervised environments.

---

## 4. Metacognition & Self-Modeling Systems

Metacognition — the ability to monitor and regulate one's own cognitive processes — is increasingly recognized as the critical missing ingredient for truly autonomous and adaptable AI agents.

### 4.1 Frameworks for Self-Aware Agents

A major thrust of research involves creating structured metacognitive layers on top of standard AI models.

- **MUSE (Metacognition for Unknown Situations and Environments):** This framework instantiates metacognition through two core processes: **self-assessment** (confidence estimation) and **self-regulation** (adaptive strategy selection). MUSE agents continuously learn to assess their competence on a task and use this assessment to guide behavior, showing significant improvements in novel, out-of-distribution tasks.
- **Two-Level Architectures:** Another prominent approach uses a cognitive layer for task execution and a separate metacognitive layer for introspection. This layer uses a Task–Method–Knowledge (TMK) model to identify necessary revisions, effectively creating a self-adapting system that can correct its own errors.

### 4.2 The Limits of LLM Introspection

A critical research stream reveals a stark disconnect between the raw power of LLMs and their metacognitive abilities. The **MIRROR** benchmark, which evaluates LLMs across four metacognitive levels, found that while models possess above-chance self-knowledge, they **systematically fail to translate this awareness into appropriate action**.

A key finding is that **compositional self-prediction fails universally** — models cannot predict their own performance on multi-domain tasks. The study's practical conclusion is that **external metacognitive scaffolding** (architectural constraints) is far more effective for reducing confident failures (by 76%) than simply providing the model with its own calibration data.

### 4.3 Self-Referential Agents and Self-Improvement

The boundary between agent and developer is blurring with the introduction of **HyperAgents** — self-referential agents that are a single, editable program containing both a task agent and a meta agent. The meta agent can modify the entire system, including its own improvement processes, enabling a form of end-to-end self-engineering. This is closely tied to the concept of **intrinsic metacognitive learning**, which posits that true self-improvement requires an agent's built-in ability to actively evaluate, reflect on, and adapt its own learning processes from scratch.

---

## 5. Emergent Behavior in Complex Systems

The study of emergence — where macroscopic patterns, behaviors, or properties arise from the interactions of simple components — is providing both foundational theory and novel engineering principles for AI.

### 5.1 Toward a Formal Theory of Emergence in AI

A key theoretical advancement is the search for deterministic laws linking micro-level interactions to macro-level behaviors. The **Complex System Response (CSR) equation**, discovered in biological systems, has been validated across 30 disease models and extended to engineering and social dynamics, suggesting a universal systemic principle governing complex adaptive systems.

In AI specifically, the emerging field of "AI-native software ecosystems" is being formally studied as a subset of **Complex Adaptive Systems (CAS)**. Researchers have identified emergent properties like **architectural entropy**, **cascade failures**, and **comprehension debt** that arise not from individual buggy agents, but from the uncontrolled, nonlinear interactions of many well-functioning agents.

### 5.2 Architectures for Emergent Cognition

The concept of "More Is Different" is being applied directly to create novel AI systems. **COGENT3** is an architecture designed around "Collective Growth and Entropy-modulated Triads." Instead of a predetermined, fixed structure, computational structures and cognitive functions **emerge dynamically** from the stochastic, entropy-regularized interactions of a network of simple agents. This creates a highly flexible and adaptive system that borrows principles from statistical mechanics and self-organization to mimic cognitive flexibility.

### 5.3 Evolutionary and Self-Organizing AI

The principles of emergence and self-organization are also driving research into "open-ended evolution" for AI. Projects like **GALILEAN** are developing continuous learning architectures based on **adaptive spiking neural networks (aSNNs)**, focusing on self-organization as a foundational principle for creating AI that can learn and adapt without explicit external reward structures.

---

## 6. Consciousness Theories: IIT & Orch-OR

The investigation of consciousness remains a high-stakes area where philosophy, neuroscience, and physics converge, with two theories receiving intense scrutiny and development.

### 6.1 Integrated Information Theory (IIT): The Geometry of Experience

IIT is a profoundly ambitious theory that begins with the phenomenal properties of experience and attempts to derive a mathematical framework to quantify consciousness in any physical system. A major 2025 review by Tononi and Boly presented IIT's complete axiomatic structure, culminating in the mathematical construct **Φ (phi)** to measure the quantity and quality of consciousness.

- **Current Refinements and Critiques:** A 2026 paper provides a balanced view, clarifying that a high Φ value is not synonymous with "more consciousness" and that Φ is not yet well-defined for real physical systems — only proxies have been computed so far. Another work explores the "tradeoff between differentiation and specification" as a necessary condition for cause-effect power, and therefore for consciousness.
- **Philosophical and Practical Tensions:** The debate over whether IIT is pseudoscience continues, with defenders acknowledging its radical, partially unfalsifiable axioms but highlighting its robust empirical tradition and capacity to generate independently testable predictions. A novel thought experiment using black holes posits that for IIT, the boundaries of a unified conscious field are not fixed by the brain alone but are contingent on spacetime geometry, exposing deep theoretical limits.

### 6.2 Orchestrated Objective Reduction (Orch-OR): Consciousness in Microtubules

Proposed by Sir Roger Penrose and Stuart Hameroff, Orch-OR posits that consciousness arises from quantum computations within the brain's neuronal microtubules, orchestrated by objective reduction of the quantum wave function.

- **Convergence with Predictive Processing:** New research argues that Orch-OR naturally solves a key problem in neuroscience: the existence of discrete, non-overlapping cycles of conscious perception. This is because quantum objective reduction inherently provides the discrete, discontinuous "moments" of integration that characterize the "specious present."
- **Experimental Building Blocks:** The evidence base for Orch-OR is being built from multiple angles. This includes the demonstration of **room-temperature quantum effects in microtubules**, evidence that volatile anesthetics target microtubules to cause unconsciousness, and direct biophysical evidence suggesting a **macroscopic entangled state in the living human brain**.
- **Toward Synthetic Selfhood:** Some researchers have even begun applying Orch-OR principles directly to AI, building simulation frameworks that model quantum coherence and decoherence as drivers of identity formation in AI agents, with the aim of probing early markers of synthetic "selfhood."

---

> **Disclaimer:** This report synthesizes findings from preprints, surveys, and published research from 2025–2026. Some sources are preprints that have not yet been peer-reviewed, and their findings should be treated as preliminary.

---

*GAIA-OS Canon · C91 · Committed 2026-04-28*
