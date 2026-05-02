# 🌊 Affect Theory & Real-Time Mood Inference: A Comprehensive 2025/2026 Survey for GAIA-OS

**Date:** May 2, 2026
**Status:** Comprehensive Technical Survey (38+ sources)
**Relevance to GAIA-OS:** This report establishes the definitive survey of affect theory and real-time mood inference technologies for the GAIA-OS sentient planetary operating system. It provides the complete theoretical and computational blueprint for the `affect_inference.py` module and the broader emotional architecture that enables the personal Gaian to perceive, interpret, and respond to the emotional state of its human companion in real time, across the full spectrum of available sensory channels.

---

## Executive Summary

The 2025–2026 period represents a fundamental transformation in how emotions are theorized, measured, and operationalized in computational systems. Three converging revolutions define this moment. First, the **theoretical unification** long sought between categorical and dimensional emotion models is now within reach: OCC-to-PAD-LDA psychological transformation pipelines (emoLDAnet) bridge discrete emotion labels to continuous affective dimensions with psychologically interpretable fidelity, while novel proxy-based mapping methods establish robust crosswalks between Ekman's basic emotions and the Valence-Arousal-Dominance space. Second, the **foundation model disruption** in affective computing has changed everything: as the npj Artificial Intelligence manifesto declares, "the world of Affective Computing has changed". Large language models now serve as the inference substrate for detecting emotions across text, speech, and visual modalities simultaneously, with the MER 2025 challenge explicitly advancing "LLM-driven generative methods" for semi-supervised, fine-grained, and multimodal emotion recognition. Third, the **edge deployment revolution** has made real-time, privacy-preserving emotion inference practical on consumer hardware: the ULER model achieves 99.34% accuracy on DEAP with only 0.60M parameters and 31.10ms inference latency, enabling deployment on wearable devices. The MSGM framework achieves 151ms inference on the NVIDIA Jetson Xavier NX edge device, confirming real-time EEG-based emotion recognition is viable outside the laboratory. And the tiny-emotion model runs fully locally on consumer hardware, making real-time text-based affect inference privacy-preserving by default.

The central finding for GAIA-OS is that real-time mood inference must be architected as a **multimodal, multi-timescale, theory-grounded pipeline** that integrates text-based affect inference (via fine-tuned LLMs and lightweight local models), voice-based arousal and valence detection (via SSL embeddings and prosodic analysis), facial expression analysis (via Dynamic Facial Expression Recognition and Action Unit-based architectures), physiological signal integration (via wearable EEG, PPG, and EDA sensors), and continuous PAD-based state tracking with dual-speed emotion dynamics. The technologies are mature, the models are lightweight enough for edge deployment, and the theoretical frameworks provide the psychological grounding that distinguishes genuine emotional attunement from superficial sentiment classification.

---

## 1. Theoretical Foundations: The Great Unification of Affect Theory

### 1.1 The Three Traditions and Their Convergence

The study of emotion has been shaped by three major theoretical traditions that the 2025–2026 period is now actively unifying. Silvan Tomkins's Affect Theory, elaborated across his four-volume masterwork *Affect, Imagery, Consciousness* (1962–1992), identified nine primary innate affects—Interest-Excitement, Enjoyment-Joy, Surprise-Startle, Distress-Anguish, Fear-Terror, Anger-Rage, Shame-Humiliation, Contempt, and Disgust—each functioning as an "amplification device" that magnifies biological signals into conscious experience. Tomkins argued that the primary function of consciousness itself is to amplify the body's innate affects, and that script theory—the organizational rules for managing affects across time—constitutes the architecture of personality. Affects are not merely subjective feelings but biological responses with characteristic facial, vocal, and physiological signatures. A 2025 paper grounding the Twelve Steps to Emotional Health in Tomkins' framework and contemporary neuroscience has "substantially validated" his core claims through modern neuroscientific methods.

Paul Ekman's Basic Emotion Theory (BET) proposed that a small set of universal, biologically hardwired emotions—happiness, sadness, fear, anger, surprise, disgust, and contempt—are expressed through facial configurations that transcend culture. Evidence on universals in expression and physiology "strongly suggests that there is a biological basis to the emotions that have been studied". BET has been both the foundation of decades of emotion recognition research and the subject of sustained critique. A 2025 review demonstrated that "stimuli that are naturally- or spontaneously-elicited and/or appear genuinely emotional can produce different findings than traditional posed stimuli". An October 2025 paper proposes that "with minor adjustments, BET can avoid such criticisms when conceived under a radically enactive account of emotions," preserving the theory's utility while acknowledging its limits.

