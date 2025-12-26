import { ApiResponse, NodeRisk, RiskAssessment, SystemHealth } from './types';

const API_BASE_URL = 'http://localhost:8000';

export class ApiClient {
    private static async fetch<T>(endpoint: string): Promise<T> {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`);
            if (!response.ok) {
                throw new Error(`API Error: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`Failed to fetch ${endpoint}:`, error);
            throw error;
        }
    }

    static async getSystemHealth(): Promise<SystemHealth> {
        return this.fetch<SystemHealth>('/health');
    }

    static async getRiskAssessment(): Promise<ApiResponse<RiskAssessment>> {
        return this.fetch<ApiResponse<RiskAssessment>>('/api/risk/assessment');
    }

    static async getNodeRisks(): Promise<ApiResponse<NodeRisk[]>> {
        return this.fetch<ApiResponse<NodeRisk[]>>('/api/risk/nodes');
    }

    static async getGraphExport(): Promise<any> { // Typing graph export might be complex, leaving as any for now
        return this.fetch<any>('/api/graph/export');
    }

    static async getMitigationStrategies(): Promise<any> {
        return this.fetch<any>('/api/mitigation/strategies');
    }
}
