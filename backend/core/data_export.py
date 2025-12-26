"""
Guardian AI Data Export Module

Utilities for exporting supply chain data in various formats for analysis and visualization.
"""

import json
import csv
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
from datetime import datetime

from .graph_engine import SupplyChainGraph

logger = logging.getLogger(__name__)

class DataExporter:
    """Export supply chain data in multiple formats."""
    
    def __init__(self, supply_chain_graph: SupplyChainGraph):
        self.graph = supply_chain_graph
    
    def export_to_json(self, output_path: str, include_metadata: bool = True) -> Dict[str, Any]:
        """Export supply chain data to JSON format."""
        
        export_data = {
            'nodes': [],
            'edges': [],
            'statistics': self.graph.get_statistics() if include_metadata else None,
            'exported_at': datetime.now().isoformat()
        }
        
        # Export nodes
        for node_id in self.graph.graph.nodes():
            node_data = self.graph.graph.nodes[node_id]
            node_features = self.graph.node_features.get(node_id)
            
            node_export = {
                'id': node_id,
                'type': node_data.get('node_type', 'vendor'),
                'name': node_data.get('name', node_id),
                'tier': node_features.tier if node_features else 3,
                'risk_score': node_features.risk_score if node_features else 0.0,
                'criticality_score': node_features.criticality_score if node_features else 50,
                'category': node_data.get('category', 'unknown'),
                'status': node_data.get('status', 'secure'),
                'metadata': node_features.metadata if node_features else {}
            }
            
            export_data['nodes'].append(node_export)
        
        # Export edges
        for source, target in self.graph.graph.edges():
            edge_data = self.graph.graph.edges[source, target]
            edge_features = self.graph.edge_features.get((source, target))
            
            edge_export = {
                'source': source,
                'target': target,
                'type': edge_data.get('edge_type', 'depends_on'),
                'category': edge_data.get('dependency_category', 'unknown'),
                'strength': edge_features.strength if edge_features else 0.5,
                'criticality': edge_features.criticality if edge_features else 'medium',
                'metadata': edge_features.metadata if edge_features else {}
            }
            
            export_data['edges'].append(edge_export)
        
        # Save to file
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        logger.info(f"Exported supply chain data to {output_path}")
        return export_data
    
    def export_to_csv(self, nodes_path: str, edges_path: str) -> None:
        """Export supply chain data to CSV files."""
        
        # Export nodes
        nodes_data = []
        for node_id in self.graph.graph.nodes():
            node_data = self.graph.graph.nodes[node_id]
            node_features = self.graph.node_features.get(node_id)
            
            nodes_data.append({
                'id': node_id,
                'name': node_data.get('name', node_id),
                'type': node_data.get('node_type', 'vendor'),
                'tier': node_features.tier if node_features else 3,
                'risk_score': node_features.risk_score if node_features else 0.0,
                'criticality_score': node_features.criticality_score if node_features else 50,
                'category': node_data.get('category', 'unknown'),
                'status': node_data.get('status', 'secure'),
                'contract_type': node_data.get('contractType', 'unknown'),
                'last_audit': node_data.get('lastAudit', ''),
                'certifications': json.dumps(node_data.get('certifications', [])),
                'employee_access': node_data.get('employeeAccess', 0),
                'data_categories': json.dumps(node_data.get('dataCategories', []))
            })
        
        nodes_df = pd.DataFrame(nodes_data)
        nodes_df.to_csv(nodes_path, index=False)
        
        # Export edges
        edges_data = []
        for source, target in self.graph.graph.edges():
            edge_data = self.graph.graph.edges[source, target]
            edge_features = self.graph.edge_features.get((source, target))
            
            edges_data.append({
                'source': source,
                'target': target,
                'type': edge_data.get('edge_type', 'depends_on'),
                'category': edge_data.get('dependency_category', 'unknown'),
                'strength': edge_features.strength if edge_features else 0.5,
                'criticality': edge_features.criticality if edge_features else 'medium',
                'last_verified': edge_data.get('lastVerified', ''),
                'data_volume': edge_data.get('dataVolume', 'medium')
            })
        
        edges_df = pd.DataFrame(edges_data)
        edges_df.to_csv(edges_path, index=False)
        
        logger.info(f"Exported nodes to {nodes_path} and edges to {edges_path}")
    
    def export_to_cytoscape(self, output_path: str) -> Dict[str, Any]:
        """Export data in Cytoscape.js format."""
        
        cytoscape_data = self.graph.export_cytoscape_format()
        
        with open(output_path, 'w') as f:
            json.dump(cytoscape_data, f, indent=2)
        
        logger.info(f"Exported Cytoscape data to {output_path}")
        return cytoscape_data
    
    def export_risk_analysis(self, output_path: str, risk_calculator=None) -> Dict[str, Any]:
        """Export comprehensive risk analysis."""
        
        analysis_data = {
            'timestamp': datetime.now().isoformat(),
            'graph_statistics': self.graph.get_statistics(),
            'structural_vulnerabilities': self.graph.identify_structural_vulnerabilities(),
            'centrality_metrics': self.graph.calculate_centrality_metrics(),
            'risk_assessment': None
        }
        
        # Add risk assessment if calculator provided
        if risk_calculator:
            try:
                risk_metrics = risk_calculator.calculate_comprehensive_risk(self.graph)
                node_risks = risk_calculator.calculate_node_risk_profiles(self.graph)
                
                analysis_data['risk_assessment'] = {
                    'overall_metrics': {
                        'overall_score': risk_metrics.overall_score,
                        'tier_1_exposure': risk_metrics.tier_1_exposure,
                        'cascade_potential': risk_metrics.cascade_potential,
                        'single_point_failures': risk_metrics.single_point_failures,
                        'critical_path_count': risk_metrics.critical_path_count,
                        'vulnerability_density': risk_metrics.vulnerability_density,
                        'resilience_score': risk_metrics.resilience_score
                    },
                    'node_risks': {
                        node_id: {
                            'combined_risk': profile.combined_risk,
                            'risk_level': profile.risk_level.value,
                            'base_risk': profile.base_risk,
                            'structural_risk': profile.structural_risk,
                            'cascade_amplification': profile.cascade_amplification,
                            'centrality_risk': profile.centrality_risk,
                            'contributing_factors': profile.contributing_factors
                        }
                        for node_id, profile in node_risks.items()
                    }
                }
            except Exception as e:
                logger.error(f"Risk assessment failed: {e}")
                analysis_data['risk_assessment'] = {'error': str(e)}
        
        # Save to file
        with open(output_path, 'w') as f:
            json.dump(analysis_data, f, indent=2, default=str)
        
        logger.info(f"Exported risk analysis to {output_path}")
        return analysis_data
    
    def export_simulation_ready_format(self, output_path: str) -> Dict[str, Any]:
        """Export data in format optimized for simulation engines."""
        
        simulation_data = {
            'metadata': {
                'node_count': len(self.graph.graph.nodes()),
                'edge_count': len(self.graph.graph.edges()),
                'exported_at': datetime.now().isoformat()
            },
            'nodes': {},
            'adjacency_list': {},
            'tier_mapping': {},
            'category_mapping': {}
        }
        
        # Build optimized node data
        for node_id in self.graph.graph.nodes():
            node_data = self.graph.graph.nodes[node_id]
            node_features = self.graph.node_features.get(node_id)
            
            simulation_data['nodes'][node_id] = {
                'tier': node_features.tier if node_features else 3,
                'risk_score': node_features.risk_score if node_features else 0.0,
                'criticality_score': node_features.criticality_score if node_features else 50,
                'category': node_data.get('category', 'unknown'),
                'status': node_data.get('status', 'secure')
            }
            
            # Build tier mapping
            tier = node_features.tier if node_features else 3
            if tier not in simulation_data['tier_mapping']:
                simulation_data['tier_mapping'][tier] = []
            simulation_data['tier_mapping'][tier].append(node_id)
            
            # Build category mapping
            category = node_data.get('category', 'unknown')
            if category not in simulation_data['category_mapping']:
                simulation_data['category_mapping'][category] = []
            simulation_data['category_mapping'][category].append(node_id)
        
        # Build adjacency list
        for node_id in self.graph.graph.nodes():
            successors = list(self.graph.graph.successors(node_id))
            simulation_data['adjacency_list'][node_id] = []
            
            for successor in successors:
                edge_features = self.graph.edge_features.get((node_id, successor))
                simulation_data['adjacency_list'][node_id].append({
                    'target': successor,
                    'strength': edge_features.strength if edge_features else 0.5,
                    'criticality': edge_features.criticality if edge_features else 'medium'
                })
        
        # Save to file
        with open(output_path, 'w') as f:
            json.dump(simulation_data, f, indent=2)
        
        logger.info(f"Exported simulation-ready data to {output_path}")
        return simulation_data


