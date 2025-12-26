export interface Vendor {
    id: string;
    name: string;
    category: string;
    tier: number;
    riskScore: number;
    status: string;
    metadata: Record<string, any>;
}

export interface RiskAssessment {
    overall_score: number;
    tier_1_exposure: number;
    cascade_potential: number;
    single_point_failures: number;
    critical_path_count: number;
    vulnerability_density: number;
    resilience_score: number;
    explanation?: any;
}

export interface NodeRisk {
    node_id: string;
    combined_risk: number;
    risk_level: string;
    contributing_factors: string[];
    base_risk: number;
    structural_risk: number;
    cascade_amplification: number;
    centrality_risk: number;
}

export interface SystemHealth {
    status: string;
    system_health_score: number;
    components: Record<string, boolean>;
    performance: Record<string, number>;
    timestamp: string;
}

export interface ApiResponse<T> {
    success: boolean;
    data: T;
    timestamp: string;
}

export interface MitigationStrategy {
    id: string;
    title: string;
    riskReduction: number;
    effectiveness: 'very_high' | 'high' | 'medium' | 'low';
    implementationTime: string;
    cost: string;
    priority: number;
    affectedVendors: number;
    category: string;
    description: string;
    technicalDetails?: string;
    businessJustification?: string;
}
