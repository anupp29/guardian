import numpy as np
import networkx as nx
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum
import logging
from collections import defaultdict
import math

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class RiskMetrics:
    overall_score: float
    tier_1_exposure: float
    cascade_potential: float
    single_point_failures: int
    critical_path_count: int
    vulnerability_density: float
    resilience_score: float

@dataclass
class NodeRiskProfile:
    node_id: str
    base_risk: float
    structural_risk: float
    cascade_amplification: float
    centrality_risk: float
    combined_risk: float
    risk_level: RiskLevel
    contributing_factors: List[str]

class AdvancedRiskCalculator:
    """
    Advanced risk calculation engine that combines multiple risk factors
    including structural vulnerabilities, cascade potential, and centrality metrics.
    """
    
    def __init__(self):
        self.risk_weights = {
            'base_risk': 0.25,
            'structural_risk': 0.30,
            'cascade_amplification': 0.25,
            'centrality_risk': 0.20
        }
        
        self.tier_multipliers = {
            1: 3.0,  # Critical tier
            2: 2.0,  # Important tier
            3: 1.0   # Standard tier
        }
    
    def calculate_comprehensive_risk(self, supply_chain_graph, gnn_predictions: Optional[Dict] = None) -> RiskMetrics:
        """Calculate comprehensive risk metrics for the entire supply chain."""
        
        # Get basic graph statistics
        total_nodes = len(supply_chain_graph.graph.nodes())
        total_edges = len(supply_chain_graph.graph.edges())
        
        if total_nodes == 0:
            return RiskMetrics(0, 0, 0, 0, 0, 0, 1.0)
        
        # Calculate individual node risks
        node_risks = self.calculate_node_risk_profiles(supply_chain_graph, gnn_predictions)
        
        # Overall risk score (weighted average)
        overall_score = self._calculate_overall_risk_score(node_risks, supply_chain_graph)
        
        # Tier 1 exposure
        tier_1_exposure = self._calculate_tier_1_exposure(node_risks, supply_chain_graph)
        
        # Cascade potential
        cascade_potential = self._calculate_cascade_potential(supply_chain_graph, node_risks)
        
        # Structural vulnerabilities
        vulnerabilities = supply_chain_graph.identify_structural_vulnerabilities()
        single_point_failures = len(vulnerabilities.get('single_points_of_failure', []))
        
        # Critical path analysis
        critical_path_count = self._count_critical_paths(supply_chain_graph, node_risks)
        
        # Vulnerability density
        vulnerability_density = self._calculate_vulnerability_density(node_risks, total_nodes)
        
        # Resilience score
        resilience_score = self._calculate_resilience_score(supply_chain_graph, node_risks)
        
        return RiskMetrics(
            overall_score=overall_score,
            tier_1_exposure=tier_1_exposure,
            cascade_potential=cascade_potential,
            single_point_failures=single_point_failures,
            critical_path_count=critical_path_count,
            vulnerability_density=vulnerability_density,
            resilience_score=resilience_score
        )
    
    def calculate_node_risk_profiles(self, supply_chain_graph, gnn_predictions: Optional[Dict] = None) -> Dict[str, NodeRiskProfile]:
        """Calculate detailed risk profiles for each node."""
        node_risks = {}
        
        # Get centrality metrics
        try:
            centrality_metrics = supply_chain_graph.calculate_centrality_metrics()
        except Exception as e:
            logger.warning(f"Failed to calculate centrality metrics: {e}")
            centrality_metrics = {}
        
        # Get GNN predictions if available
        gnn_risk_scores = gnn_predictions.get('node_risk_scores', {}) if gnn_predictions else {}
        gnn_amplification = gnn_predictions.get('cascade_amplification', {}) if gnn_predictions else {}
        
        for node_id in supply_chain_graph.graph.nodes():
            # Base risk from node properties
            base_risk = self._calculate_base_risk(supply_chain_graph, node_id)
            
            # Structural risk from graph position
            structural_risk = self._calculate_structural_risk(supply_chain_graph, node_id, centrality_metrics)
            
            # Cascade amplification potential
            cascade_amplification = gnn_amplification.get(node_id, self._calculate_cascade_amplification_fallback(supply_chain_graph, node_id))
            
            # Centrality-based risk
            centrality_risk = self._calculate_centrality_risk(centrality_metrics.get(node_id, {}))
            
            # Combine risks using weighted formula
            combined_risk = (
                base_risk * self.risk_weights['base_risk'] +
                structural_risk * self.risk_weights['structural_risk'] +
                cascade_amplification * self.risk_weights['cascade_amplification'] +
                centrality_risk * self.risk_weights['centrality_risk']
            )
            
            # Apply tier multiplier
            tier = supply_chain_graph.node_features.get(node_id, type('obj', (object,), {'tier': 3})).tier
            tier_multiplier = self.tier_multipliers.get(tier, 1.0)
            combined_risk = min(1.0, combined_risk * tier_multiplier)
            
            # Determine risk level
            risk_level = self._determine_risk_level(combined_risk)
            
            # Identify contributing factors
            contributing_factors = self._identify_contributing_factors(
                base_risk, structural_risk, cascade_amplification, centrality_risk, tier
            )
            
            node_risks[node_id] = NodeRiskProfile(
                node_id=node_id,
                base_risk=base_risk,
                structural_risk=structural_risk,
                cascade_amplification=cascade_amplification,
                centrality_risk=centrality_risk,
                combined_risk=combined_risk,
                risk_level=risk_level,
                contributing_factors=contributing_factors
            )
        
        return node_risks
    
    def _calculate_base_risk(self, supply_chain_graph, node_id: str) -> float:
        """Calculate base risk from node properties."""
        node_data = supply_chain_graph.graph.nodes[node_id]
        
        # Start with explicit risk score
        base_risk = node_data.get('risk_score', 0.0)
        
        # Adjust based on audit recency
        last_audit = node_data.get('lastAudit')
        if last_audit:
            # Increase risk for older audits (simplified)
            base_risk = min(1.0, base_risk + 0.1)
        
        # Adjust based on certifications
        certifications = node_data.get('certifications', [])
        if not certifications:
            base_risk = min(1.0, base_risk + 0.15)
        elif len(certifications) >= 2:
            base_risk = max(0.0, base_risk - 0.1)
        
        # Adjust based on contract type
        contract_type = node_data.get('contractType', 'unknown')
        if contract_type == 'month-to-month':
            base_risk = min(1.0, base_risk + 0.1)
        elif contract_type == 'annual':
            base_risk = max(0.0, base_risk - 0.05)
        
        return base_risk
    
    def _calculate_structural_risk(self, supply_chain_graph, node_id: str, centrality_metrics: Dict) -> float:
        """Calculate risk based on structural position in the graph."""
        structural_risk = 0.0
        
        # High in-degree indicates many dependencies on this node
        in_degree = supply_chain_graph.graph.in_degree(node_id)
        max_degree = max(1, len(supply_chain_graph.graph.nodes()) - 1)
        in_degree_risk = (in_degree / max_degree) * 0.6
        
        # High out-degree indicates this node depends on many others
        out_degree = supply_chain_graph.graph.out_degree(node_id)
        out_degree_risk = (out_degree / max_degree) * 0.4
        
        structural_risk = in_degree_risk + out_degree_risk
        
        # Check if node is a single point of failure
        vulnerabilities = supply_chain_graph.identify_structural_vulnerabilities()
        if node_id in vulnerabilities.get('single_points_of_failure', []):
            structural_risk = min(1.0, structural_risk + 0.3)
        
        # Check if node is a bridge
        if node_id in vulnerabilities.get('bridge_nodes', []):
            structural_risk = min(1.0, structural_risk + 0.2)
        
        return structural_risk
    
    def _calculate_cascade_amplification_fallback(self, supply_chain_graph, node_id: str) -> float:
        """Fallback calculation for cascade amplification when GNN is not available."""
        # Simple heuristic based on reachability
        try:
            reachable_nodes = len(nx.descendants(supply_chain_graph.graph, node_id))
            total_nodes = len(supply_chain_graph.graph.nodes())
            
            if total_nodes <= 1:
                return 0.0
            
            amplification = reachable_nodes / (total_nodes - 1)
            
            # Adjust based on node tier
            tier = supply_chain_graph.node_features.get(node_id, type('obj', (object,), {'tier': 3})).tier
            tier_factor = (4 - tier) / 3  # Higher tier = higher amplification
            
            return min(1.0, amplification * tier_factor)
            
        except Exception:
            return 0.5  # Default moderate amplification
    
    def _calculate_centrality_risk(self, centrality_metrics: Dict) -> float:
        """Calculate risk based on centrality metrics."""
        if not centrality_metrics:
            return 0.5
        
        # Weighted combination of centrality measures
        betweenness = centrality_metrics.get('betweenness_centrality', 0.0)
        closeness = centrality_metrics.get('closeness_centrality', 0.0)
        pagerank = centrality_metrics.get('pagerank', 0.0)
        degree = centrality_metrics.get('degree_centrality', 0.0)
        
        # High centrality = high risk (more critical to network)
        centrality_risk = (
            betweenness * 0.3 +
            closeness * 0.2 +
            pagerank * 0.3 +
            degree * 0.2
        )
        
        return centrality_risk
    
    def _determine_risk_level(self, combined_risk: float) -> RiskLevel:
        """Determine risk level category from combined risk score."""
        if combined_risk >= 0.8:
            return RiskLevel.CRITICAL
        elif combined_risk >= 0.6:
            return RiskLevel.HIGH
        elif combined_risk >= 0.3:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _identify_contributing_factors(self, base_risk: float, structural_risk: float, 
                                     cascade_amplification: float, centrality_risk: float, tier: int) -> List[str]:
        """Identify the main contributing factors to risk."""
        factors = []
        
        if base_risk > 0.6:
            factors.append("High inherent risk score")
        
        if structural_risk > 0.6:
            factors.append("Critical structural position")
        
        if cascade_amplification > 0.6:
            factors.append("High cascade amplification potential")
        
        if centrality_risk > 0.6:
            factors.append("High network centrality")
        
        if tier == 1:
            factors.append("Critical tier classification")
        
        if not factors:
            factors.append("Moderate risk across multiple factors")
        
        return factors
    
    def _calculate_overall_risk_score(self, node_risks: Dict[str, NodeRiskProfile], supply_chain_graph) -> float:
        """Calculate overall risk score for the entire supply chain."""
        if not node_risks:
            return 0.0
        
        # Weighted average based on node importance (tier)
        total_weighted_risk = 0.0
        total_weight = 0.0
        
        for node_id, risk_profile in node_risks.items():
            tier = supply_chain_graph.node_features.get(node_id, type('obj', (object,), {'tier': 3})).tier
            weight = self.tier_multipliers.get(tier, 1.0)
            
            total_weighted_risk += risk_profile.combined_risk * weight
            total_weight += weight
        
        return total_weighted_risk / max(total_weight, 1.0)
    
    def _calculate_tier_1_exposure(self, node_risks: Dict[str, NodeRiskProfile], supply_chain_graph) -> float:
        """Calculate exposure of tier 1 (critical) nodes."""
        tier_1_nodes = []
        tier_1_risk_sum = 0.0
        
        for node_id, risk_profile in node_risks.items():
            tier = supply_chain_graph.node_features.get(node_id, type('obj', (object,), {'tier': 3})).tier
            if tier == 1:
                tier_1_nodes.append(node_id)
                tier_1_risk_sum += risk_profile.combined_risk
        
        if not tier_1_nodes:
            return 0.0
        
        return tier_1_risk_sum / len(tier_1_nodes)
    
    def _calculate_cascade_potential(self, supply_chain_graph, node_risks: Dict[str, NodeRiskProfile]) -> float:
        """Calculate overall cascade potential of the network."""
        if not node_risks:
            return 0.0
        
        # Average cascade amplification weighted by node risk
        total_cascade_potential = 0.0
        total_nodes = 0
        
        for node_id, risk_profile in node_risks.items():
            # Weight cascade amplification by the node's own risk
            weighted_amplification = risk_profile.cascade_amplification * risk_profile.combined_risk
            total_cascade_potential += weighted_amplification
            total_nodes += 1
        
        return total_cascade_potential / max(total_nodes, 1)
    
    def _count_critical_paths(self, supply_chain_graph, node_risks: Dict[str, NodeRiskProfile]) -> int:
        """Count the number of critical propagation paths."""
        critical_paths = 0
        
        # Find paths from high-risk nodes
        high_risk_nodes = [
            node_id for node_id, risk_profile in node_risks.items()
            if risk_profile.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        ]
        
        for source_node in high_risk_nodes:
            try:
                paths = supply_chain_graph.find_critical_paths(source_node, max_depth=3)
                # Count paths with high risk scores
                critical_paths += len([p for p in paths if p.risk_score > 0.6])
            except Exception:
                continue
        
        return critical_paths
    
    def _calculate_vulnerability_density(self, node_risks: Dict[str, NodeRiskProfile], total_nodes: int) -> float:
        """Calculate the density of vulnerable nodes in the network."""
        if total_nodes == 0:
            return 0.0
        
        vulnerable_nodes = len([
            risk_profile for risk_profile in node_risks.values()
            if risk_profile.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        ])
        
        return vulnerable_nodes / total_nodes
    
    def _calculate_resilience_score(self, supply_chain_graph, node_risks: Dict[str, NodeRiskProfile]) -> float:
        """Calculate overall resilience score (inverse of vulnerability)."""
        if not node_risks:
            return 1.0
        
        # Factors that contribute to resilience
        resilience_factors = []
        
        # 1. Redundancy (multiple paths between critical nodes)
        redundancy_score = self._calculate_redundancy_score(supply_chain_graph)
        resilience_factors.append(redundancy_score)
        
        # 2. Distribution of risk (not concentrated in few nodes)
        risk_distribution_score = self._calculate_risk_distribution_score(node_risks)
        resilience_factors.append(risk_distribution_score)
        
        # 3. Network connectivity (well-connected networks are more resilient)
        connectivity_score = self._calculate_connectivity_score(supply_chain_graph)
        resilience_factors.append(connectivity_score)
        
        # 4. Tier diversity (not over-reliant on single tier)
        tier_diversity_score = self._calculate_tier_diversity_score(supply_chain_graph)
        resilience_factors.append(tier_diversity_score)
        
        # Average resilience factors
        return sum(resilience_factors) / len(resilience_factors)
    
    def _calculate_redundancy_score(self, supply_chain_graph) -> float:
        """Calculate redundancy score based on alternative paths."""
        try:
            # Simple approximation: ratio of edges to minimum spanning tree edges
            num_edges = len(supply_chain_graph.graph.edges())
            num_nodes = len(supply_chain_graph.graph.nodes())
            
            if num_nodes <= 1:
                return 1.0
            
            min_edges_for_connectivity = num_nodes - 1
            redundancy = min(1.0, (num_edges - min_edges_for_connectivity) / max(1, min_edges_for_connectivity))
            
            return redundancy
        except Exception:
            return 0.5
    
    def _calculate_risk_distribution_score(self, node_risks: Dict[str, NodeRiskProfile]) -> float:
        """Calculate how evenly risk is distributed (more even = more resilient)."""
        if not node_risks:
            return 1.0
        
        risk_values = [risk_profile.combined_risk for risk_profile in node_risks.values()]
        
        # Calculate coefficient of variation (lower = more even distribution)
        mean_risk = np.mean(risk_values)
        if mean_risk == 0:
            return 1.0
        
        std_risk = np.std(risk_values)
        coefficient_of_variation = std_risk / mean_risk
        
        # Convert to resilience score (inverse relationship)
        distribution_score = 1.0 / (1.0 + coefficient_of_variation)
        
        return distribution_score
    
    def _calculate_connectivity_score(self, supply_chain_graph) -> float:
        """Calculate connectivity score (higher connectivity = more resilience)."""
        try:
            num_nodes = len(supply_chain_graph.graph.nodes())
            num_edges = len(supply_chain_graph.graph.edges())
            
            if num_nodes <= 1:
                return 1.0
            
            # Maximum possible edges in directed graph
            max_edges = num_nodes * (num_nodes - 1)
            
            # Connectivity as ratio of actual to maximum edges
            connectivity = num_edges / max(1, max_edges)
            
            return min(1.0, connectivity * 10)  # Scale up since real networks are sparse
        except Exception:
            return 0.5
    
    def _calculate_tier_diversity_score(self, supply_chain_graph) -> float:
        """Calculate tier diversity score (more diverse = more resilient)."""
        try:
            tier_counts = defaultdict(int)
            
            for node_id in supply_chain_graph.graph.nodes():
                tier = supply_chain_graph.node_features.get(node_id, type('obj', (object,), {'tier': 3})).tier
                tier_counts[tier] += 1
            
            if not tier_counts:
                return 1.0
            
            # Calculate entropy of tier distribution
            total_nodes = sum(tier_counts.values())
            entropy = 0.0
            
            for count in tier_counts.values():
                if count > 0:
                    probability = count / total_nodes
                    entropy -= probability * math.log2(probability)
            
            # Normalize entropy (max entropy for 3 tiers is log2(3))
            max_entropy = math.log2(3)
            diversity_score = entropy / max_entropy if max_entropy > 0 else 1.0
            
            return diversity_score
        except Exception:
            return 0.5


