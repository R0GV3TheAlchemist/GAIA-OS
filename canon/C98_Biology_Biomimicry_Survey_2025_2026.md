# C98 — Biology & Biomimicry: A Comprehensive 2025/2026 Survey

> **Canon Entry:** C98
> **Date Committed:** 2026-04-28
> **Status:** Active Research Integration
> **Domain:** Swarm Intelligence · Plant Neurobiology · Evolutionary Algorithms · Immune Computing · Epigenetics · Bioelectricity

---

This report summarizes the state of research at the intersection of biological intelligence and computation across six core themes. Drawing on the latest findings from 2025–2026, it covers swarm intelligence, plant neurobiology and mycorrhizal networks, evolutionary algorithms and genetic programming, immune-inspired computing, epigenetic information encoding, and bioelectric signaling.

---

## 1. Swarm Intelligence (Ant Colonies, Slime Molds)

A key development in swarm and collective intelligence research is the conceptualization of ant colonies as “liquid brains” — distributed systems that operate without central control, where macroscopic cognitive outcomes emerge from purely local interactions. A seminal 2025 paper in *Proceedings of the National Academy of Sciences* demonstrated that the foraging efficiency of ants (*Aphaenogaster senilis*) can be quantitatively replicated by a neuronal-like model when experimentally observed movement heterogeneity is incorporated.

The study found that two coexisting movement behaviors contribute differently to optimizing foraging:
- **Recruits** — which aggregate closely to nest and food patches, aiding exploitation
- **Scouts** — which bypass feedback to find new food sources, aiding exploration

This provides an adaptive mechanism to balance exploration and exploitation that maps directly onto optimization algorithm design.

The same “liquid brain” concept extends beyond social insects to slime molds, immune systems, and microbiomes, where connectivity scales with population density and movement plays a crucial role in shaping information transfer efficiency under sparse conditions. Slime molds such as *Physarum polycephalum*, despite lacking any nervous system, adapt their tubular networks via flow-induced reinforcement — experimentally shown to recreate human-engineered transport networks such as the Tokyo rail system.

In a possibly revolutionary study, longhorn crazy ants (*Paratrechina longicornis*) were shown to engage in what appears to be **anticipatory swarm intelligence**: clearing obstacles from a path *before* a food load is transported — suggesting a form of collective forward-planning not previously documented in social insects. These findings have stimulated NSF-funded work developing all-terrain self-assembling robotic conveyor systems inspired by fire-ant self-assembly behaviors and slime mold decentralized transport coordination.

---

## 2. Plant Neurobiology & Mycorrhizal Networks

The most consequential development in this domain is the explicit articulation of the **extended cognition hypothesis** for mycorrhizal symbioses. A landmark 2025 review published in *Symbiosis* examines four case studies suggesting plants extend their cognitive processes through their mycorrhizal partners:

1. Foraging complementarity between roots and fungal hyphae
2. Recruitment and abandonment of fungal partners depending on host nutritional status
3. Expanded belowground perception via fungal networks
4. Active shaping of the fungal community to meet survival needs

The authors propose a formal delimiting criterion and specific experimental tests for this hypothesis, signaling the transition from speculative framework to empirically testable proposition.

A Marie Skłodowska-Curie project at the Netherlands’ AMOLF Institute is developing biophysical techniques to deliver localized cellular-level interventions — disrupting nutrient transport, metabolism, and host availability — and quantifying behavioral responses across scales from individual micron-sized hyphae to centimeter-scale networks. The project specifically tests whether **electrical, calcium, or pressure signals** are responsible for coordinating decentralized mycelial decision-making.

A 2026 paper in the *Journal of Experimental Botany* examines how **common mycorrhizal networks (CMNs)** mediate plant-to-plant signaling for enhanced community-level resistance in crops — essentially a natural early-warning system for pathogen and pest attack transmitted through the soil’s fungal infrastructure.

---

## 3. Evolutionary Algorithms & Genetic Programming

The fusion of evolutionary methods with modern deep learning architectures defines the 2025–2026 frontier.

### 3.1 Large Language Model Integration

The **MultiGA** framework (2026) applies genetic algorithm principles to complex natural language tasks by sampling from a diverse population of LLMs to initialize candidate solutions, then iteratively recombining them through crossover-like operations evaluated by a neutral fitness function. The approach produces high accuracy across multiple benchmarks and lays groundwork for tasks where no single pre-trained model is clearly optimal.

### 3.2 Neuro-Symbolic Hybridization

