"""
MitigationAgent - Structural risk mitigation prioritization.

This agent simulates graph modifications to rank mitigations by
their effectiveness in reducing cascade risk.
"""

import logging
from typing import Dict, List, Set
import networkx as nx

from .schema import MitigationInput, MitigationOutput, MitigationAction

logger = logging.getLogger(__name__)


class MitigationAgent:
    """
    Prioritizes mitigation actions based on structural risk reduction.
    
    Simulates removing nodes or edges and measures the reduction in
    propagation paths and affected nodes.
    """
    
    def __init__(self):
        """Initialize the MitigationAgent."""
        self.agent_name = "MitigationAgent"
        logger.info(f"{self.agent_name} initialized")
    
    def run(self, input_data: MitigationInput) -> MitigationOutput:
        """
        Execute mitigation prioritization.
        
        Args:
            input_data: MitigationInput with graph data and affected nodes
            
        Returns:
            MitigationOutput with ranked mitigation actions
        """
        logger.info(f"{self.agent_name} starting execution")
        logger.info(f"  Analyzing mitigations for {len(input_data.affected_nodes)} affected nodes")
        
        # Build graph
        graph = self._build_graph(input_data.graph_data)
        
        # Baseline metrics
        baseline_paths = len(input_data.propagation_paths)
        baseline_affected = len(input_data.affected_nodes)
        
        logger.info(f"  Baseline: {baseline_paths} paths, {baseline_affected} affected nodes")
        
        # Early return if no affected nodes
        if baseline_affected == 0:
            logger.warning("No affected nodes to mitigate")
            return MitigationOutput(
                ranked_mitigations=[],
                total_paths_before=baseline_paths,
                methodology="No mitigations needed - no affected nodes"
            )
        
        # Evaluate node isolation mitigations
        mitigations = []
        
        # Calculate node criticality based on graph structure
        node_metrics = self._calculate_node_metrics(
            graph, 
            input_data.source_vendor_id,
            input_data.affected_nodes
        )
        
        # For each affected node (except source), simulate isolation
        for node in input_data.affected_nodes:
            if node == input_data.source_vendor_id:
                continue  # Don't isolate the source
            
            # Get node metrics
            metrics = node_metrics.get(node, {})
            
            # Simulate removing this node
            paths_reduced, nodes_reduced = self._evaluate_node_isolation(
                graph,
                input_data.source_vendor_id,
                node,
                baseline_affected
            )
            
            # Calculate risk reduction based on both paths and nodes
            if baseline_paths > 0:
                path_reduction_ratio = paths_reduced / baseline_paths
            else:
                path_reduction_ratio = 0.0
            
            if baseline_affected > 0:
                node_reduction_ratio = nodes_reduced / baseline_affected
            else:
                node_reduction_ratio = 0.0
            
            # Combined risk reduction (weighted average)
            risk_reduction = (path_reduction_ratio * 0.6) + (node_reduction_ratio * 0.4)
            
            # Only include if there's actual reduction
            if risk_reduction > 0:
                mitigations.append(MitigationAction(
                    action_type="isolate_node",
                    target=node,
                    description=self._generate_mitigation_description(node, metrics),
                    risk_reduction=round(risk_reduction, 3),
                    affected_paths_reduced=paths_reduced
                ))
        
        # Sort by risk reduction (descending)
        mitigations.sort(key=lambda x: x.risk_reduction, reverse=True)
        
        # Take top 10
        top_mitigations = mitigations[:10]
        
        output = MitigationOutput(
            ranked_mitigations=top_mitigations,
            total_paths_before=baseline_paths,
            methodology="Ranked by combined reduction in paths (60%) and downstream nodes (40%)"
        )
        
        logger.info(f"{self.agent_name} completed execution")
        logger.info(f"  Identified {len(top_mitigations)} top mitigations")
        
        return output
    
    def _build_graph(self, adjacency_list: Dict[str, List[str]]) -> nx.DiGraph:
        """Build a NetworkX directed graph from adjacency list."""
        graph = nx.DiGraph()
        for source, targets in adjacency_list.items():
            for target in targets:
                graph.add_edge(source, target)
        return graph
    
    def _calculate_node_metrics(
        self,
        graph: nx.DiGraph,
        source: str,
        affected_nodes: List[str]
    ) -> Dict[str, Dict]:
        """Calculate structural metrics for each affected node."""
        metrics = {}
        
        for node in affected_nodes:
            if node not in graph:
                continue
            
            # Out-degree (fan-out)
            out_degree = graph.out_degree(node)
            
            # In-degree (dependencies)
            in_degree = graph.in_degree(node)
            
            # Descendants count
            try:
                descendants = len(nx.descendants(graph, node))
            except nx.NetworkXError:
                descendants = 0
            
            metrics[node] = {
                "out_degree": out_degree,
                "in_degree": in_degree,
                "descendants": descendants,
                "is_hub": out_degree > 1  # Hub if multiple outgoing edges
            }
        
        return metrics
    
    def _evaluate_node_isolation(
        self,
        graph: nx.DiGraph,
        source: str,
        node_to_remove: str,
        baseline_affected: int
    ) -> tuple[int, int]:
        """
        Evaluate the risk reduction from isolating a node.
        
        Args:
            graph: The dependency graph
            source: Source vendor ID
            node_to_remove: Node to simulate removing
            baseline_affected: Baseline count of affected nodes
            
        Returns:
            Tuple of (paths_reduced, nodes_reduced)
        """
        # Create a copy of the graph
        modified_graph = graph.copy()
        
        # Remove the node and all its edges
        if node_to_remove not in modified_graph:
            return (0, 0)
        
        # Count paths before removal
        paths_before = self._count_paths_through_node(graph, source, node_to_remove)
        
        # Remove the node
        modified_graph.remove_node(node_to_remove)
        
        # Count affected nodes in modified graph
        try:
            new_affected = len(nx.descendants(modified_graph, source))
        except nx.NetworkXError:
            new_affected = 0
        
        # Calculate reductions
        nodes_reduced = baseline_affected - new_affected
        paths_reduced = paths_before  # All paths through this node are eliminated
        
        return (paths_reduced, nodes_reduced)
    
    def _count_paths_through_node(
        self,
        graph: nx.DiGraph,
        source: str,
        intermediate_node: str
    ) -> int:
        """Count how many paths from source pass through intermediate_node."""
        if intermediate_node not in graph or source not in graph:
            return 0
        
        count = 0
        try:
            # Get all reachable nodes from source
            reachable = nx.descendants(graph, source)
            
            # For each reachable node, check if there's a path through intermediate
            for target in reachable:
                if target == intermediate_node:
                    continue
                
                # Check if there are paths source -> intermediate -> target
                try:
                    # Check if intermediate is on any path from source to target
                    for path in nx.all_simple_paths(graph, source, target, cutoff=10):
                        if intermediate_node in path:
                            count += 1
                            break  # Count each target only once
                except (nx.NetworkXNoPath, nx.NodeNotFound):
                    continue
            
            # Also count direct paths source -> intermediate
            if intermediate_node in reachable:
                count += 1
                
        except nx.NetworkXError:
            pass
        
        return count
    
    def _generate_mitigation_description(self, node: str, metrics: Dict) -> str:
        """Generate a human-readable description for a mitigation action."""
        is_hub = metrics.get("is_hub", False)
        out_degree = metrics.get("out_degree", 0)
        descendants = metrics.get("descendants", 0)
        
        if is_hub:
            return f"Isolate critical hub {node} (fan-out: {out_degree}, downstream: {descendants}) to prevent cascade"
        elif descendants > 0:
            return f"Isolate intermediate node {node} (downstream: {descendants}) to limit propagation"
        else:
            return f"Isolate leaf node {node} to reduce exposure"