class RiskTrendAnalyzer:
    """Analyze risk trends over time and predict future risk evolution."""
    
    def __init__(self):
        self.historical_metrics = []
    
    def add_historical_snapshot(self, timestamp: str, risk_metrics: RiskMetrics):
        """Add a historical risk metrics snapshot."""
        self.historical_metrics.append({
            'timestamp': timestamp,
            'metrics': risk_metrics
        })
        
        # Keep only last 30 snapshots
        if len(self.historical_metrics) > 30:
            self.historical_metrics = self.historical_metrics[-30:]
    
    def calculate_risk_trends(self) -> Dict[str, float]:
        """Calculate risk trends from historical data."""
        if len(self.historical_metrics) < 2:
            return {
                'overall_trend': 0.0,
                'cascade_trend': 0.0,
                'vulnerability_trend': 0.0,
                'resilience_trend': 0.0
            }
        
        # Calculate trends as linear regression slopes
        trends = {}
        
        metrics_keys = ['overall_score', 'cascade_potential', 'vulnerability_density', 'resilience_score']
        
        for key in metrics_keys:
            values = [snapshot['metrics'].__dict__[key] for snapshot in self.historical_metrics]
            trend = self._calculate_linear_trend(values)
            trends[f"{key.replace('_score', '').replace('_', '_')}_trend"] = trend
        
        return trends
    
    def _calculate_linear_trend(self, values: List[float]) -> float:
        """Calculate linear trend (slope) from a series of values."""
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        x = list(range(n))
        
        # Calculate linear regression slope
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        return slope
    
    def predict_future_risk(self, days_ahead: int = 30) -> Dict[str, float]:
        """Predict future risk metrics based on current trends."""
        if not self.historical_metrics:
            return {}
        
        current_metrics = self.historical_metrics[-1]['metrics']
        trends = self.calculate_risk_trends()
        
        predictions = {}
        
        # Project current metrics forward using trends
        predictions['predicted_overall_score'] = min(1.0, max(0.0, 
            current_metrics.overall_score + trends.get('overall_trend', 0.0) * days_ahead
        ))
        
        predictions['predicted_cascade_potential'] = min(1.0, max(0.0,
            current_metrics.cascade_potential + trends.get('cascade_trend', 0.0) * days_ahead
        ))
        
        predictions['predicted_vulnerability_density'] = min(1.0, max(0.0,
            current_metrics.vulnerability_density + trends.get('vulnerability_trend', 0.0) * days_ahead
        ))
        
        predictions['predicted_resilience_score'] = min(1.0, max(0.0,
            current_metrics.resilience_score + trends.get('resilience_trend', 0.0) * days_ahead
        ))
        
        return predictions


