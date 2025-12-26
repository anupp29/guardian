import numpy as np
import networkx as nx
from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from collections import defaultdict, deque
import random
import time
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SimulationStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class NodeStatus(Enum):
    SECURE = "secure"
    COMPROMISED = "compromised"
    PROPAGATING = "propagating"
    AFFECTED = "affected"
    ISOLATED = "isolated"

@dataclass
class SimulationStep:
    step_number: int
    timestamp: float
    action: str
    affected_nodes: List[str]
    new_compromised: List[str]
    propagation_paths: List[List[str]]
    metrics: Dict[str, Any]

@dataclass
class SimulationResult:
    simulation_id: str
    status: SimulationStatus
    initial_compromised: List[str]
    final_compromised: List[str]
    total_affected: int
    blast_radius: int
    cascade_depth: int
    propagation_time: float
    steps: List[SimulationStep]
    final_metrics: Dict[str, Any]
    risk_analysis: Dict[str, Any]
    mitigation_suggestions: List[Dict[str, Any]]

@dataclass
class PropagationRule:
    name: str
    condition: callable
    probability_modifier: float
    delay_modifier: float
    description: str

class AdvancedSimulationEngine:
    """
    Advanced simulation engine for supply chain compromise propagation.
    Implements sophisticated propagation models with realistic timing and probabilities.
    """
    
    def __init__(self, supply_chain_graph, gnn_inference_engine=None, risk_calculator=None):
        self.graph = supply_chain_graph
        self.gnn_engine = gnn_inference_engine
        self.risk_calculator = risk_calculator
        
        # Simulation parameters
        self.base_propagation_probability = 0.3
        self.base_propagation_delay = 300  # milliseconds
        self.max_simulation_steps = 20
        self.max_simulation_time = 10000  # milliseconds
        
        # Propagation rules
        self.propagation_rules = self._initialize_propagation_rules()
        
        # Active simulations
        self.active_simulations = {}
        
    def _initialize_propagation_rules(self) -> List[PropagationRule]:
        """Initialize propagation rules that modify how compromises spread."""
        rules = []
        
        # High-tier nodes propagate faster
        rules.append(PropagationRule(
            name="tier_amplification",
            condition=lambda source, target, graph: graph.node_features.get(source, type('obj', (object,), {'tier': 3})).tier == 1,
            probability_modifier=1.5,
            delay_modifier=0.7,
            description="Critical tier nodes propagate compromises faster and more reliably"
        ))
        
        # Authentication dependencies are high-risk
        rules.append(PropagationRule(
            name="auth_dependency",
            condition=lambda source, target, graph: graph.graph.edges.get((source, target), {}).get('dependency_category') == 'authentication',
            probability_modifier=2.0,
            delay_modifier=0.5,
            description="Authentication dependencies create high-risk propagation paths"
        ))
        
        # API integrations spread quickly
        rules.append(PropagationRule(
            name="api_integration",
            condition=lambda source, target, graph: graph.graph.edges.get((source, target), {}).get('dependency_category') == 'api_call',
            probability_modifier=1.3,
            delay_modifier=0.8,
            description="API integrations enable rapid compromise propagation"
        ))
        
        # High-strength dependencies
        rules.append(PropagationRule(
            name="strong_dependency",
            condition=lambda source, target, graph: graph.edge_features.get((source, target), type('obj', (object,), {'strength': 0.5})).strength > 0.8,
            probability_modifier=1.4,
            delay_modifier=0.9,
            description="Strong dependencies increase propagation likelihood"
        ))
        
        # Nodes with many incoming connections are vulnerable
        rules.append(PropagationRule(
            name="high_indegree_vulnerability",
            condition=lambda source, target, graph: graph.graph.in_degree(target) > np.percentile([graph.graph.in_degree(n) for n in graph.graph.nodes()], 75),
            probability_modifier=1.2,
            delay_modifier=1.0,
            description="Nodes with many dependencies are more vulnerable to compromise"
        ))
        
        return rules
    
    def run_simulation(self, initial_compromised: List[str], simulation_id: Optional[str] = None) -> SimulationResult:
        """
        Run a comprehensive supply chain compromise simulation.
        
        Args:
            initial_compromised: List of initially compromised node IDs
            simulation_id: Optional simulation identifier
            
        Returns:
            SimulationResult containing detailed simulation outcomes
        """
        if simulation_id is None:
            simulation_id = f"sim_{int(time.time() * 1000)}"
        
        logger.info(f"Starting simulation {simulation_id} with initial compromised: {initial_compromised}")
        
        # Initialize simulation state
        simulation_state = {
            'compromised': set(initial_compromised),
            'propagating': set(),
            'affected': set(),
            'secure': set(self.graph.graph.nodes()) - set(initial_compromised),
            'step_number': 0,
            'simulation_time': 0.0,
            'steps': []
        }
        
        self.active_simulations[simulation_id] = {
            'status': SimulationStatus.RUNNING,
            'start_time': time.time(),
            'state': simulation_state
        }
        
        try:
            # Run simulation steps
            while (simulation_state['step_number'] < self.max_simulation_steps and 
                   simulation_state['simulation_time'] < self.max_simulation_time):
                
                step_result = self._execute_simulation_step(simulation_state)
                
                if not step_result['new_compromised'] and not step_result['propagating_nodes']:
                    # No new propagation, simulation complete
                    break
                
                simulation_state['steps'].append(step_result)
                simulation_state['step_number'] += 1
            
            # Calculate final results
            final_result = self._finalize_simulation(simulation_id, simulation_state, initial_compromised)
            
            self.active_simulations[simulation_id]['status'] = SimulationStatus.COMPLETED
            return final_result
            
        except Exception as e:
            logger.error(f"Simulation {simulation_id} failed: {e}")
            self.active_simulations[simulation_id]['status'] = SimulationStatus.FAILED
            
            # Return partial results
            return SimulationResult(
                simulation_id=simulation_id,
                status=SimulationStatus.FAILED,
                initial_compromised=initial_compromised,
                final_compromised=list(simulation_state['compromised']),
                total_affected=len(simulation_state['compromised']) + len(simulation_state['affected']),
                blast_radius=len(simulation_state['compromised']) - len(initial_compromised),
                cascade_depth=simulation_state['step_number'],
                propagation_time=simulation_state['simulation_time'],
                steps=simulation_state['steps'],
                final_metrics={},
                risk_analysis={},
                mitigation_suggestions=[]
            )
    
    def _execute_simulation_step(self, simulation_state: Dict) -> SimulationStep:
        """Execute a single simulation step."""
        step_start_time = simulation_state['simulation_time']
        new_compromised = []
        propagation_paths = []
        propagating_nodes = []
        
        # Process each currently compromised node
        for compromised_node in list(simulation_state['compromised']):
            # Find potential propagation targets
            targets = list(self.graph.graph.successors(compromised_node))
            
            for target in targets:
                if target in simulation_state['secure']:
                    # Calculate propagation probability and delay
                    propagation_prob, delay = self._calculate_propagation_parameters(
                        compromised_node, target
                    )
                    
                    # Check if propagation occurs
                    if random.random() < propagation_prob:
                        propagating_nodes.append(target)
                        propagation_paths.append([compromised_node, target])
                        
                        # Add delay for this propagation
                        simulation_state['simulation_time'] += delay
        
        # Move propagating nodes to compromised
        for node in propagating_nodes:
            if node in simulation_state['secure']:
                simulation_state['secure'].remove(node)
                simulation_state['compromised'].add(node)
                new_compromised.append(node)
        
        # Update affected nodes (nodes connected to compromised but not compromised themselves)
        for compromised_node in simulation_state['compromised']:
            for neighbor in self.graph.graph.neighbors(compromised_node):
                if neighbor in simulation_state['secure']:
                    simulation_state['affected'].add(neighbor)
        
        # Calculate step metrics
        step_metrics = {
            'total_compromised': len(simulation_state['compromised']),
            'total_affected': len(simulation_state['affected']),
            'propagation_rate': len(new_compromised),
            'network_coverage': (len(simulation_state['compromised']) + len(simulation_state['affected'])) / len(self.graph.graph.nodes())
        }
        
        return SimulationStep(
            step_number=simulation_state['step_number'],
            timestamp=simulation_state['simulation_time'],
            action=f"Propagation step {simulation_state['step_number']}",
            affected_nodes=list(simulation_state['affected']),
            new_compromised=new_compromised,
            propagation_paths=propagation_paths,
            metrics=step_metrics
        )
    
    def _calculate_propagation_parameters(self, source: str, target: str) -> Tuple[float, float]:
        """Calculate propagation probability and delay for a specific edge."""
        # Base parameters
        probability = self.base_propagation_probability
        delay = self.base_propagation_delay
        
        # Get edge properties
        edge_data = self.graph.graph.edges.get((source, target), {})
        edge_strength = edge_data.get('strength', 0.5)
        
        # Get node properties
        target_vulnerability = 1.0 - (self.graph.node_features.get(target, type('obj', (object,), {'criticality_score': 50})).criticality_score / 100.0)
        
        # Base calculation
        probability *= edge_strength * (1 + target_vulnerability)
        
        # Apply propagation rules
        for rule in self.propagation_rules:
            try:
                if rule.condition(source, target, self.graph):
                    probability *= rule.probability_modifier
                    delay *= rule.delay_modifier
            except Exception as e:
                logger.warning(f"Rule {rule.name} failed: {e}")
        
        # Use GNN predictions if available
        if self.gnn_engine:
            try:
                gnn_predictions = self.gnn_engine.predict_cascade_amplification(self.graph)
                source_amplification = gnn_predictions.get(source, 0.5)
                probability *= (1 + source_amplification)
            except Exception as e:
                logger.warning(f"GNN prediction failed: {e}")
        
        # Clamp values
        probability = min(1.0, max(0.0, probability))
        delay = max(50, delay)  # Minimum 50ms delay
        
        return probability, delay
    
    def _finalize_simulation(self, simulation_id: str, simulation_state: Dict, initial_compromised: List[str]) -> SimulationResult:
        """Finalize simulation and calculate comprehensive results."""
        
        final_compromised = list(simulation_state['compromised'])
        total_affected = len(simulation_state['compromised']) + len(simulation_state['affected'])
        blast_radius = len(simulation_state['compromised']) - len(initial_compromised)
        
        # Calculate final metrics
        final_metrics = self._calculate_final_metrics(simulation_state)
        
        # Perform risk analysis
        risk_analysis = self._perform_risk_analysis(simulation_state, initial_compromised)
        
        # Generate mitigation suggestions
        mitigation_suggestions = self._generate_mitigation_suggestions(simulation_state, risk_analysis)
        
        return SimulationResult(
            simulation_id=simulation_id,
            status=SimulationStatus.COMPLETED,
            initial_compromised=initial_compromised,
            final_compromised=final_compromised,
            total_affected=total_affected,
            blast_radius=blast_radius,
            cascade_depth=simulation_state['step_number'],
            propagation_time=simulation_state['simulation_time'],
            steps=simulation_state['steps'],
            final_metrics=final_metrics,
            risk_analysis=risk_analysis,
            mitigation_suggestions=mitigation_suggestions
        )
    
    def _calculate_final_metrics(self, simulation_state: Dict) -> Dict[str, Any]:
        """Calculate comprehensive final metrics."""
        total_nodes = len(self.graph.graph.nodes())
        compromised_count = len(simulation_state['compromised'])
        affected_count = len(simulation_state['affected'])
        
        # Basic metrics
        metrics = {
            'compromise_rate': compromised_count / total_nodes,
            'impact_rate': (compromised_count + affected_count) / total_nodes,
            'average_propagation_time': simulation_state['simulation_time'] / max(1, simulation_state['step_number']),
            'propagation_efficiency': compromised_count / max(1, simulation_state['simulation_time'] / 1000)  # nodes per second
        }
        
        # Tier-specific impact
        tier_impact = defaultdict(int)
        for node_id in simulation_state['compromised']:
            tier = self.graph.node_features.get(node_id, type('obj', (object,), {'tier': 3})).tier
            tier_impact[tier] += 1
        
        metrics['tier_impact'] = dict(tier_impact)
        
        # Category-specific impact
        category_impact = defaultdict(int)
        for node_id in simulation_state['compromised']:
            category = self.graph.graph.nodes[node_id].get('category', 'unknown')
            category_impact[category] += 1
        
        metrics['category_impact'] = dict(category_impact)
        
        # Critical path analysis
        critical_paths = []
        for step in simulation_state['steps']:
            for path in step.propagation_paths:
                if len(path) >= 2:
                    source_tier = self.graph.node_features.get(path[0], type('obj', (object,), {'tier': 3})).tier
                    target_tier = self.graph.node_features.get(path[-1], type('obj', (object,), {'tier': 3})).tier
                    
                    if source_tier <= 2 or target_tier <= 2:  # Critical or important tiers
                        critical_paths.append(path)
        
        metrics['critical_paths'] = critical_paths
        metrics['critical_path_count'] = len(critical_paths)
        
        return metrics
    
    def _perform_risk_analysis(self, simulation_state: Dict, initial_compromised: List[str]) -> Dict[str, Any]:
        """Perform detailed risk analysis of simulation results."""
        analysis = {}
        
        # Identify most impactful initial nodes
        impact_scores = {}
        for initial_node in initial_compromised:
            # Count nodes reachable from this initial node
            reachable = set()
            queue = deque([initial_node])
            visited = set([initial_node])
            
            while queue:
                current = queue.popleft()
                for step in simulation_state['steps']:
                    for path in step.propagation_paths:
                        if len(path) >= 2 and path[0] == current and path[1] not in visited:
                            reachable.add(path[1])
                            visited.add(path[1])
                            queue.append(path[1])
            
            impact_scores[initial_node] = len(reachable)
        
        analysis['initial_node_impact'] = impact_scores
        
        # Identify bottleneck nodes (nodes that appear in many propagation paths)
        bottleneck_counts = defaultdict(int)
        for step in simulation_state['steps']:
            for path in step.propagation_paths:
                for node in path:
                    bottleneck_counts[node] += 1
        
        # Sort by frequency
        bottlenecks = sorted(bottleneck_counts.items(), key=lambda x: x[1], reverse=True)
        analysis['bottleneck_nodes'] = bottlenecks[:10]  # Top 10
        
        # Calculate propagation velocity over time
        velocity_over_time = []
        cumulative_compromised = len(initial_compromised)
        
        for step in simulation_state['steps']:
            cumulative_compromised += len(step.new_compromised)
            velocity = len(step.new_compromised) / max(1, step.timestamp / 1000)  # nodes per second
            velocity_over_time.append({
                'step': step.step_number,
                'timestamp': step.timestamp,
                'velocity': velocity,
                'cumulative_compromised': cumulative_compromised
            })
        
        analysis['propagation_velocity'] = velocity_over_time
        
        # Identify critical failure points
        critical_failures = []
        for step in simulation_state['steps']:
            if len(step.new_compromised) > 3:  # Large propagation events
                critical_failures.append({
                    'step': step.step_number,
                    'timestamp': step.timestamp,
                    'new_compromised_count': len(step.new_compromised),
                    'nodes': step.new_compromised,
                    'paths': step.propagation_paths
                })
        
        analysis['critical_failure_points'] = critical_failures
        
        return analysis
    
    def _generate_mitigation_suggestions(self, simulation_state: Dict, risk_analysis: Dict) -> List[Dict[str, Any]]:
        """Generate actionable mitigation suggestions based on simulation results."""
        suggestions = []
        
        # Suggest isolating high-impact initial nodes
        initial_impacts = risk_analysis.get('initial_node_impact', {})
        if initial_impacts:
            highest_impact_node = max(initial_impacts.items(), key=lambda x: x[1])
            suggestions.append({
                'type': 'isolation',
                'priority': 'high',
                'target': highest_impact_node[0],
                'description': f"Isolate {highest_impact_node[0]} - caused {highest_impact_node[1]} secondary compromises",
                'estimated_impact_reduction': highest_impact_node[1] / len(simulation_state['compromised']),
                'implementation_complexity': 'medium'
            })
        
        # Suggest securing bottleneck nodes
        bottlenecks = risk_analysis.get('bottleneck_nodes', [])
        if bottlenecks:
            top_bottleneck = bottlenecks[0]
            suggestions.append({
                'type': 'hardening',
                'priority': 'high',
                'target': top_bottleneck[0],
                'description': f"Harden {top_bottleneck[0]} - appears in {top_bottleneck[1]} propagation paths",
                'estimated_impact_reduction': 0.3,
                'implementation_complexity': 'medium'
            })
        
        # Suggest redundancy for critical paths
        critical_failures = risk_analysis.get('critical_failure_points', [])
        if critical_failures:
            largest_failure = max(critical_failures, key=lambda x: x['new_compromised_count'])
            suggestions.append({
                'type': 'redundancy',
                'priority': 'medium',
                'target': largest_failure['nodes'],
                'description': f"Add redundancy for nodes compromised in step {largest_failure['step']}",
                'estimated_impact_reduction': 0.4,
                'implementation_complexity': 'high'
            })
        
        # Suggest monitoring for high-velocity propagation
        velocity_data = risk_analysis.get('propagation_velocity', [])
        if velocity_data:
            max_velocity_step = max(velocity_data, key=lambda x: x['velocity'])
            if max_velocity_step['velocity'] > 1.0:  # More than 1 node per second
                suggestions.append({
                    'type': 'monitoring',
                    'priority': 'medium',
                    'target': 'network_wide',
                    'description': f"Implement real-time monitoring - detected propagation velocity of {max_velocity_step['velocity']:.2f} nodes/sec",
                    'estimated_impact_reduction': 0.2,
                    'implementation_complexity': 'low'
                })
        
        # Suggest tier-specific protections
        tier_impacts = simulation_state.get('final_metrics', {}).get('tier_impact', {})
        if tier_impacts.get(1, 0) > 0:  # Critical tier affected
            suggestions.append({
                'type': 'tier_protection',
                'priority': 'critical',
                'target': 'tier_1_nodes',
                'description': f"Implement additional protections for {tier_impacts[1]} compromised critical tier nodes",
                'estimated_impact_reduction': 0.6,
                'implementation_complexity': 'high'
            })
        
        # Sort suggestions by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        suggestions.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return suggestions
    
    def run_comparative_simulation(self, scenarios: List[Dict[str, Any]]) -> Dict[str, SimulationResult]:
        """Run multiple simulation scenarios for comparison."""
        results = {}
        
        for i, scenario in enumerate(scenarios):
            scenario_id = scenario.get('id', f"scenario_{i}")
            initial_compromised = scenario['initial_compromised']
            
            logger.info(f"Running comparative scenario: {scenario_id}")
            result = self.run_simulation(initial_compromised, f"comp_{scenario_id}")
            results[scenario_id] = result
        
        return results
    
    def simulate_mitigation_effectiveness(self, initial_compromised: List[str], 
                                       mitigation_actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Simulate the effectiveness of proposed mitigation actions."""
        
        # Run baseline simulation
        baseline_result = self.run_simulation(initial_compromised, "baseline")
        
        # Apply mitigations and run modified simulation
        modified_graph = self._apply_mitigations(mitigation_actions)
        
        # Temporarily replace graph
        original_graph = self.graph
        self.graph = modified_graph
        
        try:
            mitigated_result = self.run_simulation(initial_compromised, "mitigated")
        finally:
            # Restore original graph
            self.graph = original_graph
        
        # Calculate effectiveness
        effectiveness = {
            'baseline_impact': baseline_result.total_affected,
            'mitigated_impact': mitigated_result.total_affected,
            'impact_reduction': baseline_result.total_affected - mitigated_result.total_affected,
            'impact_reduction_percentage': ((baseline_result.total_affected - mitigated_result.total_affected) / 
                                          max(1, baseline_result.total_affected)) * 100,
            'propagation_time_reduction': baseline_result.propagation_time - mitigated_result.propagation_time,
            'baseline_result': baseline_result,
            'mitigated_result': mitigated_result
        }
        
        return effectiveness
    
    def _apply_mitigations(self, mitigation_actions: List[Dict[str, Any]]):
        """Apply mitigation actions to create a modified graph."""
        # Create a copy of the graph (simplified - in practice would deep copy)
        modified_graph = self.graph
        
        for action in mitigation_actions:
            action_type = action.get('type')
            target = action.get('target')
            
            if action_type == 'isolation':
                # Remove node from graph
                if target in modified_graph.graph.nodes():
                    modified_graph.graph.remove_node(target)
            
            elif action_type == 'hardening':
                # Reduce node vulnerability
                if target in modified_graph.graph.nodes():
                    current_risk = modified_graph.graph.nodes[target].get('risk_score', 0.0)
                    modified_graph.graph.nodes[target]['risk_score'] = current_risk * 0.3
            
            elif action_type == 'redundancy':
                # Add alternative paths (simplified)
                if isinstance(target, list):
                    for node in target:
                        if node in modified_graph.graph.nodes():
                            # Reduce criticality
                            current_criticality = modified_graph.node_features.get(node, type('obj', (object,), {'criticality_score': 50})).criticality_score
                            modified_graph.node_features[node].criticality_score = min(100, current_criticality + 20)
        
        return modified_graph
    
    def get_simulation_status(self, simulation_id: str) -> Dict[str, Any]:
        """Get the current status of a running simulation."""
        if simulation_id not in self.active_simulations:
            return {'status': 'not_found'}
        
        sim_info = self.active_simulations[simulation_id]
        
        return {
            'simulation_id': simulation_id,
            'status': sim_info['status'].value,
            'start_time': sim_info['start_time'],
            'current_step': sim_info['state']['step_number'],
            'current_time': sim_info['state']['simulation_time'],
            'compromised_count': len(sim_info['state']['compromised']),
            'affected_count': len(sim_info['state']['affected'])
        }
    
    def export_simulation_results(self, simulation_result: SimulationResult, format: str = 'json') -> str:
        """Export simulation results in various formats."""
        
        if format == 'json':
            # Convert to JSON-serializable format
            result_dict = asdict(simulation_result)
            
            # Handle enum serialization
            result_dict['status'] = result_dict['status'].value if hasattr(result_dict['status'], 'value') else str(result_dict['status'])
            
            return json.dumps(result_dict, indent=2, default=str)
        
        elif format == 'summary':
            # Generate human-readable summary
            summary = f"""
Simulation Results Summary
=========================
Simulation ID: {simulation_result.simulation_id}
Status: {simulation_result.status.value}

Initial Compromise: {len(simulation_result.initial_compromised)} nodes
Final Impact: {simulation_result.total_affected} nodes affected
Blast Radius: {simulation_result.blast_radius} additional compromises
Cascade Depth: {simulation_result.cascade_depth} propagation steps
Total Time: {simulation_result.propagation_time:.0f} milliseconds

Key Metrics:
- Compromise Rate: {simulation_result.final_metrics.get('compromise_rate', 0):.2%}
- Impact Rate: {simulation_result.final_metrics.get('impact_rate', 0):.2%}
- Critical Paths: {simulation_result.final_metrics.get('critical_path_count', 0)}

Top Mitigation Suggestions:
"""
            for i, suggestion in enumerate(simulation_result.mitigation_suggestions[:3], 1):
                summary += f"{i}. {suggestion['description']} (Priority: {suggestion['priority']})\n"
            
            return summary
        
        else:
            raise ValueError(f"Unsupported export format: {format}")


class SimulationBenchmark:
    """Benchmark and validate simulation engine performance."""
    
    def __init__(self, simulation_engine: AdvancedSimulationEngine):
        self.engine = simulation_engine
    
    def run_performance_benchmark(self, num_simulations: int = 100) -> Dict[str, Any]:
        """Run performance benchmark with multiple simulations."""
        
        results = {
            'num_simulations': num_simulations,
            'execution_times': [],
            'node_counts': [],
            'step_counts': [],
            'memory_usage': []
        }
        
        graph_nodes = list(self.engine.graph.graph.nodes())
        
        for i in range(num_simulations):
            # Random initial compromise
            num_initial = random.randint(1, min(3, len(graph_nodes)))
            initial_nodes = random.sample(graph_nodes, num_initial)
            
            start_time = time.time()
            
            try:
                result = self.engine.run_simulation(initial_nodes, f"benchmark_{i}")
                execution_time = time.time() - start_time
                
                results['execution_times'].append(execution_time)
                results['node_counts'].append(result.total_affected)
                results['step_counts'].append(result.cascade_depth)
                
            except Exception as e:
                logger.error(f"Benchmark simulation {i} failed: {e}")
        
        # Calculate statistics
        if results['execution_times']:
            results['avg_execution_time'] = np.mean(results['execution_times'])
            results['max_execution_time'] = np.max(results['execution_times'])
            results['min_execution_time'] = np.min(results['execution_times'])
            results['std_execution_time'] = np.std(results['execution_times'])
        
        return results
    
    def validate_simulation_consistency(self, initial_compromised: List[str], num_runs: int = 10) -> Dict[str, Any]:
        """Validate that simulations produce consistent results."""
        
        results = []
        
        for i in range(num_runs):
            # Set random seed for reproducibility within each run
            random.seed(42 + i)
            np.random.seed(42 + i)
            
            result = self.engine.run_simulation(initial_compromised, f"validation_{i}")
            results.append(result)
        
        # Analyze consistency
        total_affected_counts = [r.total_affected for r in results]
        cascade_depths = [r.cascade_depth for r in results]
        propagation_times = [r.propagation_time for r in results]
        
        consistency_metrics = {
            'total_affected': {
                'mean': np.mean(total_affected_counts),
                'std': np.std(total_affected_counts),
                'min': np.min(total_affected_counts),
                'max': np.max(total_affected_counts),
                'coefficient_of_variation': np.std(total_affected_counts) / max(1, np.mean(total_affected_counts))
            },
            'cascade_depth': {
                'mean': np.mean(cascade_depths),
                'std': np.std(cascade_depths),
                'min': np.min(cascade_depths),
                'max': np.max(cascade_depths)
            },
            'propagation_time': {
                'mean': np.mean(propagation_times),
                'std': np.std(propagation_times),
                'min': np.min(propagation_times),
                'max': np.max(propagation_times)
            }
        }
        
        return consistency_metrics


# Utility functions for simulation analysis
def compare_simulation_results(results: List[SimulationResult]) -> Dict[str, Any]:
    """Compare multiple simulation results and identify patterns."""
    
    if not results:
        return {}
    
    comparison = {
        'num_simulations': len(results),
        'impact_distribution': [],
        'common_patterns': [],
        'outliers': []
    }
    
    # Analyze impact distribution
    total_affected_counts = [r.total_affected for r in results]
    comparison['impact_distribution'] = {
        'mean': np.mean(total_affected_counts),
        'median': np.median(total_affected_counts),
        'std': np.std(total_affected_counts),
        'min': np.min(total_affected_counts),
        'max': np.max(total_affected_counts)
    }
    
    # Identify common compromised nodes
    all_compromised = defaultdict(int)
    for result in results:
        for node in result.final_compromised:
            all_compromised[node] += 1
    
    # Nodes compromised in >50% of simulations
    common_compromised = [
        (node, count) for node, count in all_compromised.items()
        if count > len(results) * 0.5
    ]
    comparison['common_patterns'] = sorted(common_compromised, key=lambda x: x[1], reverse=True)
    
    # Identify outliers (simulations with unusually high/low impact)
    mean_impact = np.mean(total_affected_counts)
    std_impact = np.std(total_affected_counts)
    
    for i, result in enumerate(results):
        z_score = abs(result.total_affected - mean_impact) / max(1, std_impact)
        if z_score > 2:  # More than 2 standard deviations
            comparison['outliers'].append({
                'simulation_id': result.simulation_id,
                'total_affected': result.total_affected,
                'z_score': z_score,
                'initial_compromised': result.initial_compromised
            })
    
    return comparison


def generate_simulation_report(simulation_result: SimulationResult, 
                             include_detailed_steps: bool = False) -> str:
    """Generate a comprehensive simulation report."""
    
    report = f"""
SUPPLY CHAIN COMPROMISE SIMULATION REPORT
========================================

Simulation Overview
------------------
Simulation ID: {simulation_result.simulation_id}
Status: {simulation_result.status.value}
Execution Time: {simulation_result.propagation_time:.0f} milliseconds

Initial Compromise
-----------------
Initially Compromised Nodes: {len(simulation_result.initial_compromised)}
Nodes: {', '.join(simulation_result.initial_compromised)}

Final Impact Assessment
----------------------
Total Nodes Affected: {simulation_result.total_affected}
Additional Compromises: {simulation_result.blast_radius}
Cascade Depth: {simulation_result.cascade_depth} steps

Impact Metrics
-------------
Compromise Rate: {simulation_result.final_metrics.get('compromise_rate', 0):.2%}
Network Impact Rate: {simulation_result.final_metrics.get('impact_rate', 0):.2%}
Average Propagation Time: {simulation_result.final_metrics.get('average_propagation_time', 0):.0f} ms/step
Critical Paths Identified: {simulation_result.final_metrics.get('critical_path_count', 0)}

Risk Analysis
------------
"""
    
    # Add bottleneck analysis
    bottlenecks = simulation_result.risk_analysis.get('bottleneck_nodes', [])
    if bottlenecks:
        report += "Top Bottleneck Nodes:\n"
        for node, count in bottlenecks[:5]:
            report += f"  - {node}: appeared in {count} propagation paths\n"
    
    # Add mitigation suggestions
    report += "\nMitigation Recommendations\n"
    report += "-------------------------\n"
    
    for i, suggestion in enumerate(simulation_result.mitigation_suggestions, 1):
        report += f"{i}. {suggestion['description']}\n"
        report += f"   Priority: {suggestion['priority']}\n"
        report += f"   Estimated Impact Reduction: {suggestion.get('estimated_impact_reduction', 0):.1%}\n"
        report += f"   Implementation Complexity: {suggestion.get('implementation_complexity', 'unknown')}\n\n"
    
    # Add detailed steps if requested
    if include_detailed_steps:
        report += "\nDetailed Propagation Steps\n"
        report += "-------------------------\n"
        
        for step in simulation_result.steps:
            report += f"Step {step.step_number} (t={step.timestamp:.0f}ms):\n"
            report += f"  New Compromises: {len(step.new_compromised)}\n"
            if step.new_compromised:
                report += f"  Nodes: {', '.join(step.new_compromised)}\n"
            report += f"  Propagation Paths: {len(step.propagation_paths)}\n"
            for path in step.propagation_paths:
                report += f"    {' -> '.join(path)}\n"
            report += "\n"
    
    return report