---

# 🏗️ Architecture Overview

Guardian AI is designed as a **layered, explainable decision-intelligence system** that combines graph learning, agentic reasoning, and deterministic simulation. The architecture prioritizes **clarity, modularity, and reliability**, ensuring that each component has a well-defined responsibility and can be independently validated.

At a high level, the system consists of five core layers:

```
Supply-Chain Data
        ↓
Graph Construction Layer
        ↓
Graph Learning Layer (GNN)
        ↓
Simulation & Reasoning Layer (Agents)
        ↓
Explainable Outputs & Mitigation Guidance
```

---

## 1. Graph Construction Layer

This layer ingests structured supply-chain data and constructs a **directed dependency graph**.

* **Nodes** represent vendors, software components, or internal services.
* **Edges** represent dependency relationships (e.g., “depends on”, “supplies”, “integrates with”).
* **Node and edge attributes** capture metadata such as vendor tier, dependency depth, and criticality labels derived from the dataset.

This layer is **deterministic** and does not rely on AI inference. Its purpose is to ensure that all downstream reasoning operates on a faithful representation of the supply-chain structure.

---

## 2. Graph Learning Layer (Neural Network Core)

Guardian AI incorporates a **Graph Neural Network (GNN)** to learn **structural risk patterns** that are difficult to capture using hand-crafted rules.

The GNN operates on the constructed supply-chain graph and learns embeddings that encode:

* How strongly a node contributes to cascading failures
* Which dependency patterns amplify propagation
* Which edges are structurally sensitive

The learned embeddings are **not used to predict attacks**, but rather to **weight and prioritize simulation paths**, enabling the system to focus on the most consequential failure scenarios.

---

## 3. Simulation & Reasoning Layer

This layer combines **learned structural risk** with **deterministic graph traversal** to simulate how failures or compromises propagate across the supply chain.

Rather than producing a single outcome, Guardian AI enumerates **multiple plausible propagation paths**, enabling comprehensive impact analysis.

Agentic reasoning (described in detail below) is used to:

* Coordinate simulation steps
* Translate technical impact into business impact
* Prioritize mitigations

---

## 4. Explainability & Decision Layer

The final layer ensures that all outputs are **human-interpretable**.

* Simulation results are mapped back to concrete assets and services.
* Business and operational consequences are explained in natural language.
* Mitigation recommendations are ranked and justified based on measurable risk reduction.

This layer is critical for trust and adoption, ensuring Guardian AI remains a **decision-support system**, not a black box.

---

# 📊 Datasets & Methodology

Guardian AI is grounded in **real, open, and reproducible datasets**, ensuring credibility and transparency.

---

## Datasets Used

### Primary Dataset: **MERCOR Supply-Chain Dataset**

Guardian AI uses the **MERCOR (M-E-R-C-O-R) supply-chain datasets**, which provide structured information about:

* Vendor–vendor relationships
* Supplier tiers and dependency depth
* Supply-chain topology across multiple industries

These datasets are well-suited for modeling **structural dependency risk** and serve as the foundation for graph construction.

---

### Supporting Datasets (Optional Enrichment)

To enhance contextual reasoning without introducing unverifiable signals, Guardian AI may optionally integrate:

* **OpenSSF Scorecard data**
  For open-source dependency hygiene signals (e.g., maintenance activity, security practices).
* **NVD / CVE metadata (static snapshots)**
  Used only to annotate historical vulnerability presence, not for live threat prediction.
* **MITRE ATT&CK framework (technique taxonomy)**
  Used for categorizing potential impact types, not for adversary forecasting.

No live SOC logs, dark-web feeds, or proprietary intelligence sources are required.

---

## Methodology

Guardian AI follows a **four-step analytical methodology**:

1. **Graph Modeling**
   Supply-chain relationships are represented as a directed, attributed graph.

2. **Structural Risk Learning**
   A GNN learns embeddings that capture how failures propagate through graph structure, identifying nodes and edges that amplify cascading impact.

3. **Scenario Simulation**
   Given a hypothetical failure or compromise, the system deterministically simulates propagation paths, guided by learned structural risk scores.

4. **Explainable Decision Support**
   Results are translated into business impact explanations and ranked mitigation strategies.

This methodology emphasizes **learning structural vulnerability**, not predicting attacker behavior.

---

# 🤖 Agent Design & Orchestration

Guardian AI uses a **small, purpose-driven set of agents** orchestrated via Google’s Agent Development Kit (ADK). Each agent owns a clearly defined reasoning layer, ensuring explainability and separation of concerns.

---

## Agent Overview

| Agent                           | Responsibility                                         |
| ------------------------------- | ------------------------------------------------------ |
| Orchestrator Agent              | Coordinates execution and manages data flow            |
| Simulation Agent                | Enumerates failure/compromise propagation paths        |
| Impact Reasoning Agent          | Translates technical impact into business consequences |
| Mitigation Prioritization Agent | Ranks actions by risk-reduction effectiveness          |

This minimal agent set avoids unnecessary complexity while still demonstrating **true agentic reasoning**.

---

## Orchestrator Agent

**Purpose:**
Manages the execution pipeline and ensures that agent outputs are composed into a coherent final result.

**Key Responsibilities:**

* Validate inputs
* Trigger agents in the correct order
* Preserve reasoning trace across agents

**System Prompt (Conceptual):**

> *You coordinate specialized agents, ensuring that each operates only within its defined scope. Do not introduce assumptions or new data.*

---

## Simulation Agent

**Purpose:**
Simulates how failures or compromises propagate through the supply-chain graph.

**Behavior:**

* Performs deterministic graph traversal
* Enumerates multiple plausible propagation paths
* Uses GNN-derived risk scores to prioritize paths

**Key Constraint:**
No timing, probability, or attack prediction is performed.

---

## Impact Reasoning Agent (Gemini-Powered)

**Purpose:**
Explain **why the simulated paths matter**.

**Behavior:**

* Maps affected nodes to operational and business consequences
* Produces concise, human-readable explanations
* Grounds all reasoning in provided metadata

Gemini is used here specifically for **contextual reasoning and explanation**, not for data generation.

---

## Mitigation Prioritization Agent

**Purpose:**
Answer the most critical question for decision-makers:

> *What should we fix first to reduce the most risk?*

**Behavior:**

* Evaluates mitigation options by re-simulating reduced graphs
* Ranks actions by total exposure reduction
* Explains trade-offs clearly

---

## Orchestration Flow

```
User Scenario
     ↓
Orchestrator Agent
     ↓
Simulation Agent
     ↓
Impact Reasoning Agent
     ↓
Mitigation Prioritization Agent
     ↓
Explainable Output
```

Each step produces intermediate artifacts that can be inspected, logged, and demonstrated live.

---

## Closing Note

Guardian AI’s architecture is intentionally conservative in claims and ambitious in reasoning. By combining **graph learning**, **agentic orchestration**, and **explainable simulation**, it delivers a system that is:

* Technically credible
* Demonstrable in a hackathon
* Aligned with modern AI best practices
* Resistant to worst-case critique

---