# Utility functions for risk analysis
def categorize_nodes_by_risk(node_risks: Dict[str, NodeRiskProfile]) -> Dict[RiskLevel, List[str]]:
    """Categorize nodes by their risk levels."""
    categorized = {level: [] for level in RiskLevel}
    
    for node_id, risk_profile in node_risks.items():
        categorized[risk_profile.risk_level].append(node_id)
    
    return categorized


def identify_risk_hotspots(supply_chain_graph, node_risks: Dict[str, NodeRiskProfile], 
                          radius: int = 2) -> List[Dict]:
    """Identify clusters of high-risk nodes (risk hotspots)."""
    hotspots = []
    
    high_risk_nodes = [
        node_id for node_id, risk_profile in node_risks.items()
        if risk_profile.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
    ]
    
    processed = set()
    
    for node_id in high_risk_nodes:
        if node_id in processed:
            continue
        
        # Find nearby high-risk nodes
        nearby_nodes = set([node_id])
        
        # BFS to find nodes within radius
        queue = [(node_id, 0)]
        visited = set([node_id])
        
        while queue:
            current, distance = queue.pop(0)
            
            if distance < radius:
                # Add neighbors
                for neighbor in supply_chain_graph.graph.neighbors(current):
                    if neighbor not in visited and neighbor in high_risk_nodes:
                        nearby_nodes.add(neighbor)
                        visited.add(neighbor)
                        queue.append((neighbor, distance + 1))
        
        if len(nearby_nodes) >= 2:  # At least 2 nodes to form a hotspot
            hotspot_risk = sum(node_risks[n].combined_risk for n in nearby_nodes) / len(nearby_nodes)
            
            hotspots.append({
                'nodes': list(nearby_nodes),
                'average_risk': hotspot_risk,
                'size': len(nearby_nodes),
                'center': node_id
            })
            
            processed.update(nearby_nodes)
    
    # Sort by average risk
    hotspots.sort(key=lambda x: x['average_risk'], reverse=True)
    
    return hotspots