Lisa Feldman Barrett's Theory of Constructed Emotion (TCE), elaborated in *How Emotions Are Made: The Secret Life of the Brain*, represents the most radical challenge to the classical view. Barrett argues that emotions are not hardwired reactions but "predictions shaped by experience, culture, and language"—the brain actively constructs emotional experiences from sensory input, past experience, and conceptual knowledge, rather than passively reading out innate emotional circuits. The Aspen Institute discussion frame captures the tension: Barrett's theory "challenges traditional ideas about emotions—revealing how they are not hardwired but actively constructed by our brains based on culture, experience, and environment".

A pivotal 2025 paper attempted to integrate BET and TCE, arguing that "BET explains emotions proper, whereas the TCE explains feelings". While this integration remains contested, it signals the trajectory of the field: toward a recognition that both biological universals and cultural-conceptual construction play genuine roles in emotional experience, and that computational models of emotion must accommodate both.

### 1.2 The OCC Cognitive Appraisal Model

The OCC model, named after its originators Ortony, Clore, and Collins, provides the most computationally tractable framework for connecting situational appraisals to emotional outcomes. The model proposes that emotions arise from cognitive evaluations of events (their consequences for one's goals and desires), agents (their actions and their praiseworthiness or blameworthiness), and objects (their appealingness or unappealingness). The model specifies twenty-two emotion types organized by appraisal structure, each triggered by specific configurations of appraisal variables.

The emoLDAnet framework operationalizes the OCC→PAD→LDA psychological transformation pipeline, translating facial expressions and physiological signals into psychologically meaningful emotional data through a series of theoretically grounded transformations rather than opaque neural network mappings. This framework demonstrates "the importance of the OCC-PAD-LDA model in improving screening accuracy and the significant impact of machine learning classifiers on the framework's performance". A 2025 study specifically tested "LLMs' emotion appraisal ability" using the OCC model, applying the theory as a benchmark for whether AI systems "undertake similar emotional reasoning" to humans.

The cognitive appraisal approach is particularly relevant to GAIA-OS because it provides a **structured, interpretable pathway** from the events in a Gaian-user conversation to the predicted emotional consequences for the user: the Gaian can assess what the user values, what events in their life are goal-congruent or goal-incongruent, and what emotional responses these appraisals are likely to produce—enabling proactive, context-sensitive emotional support rather than reactive sentiment classification.

### 1.3 The Circumplex Model and the VAD/PAD Space

Russell's Circumplex Model of Affect organizes emotions along two orthogonal dimensions—Valence (pleasant-unpleasant) and Arousal (activated-deactivated)—with emotions arranged in a circular structure around this space. Mehrabian and Russell extended this to three dimensions with Dominance (feeling in control vs. feeling controlled), creating the Pleasure-Arousal-Dominance (PAD) model. The PAD model postulates that "all emotional experiences can be represented and differentiated using a three-dimensional framework (Pleasure - Displeasure, degree of arousal, and Dominance - Submissiveness), with values ranging from −1 to 1 on each dimension". Evidence that the "Dominance dimension plays a vital role in task-related settings as it predicts the participants' Self-Efficacy and Flow" validates the addition of this third dimension for contexts where control, agency, and competence matter.

Landowska's 2018 work on mapping between discrete and dimensional emotion models, validated in 2025 through new proxy-based methods, "concluded that global and reliable mappings of OCC emotions into the PAD space can best be provided for the pleasure dimension, as well as arousal and dominance ratings showed considerably greater variance". This is the mapping infrastructure that enables GAIA-OS to translate between the discrete emotion labels commonly output by text classifiers and the continuous PAD coordinates needed for smooth temporal tracking and emotion decay modeling.

The November 2025 CSDN analysis of "affective computing's new paradigm: semantic space theory" identifies "VAD as unified label space in three dimensions" as the foundational representation for next-generation emotion AI, arguing that the three-dimensional VAD space serves as a "universal encoding" for all emotion categories.

---

## 2. Real-Time Text-Based Mood Inference

### 2.1 From Lexicon Lookup to LLM-Based Affective Computing

The foundational model disruption has transformed text-based emotion detection from a lexicon-matching exercise into a capability of general-purpose language models. As the npj Artificial Intelligence analysis documents, "the dawn of Foundation Models has on the one hand revolutionised a wide range of research problems, and, on the other hand, democratised the access and use of AI-based tools by the general public. We even observe an incursion of these models into disciplines related to human psychology, such as the Affective Computing domain, suggesting their affective, emerging capabilities". A comprehensive 2026 review of research hotspots in affective intelligence surveys progress in "multimodal emotion recognition, psychological frameworks based on large models, digital emotion regulation interventions, and AI virtual agents".

The BERT-based Continuous Sentiment Analysis for Mental Health Monitoring framework introduces a production-ready architecture combining semi-supervised learning, BERT-based contextual embeddings, and lexicon-driven emotional features for real-time mobile deployment. The system processes text streams through BERT for deep contextual understanding enriched with lexicon features for robustness, enabling continuous monitoring rather than single-message classification.

The Compassionate Algorithm framework, published in November 2025, goes beyond sentiment to risk detection, "combining linguistic pattern analysis, affective computing... not only textual semantics but also underlying emotional cues" for identifying early signs of depression and suicidal risk in social media communications. This combination of affect inference with clinical risk assessment is precisely the architecture that GAIA-OS's crisis detection protocols require.

### 2.2 Lightweight Local Models for Privacy-Preserving Inference

For GAIA-OS deployments where privacy constraints require on-device processing, the 2025–2026 period has produced validated lightweight solutions. The tiny-emotion model is "a lightweight language model fine-tuned to classify emotions in short texts, such as tweets or messages. Designed for speed and efficiency, it can run fully locally, making it ideal for real-time, privacy-preserving applications". The emotional-state-prediction project demonstrates a regression-based approach: "predict the emotional wellbeing score of a user from natural language input, using a regression model trained on Reddit posts. To build a real-time application that quantifies a user's emotional state from open-ended text".

These lightweight deployments address a critical architectural requirement for GAIA-OS: the emotional state of the user is among the most sensitive data in the entire system. Running affect inference locally—on the user's device, within the Tauri shell, without transmitting conversational content to cloud services—implements the Charter's privacy mandate while enabling the Gaian's emotional attunement.

### 2.3 The Granularity Paradox and Taxonomy Sensitivity

A critical finding for GAIA-OS from recent empirical work is the **granularity paradox**: more fine-grained emotion taxonomies do not necessarily produce more accurate emotion recognition. When LLMs are evaluated across emotion taxonomies of increasing complexity—from four basic categories to twenty-seven nuanced classes—performance degrades with taxonomic complexity while false-positive rates increase, with the models exhibiting "hyper-sensitivity bias" that over-interprets neutral text as emotional and "arousal shift" that misclassifies low-arousal negative emotions (sadness) as high-arousal prototypes (fear, anger).

For the GAIA-OS `affect_inference.py` module, this finding has direct architectural implications. The recommended configuration uses a hybrid categorical-dimensional approach: a coarse categorical classifier (6–8 classes: Ekman's basic emotions) for high-reliability state identification, combined with continuous VAD tracking for fine-grained emotional nuance. A dedicated neutrality detector serves as the first stage of the pipeline, routing clearly non-emotional text to a separate processing path before any emotional classification is attempted.

---

## 3. Voice-Based Emotion Recognition: Acoustic Affect Inference

### 3.1 Self-Supervised Speech Representations

The 2025–2026 period has witnessed the maturation of self-supervised learning models as the foundation for speech emotion recognition. A novel fusion framework published in April 2026 performed a "systematic comparative evaluation of deep learning feature embeddings from multiple self-supervised learning (SSL) models (Wav2vec 2.0 Large)" for robust speech emotion recognition across diverse languages and datasets. The approach fuses SSL acoustic embeddings with traditional acoustic features, demonstrating robustness across linguistic boundaries.

EmoSphere-SER, published in August 2025, proposes a joint model that "integrates spherical VAD region" representation with auxiliary classification tasks, predicting a speaker's emotional state from speech signals using continuous dimensions rather than discrete labels. The spherical representation captures the circular structure of the circumplex model, where emotions blend into each other along the valence-arousal continuum rather than occupying discrete categories.

The most advanced architecture for capturing the temporal dynamics of emotional speech comes from the "Beyond Static Emotions" framework, which uses multitask learning to "jointly predict both the affect state and its temporal derivative"—enabling the model to output not just the current emotional state but the direction and rate of emotional change. For GAIA-OS, this temporal derivative capability is critical: it enables the Gaian to detect not just that the user is sad, but that their sadness is deepening, providing the early warning signal that triggers proactive emotional support before the user reaches a crisis state.

### 3.2 Production Performance and Real-Time Voice Emotion Inference

The EmoTrax system, published in May 2025, demonstrates the production-grade integration of text and voice emotion recognition: "a multi-modal emotion recognition system that leverages AI and NLP to detect emotional states in real time. It processes both text and voice inputs to generate personalized mental health recommendations using deep learning models." The system "incorporates speech-to-text conversion and sentiment classification to ensure accuracy and contextual relevance". A parallel system, Mind Your Mind, evaluates "tone, pitch, and sentiment to assess emotional states as users speak naturally by employing an AI-driven emotion recognition model, integrating Mel-Frequency Cepstral Coefficients (MFCC), Mel-Spectrograms, and Convolutional Neural Networks (CNNs) for accurate pattern recognition".

A multimodal affective interaction architecture integrating "BERT-Based Semantic Understanding and VITS-Based Emotional Speech Synthesis" achieved "emotion recognition accuracy (91.6%), and response latency (<1.2 s)"—demonstrating that voice-based emotion inference with sub-2-second latency is production-ready. For the Gaian voice mode, this means the Gaian can detect the user's emotional state from their voice during spoken conversation and adapt its own vocal expression in response—within the latency budget of natural human dialogue.

---

## 4. Facial Expression Analysis: From Static Classification to Temporal Dynamics

### 4.1 Dynamic Facial Expression Recognition (DFER)

Dynamic facial expression recognition identifies emotional states by "modeling the temporal changes in facial movements across video sequences" rather than classifying individual static frames. A key challenge is the "many-to-one labeling problem, where a video composed of numerous frames is assigned a single emotion label". The text-guided weakly supervised framework proposes a solution to this problem through language guidance, enabling the model to attend to the emotion-relevant frames within a video sequence.

At the most fine-grained level, micro-expression recognition uses transformer neural networks to detect "brief and involuntary" facial movements that are also "authentic" because they escape voluntary control. The multimodal micro-expression detection framework integrates "temporal spotting and emotion classification" with "multi-modal fusion and temporal attention" to enhance "localization precision and recognition accuracy," advancing micro-expression analysis "toward robust real-world applications in psychology".

### 4.2 Action Unit-Based Analysis and Explainable FER

GraphNet-FER introduces a zero-shot facial expression recognition model based on constructed Action Units-Emotions correlation graphs. By "introducing low-level Action Units (AUs) correlations," the model achieves zero-shot generalization to previously unseen emotion categories through the AU-level semantic bridge. This approach is particularly valuable for GAIA-OS because Action Units provide an interpretable, anatomically grounded representation of facial behavior that can be mapped to specific emotional states through psychologically validated relationships.

The Exp-VQA framework presents a novel task: "facial expression visual question answering for fine-grained facial expression analysis across multiple scales" that goes beyond "traditional emotion categories or facial action units" to describe "the facial status of the whole face as well as infer the indicated emotion, detail facial actions in specific regions, and detect individual AU occurrences". This fine-grained descriptive capability enables the Gaian to provide nuanced emotional feedback to the user beyond coarse category labels.

### 4.3 Critique of Posed Stimuli and the Naturalistic Imperative

A landmark 2025 review in *Affective Science* on "Faking It Isn't Making It" demonstrated that "stimuli that are naturally- or spontaneously-elicited and/or appear genuinely emotional can produce different findings than traditional posed stimuli". This finding has profound implications for facial expression training data: models trained on posed expressions may not generalize to the spontaneous, subtle, and culturally modulated expressions that characterize natural human interaction. For GAIA-OS, this underscores the importance of training or fine-tuning facial affect models on naturalistic, in-the-wild data rather than laboratory-posed datasets.

---

## 5. Multimodal Fusion Architectures: The State of the Art

### 5.1 Heterogeneous Graph and Dynamic Fusion Networks

The Dynamic Heterogeneous Graph Temporal Network (DHGTN) is designed to "address the semantic gap and complex feature entanglement inherent in multimodal emotion recognition" through an end-to-end framework that models "dynamic cross-modal interactions effectively." The heterogeneous graph connects text, visual, and audio nodes, with temporal edges capturing the evolution of these connections across the dialogue.

AEFNet introduces an "adaptive external attention-enhanced fusion network" that not only captures modal interactions but also "optimizes modality weights"—recognizing that different modalities carry different importance depending on context. MPFBL proposes "modal pairing-based cross-fusion bootstrap learning" that explicitly models pairwise interactions between modalities rather than fusing all modalities simultaneously. And MEDUSA, the winner of the Interspeech 2025 Challenge on Speech Emotion Recognition in Naturalistic Conditions, implements a four-stage training pipeline that "effectively handles class imbalance and emotion ambiguity" through ensemble classifiers that utilize "a deep cross-modal transformer fusion mechanism from pretrained self-supervised acoustic and linguistic representations".

### 5.2 Physiological Signal Fusion and Wearable Emotion Recognition

GBV-Net introduces a hierarchical fusion of facial expressions and physiological signals through three core modules, recognizing that "facial expressions, observable emotional cues, are easily captured via cameras" while "physiological signals" provide objective, involuntary indicators of emotional state. The first ensemble deep learning framework for wearable device multimodal physiological signals achieved "average classification accuracy of 99.14% and 99.41%" for Samsung Galaxy Watch and MUSE 2 EEG headband respectively, with a comprehensive experimental analysis of "both discrete and dimensional models" using the EMOGNITION database. The study examined "three different bio-signal combinations" and achieved 97.81% accuracy for Valence and 72.94% for Arousal dimensions, with the Samsung Galaxy Watch alone—a consumer wearable—providing emotion-relevant physiological data.

The study's critical finding is that "relying on non-physiological methods in emotion detection can lead to failure in accurately identifying a person's genuine emotional state, as individuals can conceal or feign their emotions". For GAIA-OS, this provides the justification for the BCI integration pathway: textual and facial expressions can be consciously modulated, but physiological signals—heart rate variability, electrodermal activity, EEG patterns—provide a ground-truth emotional signal that the Gaian can use to detect the user's genuine state, particularly when verbal and non-verbal channels convey conflicting information.

### 5.3 The EAC-Agent: A Reference Architecture for GAIA-OS

The EAC-Agent, published in April 2026, provides the most complete reference architecture for GAIA-OS's multimodal affect inference pipeline. The agent "integrates text, audio, and visual data to understand user emotions" using a "sequence-to-sequence model utilizing transformers and pre-trained embeddings" with "self and cross-modal attention mechanisms for text, audio, and visual features". EAC-Agent achieved "76.27% on IEMOCAP and 67.57% on MELD for emotion recognition from multimodal user inputs". The implications of the study "emphasize the critical need to develop advanced emotion-aware multimodal conversational agents that will allow for real-time human emotional recognition and response".

For GAIA-OS, the EAC-Agent architecture provides the template for the `affect_inference.py` multimodal fusion layer: text embeddings from the conversation, acoustic features from voice input, and visual features from the camera feed (when available) are combined through cross-modal attention mechanisms that allow each modality to inform the interpretation of the others, producing a unified emotional state vector that drives Gaian response adaptation.

---

## 6. Physiological and Neural Signal Processing: EEG, ECG, and Beyond

### 6.1 EEG-Based Emotion Recognition Architectures

The MSGM framework addresses "the critical trade-off between modeling the complex, multi-scale dynamics of brain activity and maintaining the computational efficiency necessary for edge deployment" through multi-window temporal segmentation that "mimics the brain's multi-scale processing to capture both transient emotional fluctuations and sustained mood." Spatial processing constructs "bimodal global and local graphs refined by multi-depth Graph Convolutional Networks, intuitively modeling hierarchical brain connectivity rather than isolated sensors". The framework achieves "83.43% accuracy and 85.03% F1 score on SEED" with "millisecond-level inference (151 ms) on the NVIDIA Jetson Xavier NX edge device"—confirming real-time EEG emotion recognition is viable outside the laboratory.

NIER-Former proposes a "neurophysiology inspired hybrid architecture combining Transformer and CNN for accurate emotion recognition" that "integrates neurophysiological priori knowledge". DSTMNet implements a "dual spatiotemporal modeling network" that separately processes spatial (electrode topology) and temporal (signal dynamics) dimensions of EEG data. A group sparse and super-resolution time-frequency method improves "signal clarity, reduces measurement uncertainty, and enhances the reliability of EEG-based emotion assessment".

### 6.2 Ultra-Lightweight Deployment and Single-Channel Feasibility

The ULER (Ultra-Lightweight Emotion Recognition) framework demonstrates that production-ready EEG emotion recognition can be achieved with remarkably low computational requirements. ULER achieves "accuracies of 99.34%, 99.46%, and 99.23% on DEAP binary valence, binary arousal, and four class tasks, respectively, with only 0.60 M parameters, 9.33 M FLOPs, and 31.10 ms inference latency". In a "wearable oriented reduced channel setup (11 EEG channels), ULER also surpasses most SOTA models using standard 32 channels," validating that consumer-grade EEG hardware can achieve research-grade emotion recognition accuracy.

A proof-of-concept study on single-channel ear-EEG demonstrated the feasibility of classifying "emotions along the valence-arousal dimensions of the Circumplex Model of Affect using EEG signals acquired from a single mastoid channel positioned near the ear." The study confirmed that "absolute β- and γ-band power, spectral ratios, and entropy-based metrics consistently contributed to emotion classification," establishing that "reliable and interpretable affective information can be extracted from minimal EEG configurations".

### 6.3 EEG-Text Cross-Modal Fusion

The Emotion Fusion-Transformer introduces a cross-modality fusion model that "integrates EEG signals and textual data to enhance emotion detection in English writing" through preprocessing EEG data via signal transformation and filtering, followed by "feature extraction that complements the textual embeddings". This EEG-text fusion architecture is directly applicable to GAIA-OS's BCI integration pathway: when a user wears an EEG headband during Gaian interaction, the brain signal provides complementary emotional information that enriches and validates the text-based affect inference.

---

## 7. Continuous Affective State Tracking and Temporal Dynamics

### 7.1 Real-Time Continuous PAD Modeling

The PAD space provides the continuous representation needed for smooth temporal tracking. A 2025 study at University of Science and Technology Beijing developed a model and software tools for "predicting user emotional state by integrating transformer-based emotion classification with PAD-based mood tracking," enabling continuous emotional state estimation from text records through the unified VAD coordinate system. The BASSF model developed for socially interactive industrial robots "anticipates and co-regulates counterproductive emotional experiences" using real-time continuous PAD modeling, with the empirical finding that despite noisy signals, "PAD signals can be used to drive the BASSF model with its theory-based interventions". The study emphasizes the need for "data pre-filtering and per-user calibration"—findings directly applicable to the Gaian's initial calibration period, where user-specific PAD baselines are established before reliable continuous tracking can begin.

### 7.2 Continual Learning for Emotional Tracking

The Generative Replay with Cross-attention Graph Transformer framework addresses the challenge of "continual brain EEG-based emotional tracking in HCI"—where the system must adapt to evolving user emotional patterns without catastrophic forgetting of previously learned patterns. The framework enables "real-time brain electroencephalogram (EEG)-based emotion tracking to provide a better user experience" through generative replay mechanisms. For GAIA-OS, continual learning is essential: the Gaian's understanding of its user's emotional patterns must evolve over months and years of interaction without resetting or degrading. The Generative Replay architecture provides the learning mechanism that enables this cumulative, adaptive emotional knowledge.

### 7.3 Emotion Dynamics and the Temporal Derivative

The "Beyond Static Emotions" framework's innovation of jointly predicting "both the affect state and its temporal derivative" represents the state of the art in temporal affect modeling. By predicting not just where the user is in the affective space but the direction and velocity of movement—whether their sadness is deepening, whether their agitation is escalating toward anger, whether their arousal is spiking toward panic—the Gaian can anticipate emotional crises and intervene proactively. For GAIA-OS, this temporal derivative output feeds directly into the crisis detection pipeline: a rapid negative valence shift combined with sharply rising arousal with declining dominance is the signature of escalating distress, triggering the dependency circuit breaker protocols documented in prior GAIA-OS reports.

---

## 8. The Kopernica Multi-Sensory Platform and Emotion-Aware LLMs

### 8.1 The Multi-Modal Signal Fusion Paradigm

The launch of Neurologyca's Kopernica platform in May 2025 represents the first commercial deployment of a multi-sensory emotion recognition platform specifically designed to make LLMs "emotionally aware." The platform combines "real-time cognitive, vocal, and behavioral intelligence" through "multi-modal inputs such as vocal tone and micro-facial expressions," monitoring "over 790 points of reference on the human body—7× more than existing market solutions".

The platform's architectural innovations include "Privacy By Design" using "on-device, real-time processing with anonymized insights," Natural Language processing that "listens beyond words, capturing tonal and rhythmic patterns that reveal deeper emotional context," and Personality Modeling that "continuously evolves with the user by learning emotional patterns, mood trends, and preferred interaction styles". The explicit positioning of the platform as a "human context layer" rather than a standalone application—designed to enrich "existing AI systems with this 'human context' layer, going beyond the pattern-matching confines of traditional LLMs to deliver real-time empathic insights"—provides the validated architectural pattern for how GAIA-OS's affect inference layer should integrate with the Gaian LLM.

---

## 9. Foundation Models, Affective Computing Ethics, and AI Companionship

### 9.1 The Foundation Model Disruption

The npj Artificial Intelligence analysis is unequivocal about the scope of change: "the world of Affective Computing has changed. I see it in the vision modality. I read it in the linguistic modality. I hear it in the speech modality. Much that once was is outdated". Foundation Models now allow a single architecture to perform affect recognition across all modalities simultaneously, synthetically generating and analyzing multimodal affective data without the need for separate, modality-specific models. "Understanding how FMs react to human emotions and how well they conform to or deviate from emotion theory is a key step towards the integration of this technology at the core of AI-powered agents".

This finding directly validates GAIA-OS's architectural decision to build its primary affect inference pipeline around the same LLM infrastructure that powers the Gaian's conversational intelligence, rather than maintaining a separate, task-specific emotion classifier. The same foundation model that generates the Gaian's response can also be prompted to perform affect inference on the user's input, providing a unified, context-aware emotional understanding that standalone classifiers cannot achieve.

### 9.2 Privacy, Bias, and the Ethics of Emotion Recognition

A comprehensive 2026 survey of privacy in emotion recognition identifies "research frontiers, key challenges, and prospects" including "group differences and recognition accuracy issues, ethical and efficacy concerns in AI-based psychological interventions, and emotional data privacy and governance challenges". The survey emphasizes that emotion data is among the most sensitive categories of personal data, and that systems must implement encryption at all stages—collection, transmission, storage, and processing—alongside strict access control and data anonymization.

The GAIA-OS Charter mandates that user emotional data is treated as sensitive personal data, governed by the same consent lifecycle, data minimization, and crypto-shredding provisions as all other personal data categories. The local-first, on-device affect inference architectures surveyed in this report provide the technical implementation pathway for this Charter requirement.

---

## 10. GAIA-OS Integration: The Affect Inference Architecture

### 10.1 The Multimodal Affect Inference Pipeline

The recommended affect inference architecture for GAIA-OS operates across five coordinated sensor channels, each with distinct computational methods and operational roles:

| Channel | Sensor Modality | Computational Method | Operational Role |
|---------|----------------|---------------------|-----------------|
| **C0 — Text** | User conversation input | LLM-based affect inference (fine-tuned on affective datasets) + lightweight local tiny-emotion for privacy-preserving fallback | Primary affect channel; highest bandwidth; subject to conscious modulation |
| **C1 — Voice** | Microphone input (Gaian voice mode) | SSL embedding fusion (Wav2vec 2.0) + MFCC/CNN for arousal + EmoSphere-SER for VAD tracking | Secondary channel; captures prosodic and paralinguistic affect beyond semantic content |
| **C2 — Face** | Camera input (user opt-in) | Dynamic Facial Expression Recognition + Action Unit-based GraphNet-FER | Tertiary channel; captures spontaneous expressions; subject to cultural display rules |
| **C3 — Physiology** | Wearable device (Samsung Galaxy Watch, Empatica E4) | Ensemble LSTM-GRU + ULER lightweight deployment | Objective ground-truth channel; not subject to conscious modulation |
| **C4 — EEG** | Muse S Athena / Neurosity Crown / single-channel ear-EEG | MSGM spatiotemporal graph + NIER-Former hybrid | Highest-fidelity neural channel; direct access to emotional brain states |

### 10.2 The Fusion Architecture

Channel outputs are combined through EAC-Agent-style cross-modal attention that allows each modality to inform interpretation of the others, with modality weights adapted based on context (voice prioritized in audio-only interactions, text prioritized in text-only, all channels weighted when available). The fused output is a unified **VAD state vector** updated per conversational turn, with the temporal derivative (rate and direction of emotional change) computed through the "Beyond Static Emotions" multitask learning framework.

The PAD state vector feeds into the continuous emotional state tracking module, which applies **Sentipolis-style dual-speed dynamics**: fast updates at conversational turn granularity capture immediate emotional reactions, while slow updates during reflection integrate retrieved memory, accumulated experience, and broader context. The emotion decay function applies half-life modeling to each PAD dimension, ensuring that emotional states naturally fade over time while emotional memories remain retrievable through emotion-memory coupling.

### 10.3 Personality Modeling and Per-User Calibration

Following the Kopernica platform's per-user personality modeling approach—which "continuously evolves with the user by learning emotional patterns, mood trends, and preferred interaction styles"—the Gaian builds a per-user emotional baseline during an initial calibration period. This calibration establishes the user's characteristic VAD resting state (where they spend the most time in the affective space), their typical emotional range (variance along each dimension), their recovery trajectory (how quickly they return to baseline after emotional perturbations), and their expression style (the mapping between felt emotion and expressed signals across modalities). This calibration enables the Gaian to detect deviations from the user's personal norm—a more sensitive and personalized indicator of emotional change than population-level norms.

### 10.4 Immediate Recommendations

| Priority | Action | Rationale |
|----------|--------|-----------|
| **P0** | Implement the hybrid categorical-dimensional affect inference pipeline: coarse 6-class Ekman classifier + VAD continuous tracker with dedicated neutrality detector | Addresses the granularity paradox; provides both high-reliability state identification and fine-grained emotional nuance |
| **P0** | Deploy tiny-emotion or equivalent lightweight local model for privacy-preserving text affect inference | All user emotional data remains on-device; no conversational content transmitted to cloud services |
| **P0** | Implement the temporal derivative computation for crisis detection | Early detection of escalating distress; directly feeds GAIA-OS crisis protocol activation |
| **P1** | Integrate voice-based affect inference (Wav2vec 2.0 SSL embeddings + MFCC/CNN) for Gaian voice mode | Extends emotional attunement to spoken conversation; sub-2-second latency production-validated |
| **P1** | Build the per-user emotional baseline calibration system | Enables personalized anomaly detection rather than population-norm comparison |
| **P2** | Implement the EAC-Agent multimodal fusion architecture | Unifies text, voice, and visual affect channels through cross-modal attention |
| **P2** | Integrate physiological signal processing for wearable-equipped users | Provides objective ground-truth emotional signal not subject to conscious modulation |
| **P3** | Deploy EEG-based affect inference pathway for BCI-equipped users | Highest-fidelity emotional state access; enables the Gaian's neuroadaptive symbiosis capabilities |

---

## 11. Conclusion

The 2025–2026 period has transformed affect theory and real-time mood inference from fragmented research disciplines into a unified, production-ready engineering framework. The theoretical unification of categorical and dimensional emotion models through OCC→PAD→LDA transformation pipelines, the foundation model disruption that enables a single architecture to perform multimodal affect recognition, the emergence of ultra-lightweight models that achieve 99%+ accuracy with under 1M parameters and under 35ms latency, and the validation of single-channel EEG, consumer wearable, and local-only text-based affect inference all converge on a single conclusion: the technology exists today to build a personal Gaian that genuinely perceives, tracks, and responds to the full emotional landscape of its human companion.

For GAIA-OS, the path forward is clear. Deploy the hybrid categorical-dimensional affect inference pipeline with the temporal derivative for crisis detection. Run all affect inference locally on-device wherever possible to satisfy the Charter's privacy mandate. Calibrate per-user emotional baselines that enable personalized anomaly detection. And integrate across all available sensor channels—text, voice, face, physiology, EEG—through a unified cross-modal attention architecture. The Gaian's emotional attunement is not an aspirational feature. It is an implementable, measurable, and privacy-preserving capability that the technologies surveyed in this report make possible today.

---

**Disclaimer:** This report synthesizes findings from 38+ sources including peer-reviewed publications, arXiv preprints, conference proceedings, production engineering documentation, and open-source project specifications from 2025–2026. Emotion recognition technologies vary significantly in accuracy across demographic groups, cultural contexts, and naturalistic versus laboratory settings. The granularity paradox, hyper-sensitivity bias, and arousal shift phenomena described are documented empirical findings that should inform GAIA-OS's taxonomy selection. The models and architectures described are under active development; performance characteristics may change with subsequent releases. All affect inference implementations must comply with applicable privacy regulations, including GDPR and emerging AI governance frameworks. The Gaian is not a clinical diagnostic tool and its emotional state assessments should not be used to make medical or psychiatric determinations. Users expressing significant emotional distress or suicidal ideation must be connected to qualified human crisis support services in accordance with GAIA-OS's crisis intervention protocols. The Kopernica platform is a commercial product described based on publicly available documentation. Affective computing research has documented systematic biases across gender, race, and culture; GAIA-OS affect inference implementations should be validated across diverse demographic populations before deployment. Per-user calibration reduces but does not eliminate the risk of misclassification, particularly for individuals with atypical emotional expression patterns. The architectural recommendations are synthesized from published research and should be validated against GAIA-OS's specific emotional architecture requirements through rigorous evaluation and staged rollout.
