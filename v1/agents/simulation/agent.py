"""
SimulationAgent - Simulates failure propagation in supply-chain graphs using Google ADK
"""

import logging
from typing import Dict, Any, List, Set, Optional
import networkx as nx

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from .schema import SimulationInput, SimulationOutput, PropagationPath


logger = logging.getLogger(__name__)


def build_graph_tool(graph_metadata: Dict[str, Any]) -> nx.DiGraph:
    """
    Build NetworkX directed graph from metadata.
    Falls back to sample graph if metadata not provided.
    """
    G = nx.DiGraph()
    
    if graph_metadata and 'nodes' in graph_metadata and 'edges' in graph_metadata:
        # Build from provided metadata
        for node in graph_metadata['nodes']:
            node_id = node.get('id', node) if isinstance(node, dict) else node
            attrs = node if isinstance(node, dict) else {}
            G.add_node(node_id, **attrs)
        
        for edge in graph_metadata['edges']:
            if isinstance(edge, dict):
                source = edge.get('source')
                target = edge.get('target')
                attrs = {k: v for k, v in edge.items() if k not in ['source', 'target']}
            else:
                source, target = edge[0], edge[1]
                attrs = {}
            if source and target:
                G.add_edge(source, target, **attrs)
    else:
        # Fallback: Create sample supply-chain graph
        logger.warning("No graph metadata provided, using sample graph")
        sample_nodes = [
            "VENDOR_001", "VENDOR_002", "VENDOR_003", "VENDOR_004",
            "VENDOR_005", "VENDOR_006", "VENDOR_007", "VENDOR_008",
            "VENDOR_009", "VENDOR_010"
        ]
        sample_edges = [
            ("VENDOR_001", "VENDOR_002"),
            ("VENDOR_001", "VENDOR_003"),
            ("VENDOR_002", "VENDOR_004"),
            ("VENDOR_002", "VENDOR_005"),
            ("VENDOR_003", "VENDOR_006"),
            ("VENDOR_003", "VENDOR_007"),
            ("VENDOR_004", "VENDOR_008"),
            ("VENDOR_005", "VENDOR_009"),
            ("VENDOR_006", "VENDOR_010"),
        ]
        
        G.add_nodes_from(sample_nodes)
        G.add_edges_from(sample_edges)
    
    return G


def enumerate_paths_tool(G: nx.DiGraph, source: str, max_depth: int, max_paths: int = 10000) -> List[PropagationPath]:
    """
    Enumerate all propagation paths from source up to max_depth.
    Uses BFS to find all reachable paths.
    
    Args:
        G: NetworkX directed graph
        source: Source node ID
        max_depth: Maximum traversal depth
        max_paths: Maximum number of paths to enumerate (safety limit)
        
    Returns:
        List of PropagationPath objects
    """
    # Input validation
    if not isinstance(G, nx.DiGraph):
        raise TypeError("G must be a NetworkX DiGraph")
    if not isinstance(source, str) or not source:
        raise ValueError("source must be a non-empty string")
    if not isinstance(max_depth, int) or max_depth < 1:
        raise ValueError("max_depth must be a positive integer")
    if not isinstance(max_paths, int) or max_paths < 1:
        raise ValueError("max_paths must be a positive integer")
    
    if source not in G:
        logger.warning(f"Source node {source} not in graph")
        return []
    
    paths = []
    visited_paths: Set[tuple] = set()  # Track paths to avoid duplicates
    
    # BFS queue: (current_node, path_so_far, depth)
    queue = [(source, [source], 0)]
    iterations = 0
    max_iterations = max_paths * 10  # Safety limit for iterations
    
    while queue and len(paths) < max_paths:
        iterations += 1
        if iterations > max_iterations:
            logger.warning(f"Reached maximum iterations ({max_iterations}), stopping path enumeration")
            break
        
        current, path, depth = queue.pop(0)
        
        # Record this path if it has length > 0
        if len(path) > 1:
            path_tuple = tuple(path)
            if path_tuple not in visited_paths:
                visited_paths.add(path_tuple)
                # Collect all nodes affected by this path
                affected = set(path[1:])  # All nodes except source
                paths.append(PropagationPath(
                    path=path.copy(),
                    length=len(path) - 1,  # Number of edges
                    affected_nodes=list(affected)
                ))
        
        # Continue traversal if within depth limit
        if depth < max_depth:
            for neighbor in G.successors(current):
                if neighbor not in path:  # Avoid cycles
                    queue.append((neighbor, path + [neighbor], depth + 1))
    
    if len(paths) >= max_paths:
        logger.warning(f"Reached maximum path limit ({max_paths}), some paths may be missing")
    
    return paths


