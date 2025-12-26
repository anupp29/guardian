export interface Dependency {
  id: string;
  source: string;
  target: string;
  type: 'depends_on' | 'integrates_with' | 'supplies';
  category: 'data_flow' | 'authentication' | 'api_call' | 'infrastructure';
  strength: number;
  metadata: {
    lastVerified: string;
    dataVolume: 'low' | 'medium' | 'high';
    criticality: 'low' | 'medium' | 'high';
  };
}

export const dependencies: Dependency[] = [
  // Okta dependencies (authentication hub)
  { id: "dep_001", source: "vnd_auth_okta", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.95, metadata: { lastVerified: "2024-12-01", dataVolume: "high", criticality: "high" }},
  { id: "dep_002", source: "vnd_auth_okta", target: "vnd_api_slack", type: "integrates_with", category: "api_call", strength: 0.75, metadata: { lastVerified: "2024-11-20", dataVolume: "medium", criticality: "medium" }},
  { id: "dep_003", source: "vnd_auth_okta", target: "vnd_infra_datadog", type: "integrates_with", category: "data_flow", strength: 0.6, metadata: { lastVerified: "2024-11-15", dataVolume: "low", criticality: "low" }},
  { id: "dep_004", source: "vnd_auth_okta", target: "vnd_data_snowflake", type: "integrates_with", category: "authentication", strength: 0.85, metadata: { lastVerified: "2024-12-05", dataVolume: "low", criticality: "high" }},
  
  // Stripe dependencies (payment hub)
  { id: "dep_005", source: "vnd_pay_stripe", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.92, metadata: { lastVerified: "2024-12-10", dataVolume: "high", criticality: "high" }},
  { id: "dep_006", source: "vnd_pay_stripe", target: "vnd_auth_okta", type: "depends_on", category: "authentication", strength: 0.88, metadata: { lastVerified: "2024-12-01", dataVolume: "medium", criticality: "high" }},
  { id: "dep_007", source: "vnd_pay_stripe", target: "vnd_api_segment", type: "integrates_with", category: "data_flow", strength: 0.7, metadata: { lastVerified: "2024-11-25", dataVolume: "high", criticality: "medium" }},
  { id: "dep_008", source: "vnd_pay_stripe", target: "vnd_data_snowflake", type: "supplies", category: "data_flow", strength: 0.8, metadata: { lastVerified: "2024-12-08", dataVolume: "high", criticality: "high" }},
  
  // AWS dependencies (infrastructure hub)
  { id: "dep_009", source: "vnd_data_snowflake", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.98, metadata: { lastVerified: "2024-12-15", dataVolume: "high", criticality: "high" }},
  { id: "dep_010", source: "vnd_infra_datadog", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.9, metadata: { lastVerified: "2024-12-12", dataVolume: "high", criticality: "high" }},
  { id: "dep_011", source: "vnd_infra_cloudflare", target: "vnd_data_aws", type: "integrates_with", category: "infrastructure", strength: 0.85, metadata: { lastVerified: "2024-12-01", dataVolume: "high", criticality: "high" }},
  
  // Twilio dependencies
  { id: "dep_012", source: "vnd_api_twilio", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.88, metadata: { lastVerified: "2024-11-28", dataVolume: "high", criticality: "high" }},
  { id: "dep_013", source: "vnd_api_twilio", target: "vnd_auth_okta", type: "depends_on", category: "authentication", strength: 0.75, metadata: { lastVerified: "2024-11-20", dataVolume: "low", criticality: "medium" }},
  { id: "dep_014", source: "vnd_api_twilio", target: "vnd_api_segment", type: "integrates_with", category: "data_flow", strength: 0.65, metadata: { lastVerified: "2024-11-15", dataVolume: "medium", criticality: "medium" }},
  
  // Auth0 dependencies
  { id: "dep_015", source: "vnd_auth_auth0", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.9, metadata: { lastVerified: "2024-12-05", dataVolume: "medium", criticality: "high" }},
  { id: "dep_016", source: "vnd_auth_auth0", target: "vnd_api_sendgrid", type: "integrates_with", category: "api_call", strength: 0.7, metadata: { lastVerified: "2024-11-22", dataVolume: "medium", criticality: "medium" }},
  
  // Adyen dependencies
  { id: "dep_017", source: "vnd_pay_adyen", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.85, metadata: { lastVerified: "2024-12-08", dataVolume: "high", criticality: "high" }},
  { id: "dep_018", source: "vnd_pay_adyen", target: "vnd_auth_okta", type: "depends_on", category: "authentication", strength: 0.8, metadata: { lastVerified: "2024-11-30", dataVolume: "low", criticality: "high" }},
  
  // MongoDB dependencies
  { id: "dep_019", source: "vnd_data_mongodb", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.95, metadata: { lastVerified: "2024-12-10", dataVolume: "high", criticality: "high" }},
  { id: "dep_020", source: "vnd_data_mongodb", target: "vnd_infra_datadog", type: "integrates_with", category: "data_flow", strength: 0.6, metadata: { lastVerified: "2024-11-25", dataVolume: "medium", criticality: "medium" }},
  
  // SendGrid dependencies
  { id: "dep_021", source: "vnd_api_sendgrid", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.82, metadata: { lastVerified: "2024-12-02", dataVolume: "high", criticality: "medium" }},
  { id: "dep_022", source: "vnd_api_sendgrid", target: "vnd_auth_okta", type: "depends_on", category: "authentication", strength: 0.7, metadata: { lastVerified: "2024-11-18", dataVolume: "low", criticality: "medium" }},
  
  // Cloudflare dependencies
  { id: "dep_023", source: "vnd_infra_cloudflare", target: "vnd_infra_datadog", type: "integrates_with", category: "data_flow", strength: 0.65, metadata: { lastVerified: "2024-12-05", dataVolume: "high", criticality: "medium" }},
  
  // Redis dependencies
  { id: "dep_024", source: "vnd_data_redis", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.92, metadata: { lastVerified: "2024-12-08", dataVolume: "high", criticality: "high" }},
  { id: "dep_025", source: "vnd_data_redis", target: "vnd_data_mongodb", type: "integrates_with", category: "data_flow", strength: 0.75, metadata: { lastVerified: "2024-11-28", dataVolume: "high", criticality: "medium" }},
  
  // Segment dependencies
  { id: "dep_026", source: "vnd_api_segment", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.88, metadata: { lastVerified: "2024-12-12", dataVolume: "high", criticality: "high" }},
  { id: "dep_027", source: "vnd_api_segment", target: "vnd_data_snowflake", type: "supplies", category: "data_flow", strength: 0.9, metadata: { lastVerified: "2024-12-10", dataVolume: "high", criticality: "high" }},
  { id: "dep_028", source: "vnd_api_segment", target: "vnd_api_mixpanel", type: "integrates_with", category: "data_flow", strength: 0.8, metadata: { lastVerified: "2024-11-22", dataVolume: "high", criticality: "medium" }},
  
  // Datadog dependencies
  { id: "dep_029", source: "vnd_infra_pagerduty", target: "vnd_infra_datadog", type: "depends_on", category: "data_flow", strength: 0.85, metadata: { lastVerified: "2024-12-05", dataVolume: "medium", criticality: "high" }},
  
  // Plaid dependencies
  { id: "dep_030", source: "vnd_pay_plaid", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.9, metadata: { lastVerified: "2024-12-01", dataVolume: "high", criticality: "high" }},
  { id: "dep_031", source: "vnd_pay_plaid", target: "vnd_auth_okta", type: "depends_on", category: "authentication", strength: 0.82, metadata: { lastVerified: "2024-11-25", dataVolume: "low", criticality: "high" }},
  { id: "dep_032", source: "vnd_pay_plaid", target: "vnd_pay_stripe", type: "integrates_with", category: "data_flow", strength: 0.78, metadata: { lastVerified: "2024-11-20", dataVolume: "high", criticality: "high" }},
  
  // OneLogin dependencies
  { id: "dep_033", source: "vnd_auth_onelogin", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.85, metadata: { lastVerified: "2024-12-08", dataVolume: "medium", criticality: "high" }},
  { id: "dep_034", source: "vnd_auth_onelogin", target: "vnd_api_slack", type: "integrates_with", category: "api_call", strength: 0.7, metadata: { lastVerified: "2024-11-15", dataVolume: "low", criticality: "medium" }},
  
  // Elasticsearch dependencies
  { id: "dep_035", source: "vnd_data_elasticsearch", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.92, metadata: { lastVerified: "2024-12-10", dataVolume: "high", criticality: "high" }},
  { id: "dep_036", source: "vnd_data_elasticsearch", target: "vnd_infra_datadog", type: "integrates_with", category: "data_flow", strength: 0.68, metadata: { lastVerified: "2024-11-28", dataVolume: "high", criticality: "medium" }},
  
  // Slack dependencies
  { id: "dep_037", source: "vnd_api_slack", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.88, metadata: { lastVerified: "2024-12-05", dataVolume: "high", criticality: "high" }},
  { id: "dep_038", source: "vnd_api_slack", target: "vnd_auth_okta", type: "depends_on", category: "authentication", strength: 0.9, metadata: { lastVerified: "2024-12-01", dataVolume: "medium", criticality: "high" }},
  
  // PagerDuty dependencies
  { id: "dep_039", source: "vnd_infra_pagerduty", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.8, metadata: { lastVerified: "2024-12-08", dataVolume: "medium", criticality: "medium" }},
  { id: "dep_040", source: "vnd_infra_pagerduty", target: "vnd_api_slack", type: "integrates_with", category: "api_call", strength: 0.85, metadata: { lastVerified: "2024-11-25", dataVolume: "low", criticality: "high" }},
  
  // Braintree dependencies
  { id: "dep_041", source: "vnd_pay_braintree", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.88, metadata: { lastVerified: "2024-12-12", dataVolume: "high", criticality: "high" }},
  { id: "dep_042", source: "vnd_pay_braintree", target: "vnd_pay_stripe", type: "integrates_with", category: "data_flow", strength: 0.6, metadata: { lastVerified: "2024-11-20", dataVolume: "medium", criticality: "medium" }},
  
  // Confluent dependencies
  { id: "dep_043", source: "vnd_data_confluent", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.95, metadata: { lastVerified: "2024-12-10", dataVolume: "high", criticality: "high" }},
  { id: "dep_044", source: "vnd_data_confluent", target: "vnd_data_snowflake", type: "supplies", category: "data_flow", strength: 0.88, metadata: { lastVerified: "2024-12-05", dataVolume: "high", criticality: "high" }},
  
  // Zapier dependencies
  { id: "dep_045", source: "vnd_api_zapier", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.75, metadata: { lastVerified: "2024-11-28", dataVolume: "medium", criticality: "medium" }},
  { id: "dep_046", source: "vnd_api_zapier", target: "vnd_api_slack", type: "integrates_with", category: "api_call", strength: 0.8, metadata: { lastVerified: "2024-11-22", dataVolume: "medium", criticality: "medium" }},
  { id: "dep_047", source: "vnd_api_zapier", target: "vnd_api_hubspot", type: "integrates_with", category: "api_call", strength: 0.72, metadata: { lastVerified: "2024-11-15", dataVolume: "medium", criticality: "low" }},
  
  // Intercom dependencies
  { id: "dep_048", source: "vnd_api_intercom", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.82, metadata: { lastVerified: "2024-12-05", dataVolume: "medium", criticality: "medium" }},
  { id: "dep_049", source: "vnd_api_intercom", target: "vnd_api_segment", type: "integrates_with", category: "data_flow", strength: 0.78, metadata: { lastVerified: "2024-11-28", dataVolume: "high", criticality: "medium" }},
  
  // Amplitude dependencies
  { id: "dep_050", source: "vnd_data_amplitude", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.85, metadata: { lastVerified: "2024-12-08", dataVolume: "high", criticality: "medium" }},
  { id: "dep_051", source: "vnd_data_amplitude", target: "vnd_api_segment", type: "depends_on", category: "data_flow", strength: 0.9, metadata: { lastVerified: "2024-12-01", dataVolume: "high", criticality: "high" }},
  
  // Vercel dependencies
  { id: "dep_052", source: "vnd_infra_vercel", target: "vnd_infra_cloudflare", type: "depends_on", category: "infrastructure", strength: 0.7, metadata: { lastVerified: "2024-12-10", dataVolume: "high", criticality: "medium" }},
  { id: "dep_053", source: "vnd_infra_vercel", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.88, metadata: { lastVerified: "2024-12-05", dataVolume: "high", criticality: "high" }},
  
  // Mixpanel dependencies
  { id: "dep_054", source: "vnd_api_mixpanel", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.82, metadata: { lastVerified: "2024-12-02", dataVolume: "high", criticality: "medium" }},
  
  // Recurly dependencies
  { id: "dep_055", source: "vnd_pay_recurly", target: "vnd_pay_stripe", type: "depends_on", category: "data_flow", strength: 0.85, metadata: { lastVerified: "2024-11-25", dataVolume: "high", criticality: "high" }},
  { id: "dep_056", source: "vnd_pay_recurly", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.8, metadata: { lastVerified: "2024-12-01", dataVolume: "medium", criticality: "medium" }},
  
  // Duo dependencies
  { id: "dep_057", source: "vnd_auth_duo", target: "vnd_auth_okta", type: "integrates_with", category: "authentication", strength: 0.88, metadata: { lastVerified: "2024-12-08", dataVolume: "medium", criticality: "high" }},
  { id: "dep_058", source: "vnd_auth_duo", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.78, metadata: { lastVerified: "2024-11-28", dataVolume: "medium", criticality: "medium" }},
  
  // Looker dependencies
  { id: "dep_059", source: "vnd_data_looker", target: "vnd_data_snowflake", type: "depends_on", category: "data_flow", strength: 0.95, metadata: { lastVerified: "2024-12-10", dataVolume: "high", criticality: "high" }},
  { id: "dep_060", source: "vnd_data_looker", target: "vnd_auth_okta", type: "depends_on", category: "authentication", strength: 0.82, metadata: { lastVerified: "2024-12-01", dataVolume: "low", criticality: "medium" }},
  
  // Netlify dependencies
  { id: "dep_061", source: "vnd_infra_netlify", target: "vnd_infra_cloudflare", type: "depends_on", category: "infrastructure", strength: 0.72, metadata: { lastVerified: "2024-11-25", dataVolume: "high", criticality: "medium" }},
  
  // HubSpot dependencies
  { id: "dep_062", source: "vnd_api_hubspot", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.8, metadata: { lastVerified: "2024-12-05", dataVolume: "high", criticality: "medium" }},
  { id: "dep_063", source: "vnd_api_hubspot", target: "vnd_api_segment", type: "integrates_with", category: "data_flow", strength: 0.85, metadata: { lastVerified: "2024-11-22", dataVolume: "high", criticality: "medium" }},
  { id: "dep_064", source: "vnd_api_hubspot", target: "vnd_api_slack", type: "integrates_with", category: "api_call", strength: 0.7, metadata: { lastVerified: "2024-11-15", dataVolume: "low", criticality: "low" }},
  
  // Fivetran dependencies
  { id: "dep_065", source: "vnd_data_fivetran", target: "vnd_data_snowflake", type: "supplies", category: "data_flow", strength: 0.95, metadata: { lastVerified: "2024-12-08", dataVolume: "high", criticality: "high" }},
  { id: "dep_066", source: "vnd_data_fivetran", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.85, metadata: { lastVerified: "2024-12-01", dataVolume: "high", criticality: "medium" }},
  
  // Chargebee dependencies
  { id: "dep_067", source: "vnd_pay_chargebee", target: "vnd_pay_stripe", type: "depends_on", category: "data_flow", strength: 0.9, metadata: { lastVerified: "2024-12-05", dataVolume: "high", criticality: "high" }},
  { id: "dep_068", source: "vnd_pay_chargebee", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.78, metadata: { lastVerified: "2024-11-28", dataVolume: "medium", criticality: "medium" }},
  
  // Sentry dependencies
  { id: "dep_069", source: "vnd_infra_sentry", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.85, metadata: { lastVerified: "2024-12-10", dataVolume: "high", criticality: "medium" }},
  { id: "dep_070", source: "vnd_infra_sentry", target: "vnd_api_slack", type: "integrates_with", category: "api_call", strength: 0.75, metadata: { lastVerified: "2024-11-25", dataVolume: "low", criticality: "medium" }},
  
  // Zendesk dependencies
  { id: "dep_071", source: "vnd_api_zendesk", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.82, metadata: { lastVerified: "2024-12-02", dataVolume: "medium", criticality: "medium" }},
  { id: "dep_072", source: "vnd_api_zendesk", target: "vnd_api_slack", type: "integrates_with", category: "api_call", strength: 0.78, metadata: { lastVerified: "2024-11-20", dataVolume: "low", criticality: "medium" }},
  { id: "dep_073", source: "vnd_api_zendesk", target: "vnd_api_intercom", type: "integrates_with", category: "data_flow", strength: 0.65, metadata: { lastVerified: "2024-11-15", dataVolume: "medium", criticality: "low" }},
  
  // dbt dependencies
  { id: "dep_074", source: "vnd_data_dbt", target: "vnd_data_snowflake", type: "depends_on", category: "data_flow", strength: 0.98, metadata: { lastVerified: "2024-12-12", dataVolume: "high", criticality: "high" }},
  { id: "dep_075", source: "vnd_data_dbt", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.75, metadata: { lastVerified: "2024-12-05", dataVolume: "medium", criticality: "medium" }},
  
  // Ping Identity dependencies
  { id: "dep_076", source: "vnd_auth_ping", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.85, metadata: { lastVerified: "2024-12-08", dataVolume: "medium", criticality: "high" }},
  { id: "dep_077", source: "vnd_auth_ping", target: "vnd_auth_okta", type: "integrates_with", category: "authentication", strength: 0.7, metadata: { lastVerified: "2024-11-22", dataVolume: "low", criticality: "medium" }},
  
  // CircleCI dependencies
  { id: "dep_078", source: "vnd_infra_circleci", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.9, metadata: { lastVerified: "2024-12-01", dataVolume: "high", criticality: "high" }},
  { id: "dep_079", source: "vnd_infra_circleci", target: "vnd_api_slack", type: "integrates_with", category: "api_call", strength: 0.72, metadata: { lastVerified: "2024-11-25", dataVolume: "low", criticality: "medium" }},
  
  // LaunchDarkly dependencies
  { id: "dep_080", source: "vnd_api_launchdarkly", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.82, metadata: { lastVerified: "2024-12-05", dataVolume: "medium", criticality: "medium" }},
  { id: "dep_081", source: "vnd_api_launchdarkly", target: "vnd_infra_datadog", type: "integrates_with", category: "data_flow", strength: 0.68, metadata: { lastVerified: "2024-11-28", dataVolume: "medium", criticality: "medium" }},
  
  // Heap dependencies
  { id: "dep_082", source: "vnd_data_heap", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.8, metadata: { lastVerified: "2024-12-02", dataVolume: "high", criticality: "medium" }},
  { id: "dep_083", source: "vnd_data_heap", target: "vnd_api_segment", type: "integrates_with", category: "data_flow", strength: 0.85, metadata: { lastVerified: "2024-11-22", dataVolume: "high", criticality: "medium" }},
  
  // Paddle dependencies
  { id: "dep_084", source: "vnd_pay_paddle", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.78, metadata: { lastVerified: "2024-12-08", dataVolume: "medium", criticality: "medium" }},
  { id: "dep_085", source: "vnd_pay_paddle", target: "vnd_pay_stripe", type: "integrates_with", category: "data_flow", strength: 0.65, metadata: { lastVerified: "2024-11-25", dataVolume: "medium", criticality: "medium" }},
  
  // Terraform dependencies
  { id: "dep_086", source: "vnd_infra_terraform", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.95, metadata: { lastVerified: "2024-12-10", dataVolume: "medium", criticality: "high" }},
  
  // Postman dependencies
  { id: "dep_087", source: "vnd_api_postman", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.7, metadata: { lastVerified: "2024-12-01", dataVolume: "low", criticality: "low" }},
  
  // Metabase dependencies
  { id: "dep_088", source: "vnd_data_metabase", target: "vnd_data_snowflake", type: "depends_on", category: "data_flow", strength: 0.88, metadata: { lastVerified: "2024-11-28", dataVolume: "high", criticality: "medium" }},
  { id: "dep_089", source: "vnd_data_metabase", target: "vnd_data_mongodb", type: "integrates_with", category: "data_flow", strength: 0.75, metadata: { lastVerified: "2024-11-20", dataVolume: "medium", criticality: "medium" }},
  
  // JumpCloud dependencies
  { id: "dep_090", source: "vnd_auth_jumpcloud", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.82, metadata: { lastVerified: "2024-12-05", dataVolume: "medium", criticality: "medium" }},
  { id: "dep_091", source: "vnd_auth_jumpcloud", target: "vnd_auth_okta", type: "integrates_with", category: "authentication", strength: 0.75, metadata: { lastVerified: "2024-11-22", dataVolume: "low", criticality: "medium" }},
  
  // Sumo Logic dependencies
  { id: "dep_092", source: "vnd_infra_sumo", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.88, metadata: { lastVerified: "2024-12-08", dataVolume: "high", criticality: "medium" }},
  { id: "dep_093", source: "vnd_infra_sumo", target: "vnd_infra_datadog", type: "integrates_with", category: "data_flow", strength: 0.6, metadata: { lastVerified: "2024-11-25", dataVolume: "high", criticality: "low" }},
  
  // Airtable dependencies
  { id: "dep_094", source: "vnd_api_airtable", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.78, metadata: { lastVerified: "2024-12-01", dataVolume: "medium", criticality: "medium" }},
  { id: "dep_095", source: "vnd_api_airtable", target: "vnd_api_zapier", type: "integrates_with", category: "api_call", strength: 0.85, metadata: { lastVerified: "2024-11-20", dataVolume: "medium", criticality: "low" }},
  
  // Databricks dependencies
  { id: "dep_096", source: "vnd_data_databricks", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.95, metadata: { lastVerified: "2024-12-12", dataVolume: "high", criticality: "high" }},
  { id: "dep_097", source: "vnd_data_databricks", target: "vnd_data_snowflake", type: "integrates_with", category: "data_flow", strength: 0.82, metadata: { lastVerified: "2024-12-05", dataVolume: "high", criticality: "high" }},
  
  // Square dependencies
  { id: "dep_098", source: "vnd_pay_square", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.85, metadata: { lastVerified: "2024-12-08", dataVolume: "high", criticality: "high" }},
  { id: "dep_099", source: "vnd_pay_square", target: "vnd_pay_stripe", type: "integrates_with", category: "data_flow", strength: 0.55, metadata: { lastVerified: "2024-11-22", dataVolume: "medium", criticality: "medium" }},
  
  // New Relic dependencies
  { id: "dep_100", source: "vnd_infra_newrelic", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.88, metadata: { lastVerified: "2024-12-05", dataVolume: "high", criticality: "medium" }},
  { id: "dep_101", source: "vnd_infra_newrelic", target: "vnd_api_slack", type: "integrates_with", category: "api_call", strength: 0.72, metadata: { lastVerified: "2024-11-28", dataVolume: "low", criticality: "medium" }},
  
  // Algolia dependencies
  { id: "dep_102", source: "vnd_api_algolia", target: "vnd_data_aws", type: "depends_on", category: "infrastructure", strength: 0.82, metadata: { lastVerified: "2024-12-01", dataVolume: "high", criticality: "medium" }},
  { id: "dep_103", source: "vnd_api_algolia", target: "vnd_api_segment", type: "integrates_with", category: "data_flow", strength: 0.7, metadata: { lastVerified: "2024-11-22", dataVolume: "medium", criticality: "medium" }},
  
  // Additional cross-dependencies for realistic complexity
  { id: "dep_104", source: "vnd_pay_stripe", target: "vnd_api_twilio", type: "integrates_with", category: "api_call", strength: 0.65, metadata: { lastVerified: "2024-11-28", dataVolume: "medium", criticality: "medium" }},
  { id: "dep_105", source: "vnd_data_snowflake", target: "vnd_infra_datadog", type: "integrates_with", category: "data_flow", strength: 0.72, metadata: { lastVerified: "2024-12-05", dataVolume: "medium", criticality: "medium" }},
  { id: "dep_106", source: "vnd_auth_okta", target: "vnd_infra_pagerduty", type: "integrates_with", category: "api_call", strength: 0.58, metadata: { lastVerified: "2024-11-20", dataVolume: "low", criticality: "medium" }},
  { id: "dep_107", source: "vnd_api_segment", target: "vnd_data_amplitude", type: "supplies", category: "data_flow", strength: 0.92, metadata: { lastVerified: "2024-12-10", dataVolume: "high", criticality: "high" }},
  { id: "dep_108", source: "vnd_infra_datadog", target: "vnd_api_slack", type: "integrates_with", category: "api_call", strength: 0.85, metadata: { lastVerified: "2024-12-01", dataVolume: "medium", criticality: "high" }},
  { id: "dep_109", source: "vnd_data_confluent", target: "vnd_data_elasticsearch", type: "supplies", category: "data_flow", strength: 0.78, metadata: { lastVerified: "2024-11-25", dataVolume: "high", criticality: "medium" }},
  { id: "dep_110", source: "vnd_pay_plaid", target: "vnd_data_snowflake", type: "supplies", category: "data_flow", strength: 0.75, metadata: { lastVerified: "2024-12-08", dataVolume: "high", criticality: "high" }},
  { id: "dep_111", source: "vnd_auth_auth0", target: "vnd_api_twilio", type: "integrates_with", category: "api_call", strength: 0.68, metadata: { lastVerified: "2024-11-22", dataVolume: "medium", criticality: "medium" }},
  { id: "dep_112", source: "vnd_infra_cloudflare", target: "vnd_infra_vercel", type: "integrates_with", category: "infrastructure", strength: 0.82, metadata: { lastVerified: "2024-12-05", dataVolume: "high", criticality: "medium" }},
  { id: "dep_113", source: "vnd_api_sendgrid", target: "vnd_api_intercom", type: "integrates_with", category: "api_call", strength: 0.62, metadata: { lastVerified: "2024-11-18", dataVolume: "medium", criticality: "low" }},
  { id: "dep_114", source: "vnd_data_mongodb", target: "vnd_data_confluent", type: "integrates_with", category: "data_flow", strength: 0.7, metadata: { lastVerified: "2024-12-01", dataVolume: "high", criticality: "medium" }},
  { id: "dep_115", source: "vnd_infra_sentry", target: "vnd_infra_pagerduty", type: "integrates_with", category: "api_call", strength: 0.8, metadata: { lastVerified: "2024-11-28", dataVolume: "low", criticality: "high" }},
  { id: "dep_116", source: "vnd_api_zendesk", target: "vnd_api_hubspot", type: "integrates_with", category: "data_flow", strength: 0.72, metadata: { lastVerified: "2024-11-22", dataVolume: "medium", criticality: "medium" }},
  { id: "dep_117", source: "vnd_data_looker", target: "vnd_data_databricks", type: "integrates_with", category: "data_flow", strength: 0.78, metadata: { lastVerified: "2024-12-05", dataVolume: "high", criticality: "medium" }},
  { id: "dep_118", source: "vnd_infra_terraform", target: "vnd_infra_datadog", type: "integrates_with", category: "data_flow", strength: 0.55, metadata: { lastVerified: "2024-11-25", dataVolume: "low", criticality: "low" }},
  { id: "dep_119", source: "vnd_pay_adyen", target: "vnd_data_snowflake", type: "supplies", category: "data_flow", strength: 0.72, metadata: { lastVerified: "2024-12-08", dataVolume: "high", criticality: "high" }},
  { id: "dep_120", source: "vnd_api_launchdarkly", target: "vnd_api_segment", type: "integrates_with", category: "data_flow", strength: 0.75, metadata: { lastVerified: "2024-11-20", dataVolume: "medium", criticality: "medium" }},
];

export const getDependenciesForVendor = (vendorId: string): Dependency[] => {
  return dependencies.filter(d => d.source === vendorId || d.target === vendorId);
};

export const getOutgoingDependencies = (vendorId: string): Dependency[] => {
  return dependencies.filter(d => d.source === vendorId);
};

export const getIncomingDependencies = (vendorId: string): Dependency[] => {
  return dependencies.filter(d => d.target === vendorId);
};
