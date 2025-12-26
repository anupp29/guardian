---

# 🛠️ Implementation Details

Guardian AI is implemented as a **modular system** where learning, simulation, and reasoning are clearly separated. This separation ensures that each component can be independently validated and demonstrated during a live hackathon demo.

---

## 1. Data Ingestion & Graph Construction

### Input Format

Guardian AI ingests structured supply-chain data derived from the **MERCOR dataset**, represented as:

* Vendor identifiers
* Supplier tier information
* Dependency relationships (vendor → vendor, vendor → software)
* Optional metadata (industry, dependency category)

### Graph Representation

* Implemented using **NetworkX** (Python) for transparency and debuggability.
* Directed graph:

  * **Nodes**: Vendors / software components
  * **Edges**: Dependency relationships

Each node is annotated with:

* Tier depth
* Dependency count
* Historical incident flag (if available)
* Optional enrichment from OpenSSF / CVE snapshots

This graph becomes the **single source of truth** for both learning and simulation.

---

## 2. Graph Learning Integration

The learning component is **decoupled** from simulation logic.

* A trained GNN produces:

  * Node-level risk embeddings
  * Edge-level sensitivity scores
* These scores are **cached** and reused during simulation.

This design ensures:

* No model retraining during demo
* Stable and reproducible outputs
* Fast inference suitable for live interaction

---

## 3. Simulation Engine

The simulation engine is **deterministic**, ensuring repeatability.

### Core Logic

1. User selects a vendor or component to fail / be compromised.
2. Engine performs bounded graph traversal (BFS with depth limits).
3. Traversal is **guided by learned risk weights**:

   * Higher-risk paths are explored first.
4. All reachable impact paths are recorded.

### Outputs

* List of affected nodes
* Multiple propagation paths
* Path reach and depth metrics

No probabilistic or temporal assumptions are introduced.

---

## 4. Agent Execution (ADK)

Agents are implemented as **thin reasoning layers**, not heavy controllers.

* Agents do not mutate the graph.
* Agents operate only on outputs provided by previous steps.
* Each agent produces structured JSON outputs for traceability.

Agent orchestration is handled by a lightweight controller that:

* Ensures correct execution order
* Captures reasoning traces
* Aggregates results for presentation

---

## 5. Explainable Output Layer

Final outputs are composed into:

* Graph visualizations (highlighted paths)
* Natural-language explanations
* Ranked mitigation lists

Gemini is used **only** where human-level reasoning is required (impact explanation, trade-off articulation).

---

## 6. Google Cloud Integration

Guardian AI is deployed using a **minimal and justifiable GCP footprint**:

* **Cloud Run**: Backend API and simulation service
* **Vertex AI**:

  * GNN inference
  * Gemini access
  * Vector Search for mitigation enrichment
* **Cloud Storage / Firestore**:

  * Graph snapshots
  * Cached embeddings

No unnecessary services are included.


---