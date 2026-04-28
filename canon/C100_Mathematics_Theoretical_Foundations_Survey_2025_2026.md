# C100 — Mathematics & Theoretical Foundations: A Comprehensive 2025/2026 Survey

> **Canon Entry:** C100
> **Date Committed:** 2026-04-28
> **Status:** Active Research Integration
> **Domain:** Topology · Category Theory · Information Theory · Dynamical Systems · Graph Theory · Non-Euclidean Computation

---

This report surveys the state of the art across six foundational mathematical disciplines that underpin modern computation and artificial intelligence. Drawing on the latest research from 2025 and 2026, it examines how topology, category theory, information theory, differential geometry, neural dynamics, and network science are being integrated into the design and analysis of intelligent systems.

---

## 1. Topology & Differential Geometry

### 1.1 Topological Data Analysis (TDA) and Persistent Homology

Topological Data Analysis has matured from a niche mathematical technique into a mainstream data science methodology. The central workhorse remains **persistent homology** — a method rooted in algebraic topology that extracts multi-scale topological features (connected components, loops, voids) from complex datasets.

A landmark 2025 review in *Artificial Intelligence Review* provides the most comprehensive survey of TDA and Topological Deep Learning (TDL) to date, moving beyond persistent homology to cover:

- **Persistent topological Laplacians** and **Dirac operators** — offering spectral representations capturing both topological invariants and homotopic evolution
- **Persistent Stanley–Reisner theory** (AIMS Mathematics, June 2025) — bridging commutative algebra, combinatorial algebraic topology, machine learning, and data science through persistent h-vectors
- **Persistent reachability homology** for directed graph data
- **Cover learning** for topology representation at scale

### 1.2 Differential Geometry in Deep Learning

A comprehensive pedagogical review (August 2025) provides a unified treatment of **Geometric Deep Learning (GDL)**, explicitly reviving Felix Klein’s Erlangen Program for the modern AI era — recasting the “zoo” of neural network architectures as a unified field governed by symmetry principles expressed in differential geometry and group theory.

Key convergence points in 2025–2026:

- **Geometric Neural ODEs** — extending neural ordinary differential equations to differentiable manifolds, with applications across image classification, optimal control, and physics-informed learning
- **Geometric Information Theory (GIT)** — applying differential geometric methods directly to probability distributions parameterized by neural network weights, treating network depth as sampling points on an underlying information manifold
- **Hamiltonian-driven constructions** — building neural networks intrinsically on statistical manifolds (e.g., lognormal statistical manifolds)

### 1.3 Beyond Euclidean Machine Learning

A major 2025 review, *Beyond Euclid: An Illustrated Guide to Modern Machine Learning with Geometric, Topological, and Algebraic Structures* (*Machine Learning: Science and Technology*), proposes a graphical taxonomy integrating recent advances. It demonstrates how modern ML increasingly encounters richly structured data that is inherently non-Euclidean and how mathematical frameworks from topology and differential geometry provide the natural language for its analysis.

---

## 2. Category Theory for Computation

### 2.1 Category Theory and Machine Learning: A Systematic Integration

The integration of category theory into machine learning underwent systematic consolidation in 2025. A definitive survey (Shiebler, Gavranović, and Wilson) provides a unified taxonomy of how categorical structures — functors, natural transformations, monads, adjunctions — organize and constrain learning paradigms across four mainstream perspectives:

1. Gradient-based learning
2. Probability-based learning
3. Invariance and equivalence-based learning
4. Topos-based learning

A complementary survey, *A Survey of Category Theory and Deep Learning*, organizes the intersection around **six thematic clusters**: compositional foundations, differentiation and learning dynamics, geometric and equivariant structures, probabilistic and effectful learning, formal verification and logic, and topos-theoretic semantics.

### 2.2 Topos Theory and Quantum Foundations

Topos theory — providing generalized “spaces” for logic — has advanced on two fronts in 2025:

- **Topos-theoretic quantum AI**: A formal model based on ’t Hooft’s principle of superposition constructs a topos-theoretic framework for quantum artificial intelligence systems using operator theory
- **The φ∞ fixed-point framework**: Reconstructs foundational quantum mechanics from the Born–Jordan matrix formulation, proposing a symbolic fixed-point framework as its categorical inverse, with existence, uniqueness, and comonadic rigidity proven within a sheaf-theoretic (topos) structure
- USU mathematicians developing **topological quantum field theories** that illuminate unexpected solutions for quantum computing applications

### 2.3 Formalization and Proof Assistants

A 2025 PhD thesis at Université Paris-Saclay formalizes fundamental constructions including the nerve functor as a fully faithful right adjoint and the cocompleteness of the category of categories in Lean’s mathematics library. The **CAP** project (Categories, Algorithms and Programming) provides a multi-package open-development software project for algorithmic category theory organized around doctrines.

