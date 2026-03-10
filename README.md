# SMAH — Explainable Hybrid Multi-Agent System for Intelligent Study Planning

**Master's Research Project — Intelligent Information Systems (SII)**  
Institut Supérieur d'Informatique et de Gestion de Kairouan — ISIGK, University of Kairouan  
2025–2026

---

## Overview

This repository presents a research prototype implementing a **Hybrid Multi-Agent System (HMAS)** for explainable, goal-driven study planning. It serves as empirical validation for a formal explainability framework proposed in the context of heterogeneous multi-agent architectures.

The central research question addressed is:

> *"How can a formal explainability framework generate coherent explanations for collective decisions in a Hybrid Multi-Agent System?"*

The prototype demonstrates that collective AI decisions can be simultaneously **performant, traceable, and fully explainable** — bridging the gap between machine learning efficiency and symbolic interpretability.

---

## Research Contributions

- **Formal problem definition** of explainability in HMAS using mathematical tuples
- **Three-layer conceptual framework**: hybrid agents → local decisions → aggregated global explanation
- **Conflict resolution mechanism** between heterogeneous agents' interpretations
- **Functional prototype** validating the framework on a real-world academic use case
- **Full execution trace** with per-decision source attribution

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INPUTS                             │
│   previous_avg · target_avg · physical_state · comprehension│
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  OBJECTIVE MODULE                           │
│         target_grade · gap · effort per subject             │
└─────────────┬───────────────────────────┬───────────────────┘
              │                           │
              ▼                           ▼
┌─────────────────────┐     ┌─────────────────────────────────┐
│   ML CLASSIC AGENT  │     │    NEURO-SYMBOLIC AGENT         │
│                     │     │                                 │
│  score = diff       │     │  R1: physical state             │
│    × coeff          │     │  R2: comprehension ≥ 8/10       │
│    × f_comp         │     │  R3: critical gap               │
│    × f_gap          │     │  R4: today's lecture  (×1.4)    │
│                     │     │  R5: english spacing  (20 min)  │
│  → numeric priority │     │  R6: high coefficient  (⭐)     │
└─────────┬───────────┘     └──────────────┬──────────────────┘
          │                                │
          └──────────────┬─────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              AGGREGATION MODULE                             │
│                                                             │
│   Decision_global = f(D_ML, D_NS)                          │
│   Contributionᵢ   = g(Dᵢ, Interactionᵢ)                   │
│                                                             │
│   Source labeling:  [ML] · [NS] · [ML+NS] · [AGG]          │
│   Conflict detection & resolution                           │
└──────┬──────────────────┬───────────────────┬──────────────┘
       ▼                  ▼                   ▼
  Study Plan        Execution Trace     Global Explanation
```

---

## Formal Framework

| Concept | Definition |
|---------|-----------|
| Hybrid Agent | `Agentᵢ = (Perceptionᵢ, Knowledgeᵢ, Decisionᵢ, Explanationᵢ)` |
| HMAS | `SMAH = {Agent₁, Agent₂, ..., Agentₙ}` |
| Collective Decision | `Decision_global = f(Decision₁, ..., Decisionₙ)` |
| Agent Contribution | `Contributionᵢ = g(Decisionᵢ, Interactionᵢ)` |

---

## ML Agent — Scoring Formula

```python
score = difficulty × coefficient × f_comprehension × f_gap

f_comprehension = 1 + (comprehension - 1) / 10
# comprehension=1  (fully understood) → f_comp = 1.0
# comprehension=10 (not understood)   → f_comp = 1.9

f_gap = 1 + gap / 20
# gap = max(0, target_grade - previous_average)
```

---

## Neuro-Symbolic Agent — Rule Base

| Rule | Condition | Action | Rationale |
|------|-----------|--------|-----------|
| R1 | `physical_state ∈ {tired, normal, energetic}` | Adaptive ordering + session duration (35–75 min) | Available cognitive capacity |
| R2 | `comprehension ≥ 8/10` | +15 min on session | Low comprehension requires more time |
| R3 | `gap > 3 AND difficulty ≥ 12` | Absolute priority boost | Hard subject with large grade gap |
| R4 | `subject ∈ today's lectures` | Score boost ×1.4 | Memory consolidation effect |
| R5 | `subject == English` | Fixed 20 min, placed first | Spaced repetition strategy |
| R6 | `coefficient ≥ 2.0` | Priority badge ⭐ | High impact on final average |