def calculate_metrics_tool(G: nx.DiGraph, paths: List[PropagationPath], source: str) -> Dict[str, Any]:
    """Calculate graph metrics from propagation paths"""
    if not paths:
        return {
            "max_fan_out": 0,
            "average_path_length": 0.0,
            "max_path_length": 0,
            "total_paths": 0
        }
    
    path_lengths = [p.length for p in paths]
    max_fan_out = max(len(list(G.successors(node))) for node in G.nodes()) if G.number_of_nodes() > 0 else 0
    
    return {
        "max_fan_out": max_fan_out,
        "average_path_length": sum(path_lengths) / len(path_lengths) if path_lengths else 0.0,
        "max_path_length": max(path_lengths) if path_lengths else 0,
        "total_paths": len(paths),
        "graph_nodes": G.number_of_nodes(),
        "graph_edges": G.number_of_edges()
    }


def simulate_propagation(
    vendor_id: str, 
    max_depth: int, 
    graph_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Execute simulation: enumerate propagation paths from source vendor.
    
    Args:
        vendor_id: Starting vendor/component ID
        max_depth: Maximum traversal depth
        graph_metadata: Optional graph structure (nodes, edges, attributes)
        
    Returns:
        Dict with propagation_paths, affected_nodes, metrics
    """
    try:
        # Input validation
        if not vendor_id or not isinstance(vendor_id, str):
            raise ValueError("vendor_id must be a non-empty string")
        if not isinstance(max_depth, int) or max_depth < 1 or max_depth > 10:
            raise ValueError("max_depth must be an integer between 1 and 10")
        
        # Build graph
        G = build_graph_tool(graph_metadata or {})
        logger.info(f"Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        
        # Enumerate paths (with safety limit)
        max_paths_limit = 10000  # Prevent memory issues with very large graphs
        paths = enumerate_paths_tool(G, vendor_id, max_depth, max_paths=max_paths_limit)
        logger.info(f"Enumerated {len(paths)} propagation paths")
        
        # Collect unique affected nodes
        unique_affected = set()
        for path in paths:
            unique_affected.update(path.affected_nodes)
        unique_affected_list = sorted(list(unique_affected))
        
        # Calculate metrics
        metrics = calculate_metrics_tool(G, paths, vendor_id)
        
        # Build output
        output = SimulationOutput(
            source_vendor_id=vendor_id,
            propagation_paths=paths,
            total_affected_nodes=len(unique_affected),
            unique_affected_nodes=unique_affected_list,
            metrics=metrics
        )
        
        logger.info(f"Simulation complete: {len(unique_affected)} nodes affected via {len(paths)} paths")
        
        # Return as dict for JSON serialization
        return output.model_dump()
        
    except Exception as e:
        logger.error(f"Simulation failed: {str(e)}", exc_info=True)
        raise


# Create ADK Tool for simulation
simulation_tool = FunctionTool(
    func=simulate_propagation
)


# Create ADK Agent
simulation_agent = Agent(
    name="SimulationAgent",
    instruction="""You are the SimulationAgent for Guardian AI, responsible for simulating failure propagation in supply-chain dependency graphs.

## Core Responsibility
Enumerate all possible propagation paths from a starting vendor/component failure through the dependency graph. This is a **deterministic graph traversal task**, not a prediction or forecasting exercise.

## Methodology
1. Start from the specified vendor_id
2. Perform breadth-first traversal (BFS) up to max_depth
3. Record all paths from source to affected nodes
4. Calculate basic graph metrics

## Rules
- **DO** perform deterministic graph traversal
- **DO** enumerate all reachable paths within depth limit
- **DO** record path lengths and affected nodes
- **DO NOT** assign probabilities or likelihoods
- **DO NOT** predict timing or attack scenarios
- **DO NOT** make assumptions about failure modes

Use the simulate_propagation tool to execute the simulation.""",
    description="Simulates failure propagation in supply-chain dependency graphs using deterministic graph traversal",
    tools=[simulation_tool]
)


class SimulationAgent:
    """
    SimulationAgent wrapper for backward compatibility.
    Uses Google ADK Agent internally.
    """
    
    def __init__(self):
        self.name = "SimulationAgent"
        self.agent = simulation_agent
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute simulation: enumerate propagation paths from source vendor.
        
        Args:
            input_data: Dict with vendor_id, max_depth, graph_metadata
            
        Returns:
            Dict with propagation_paths, affected_nodes, metrics
        """
        try:
            # Parse input
            sim_input = SimulationInput(**input_data)
            logger.info(f"[{self.name}] Starting simulation: vendor_id={sim_input.vendor_id}, max_depth={sim_input.max_depth}")
            
            # Use the tool directly for now (ADK engine integration will be in orchestrator)
            result = simulate_propagation(
                vendor_id=sim_input.vendor_id,
                max_depth=sim_input.max_depth,
                graph_metadata=sim_input.graph_metadata or {}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"[{self.name}] Simulation failed: {str(e)}", exc_info=True)
            raise
