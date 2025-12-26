import numpy as np
import networkx as nx
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum
import json
import logging
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class NodeType(Enum):
    VENDOR = "vendor"
    SOFTWARE = "software"
    SERVICE = "service"

class EdgeType(Enum):
    DEPENDS_ON = "depends_on"
    INTEGRATES_WITH = "integrates_with"
    SUPPLIES = "supplies"

@dataclass
class NodeFeatures:
    node_id: str
    node_type: NodeType
    tier: int  # 1=critical, 2=important, 3=standard
    in_degree: int
    out_degree: int
    dependency_depth: int
    risk_score: float
    criticality_score: float
    metadata: Dict

@dataclass
class EdgeFeatures:
    source: str
    target: str
    edge_type: EdgeType
    dependency_category: str
    strength: float
    criticality: str
    metadata: Dict

@dataclass
class PropagationPath:
    path: List[str]
    risk_score: float
    propagation_delay: int
    impact_level: str

class SupplyChainGraph:
    """
    Core graph representation for supply chain dependencies.
    Implements NetworkX-based graph with enhanced features for risk analysis.
    """
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.node_features: Dict[str, NodeFeatures] = {}
        self.edge_features: Dict[Tuple[str, str], EdgeFeatures] = {}
        self.risk_embeddings: Dict[str, np.ndarray] = {}
        
    def add_node(self, node_id: str, node_type: NodeType, tier: int, 
                 risk_score: float = 0.0, criticality_score: float = 0.0, 
                 metadata: Optional[Dict] = None):
        """Add a node to the supply chain graph."""
        if metadata is None:
            metadata = {}
            
        self.graph.add_node(node_id, 
                           node_type=node_type.value,
                           tier=tier,
                           risk_score=risk_score,
                           criticality_score=criticality_score,
                           **metadata)
        
        # Calculate graph metrics
        in_degree = self.graph.in_degree(node_id)
        out_degree = self.graph.out_degree(node_id)
        dependency_depth = self._calculate_dependency_depth(node_id)
        
        self.node_features[node_id] = NodeFeatures(
            node_id=node_id,
            node_type=node_type,
            tier=tier,
            in_degree=in_degree,
            out_degree=out_degree,
            dependency_depth=dependency_depth,
            risk_score=risk_score,
            criticality_score=criticality_score,
            metadata=metadata
        )
        
    def add_edge(self, source: str, target: str, edge_type: EdgeType,
                 dependency_category: str, strength: float = 1.0,
                 criticality: str = "medium", metadata: Optional[Dict] = None):
        """Add an edge to the supply chain graph."""
        if metadata is None:
            metadata = {}
            
        self.graph.add_edge(source, target,
                           edge_type=edge_type.value,
                           dependency_category=dependency_category,
                           strength=strength,
                           criticality=criticality,
                           **metadata)
        
        self.edge_features[(source, target)] = EdgeFeatures(
            source=source,
            target=target,
            edge_type=edge_type,
            dependency_category=dependency_category,
            strength=strength,
            criticality=criticality,
            metadata=metadata
        )
        
        # Update node degrees
        if source in self.node_features:
            self.node_features[source].out_degree = self.graph.out_degree(source)
        if target in self.node_features:
            self.node_features[target].in_degree = self.graph.in_degree(target)
            
    def _calculate_dependency_depth(self, node_id: str) -> int:
        """Calculate the maximum dependency depth from this node."""
        if not self.graph.has_node(node_id):
            return 0
            
        try:
            # Use BFS to find maximum depth
            visited = set()
            queue = deque([(node_id, 0)])
            max_depth = 0
            
            while queue:
                current, depth = queue.popleft()
                if current in visited:
                    continue
                    
                visited.add(current)
                max_depth = max(max_depth, depth)
                
                # Add successors
                for successor in self.graph.successors(current):
                    if successor not in visited:
                        queue.append((successor, depth + 1))
                        
            return max_depth
        except:
            return 0
            
    def get_subgraph(self, nodes: List[str]) -> 'SupplyChainGraph':
        """Extract a subgraph containing specified nodes and their connections."""
        subgraph = SupplyChainGraph()
        
        # Add nodes
        for node_id in nodes:
            if node_id in self.node_features:
                features = self.node_features[node_id]
                subgraph.add_node(
                    node_id=features.node_id,
                    node_type=features.node_type,
                    tier=features.tier,
                    risk_score=features.risk_score,
                    criticality_score=features.criticality_score,
                    metadata=features.metadata
                )
                
        # Add edges between included nodes
        for source, target in self.edge_features:
            if source in nodes and target in nodes:
                features = self.edge_features[(source, target)]
                subgraph.add_edge(
                    source=features.source,
                    target=features.target,
                    edge_type=features.edge_type,
                    dependency_category=features.dependency_category,
                    strength=features.strength,
                    criticality=features.criticality,
                    metadata=features.metadata
                )
                
        return subgraph
        
    def find_critical_paths(self, source: str, max_depth: int = 5) -> List[PropagationPath]:
        """Find critical propagation paths from a source node."""
        paths = []
        
        def dfs_paths(current: str, path: List[str], depth: int, risk_accumulator: float):
            if depth >= max_depth:
                return
                
            for successor in self.graph.successors(current):
                if successor not in path:  # Avoid cycles
                    new_path = path + [successor]
                    edge_risk = self.edge_features.get((current, successor), EdgeFeatures("", "", EdgeType.DEPENDS_ON, "", 0.5, "", {})).strength
                    node_risk = self.node_features.get(successor, NodeFeatures("", NodeType.VENDOR, 3, 0, 0, 0, 0.5, 0.5, {})).risk_score
                    
                    new_risk = risk_accumulator * edge_risk * (1 + node_risk)
                    
                    # Create propagation path
                    prop_path = PropagationPath(
                        path=new_path,
                        risk_score=new_risk,
                        propagation_delay=len(new_path) * 300,  # 300ms per hop
                        impact_level="high" if new_risk > 0.7 else "medium" if new_risk > 0.4 else "low"
                    )
                    paths.append(prop_path)
                    
                    # Continue DFS
                    dfs_paths(successor, new_path, depth + 1, new_risk)
        
        if source in self.graph:
            initial_risk = self.node_features.get(source, NodeFeatures("", NodeType.VENDOR, 3, 0, 0, 0, 0.5, 0.5, {})).risk_score
            dfs_paths(source, [source], 0, initial_risk)
            
        # Sort by risk score and return top paths
        paths.sort(key=lambda x: x.risk_score, reverse=True)
        return paths[:20]  # Return top 20 paths
        
    def calculate_centrality_metrics(self) -> Dict[str, Dict[str, float]]:
        """Calculate various centrality metrics for all nodes."""
        metrics = {}
        
        try:
            betweenness = nx.betweenness_centrality(self.graph)
            closeness = nx.closeness_centrality(self.graph)
            pagerank = nx.pagerank(self.graph)
            eigenvector = nx.eigenvector_centrality(self.graph, max_iter=1000)
        except:
            # Fallback to simple degree centrality if other metrics fail
            betweenness = {node: 0.0 for node in self.graph.nodes()}
            closeness = {node: 0.0 for node in self.graph.nodes()}
            pagerank = {node: 1.0/len(self.graph.nodes()) for node in self.graph.nodes()}
            eigenvector = {node: 0.0 for node in self.graph.nodes()}
            
        for node in self.graph.nodes():
            metrics[node] = {
                'betweenness_centrality': betweenness.get(node, 0.0),
                'closeness_centrality': closeness.get(node, 0.0),
                'pagerank': pagerank.get(node, 0.0),
                'eigenvector_centrality': eigenvector.get(node, 0.0),
                'degree_centrality': self.graph.degree(node) / max(1, len(self.graph.nodes()) - 1)
            }
            
        return metrics
        
    def identify_structural_vulnerabilities(self) -> Dict[str, List[str]]:
        """Identify structural vulnerabilities in the supply chain."""
        vulnerabilities = {
            'single_points_of_failure': [],
            'high_degree_nodes': [],
            'bridge_nodes': [],
            'critical_clusters': []
        }
        
        # Single points of failure (articulation points)
        try:
            articulation_points = list(nx.articulation_points(self.graph.to_undirected()))
            vulnerabilities['single_points_of_failure'] = articulation_points
        except:
            pass
            
        # High degree nodes (potential bottlenecks)
        degree_threshold = np.percentile([self.graph.degree(n) for n in self.graph.nodes()], 90)
        vulnerabilities['high_degree_nodes'] = [
            node for node in self.graph.nodes() 
            if self.graph.degree(node) >= degree_threshold
        ]
        
        # Bridge edges (critical connections)
        try:
            bridges = list(nx.bridges(self.graph.to_undirected()))
            bridge_nodes = set()
            for source, target in bridges:
                bridge_nodes.add(source)
                bridge_nodes.add(target)
            vulnerabilities['bridge_nodes'] = list(bridge_nodes)
        except:
            pass
            
        return vulnerabilities
        
    def simulate_cascade_failure(self, initial_compromised: List[str], 
                                propagation_threshold: float = 0.3) -> Dict:
        """Simulate cascade failure propagation through the network."""
        compromised = set(initial_compromised)
        propagating = set()
        affected = set()
        
        # Track propagation waves
        waves = []
        current_wave = list(initial_compromised)
        wave_number = 0
        
        while current_wave and wave_number < 10:  # Limit to 10 waves
            next_wave = []
            wave_info = {
                'wave': wave_number,
                'nodes': current_wave.copy(),
                'timestamp': wave_number * 300  # 300ms per wave
            }
            waves.append(wave_info)
            
            for node in current_wave:
                # Check all neighbors
                for neighbor in self.graph.successors(node):
                    if neighbor not in compromised and neighbor not in propagating:
                        # Calculate propagation probability
                        edge_strength = self.edge_features.get((node, neighbor), EdgeFeatures("", "", EdgeType.DEPENDS_ON, "", 0.5, "", {})).strength
                        neighbor_vulnerability = 1.0 - self.node_features.get(neighbor, NodeFeatures("", NodeType.VENDOR, 3, 0, 0, 0, 0.5, 0.5, {})).criticality_score / 100.0
                        
                        propagation_prob = edge_strength * neighbor_vulnerability
                        
                        if propagation_prob >= propagation_threshold:
                            propagating.add(neighbor)
                            next_wave.append(neighbor)
                            
            # Move propagating nodes to compromised
            compromised.update(propagating)
            current_wave = next_wave
            wave_number += 1
            
        # Calculate final impact
        total_affected = len(compromised)
        critical_affected = len([n for n in compromised if self.node_features.get(n, NodeFeatures("", NodeType.VENDOR, 3, 0, 0, 0, 0.5, 0.5, {})).tier == 1])
        
        return {
            'initial_compromised': initial_compromised,
            'total_affected': total_affected,
            'critical_affected': critical_affected,
            'compromised_nodes': list(compromised),
            'propagation_waves': waves,
            'blast_radius': total_affected - len(initial_compromised),
            'cascade_depth': len(waves)
        }
        
    def export_cytoscape_format(self) -> Dict:
        """Export graph in Cytoscape.js compatible format."""
        elements = []
        
        # Add nodes
        for node_id in self.graph.nodes():
            node_data = self.graph.nodes[node_id]
            features = self.node_features.get(node_id)
            
            element = {
                'data': {
                    'id': node_id,
                    'label': node_data.get('name', node_id),
                    'type': node_data.get('node_type', 'vendor'),
                    'tier': node_data.get('tier', 3),
                    'riskScore': node_data.get('risk_score', 0.0),
                    'criticalityScore': node_data.get('criticality_score', 0.0),
                    'status': node_data.get('status', 'secure'),
                    'category': node_data.get('category', 'unknown')
                }
            }
            elements.append(element)
            
        # Add edges
        for source, target in self.graph.edges():
            edge_data = self.graph.edges[source, target]
            
            element = {
                'data': {
                    'id': f"{source}-{target}",
                    'source': source,
                    'target': target,
                    'type': edge_data.get('edge_type', 'depends_on'),
                    'category': edge_data.get('dependency_category', 'data_flow'),
                    'strength': edge_data.get('strength', 1.0),
                    'criticality': edge_data.get('criticality', 'medium')
                }
            }
            elements.append(element)
            
        return {'elements': elements}
        
    def get_statistics(self) -> Dict:
        """Get comprehensive graph statistics."""
        return {
            'node_count': len(self.graph.nodes()),
            'edge_count': len(self.graph.edges()),
            'density': nx.density(self.graph),
            'is_connected': nx.is_weakly_connected(self.graph),
            'number_of_components': nx.number_weakly_connected_components(self.graph),
            'average_clustering': nx.average_clustering(self.graph.to_undirected()),
            'tier_distribution': self._get_tier_distribution(),
            'category_distribution': self._get_category_distribution()
        }
        
    def _get_tier_distribution(self) -> Dict[int, int]:
        """Get distribution of nodes by tier."""
        distribution = defaultdict(int)
        for node_id in self.graph.nodes():
            tier = self.node_features.get(node_id, NodeFeatures("", NodeType.VENDOR, 3, 0, 0, 0, 0.5, 0.5, {})).tier
            distribution[tier] += 1
        return dict(distribution)
        
    def _get_category_distribution(self) -> Dict[str, int]:
        """Get distribution of nodes by category."""
        distribution = defaultdict(int)
        for node_id in self.graph.nodes():
            category = self.graph.nodes[node_id].get('category', 'unknown')
            distribution[category] += 1
        return dict(distribution)