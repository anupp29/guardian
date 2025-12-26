export interface DashboardMetrics {
  current: {
    totalVendors: number;
    criticalVendors: number;
    highRiskVendors: number;
    overallRiskScore: number;
    lastUpdated: string;
  };
  trends: {
    riskScoreChange: number;
    newVendorsAdded: number;
    vendorsRemoved: number;
    periodDays: number;
  };
  distribution: {
    byTier: {
      tier1: number;
      tier2: number;
      tier3: number;
    };
    byCategory: {
      authentication: number;
      payment: number;
      data: number;
      api: number;
      infrastructure: number;
    };
    byRiskLevel: {
      low: number;
      medium: number;
      high: number;
      critical: number;
    };
  };
}

export const dashboardMetrics: DashboardMetrics = {
  current: {
    totalVendors: 50,
    criticalVendors: 5,
    highRiskVendors: 8,
    overallRiskScore: 23,
    lastUpdated: "2024-12-20T14:30:00Z"
  },
  trends: {
    riskScoreChange: -5,
    newVendorsAdded: 2,
    vendorsRemoved: 1,
    periodDays: 30
  },
  distribution: {
    byTier: {
      tier1: 5,
      tier2: 15,
      tier3: 30
    },
    byCategory: {
      authentication: 5,
      payment: 8,
      data: 12,
      api: 15,
      infrastructure: 10
    },
    byRiskLevel: {
      low: 28,
      medium: 14,
      high: 6,
      critical: 2
    }
  }
};

export interface SimulationMetrics {
  simulationsRun: number;
  averageBlastRadius: number;
  criticalPathsIdentified: number;
  mitigationsImplemented: number;
  riskReductionAchieved: number;
}

export const simulationMetrics: SimulationMetrics = {
  simulationsRun: 24,
  averageBlastRadius: 28,
  criticalPathsIdentified: 47,
  mitigationsImplemented: 12,
  riskReductionAchieved: 34
};
