"""
Guardian AI Backend Core Module

This module contains the core components for supply chain risk analysis:
- Graph Neural Network models for structural risk learning
- Graph engine for supply chain representation and analysis
- Risk calculation and assessment algorithms
- Simulation engine for cascade failure modeling
- Data loading and processing utilities
- Mitigation strategy generation
"""

from .graph_engine import (
    SupplyChainGraph,
    NodeType,
    EdgeType,
    NodeFeatures,
    EdgeFeatures,
    PropagationPath
)

from .gnn_model import (
    SupplyChainGNN,
    GNNConfig,
    GNNTrainer,
    GNNInferenceEngine,
    GraphFeatureExtractor,
    create_default_model,
    train_model_on_synthetic_data
)

from .risk_calculator import (
    AdvancedRiskCalculator,
    RiskMetrics,
    NodeRiskProfile,
    RiskLevel,
    RiskTrendAnalyzer,
    categorize_nodes_by_risk,
    identify_risk_hotspots,
    calculate_mitigation_impact
)

from .simulation_engine import (
    AdvancedSimulationEngine,
    SimulationResult,
    SimulationStatus,
    NodeStatus,
    SimulationStep,
    PropagationRule,
    SimulationBenchmark,
    compare_simulation_results,
    generate_simulation_report
)

from .data_loader import (
    MERCORDataLoader,
    VendorData,
    DependencyData,
    DataValidator,
    create_sample_supply_chain,
    export_sample_data
)

from .mitigation_engine import (
    AdvancedMitigationEngine,
    MitigationStrategy,
    MitigationCategory,
    MitigationPriority,
    generate_mitigation_strategies
)

__version__ = "1.0.0"
__author__ = "Guardian AI Team"

# Core system components
__all__ = [
    # Graph Engine
    'SupplyChainGraph',
    'NodeType',
    'EdgeType',
    'NodeFeatures',
    'EdgeFeatures',
    'PropagationPath',
    
    # GNN Model
    'SupplyChainGNN',
    'GNNConfig',
    'GNNTrainer',
    'GNNInferenceEngine',
    'GraphFeatureExtractor',
    'create_default_model',
    'train_model_on_synthetic_data',
    
    # Risk Calculator
    'AdvancedRiskCalculator',
    'RiskMetrics',
    'NodeRiskProfile',
    'RiskLevel',
    'RiskTrendAnalyzer',
    'categorize_nodes_by_risk',
    'identify_risk_hotspots',
    'calculate_mitigation_impact',
    
    # Simulation Engine
    'AdvancedSimulationEngine',
    'SimulationResult',
    'SimulationStatus',
    'NodeStatus',
    'SimulationStep',
    'PropagationRule',
    'SimulationBenchmark',
    'compare_simulation_results',
    'generate_simulation_report',
    
    # Data Loader
    'MERCORDataLoader',
    'VendorData',
    'DependencyData',
    'DataValidator',
    'create_sample_supply_chain',
    'export_sample_data',
    
    # Mitigation Engine
    'AdvancedMitigationEngine',
    'MitigationStrategy',
    'MitigationCategory',
    'MitigationPriority',
    'generate_mitigation_strategies'
]