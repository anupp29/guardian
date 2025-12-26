import { motion } from "framer-motion";
import Layout from "@/components/Layout";
import { Shield, Brain, Network, AlertTriangle, CheckCircle, Info } from "lucide-react";

const About = () => {
  const features = [
    {
      icon: Network,
      title: "Graph Neural Networks",
      description: "Advanced GNN models analyze vendor relationships to identify hidden risk propagation paths across your supply chain network."
    },
    {
      icon: Brain,
      title: "AI Agent Orchestration",
      description: "Multiple specialized AI agents work together to assess risks, generate recommendations, and simulate attack scenarios in real-time."
    },
    {
      icon: Shield,
      title: "Risk Intelligence",
      description: "Continuous monitoring and scoring of all vendors based on security posture, certifications, audit history, and dependency criticality."
    },
  ];

  const capabilities = [
    "Real-time vendor risk scoring and monitoring",
    "Attack simulation with cascade analysis",
    "AI-powered mitigation recommendations",
    "Compliance tracking (SOC2, ISO27001, PCI-DSS)",
    "Dependency mapping and critical path identification",
    "Automated incident response workflows"
  ];

  return (
    <Layout>
      <div className="p-8 max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl font-bold text-foreground mb-4">About Guardian AI</h1>
          <p className="text-xl text-text-secondary max-w-2xl mx-auto">
            An enterprise-grade Supply Chain Risk Intelligence Platform powered by Graph Neural Networks and AI agent orchestration
          </p>
        </motion.div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + i * 0.1 }}
              className="bg-surface-1 rounded-lg border border-border p-6 hover:border-primary/30 transition-colors"
            >
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <feature.icon className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-lg font-semibold text-foreground mb-2">{feature.title}</h3>
              <p className="text-sm text-text-secondary">{feature.description}</p>
            </motion.div>
          ))}
        </div>

        {/* Capabilities */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-surface-1 rounded-lg border border-border p-8 mb-8"
        >
          <h2 className="text-2xl font-bold text-foreground mb-6">Platform Capabilities</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {capabilities.map((cap, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 + i * 0.05 }}
                className="flex items-center gap-3"
              >
                <CheckCircle className="w-5 h-5 text-success flex-shrink-0" />
                <span className="text-text-secondary">{cap}</span>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Limitations */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-warning/5 rounded-lg border border-warning/30 p-8"
        >
          <div className="flex items-center gap-3 mb-4">
            <AlertTriangle className="w-6 h-6 text-warning" />
            <h2 className="text-xl font-semibold text-warning-light">Current Limitations</h2>
          </div>
          <ul className="space-y-3">
            <li className="flex items-start gap-3">
              <Info className="w-5 h-5 text-warning mt-0.5 flex-shrink-0" />
              <span className="text-text-secondary">
                <strong className="text-foreground">Demo Mode:</strong> This interface uses simulated data. In production, connect to live vendor APIs and security feeds.
              </span>
            </li>
            <li className="flex items-start gap-3">
              <Info className="w-5 h-5 text-warning mt-0.5 flex-shrink-0" />
              <span className="text-text-secondary">
                <strong className="text-foreground">AI Recommendations:</strong> Generated recommendations should be reviewed by security teams before implementation.
              </span>
            </li>
            <li className="flex items-start gap-3">
              <Info className="w-5 h-5 text-warning mt-0.5 flex-shrink-0" />
              <span className="text-text-secondary">
                <strong className="text-foreground">Risk Scores:</strong> Scores are calculated based on available data; real-world assessments require additional context.
              </span>
            </li>
          </ul>
        </motion.div>

        {/* Footer */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="text-center text-text-tertiary text-sm mt-12"
        >
          Guardian AI — Protecting Supply Chains Through Intelligent Risk Analysis
        </motion.p>
      </div>
    </Layout>
  );
};

export default About;
