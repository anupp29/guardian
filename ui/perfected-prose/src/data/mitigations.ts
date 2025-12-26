export interface Mitigation {
  id: string;
  title: string;
  riskReduction: number;
  effectiveness: 'very_high' | 'high' | 'medium' | 'low';
  implementationTime: string;
  cost: '$' | '$$' | '$$$';
  priority: number;
  affectedVendors: number;
  category: string;
  description: string;
  technicalDetails: string;
  businessJustification: string;
  dependencies: string[];
  effort: {
    engineering: string;
    testing: string;
    deployment: string;
  };
  prerequisites: string[];
  successMetrics: string[];
}

export const mitigations: Mitigation[] = [
  {
    id: "mit_001",
    title: "Implement Multi-Factor Authentication Redundancy",
    riskReduction: 68,
    effectiveness: "very_high",
    implementationTime: "2 weeks",
    cost: "$$",
    priority: 1,
    affectedVendors: 15,
    category: "authentication",
    description: "Deploy secondary authentication provider (Auth0) as failover system. Automatically switches if Okta experiences disruption, maintaining continuous authentication services.",
    technicalDetails: "Configure Auth0 as backup IdP with real-time health monitoring. Implement automatic failover with <30 second transition time. Maintain user session continuity through token synchronization. Deploy health check endpoints every 10 seconds.",
    businessJustification: "Eliminates single point of failure for authentication, protecting 87% of critical operations. Reduces potential downtime cost from $2.4M/hour to near-zero. Meets SOC2 redundancy requirements.",
    dependencies: ["vnd_auth_okta", "vnd_auth_auth0"],
    effort: {
      engineering: "3 person-weeks",
      testing: "1 week",
      deployment: "3 days"
    },
    prerequisites: ["Auth0 enterprise contract", "SSO protocol alignment", "User directory sync"],
    successMetrics: [
      "Failover time < 30 seconds",
      "Zero authentication disruptions during tests",
      "95% user satisfaction maintained",
      "100% session continuity during failover"
    ]
  },
  {
    id: "mit_002",
    title: "Deploy Multi-Region Infrastructure Redundancy",
    riskReduction: 62,
    effectiveness: "very_high",
    implementationTime: "4 weeks",
    cost: "$$$",
    priority: 2,
    affectedVendors: 48,
    category: "infrastructure",
    description: "Establish active-active multi-region AWS deployment with automatic failover. Eliminates single-region dependency and provides geographic redundancy for disaster recovery.",
    technicalDetails: "Deploy identical infrastructure stacks in us-east-1 and eu-west-1. Configure Route53 health checks with 10-second intervals. Implement database replication with <1 second lag. Use Global Accelerator for traffic management.",
    businessJustification: "Reduces AWS single-point-of-failure risk by 95%. Provides compliance with data residency requirements. Improves global performance by 40%. Estimated ROI of 850% over 3 years based on downtime prevention.",
    dependencies: ["vnd_data_aws"],
    effort: {
      engineering: "8 person-weeks",
      testing: "2 weeks",
      deployment: "1 week"
    },
    prerequisites: ["Budget approval for 2x infrastructure cost", "Cross-region database licensing", "Updated disaster recovery runbooks"],
    successMetrics: [
      "Region failover < 60 seconds",
      "99.99% uptime achieved",
      "Database replication lag < 1 second",
      "Zero data loss during failover"
    ]
  },
  {
    id: "mit_003",
    title: "Implement Zero Trust Network Architecture",
    riskReduction: 55,
    effectiveness: "very_high",
    implementationTime: "6 weeks",
    cost: "$$$",
    priority: 3,
    affectedVendors: 42,
    category: "security",
    description: "Replace perimeter-based security with zero trust model. Every request is authenticated and authorized regardless of network location, limiting lateral movement in case of breach.",
    technicalDetails: "Deploy Cloudflare Access for all internal applications. Implement device posture checks. Require MFA for all service-to-service communication. Enable micro-segmentation at the application layer. Deploy mTLS for all internal APIs.",
    businessJustification: "Limits breach blast radius by 85%. Meets NIST 800-207 zero trust guidelines. Reduces audit preparation time by 60%. Enables secure remote work without VPN.",
    dependencies: ["vnd_infra_cloudflare", "vnd_auth_okta"],
    effort: {
      engineering: "10 person-weeks",
      testing: "3 weeks",
      deployment: "2 weeks"
    },
    prerequisites: ["Application inventory complete", "Identity provider integration", "Service mesh deployment"],
    successMetrics: [
      "100% applications behind zero trust proxy",
      "Lateral movement time increased to >24 hours",
      "Zero VPN-related security incidents",
      "90% reduction in network attack surface"
    ]
  },
  {
    id: "mit_004",
    title: "Establish Payment Processing Redundancy",
    riskReduction: 45,
    effectiveness: "high",
    implementationTime: "3 weeks",
    cost: "$$",
    priority: 4,
    affectedVendors: 8,
    category: "payment",
    description: "Configure Adyen as backup payment processor with automatic routing during Stripe outages. Maintains revenue collection capability during payment infrastructure disruptions.",
    technicalDetails: "Implement payment abstraction layer supporting multiple processors. Configure real-time health monitoring with 5-second intervals. Maintain payment method tokens across both providers. Enable smart routing based on transaction type and geography.",
    businessJustification: "Protects $890K/hour revenue stream. Reduces payment processing single-point-of-failure. Improves international transaction success rates. Provides negotiating leverage with payment providers.",
    dependencies: ["vnd_pay_stripe", "vnd_pay_adyen"],
    effort: {
      engineering: "4 person-weeks",
      testing: "1.5 weeks",
      deployment: "4 days"
    },
    prerequisites: ["Adyen merchant account", "PCI-DSS scope expansion approval", "Payment team training"],
    successMetrics: [
      "Payment failover < 15 seconds",
      "99.95% transaction success rate",
      "Zero revenue loss during processor outages",
      "Customer payment method continuity maintained"
    ]
  },
  {
    id: "mit_005",
    title: "Deploy Data Loss Prevention Controls",
    riskReduction: 42,
    effectiveness: "high",
    implementationTime: "3 weeks",
    cost: "$$",
    priority: 5,
    affectedVendors: 25,
    category: "data",
    description: "Implement comprehensive DLP controls across all data storage and transmission points. Detect and prevent unauthorized data exfiltration in real-time.",
    technicalDetails: "Deploy Cloudflare DLP policies for all outbound traffic. Implement AWS Macie for S3 bucket monitoring. Configure Snowflake data masking for sensitive columns. Enable real-time alerting on anomalous data access patterns.",
    businessJustification: "Reduces data breach impact by 75%. Meets GDPR Article 32 security requirements. Provides evidence for compliance audits. Reduces cyber insurance premiums by estimated 20%.",
    dependencies: ["vnd_infra_cloudflare", "vnd_data_aws", "vnd_data_snowflake"],
    effort: {
      engineering: "5 person-weeks",
      testing: "1.5 weeks",
      deployment: "1 week"
    },
    prerequisites: ["Data classification complete", "Sensitive data inventory", "DLP policy definitions"],
    successMetrics: [
      "100% sensitive data classified",
      "< 0.1% false positive rate on DLP alerts",
      "Zero unauthorized data exports",
      "Audit evidence generation automated"
    ]
  },
  {
    id: "mit_006",
    title: "Implement Real-Time Threat Detection",
    riskReduction: 38,
    effectiveness: "high",
    implementationTime: "2 weeks",
    cost: "$$",
    priority: 6,
    affectedVendors: 35,
    category: "monitoring",
    description: "Deploy advanced threat detection across all infrastructure layers with automated response capabilities. Reduce mean time to detect from hours to minutes.",
    technicalDetails: "Integrate Datadog Security Monitoring with custom detection rules. Deploy UEBA (User Entity Behavior Analytics) across authentication logs. Configure automated incident creation in PagerDuty. Implement honeypot services for early breach detection.",
    businessJustification: "Reduces breach dwell time by 90%. Provides 24/7 automated monitoring. Meets SOC2 continuous monitoring requirements. Reduces incident response costs by 60%.",
    dependencies: ["vnd_infra_datadog", "vnd_infra_pagerduty", "vnd_auth_okta"],
    effort: {
      engineering: "3 person-weeks",
      testing: "1 week",
      deployment: "3 days"
    },
    prerequisites: ["Log aggregation complete", "Detection rule library", "Incident response playbooks"],
    successMetrics: [
      "Mean time to detect < 5 minutes",
      "90% automated alert triage",
      "< 5% alert fatigue rate",
      "Zero critical threats missed"
    ]
  },
  {
    id: "mit_007",
    title: "Establish Vendor Security Scoring Program",
    riskReduction: 28,
    effectiveness: "medium",
    implementationTime: "4 weeks",
    cost: "$",
    priority: 7,
    affectedVendors: 50,
    category: "governance",
    description: "Implement continuous vendor security assessment program with automated scoring. Identify high-risk vendors before they become attack vectors.",
    technicalDetails: "Deploy SecurityScorecard API integration for continuous monitoring. Implement quarterly security questionnaire automation. Configure risk-based vendor tiering with SLA requirements. Create vendor offboarding playbook for high-risk situations.",
    businessJustification: "Proactively identifies 80% of supply chain risks. Reduces vendor security review time by 70%. Provides board-level risk visibility. Meets third-party risk management compliance requirements.",
    dependencies: [],
    effort: {
      engineering: "2 person-weeks",
      testing: "1 week",
      deployment: "1 week"
    },
    prerequisites: ["Vendor inventory complete", "Risk tolerance thresholds defined", "Stakeholder buy-in"],
    successMetrics: [
      "100% vendors continuously monitored",
      "Average vendor score improvement of 15%",
      "Zero high-risk vendor surprises",
      "Quarterly board reporting automated"
    ]
  },
  {
    id: "mit_008",
    title: "Create Incident Response Automation",
    riskReduction: 22,
    effectiveness: "medium",
    implementationTime: "2 weeks",
    cost: "$",
    priority: 8,
    affectedVendors: 30,
    category: "operations",
    description: "Automate incident response workflows to reduce human response time. Enable rapid containment and recovery during security events.",
    technicalDetails: "Deploy PagerDuty automated incident workflows. Implement Slack-based war room creation. Configure automatic access revocation playbooks. Enable one-click service isolation capabilities.",
    businessJustification: "Reduces mean time to respond by 75%. Enables 24/7 response without human on-call. Ensures consistent incident handling. Reduces incident escalation costs by 50%.",
    dependencies: ["vnd_infra_pagerduty", "vnd_api_slack"],
    effort: {
      engineering: "2 person-weeks",
      testing: "1 week",
      deployment: "3 days"
    },
    prerequisites: ["Incident classification matrix", "Escalation policies defined", "Runbook library"],
    successMetrics: [
      "Mean time to respond < 10 minutes",
      "80% incidents auto-triaged",
      "Zero missed P1 incidents",
      "Incident retrospective completion rate 100%"
    ]
  }
];

export const getMitigationById = (id: string): Mitigation | undefined => {
  return mitigations.find(m => m.id === id);
};

export const getMitigationsByCategory = (category: string): Mitigation[] => {
  return mitigations.filter(m => m.category === category);
};

export const getMitigationsByEffectiveness = (effectiveness: Mitigation['effectiveness']): Mitigation[] => {
  return mitigations.filter(m => m.effectiveness === effectiveness);
};