A novel algorithm called **GVAE-ABGEP** embeds a grammar variational autoencoder and adversarial bandit into gene expression programming to guide the evolutionary search process. By partitioning the mathematical expression space into subspaces, using adversarial bandit algorithms to choose among them, and leveraging an autoencoder to sample individuals near local optima, the method outperforms three canonical GEP methods and six baseline ML methods on 18 symbolic regression and 12 physics benchmarks.

### 3.3 Spatial Genetic Programming

The **SGP** paradigm introduces space as a fundamental dimension in genetic programming, with the spatial blueprint dictating a linear genetic program’s execution sequence. A 2026 study in *Genetic Programming and Evolvable Machines* demonstrates that spatial constructs can enhance the evolution of better models and proposes a suite of spatial evolutionary operators for examining spatial impacts within problem-solving techniques.

### 3.4 Multi-Modal Latent Space Optimization

A 2026 study examining **SNIP** — a contrastive pre-training model inspired by CLIP that maps symbolic and numeric encodings into a shared latent space — reveals that effective alignment-guided optimization remains unrealized in practice: cross-modal alignment does not improve during optimization despite increasing fitness, and the learned alignment is too coarse-grained for principled symbolic search. This serves as an important negative result guiding future hybrid approaches.

---

## 4. Immune-Inspired Computing

Immune-inspired computing has developed a formal mathematical equivalence with modern AI architectures that constitutes possibly the most significant conceptual breakthrough in biomimetic computing of the decade.

### 4.1 Mathematical Convergence of Adaptive Immunity and AI

In a landmark 2026 preprint, Sai T. Reddy demonstrates that the adaptive immune system and modern AI have independently converged on identical computational strategies for solving recognition and generalization. Four key equivalences:

| Immune System | AI Architecture | Equivalence Type |
|---|---|---|
| Boltzmann distribution (antibody-antigen binding) | Softmax in transformer attention | **Exact mathematical** |
| Clonal selection probability | InfoNCE contrastive loss | **Exact mathematical** |
| Germline → somatic hypermutation → T-follicular-helper | Pre-training → fine-tuning → RLHF | **Strategic convergence** |
| Long-lived plasma cells + memory B cells | Retrieval-augmented generation dual memory | **Strategic convergence** |

The paper argues that the mathematical structures of transformer attention and contrastive learning could have been derived from immunological first principles *before* their empirical discovery in AI.

### 4.2 Bio-RegNet: Homeostatic Neural Computing

The **Bio-RegNet** (2026) architecture integrates T-regulatory (Treg) cell-inspired immunoregulation with autophagic structural optimization into a meta-homeostatic Bayesian neural network. Three synergistic subsystems:

- **Bayesian Effector Network** — uncertainty-aware inference
- **Regulatory Immune Network** — Lyapunov-based inhibitory control
- **Autophagic Optimization Engine** — energy-efficient regeneration

Together these establish a closed energy-entropy loop achieving adaptive equilibrium. Across twelve benchmarks, Bio-RegNet enhanced calibration and energy efficiency by over **20%** and expedited recovery from perturbations by **14%** compared to state-of-the-art dynamic graph neural networks.

---

## 5. Epigenetic Information Encoding

Epigenetic information encoding has advanced along two complementary fronts: the use of epigenetic marks as computational bits, and the theoretical understanding of epigenetic memory.

### 5.1 Epigenetic DNA Data Storage

Research published in *Nature* demonstrates a strategy for writing arbitrary data onto DNA using **premade nucleic acids** — a paradigmatic shift away from de novo synthesis. Through self-assembly guided enzymatic methylation, epigenetic modifications serve as information bits precisely introduced onto universal DNA templates, achieving “molecular movable-type printing” in a parallel, programmable, and scalable modality. With 700 DNA movable types and five templates, approximately **275,000 bits** were written on an automated platform at **350 bits per reaction**.

### 5.2 Analog Epigenetic Memory

A 2025 study in *Cell Genomics* reveals that epigenetic memory is not strictly binary (on/off) but **analog**: chromatin modifications can maintain a continuous spectrum of gene expression levels over time. Distinct grades of DNA methylation produce corresponding, persistent expression levels, with DNA methylation acting as “the knob of a molecular dimmer switch” whose setting is conserved across cell divisions. Analog memory emerges specifically when the positive feedback loop between DNA methylation and the repressive H3K9me3 histone modification is absent.

A related 2025 study mapped DNA adenine methylation into linguistic Chinese character space, enabling the first semantic-level encoding of DNA into human language and revealing that DNA possesses an embedded redundant information storage mechanism supporting stable information transfer in liquid media.

