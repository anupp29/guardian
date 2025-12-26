"""
MitigationAgent - Ranks structural mitigations by risk reduction using Google ADK
"""

import logging
from typing import Dict, Any, List, Set, Optional
import networkx as nx

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from .schema import MitigationInput, MitigationOutput, MitigationAction

# Import simulation function - will be used in tool
try:
    from ..simulation.agent import simulate_propagation
except ImportError:
    # Fallback if circular import
    simulate_propagation = None


logger = logging.getLogger(__name__)


def build_graph_tool(graph_metadata: Dict[str, Any]) -> nx.DiGraph:
    """Build graph from metadata (reuse SimulationAgent logic)"""
    G = nx.DiGraph()
    
    if graph_metadata and 'nodes' in graph_metadata and 'edges' in graph_metadata:
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
        # Fallback sample graph
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


def evaluate_node_isolation(
    G: nx.DiGraph,
    node_id: str,
    original_paths: List[Dict[str, Any]],
    source_vendor: str,
    max_depth: int
) -> Dict[str, Any]:
    """
    Evaluate impact of isolating a node (removing it from graph).
    
    Args:
        G: Original graph
        node_id: Node to isolate
        original_paths: Original propagation paths
        source_vendor: Source vendor ID
        max_depth: Maximum depth for re-simulation
        
    Returns:
        Dict with risk_reduction, paths_reduced, feasible
    """
    # Input validation
    if not isinstance(G, nx.DiGraph):
        raise TypeError("G must be a NetworkX DiGraph")
    if not isinstance(node_id, str) or not node_id:
        raise ValueError("node_id must be a non-empty string")
    if not isinstance(original_paths, list):
        raise TypeError("original_paths must be a list")
    if node_id not in G or node_id == source_vendor:
        return {
            "risk_reduction": 0.0,
            "paths_reduced": 0,
            "feasible": False
        }
    
    # Create modified graph (will be cleaned up automatically)
    G_modified = G.copy()
    G_modified.remove_node(node_id)
    
    # Re-simulate
    try:
        graph_metadata = {
            "nodes": [{"id": str(n)} for n in G_modified.nodes()],  # Ensure string IDs
            "edges": [{"source": str(u), "target": str(v)} for u, v in G_modified.edges()]
        }
        if simulate_propagation is None:
            from ..simulation.agent import simulate_propagation
        if simulate_propagation is None:
            raise ImportError("Could not import simulate_propagation function")
        sim_result = simulate_propagation(str(source_vendor), max_depth, graph_metadata)
        new_paths = sim_result.get('propagation_paths', [])
        
        # Calculate reduction
        original_path_count = len(original_paths)
        new_path_count = len(new_paths)
        paths_reduced = max(0, original_path_count - new_path_count)
        risk_reduction = paths_reduced / original_path_count if original_path_count > 0 else 0.0
        
        return {
            "risk_reduction": risk_reduction,
            "paths_reduced": paths_reduced,
            "feasible": True
        }
    except Exception as e:
        logger.warning(f"Failed to evaluate isolation of {node_id}: {e}")
        return {
            "risk_reduction": 0.0,
            "paths_reduced": 0,
            "feasible": False
        }
    finally:
        # Cleanup: explicitly delete modified graph to free memory
        del G_modified


def evaluate_edge_removal(
    G: nx.DiGraph,
    source: str,
    target: str,
    original_paths: List[Dict[str, Any]],
    source_vendor: str,
    max_depth: int
) -> Dict[str, Any]:
    """
    Evaluate impact of removing a specific edge.
    
    Args:
        G: Original graph
        source: Source node of edge
        target: Target node of edge
        original_paths: Original propagation paths
        source_vendor: Source vendor ID
        max_depth: Maximum depth for re-simulation
        
    Returns:
        Dict with risk_reduction, paths_reduced, feasible
    """
    # Input validation
    if not isinstance(G, nx.DiGraph):
        raise TypeError("G must be a NetworkX DiGraph")
    if not isinstance(source, str) or not isinstance(target, str):
        raise ValueError("source and target must be strings")
    if not isinstance(original_paths, list):
        raise TypeError("original_paths must be a list")
    
    if not G.has_edge(source, target):
        return {
            "risk_reduction": 0.0,
            "paths_reduced": 0,
            "feasible": False
        }
    
    # Create modified graph (will be cleaned up automatically)
    G_modified = G.copy()
    G_modified.remove_edge(source, target)
    
    # Re-simulate
    try:
        graph_metadata = {
            "nodes": [{"id": str(n)} for n in G_modified.nodes()],  # Ensure string IDs
            "edges": [{"source": str(u), "target": str(v)} for u, v in G_modified.edges()]
        }
        global simulate_propagation
        if simulate_propagation is None:
            from ..simulation.agent import simulate_propagation
        if simulate_propagation is None:
            raise ImportError("Could not import simulate_propagation function")
        sim_result = simulate_propagation(str(source_vendor), max_depth, graph_metadata)
        new_paths = sim_result.get('propagation_paths', [])
        
        # Calculate reduction
        original_path_count = len(original_paths)
        new_path_count = len(new_paths)
        paths_reduced = max(0, original_path_count - new_path_count)
        risk_reduction = paths_reduced / original_path_count if original_path_count > 0 else 0.0
        
        return {
            "risk_reduction": risk_reduction,
            "paths_reduced": paths_reduced,
            "feasible": True
        }
    except Exception as e:
        logger.warning(f"Failed to evaluate edge removal {source}->{target}: {e}")
        return {
            "risk_reduction": 0.0,
            "paths_reduced": 0,
            "feasible": False
        }
    finally:
        # Cleanup: explicitly delete modified graph to free memory
        del G_modified


