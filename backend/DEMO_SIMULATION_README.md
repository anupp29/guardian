# NetworkX Demo Simulation Endpoint

## Overview

The `/api/simulation/demo` endpoint showcases a comprehensive NetworkX-based simulation with extensive graph analysis capabilities.

## Features

### NetworkX Graph Analysis
- **Graph Metrics**: Total nodes, edges, density, connectivity
- **Centrality Measures**: Betweenness, closeness, PageRank, degree centrality
- **Path Analysis**: Shortest paths, path statistics, cycles detection
- **Component Analysis**: Strongly/weakly connected components
- **Reachability Analysis**: Descendants and ancestors for each node

### Simulation Results
- Multi-node compromise simulation starting from most critical nodes
- Detailed propagation analysis with step-by-step breakdown
- Comprehensive metrics and statistics

## Usage

### Via API Server

1. Start the backend server:
```bash
cd guardian/backend
python -m uvicorn api.main:app --reload
```

2. Call the endpoint:
```bash
curl http://localhost:8000/api/simulation/demo
```

Or visit in browser:
```
http://localhost:8000/api/simulation/demo
```

### Via Test Script

```bash
cd guardian/backend
python run_demo.py
```

## Response Structure

The endpoint returns a comprehensive JSON response including:

- `networkx_metrics`: Graph structure and centrality metrics
- `simulation_results`: Compromise propagation results
- `path_analysis`: NetworkX path finding results
- `propagation_analysis`: Step-by-step propagation details
- `reachability_analysis`: Node reachability information
- `graph_summary`: Tier and risk distribution
- `mitigation_suggestions`: Recommended actions

## NetworkX Features Demonstrated

1. **Graph Traversal**: BFS/DFS for finding paths
2. **Centrality Calculations**: Multiple centrality metrics
3. **Path Finding**: Shortest paths and all paths
4. **Cycle Detection**: Finding cycles in the graph
5. **Component Analysis**: Connected components
6. **Subgraph Analysis**: Analyzing compromised subgraphs
7. **Reachability**: Finding descendants and ancestors

## Example Output

```json
{
  "success": true,
  "data": {
    "simulation_id": "demo_crazy_abc123",
    "status": "completed",
    "message": "🚀 CRAZY NetworkX Simulation Complete!",
    "networkx_metrics": {
      "total_nodes": 50,
      "total_edges": 120,
      "graph_density": 0.048,
      "most_central_node": {...}
    },
    "simulation_results": {
      "total_affected": 35,
      "blast_radius": 32,
      "cascade_depth": 5
    },
    ...
  }
}
```

## Technical Details

- Uses NetworkX DiGraph for directed graph representation
- Implements deterministic BFS traversal for propagation
- Calculates multiple NetworkX metrics in parallel
- Handles large graphs efficiently with sampling
- Provides comprehensive error handling


