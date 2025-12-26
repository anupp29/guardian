"""
MitigationAgent - Ranks structural mitigations by risk reduction using Google ADK
"""

import os
import logging
from typing import Dict, Any, List, Set, Optional
import networkx as nx

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from .schema import MitigationInput, MitigationOutput, MitigationAction


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
    """
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
    
    G_modified = G.copy()
    G_modified.remove_node(node_id)
    
    try:
        graph_metadata = {
            "nodes": [{"id": str(n)} for n in G_modified.nodes()],
            "edges": [{"source": str(u), "target": str(v)} for u, v in G_modified.edges()]
        }
        
        from ..simulation.agent import simulate_propagation
        sim_result = simulate_propagation(str(source_vendor), max_depth, graph_metadata)
        new_paths = sim_result.get('propagation_paths', [])
        
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
    """
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
    
    G_modified = G.copy()
    G_modified.remove_edge(source, target)
    
    try:
        graph_metadata = {
            "nodes": [{"id": str(n)} for n in G_modified.nodes()],
            "edges": [{"source": str(u), "target": str(v)} for u, v in G_modified.edges()]
        }
        
        from ..simulation.agent import simulate_propagation
        sim_result = simulate_propagation(str(source_vendor), max_depth, graph_metadata)
        new_paths = sim_result.get('propagation_paths', [])
        
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
        del G_modified


def estimate_complexity(action_type: str, target: str, G: nx.DiGraph) -> str:
    """Estimate implementation complexity"""
    if action_type == "isolate_node":
        if target in G:
            degree = G.in_degree(target) + G.out_degree(target)
            if degree <= 2:
                return "low"
            elif degree <= 5:
                return "medium"
            else:
                return "high"
    elif action_type == "remove_edge":
        return "low"
    
    return "medium"


def evaluate_mitigations(
    simulation_results: Dict[str, Any],
    impact_explanations: Optional[List[Dict[str, Any]]] = None,
    graph_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Evaluate and rank mitigation actions by risk reduction.
    """
    try:
        if not isinstance(simulation_results, dict):
            raise ValueError("simulation_results must be a dictionary")
        
        source_vendor = simulation_results.get('source_vendor_id')
        if not source_vendor:
            raise ValueError("simulation_results must contain 'source_vendor_id'")
        
        original_paths = simulation_results.get('propagation_paths', [])
        affected_nodes = simulation_results.get('unique_affected_nodes', [])
        
        max_path_length = simulation_results.get('metrics', {}).get('max_path_length', 0)
        max_depth = max(max_path_length + 1, 3)
        
        if not original_paths:
            logger.warning("No paths to mitigate")
            return MitigationOutput(
                ranked_mitigations=[],
                total_paths_original=0,
                total_paths_reducible=0
            ).model_dump()
        
        G = build_graph_tool(graph_metadata or {})
        
        max_mitigations = 50
        mitigations = []
        
        # Candidate 1: Isolate high-impact nodes
        node_path_count: Dict[str, int] = {}
        for path_data in original_paths:
            path = path_data.get('path', [])
            if isinstance(path, list) and len(path) > 1:
                for node in path[1:]:
                    if isinstance(node, str):
                        node_path_count[node] = node_path_count.get(node, 0) + 1
        
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
        edge_path_count: Dict[tuple, int] = {}
        for path_data in original_paths:
            path = path_data.get('path', [])
            if isinstance(path, list) and len(path) > 1:
                for i in range(len(path) - 1):
                    source = path[i]
                    target = path[i + 1]
                    if isinstance(source, str) and isinstance(target, str):
                        edge = (source, target)
                        edge_path_count[edge] = edge_path_count.get(edge, 0) + 1
        
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


class MitigationAgent:
    """
    MitigationAgent using Google ADK Agent.
    Ranks structural mitigation actions by risk reduction effectiveness.
    """
    
    def __init__(self):
        self.name = "MitigationAgent"
        
        # Create ADK Agent
        self.agent = Agent(
            name="MitigationAgent",
            instruction=self._load_prompt(),
            description="Ranks structural mitigation actions by risk reduction effectiveness using graph simulation",
            tools=[mitigation_tool]
        )
    
    def _load_prompt(self) -> str:
        """Load system prompt from prompt.md"""
        try:
            prompt_path = os.path.join(os.path.dirname(__file__), "prompt.md")
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return """You are the MitigationAgent for Guardian AI. Evaluate structural mitigations by simulating their impact on propagation paths and rank actions by measurable risk reduction."""
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate and rank mitigation actions by risk reduction.
        """
        try:
            mit_input = MitigationInput(**input_data)
            logger.info(f"[{self.name}] Evaluating mitigation actions")
            
            result = evaluate_mitigations(
                simulation_results=mit_input.simulation_results,
                impact_explanations=mit_input.impact_explanations,
                graph_metadata=mit_input.graph_metadata or {}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"[{self.name}] Mitigation evaluation failed: {str(e)}", exc_info=True)
            raise


# Create global instance for registry
mitigation_agent = MitigationAgent()