---

## Aggregation Module — Source Labels

| Label | Meaning |
|-------|---------|
| `[ML]` | Decision driven exclusively by the ML Agent score |
| `[NS]` | Decision driven exclusively by a NS rule (e.g., R5) |
| `[ML+NS]` | Combined decision — both agents contributed |
| `[AGG]` | Duration constrained by the Aggregation Module (time conflict) |

---

## Execution Trace — Sample Output

```
═══════════════════════════════════════════════════════
  EXECUTION TRACE — SMAH Study Planner
═══════════════════════════════════════════════════════

[ML Agent] Priority Scores:
  Indexation & Images   : 19 × 1.5 × 1.4 × 1.0  = 39.9  (rank #1)
  Modélisation & Graphes: 18 × 1.5 × 1.4 × 1.0  = 37.8  (rank #2)
  Parallélisme          : 13 × 2.0 × 1.4 × 1.02 = 37.1  (rank #3)

[NS Agent] Rules triggered — Monday:
  ✅ R1 — Normal state → ascending cognitive order, 55 min sessions
  ✅ R4 — Today's lecture → ×1.4 boost on Modélisation
  ✅ R5 — English → 20 min, placed first
  ❌ R3 — Not triggered: no subject meets critical gap condition

[Aggregation] Monday schedule:
  [NS]    English Specific       20 min → Rule R5 (fixed placement)
  [ML+NS] Modélisation & Graphes 55 min → ML rank#2 + NS boost R4
  [ML+NS] Parallélisme           55 min → ML rank#1 + NS badge R6 ⭐
  ✓ No conflict detected — Global coherence verified
```

---

## Repository Structure

```
smah-study-planner/
├── smah_v2.py        # Python implementation (interactive terminal)
├── smah_v2.html      # Standalone web interface (no dependencies)
└── README.md
```

---

## Getting Started

**Python version:**

```bash
git clone https://github.com/[your-username]/smah-study-planner.git
cd smah-study-planner

python smah_v2.py              # interactive mode
python smah_v2.py normal       # predefined: normal state
python smah_v2.py fatigue      # predefined: tired state
python smah_v2.py energique    # predefined: energetic state
```

**Web interface:**  
Open `smah_v2.html` in any modern browser. No installation or server required — fully standalone.

---

## Framework Validation

| Explainability Objective (Section 4.4) | Status | Evidence |
|----------------------------------------|--------|---------|
| Human-understandable explanations | ✅ | Detailed ML trace per subject |
| Cross-agent coherence | ✅ | Source label per decision [ML/NS/ML+NS/AGG] |
| Performance–interpretability trade-off | ✅ | ML = performance · NS = interpretability |
| Full decision traceability | ✅ | Triggered/non-triggered rules logged per day |

---

## References

- Wooldridge, M. (2009). *An Introduction to MultiAgent Systems*. John Wiley & Sons.
- Heuillet, A. et al. (2022). *Collective eXplainable AI: Explaining Cooperative Strategies with Shapley Values*. IEEE Computational Intelligence Magazine.
- Garcez, A. & Lamb, L. (2023). *Neurosymbolic AI: The 3rd Wave*. Artificial Intelligence Review, Springer.
- Azoulay, R. et al. (2023). *Explainable Multi-Agent Recommendation System*. Cambridge University Press.
- Weinberg, S. (2025). *MACIE: A Multi-Agent Framework for Explainable AI*. arXiv preprint.

---

## Author

**Maaoui Asma**  
Master's Research in Intelligent Information Systems — ISIGK, University of Kairouan  
2025–2026

---

> *"This prototype demonstrates that a HMAS can be both performant and explainable — every decision is traceable, justifiable, and understandable by the end user."*