class ReportGenerator:
    """Generate comprehensive reports from supply chain data."""
    
    def __init__(self, supply_chain_graph: SupplyChainGraph):
        self.graph = supply_chain_graph
    
    def generate_executive_summary(self, risk_calculator=None) -> str:
        """Generate executive summary report."""
        
        stats = self.graph.get_statistics()
        vulnerabilities = self.graph.identify_structural_vulnerabilities()
        
        report = f"""
GUARDIAN AI SUPPLY CHAIN RISK ASSESSMENT
Executive Summary Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

NETWORK OVERVIEW
================
Total Vendors: {stats['node_count']}
Dependencies: {stats['edge_count']}
Network Density: {stats['density']:.3f}
Connected Components: {stats['number_of_components']}

TIER DISTRIBUTION
=================
"""
        
        tier_dist = stats.get('tier_distribution', {})
        for tier, count in sorted(tier_dist.items()):
            percentage = (count / stats['node_count']) * 100 if stats['node_count'] > 0 else 0
            report += f"Tier {tier} (Critical): {count} vendors ({percentage:.1f}%)\n"
        
        report += f"""

STRUCTURAL VULNERABILITIES
==========================
Single Points of Failure: {len(vulnerabilities.get('single_points_of_failure', []))}
High-Degree Nodes: {len(vulnerabilities.get('high_degree_nodes', []))}
Bridge Nodes: {len(vulnerabilities.get('bridge_nodes', []))}

"""
        
        # Add risk assessment if available
        if risk_calculator:
            try:
                risk_metrics = risk_calculator.calculate_comprehensive_risk(self.graph)
                report += f"""RISK ASSESSMENT
===============
Overall Risk Score: {risk_metrics.overall_score:.2f}/1.00
Tier 1 Exposure: {risk_metrics.tier_1_exposure:.2f}/1.00
Cascade Potential: {risk_metrics.cascade_potential:.2f}/1.00
Resilience Score: {risk_metrics.resilience_score:.2f}/1.00
Vulnerability Density: {risk_metrics.vulnerability_density:.2f}/1.00

RECOMMENDATIONS
===============
"""
                
                if risk_metrics.overall_score > 0.7:
                    report += "• CRITICAL: Immediate action required to reduce overall risk\n"
                elif risk_metrics.overall_score > 0.5:
                    report += "• HIGH: Significant risk mitigation measures recommended\n"
                else:
                    report += "• MODERATE: Continue monitoring and gradual improvements\n"
                
                if risk_metrics.single_point_failures > 0:
                    report += f"• Address {risk_metrics.single_point_failures} single points of failure\n"
                
                if risk_metrics.tier_1_exposure > 0.6:
                    report += "• Implement additional protections for critical tier vendors\n"
                
                if risk_metrics.resilience_score < 0.5:
                    report += "• Improve network resilience through redundancy and diversification\n"
                
            except Exception as e:
                report += f"Risk assessment unavailable: {e}\n"
        
        return report
    
    def generate_detailed_vendor_report(self, risk_calculator=None) -> str:
        """Generate detailed vendor-by-vendor report."""
        
        report = f"""
GUARDIAN AI DETAILED VENDOR ANALYSIS
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
        
        # Get risk profiles if available
        node_risks = {}
        if risk_calculator:
            try:
                node_risks = risk_calculator.calculate_node_risk_profiles(self.graph)
            except Exception as e:
                logger.error(f"Risk calculation failed: {e}")
        
        # Sort vendors by tier and risk
        vendors = []
        for node_id in self.graph.graph.nodes():
            node_data = self.graph.graph.nodes[node_id]
            node_features = self.graph.node_features.get(node_id)
            risk_profile = node_risks.get(node_id)
            
            vendors.append({
                'id': node_id,
                'name': node_data.get('name', node_id),
                'tier': node_features.tier if node_features else 3,
                'category': node_data.get('category', 'unknown'),
                'risk_score': risk_profile.combined_risk if risk_profile else 0.0,
                'risk_level': risk_profile.risk_level.value if risk_profile else 'unknown',
                'in_degree': self.graph.graph.in_degree(node_id),
                'out_degree': self.graph.graph.out_degree(node_id)
            })
        
        # Sort by tier (ascending) then risk (descending)
        vendors.sort(key=lambda x: (x['tier'], -x['risk_score']))
        
        current_tier = None
        for vendor in vendors:
            if vendor['tier'] != current_tier:
                current_tier = vendor['tier']
                tier_name = {1: 'CRITICAL', 2: 'IMPORTANT', 3: 'STANDARD'}.get(current_tier, 'UNKNOWN')
                report += f"\nTIER {current_tier} ({tier_name}) VENDORS\n"
                report += "=" * 50 + "\n"
            
            report += f"""
