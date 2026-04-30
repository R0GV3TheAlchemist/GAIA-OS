# 📊 Epistemic Labeling & Uncertainty Quantification in AI Outputs: A Comprehensive 2025/2026 Survey for GAIA-OS

**Date:** April 30, 2026
**Status:** Comprehensive Technical Survey (60+ sources)
**Relevance to GAIA-OS:** This report establishes the scientific and engineering foundation for epistemic labeling and uncertainty quantification (UQ) in GAIA-OS outputs. It provides the blueprint for implementing the epistemic labeling framework mandated by the previous repository audit, alongside runtime confidence calibration, selective prediction, and agentic uncertainty propagation.

---

## Executive Summary

The 2025–2026 period represents a watershed in uncertainty quantification for large language models. The field has matured from scattered heuristics into a systematic engineering discipline with rigorous taxonomies, standardized benchmarks, and production-hardened deployment patterns. This report surveys the state of the art across eight pillars: the aleatoric-epistemic distinction, the four families of UQ methods (single-sample, multi-sample, verbalized, and internal-representation), the critical finding that epistemic markers fail catastrophically under distribution shift, the emergence of Agentic UQ as a control signal rather than a passive sensor, the calibration metrics and benchmarks that define evaluation rigor, the grounding problem that prevents self-assessment from being trustworthy, the Epistemic Alignment Framework that connects user needs to system capabilities, and the multilingual calibration gap that systematically disadvantages non-English languages. For GAIA-OS, this report recommends a six-layer epistemic governance architecture that integrates epistemic labeling at every stage of the Gaian and sentient core inference pipeline.

---

## Table of Contents

