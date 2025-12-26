import json
import csv
import pandas as pd
import numpy as np
import networkx as nx
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
import logging
from pathlib import Path
import random
from datetime import datetime, timedelta
import uuid

from .graph_engine import SupplyChainGraph, NodeType, EdgeType

logger = logging.getLogger(__name__)

@dataclass
class VendorData:
    id: str
    name: str
    category: str
    tier: int
    risk_score: float
    status: str
    contract_type: str
    last_audit: str
    certifications: List[str]
    criticality_score: int
    employee_access: int
    data_categories: List[str]

@dataclass
class DependencyData:
    id: str
    source: str
    target: str
    type: str
    category: str
    strength: float
    last_verified: str
    data_volume: str
    criticality: str

class MERCORDataLoader:
    """
    Data loader for MERCOR supply chain dataset and synthetic data generation.
    Creates realistic supply chain graphs with proper vendor relationships.
    """
    
    def __init__(self):
        self.vendors = []
        self.dependencies = []
        self.categories = {
            'authentication': ['Okta', 'Auth0', 'Microsoft Azure AD', 'Ping Identity', 'OneLogin'],
            'payment': ['Stripe', 'PayPal', 'Square', 'Adyen', 'Braintree', 'Klarna', 'Worldpay', 'Authorize.Net'],
            'data': ['AWS S3', 'Google Cloud Storage', 'Azure Blob', 'Snowflake', 'MongoDB Atlas', 'PostgreSQL Cloud', 'Redis Cloud', 'Elasticsearch Cloud', 'Databricks', 'BigQuery', 'Redshift', 'Cassandra'],
            'api': ['Twilio', 'SendGrid', 'Mailgun', 'Slack API', 'GitHub API', 'Google Maps', 'Zoom API', 'Salesforce API', 'HubSpot API', 'Zendesk API', 'Intercom API', 'Shopify API', 'DocuSign API', 'Adobe API', 'Dropbox API'],
            'infrastructure': ['AWS EC2', 'Google Compute', 'Azure VMs', 'DigitalOcean', 'Linode', 'Heroku', 'Vercel', 'Netlify', 'Cloudflare', 'Fastly']
        }
        
        # Realistic company names for different categories
        self.company_suffixes = ['Inc', 'Corp', 'LLC', 'Ltd', 'Systems', 'Solutions', 'Technologies', 'Services', 'Platform', 'Labs']
        
    def generate_realistic_supply_chain(self, num_vendors: int = 50) -> SupplyChainGraph:
        """Generate a realistic supply chain graph with proper relationships."""
        
        logger.info(f"Generating supply chain with {num_vendors} vendors")
        
        # Generate vendors
        self.vendors = self._generate_vendors(num_vendors)
        
        # Generate dependencies with realistic patterns
        self.dependencies = self._generate_dependencies()
        
        # Create supply chain graph
        graph = self._build_supply_chain_graph()
        
        logger.info(f"Generated supply chain: {len(graph.graph.nodes())} nodes, {len(graph.graph.edges())} edges")
        
        return graph
    
    def _generate_vendors(self, num_vendors: int) -> List[VendorData]:
        """Generate realistic vendor data."""
        vendors = []
        
        # Ensure we have vendors in each category
        category_counts = {
            'authentication': 5,
            'payment': 8,
            'data': 12,
            'api': 15,
            'infrastructure': 10
        }
        
        # Adjust counts to match total
        total_planned = sum(category_counts.values())
        if total_planned != num_vendors:
            # Distribute remaining vendors
            remaining = num_vendors - total_planned
            categories = list(category_counts.keys())
            for i in range(abs(remaining)):
                if remaining > 0:
                    category_counts[categories[i % len(categories)]] += 1
                else:
                    if category_counts[categories[i % len(categories)]] > 1:
                        category_counts[categories[i % len(categories)]] -= 1
        
        vendor_id_counter = 1
        
        for category, count in category_counts.items():
            for i in range(count):
                vendor = self._create_vendor(vendor_id_counter, category, i)
                vendors.append(vendor)
                vendor_id_counter += 1
        
        return vendors
    
    def _create_vendor(self, vendor_id: int, category: str, index: int) -> VendorData:
        """Create a single realistic vendor."""
        
        # Use real company names for first few in each category, then generate synthetic ones
        if index < len(self.categories[category]):
            name = self.categories[category][index]
            vendor_id_str = f"vnd_{category}_{name.lower().replace(' ', '_').replace('.', '')}"
        else:
            # Generate synthetic company name
            base_names = {
                'authentication': ['SecureAuth', 'IdentityGuard', 'AccessControl', 'AuthFlow', 'TrustLink'],
                'payment': ['PayFlow', 'TransactPro', 'MoneyBridge', 'PaymentHub', 'CashLink'],
                'data': ['DataVault', 'CloudStore', 'InfoBase', 'DataFlow', 'StorageMax'],
                'api': ['APIBridge', 'ConnectHub', 'IntegrationPro', 'ServiceLink', 'APIFlow'],
                'infrastructure': ['CloudOps', 'InfraPro', 'ServerMax', 'HostingPlus', 'CloudBridge']
            }
            
            base_name = random.choice(base_names[category])
            suffix = random.choice(self.company_suffixes)
            name = f"{base_name} {suffix}"
            vendor_id_str = f"vnd_{category}_{vendor_id:03d}"
        
        # Assign tier based on category and randomness
        tier_probabilities = {
            'authentication': [0.4, 0.4, 0.2],  # 40% tier 1, 40% tier 2, 20% tier 3
            'payment': [0.3, 0.5, 0.2],
            'data': [0.2, 0.4, 0.4],
            'api': [0.1, 0.3, 0.6],
            'infrastructure': [0.3, 0.4, 0.3]
        }
        
        tier = np.random.choice([1, 2, 3], p=tier_probabilities[category])
        
        # Risk score based on tier and some randomness
        base_risk = {1: 0.15, 2: 0.25, 3: 0.35}[tier]
        risk_score = max(0.0, min(1.0, base_risk + np.random.normal(0, 0.1)))
        
        # Status (most are secure)
        status_prob = [0.85, 0.10, 0.05]  # secure, warning, compromised
        status = np.random.choice(['secure', 'warning', 'compromised'], p=status_prob)
        
        # Contract type
        contract_types = ['annual', 'multi-year', 'month-to-month']
        contract_weights = [0.6, 0.3, 0.1]
        contract_type = np.random.choice(contract_types, p=contract_weights)
        
        # Last audit (within last 2 years)
        days_ago = np.random.randint(30, 730)
        last_audit = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        # Certifications
        all_certifications = ['SOC2', 'ISO27001', 'PCI DSS', 'HIPAA', 'FedRAMP', 'GDPR']
        num_certs = np.random.choice([0, 1, 2, 3], p=[0.2, 0.4, 0.3, 0.1])
        certifications = random.sample(all_certifications, min(num_certs, len(all_certifications)))
        
        # Criticality score (inverse of risk, with some noise)
        criticality_score = int(max(10, min(100, (1 - risk_score) * 100 + np.random.normal(0, 10))))
        
        # Employee access (realistic numbers)
        access_ranges = {1: (1000, 5000), 2: (500, 2000), 3: (100, 1000)}
        min_access, max_access = access_ranges[tier]
        employee_access = np.random.randint(min_access, max_access)
        
        # Data categories
        category_mappings = {
            'authentication': ['authentication', 'user_identity', 'access_control'],
            'payment': ['payment_data', 'financial', 'transaction_logs'],
            'data': ['customer_data', 'analytics', 'backups', 'logs'],
            'api': ['integration_data', 'api_logs', 'service_data'],
            'infrastructure': ['system_logs', 'performance_data', 'configuration']
        }
        
        data_categories = category_mappings[category]
        if np.random.random() > 0.7:  # 30% chance of additional categories
            other_categories = [cat for cats in category_mappings.values() for cat in cats if cat not in data_categories]
            additional = random.sample(other_categories, min(2, len(other_categories)))
            data_categories.extend(additional)
        
        return VendorData(
            id=vendor_id_str,
            name=name,
            category=category,
            tier=tier,
            risk_score=risk_score,
            status=status,
            contract_type=contract_type,
            last_audit=last_audit,
            certifications=certifications,
            criticality_score=criticality_score,
            employee_access=employee_access,
            data_categories=data_categories
        )
    
    def _generate_dependencies(self) -> List[DependencyData]:
        """Generate realistic dependency relationships."""
        dependencies = []
        dependency_id_counter = 1
        
        # Create vendor lookup
        vendor_by_category = {}
        for vendor in self.vendors:
            if vendor.category not in vendor_by_category:
                vendor_by_category[vendor.category] = []
            vendor_by_category[vendor.category].append(vendor)
        
        # Define realistic dependency patterns
        dependency_patterns = {
            # Most services depend on authentication
            'authentication': {
                'targets': ['payment', 'data', 'api', 'infrastructure'],
                'probability': 0.8,
                'type': 'depends_on',
                'category': 'authentication'
            },
            # Payment services often integrate with data storage
            'payment': {
                'targets': ['data', 'api'],
                'probability': 0.7,
                'type': 'integrates_with',
                'category': 'data_flow'
            },
            # Data services may depend on infrastructure
            'data': {
                'targets': ['infrastructure'],
                'probability': 0.6,
                'type': 'depends_on',
                'category': 'infrastructure'
            },
            # API services connect to various other services
            'api': {
                'targets': ['data', 'authentication', 'infrastructure'],
                'probability': 0.5,
                'type': 'integrates_with',
                'category': 'api_call'
            },
            # Infrastructure provides foundation for others
            'infrastructure': {
                'targets': ['data'],
                'probability': 0.4,
                'type': 'supplies',
                'category': 'infrastructure'
            }
        }
        
        # Generate dependencies based on patterns
        for source_vendor in self.vendors:
            source_category = source_vendor.category
            
            if source_category in dependency_patterns:
                pattern = dependency_patterns[source_category]
                
                for target_category in pattern['targets']:
                    if target_category in vendor_by_category:
                        target_vendors = vendor_by_category[target_category]
                        
                        # Each source vendor connects to 1-3 vendors in target category
                        num_connections = min(len(target_vendors), np.random.choice([1, 2, 3], p=[0.5, 0.3, 0.2]))
                        
                        selected_targets = random.sample(target_vendors, num_connections)
                        
                        for target_vendor in selected_targets:
                            if np.random.random() < pattern['probability']:
                                dependency = self._create_dependency(
                                    dependency_id_counter,
                                    source_vendor,
                                    target_vendor,
                                    pattern['type'],
                                    pattern['category']
                                )
                                dependencies.append(dependency)
                                dependency_id_counter += 1
        
        # Add some random cross-category dependencies for realism
        for _ in range(len(self.vendors) // 4):  # About 25% additional random connections
            source = random.choice(self.vendors)
            target = random.choice(self.vendors)
            
            if source.id != target.id:
                # Avoid duplicate dependencies
                existing = any(d.source == source.id and d.target == target.id for d in dependencies)
                if not existing:
                    dependency = self._create_dependency(
                        dependency_id_counter,
                        source,
                        target,
                        'integrates_with',
                        'cross_category'
                    )
                    dependencies.append(dependency)
                    dependency_id_counter += 1
        
        return dependencies
    
    def _create_dependency(self, dep_id: int, source: VendorData, target: VendorData, 
                          dep_type: str, category: str) -> DependencyData:
        """Create a single dependency relationship."""
        
        # Strength based on tier relationship
        source_tier = source.tier
        target_tier = target.tier
        
        # Higher tier dependencies are typically stronger
        base_strength = 0.5
        if source_tier == 1 or target_tier == 1:
            base_strength = 0.8
        elif source_tier == 2 or target_tier == 2:
            base_strength = 0.6
        
        strength = max(0.1, min(1.0, base_strength + np.random.normal(0, 0.15)))
        
        # Last verified (within last year)
        days_ago = np.random.randint(1, 365)
        last_verified = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        # Data volume
        data_volumes = ['low', 'medium', 'high']
        volume_weights = [0.4, 0.4, 0.2]
        data_volume = np.random.choice(data_volumes, p=volume_weights)
        
        # Criticality
        criticalities = ['low', 'medium', 'high']
        # Higher tier relationships tend to be more critical
        if source_tier == 1 or target_tier == 1:
            crit_weights = [0.1, 0.3, 0.6]
        elif source_tier == 2 or target_tier == 2:
            crit_weights = [0.2, 0.5, 0.3]
        else:
            crit_weights = [0.4, 0.4, 0.2]
        
        criticality = np.random.choice(criticalities, p=crit_weights)
        
        return DependencyData(
            id=f"dep_{dep_id:03d}",
            source=source.id,
            target=target.id,
            type=dep_type,
            category=category,
            strength=strength,
            last_verified=last_verified,
            data_volume=data_volume,
            criticality=criticality
        )
    
    def _build_supply_chain_graph(self) -> SupplyChainGraph:
        """Build the supply chain graph from generated data."""
        graph = SupplyChainGraph()
        
        # Add nodes
        for vendor in self.vendors:
            node_type = NodeType.VENDOR  # All are vendors in this implementation
            
            metadata = {
                'name': vendor.name,
                'category': vendor.category,
                'status': vendor.status,
                'contractType': vendor.contract_type,
                'lastAudit': vendor.last_audit,
                'certifications': vendor.certifications,
                'employeeAccess': vendor.employee_access,
                'dataCategories': vendor.data_categories
            }
            
            graph.add_node(
                node_id=vendor.id,
                node_type=node_type,
                tier=vendor.tier,
                risk_score=vendor.risk_score,
                criticality_score=vendor.criticality_score,
                metadata=metadata
            )
        
        # Add edges
        for dependency in self.dependencies:
            edge_type = EdgeType.DEPENDS_ON
            if dependency.type == 'integrates_with':
                edge_type = EdgeType.INTEGRATES_WITH
            elif dependency.type == 'supplies':
                edge_type = EdgeType.SUPPLIES
            
            metadata = {
                'lastVerified': dependency.last_verified,
                'dataVolume': dependency.data_volume
            }
            
            graph.add_edge(
                source=dependency.source,
                target=dependency.target,
                edge_type=edge_type,
                dependency_category=dependency.category,
                strength=dependency.strength,
                criticality=dependency.criticality,
                metadata=metadata
            )
        
        return graph
    
    def load_from_csv(self, vendors_file: str, dependencies_file: str) -> SupplyChainGraph:
        """Load supply chain data from CSV files."""
        
        logger.info(f"Loading supply chain from CSV files: {vendors_file}, {dependencies_file}")
        
        # Load vendors
        vendors_df = pd.read_csv(vendors_file)
        self.vendors = []
        
        for _, row in vendors_df.iterrows():
            vendor = VendorData(
                id=row['id'],
                name=row['name'],
                category=row['category'],
                tier=int(row['tier']),
                risk_score=float(row['risk_score']),
                status=row['status'],
                contract_type=row.get('contract_type', 'annual'),
                last_audit=row.get('last_audit', '2024-01-01'),
                certifications=json.loads(row.get('certifications', '[]')),
                criticality_score=int(row.get('criticality_score', 50)),
                employee_access=int(row.get('employee_access', 1000)),
                data_categories=json.loads(row.get('data_categories', '[]'))
            )
            self.vendors.append(vendor)
        
        # Load dependencies
        dependencies_df = pd.read_csv(dependencies_file)
        self.dependencies = []
        
        for _, row in dependencies_df.iterrows():
            dependency = DependencyData(
                id=row['id'],
                source=row['source'],
                target=row['target'],
                type=row['type'],
                category=row['category'],
                strength=float(row['strength']),
                last_verified=row.get('last_verified', '2024-01-01'),
                data_volume=row.get('data_volume', 'medium'),
                criticality=row.get('criticality', 'medium')
            )
            self.dependencies.append(dependency)
        
        # Build graph
        graph = self._build_supply_chain_graph()
        
        logger.info(f"Loaded supply chain: {len(graph.graph.nodes())} nodes, {len(graph.graph.edges())} edges")
        
        return graph
    
    def save_to_csv(self, vendors_file: str, dependencies_file: str):
        """Save current supply chain data to CSV files."""
        
        # Save vendors
        vendors_data = []
        for vendor in self.vendors:
            vendors_data.append({
                'id': vendor.id,
                'name': vendor.name,
                'category': vendor.category,
                'tier': vendor.tier,
                'risk_score': vendor.risk_score,
                'status': vendor.status,
                'contract_type': vendor.contract_type,
                'last_audit': vendor.last_audit,
                'certifications': json.dumps(vendor.certifications),
                'criticality_score': vendor.criticality_score,
                'employee_access': vendor.employee_access,
                'data_categories': json.dumps(vendor.data_categories)
            })
        
        vendors_df = pd.DataFrame(vendors_data)
        vendors_df.to_csv(vendors_file, index=False)
        
        # Save dependencies
        dependencies_data = []
        for dependency in self.dependencies:
            dependencies_data.append({
                'id': dependency.id,
                'source': dependency.source,
                'target': dependency.target,
                'type': dependency.type,
                'category': dependency.category,
                'strength': dependency.strength,
                'last_verified': dependency.last_verified,
                'data_volume': dependency.data_volume,
                'criticality': dependency.criticality
            })
        
        dependencies_df = pd.DataFrame(dependencies_data)
        dependencies_df.to_csv(dependencies_file, index=False)
        
        logger.info(f"Saved supply chain data to {vendors_file} and {dependencies_file}")
    
    def export_for_frontend(self, output_file: str):
        """Export data in format suitable for frontend consumption."""
        
        # Convert to frontend format
        frontend_data = {
            'vendors': [],
            'dependencies': [],
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_vendors': len(self.vendors),
                'total_dependencies': len(self.dependencies),
                'categories': list(self.categories.keys())
            }
        }
        
        # Export vendors
        for vendor in self.vendors:
            frontend_vendor = {
                'id': vendor.id,
                'name': vendor.name,
                'category': vendor.category,
                'tier': vendor.tier,
                'riskScore': vendor.risk_score,
                'status': vendor.status,
                'metadata': {
                    'contractType': vendor.contract_type,
                    'lastAudit': vendor.last_audit,
                    'certifications': vendor.certifications,
                    'criticalityScore': vendor.criticality_score,
                    'employeeAccess': vendor.employee_access,
                    'dataCategories': vendor.data_categories
                }
            }
            frontend_data['vendors'].append(frontend_vendor)
        
        # Export dependencies
        for dependency in self.dependencies:
            frontend_dependency = {
                'id': dependency.id,
                'source': dependency.source,
                'target': dependency.target,
                'type': dependency.type,
                'category': dependency.category,
                'strength': dependency.strength,
                'metadata': {
                    'lastVerified': dependency.last_verified,
                    'dataVolume': dependency.data_volume,
                    'criticality': dependency.criticality
                }
            }
            frontend_data['dependencies'].append(frontend_dependency)
        
        # Save to JSON
        with open(output_file, 'w') as f:
            json.dump(frontend_data, f, indent=2)
        
        logger.info(f"Exported frontend data to {output_file}")
    
    def generate_simulation_scenarios(self, graph: SupplyChainGraph, num_scenarios: int = 5) -> List[Dict[str, Any]]:
        """Generate realistic simulation scenarios."""
        
        scenarios = []
        
        # Get vendors by tier for realistic scenario selection
        tier_1_vendors = [v.id for v in self.vendors if v.tier == 1]
        tier_2_vendors = [v.id for v in self.vendors if v.tier == 2]
        high_risk_vendors = [v.id for v in self.vendors if v.risk_score > 0.6]
        
        scenario_templates = [
            {
                'name': 'Critical Authentication Compromise',
                'description': 'Compromise of primary authentication provider',
                'initial_compromised': lambda: random.sample([v for v in tier_1_vendors if any(vendor.category == 'authentication' for vendor in self.vendors if vendor.id == v)], 1),
                'severity': 'critical'
            },
            {
                'name': 'Payment System Breach',
                'description': 'Breach of payment processing infrastructure',
                'initial_compromised': lambda: random.sample([v for v in tier_1_vendors + tier_2_vendors if any(vendor.category == 'payment' for vendor in self.vendors if vendor.id == v)], min(2, len([v for v in tier_1_vendors + tier_2_vendors if any(vendor.category == 'payment' for vendor in self.vendors if vendor.id == v)]))),
                'severity': 'high'
            },
            {
                'name': 'Data Storage Compromise',
                'description': 'Compromise of critical data storage systems',
                'initial_compromised': lambda: random.sample([v for v in tier_1_vendors + tier_2_vendors if any(vendor.category == 'data' for vendor in self.vendors if vendor.id == v)], min(2, len([v for v in tier_1_vendors + tier_2_vendors if any(vendor.category == 'data' for vendor in self.vendors if vendor.id == v)]))),
                'severity': 'high'
            },
            {
                'name': 'API Integration Attack',
                'description': 'Coordinated attack through API integrations',
                'initial_compromised': lambda: random.sample([v for v in self.vendors if v.category == 'api'][:3], min(3, len([v for v in self.vendors if v.category == 'api']))),
                'severity': 'medium'
            },
            {
                'name': 'Infrastructure Failure',
                'description': 'Critical infrastructure provider compromise',
                'initial_compromised': lambda: random.sample([v for v in tier_1_vendors if any(vendor.category == 'infrastructure' for vendor in self.vendors if vendor.id == v)], min(1, len([v for v in tier_1_vendors if any(vendor.category == 'infrastructure' for vendor in self.vendors if vendor.id == v)]))),
                'severity': 'high'
            },
            {
                'name': 'High-Risk Vendor Compromise',
                'description': 'Compromise of vendors with elevated risk scores',
                'initial_compromised': lambda: random.sample(high_risk_vendors, min(2, len(high_risk_vendors))),
                'severity': 'medium'
            }
        ]
        
        # Generate scenarios
        for i in range(min(num_scenarios, len(scenario_templates))):
            template = scenario_templates[i]
            
            try:
                initial_compromised = template['initial_compromised']()
                if not initial_compromised:
                    continue
                
                scenario = {
                    'id': f'scenario_{i+1}',
                    'name': template['name'],
                    'description': template['description'],
                    'initial_compromised': initial_compromised,
                    'severity': template['severity'],
                    'created_at': datetime.now().isoformat()
                }
                
                scenarios.append(scenario)
                
            except Exception as e:
                logger.warning(f"Failed to generate scenario {template['name']}: {e}")
        
        return scenarios
    
    def generate_mitigation_strategies(self, graph: SupplyChainGraph) -> List[Dict[str, Any]]:
        """Generate realistic mitigation strategies based on the supply chain structure."""
        
        strategies = []
        
        # Analyze graph for mitigation opportunities
        vulnerabilities = graph.identify_structural_vulnerabilities()
        centrality_metrics = graph.calculate_centrality_metrics()
        
        # Strategy 1: Address single points of failure
        spof_nodes = vulnerabilities.get('single_points_of_failure', [])
        if spof_nodes:
            top_spof = spof_nodes[0] if spof_nodes else None
            if top_spof:
                vendor_name = next((v.name for v in self.vendors if v.id == top_spof), top_spof)
                strategies.append({
                    'id': 'mit_001',
                    'title': f'Implement Redundancy for {vendor_name}',
                    'riskReduction': 65,
                    'effectiveness': 'very_high',
                    'implementationTime': '3-4 weeks',
                    'cost': '$$',
                    'priority': 1,
                    'affectedVendors': len([n for n in graph.graph.successors(top_spof)]) + 1,
                    'category': 'redundancy',
                    'description': f'Deploy backup systems for {vendor_name} to eliminate single point of failure. Implement automatic failover mechanisms.',
                    'technicalDetails': f'Configure secondary provider with real-time synchronization. Implement health monitoring and automatic failover with <30 second transition time.',
                    'businessJustification': f'Eliminates critical dependency on {vendor_name}, protecting downstream services from cascading failures.'
                })
        
        # Strategy 2: Secure high-centrality nodes
        if centrality_metrics:
            high_centrality_nodes = sorted(
                centrality_metrics.items(),
                key=lambda x: x[1].get('betweenness_centrality', 0),
                reverse=True
            )[:3]
            
            for i, (node_id, metrics) in enumerate(high_centrality_nodes):
                vendor_name = next((v.name for v in self.vendors if v.id == node_id), node_id)
                strategies.append({
                    'id': f'mit_{len(strategies)+1:03d}',
                    'title': f'Enhanced Security for {vendor_name}',
                    'riskReduction': 45 - i*5,
                    'effectiveness': 'high' if i == 0 else 'medium',
                    'implementationTime': '2-3 weeks',
                    'cost': '$' if i > 1 else '$$',
                    'priority': i + 2,
                    'affectedVendors': len([n for n in graph.graph.neighbors(node_id)]),
                    'category': 'hardening',
                    'description': f'Implement additional security controls for {vendor_name} due to high network centrality.',
                    'technicalDetails': 'Deploy advanced monitoring, implement zero-trust access controls, and enhance incident response capabilities.',
                    'businessJustification': f'{vendor_name} is a critical network hub - securing it protects multiple downstream dependencies.'
                })
        
        # Strategy 3: Category-specific mitigations
        category_strategies = {
            'authentication': {
                'title': 'Multi-Factor Authentication Redundancy',
                'description': 'Deploy secondary authentication provider as failover system.',
                'riskReduction': 55,
                'category': 'authentication'
            },
            'payment': {
                'title': 'Payment Processing Diversification',
                'description': 'Implement multiple payment processors to reduce single-provider risk.',
                'riskReduction': 40,
                'category': 'payment'
            },
            'data': {
                'title': 'Data Backup and Recovery Enhancement',
                'description': 'Implement cross-provider data replication and enhanced backup systems.',
                'riskReduction': 35,
                'category': 'data'
            }
        }
        
        for category, strategy_template in category_strategies.items():
            category_vendors = [v for v in self.vendors if v.category == category and v.tier <= 2]
            if category_vendors:
                strategies.append({
                    'id': f'mit_{len(strategies)+1:03d}',
                    'title': strategy_template['title'],
                    'riskReduction': strategy_template['riskReduction'],
                    'effectiveness': 'high',
                    'implementationTime': '4-6 weeks',
                    'cost': '$$',
                    'priority': len(strategies) + 1,
                    'affectedVendors': len(category_vendors),
                    'category': strategy_template['category'],
                    'description': strategy_template['description'],
                    'technicalDetails': f'Coordinate with {len(category_vendors)} {category} providers to implement redundant systems.',
                    'businessJustification': f'Reduces risk across entire {category} category, protecting {len(category_vendors)} critical vendors.'
                })
        
        # Sort by priority and limit to top 8
        strategies.sort(key=lambda x: x['priority'])
        return strategies[:8]


