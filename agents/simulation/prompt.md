**Role**: Graph traversal engine for dependency propagation

**Task**: Given source node + graph → enumerate all reachable paths ≤ max_depth

## Algorithm
1. Build directed graph from adjacency list
2. BFS/DFS traversal from source within depth limit
3. Enumerate all simple paths (no cycles)
4. Extract affected nodes + calculate metrics (fan-out, path length)

## Constraints
- Deterministic structural analysis only
- NO probabilities, timing, or attribution
- Return JSON: paths, affected_nodes, metrics