def estimate_complexity(action_type: str, target: str, G: nx.DiGraph) -> str:
    """Estimate implementation complexity"""
    if action_type == "isolate_node":
        # Complexity based on node degree
        if target in G:
            degree = G.in_degree(target) + G.out_degree(target)
            if degree <= 2:
                return "low"
            elif degree <= 5:
                return "medium"
            else:
                return "high"
    elif action_type == "remove_edge":
        return "low"  # Edge removal is typically simpler
    
    return "medium"


def evaluate_mitigations(
    simulation_results: Dict[str, Any],
    impact_explanations: Optional[List[Dict[str, Any]]] = None,
    graph_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Evaluate and rank mitigation actions by risk reduction.
    
    Args:
        simulation_results: Output from SimulationAgent
        impact_explanations: Output from ImpactReasoningAgent (optional)
        graph_metadata: Optional graph metadata
        
    Returns:
        Dict with ranked_mitigations, total_paths_original, total_paths_reducible
    """
    try:
        # Input validation
        if not isinstance(simulation_results, dict):
            raise ValueError("simulation_results must be a dictionary")
        
        source_vendor = simulation_results.get('source_vendor_id')
        if not source_vendor:
            raise ValueError("simulation_results must contain 'source_vendor_id'")
        
        original_paths = simulation_results.get('propagation_paths', [])
        affected_nodes = simulation_results.get('unique_affected_nodes', [])
        
        # Use max_path_length + 1 as proxy for original max_depth, or default to 3
        max_path_length = simulation_results.get('metrics', {}).get('max_path_length', 0)
        max_depth = max(max_path_length + 1, 3)  # Ensure at least 3, or use path length + 1
        
        if not original_paths:
            logger.warning("No paths to mitigate")
            return MitigationOutput(
                ranked_mitigations=[],
                total_paths_original=0,
                total_paths_reducible=0
            ).model_dump()
        
        # Build graph
        G = build_graph_tool(graph_metadata or {})
        
        # Safety check: limit number of mitigations to prevent memory issues
        max_mitigations = 50
        
        # Generate candidate mitigations
        mitigations = []
        
        # Candidate 1: Isolate high-impact nodes
        # Focus on nodes that appear in many paths
        node_path_count: Dict[str, int] = {}
        for path_data in original_paths:
            path = path_data.get('path', [])
            for node in path[1:]:  # Exclude source
                node_path_count[node] = node_path_count.get(node, 0) + 1
        
        # Evaluate top nodes by path count (limit to prevent excessive computation)
        top_nodes = sorted(node_path_count.items(), key=lambda x: x[1], reverse=True)[:min(5, max_mitigations)]
        
        for node_id, path_count in top_nodes:
            if len(mitigations) >= max_mitigations:
                logger.info(f"Reached maximum mitigation limit ({max_mitigations}), stopping evaluation")
                break
            if node_id != source_vendor:
                eval_result = evaluate_node_isolation(
                    G, node_id, original_paths, source_vendor, max_depth
                )
                if eval_result["feasible"] and eval_result["risk_reduction"] > 0:
                    complexity = estimate_complexity("isolate_node", node_id, G)
                    mitigations.append(MitigationAction(
                        action_type="isolate_node",
                        target=node_id,
                        description=f"Isolate {node_id} to break {path_count} propagation paths",
                        risk_reduction=eval_result["risk_reduction"],
                        affected_paths_reduced=eval_result["paths_reduced"],
                        implementation_complexity=complexity,
                        trade_offs=f"May impact services directly dependent on {node_id}"
                    ))
        
        # Candidate 2: Remove critical edges
        # Focus on edges that appear early in paths
        edge_path_count: Dict[tuple, int] = {}
        for path_data in original_paths:
            path = path_data.get('path', [])
            for i in range(len(path) - 1):
                edge = (path[i], path[i + 1])
                edge_path_count[edge] = edge_path_count.get(edge, 0) + 1
        
        # Evaluate top edges (limit to prevent excessive computation)
        remaining_slots = max_mitigations - len(mitigations)
        top_edges = sorted(edge_path_count.items(), key=lambda x: x[1], reverse=True)[:min(5, remaining_slots)]
        
        for (source, target), path_count in top_edges:
            if len(mitigations) >= max_mitigations:
                logger.info(f"Reached maximum mitigation limit ({max_mitigations}), stopping evaluation")
                break
            eval_result = evaluate_edge_removal(
                G, source, target, original_paths, source_vendor, max_depth
            )
            if eval_result["feasible"] and eval_result["risk_reduction"] > 0:
                mitigations.append(MitigationAction(
                    action_type="remove_edge",
                    target=f"{source}→{target}",
                    description=f"Remove dependency {source}→{target} to break {path_count} paths",
                    risk_reduction=eval_result["risk_reduction"],
                    affected_paths_reduced=eval_result["paths_reduced"],
                    implementation_complexity="low",
                    trade_offs=f"May require alternative supplier or integration method"
                ))
        
        # Rank by risk_reduction (descending)
        ranked = sorted(mitigations, key=lambda m: m.risk_reduction, reverse=True)
        
        # Calculate total reducible paths
        total_reducible = sum(m.affected_paths_reduced for m in ranked)
        
        output = MitigationOutput(
            ranked_mitigations=[m.model_dump() for m in ranked],
            total_paths_original=len(original_paths),
            total_paths_reducible=total_reducible
        )
        
        logger.info(f"Ranked {len(ranked)} mitigation actions")
        
        return output.model_dump()
        
    except Exception as e:
        logger.error(f"Mitigation evaluation failed: {str(e)}", exc_info=True)
        raise


# Create ADK Tool for mitigation evaluation
mitigation_tool = FunctionTool(
    func=evaluate_mitigations
)


# Create ADK Agent
mitigation_agent = Agent(
    name="MitigationAgent",
    instruction="""You are the MitigationAgent for Guardian AI, responsible for ranking structural mitigation actions by their effectiveness in reducing supply-chain risk exposure.

## Core Responsibility
Evaluate structural mitigations (node isolation, edge removal, redundancy) by simulating their impact on propagation paths. Rank actions by measurable risk reduction, not by intuition or heuristics.

## Methodology
1. Analyze original simulation results (paths, affected nodes)
2. For each candidate mitigation:
   - Simulate graph modification (remove node/edge, add redundancy)
   - Re-run propagation simulation
   - Measure reduction in affected paths/nodes
   - Calculate risk_reduction metric
3. Rank mitigations by risk_reduction (descending)

## Mitigation Types
- **isolate_node**: Remove node from graph (breaks all paths through it)
- **remove_edge**: Remove specific dependency edge
- **add_redundancy**: Add alternative path (not implemented in v1, placeholder)

## Rules
- **DO** measure risk reduction by re-simulating modified graphs
- **DO** rank by quantitative metrics (paths reduced, nodes isolated)
- **DO** explain trade-offs clearly
- **DO NOT** assign probabilities or likelihoods
- **DO NOT** predict attack scenarios
- **DO NOT** make assumptions about implementation feasibility

## Ranking Criteria
Primary: risk_reduction (paths eliminated / total paths)
Secondary: affected_paths_reduced (absolute count)
Tertiary: implementation_complexity (prefer lower complexity)

Use the evaluate_mitigations tool to process simulation results and generate ranked recommendations.""",
    description="Ranks structural mitigation actions by risk reduction effectiveness using graph simulation",
    tools=[mitigation_tool]
)


class MitigationAgent:
    """
    MitigationAgent wrapper for backward compatibility.
    Uses Google ADK Agent internally.
    """
    
    def __init__(self):
        self.name = "MitigationAgent"
        self.agent = mitigation_agent
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate and rank mitigation actions by risk reduction.
        
        Args:
            input_data: Dict with simulation_results, impact_explanations, graph_metadata
            
        Returns:
            Dict with ranked_mitigations, total_paths_original, total_paths_reducible
        """
        try:
            # Parse input
            mit_input = MitigationInput(**input_data)
            logger.info(f"[{self.name}] Evaluating mitigation actions")
            
            # Use the tool directly for now (ADK engine integration will be in orchestrator)
            result = evaluate_mitigations(
                simulation_results=mit_input.simulation_results,
                impact_explanations=mit_input.impact_explanations,
                graph_metadata=mit_input.graph_metadata or {}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"[{self.name}] Mitigation evaluation failed: {str(e)}", exc_info=True)
            raise