class DataValidator:
    """Validate supply chain data for consistency and realism."""
    
    @staticmethod
    def validate_supply_chain_data(vendors: List[VendorData], dependencies: List[DependencyData]) -> Dict[str, List[str]]:
        """Validate supply chain data and return any issues found."""
        
        issues = {
            'errors': [],
            'warnings': [],
            'info': []
        }
        
        # Check vendor data
        vendor_ids = set()
        for vendor in vendors:
            # Check for duplicate IDs
            if vendor.id in vendor_ids:
                issues['errors'].append(f"Duplicate vendor ID: {vendor.id}")
            vendor_ids.add(vendor.id)
            
            # Check tier values
            if vendor.tier not in [1, 2, 3]:
                issues['errors'].append(f"Invalid tier {vendor.tier} for vendor {vendor.id}")
            
            # Check risk score range
            if not 0 <= vendor.risk_score <= 1:
                issues['errors'].append(f"Risk score {vendor.risk_score} out of range [0,1] for vendor {vendor.id}")
            
            # Check criticality score
            if not 0 <= vendor.criticality_score <= 100:
                issues['errors'].append(f"Criticality score {vendor.criticality_score} out of range [0,100] for vendor {vendor.id}")
        
        # Check dependency data
        dependency_pairs = set()
        for dependency in dependencies:
            # Check for duplicate dependencies
            pair = (dependency.source, dependency.target)
            if pair in dependency_pairs:
                issues['warnings'].append(f"Duplicate dependency: {dependency.source} -> {dependency.target}")
            dependency_pairs.add(pair)
            
            # Check that source and target exist
            if dependency.source not in vendor_ids:
                issues['errors'].append(f"Dependency source {dependency.source} not found in vendors")
            if dependency.target not in vendor_ids:
                issues['errors'].append(f"Dependency target {dependency.target} not found in vendors")
            
            # Check strength range
            if not 0 <= dependency.strength <= 1:
                issues['errors'].append(f"Dependency strength {dependency.strength} out of range [0,1]")
            
            # Check for self-dependencies
            if dependency.source == dependency.target:
                issues['warnings'].append(f"Self-dependency detected: {dependency.source}")
        
        # Check graph connectivity
        if len(dependencies) < len(vendors) - 1:
            issues['warnings'].append("Graph may not be connected - too few dependencies")
        
        # Check tier distribution
        tier_counts = {1: 0, 2: 0, 3: 0}
        for vendor in vendors:
            tier_counts[vendor.tier] += 1
        
        if tier_counts[1] == 0:
            issues['warnings'].append("No tier 1 (critical) vendors found")
        if tier_counts[1] > len(vendors) * 0.3:
            issues['warnings'].append("Too many tier 1 vendors (>30% of total)")
        
        # Info messages
        issues['info'].append(f"Total vendors: {len(vendors)}")
        issues['info'].append(f"Total dependencies: {len(dependencies)}")
        issues['info'].append(f"Tier distribution: T1={tier_counts[1]}, T2={tier_counts[2]}, T3={tier_counts[3]}")
        
        return issues
    
    @staticmethod
    def validate_graph_structure(graph: SupplyChainGraph) -> Dict[str, Any]:
        """Validate the structure of a supply chain graph."""
        
        validation_results = {
            'is_valid': True,
            'issues': [],
            'metrics': {},
            'recommendations': []
        }
        
        # Basic connectivity checks
        if not nx.is_weakly_connected(graph.graph):
            validation_results['is_valid'] = False
            validation_results['issues'].append("Graph is not weakly connected")
        
        # Check for isolated nodes
        isolated_nodes = list(nx.isolates(graph.graph))
        if isolated_nodes:
            validation_results['issues'].append(f"Found {len(isolated_nodes)} isolated nodes")
        
        # Check degree distribution
        degrees = [graph.graph.degree(n) for n in graph.graph.nodes()]
        if degrees:
            avg_degree = sum(degrees) / len(degrees)
            validation_results['metrics']['average_degree'] = avg_degree
            
            if avg_degree < 2:
                validation_results['recommendations'].append("Consider adding more dependencies for better connectivity")
        
        # Check for potential bottlenecks
        vulnerabilities = graph.identify_structural_vulnerabilities()
        spof_count = len(vulnerabilities.get('single_points_of_failure', []))
        
        validation_results['metrics']['single_points_of_failure'] = spof_count
        
        if spof_count > len(graph.graph.nodes()) * 0.1:
            validation_results['recommendations'].append("High number of single points of failure detected")
        
        return validation_results


