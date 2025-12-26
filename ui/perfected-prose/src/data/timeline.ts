export interface ActivityEvent {
  id: string;
  type: 'simulation_run' | 'vendor_added' | 'vendor_removed' | 'risk_assessment' | 'mitigation_implemented' | 'alert_triggered';
  title: string;
  severity: 'info' | 'success' | 'warning' | 'critical';
  timestamp: string;
  details: string;
  actor: string;
  icon: string;
}

export const activityFeed: ActivityEvent[] = [
  {
    id: "evt_001",
    type: "simulation_run",
    title: "Simulation: Okta Compromise",
    severity: "critical",
    timestamp: "2024-12-20T14:15:00Z",
    details: "42 vendors affected, 7 critical paths identified",
    actor: "System",
    icon: "AlertTriangle"
  },
  {
    id: "evt_002",
    type: "vendor_added",
    title: "New Vendor: Databricks",
    severity: "info",
    timestamp: "2024-12-20T09:30:00Z",
    details: "Added to data analytics tier 3",
    actor: "Admin User",
    icon: "PlusCircle"
  },
  {
    id: "evt_003",
    type: "risk_assessment",
    title: "Quarterly Risk Assessment Completed",
    severity: "success",
    timestamp: "2024-12-19T16:00:00Z",
    details: "Overall risk decreased by 12%",
    actor: "System",
    icon: "CheckCircle"
  },
  {
    id: "evt_004",
    type: "alert_triggered",
    title: "High Risk: MongoDB Atlas",
    severity: "warning",
    timestamp: "2024-12-19T11:45:00Z",
    details: "Audit overdue by 30 days",
    actor: "System",
    icon: "AlertCircle"
  },
  {
    id: "evt_005",
    type: "mitigation_implemented",
    title: "MFA Redundancy Deployed",
    severity: "success",
    timestamp: "2024-12-18T15:20:00Z",
    details: "Auth0 failover now active",
    actor: "Security Team",
    icon: "Shield"
  },
  {
    id: "evt_006",
    type: "simulation_run",
    title: "Simulation: AWS Breach",
    severity: "critical",
    timestamp: "2024-12-18T10:00:00Z",
    details: "48 vendors affected, worst-case scenario",
    actor: "Risk Analyst",
    icon: "AlertTriangle"
  },
  {
    id: "evt_007",
    type: "vendor_removed",
    title: "Vendor Offboarded: Legacy CRM",
    severity: "info",
    timestamp: "2024-12-17T14:30:00Z",
    details: "Migration to HubSpot complete",
    actor: "IT Admin",
    icon: "MinusCircle"
  },
  {
    id: "evt_008",
    type: "risk_assessment",
    title: "Vendor Score Update: Cloudflare",
    severity: "success",
    timestamp: "2024-12-17T09:15:00Z",
    details: "Risk score improved from 18 to 14",
    actor: "System",
    icon: "TrendingDown"
  },
  {
    id: "evt_009",
    type: "alert_triggered",
    title: "Certificate Expiry Warning",
    severity: "warning",
    timestamp: "2024-12-16T16:45:00Z",
    details: "Stripe API cert expires in 14 days",
    actor: "System",
    icon: "Clock"
  },
  {
    id: "evt_010",
    type: "mitigation_implemented",
    title: "DLP Controls Activated",
    severity: "success",
    timestamp: "2024-12-16T11:00:00Z",
    details: "Cloudflare DLP policies enforced",
    actor: "Security Team",
    icon: "Lock"
  },
  {
    id: "evt_011",
    type: "simulation_run",
    title: "Simulation: Stripe Compromise",
    severity: "warning",
    timestamp: "2024-12-15T15:30:00Z",
    details: "23 vendors affected, payment focus",
    actor: "Risk Analyst",
    icon: "AlertTriangle"
  },
  {
    id: "evt_012",
    type: "vendor_added",
    title: "New Vendor: Algolia",
    severity: "info",
    timestamp: "2024-12-15T10:20:00Z",
    details: "Added to API services tier 3",
    actor: "Engineering Lead",
    icon: "PlusCircle"
  },
  {
    id: "evt_013",
    type: "risk_assessment",
    title: "PCI-DSS Compliance Check",
    severity: "success",
    timestamp: "2024-12-14T14:00:00Z",
    details: "All payment vendors compliant",
    actor: "Compliance Team",
    icon: "CheckCircle"
  },
  {
    id: "evt_014",
    type: "alert_triggered",
    title: "Unusual Access Pattern: Redis",
    severity: "warning",
    timestamp: "2024-12-14T08:30:00Z",
    details: "500% increase in read operations",
    actor: "System",
    icon: "Activity"
  },
  {
    id: "evt_015",
    type: "mitigation_implemented",
    title: "Zero Trust Policies Updated",
    severity: "success",
    timestamp: "2024-12-13T16:15:00Z",
    details: "New device posture requirements active",
    actor: "Security Team",
    icon: "Shield"
  },
  {
    id: "evt_016",
    type: "simulation_run",
    title: "Simulation: Snowflake Breach",
    severity: "warning",
    timestamp: "2024-12-13T11:45:00Z",
    details: "31 vendors affected, data focus",
    actor: "Risk Analyst",
    icon: "AlertTriangle"
  },
  {
    id: "evt_017",
    type: "vendor_added",
    title: "New Vendor: LaunchDarkly",
    severity: "info",
    timestamp: "2024-12-12T09:00:00Z",
    details: "Added to API services tier 3",
    actor: "Product Team",
    icon: "PlusCircle"
  },
  {
    id: "evt_018",
    type: "risk_assessment",
    title: "SOC2 Evidence Collection",
    severity: "success",
    timestamp: "2024-12-11T15:30:00Z",
    details: "Automated evidence gathering complete",
    actor: "System",
    icon: "FileText"
  },
  {
    id: "evt_019",
    type: "alert_triggered",
    title: "Vendor Score Drop: CircleCI",
    severity: "warning",
    timestamp: "2024-12-11T10:15:00Z",
    details: "Score decreased from 52 to 58",
    actor: "System",
    icon: "TrendingUp"
  },
  {
    id: "evt_020",
    type: "mitigation_implemented",
    title: "Incident Response Automation",
    severity: "success",
    timestamp: "2024-12-10T14:00:00Z",
    details: "PagerDuty workflows configured",
    actor: "DevOps Team",
    icon: "Zap"
  }
];

export const getRecentActivity = (count: number = 10): ActivityEvent[] => {
  return activityFeed.slice(0, count);
};

export const getActivityByType = (type: ActivityEvent['type']): ActivityEvent[] => {
  return activityFeed.filter(e => e.type === type);
};

export const getActivityBySeverity = (severity: ActivityEvent['severity']): ActivityEvent[] => {
  return activityFeed.filter(e => e.severity === severity);
};
