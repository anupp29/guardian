export interface Vendor {
  id: string;
  name: string;
  category: 'authentication' | 'payment' | 'data' | 'api' | 'infrastructure';
  tier: 1 | 2 | 3;
  riskScore: number;
  status: 'secure' | 'warning' | 'compromised';
  metadata: {
    contractType: string;
    lastAudit: string;
    certifications: string[];
    criticalityScore: number;
    employeeAccess: number;
    dataCategories: string[];
  };
}

export const vendors: Vendor[] = [
  // Tier 1 - Critical (5 vendors)
  {
    id: "vnd_auth_okta",
    name: "Okta",
    category: "authentication",
    tier: 1,
    riskScore: 15,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-11-15",
      certifications: ["SOC2", "ISO27001", "FedRAMP"],
      criticalityScore: 95,
      employeeAccess: 2840,
      dataCategories: ["authentication", "user_identity"]
    }
  },
  {
    id: "vnd_pay_stripe",
    name: "Stripe",
    category: "payment",
    tier: 1,
    riskScore: 12,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-10-20",
      certifications: ["PCI-DSS", "SOC2", "ISO27001"],
      criticalityScore: 98,
      employeeAccess: 450,
      dataCategories: ["payment", "financial"]
    }
  },
  {
    id: "vnd_data_aws",
    name: "AWS",
    category: "infrastructure",
    tier: 1,
    riskScore: 8,
    status: "secure",
    metadata: {
      contractType: "enterprise",
      lastAudit: "2024-12-01",
      certifications: ["SOC2", "ISO27001", "FedRAMP", "HIPAA"],
      criticalityScore: 99,
      employeeAccess: 120,
      dataCategories: ["infrastructure", "storage", "compute"]
    }
  },
  {
    id: "vnd_data_snowflake",
    name: "Snowflake",
    category: "data",
    tier: 1,
    riskScore: 18,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-09-15",
      certifications: ["SOC2", "ISO27001", "HIPAA"],
      criticalityScore: 92,
      employeeAccess: 85,
      dataCategories: ["analytics", "data_warehouse"]
    }
  },
  {
    id: "vnd_api_twilio",
    name: "Twilio",
    category: "api",
    tier: 1,
    riskScore: 22,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-08-30",
      certifications: ["SOC2", "ISO27001"],
      criticalityScore: 88,
      employeeAccess: 340,
      dataCategories: ["communications", "sms", "voice"]
    }
  },
  
  // Tier 2 - Important (15 vendors)
  {
    id: "vnd_auth_auth0",
    name: "Auth0",
    category: "authentication",
    tier: 2,
    riskScore: 25,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-07-20",
      certifications: ["SOC2", "ISO27001"],
      criticalityScore: 75,
      employeeAccess: 180,
      dataCategories: ["authentication"]
    }
  },
  {
    id: "vnd_pay_adyen",
    name: "Adyen",
    category: "payment",
    tier: 2,
    riskScore: 28,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-06-15",
      certifications: ["PCI-DSS", "SOC2"],
      criticalityScore: 72,
      employeeAccess: 95,
      dataCategories: ["payment"]
    }
  },
  {
    id: "vnd_data_mongodb",
    name: "MongoDB Atlas",
    category: "data",
    tier: 2,
    riskScore: 32,
    status: "warning",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-05-10",
      certifications: ["SOC2", "ISO27001"],
      criticalityScore: 78,
      employeeAccess: 65,
      dataCategories: ["database", "storage"]
    }
  },
  {
    id: "vnd_api_sendgrid",
    name: "SendGrid",
    category: "api",
    tier: 2,
    riskScore: 35,
    status: "secure",
    metadata: {
      contractType: "monthly",
      lastAudit: "2024-04-22",
      certifications: ["SOC2"],
      criticalityScore: 68,
      employeeAccess: 420,
      dataCategories: ["email", "communications"]
    }
  },
  {
    id: "vnd_infra_cloudflare",
    name: "Cloudflare",
    category: "infrastructure",
    tier: 2,
    riskScore: 14,
    status: "secure",
    metadata: {
      contractType: "enterprise",
      lastAudit: "2024-11-01",
      certifications: ["SOC2", "ISO27001", "PCI-DSS"],
      criticalityScore: 85,
      employeeAccess: 25,
      dataCategories: ["cdn", "security", "dns"]
    }
  },
  {
    id: "vnd_data_redis",
    name: "Redis Enterprise",
    category: "data",
    tier: 2,
    riskScore: 38,
    status: "warning",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-03-18",
      certifications: ["SOC2"],
      criticalityScore: 65,
      employeeAccess: 45,
      dataCategories: ["cache", "database"]
    }
  },
  {
    id: "vnd_api_segment",
    name: "Segment",
    category: "api",
    tier: 2,
    riskScore: 42,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-02-28",
      certifications: ["SOC2", "GDPR"],
      criticalityScore: 62,
      employeeAccess: 280,
      dataCategories: ["analytics", "tracking"]
    }
  },
  {
    id: "vnd_infra_datadog",
    name: "Datadog",
    category: "infrastructure",
    tier: 2,
    riskScore: 20,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-10-05",
      certifications: ["SOC2", "ISO27001"],
      criticalityScore: 70,
      employeeAccess: 95,
      dataCategories: ["monitoring", "observability"]
    }
  },
  {
    id: "vnd_pay_plaid",
    name: "Plaid",
    category: "payment",
    tier: 2,
    riskScore: 45,
    status: "warning",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-01-20",
      certifications: ["SOC2", "ISO27001"],
      criticalityScore: 80,
      employeeAccess: 120,
      dataCategories: ["financial", "banking"]
    }
  },
  {
    id: "vnd_auth_onelogin",
    name: "OneLogin",
    category: "authentication",
    tier: 2,
    riskScore: 48,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2023-12-15",
      certifications: ["SOC2"],
      criticalityScore: 58,
      employeeAccess: 890,
      dataCategories: ["authentication", "sso"]
    }
  },
  {
    id: "vnd_data_elasticsearch",
    name: "Elastic Cloud",
    category: "data",
    tier: 2,
    riskScore: 30,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-08-12",
      certifications: ["SOC2", "ISO27001"],
      criticalityScore: 66,
      employeeAccess: 55,
      dataCategories: ["search", "logging"]
    }
  },
  {
    id: "vnd_api_slack",
    name: "Slack",
    category: "api",
    tier: 2,
    riskScore: 26,
    status: "secure",
    metadata: {
      contractType: "enterprise",
      lastAudit: "2024-09-28",
      certifications: ["SOC2", "ISO27001", "HIPAA"],
      criticalityScore: 74,
      employeeAccess: 2200,
      dataCategories: ["communications", "collaboration"]
    }
  },
  {
    id: "vnd_infra_pagerduty",
    name: "PagerDuty",
    category: "infrastructure",
    tier: 2,
    riskScore: 33,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-07-08",
      certifications: ["SOC2"],
      criticalityScore: 64,
      employeeAccess: 180,
      dataCategories: ["alerting", "incident"]
    }
  },
  {
    id: "vnd_pay_braintree",
    name: "Braintree",
    category: "payment",
    tier: 2,
    riskScore: 24,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-06-30",
      certifications: ["PCI-DSS", "SOC2"],
      criticalityScore: 76,
      employeeAccess: 75,
      dataCategories: ["payment", "subscriptions"]
    }
  },
  {
    id: "vnd_data_confluent",
    name: "Confluent",
    category: "data",
    tier: 2,
    riskScore: 36,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-05-25",
      certifications: ["SOC2", "ISO27001"],
      criticalityScore: 68,
      employeeAccess: 40,
      dataCategories: ["streaming", "kafka"]
    }
  },
  
  // Tier 3 - Standard (30 vendors)
  {
    id: "vnd_api_zapier",
    name: "Zapier",
    category: "api",
    tier: 3,
    riskScore: 52,
    status: "warning",
    metadata: {
      contractType: "monthly",
      lastAudit: "2023-11-10",
      certifications: ["SOC2"],
      criticalityScore: 45,
      employeeAccess: 650,
      dataCategories: ["automation", "integration"]
    }
  },
  {
    id: "vnd_api_intercom",
    name: "Intercom",
    category: "api",
    tier: 3,
    riskScore: 44,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-04-15",
      certifications: ["SOC2", "GDPR"],
      criticalityScore: 52,
      employeeAccess: 320,
      dataCategories: ["support", "messaging"]
    }
  },
  {
    id: "vnd_data_amplitude",
    name: "Amplitude",
    category: "data",
    tier: 3,
    riskScore: 48,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-03-20",
      certifications: ["SOC2"],
      criticalityScore: 48,
      employeeAccess: 145,
      dataCategories: ["analytics", "product"]
    }
  },
  {
    id: "vnd_infra_vercel",
    name: "Vercel",
    category: "infrastructure",
    tier: 3,
    riskScore: 28,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-08-05",
      certifications: ["SOC2"],
      criticalityScore: 55,
      employeeAccess: 35,
      dataCategories: ["hosting", "deployment"]
    }
  },
  {
    id: "vnd_api_mixpanel",
    name: "Mixpanel",
    category: "api",
    tier: 3,
    riskScore: 46,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-02-10",
      certifications: ["SOC2", "GDPR"],
      criticalityScore: 50,
      employeeAccess: 165,
      dataCategories: ["analytics", "events"]
    }
  },
  {
    id: "vnd_pay_recurly",
    name: "Recurly",
    category: "payment",
    tier: 3,
    riskScore: 55,
    status: "warning",
    metadata: {
      contractType: "annual",
      lastAudit: "2023-10-25",
      certifications: ["PCI-DSS"],
      criticalityScore: 42,
      employeeAccess: 60,
      dataCategories: ["subscriptions", "billing"]
    }
  },
  {
    id: "vnd_auth_duo",
    name: "Duo Security",
    category: "authentication",
    tier: 3,
    riskScore: 22,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-09-10",
      certifications: ["SOC2", "FedRAMP"],
      criticalityScore: 58,
      employeeAccess: 1200,
      dataCategories: ["mfa", "security"]
    }
  },
  {
    id: "vnd_data_looker",
    name: "Looker",
    category: "data",
    tier: 3,
    riskScore: 34,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-07-18",
      certifications: ["SOC2", "ISO27001"],
      criticalityScore: 54,
      employeeAccess: 75,
      dataCategories: ["bi", "visualization"]
    }
  },
  {
    id: "vnd_infra_netlify",
    name: "Netlify",
    category: "infrastructure",
    tier: 3,
    riskScore: 38,
    status: "secure",
    metadata: {
      contractType: "monthly",
      lastAudit: "2024-05-08",
      certifications: ["SOC2"],
      criticalityScore: 46,
      employeeAccess: 28,
      dataCategories: ["hosting", "serverless"]
    }
  },
  {
    id: "vnd_api_hubspot",
    name: "HubSpot",
    category: "api",
    tier: 3,
    riskScore: 40,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-04-28",
      certifications: ["SOC2", "GDPR"],
      criticalityScore: 56,
      employeeAccess: 480,
      dataCategories: ["crm", "marketing"]
    }
  },
  {
    id: "vnd_data_fivetran",
    name: "Fivetran",
    category: "data",
    tier: 3,
    riskScore: 50,
    status: "warning",
    metadata: {
      contractType: "annual",
      lastAudit: "2023-12-20",
      certifications: ["SOC2"],
      criticalityScore: 44,
      employeeAccess: 35,
      dataCategories: ["etl", "integration"]
    }
  },
  {
    id: "vnd_pay_chargebee",
    name: "Chargebee",
    category: "payment",
    tier: 3,
    riskScore: 42,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-03-12",
      certifications: ["PCI-DSS", "SOC2"],
      criticalityScore: 48,
      employeeAccess: 55,
      dataCategories: ["billing", "subscriptions"]
    }
  },
  {
    id: "vnd_infra_sentry",
    name: "Sentry",
    category: "infrastructure",
    tier: 3,
    riskScore: 32,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-06-22",
      certifications: ["SOC2"],
      criticalityScore: 52,
      employeeAccess: 85,
      dataCategories: ["errors", "monitoring"]
    }
  },
  {
    id: "vnd_api_zendesk",
    name: "Zendesk",
    category: "api",
    tier: 3,
    riskScore: 36,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-05-30",
      certifications: ["SOC2", "ISO27001"],
      criticalityScore: 50,
      employeeAccess: 390,
      dataCategories: ["support", "ticketing"]
    }
  },
  {
    id: "vnd_data_dbt",
    name: "dbt Cloud",
    category: "data",
    tier: 3,
    riskScore: 44,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-02-25",
      certifications: ["SOC2"],
      criticalityScore: 46,
      employeeAccess: 30,
      dataCategories: ["transformation", "analytics"]
    }
  },
  {
    id: "vnd_auth_ping",
    name: "Ping Identity",
    category: "authentication",
    tier: 3,
    riskScore: 30,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-08-20",
      certifications: ["SOC2", "ISO27001"],
      criticalityScore: 54,
      employeeAccess: 560,
      dataCategories: ["sso", "identity"]
    }
  },
  {
    id: "vnd_infra_circleci",
    name: "CircleCI",
    category: "infrastructure",
    tier: 3,
    riskScore: 58,
    status: "warning",
    metadata: {
      contractType: "monthly",
      lastAudit: "2023-09-15",
      certifications: ["SOC2"],
      criticalityScore: 40,
      employeeAccess: 65,
      dataCategories: ["ci/cd", "deployment"]
    }
  },
  {
    id: "vnd_api_launchdarkly",
    name: "LaunchDarkly",
    category: "api",
    tier: 3,
    riskScore: 38,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-07-05",
      certifications: ["SOC2"],
      criticalityScore: 48,
      employeeAccess: 95,
      dataCategories: ["feature_flags", "experimentation"]
    }
  },
  {
    id: "vnd_data_heap",
    name: "Heap",
    category: "data",
    tier: 3,
    riskScore: 52,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2023-11-28",
      certifications: ["SOC2"],
      criticalityScore: 42,
      employeeAccess: 110,
      dataCategories: ["analytics", "behavioral"]
    }
  },
  {
    id: "vnd_pay_paddle",
    name: "Paddle",
    category: "payment",
    tier: 3,
    riskScore: 46,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-01-15",
      certifications: ["PCI-DSS"],
      criticalityScore: 44,
      employeeAccess: 40,
      dataCategories: ["payments", "saas"]
    }
  },
  {
    id: "vnd_infra_terraform",
    name: "Terraform Cloud",
    category: "infrastructure",
    tier: 3,
    riskScore: 26,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-09-05",
      certifications: ["SOC2"],
      criticalityScore: 56,
      employeeAccess: 25,
      dataCategories: ["iac", "provisioning"]
    }
  },
  {
    id: "vnd_api_postman",
    name: "Postman",
    category: "api",
    tier: 3,
    riskScore: 34,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-06-10",
      certifications: ["SOC2"],
      criticalityScore: 38,
      employeeAccess: 180,
      dataCategories: ["api_development", "testing"]
    }
  },
  {
    id: "vnd_data_metabase",
    name: "Metabase",
    category: "data",
    tier: 3,
    riskScore: 56,
    status: "warning",
    metadata: {
      contractType: "monthly",
      lastAudit: "2023-08-20",
      certifications: ["SOC2"],
      criticalityScore: 36,
      employeeAccess: 125,
      dataCategories: ["bi", "reporting"]
    }
  },
  {
    id: "vnd_auth_jumpcloud",
    name: "JumpCloud",
    category: "authentication",
    tier: 3,
    riskScore: 40,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-04-08",
      certifications: ["SOC2", "ISO27001"],
      criticalityScore: 50,
      employeeAccess: 720,
      dataCategories: ["directory", "identity"]
    }
  },
  {
    id: "vnd_infra_sumo",
    name: "Sumo Logic",
    category: "infrastructure",
    tier: 3,
    riskScore: 42,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-03-25",
      certifications: ["SOC2", "FedRAMP"],
      criticalityScore: 48,
      employeeAccess: 70,
      dataCategories: ["logging", "siem"]
    }
  },
  {
    id: "vnd_api_airtable",
    name: "Airtable",
    category: "api",
    tier: 3,
    riskScore: 48,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-02-18",
      certifications: ["SOC2"],
      criticalityScore: 44,
      employeeAccess: 285,
      dataCategories: ["database", "collaboration"]
    }
  },
  {
    id: "vnd_data_databricks",
    name: "Databricks",
    category: "data",
    tier: 3,
    riskScore: 24,
    status: "secure",
    metadata: {
      contractType: "enterprise",
      lastAudit: "2024-10-12",
      certifications: ["SOC2", "ISO27001", "HIPAA"],
      criticalityScore: 62,
      employeeAccess: 45,
      dataCategories: ["analytics", "ml"]
    }
  },
  {
    id: "vnd_pay_square",
    name: "Square",
    category: "payment",
    tier: 3,
    riskScore: 30,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-07-28",
      certifications: ["PCI-DSS", "SOC2"],
      criticalityScore: 52,
      employeeAccess: 85,
      dataCategories: ["payments", "pos"]
    }
  },
  {
    id: "vnd_infra_newrelic",
    name: "New Relic",
    category: "infrastructure",
    tier: 3,
    riskScore: 36,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-05-18",
      certifications: ["SOC2", "ISO27001"],
      criticalityScore: 50,
      employeeAccess: 80,
      dataCategories: ["apm", "observability"]
    }
  },
  {
    id: "vnd_api_algolia",
    name: "Algolia",
    category: "api",
    tier: 3,
    riskScore: 32,
    status: "secure",
    metadata: {
      contractType: "annual",
      lastAudit: "2024-06-28",
      certifications: ["SOC2", "GDPR"],
      criticalityScore: 46,
      employeeAccess: 55,
      dataCategories: ["search", "discovery"]
    }
  }
];

export const getVendorById = (id: string): Vendor | undefined => {
  return vendors.find(v => v.id === id);
};

export const getVendorsByCategory = (category: Vendor['category']): Vendor[] => {
  return vendors.filter(v => v.category === category);
};

export const getVendorsByTier = (tier: Vendor['tier']): Vendor[] => {
  return vendors.filter(v => v.tier === tier);
};

export const getHighRiskVendors = (): Vendor[] => {
  return vendors.filter(v => v.riskScore >= 40 || v.status === 'warning');
};