Vendor: {vendor['name']} ({vendor['id']})
Category: {vendor['category']}
Risk Level: {vendor['risk_level'].upper()}
Risk Score: {vendor['risk_score']:.3f}
Dependencies: {vendor['out_degree']} outgoing, {vendor['in_degree']} incoming
"""
            
            # Add risk factors if available
            if vendor['id'] in node_risks:
                risk_profile = node_risks[vendor['id']]
                if risk_profile.contributing_factors:
                    report += "Risk Factors:\n"
                    for factor in risk_profile.contributing_factors:
                        report += f"  • {factor}\n"
        
        return report
    
    def generate_mitigation_report(self, mitigation_engine=None) -> str:
        """Generate mitigation strategies report."""
        
        report = f"""
GUARDIAN AI MITIGATION STRATEGIES
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
        
        if mitigation_engine:
            try:
                strategies = mitigation_engine.generate_mitigation_strategies(8)
                
                report += f"RECOMMENDED MITIGATION STRATEGIES\n"
                report += "=" * 50 + "\n"
                
                for i, strategy in enumerate(strategies, 1):
                    report += f"""
{i}. {strategy['title']}
   Category: {strategy['category'].title()}
   Priority: {strategy['priority']}
   Risk Reduction: {strategy['riskReduction']}%
   Implementation Time: {strategy['implementationTime']}
   Cost Estimate: {strategy['cost']}
   Affected Vendors: {strategy['affectedVendors']}
   
   Description: {strategy['description']}
   
   Technical Details: {strategy['technicalDetails']}
   
   Business Justification: {strategy['businessJustification']}
   
   ---
"""
                
            except Exception as e:
                report += f"Mitigation analysis unavailable: {e}\n"
        else:
            report += "Mitigation engine not available\n"
        
        return report