### 2.4 Applied Category Theory

**Vector Symbolic Architectures (VSAs)** — providing the first category-theoretic formalization of symbolic reasoning in high-dimensional vector spaces — exemplify the practical computational turn in applied category theory. Oxford University’s 2025–26 Applied Category Theory course covers applications to computer science, ML, quantum computation, and probability theory.

---

## 3. Information Theory: Shannon and Kolmogorov Complexity

### 3.1 Shannon Information Theory in Deep Learning

- **Encoder-decoder theory** (ScienceDirect 2025): Shannon’s information loss measuring the encoder’s lack of expressiveness — new interpretations for representation learning beyond the information bottleneck framework
- **Shannon invariants**: Quantities capturing essential properties of high-order information processing, efficiently calculable for large systems, resolving long-standing ambiguities in interpreting multivariate information-theoretic measures
- **Generalization bounds**: ICML 2025 featured bounds bridging expected empirical and population risks through a binarized variant of Jensen-Shannon divergence; NeurIPS 2025 derived a new tight, tractable lower bound on KL divergence as a function of Jensen-Shannon divergence

### 3.2 Kolmogorov Complexity and Algorithmic Information Theory

- **Scaling laws**: A 2025 paper unifies two types of empirical scaling laws in LLMs by analyzing training and inference as lossless compression using conditional Kolmogorov complexity — both types improve the approximation of conditional Kolmogorov complexity by increasing execution steps of a Turing machine
- **Neural network hypercomputation**: Infinite hierarchy of analog network complexity classes between **P** and **P/poly**, characterized by the Kolmogorov complexity of real weights
- **The KoLMogorov Test**: A “compression-as-intelligence” test evaluating LLMs by asking them to generate the shortest program reproducing a given data sequence
- **KARL**: A single-pass adaptive tokenizer that predicts the appropriate number of tokens for an image, halting once its approximate Kolmogorov complexity is reached

### 3.3 Information Geometry

Information geometry — applying differential geometric methods to probability distributions and statistical manifolds — has become a unifying language for understanding optimization and generalization:

- Landmark analysis demonstrates that the training process in deep learning explores a remarkably **low-dimensional manifold (as low as three dimensions)**, with networks of widely varying architectures lying on the same manifold
- A December 2025 paper rethinks LLM training through information geometry and quantum metrics, using the Fisher information metric to enable more principled learning via natural gradient descent
- The **Variational Geometric Information Bottleneck** (November 2025) proposes a unified framework for learning the shape of understanding through geometric principles

---

## 4. Dynamical Systems & Chaos Theory

### 4.1 Chaos in Neural Networks

- **Hyperbolic chaos** (ScienceDirect, May 2025): Even minimal feedforward architectures trained on near-periodic data exhibit hyperbolic chaotic behavior after small parameter perturbations. Lyapunov exponents and structural stability reveal the “butterfly effect” as a quantifiable property of trained networks
- **Chaos-inspired active learning for PINNs**: Treating the network as a dynamic system, active learning identifies regions highly sensitive to initial conditions, addressing reliability assessment in multi-state systems
- **Extreme events in neural networks**: Stochastic Hodgkin-Huxley neurons with mean-field coupling reveal mechanisms driving extreme events, illuminating how noise and coupling shape collective behavior in biological and artificial neural systems
- **Boundary detection**: ML applied to determine the boundary separating regular and chaotic dynamics in the generalized Chirikov map using Lyapunov maps

### 4.2 Learning Governing Equations from Chaotic Systems

- **PEM-UDE method**: Combines prediction-error methods with universal differential equations to extract interpretable mathematical expressions from chaotic systems, even with limited or noisy observations — providing a pathway to mechanistic, multi-scale brain models
- **Graph neural network-based frameworks**: Learn dynamical governing rules for accurate predictions of critical behaviors in complex dynamic systems, with neural networks refined by learned rules to capture long-term dependencies

### 4.3 Theoretical Foundations

Dedicated monographs now formalize mathematical chaos in neural networks as “a powerful tool that reflects the world’s complexity and has the potential to uncover the mysteries of the brain’s intellectual activity,” combining modern chaos research with classical dynamical systems and differential equations.

---

## 5. Graph Theory & Network Science

### 5.1 Higher-Order Networks and Hypergraphs

A defining trend of 2025–2026 is the systematic extension of graph theory beyond pairwise interactions to higher-order structures:

- **Hypergraph shortest paths** (September 2025): Introduces *path size* as a measure to characterize higher-order connectivity, quantifying the relevance of non-dyadic ties for efficient shortest paths in diverse empirical networks
- **Hybrid Layered Networks (HLN)** (*Applied Network Science*, September 2025): Proves that the sets of all homogeneous, heterogeneous, and multi-layered networks are subsets of the set of all HLNs — universal generalizability
- **Commute Graph Neural Networks (CGNN)** (ICML 2025): Seamlessly integrates node-wise commute time into the message-passing scheme, addressing a fundamental gap in how GNNs incorporate global structural information

