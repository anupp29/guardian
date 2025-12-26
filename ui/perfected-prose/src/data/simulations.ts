export interface SimulationScenario {
  id: string;
  title: string;
  targetVendor: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  blastRadius: number;
  affectedVendors: {
    id: string;
    status: 'compromised' | 'propagating' | 'affected';
    impactLevel: 'direct' | 'first_hop' | 'second_hop' | 'third_hop';
    pathFromSource: string[];
  }[];
  propagationPaths: {
    path: string[];
    delay: number;
    risk: number;
  }[];
  aiExplanation: {
    summary: string;
    keyFindings: string[];
    technicalDetails: string;
    businessImpact: string;
    estimatedRecovery: string;
  };
  metricsChange: {
    before: {
      compromisedVendors: number;
      affectedServices: number;
      criticalPathCount: number;
      overallRisk: number;
    };
    after: {
      compromisedVendors: number;
      affectedServices: number;
      criticalPathCount: number;
      overallRisk: number;
    };
  };
  timestamp: string;
}

export const simulations: SimulationScenario[] = [
  {
    id: "sim_001",
    title: "Okta Authentication Service Compromise",
    targetVendor: "vnd_auth_okta",
    severity: "critical",
    blastRadius: 42,
    affectedVendors: [
      { id: "vnd_auth_okta", status: "compromised", impactLevel: "direct", pathFromSource: ["vnd_auth_okta"] },
      { id: "vnd_data_aws", status: "propagating", impactLevel: "first_hop", pathFromSource: ["vnd_auth_okta", "vnd_data_aws"] },
      { id: "vnd_api_slack", status: "propagating", impactLevel: "first_hop", pathFromSource: ["vnd_auth_okta", "vnd_api_slack"] },
      { id: "vnd_data_snowflake", status: "propagating", impactLevel: "first_hop", pathFromSource: ["vnd_auth_okta", "vnd_data_snowflake"] },
      { id: "vnd_pay_stripe", status: "affected", impactLevel: "second_hop", pathFromSource: ["vnd_auth_okta", "vnd_data_aws", "vnd_pay_stripe"] },
      { id: "vnd_infra_datadog", status: "affected", impactLevel: "second_hop", pathFromSource: ["vnd_auth_okta", "vnd_data_aws", "vnd_infra_datadog"] },
      { id: "vnd_api_twilio", status: "affected", impactLevel: "second_hop", pathFromSource: ["vnd_auth_okta", "vnd_data_aws", "vnd_api_twilio"] },
      { id: "vnd_auth_duo", status: "propagating", impactLevel: "first_hop", pathFromSource: ["vnd_auth_okta", "vnd_auth_duo"] },
      { id: "vnd_data_looker", status: "affected", impactLevel: "second_hop", pathFromSource: ["vnd_auth_okta", "vnd_data_snowflake", "vnd_data_looker"] },
      { id: "vnd_api_segment", status: "affected", impactLevel: "second_hop", pathFromSource: ["vnd_auth_okta", "vnd_data_aws", "vnd_api_segment"] },
      { id: "vnd_infra_cloudflare", status: "affected", impactLevel: "second_hop", pathFromSource: ["vnd_auth_okta", "vnd_data_aws", "vnd_infra_cloudflare"] },
      { id: "vnd_auth_auth0", status: "affected", impactLevel: "second_hop", pathFromSource: ["vnd_auth_okta", "vnd_data_aws", "vnd_auth_auth0"] },
    ],
    propagationPaths: [
      { path: ["vnd_auth_okta", "vnd_data_aws", "vnd_pay_stripe"], delay: 300, risk: 0.95 },
      { path: ["vnd_auth_okta", "vnd_data_snowflake", "vnd_data_looker"], delay: 400, risk: 0.88 },
      { path: ["vnd_auth_okta", "vnd_api_slack", "vnd_infra_pagerduty"], delay: 350, risk: 0.82 },
      { path: ["vnd_auth_okta", "vnd_data_aws", "vnd_api_segment", "vnd_data_amplitude"], delay: 500, risk: 0.78 },
      { path: ["vnd_auth_okta", "vnd_auth_duo"], delay: 200, risk: 0.92 },
      { path: ["vnd_auth_okta", "vnd_data_aws", "vnd_infra_datadog", "vnd_api_slack"], delay: 450, risk: 0.85 },
      { path: ["vnd_auth_okta", "vnd_data_aws", "vnd_api_twilio"], delay: 350, risk: 0.80 },
    ],
    aiExplanation: {
      summary: "A compromise of Okta's authentication service would cascade through 42 dependent vendors, affecting user authentication across your entire supply chain. The attack could propagate within 15 minutes through automated API integrations, creating a critical single point of failure scenario.",
      keyFindings: [
        "Single point of failure affects 87% of critical operations",
        "No redundant authentication system currently in place",
        "Average propagation time estimated at 12 minutes",
        "Estimated business impact: $2.4M per hour of downtime",
        "7 critical propagation paths identified requiring immediate attention"
      ],
      technicalDetails: "Okta serves as the primary authentication layer for 42 downstream services. The compromise vector would propagate through OAuth tokens and SAML assertions, affecting session management across integrated services. AWS credentials derived from Okta SSO would grant lateral movement capabilities.",
      businessImpact: "Loss of authentication would immediately affect all employee access to critical systems. Customer-facing applications using Okta for SSO would become inaccessible. Payment processing through Stripe would halt due to authentication failures.",
      estimatedRecovery: "4-6 hours with emergency protocols; 24-48 hours for full security audit and credential rotation"
    },
    metricsChange: {
      before: { compromisedVendors: 0, affectedServices: 0, criticalPathCount: 0, overallRisk: 23 },
      after: { compromisedVendors: 1, affectedServices: 42, criticalPathCount: 7, overallRisk: 87 }
    },
    timestamp: "2024-12-20T10:30:00Z"
  },
  {
    id: "sim_002",
    title: "AWS Infrastructure Breach",
    targetVendor: "vnd_data_aws",
    severity: "critical",
    blastRadius: 48,
    affectedVendors: [
      { id: "vnd_data_aws", status: "compromised", impactLevel: "direct", pathFromSource: ["vnd_data_aws"] },
      { id: "vnd_data_snowflake", status: "propagating", impactLevel: "first_hop", pathFromSource: ["vnd_data_aws", "vnd_data_snowflake"] },
      { id: "vnd_pay_stripe", status: "propagating", impactLevel: "first_hop", pathFromSource: ["vnd_data_aws", "vnd_pay_stripe"] },
      { id: "vnd_infra_datadog", status: "propagating", impactLevel: "first_hop", pathFromSource: ["vnd_data_aws", "vnd_infra_datadog"] },
      { id: "vnd_api_twilio", status: "propagating", impactLevel: "first_hop", pathFromSource: ["vnd_data_aws", "vnd_api_twilio"] },
      { id: "vnd_auth_okta", status: "affected", impactLevel: "first_hop", pathFromSource: ["vnd_data_aws", "vnd_auth_okta"] },
      { id: "vnd_auth_auth0", status: "affected", impactLevel: "first_hop", pathFromSource: ["vnd_data_aws", "vnd_auth_auth0"] },
      { id: "vnd_data_mongodb", status: "affected", impactLevel: "first_hop", pathFromSource: ["vnd_data_aws", "vnd_data_mongodb"] },
      { id: "vnd_infra_cloudflare", status: "affected", impactLevel: "first_hop", pathFromSource: ["vnd_data_aws", "vnd_infra_cloudflare"] },
    ],
    propagationPaths: [
      { path: ["vnd_data_aws", "vnd_data_snowflake", "vnd_data_looker"], delay: 250, risk: 0.98 },
      { path: ["vnd_data_aws", "vnd_pay_stripe", "vnd_api_segment"], delay: 300, risk: 0.95 },
      { path: ["vnd_data_aws", "vnd_infra_datadog", "vnd_api_slack"], delay: 350, risk: 0.92 },
      { path: ["vnd_data_aws", "vnd_data_mongodb", "vnd_data_redis"], delay: 400, risk: 0.88 },
    ],
    aiExplanation: {
      summary: "An AWS infrastructure breach represents the most severe scenario in your supply chain, with 48 services directly dependent on AWS resources. This would result in complete operational paralysis across all business functions.",
      keyFindings: [
        "AWS is the foundational infrastructure layer for 96% of services",
        "Complete data exfiltration risk across all stored assets",
        "Estimated financial impact: $5.2M per hour",
        "Recovery requires complete infrastructure rebuild",
        "All encryption keys stored in AWS KMS would be compromised"
      ],
      technicalDetails: "AWS serves as the foundational infrastructure layer hosting compute, storage, and networking resources. A breach would grant access to S3 buckets containing sensitive data, EC2 instances running critical services, and RDS databases storing customer information.",
      businessImpact: "Total operational shutdown. All customer-facing services would become unavailable. Complete loss of data confidentiality including PII, financial records, and proprietary business data. Regulatory reporting requirements triggered immediately.",
      estimatedRecovery: "72-96 hours minimum for basic operations; 2-4 weeks for full recovery with new infrastructure"
    },
    metricsChange: {
      before: { compromisedVendors: 0, affectedServices: 0, criticalPathCount: 0, overallRisk: 23 },
      after: { compromisedVendors: 1, affectedServices: 48, criticalPathCount: 12, overallRisk: 98 }
    },
    timestamp: "2024-12-20T11:15:00Z"
  },
  {
    id: "sim_003",
    title: "Stripe Payment Gateway Compromise",
    targetVendor: "vnd_pay_stripe",
    severity: "high",
    blastRadius: 23,
    affectedVendors: [
      { id: "vnd_pay_stripe", status: "compromised", impactLevel: "direct", pathFromSource: ["vnd_pay_stripe"] },
      { id: "vnd_api_segment", status: "propagating", impactLevel: "first_hop", pathFromSource: ["vnd_pay_stripe", "vnd_api_segment"] },
      { id: "vnd_data_snowflake", status: "propagating", impactLevel: "first_hop", pathFromSource: ["vnd_pay_stripe", "vnd_data_snowflake"] },
      { id: "vnd_pay_braintree", status: "affected", impactLevel: "first_hop", pathFromSource: ["vnd_pay_stripe", "vnd_pay_braintree"] },
      { id: "vnd_pay_plaid", status: "affected", impactLevel: "first_hop", pathFromSource: ["vnd_pay_stripe", "vnd_pay_plaid"] },
      { id: "vnd_pay_recurly", status: "affected", impactLevel: "first_hop", pathFromSource: ["vnd_pay_stripe", "vnd_pay_recurly"] },
      { id: "vnd_pay_chargebee", status: "affected", impactLevel: "first_hop", pathFromSource: ["vnd_pay_stripe", "vnd_pay_chargebee"] },
    ],
    propagationPaths: [
      { path: ["vnd_pay_stripe", "vnd_api_segment", "vnd_data_snowflake"], delay: 300, risk: 0.88 },
      { path: ["vnd_pay_stripe", "vnd_pay_plaid", "vnd_data_snowflake"], delay: 350, risk: 0.82 },
      { path: ["vnd_pay_stripe", "vnd_api_twilio"], delay: 250, risk: 0.75 },
    ],
    aiExplanation: {
      summary: "A Stripe payment gateway compromise would immediately halt all payment processing capabilities, affecting 23 downstream services. Financial data exposure risk is critical, with potential PCI-DSS compliance violations.",
      keyFindings: [
        "All payment processing immediately halted",
        "Customer payment data potentially exposed",
        "PCI-DSS compliance breach requiring immediate notification",
        "Estimated revenue loss: $890K per hour",
        "Subscription billing for 45,000 customers affected"
      ],
      technicalDetails: "Stripe processes all payment transactions and stores tokenized payment methods. A breach would expose payment tokens, transaction histories, and customer billing information. Connected services using Stripe Connect would also be compromised.",
      businessImpact: "Immediate revenue collection halt. Customer payment methods require re-verification. Mandatory breach notification to affected customers. Potential regulatory fines for PCI-DSS non-compliance.",
      estimatedRecovery: "24-48 hours for payment processing restoration; 2-3 weeks for customer notification and card replacement"
    },
    metricsChange: {
      before: { compromisedVendors: 0, affectedServices: 0, criticalPathCount: 0, overallRisk: 23 },
      after: { compromisedVendors: 1, affectedServices: 23, criticalPathCount: 4, overallRisk: 72 }
    },
    timestamp: "2024-12-20T14:00:00Z"
  },
  {
    id: "sim_004",
    title: "Snowflake Data Warehouse Breach",
    targetVendor: "vnd_data_snowflake",
    severity: "high",
    blastRadius: 31,
    affectedVendors: [
      { id: "vnd_data_snowflake", status: "compromised", impactLevel: "direct", pathFromSource: ["vnd_data_snowflake"] },
      { id: "vnd_data_looker", status: "propagating", impactLevel: "first_hop", pathFromSource: ["vnd_data_snowflake", "vnd_data_looker"] },
      { id: "vnd_data_dbt", status: "propagating", impactLevel: "first_hop", pathFromSource: ["vnd_data_snowflake", "vnd_data_dbt"] },
      { id: "vnd_data_metabase", status: "affected", impactLevel: "first_hop", pathFromSource: ["vnd_data_snowflake", "vnd_data_metabase"] },
      { id: "vnd_data_fivetran", status: "affected", impactLevel: "first_hop", pathFromSource: ["vnd_data_snowflake", "vnd_data_fivetran"] },
      { id: "vnd_data_databricks", status: "affected", impactLevel: "first_hop", pathFromSource: ["vnd_data_snowflake", "vnd_data_databricks"] },
    ],
    propagationPaths: [
      { path: ["vnd_data_snowflake", "vnd_data_looker", "vnd_auth_okta"], delay: 300, risk: 0.85 },
      { path: ["vnd_data_snowflake", "vnd_data_dbt"], delay: 200, risk: 0.92 },
      { path: ["vnd_data_snowflake", "vnd_data_databricks"], delay: 350, risk: 0.78 },
    ],
    aiExplanation: {
      summary: "A Snowflake data warehouse breach would expose the entire analytical data layer containing aggregated business intelligence. 31 downstream analytics and reporting services would be affected, with significant data exfiltration risk.",
      keyFindings: [
        "Complete business intelligence data potentially exposed",
        "5 years of historical transaction data at risk",
        "Customer behavioral analytics compromised",
        "Competitive intelligence data vulnerable",
        "GDPR/CCPA breach notification requirements triggered"
      ],
      technicalDetails: "Snowflake contains the consolidated data warehouse with data from all operational systems. This includes customer PII, financial analytics, product usage metrics, and proprietary business algorithms.",
      businessImpact: "Competitive advantage loss through data exposure. Regulatory fines for data protection failures. Customer trust erosion. Potential lawsuits from affected data subjects.",
      estimatedRecovery: "48-72 hours for access revocation and audit; 1-2 weeks for data integrity verification"
    },
    metricsChange: {
      before: { compromisedVendors: 0, affectedServices: 0, criticalPathCount: 0, overallRisk: 23 },
      after: { compromisedVendors: 1, affectedServices: 31, criticalPathCount: 5, overallRisk: 76 }
    },
    timestamp: "2024-12-20T15:30:00Z"
  },
  {
    id: "sim_005",
    title: "Segment Analytics Pipeline Compromise",
    targetVendor: "vnd_api_segment",
    severity: "medium",
    blastRadius: 15,
    affectedVendors: [
      { id: "vnd_api_segment", status: "compromised", impactLevel: "direct", pathFromSource: ["vnd_api_segment"] },
      { id: "vnd_data_snowflake", status: "propagating", impactLevel: "first_hop", pathFromSource: ["vnd_api_segment", "vnd_data_snowflake"] },
      { id: "vnd_api_mixpanel", status: "propagating", impactLevel: "first_hop", pathFromSource: ["vnd_api_segment", "vnd_api_mixpanel"] },
      { id: "vnd_data_amplitude", status: "affected", impactLevel: "first_hop", pathFromSource: ["vnd_api_segment", "vnd_data_amplitude"] },
      { id: "vnd_api_intercom", status: "affected", impactLevel: "first_hop", pathFromSource: ["vnd_api_segment", "vnd_api_intercom"] },
      { id: "vnd_data_heap", status: "affected", impactLevel: "first_hop", pathFromSource: ["vnd_api_segment", "vnd_data_heap"] },
    ],
    propagationPaths: [
      { path: ["vnd_api_segment", "vnd_data_snowflake", "vnd_data_looker"], delay: 400, risk: 0.72 },
      { path: ["vnd_api_segment", "vnd_api_mixpanel"], delay: 250, risk: 0.68 },
      { path: ["vnd_api_segment", "vnd_data_amplitude"], delay: 300, risk: 0.65 },
    ],
    aiExplanation: {
      summary: "A Segment analytics pipeline compromise would affect customer data collection and distribution to 15 downstream analytics services. While not immediately operational, it poses significant privacy and data integrity risks.",
      keyFindings: [
        "Customer tracking data potentially manipulated",
        "Analytics integrity compromised across all platforms",
        "User behavioral patterns exposed",
        "Marketing attribution data unreliable",
        "A/B testing results potentially corrupted"
      ],
      technicalDetails: "Segment acts as the central customer data platform, routing events to multiple analytics destinations. A compromise could allow injection of false data or exfiltration of user behavior patterns.",
      businessImpact: "Business decisions based on corrupted analytics. Marketing spend misallocation. Product development misdirection based on false user signals. Privacy violations through tracking data exposure.",
      estimatedRecovery: "12-24 hours for pipeline restoration; 1-2 weeks for data integrity audit"
    },
    metricsChange: {
      before: { compromisedVendors: 0, affectedServices: 0, criticalPathCount: 0, overallRisk: 23 },
      after: { compromisedVendors: 1, affectedServices: 15, criticalPathCount: 3, overallRisk: 54 }
    },
    timestamp: "2024-12-20T16:45:00Z"
  }
];

export const getSimulationById = (id: string): SimulationScenario | undefined => {
  return simulations.find(s => s.id === id);
};

export const getSimulationByVendor = (vendorId: string): SimulationScenario | undefined => {
  return simulations.find(s => s.targetVendor === vendorId);
};