def calculate_mitigation_impact(supply_chain_graph, node_risks: Dict[str, NodeRiskProfile], 
                              mitigation_targets: List[str]) -> Dict[str, float]:
    """Calculate the impact of mitigating specific nodes."""
    calculator = AdvancedRiskCalculator()
    
    # Calculate current risk
    current_metrics = calculator.calculate_comprehensive_risk(supply_chain_graph)
    
    # Simulate mitigation by reducing risk of target nodes
    modified_graph = supply_chain_graph  # In practice, would create a copy
    
    # Temporarily reduce risk scores of mitigation targets
    original_risks = {}
    for node_id in mitigation_targets:
        if node_id in modified_graph.graph.nodes():
            original_risks[node_id] = modified_graph.graph.nodes[node_id].get('risk_score', 0.0)
            modified_graph.graph.nodes[node_id]['risk_score'] = original_risks[node_id] * 0.3  # 70% reduction
    
    # Recalculate risk
    mitigated_metrics = calculator.calculate_comprehensive_risk(modified_graph)
    
    # Restore original risks
    for node_id, original_risk in original_risks.items():
        modified_graph.graph.nodes[node_id]['risk_score'] = original_risk
    
    # Calculate impact
    impact = {
        'overall_risk_reduction': current_metrics.overall_score - mitigated_metrics.overall_score,
        'cascade_reduction': current_metrics.cascade_potential - mitigated_metrics.cascade_potential,
        'vulnerability_reduction': current_metrics.vulnerability_density - mitigated_metrics.vulnerability_density,
        'resilience_improvement': mitigated_metrics.resilience_score - current_metrics.resilience_score
    }
    
    return impact