def export_comprehensive_analysis(supply_chain_graph: SupplyChainGraph, 
                                output_dir: str,
                                risk_calculator=None,
                                mitigation_engine=None) -> Dict[str, str]:
    """Export comprehensive analysis in multiple formats."""
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    exporter = DataExporter(supply_chain_graph)
    reporter = ReportGenerator(supply_chain_graph)
    
    exported_files = {}
    
    # Export data files
    json_path = output_path / "supply_chain_data.json"
    exporter.export_to_json(str(json_path))
    exported_files['json'] = str(json_path)
    
    nodes_csv = output_path / "vendors.csv"
    edges_csv = output_path / "dependencies.csv"
    exporter.export_to_csv(str(nodes_csv), str(edges_csv))
    exported_files['nodes_csv'] = str(nodes_csv)
    exported_files['edges_csv'] = str(edges_csv)
    
    cytoscape_path = output_path / "cytoscape_data.json"
    exporter.export_to_cytoscape(str(cytoscape_path))
    exported_files['cytoscape'] = str(cytoscape_path)
    
    # Export analysis
    risk_analysis_path = output_path / "risk_analysis.json"
    exporter.export_risk_analysis(str(risk_analysis_path), risk_calculator)
    exported_files['risk_analysis'] = str(risk_analysis_path)
    
    simulation_path = output_path / "simulation_data.json"
    exporter.export_simulation_ready_format(str(simulation_path))
    exported_files['simulation'] = str(simulation_path)
    
    # Export reports
    executive_report_path = output_path / "executive_summary.txt"
    with open(executive_report_path, 'w') as f:
        f.write(reporter.generate_executive_summary(risk_calculator))
    exported_files['executive_report'] = str(executive_report_path)
    
    vendor_report_path = output_path / "detailed_vendor_report.txt"
    with open(vendor_report_path, 'w') as f:
        f.write(reporter.generate_detailed_vendor_report(risk_calculator))
    exported_files['vendor_report'] = str(vendor_report_path)
    
    mitigation_report_path = output_path / "mitigation_strategies.txt"
    with open(mitigation_report_path, 'w') as f:
        f.write(reporter.generate_mitigation_report(mitigation_engine))
    exported_files['mitigation_report'] = str(mitigation_report_path)
    
    logger.info(f"Comprehensive analysis exported to {output_dir}")
    return exported_files