# Utility functions for data management
def create_sample_supply_chain(num_vendors: int = 50) -> SupplyChainGraph:
    """Create a sample supply chain for testing and demonstration."""
    loader = MERCORDataLoader()
    return loader.generate_realistic_supply_chain(num_vendors)


def export_sample_data(output_dir: str = "data", num_vendors: int = 50):
    """Export sample data files for development and testing."""
    
    Path(output_dir).mkdir(exist_ok=True)
    
    loader = MERCORDataLoader()
    graph = loader.generate_realistic_supply_chain(num_vendors)
    
    # Export in multiple formats
    loader.save_to_csv(
        f"{output_dir}/vendors.csv",
        f"{output_dir}/dependencies.csv"
    )
    
    loader.export_for_frontend(f"{output_dir}/supply_chain_data.json")
    
    # Export scenarios and mitigations
    scenarios = loader.generate_simulation_scenarios(graph)
    with open(f"{output_dir}/simulation_scenarios.json", 'w') as f:
        json.dump(scenarios, f, indent=2)
    
    mitigations = loader.generate_mitigation_strategies(graph)
    with open(f"{output_dir}/mitigation_strategies.json", 'w') as f:
        json.dump(mitigations, f, indent=2)
    
    logger.info(f"Sample data exported to {output_dir}/")
    
    return graph


if __name__ == "__main__":
    # Generate sample data when run directly
    graph = export_sample_data()
    print(f"Generated supply chain with {len(graph.graph.nodes())} vendors and {len(graph.graph.edges())} dependencies")