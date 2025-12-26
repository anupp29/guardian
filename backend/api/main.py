from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import asyncio
import uuid
from datetime import datetime

# Import core Guardian AI components
from backend.core import (
    create_sample_supply_chain,
    AdvancedRiskCalculator,
    AdvancedSimulationEngine,
    AdvancedMitigationEngine,
    GNNInferenceEngine,
    export_sample_data
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Guardian AI API",
    description="Supply Chain Risk Intelligence Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state (in production, use proper state management)
class AppState:
    def __init__(self):
        self.supply_chain_graph = None
        self.risk_calculator = None
        self.simulation_engine = None
        self.mitigation_engine = None
        self.gnn_engine = None
        self.active_simulations = {}
        
    def initialize(self):
        """Initialize the core components."""
        logger.info("Initializing Guardian AI components...")
        
        # Create sample supply chain
        self.supply_chain_graph = create_sample_supply_chain(50)
        
        # Initialize engines
        self.risk_calculator = AdvancedRiskCalculator()
        self.simulation_engine = AdvancedSimulationEngine(
            self.supply_chain_graph,
            risk_calculator=self.risk_calculator
        )
        self.mitigation_engine = AdvancedMitigationEngine(
            self.supply_chain_graph,
            risk_calculator=self.risk_calculator
        )
        
        # Initialize GNN (with fallback)
        try:
            self.gnn_engine = GNNInferenceEngine("models/supply_chain_gnn.pth")
        except Exception as e:
            logger.warning(f"GNN initialization failed: {e}. Using fallback.")
            self.gnn_engine = None
        
        logger.info("Guardian AI initialization complete")

# Global app state
state = AppState()

# Pydantic models for API
class SimulationRequest(BaseModel):
    initial_compromised: List[str]
    simulation_id: Optional[str] = None

class RiskAssessmentResponse(BaseModel):
    overall_score: float
    tier_1_exposure: float
    cascade_potential: float
    single_point_failures: int
    critical_path_count: int
    vulnerability_density: float
    resilience_score: float

class NodeRiskResponse(BaseModel):
    node_id: str
    combined_risk: float
    risk_level: str
    contributing_factors: List[str]

class SimulationResponse(BaseModel):
    simulation_id: str
    status: str
    total_affected: int
    blast_radius: int
    cascade_depth: int
    propagation_time: float
    final_metrics: Dict[str, Any]
    mitigation_suggestions: List[Dict[str, Any]]

# API Endpoints

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    state.initialize()

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Guardian AI API",
        "version": "1.0.0",
        "description": "Supply Chain Risk Intelligence Platform",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "components": {
            "supply_chain_graph": state.supply_chain_graph is not None,
            "risk_calculator": state.risk_calculator is not None,
            "simulation_engine": state.simulation_engine is not None,
            "mitigation_engine": state.mitigation_engine is not None,
            "gnn_engine": state.gnn_engine is not None
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/graph/export")
async def export_graph():
    """Export supply chain graph in Cytoscape format."""
    try:
        if not state.supply_chain_graph:
            raise HTTPException(status_code=500, detail="Supply chain graph not initialized")
        
        cytoscape_data = state.supply_chain_graph.export_cytoscape_format()
        
        return JSONResponse(content={
            "success": True,
            "data": cytoscape_data,
            "metadata": {
                "node_count": len(state.supply_chain_graph.graph.nodes()),
                "edge_count": len(state.supply_chain_graph.graph.edges()),
                "exported_at": datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Graph export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/graph/statistics")
async def get_graph_statistics():
    """Get comprehensive graph statistics."""
    try:
        if not state.supply_chain_graph:
            raise HTTPException(status_code=500, detail="Supply chain graph not initialized")
        
        stats = state.supply_chain_graph.get_statistics()
        
        return JSONResponse(content={
            "success": True,
            "data": stats,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Statistics calculation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/risk/assessment")
async def get_risk_assessment():
    """Get comprehensive risk assessment."""
    try:
        if not state.risk_calculator or not state.supply_chain_graph:
            raise HTTPException(status_code=500, detail="Risk calculator not initialized")
        
        # Get GNN predictions if available
        gnn_predictions = None
        if state.gnn_engine:
            try:
                gnn_predictions = {
                    'node_risk_scores': state.gnn_engine.predict_risk_scores(state.supply_chain_graph),
                    'cascade_amplification': state.gnn_engine.predict_cascade_amplification(state.supply_chain_graph)
                }
            except Exception as e:
                logger.warning(f"GNN prediction failed: {e}")
        
        # Calculate risk metrics
        risk_metrics = state.risk_calculator.calculate_comprehensive_risk(
            state.supply_chain_graph, 
            gnn_predictions
        )
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "overall_score": risk_metrics.overall_score,
                "tier_1_exposure": risk_metrics.tier_1_exposure,
                "cascade_potential": risk_metrics.cascade_potential,
                "single_point_failures": risk_metrics.single_point_failures,
                "critical_path_count": risk_metrics.critical_path_count,
                "vulnerability_density": risk_metrics.vulnerability_density,
                "resilience_score": risk_metrics.resilience_score
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Risk assessment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/risk/nodes")
async def get_node_risks():
    """Get risk profiles for all nodes."""
    try:
        if not state.risk_calculator or not state.supply_chain_graph:
            raise HTTPException(status_code=500, detail="Risk calculator not initialized")
        
        # Get GNN predictions if available
        gnn_predictions = None
        if state.gnn_engine:
            try:
                gnn_predictions = {
                    'node_risk_scores': state.gnn_engine.predict_risk_scores(state.supply_chain_graph),
                    'cascade_amplification': state.gnn_engine.predict_cascade_amplification(state.supply_chain_graph)
                }
            except Exception as e:
                logger.warning(f"GNN prediction failed: {e}")
        
        # Calculate node risk profiles
        node_risks = state.risk_calculator.calculate_node_risk_profiles(
            state.supply_chain_graph,
            gnn_predictions
        )
        
        # Convert to API format
        risk_data = []
        for node_id, risk_profile in node_risks.items():
            risk_data.append({
                "node_id": node_id,
                "combined_risk": risk_profile.combined_risk,
                "risk_level": risk_profile.risk_level.value,
                "contributing_factors": risk_profile.contributing_factors,
                "base_risk": risk_profile.base_risk,
                "structural_risk": risk_profile.structural_risk,
                "cascade_amplification": risk_profile.cascade_amplification,
                "centrality_risk": risk_profile.centrality_risk
            })
        
        return JSONResponse(content={
            "success": True,
            "data": risk_data,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Node risk calculation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/simulation/run")
async def run_simulation(request: SimulationRequest, background_tasks: BackgroundTasks):
    """Run supply chain compromise simulation."""
    try:
        if not state.simulation_engine:
            raise HTTPException(status_code=500, detail="Simulation engine not initialized")
        
        # Validate initial compromised nodes
        graph_nodes = set(state.supply_chain_graph.graph.nodes())
        invalid_nodes = [node for node in request.initial_compromised if node not in graph_nodes]
        
        if invalid_nodes:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid node IDs: {invalid_nodes}"
            )
        
        # Generate simulation ID if not provided
        simulation_id = request.simulation_id or f"sim_{uuid.uuid4().hex[:8]}"
        
        # Run simulation
        result = state.simulation_engine.run_simulation(
            request.initial_compromised,
            simulation_id
        )
        
        # Store result
        state.active_simulations[simulation_id] = result
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "simulation_id": result.simulation_id,
                "status": result.status.value,
                "total_affected": result.total_affected,
                "blast_radius": result.blast_radius,
                "cascade_depth": result.cascade_depth,
                "propagation_time": result.propagation_time,
                "final_metrics": result.final_metrics,
                "mitigation_suggestions": result.mitigation_suggestions,
                "initial_compromised": result.initial_compromised,
                "final_compromised": result.final_compromised
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/simulation/{simulation_id}")
async def get_simulation_result(simulation_id: str):
    """Get simulation result by ID."""
    try:
        if simulation_id not in state.active_simulations:
            raise HTTPException(status_code=404, detail="Simulation not found")
        
        result = state.active_simulations[simulation_id]
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "simulation_id": result.simulation_id,
                "status": result.status.value,
                "total_affected": result.total_affected,
                "blast_radius": result.blast_radius,
                "cascade_depth": result.cascade_depth,
                "propagation_time": result.propagation_time,
                "final_metrics": result.final_metrics,
                "mitigation_suggestions": result.mitigation_suggestions,
                "initial_compromised": result.initial_compromised,
                "final_compromised": result.final_compromised
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Simulation retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mitigation/strategies")
async def get_mitigation_strategies():
    """Get mitigation strategies."""
    try:
        if not state.mitigation_engine:
            raise HTTPException(status_code=500, detail="Mitigation engine not initialized")
        
        strategies = state.mitigation_engine.generate_mitigation_strategies(8)
        
        return JSONResponse(content={
            "success": True,
            "data": strategies,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Mitigation strategy generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/metrics")
async def get_dashboard_metrics():
    """Get dashboard metrics."""
    try:
        if not state.supply_chain_graph or not state.risk_calculator:
            raise HTTPException(status_code=500, detail="Components not initialized")
        
        # Get basic statistics
        stats = state.supply_chain_graph.get_statistics()
        
        # Get risk assessment
        risk_metrics = state.risk_calculator.calculate_comprehensive_risk(state.supply_chain_graph)
        
        # Calculate tier distribution
        tier_distribution = {}
        for node_id in state.supply_chain_graph.graph.nodes():
            tier = state.supply_chain_graph.node_features.get(node_id, type('obj', (object,), {'tier': 3})).tier
            tier_distribution[f"tier_{tier}"] = tier_distribution.get(f"tier_{tier}", 0) + 1
        
        # Calculate category distribution
        category_distribution = {}
        for node_id in state.supply_chain_graph.graph.nodes():
            category = state.supply_chain_graph.graph.nodes[node_id].get('category', 'unknown')
            category_distribution[category] = category_distribution.get(category, 0) + 1
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "current": {
                    "totalVendors": stats['node_count'],
                    "criticalVendors": tier_distribution.get('tier_1', 0),
                    "highRiskVendors": len([n for n in state.supply_chain_graph.graph.nodes() 
                                         if state.supply_chain_graph.graph.nodes[n].get('risk_score', 0) > 0.6]),
                    "overallRiskScore": int(risk_metrics.overall_score * 100),
                    "lastUpdated": datetime.now().isoformat()
                },
                "trends": {
                    "riskScoreChange": -5,
                    "newVendorsAdded": 2,
                    "vendorsRemoved": 1,
                    "periodDays": 30
                },
                "distribution": {
                    "byTier": tier_distribution,
                    "byCategory": category_distribution,
                    "byRiskLevel": {
                        "low": len([n for n in state.supply_chain_graph.graph.nodes() 
                                  if state.supply_chain_graph.graph.nodes[n].get('risk_score', 0) <= 0.3]),
                        "medium": len([n for n in state.supply_chain_graph.graph.nodes() 
                                     if 0.3 < state.supply_chain_graph.graph.nodes[n].get('risk_score', 0) <= 0.6]),
                        "high": len([n for n in state.supply_chain_graph.graph.nodes() 
                                   if 0.6 < state.supply_chain_graph.graph.nodes[n].get('risk_score', 0) <= 0.8]),
                        "critical": len([n for n in state.supply_chain_graph.graph.nodes() 
                                       if state.supply_chain_graph.graph.nodes[n].get('risk_score', 0) > 0.8])
                    }
                }
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Dashboard metrics calculation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/activity/feed")
async def get_activity_feed():
    """Get activity feed events."""
    try:
        # Generate sample activity feed
        activities = [
            {
                "id": "evt_001",
                "type": "simulation_run",
                "title": "Simulation: Okta Compromise",
                "severity": "critical",
                "timestamp": datetime.now().isoformat(),
                "details": "42 vendors affected, 7 critical paths identified",
                "actor": "System",
                "icon": "alert-triangle"
            },
            {
                "id": "evt_002",
                "type": "vendor_added",
                "title": "New Vendor: Stripe Payment Gateway",
                "severity": "info",
                "timestamp": datetime.now().isoformat(),
                "details": "Added to payment processing tier 1",
                "actor": "Admin User",
                "icon": "plus-circle"
            },
            {
                "id": "evt_003",
                "type": "risk_assessment",
                "title": "Risk Assessment Completed",
                "severity": "success",
                "timestamp": datetime.now().isoformat(),
                "details": "Overall risk decreased by 12%",
                "actor": "System",
                "icon": "check-circle"
            }
        ]
        
        return JSONResponse(content={
            "success": True,
            "data": activities,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Activity feed generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "timestamp": datetime.now().isoformat()
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": 500,
                "message": "Internal server error",
                "timestamp": datetime.now().isoformat()
            }
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)