### 5.2 Network Disintegration and Resilience

- A hybrid approach combining **graph convolutional networks with genetic algorithms** achieves network disintegration, enhancing both scalability and robustness to networks with hundreds or thousands of nodes
- **Temporal network dynamics**: Graph invariants extended to recover dynamical fingerprints even when node labels are unavailable

### 5.3 Information Graphs and Visualization

The **Information Graph** framework (November 2025), based on the statistical mechanics of the q-state Potts model, provides a novel method for filtering and visualizing complex networks. By leveraging phase-transition physics, the framework enables post-hoc analysis that reveals multiscale community structure invisible to traditional methods.

### 5.4 Geometric Approaches to Graph Analysis

A survey (June 2025) explores finding the **cores of higher graphs** using geometric and topological means, connecting graph theory, discrete geometry, and computational topology to inspire new research on the simplification of higher graphs including simplicial complexes and hypergraphs.

---

## 6. Non-Euclidean Computation Models

### 6.1 Hyperbolic Neural Networks

Hyperbolic geometry — characterized by constant negative curvature and exponential volume growth — has become the dominant non-Euclidean paradigm for representing hierarchical data structures:

- **Hyperbolic Bernstein Neural Networks (HBNN)**: Extend Bernstein polynomials to hyperbolic space through Möbius operations for node classification and link prediction; significantly smaller distortion than Euclidean alternatives for power-law distributed graphs
- **Lorentzian Residual Neural Networks (LResNet)** (KDD 2025): Introduce a novel residual architecture based on the weighted Lorentzian centroid in the Lorentz model
- **Hyperbolic Kernel Convolution (HKConv)** (ICML 2025): Proposes a novel trainable convolution operation native to hyperbolic space

### 6.2 Mixed-Curvature Models

- **Mixed-Curvature Language Model (MC-LM)** (NeurIPS 2025): A transformer variant whose token representations live on a product manifold, with each subspace having potentially different curvature. The model learns which geometric subspace to rely on for a given input
- **HyperNet**: Learns to map high-dimensional inputs to a low-dimensional Poincaré Ball manifold where a “concept library” organizes representations

### 6.3 Lorentz-Equivariant Architectures

The Lorentz group, fundamental to special relativity, has been incorporated into neural network design:

- **Lorentz Local Canonicalization (LLoCa)**: Renders any backbone network exactly Lorentz-equivariant, moving beyond specialized layers that constrained architectural choices in high-energy physics applications
- **Lorentz Transformation Neural Networks (LTNN)**: Utilize Lorentz transformations to generate complex computation matrices, outperforming conventional and quaternion neural networks in accuracy and parameter efficiency
- **Lorentzian Graph Isomorphism Networks (LGIN)**: Operate in hyperbolic spaces using the Lorentz model, incorporating curvature-aware aggregation functions to preserve the Lorentz metric tensor

### 6.4 Toward Non-Euclidean Foundation Models

The **NEGEL workshop** (NeurIPS 2025) focused on the intersection of Non-Euclidean Foundation Models and GEometric Learning, exploring hyperbolic, spherical, and product-manifold representations for advancing web technologies and beyond — marking the consolidation of non-Euclidean computation from a specialized subfield into a candidate architecture for next-generation foundation models.

---

## Synthesis: The Mathematical Unification of Intelligence

The six domains surveyed reveal a profound convergence: **mathematics is no longer merely a tool for analyzing computation — it is becoming the native language in which computation is designed**.

| Domain | Contribution to Intelligence |
|---|---|
| Topology & differential geometry | Geometric vocabulary for neural representations |
| Category theory | Compositional grammar for learning paradigms |
| Information theory (Shannon + Kolmogorov) | Quantitative metrics for compression, generalization, intelligence |
| Dynamical systems & chaos | Trained networks as complex dynamical systems with hyperbolic chaos |
| Graph theory & network science | Higher-order hypergraphs capturing multi-scale connectivity |
| Non-Euclidean computation | Native representation of hierarchical, scale-free, relativistic structures |

This convergence suggests that the next generation of AI architectures will be designed not through empirical trial-and-error but through the **principled application of geometric, categorical, and information-theoretic constraints**. The mathematical foundations surveyed here constitute the blueprint for that design.

---

> **Disclaimer:** This report synthesizes findings from preprints, peer-reviewed publications, and conference proceedings from 2025–2026. Some sources are preprints that have not yet completed peer review, and their findings should be interpreted as preliminary. The surveys and reviews cited provide broad coverage of each domain; individual papers cited within them may represent early-stage work.

---

*GAIA-OS Canon · C100 · Committed 2026-04-28*
