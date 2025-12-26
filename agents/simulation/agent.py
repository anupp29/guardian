"""
SimulationAgent - Graph-based failure propagation simulation.

This agent uses NetworkX for deterministic graph traversal and path enumeration.
No probabilities, no predictions - only structural analysis.
"""

import logging
from typing import Dict, List, Set
import networkx as nx

from .schema import SimulationInput, SimulationOutput, PropagationPath, GraphMetrics

logger = logging.getLogger(__name__)


class SimulationAgent:
    """
    Simulates failure propagation through a supply chain dependency graph.
    
    Uses deterministic graph traversal to enumerate all possible impact paths
    from a source vendor within a specified depth limit.
    """
    
    def __init__(self):
        """Initialize the SimulationAgent."""
        self.agent_name = "SimulationAgent"
        logger.info(f"{self.agent_name} initialized")
    
    def run(self, input_data: SimulationInput) -> SimulationOutput:
        """
        Execute the simulation.
        
        Args:
            input_data: SimulationInput with vendor_id, graph_data, and max_depth
            
        Returns:
            SimulationOutput with propagation paths, affected nodes, and metrics
        """
        logger.info(f"{self.agent_name} starting execution")
        logger.info(f"  Source vendor: {input_data.vendor_id}")
        logger.info(f"  Max depth: {input_data.max_depth}")
        
        # Build NetworkX directed graph from adjacency list
        graph = self._build_graph(input_data.graph_data)
        
        # Validate source node exists
        if input_data.vendor_id not in graph:
            logger.warning(f"Source vendor {input_data.vendor_id} not found in graph")
            return SimulationOutput(
                source_vendor_id=input_data.vendor_id,
                propagation_paths=[],
                affected_node_ids=[],
                metrics=GraphMetrics(
                    total_affected_nodes=0,
                    max_fan_out=0,
                    average_path_length=0.0
                )
            )
        
        # Enumerate all paths from source within max_depth
        paths = self._enumerate_paths(graph, input_data.vendor_id, input_data.max_depth)
        
        # Extract unique affected nodes
        affected_nodes = self._extract_affected_nodes(paths)
        
        # Calculate graph metrics
        metrics = self._calculate_metrics(graph, paths, affected_nodes)
        
        # Convert to schema format
        propagation_paths = [
            PropagationPath(path=path, length=len(path) - 1)
            for path in paths
        ]
        
        output = SimulationOutput(
            source_vendor_id=input_data.vendor_id,
            propagation_paths=propagation_paths,
            affected_node_ids=sorted(affected_nodes),
            metrics=metrics
        )
        
        logger.info(f"{self.agent_name} completed execution")
        logger.info(f"  Found {len(paths)} propagation paths")
        logger.info(f"  Affected {len(affected_nodes)} nodes")
        
        return output
    
    def _build_graph(self, adjacency_list: Dict[str, List[str]]) -> nx.DiGraph:
        """Build a NetworkX directed graph from adjacency list."""
        graph = nx.DiGraph()
        for source, targets in adjacency_list.items():
            for target in targets:
                graph.add_edge(source, target)
        return graph
    
    def _enumerate_paths(
        self, 
        graph: nx.DiGraph, 
        source: str, 
        max_depth: int
    ) -> List[List[str]]:
        """
        Enumerate all paths from source within max_depth.
        
        Uses DFS to find all simple paths (no cycles) up to max_depth.
        """
        all_paths = []
        
        # Get all nodes reachable from source
        try:
            reachable = nx.descendants(graph, source)
        except nx.NetworkXError:
            reachable = set()
        
        # For each reachable node, find all simple paths
        for target in reachable:
            try:
                # Find all simple paths of length <= max_depth
                for path in nx.all_simple_paths(
                    graph, 
                    source=source, 
                    target=target, 
                    cutoff=max_depth
                ):
                    all_paths.append(path)
            except nx.NetworkXNoPath:
                continue
        
        # Also include single-edge paths from source
        for neighbor in graph.successors(source):
            if [source, neighbor] not in all_paths:
                all_paths.append([source, neighbor])
        
        return all_paths
    
    def _extract_affected_nodes(self, paths: List[List[str]]) -> Set[str]:
        """Extract unique set of affected nodes from all paths."""
        affected = set()
        for path in paths:
            # Skip the source node itself, include only downstream nodes
            affected.update(path[1:])
        return affected
    
    def _calculate_metrics(
        self, 
        graph: nx.DiGraph, 
        paths: List[List[str]], 
        affected_nodes: Set[str]
    ) -> GraphMetrics:
        """Calculate basic graph metrics."""
        # Total affected nodes
        total_affected = len(affected_nodes)
        
        # Max fan-out (outgoing edges) from any affected node
        max_fan_out = 0
        for node in affected_nodes:
            if node in graph:
                fan_out = graph.out_degree(node)
                max_fan_out = max(max_fan_out, fan_out)
        
        # Average path length
        if paths:
            total_length = sum(len(path) - 1 for path in paths)
            avg_path_length = total_length / len(paths)
        else:
            avg_path_length = 0.0
        
        return GraphMetrics(
            total_affected_nodes=total_affected,
            max_fan_out=max_fan_out,
            average_path_length=round(avg_path_length, 2)
        )