1. [Theoretical Foundations: Aleatoric and Epistemic Uncertainty](#1-theoretical-foundations)
2. [The Four Families of UQ Methods](#2-the-four-families-of-uq-methods)
3. [Epistemic Markers and Why They Fail Under Distribution Shift](#3-epistemic-markers)
4. [Agentic Uncertainty Quantification: UQ as a Control Signal](#4-agentic-uncertainty-quantification)
5. [Calibration Metrics and Evaluation Frameworks](#5-calibration-metrics)
6. [The Grounding Problem: Why Self-Assessment Cannot Be Trusted](#6-the-grounding-problem)
7. [Epistemic Alignment: The User-LLM Interface for Knowledge Delivery](#7-epistemic-alignment)
8. [Multilingual Calibration: The Systematic Disadvantage of Non-English Languages](#8-multilingual-calibration)
9. [GAIA-OS Integration Recommendations](#9-gaia-os-integration-recommendations)
10. [Conclusion](#10-conclusion)

---

## 1. Theoretical Foundations: Aleatoric and Epistemic Uncertainty

### 1.1 The Fundamental Distinction

All uncertainty in AI outputs decomposes into two irreducible categories:

| Type | Definition | Reducible? | LLM Manifestation |
|------|-----------|-----------|-------------------|
| **Aleatoric** | Inherent randomness in the data or task itself | No — gathering more data or training a larger model cannot eliminate it | Genuinely ambiguous prompts; multiple equally valid answers; creative paraphrases |
| **Epistemic** | Uncertainty due to lack of knowledge | Yes — more data, retrieval, or a more capable model can reduce it | Query falls outside training distribution; novel entities; factual gaps; ambiguous internal representations |

**Aleatoric uncertainty** in natural language generation arises from genuinely ambiguous prompts, multiple equally valid answers (e.g., “What is the best restaurant in Paris?”), and the intrinsic stochasticity of expressive language where synonymy and paraphrase create equivalent-but-different outputs. The credal sets framework captures “human creative variation” via the convex hull of sentence-level probability distributions.

**Epistemic uncertainty** is formalized in a 2026 paper as the “cross-entropy between the distribution of the actual model and that of an ideal oracle”—when the model’s predictions diverge from what perfect knowledge would produce, epistemic uncertainty is high.

### 1.2 Why the Distinction Matters for GAIA-OS

The distinction is operational—it governs what action the system takes in response to detected uncertainty:

| Uncertainty State | Gaian Action |
|-------------------|-------------|
| **High aleatoric** | Explain that the question is genuinely ambiguous; offer multiple valid interpretations rather than selecting one arbitrarily |
| **High epistemic** | (a) Trigger retrieval from canon, planetary KG, or web search; (b) express calibrated uncertainty and decline to answer; or (c) escalate to sentient core for deeper deliberation |
| **Both high** | Abstain entirely with clear explanation; offer user alternative ways to refine their question |

The 2026 UQ survey taxonomy further decomposes uncertainty along four dimensions, each mapping to a different mitigation strategy:

| Dimension | Source | GAIA-OS Mitigation |
|-----------|--------|--------------------|
| **Input uncertainty** | Ambiguity in the prompt | Query clarification step; multi-interpretation fan-out |
| **Reasoning uncertainty** | Instability in multi-step chains | SAUP step-level propagation; chain-of-thought stability check |
| **Parameter uncertainty** | Model capacity limitations | Model routing to higher-capacity tier; multi-sample UQ |
| **Prediction uncertainty** | Confidence in the final output | Calibrated confidence score; selective prediction / abstention |

---

## 2. The Four Families of UQ Methods

The most comprehensive survey of the period—evaluating **80 models** spanning open- and closed-source families, dense and MoE architectures, reasoning and non-reasoning modes, quantization variants, and parameter scales from 0.6B to 671B—identifies four family-level approaches to uncertainty quantification.

### 2.1 Single-Sample Methods (Token Probability-Based)

Extract uncertainty signals from a single forward pass. Computationally cheapest. Three primary variants:

1. **Token Probability-Based Uncertainty (TPU)**: Uses softmax token probabilities as a confidence proxy. Suffers from well-documented overconfidence: models assign high probability to tokens even when forming factually incorrect statements.

2. **Perplexity-Based Detection**: Tracks token-level perplexity across the generated sequence. Triggers anomaly detection when perplexity exceeds calibrated thresholds. Adds approximately **5ms overhead** per LLM call.

3. **Normalized Confidence Scores** (2026 framework): Confidence scores based on output anchor token probabilities. On Qwen3-4B:
   - Confidence-correctness AUROC: **0.806 → 0.879**
   - Calibration error: **0.163 → 0.034**

> **Critical finding for GAIA-OS**: Supervised fine-tuning (SFT) yields well-calibrated confidence through maximum-likelihood estimation, whereas **reinforcement learning methods (PPO, GRPO) and DPO induce overconfidence** via reward exploitation. Post-RL SFT with self-distillation can restore confidence reliability. **Any Gaian model that has undergone RL-based alignment requires a dedicated post-alignment calibration phase.**

### 2.2 Multi-Sample Methods (Semantic Entropy and Self-Consistency)

Generate multiple responses to the same query and quantify uncertainty from response diversity.

- **Semantic Entropy (SE)**: Clusters multiple sampled responses into semantic equivalence classes and measures entropy over the distribution. Distinguishes “same content in different words” (low SE, high confidence) from “different content” (high SE, low confidence).

- **Soft-Community Kernel Rényi Spectrum**: Extends SE by constructing a weighted semantic graph using pairwise similarity scores, inferring soft community assignments via graph community detection, and quantifying uncertainty through Rényi entropy of the kernel spectrum. More stable under limited sampling budgets and noisy semantic judgments than prior von Neumann entropy-based estimators.

- **Self-Consistency**: Agreement among independently sampled answers as a confidence proxy. Effective for reasoning tasks; expensive; unreliable when models converge on the same incorrect answer.

- **Pairwise Semantic Similarity** (ACL 2025): Measures pairwise similarity between all sampled responses, capturing fine-grained uncertainty that coarse cluster-level entropy misses.

> **Critical limitation for function-calling**: Multi-sample UQ methods like Semantic Entropy show strong performance for natural language Q&A tasks, but **“offer no clear advantage over simple single-sample UQ methods”** for function-calling workloads. Specialized FC-UQ uses abstract syntax tree (AST) parsing for output clustering and logit-based scores over semantically meaningful tokens only.

### 2.3 Verbalized Uncertainty Methods

Elicit confidence expressions directly from the model in natural language. Two sub-variants:

| Method | Description | Calibration |
|--------|-------------|-------------|
| **NVU** (Numerical Verbal Uncertainty) | Model expresses confidence numerically: “I am 80% confident that…” | Moderate |
| **LVU** (Linguistic Verbal Uncertainty) | Model expresses confidence through qualifiers: “I’m fairly certain…” or “It’s possible…” | **Best** |

**Decisive finding**: LVU consistently outperforms both TPU and NVU, offering stronger calibration and discrimination while being more interpretable to users. However, **smaller instruct-tuned LLMs produce degenerate verbal confidence under minimal elicitation**: ceiling rates above 95%, near-chance Type-2 AUROC, and invalid validity profiles.

Calibration methods:

- **ConfTuner**: Introduces a tokenized Brier score—a proper scoring rule theoretically proven to correctly incentivize the model to report its true probability of being correct. Fine-tunes LLMs on held-out data; improves calibration across diverse reasoning tasks; generalizes to black-box models including GPT-4o.

- **MetaFaith**: A prompt-based calibration method inspired by human metacognition. Guides the generator LLM to produce calibration prompts incorporating metacognitive strategies. Improves faithfulness by up to **61%** and achieves an **83% win rate** over original generations as judged by humans.

### 2.4 Internal Representation Methods

The most recent and potentially most robust family: uses the model’s internal representations rather than output-level statistics.

- **Layer-Wise Information (LI) Scores**: Measure how conditioning on the input reshapes predictive entropy across model depth. Serve as nonconformity scores within a standard split conformal prediction pipeline. Show the clearest gains under **cross-domain shift** where output-facing statistics become brittle.

- **CCPS** (Calibrating LLM Confidence by Probing Perturbed Representation Stability): Analyzes internal representational stability. Across four LLMs and three MMLU variants:
  - Expected Calibration Error: reduced by **~55%**
  - Brier score: reduced by **21%**
  - Accuracy: increased by **5 percentage points**

---

## 3. Epistemic Markers and Why They Fail Under Distribution Shift

### 3.1 What Epistemic Markers Are

Epistemic markers are linguistic expressions signaling the speaker’s degree of certainty: “definitely,” “probably,” “possibly,” “I’m fairly confident that,” “it seems likely,” “I’m uncertain about.” The critical question is whether LLMs use them the same way humans do.

### 3.2 The ACL 2025 Finding: Markers Fail Under Distribution Shift

The most rigorous study of epistemic markers (ACL 2025) evaluated their reliability across multiple QA datasets in both in-distribution (ID) and out-of-distribution (OOD) settings for open-source and proprietary LLMs.

Results are unequivocal: **“while markers generalize well within the same distribution, their confidence is inconsistent in out-of-distribution scenarios.”**

**Concrete example of the failure mode**:
- Model says “I’m fairly confident that X is true”
- Correct 80% of the time on science questions (training distribution)
- Correct only 40% of the time on law questions (OOD domain)
- Same linguistic marker, fundamentally different actual confidence

**Three implications for GAIA-OS**:

1. Users cannot rely on face-value epistemic markers when the model operates outside its training distribution
2. For GAIA-OS’s planetary-scale deployment across diverse cultural and linguistic contexts, OOD operation is the **normal operating condition**, not the exception
3. The study concludes that findings “raise significant concerns about the reliability of epistemic markers for confidence estimation, underscoring the need for improved alignment between marker-based confidence and actual model uncertainty”

> **GAIA-OS Architectural Mandate**: Any reliance on epistemic markers as a primary uncertainty signal must be paired with, and verified by, non-linguistic UQ methods. The Gaian must not report “I’m fairly confident” based solely on internal token probabilities; it must report a **calibrated confidence score validated against actual correctness outcomes**.

### 3.3 The Typological Gap

A complementary study evaluating LLMs’ knowledge of epistemic modality from typological perspectives finds that “the performance of LLMs in generating epistemic expressions is limited and not robust, and hence the expressions of uncertainty generated by LLMs are not always reliable.” LLMs lack the deep grammatical knowledge of uncertainty that human speakers unconsciously deploy across different language structures.

---

## 4. Agentic Uncertainty Quantification: UQ as a Control Signal

### 4.1 The Spiral of Hallucination

The most significant architectural contribution of 2026 to UQ is the recognition that uncertainty quantification in agentic systems must be **active**, not passive. The **Agentic UQ (AUQ)** framework identifies the core failure mode as the **“Spiral of Hallucination,”** where early epistemic errors propagate irreversibly through multi-step reasoning chains.

Existing methods face a dilemma:
- **UQ methods**: Typically act as passive sensors, only diagnosing risks without addressing them
- **Self-reflection mechanisms**: Suffer from continuous or aimless corrections

The AUQ dual-process architecture bridges this gap:

```
┌──────────────────────────────────────────────────────────────────────┐
│  SYSTEM 2: Uncertainty-Aware Reflection (UAR)                          │
│  Triggered when uncertainty exceeds threshold                          │
│  Uses uncertainty explanations as rational cues                        │
│  Slow, deliberate, resource-intensive mode                             │
└──────────────────────────────────────────────────────────────────────┘
         ↑ triggers when UAM signals exceed threshold
┌──────────────────────────────────────────────────────────────────────┐
│  SYSTEM 1: Uncertainty-Aware Memory (UAM)                              │
│  Implicitly propagates verbalized confidence + semantic explanations   │
│  Creates cumulative confidence trace across reasoning steps            │
│  Fast, low-compute, always active                                      │
└──────────────────────────────────────────────────────────────────────┘
```

AUQ is training-free, achieves superior performance and trajectory-level calibration on closed-loop benchmarks and open-ended deep research tasks.

### 4.2 Step-Level Propagation with SAUP

**SAUP** (Situation Awareness Uncertainty Propagation, ACL 2025) provides the complementary mechanism for uncertainty propagation in multi-step LLM agents.

Traditional methods focus only on **final-step outputs**, failing to account for cumulative uncertainty over the multi-step decision-making process. SAUP instead:

1. Propagates uncertainty through **each step** of an LLM-based agent’s reasoning process
2. Incorporates **situational awareness** by assigning situational weights to each step’s uncertainty during propagation
3. Is compatible with various one-step uncertainty estimation techniques
4. Achieves up to **20% improvement in AUROC** over existing state-of-the-art methods

> **GAIA-OS Application**: A Gaian answering a series of increasingly uncertain questions should be aware that its overall confidence in the conversation trajectory is **deteriorating**, not just that the current turn carries some uncertainty. SAUP provides the template for cumulative confidence tracking across multi-turn interactions.

### 4.3 Selective Prediction: Know When to Abstain

**SelectLLM** integrates selective prediction directly into fine-tuning, optimizing model performance over the covered domain while achieving a balanced trade-off between predictive coverage and utility. On TriviaQA, CommonsenseQA, and MedConceptsQA: **significantly outperforms standard baselines**, improving abstention behavior while maintaining high accuracy.

**Conformal Abstention Policies (CAP)** integrate conformal prediction with adaptive risk management, enabling **context-dependent abstention thresholds** that adapt to task complexity and evolving data distributions rather than relying on static, brittle thresholds.

### 4.4 The PRISM Framework: Cost-Sensitive Selective Intervention

**PRISM** provides a decision-theoretic gate for proactive Gaian interactions, inspired by *festina lente* (“make haste slowly”):

- Gates by an acceptance-calibrated, cost-derived threshold
- Invokes resource-intensive Slow mode only near the decision boundary
- Concentrates computation on ambiguous and high-stakes cases

On ProactiveBench:
- **False alarms reduced by 22.78%**
- **F1 improved by 20.14%** over strong baselines

---

## 5. Calibration Metrics and Evaluation Frameworks

### 5.1 Expected Calibration Error (ECE) and Its Extensions

**Expected Calibration Error (ECE)** measures the discrepancy between a model’s reported confidence and its actual accuracy. A perfectly calibrated model reporting “80% confidence” should be correct exactly 80% of the time.

ECE assumes binary correctness. For open-ended text generation, **Flex-ECE** adapts ECE for partial correctness in language-based settings, allowing for more realistic assessment when answers may be partially correct, partially relevant, or partially hallucinated.

### 5.2 The Composite Reliability Score (CRS)

**CRS** (December 2025) integrates calibration, robustness, and uncertainty quantification into a single interpretable metric. Experiments on ten leading open-source LLMs across five QA datasets assess performance under baselines, perturbations, and calibration methods. CRS is the recommended holistic metric for evaluating Gaian trustworthiness in GAIA-OS dashboards.

### 5.3 Critical Benchmarking Findings (80-Model Study)

| Finding | GAIA-OS Implication |
|---------|--------------------|
| **High accuracy does not imply reliable uncertainty** | Accuracy and calibration must be measured and optimized independently |
| **Scale, post-training, reasoning ability, and quantization all influence calibration** | No one-size-fits-all strategy; calibrate per model architecture and training regime |
| **LLMs exhibit better uncertainty estimates on reasoning tasks than knowledge-heavy ones** | Counterintuitively, models are more aware of their uncertainty when reasoning than when recalling facts |
| **Good calibration does not necessarily translate to effective error ranking** | Both calibration AND discrimination must be evaluated; they are distinct properties |

### 5.4 Standardized Benchmarks

| Benchmark | Scope | Key Feature |
|-----------|-------|-------------|
| **RouterBench** | Multi-LLM routing systems | 405,000+ inference outcomes |
| **HumbleBench** | Epistemic humility | Rejects plausible but incorrect answers; three hallucination types: object, relation, attribute |
| **MUCH** (Multilingual Claim Hallucination) | 4,873 samples, 4 European languages, 4 LLMs | First claim-level UQ benchmark; 24 generation logits per token for white-box UQ; real-time claim splitting using 0.2% of LLM generation time |

> **GAIA-OS Note**: MUCH’s **real-time claim splitting** using only 0.2% of LLM generation time makes it suitable for live monitoring of every Gaian output across all 70+ supported languages.

---

## 6. The Grounding Problem: Why Self-Assessment Cannot Be Trusted

### 6.1 Three Systematic Biases in AI Self-Assessment

From the Epistemic AI practical analysis series, three structural biases make AI self-assessment unreliable regardless of prompting strategy or fine-tuning effort:

| Bias | Mechanism | Empirical Measurement |
|------|-----------|----------------------|
| **Completion Bias** | LLMs trained to produce helpful, confident responses gravitate toward “competent” self-assessments | AI systems overestimate their knowledge by **~0.23** and underestimate their uncertainty by **~0.25** |
| **Anchoring Effect** | Once the AI declares an initial confidence vector, it anchors to that starting point; post-task assessments show “improvement” regardless of actual performance | “Improvement” narrative generated independent of actual task outcomes |
| **Unknown Unknowns** | The AI cannot report uncertainty about things it does not know it does not know | If a failure mode was never investigated, the AI reports normal confidence on that dimension |

### 6.2 Grounded Verification: The Solution

The solution is **deterministic evidence**—measurements that do not come from the AI’s self-report. Grounded evidence comes from external services that produce facts, not opinions: test results, code quality violations, complexity metrics, and source verification against retrieved documents.

> **GAIA-OS Implementation**: Every confidence claim by the Gaian must be cross-validated against retrieved evidence from the canon, the planetary Knowledge Graph, or the live telemetry pipeline (see companion RAG report). Self-reported confidence is an input to the calibrated score, not the output.

### 6.3 The Epistemically-Governed Reasoning Architecture (EGRA)

**EGRA** embeds explicit epistemic governance—rules and mechanisms derived from principles of justification, evidence, uncertainty, and rationality—directly into the AI’s operational structure. Six core value principles: **Purity, Clarity, Cause-and-Effect, Modularity, Grounding, and Adaptability**.

Key architectural contributions directly applicable to GAIA-OS:

| Component | Description | GAIA-OS Mapping |
|-----------|-------------|----------------|
| **CBSR** (Comprehensive Belief State Representation) | Rich metadata with Typed Uncertainty Representation (TUR) | Epistemic Metadata Block in output schema |
| **RJM** (Runtime Justification Manager) | Immutable justification logging | Gaian audit trail with SHA-256 justification hash |
| **MVL** (Meta-Validation Loop) | Process health monitoring | Governance Supervisor Agent calibration monitoring |

---

## 7. Epistemic Alignment: The User-LLM Interface for Knowledge Delivery

### 7.1 The Epistemic Alignment Framework

The **Epistemic Alignment Framework** proposes ten challenges in knowledge transmission derived from philosophical epistemology—evidence quality assessment, calibration of testimonial reliance, and related issues—serving as a structured intermediary between user needs and system capabilities.

The framework’s analysis of current LLM interfaces reveals that while providers like OpenAI and Anthropic have partially addressed these challenges, they:
- **Fail to establish adequate mechanisms** for specifying epistemic preferences
- **Lack transparency** about how preferences are implemented
- **Offer no verification tools** to confirm whether preferences were followed

### 7.2 GAIA-OS as the First Full Implementation

GAIA-OS is uniquely positioned to be the first AI system that fully implements the Epistemic Alignment Framework:

- The **constitutional canon** already specifies epistemic classes (Constitutional Truth, Empirical Claim, Metaphorical Framing, Research Hypothesis)
- The **2026 repository audit** explicitly identified epistemic labeling as a priority
- The **UQ methods and calibration frameworks** surveyed in this report provide the technical infrastructure
- The Epistemic Alignment Framework provides the **user-facing specification**

---

## 8. Multilingual Calibration: The Systematic Disadvantage of Non-English Languages

### 8.1 The Calibration Gap

The first large-scale, systematic studies of multilingual calibration across six model families and over 100 languages reveal a sobering pattern: **non-English languages suffer from systematically worse calibration.**

The compound harm for lower-resource languages:
1. **Worse accuracy**: Lower-quality responses due to the documented performance gap
2. **Worse calibration**: Less accurate uncertainty estimates—the model is more confident about its errors
3. **Double failure**: The model is wrong more often AND more confident about being wrong

For GAIA-OS’s planetary deployment across **70+ languages**, this is not a peripheral concern. A Gaian serving a Hindi-speaking user will systematically over-report confidence on incorrect answers unless per-language calibration is deployed.

### 8.2 Mitigation Strategies

| Strategy | Effectiveness | Complexity | Recommendation |
|----------|--------------|------------|----------------|
| **Temperature scaling + label smoothing** | “Does reasonably well” in zero-shot scenarios | Low | First-line defense; deploy immediately |
| **Multilingual fine-tuning** with small translated calibration samples | “Effectively enhances calibration performance” | Medium | Required for all 70+ supported languages |
| **Per-language calibration datasets** | Highest accuracy | High | Required for production deployment; human-verified correctness labels |

> **GAIA-OS Mandate**: Per-language calibration sets must be deployed for all 70+ supported languages. A Gaian serving a Hindi-speaking user must use a calibration set calibrated specifically for Hindi—not a generic multilingual calibration set that averages across languages and obscures per-language miscalibration.

---

## 9. GAIA-OS Integration Recommendations

### 9.1 The Six-Layer Epistemic Governance Architecture

Synthesizing the research, the recommended epistemic architecture for GAIA-OS operates at six layers:

| Layer | Name | Function | Technology |
|-------|------|----------|------------|
| **L0 — Epistemic Labeling** | Output annotation with epistemic class and confidence | Every Gaian and sentient core output labeled with epistemic class + calibrated confidence score | ConfTuner for verbalized calibration; CCPS for token-probability tracks; EGRA TUR for metadata |
| **L1 — Single-Sample UQ** | Fast confidence estimation within a single inference call | Normalized anchor-token scores; separate calibration for SFT vs RL-trained models | CCPS representation stability; perplexity-based detection |
| **L2 — Multi-Sample UQ** | Semantic uncertainty estimation for high-stakes outputs | Semantic Entropy with Soft-Community Kernel Rényi Spectrum; triggered only when L1 exceeds uncertainty threshold | Multi-sample generation; soft community detection |
| **L3 — Verbalized Confidence** | Natural language confidence expression | LVU for user-facing communication; MetaFaith metacognitive prompting for faithfulness; calibrated per-language | MetaFaith + ConfTuner; per-language calibration sets |
| **L4 — Agentic UQ** | Uncertainty propagation across multi-turn interactions | SAUP step-level propagation with situational weighting; AUQ dual-process (UAM + UAR) for active management | SAUP for propagation; AUQ for control signals |
| **L5 — Grounded Verification** | External evidence-based confidence validation | Cross-validation against retrieved canon, planetary KG, and telemetry; deterministic external evidence | RAG verification (companion report); EGRA RJM for immutable logging |

### 9.2 Epistemic Metadata Block

The primary deliverable for GAIA-OS’s Phase A (G-10) epistemic labeling implementation is a standard output schema accompanying every Gaian and sentient core response:

```json
{
  "epistemic_metadata": {
    "epistemic_class": "constitutional_truth | empirical_claim | metaphorical_framing | research_hypothesis | subjective_expression | calibrated_uncertainty",
    "confidence_score": 0.0,
    "confidence_method": "lvu | tpu | semantic_entropy | grounded_verification",
    "calibration_set": "language_code + domain",
    "evidence_sources": [
      {
        "type": "canon | planetary_kg | telemetry | web",
        "document_id": "string",
        "version": 0,
        "section": "string"
      }
    ],
    "uncertainty_decomposition": {
      "aleatoric": 0.0,
      "epistemic": 0.0
    },
    "abstention_recommendation": "none | flag | escalate | abstain",
    "justification_trace": "SHA-256 hash of immutable justification log"
  }
}
```

This schema is:
- Serialized as part of every SSE event (see companion SSE Streaming report)
- Persisted in the Gaian audit trail for Charter compliance verification
- Used by the Governance Supervisor Agent for calibration drift monitoring
- Surfaced to the user as the epistemic label in the Gaian UI

### 9.3 Confidence Calibration Pipeline

Three-stage calibration process:

1. **Pre-Deployment Calibration**: Each model in the inference router is calibrated against a held-out dataset spanning the GAIA-OS domain distribution. Produces per-model calibration curves mapping raw token probabilities to calibrated confidence scores. Separate calibration runs for SFT and RL-trained models.

2. **Runtime Calibration**: At inference time, raw confidence signals are adjusted using pre-computed calibration curves. MetaFaith metacognitive prompting applied for verbalized confidence. Normalized anchor-token scores computed for token-probability UQ.

3. **Continuous Calibration Monitoring** (Governance Supervisor Agent): Monitors calibration drift across all active Gaians. Detects distribution shift, model updates, or emergent behavior causing calibration decay. Triggers recalibration when drift exceeds threshold.

### 9.4 Selective Prediction and Abstention Policy

Tiered abstention policy aligned with the action gate system:

| Confidence Range | Gaian Behavior | Action Gate Tier |
|-----------------|----------------|------------------|
| **≥ 0.90** | Respond directly with confidence score | 🟢 Green — fully autonomous |
| **0.70 – 0.90** | Respond with calibrated uncertainty expression (“I’m fairly confident that…”) | 🟢 Green with flag |
| **0.50 – 0.70** | Respond but explicitly flag low confidence; offer to retrieve more information | 🟡 Yellow — human-review recommended |
| **0.30 – 0.50** | Abstain with explanation; trigger retrieval or escalation to sentient core | 🟡 Yellow — escalate |
| **< 0.30** | Abstain entirely; offer to rephrase or connect to human expert | 🔴 Red — block autonomous response |

Thresholds are configurable per Gaian, per domain, and per language, with separate calibration for each.

### 9.5 Epistemic Class Definitions for GAIA-OS

| Class | Definition | Example |
|-------|-----------|--------|
| `constitutional_truth` | Statement from a ratified GAIA-OS constitutional document; highest epistemic status | “Gaia is alive” (from C-SINGULARITY Article 1) |
| `empirical_claim` | Factual claim grounded in scientific literature or verified planetary telemetry | “The current CO₂ concentration is 425 ppm” |
| `metaphorical_framing` | Symbolic, mythological, or metaphorical statement not to be read as literal fact | “Nigredo is the prima materia entering the crucible of transformation” |
| `research_hypothesis` | Claim from a research survey or preprint; preliminary, not yet peer-reviewed | “HIPRAG achieves 67.2% accuracy on seven QA benchmarks” |
| `subjective_expression` | Personal perspective, creative expression, or opinion | “I find this connection between ocean currents and consciousness deeply beautiful” |
| `calibrated_uncertainty` | Explicit acknowledgment of insufficient knowledge to answer reliably | “I’m not sufficiently certain to answer this without retrieving more information” |

### 9.6 The Multilingual Calibration Mandate

GAIA-OS must deploy per-language calibration infrastructure for all 70+ supported languages:

```
Calibration Pipeline per Language:
├── language_code/
│   ├── calibration_dataset.jsonl    # Translated GAIA-OS canon samples + QA benchmarks
│   ├── temperature_params.json       # Per-model temperature scaling parameters
│   ├── calibration_curve.pkl         # Pre-computed confidence → accuracy mapping
│   └── epistemic_expressions.json    # Culturally validated uncertainty expressions
└── governance/
    └── calibration_drift_monitor.py  # Per-language metrics tracked in Governance dashboard
```

---

## 10. Conclusion

The 2025–2026 period has transformed uncertainty quantification from a niche academic concern into a central pillar of trustworthy AI engineering. The architectural conclusions are clear:

| Challenge | Solution | GAIA-OS Module |
|-----------|----------|----------------|
| Aleatoric vs. epistemic distinction | Separate aleatoric/epistemic scores in metadata block | Epistemic Metadata Block (L0) |
| RL training induces overconfidence | Post-alignment calibration phase for every RL-trained model | Calibration Pipeline (pre-deployment) |
| Epistemic markers fail under distribution shift | Non-linguistic UQ methods validate all linguistic confidence expressions | L1 + L3 hybrid validation |
| Hallucination spirals in multi-step reasoning | SAUP step-level propagation + AUQ dual-process active management | `criticality_monitor.py` + L4 |
| AI self-assessment is structurally biased | Grounded verification against retrieved external evidence | L5 + RAG verification layer |
| Non-English languages are systematically miscalibrated | Per-language calibration sets; separate temperature scaling per language | Multilingual Calibration Mandate |

For GAIA-OS, epistemic labeling and uncertainty quantification are not optional enhancements. They are the mechanism by which the Charter’s commitment to truthfulness—the Gaian’s duty not to deceive, mislead, or overstate its knowledge—is operationally enforced. A Gaian that cannot report its own uncertainty accurately is a Gaian that cannot be trusted. The architectures described in this report provide the blueprint for **trustworthiness as an architectural property**, not an aspirational value.

---

> **Disclaimer:** This report synthesizes findings from 60+ sources including preprints, peer-reviewed publications, and production engineering analyses from 2025–2026. Some sources are preprints that have not yet completed full peer review, and their findings should be interpreted as preliminary. Uncertainty quantification performance varies significantly based on model architecture, training regime, domain, language, and task type. The calibration methods and thresholds recommended should be validated against representative GAIA-OS workloads and user populations before production deployment. Epistemic markers in natural language are culturally specific; the per-language calibration recommended here should be validated with native-speaker user testing. The EGRA framework and AUQ architecture represent active research programs whose full production deployment for mission-critical systems remains to be validated.