### 5.3 Frameshift Encoding

A 2026 paper introduces a **frameshift-encoding** strategy inspired by ribosomal frameshifting in viruses: by designing DNA base sequences such that shifting the reading frame encodes additional information, multiple bits are extracted from a single sequence, achieving higher effective data density and enabling **DNA-hard-drive-like rewritability**.

---

## 6. Bioelectric Signaling

Bioelectricity — encompassing ion flows, voltage gradients, and electric fields across cell membranes — has been recognized as a fundamental, non-neural information-processing modality operating across all tissue types.

### 6.1 Bioelectric Collective Decision-Making

Landmark results published in *Nature* reveal that cells in epithelial tissues use bioelectricity to coordinate extrusion — the vital process of ejecting sick or struggling cells from the tissue. As tissue grows and cells become more tightly packed, the electrical current flowing through each cell’s membrane increases. A weak, old, or energy-starved cell cannot compensate for this increased current, triggering water efflux, cell shriveling, and marking for death. The work establishes that “bioelectricity is the earliest event during this cell-extrusion process,” making electrical signaling a fundamental coordination mechanism across all tissues, not merely neurons.

### 6.2 Biofilms as Bioelectric Networks

Researchers at the Universidad Complutense de Madrid demonstrated that bacterial biofilms exhibit a coordinated, synchronized shift in membrane potential (Vmem) upon exposure to the neurotransmitter glutamate — a behavior distinct from the independent responses of planktonic bacterial cells. These findings suggest that biofilms, much like neural networks, utilize dynamic and synchronized bioelectrical signals to process external stimuli, opening new avenues for understanding the microbiota-gut-brain axis.

### 6.3 Neuron-Bacteria Interkingdom Communication

A parallel study examined transcriptomic responses of neurons following short-term direct interaction with the probiotic bacterium *Lactiplantibacillus plantarum*. Neurons detect bacterial presence in the culture medium, triggering significant transcriptomic changes related to bioelectricity, excitability, and synaptic plasticity, with responses that are species-specific and modulated by interaction duration, concentration, and bacterial strain.

### 6.4 Bioelectric Reprogramming for Medicine

Researchers engineered a ferroelectric barium titanate-nanostructured titanium implant (ferroTi) that enables sequentially controlled bioelectric manipulation of macrophages. Under ultrasound activation, dynamic electrical signals activate voltage-gated Ca²⁺ channels to potentiate bacterial phagocytosis, while static inherent surface potentials polarize macrophages toward anti-inflammatory phenotypes promoting bone integration — a paradigm for spatiotemporally controlled, noninvasive bioelectric therapy.

### 6.5 Top-Down Bioelectric Control

A theoretical model published in *Scientific Reports* demonstrates that multicellular membrane potential patterns function as a **top-down control mechanism**: shifts in Vmem allow transitions between gene expression states, polarized cells can more effectively control distinct gene expressions than depolarized cells, and community effects extend single-cell control to the multicellular level. These predictions suggest that multiscale bioelectricity operates as an instructive signal in development and regeneration, potentially causally prior to biochemical signaling networks.

---

## Synthesis: Multiply Realized Biological Intelligence

These six biological and biomimetic domains reveal a consistent underlying theme: **biological intelligence is multiply realized across radically different substrates**.

- Ant colonies perform neuronal-like computations without neurons
- Mycelial networks execute cognitive functions without nervous systems
- Immune systems implement transformer-attention mathematics without deep-learning libraries
- Chromatin stores information in analog form without silicon transistors
- Bioelectric signals coordinate tissue-level decisions independent of synaptic connections
- Evolutionary algorithms increasingly mirror the hierarchical architectures of modern deep learning

The convergence of adaptive immunity and transformer attention — where an AI architecture’s core mathematical operation is demonstrably derivable from the biophysics of molecular recognition refined by 500 million years of evolution — suggests that certain computational strategies may be **fundamental to any system solving recognition and generalization under resource constraints**. Whether implemented in carbon- or silicon-based substrates, the underlying principles appear universal.

---

> **Disclaimer:** This report synthesizes findings from preprints, peer-reviewed publications, and research announcements from 2025–2026. Some sources are preprints that have not yet completed peer review, and their findings should be interpreted as preliminary. Some conceptual frameworks — particularly extended plant cognition through mycorrhizal networks — remain scientifically contested.

---

*GAIA-OS Canon · C98 · Committed 2026-04-28*
