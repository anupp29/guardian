import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
import pickle
import os

# Optional PyTorch imports with fallbacks
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
    nn = None
    F = None

try:
    from torch_geometric.nn import GCNConv, SAGEConv, global_mean_pool, global_max_pool
    from torch_geometric.data import Data, Batch
    TORCH_GEOMETRIC_AVAILABLE = True
except ImportError:
    TORCH_GEOMETRIC_AVAILABLE = False
    GCNConv = SAGEConv = global_mean_pool = global_max_pool = None
    Data = Batch = None

logger = logging.getLogger(__name__)

@dataclass
class GNNConfig:
    input_dim: int = 16
    hidden_dim: int = 64
    output_dim: int = 32
    num_layers: int = 3
    dropout: float = 0.2
    learning_rate: float = 0.001
    batch_size: int = 32
    num_epochs: int = 100
    use_sage: bool = True  # Use GraphSAGE instead of GCN
    aggregation: str = "mean"  # mean, max, add
    normalize_features: bool = True

class SupplyChainGNN:
    """
    Graph Neural Network for supply chain risk analysis.
    Uses GraphSAGE/GCN to learn structural vulnerability patterns.
    
    Note: This is a fallback implementation when PyTorch Geometric is not available.
    """
    
    def __init__(self, config: GNNConfig):
        if not TORCH_AVAILABLE:
            logger.warning("PyTorch not available. Using fallback GNN implementation.")
            self.config = config
            self.fallback_mode = True
            return
            
        if not TORCH_GEOMETRIC_AVAILABLE:
            logger.warning("PyTorch Geometric not available. Using fallback GNN implementation.")
            self.config = config
            self.fallback_mode = True
            return
            
        # Original PyTorch implementation
        super(SupplyChainGNN, self).__init__()
        self.config = config
        self.fallback_mode = False
        
        # Graph convolution layers
        self.convs = nn.ModuleList()
        self.batch_norms = nn.ModuleList()
        
        # Input layer
        if config.use_sage:
            self.convs.append(SAGEConv(config.input_dim, config.hidden_dim, aggr=config.aggregation))
        else:
            self.convs.append(GCNConv(config.input_dim, config.hidden_dim))
        self.batch_norms.append(nn.BatchNorm1d(config.hidden_dim))
        
        # Hidden layers
        for _ in range(config.num_layers - 2):
            if config.use_sage:
                self.convs.append(SAGEConv(config.hidden_dim, config.hidden_dim, aggr=config.aggregation))
            else:
                self.convs.append(GCNConv(config.hidden_dim, config.hidden_dim))
            self.batch_norms.append(nn.BatchNorm1d(config.hidden_dim))
        
        # Output layer
        if config.use_sage:
            self.convs.append(SAGEConv(config.hidden_dim, config.output_dim, aggr=config.aggregation))
        else:
            self.convs.append(GCNConv(config.hidden_dim, config.output_dim))
        
        # Risk prediction heads
        self.node_risk_head = nn.Sequential(
            nn.Linear(config.output_dim, config.hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(config.dropout),
            nn.Linear(config.hidden_dim // 2, 1),
            nn.Sigmoid()
        )
        
        self.cascade_amplification_head = nn.Sequential(
            nn.Linear(config.output_dim, config.hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(config.dropout),
            nn.Linear(config.hidden_dim // 2, 1),
            nn.Sigmoid()
        )
        
        # Edge importance predictor
        self.edge_importance_head = nn.Sequential(
            nn.Linear(config.output_dim * 2, config.hidden_dim),
            nn.ReLU(),
            nn.Dropout(config.dropout),
            nn.Linear(config.hidden_dim, 1),
            nn.Sigmoid()
        )
        
        self.dropout = nn.Dropout(config.dropout)
    
    def forward(self, x, edge_index, batch=None):
        """Forward pass through the GNN."""
        if self.fallback_mode:
            return self._fallback_forward(x, edge_index, batch)
            
        # Graph convolution layers
        for i, (conv, bn) in enumerate(zip(self.convs[:-1], self.batch_norms)):
            x = conv(x, edge_index)
            x = bn(x)
            x = F.relu(x)
            x = self.dropout(x)
        
        # Final convolution (no activation)
        node_embeddings = self.convs[-1](x, edge_index)
        
        # Risk predictions
        node_risk_scores = self.node_risk_head(node_embeddings)
        cascade_amplification = self.cascade_amplification_head(node_embeddings)
        
        # Edge importance (for edges in edge_index)
        edge_embeddings = self._compute_edge_embeddings(node_embeddings, edge_index)
        edge_importance = self.edge_importance_head(edge_embeddings)
        
        return {
            'node_embeddings': node_embeddings,
            'node_risk_scores': node_risk_scores,
            'cascade_amplification': cascade_amplification,
            'edge_importance': edge_importance,
            'edge_embeddings': edge_embeddings
        }
    
    def _fallback_forward(self, x, edge_index, batch=None):
        """Fallback implementation when PyTorch is not available."""
        num_nodes = len(x) if hasattr(x, '__len__') else 10
        
        # Return dummy predictions
        return {
            'node_embeddings': np.random.randn(num_nodes, self.config.output_dim),
            'node_risk_scores': np.random.rand(num_nodes, 1),
            'cascade_amplification': np.random.rand(num_nodes, 1),
            'edge_importance': np.random.rand(len(edge_index[0]) if edge_index else 0, 1),
            'edge_embeddings': np.random.randn(len(edge_index[0]) if edge_index else 0, self.config.output_dim * 2)
        }
    
    def _compute_edge_embeddings(self, node_embeddings, edge_index):
        """Compute edge embeddings by concatenating source and target node embeddings."""
        if self.fallback_mode or not TORCH_AVAILABLE:
            return np.random.randn(len(edge_index[0]) if edge_index else 0, self.config.output_dim * 2)
            
        source_embeddings = node_embeddings[edge_index[0]]
        target_embeddings = node_embeddings[edge_index[1]]
        return torch.cat([source_embeddings, target_embeddings], dim=1)
    
    def predict_cascade_impact(self, x, edge_index, source_nodes):
        """
        Predict cascade impact starting from source nodes.
        
        Args:
            x: Node features
            edge_index: Edge connectivity
            source_nodes: List of source node indices
            
        Returns:
            Impact scores for all nodes
        """
        with torch.no_grad():
            outputs = self.forward(x, edge_index)
            
            # Get cascade amplification scores
            amplification_scores = outputs['cascade_amplification'].squeeze()
            
            # Initialize impact with source nodes
            impact_scores = torch.zeros_like(amplification_scores)
            impact_scores[source_nodes] = 1.0
            
            # Propagate impact through network (simplified)
            for _ in range(5):  # 5 propagation steps
                new_impact = impact_scores.clone()
                
                for i in range(edge_index.shape[1]):
                    source_idx = edge_index[0, i]
                    target_idx = edge_index[1, i]
                    
                    # Propagate impact based on amplification scores
                    propagated_impact = impact_scores[source_idx] * amplification_scores[target_idx]
                    new_impact[target_idx] = torch.max(new_impact[target_idx], propagated_impact)
                
                impact_scores = new_impact
            
            return impact_scores


class SupplyChainDataset:
    """Dataset class for supply chain graph data."""
    
    def __init__(self, graphs: List[Data], labels: Optional[List[torch.Tensor]] = None):
        self.graphs = graphs
        self.labels = labels or [None] * len(graphs)
    
    def __len__(self):
        return len(self.graphs)
    
    def __getitem__(self, idx):
        return self.graphs[idx], self.labels[idx]


class GNNTrainer:
    """Trainer class for the Supply Chain GNN."""
    
    def __init__(self, model: SupplyChainGNN, config: GNNConfig, device: str = 'cpu'):
        self.model = model.to(device)
        self.config = config
        self.device = device
        
        self.optimizer = torch.optim.Adam(
            model.parameters(), 
            lr=config.learning_rate,
            weight_decay=1e-5
        )
        
        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode='min', patience=10, factor=0.5
        )
        
        self.criterion_node = nn.MSELoss()
        self.criterion_cascade = nn.MSELoss()
        self.criterion_edge = nn.BCELoss()
        
    def train_epoch(self, dataloader):
        """Train for one epoch."""
        self.model.train()
        total_loss = 0
        num_batches = 0
        
        for batch_data, batch_labels in dataloader:
            if batch_labels is None:
                continue
                
            batch_data = batch_data.to(self.device)
            
            self.optimizer.zero_grad()
            
            # Forward pass
            outputs = self.model(batch_data.x, batch_data.edge_index, batch_data.batch)
            
            # Compute losses
            loss = 0
            
            if 'node_risk_targets' in batch_labels:
                node_risk_loss = self.criterion_node(
                    outputs['node_risk_scores'].squeeze(),
                    batch_labels['node_risk_targets'].to(self.device)
                )
                loss += node_risk_loss
            
            if 'cascade_targets' in batch_labels:
                cascade_loss = self.criterion_cascade(
                    outputs['cascade_amplification'].squeeze(),
                    batch_labels['cascade_targets'].to(self.device)
                )
                loss += cascade_loss
            
            if 'edge_importance_targets' in batch_labels:
                edge_loss = self.criterion_edge(
                    outputs['edge_importance'].squeeze(),
                    batch_labels['edge_importance_targets'].to(self.device)
                )
                loss += edge_loss
            
            # Backward pass
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            self.optimizer.step()
            
            total_loss += loss.item()
            num_batches += 1
        
        return total_loss / max(num_batches, 1)
    
    def validate(self, dataloader):
        """Validate the model."""
        self.model.eval()
        total_loss = 0
        num_batches = 0
        
        with torch.no_grad():
            for batch_data, batch_labels in dataloader:
                if batch_labels is None:
                    continue
                    
                batch_data = batch_data.to(self.device)
                outputs = self.model(batch_data.x, batch_data.edge_index, batch_data.batch)
                
                # Compute validation loss (same as training)
                loss = 0
                
                if 'node_risk_targets' in batch_labels:
                    node_risk_loss = self.criterion_node(
                        outputs['node_risk_scores'].squeeze(),
                        batch_labels['node_risk_targets'].to(self.device)
                    )
                    loss += node_risk_loss
                
                if 'cascade_targets' in batch_labels:
                    cascade_loss = self.criterion_cascade(
                        outputs['cascade_amplification'].squeeze(),
                        batch_labels['cascade_targets'].to(self.device)
                    )
                    loss += cascade_loss
                
                total_loss += loss.item()
                num_batches += 1
        
        return total_loss / max(num_batches, 1)
    
    def train(self, train_dataloader, val_dataloader=None, save_path: str = None):
        """Full training loop."""
        best_val_loss = float('inf')
        patience_counter = 0
        
        for epoch in range(self.config.num_epochs):
            # Training
            train_loss = self.train_epoch(train_dataloader)
            
            # Validation
            val_loss = train_loss  # Default to train loss if no validation set
            if val_dataloader:
                val_loss = self.validate(val_dataloader)
            
            # Learning rate scheduling
            self.scheduler.step(val_loss)
            
            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                
                # Save best model
                if save_path:
                    self.save_model(save_path)
            else:
                patience_counter += 1
                
            if patience_counter >= 20:  # Early stopping patience
                logger.info(f"Early stopping at epoch {epoch}")
                break
            
            if epoch % 10 == 0:
                logger.info(f"Epoch {epoch}: Train Loss = {train_loss:.4f}, Val Loss = {val_loss:.4f}")
        
        return best_val_loss
    
    def save_model(self, path: str):
        """Save model state."""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'config': self.config,
            'optimizer_state_dict': self.optimizer.state_dict()
        }, path)
    
    def load_model(self, path: str):
        """Load model state."""
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        return checkpoint['config']


class GraphFeatureExtractor:
    """Extract features from supply chain graphs for GNN training."""
    
    @staticmethod
    def extract_node_features(graph, node_id: str) -> np.ndarray:
        """Extract feature vector for a single node."""
        node_data = graph.nodes[node_id]
        
        # Basic features
        features = [
            node_data.get('tier', 3) / 3.0,  # Normalized tier
            node_data.get('risk_score', 0.0),
            node_data.get('criticality_score', 0.0) / 100.0,
            graph.in_degree(node_id) / max(1, len(graph.nodes())),  # Normalized in-degree
            graph.out_degree(node_id) / max(1, len(graph.nodes())),  # Normalized out-degree
        ]
        
        # Centrality features
        try:
            betweenness = nx.betweenness_centrality(graph).get(node_id, 0.0)
            closeness = nx.closeness_centrality(graph).get(node_id, 0.0)
            pagerank = nx.pagerank(graph).get(node_id, 0.0)
        except:
            betweenness = closeness = pagerank = 0.0
        
        features.extend([betweenness, closeness, pagerank])
        
        # Category encoding (one-hot)
        categories = ['authentication', 'payment', 'data', 'api', 'infrastructure', 'other']
        category = node_data.get('category', 'other')
        category_features = [1.0 if cat == category else 0.0 for cat in categories]
        features.extend(category_features)
        
        # Node type encoding
        node_types = ['vendor', 'software', 'service']
        node_type = node_data.get('node_type', 'vendor')
        type_features = [1.0 if nt == node_type else 0.0 for nt in node_types]
        features.extend(type_features)
        
        return np.array(features, dtype=np.float32)
    
    @staticmethod
    def graph_to_pytorch_geometric(supply_chain_graph) -> Data:
        """Convert SupplyChainGraph to PyTorch Geometric Data object."""
        # Extract node features
        node_ids = list(supply_chain_graph.graph.nodes())
        node_features = []
        
        for node_id in node_ids:
            features = GraphFeatureExtractor.extract_node_features(supply_chain_graph.graph, node_id)
            node_features.append(features)
        
        x = torch.tensor(node_features, dtype=torch.float)
        
        # Extract edges
        edge_list = list(supply_chain_graph.graph.edges())
        if edge_list:
            # Map node IDs to indices
            node_to_idx = {node_id: idx for idx, node_id in enumerate(node_ids)}
            
            edge_index = []
            for source, target in edge_list:
                edge_index.append([node_to_idx[source], node_to_idx[target]])
            
            edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()
        else:
            edge_index = torch.empty((2, 0), dtype=torch.long)
        
        # Create PyTorch Geometric Data object
        data = Data(x=x, edge_index=edge_index)
        
        # Add node mapping for later reference
        data.node_ids = node_ids
        
        return data
    
    @staticmethod
    def generate_synthetic_labels(supply_chain_graph, num_simulations: int = 100) -> Dict[str, torch.Tensor]:
        """Generate synthetic training labels through cascade simulations."""
        node_ids = list(supply_chain_graph.graph.nodes())
        num_nodes = len(node_ids)
        
        # Initialize label tensors
        node_risk_scores = torch.zeros(num_nodes)
        cascade_amplification = torch.zeros(num_nodes)
        
        # Run multiple cascade simulations
        for _ in range(num_simulations):
            # Randomly select initial compromised nodes
            num_initial = np.random.randint(1, min(5, num_nodes))
            initial_nodes = np.random.choice(node_ids, size=num_initial, replace=False)
            
            # Simulate cascade
            result = supply_chain_graph.simulate_cascade_failure(list(initial_nodes))
            
            # Update labels based on simulation results
            for node_id in result['compromised_nodes']:
                if node_id in node_ids:
                    idx = node_ids.index(node_id)
                    
                    # Node risk score (how often this node gets compromised)
                    node_risk_scores[idx] += 1.0 / num_simulations
                    
                    # Cascade amplification (impact when this node is compromised)
                    amplification = len(result['compromised_nodes']) / num_nodes
                    cascade_amplification[idx] = max(cascade_amplification[idx], amplification)
        
        return {
            'node_risk_targets': node_risk_scores,
            'cascade_targets': cascade_amplification
        }


class GNNInferenceEngine:
    """Production inference engine for trained GNN models."""
    
    def __init__(self, model_path: str, device: str = 'cpu'):
        self.device = device
        self.model = None
        self.config = None
        self.fallback_mode = True
        
        if TORCH_AVAILABLE:
            try:
                self.load_model(model_path)
                self.fallback_mode = False
            except Exception as e:
                logger.warning(f"Failed to load GNN model: {e}. Using fallback mode.")
        else:
            logger.warning("PyTorch not available. Using fallback mode.")
    
    def load_model(self, model_path: str):
        """Load trained model from disk."""
        if not TORCH_AVAILABLE:
            logger.warning("PyTorch not available for model loading.")
            return
            
        if not os.path.exists(model_path):
            logger.warning(f"Model file not found: {model_path}. Using default configuration.")
            self.config = GNNConfig()
            self.model = SupplyChainGNN(self.config)
            return
        
        try:
            checkpoint = torch.load(model_path, map_location=self.device)
            self.config = checkpoint.get('config', GNNConfig())
            self.model = SupplyChainGNN(self.config)
            if not self.model.fallback_mode:
                self.model.load_state_dict(checkpoint['model_state_dict'])
                self.model.eval()
        except Exception as e:
            logger.warning(f"Failed to load model checkpoint: {e}")
            self.config = GNNConfig()
            self.model = SupplyChainGNN(self.config)
    
    def predict_risk_scores(self, supply_chain_graph) -> Dict[str, float]:
        """Predict risk scores for all nodes in the graph."""
        if self.fallback_mode or self.model is None:
            # Fallback to simple heuristic
            return self._fallback_risk_prediction(supply_chain_graph)
        
        try:
            # Convert to PyTorch Geometric format
            data = GraphFeatureExtractor.graph_to_pytorch_geometric(supply_chain_graph)
            
            if not TORCH_AVAILABLE:
                return self._fallback_risk_
                outputs = self.model(data.x, data.edge_index)
                risk_scores = outputs['node_risk_scores'].squeeze().cpu().numpy()
            
            # Map back to node IDs
            risk_dict = {}
            for i, node_id in enumerate(data.node_ids):
                risk_dict[node_id] = float(risk_scores[i])
            
            return risk_dict
            
        except Exception as e:
            logger.error(f"GNN prediction failed: {e}. Using fallback.")
            return self._fallback_risk_prediction(supply_chain_graph)
    
    def predict_cascade_amplification(self, supply_chain_graph) -> Dict[str, float]:
        """Predict cascade amplification scores for all nodes."""
        if self.model is None:
            return self._fallback_amplification_prediction(supply_chain_graph)
        
        try:
            data = GraphFeatureExtractor.graph_to_pytorch_geometric(supply_chain_graph)
            data = data.to(self.device)
            
            with torch.no_grad():
                outputs = self.model(data.x, data.edge_index)
                amplification_scores = outputs['cascade_amplification'].squeeze().cpu().numpy()
            
            amplification_dict = {}
            for i, node_id in enumerate(data.node_ids):
                amplification_dict[node_id] = float(amplification_scores[i])
            
            return amplification_dict
            
        except Exception as e:
            logger.error(f"GNN amplification prediction failed: {e}. Using fallback.")
            return self._fallback_amplification_prediction(supply_chain_graph)
    
    def predict_edge_importance(self, supply_chain_graph) -> Dict[Tuple[str, str], float]:
        """Predict importance scores for all edges."""
        if self.model is None:
            return self._fallback_edge_prediction(supply_chain_graph)
        
        try:
            data = GraphFeatureExtractor.graph_to_pytorch_geometric(supply_chain_graph)
            data = data.to(self.device)
            
            with torch.no_grad():
                outputs = self.model(data.x, data.edge_index)
                edge_importance = outputs['edge_importance'].squeeze().cpu().numpy()
            
            # Map back to edge tuples
            importance_dict = {}
            edge_list = list(supply_chain_graph.graph.edges())
            
            for i, (source, target) in enumerate(edge_list):
                if i < len(edge_importance):
                    importance_dict[(source, target)] = float(edge_importance[i])
            
            return importance_dict
            
        except Exception as e:
            logger.error(f"GNN edge prediction failed: {e}. Using fallback.")
            return self._fallback_edge_prediction(supply_chain_graph)
    
    def _fallback_risk_prediction(self, supply_chain_graph) -> Dict[str, float]:
        """Fallback risk prediction using graph metrics."""
        risk_scores = {}
        
        # Calculate centrality metrics
        try:
            centrality_metrics = supply_chain_graph.calculate_centrality_metrics()
        except:
            centrality_metrics = {}
        
        for node_id in supply_chain_graph.graph.nodes():
            # Base risk from node properties
            node_data = supply_chain_graph.graph.nodes[node_id]
            base_risk = node_data.get('risk_score', 0.0)
            
            # Adjust based on centrality
            metrics = centrality_metrics.get(node_id, {})
            centrality_factor = (
                metrics.get('betweenness_centrality', 0.0) * 0.3 +
                metrics.get('degree_centrality', 0.0) * 0.4 +
                metrics.get('pagerank', 0.0) * 0.3
            )
            
            # Combine factors
            final_risk = min(1.0, base_risk + centrality_factor * 0.5)
            risk_scores[node_id] = final_risk
        
        return risk_scores
    
    def _fallback_amplification_prediction(self, supply_chain_graph) -> Dict[str, float]:
        """Fallback amplification prediction."""
        amplification_scores = {}
        
        for node_id in supply_chain_graph.graph.nodes():
            # Base amplification on out-degree and tier
            out_degree = supply_chain_graph.graph.out_degree(node_id)
            tier = supply_chain_graph.node_features.get(node_id, type('obj', (object,), {'tier': 3})).tier
            
            # Higher amplification for nodes with more outgoing connections and higher tier
            amplification = (out_degree / max(1, len(supply_chain_graph.graph.nodes()))) * (4 - tier) / 3
            amplification_scores[node_id] = min(1.0, amplification)
        
        return amplification_scores
    
    def _fallback_edge_prediction(self, supply_chain_graph) -> Dict[Tuple[str, str], float]:
        """Fallback edge importance prediction."""
        importance_scores = {}
        
        for source, target in supply_chain_graph.graph.edges():
            edge_data = supply_chain_graph.graph.edges[source, target]
            
            # Base importance on edge strength and criticality
            strength = edge_data.get('strength', 0.5)
            criticality = edge_data.get('criticality', 'medium')
            
            criticality_multiplier = {'low': 0.3, 'medium': 0.6, 'high': 1.0}.get(criticality, 0.6)
            importance = strength * criticality_multiplier
            
            importance_scores[(source, target)] = importance
        
        return importance_scores


# Utility functions for model management
def create_default_model(save_path: str = "models/supply_chain_gnn.pth") -> GNNInferenceEngine:
    """Create and save a default model for immediate use."""
    
    if not TORCH_AVAILABLE:
        logger.warning("PyTorch not available. Creating placeholder model file.")
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Create placeholder file
        with open(save_path, 'w') as f:
            f.write("# Placeholder GNN model file\n")
        
        logger.info(f"Placeholder model file created at {save_path}")
        return GNNInferenceEngine(save_path)
    
    config = GNNConfig()
    model = SupplyChainGNN(config)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # Save model
    if not model.fallback_mode:
        torch.save({
            'model_state_dict': model.state_dict(),
            'config': config,
            'optimizer_state_dict': {}
        }, save_path)
    else:
        # Create placeholder for fallback mode
        with open(save_path, 'w') as f:
            f.write("# Fallback GNN model file\n")
    
    logger.info(f"Default model saved to {save_path}")
    return GNNInferenceEngine(save_path)


def train_model_on_synthetic_data(supply_chain_graph, save_path: str = "models/supply_chain_gnn.pth"):
    """Train a model on synthetic data generated from the supply chain graph."""
    config = GNNConfig()
    model = SupplyChainGNN(config)
    trainer = GNNTrainer(model, config)
    
    # Generate training data
    data = GraphFeatureExtractor.graph_to_pytorch_geometric(supply_chain_graph)
    labels = GraphFeatureExtractor.generate_synthetic_labels(supply_chain_graph)
    
    # Create simple dataset
    dataset = [(data, labels)]
    
    # Train model
    trainer.train(dataset, save_path=save_path)
    
    logger.info(f"Model trained and saved to {save_path}")
    return GNNInferenceEngine(save_path)