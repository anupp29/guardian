import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle, Activity, Clock, DollarSign, Zap, AlertCircle, Shield } from "lucide-react";
import { cn } from "@/lib/utils";

interface SimulationResult {
  blastRadius: number;
  cascadeDepth: number;
  propagationTime: string;
  estimatedDamage: string;
  riskLevel: "low" | "medium" | "high" | "critical";
  aiAnalysis: string;
}

interface AnalysisResultsProps {
  results: SimulationResult | null;
  isLoading?: boolean;
}

const AnalysisResults = ({ results, isLoading }: AnalysisResultsProps) => {
  const riskColors = {
    low: { bg: "bg-success/10", border: "border-success/30", text: "text-success" },
    medium: { bg: "bg-info/10", border: "border-info/30", text: "text-info" },
    high: { bg: "bg-warning/10", border: "border-warning/30", text: "text-warning" },
    critical: { bg: "bg-critical/10", border: "border-critical/30", text: "text-critical" },
  };

  return (
    <div className="bg-surface-1 rounded-lg border border-border h-full flex flex-col">
      <div className="p-4 border-b border-border">
        <h2 className="text-lg font-semibold text-foreground">Analysis Results</h2>
      </div>
      
      <div className="flex-1 p-4 overflow-auto scrollbar-custom">
        <AnimatePresence mode="wait">
          {isLoading ? (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center justify-center h-64"
            >
              <div className="w-12 h-12 border-3 border-primary/20 border-t-primary rounded-full animate-spin mb-4" />
              <p className="text-text-secondary text-sm">Analyzing cascade impact...</p>
            </motion.div>
          ) : results ? (
            <motion.div
              key="results"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-4"
            >
              {/* Risk Level Badge */}
              <div className="flex items-center justify-between">
                <span className="text-sm text-text-tertiary">Risk Level</span>
                <span className={cn(
                  "px-3 py-1 rounded-full text-sm font-semibold uppercase tracking-wide flex items-center gap-1.5",
                  riskColors[results.riskLevel].bg,
                  riskColors[results.riskLevel].border,
                  riskColors[results.riskLevel].text,
                  "border"
                )}>
                  <span className="w-2 h-2 rounded-full bg-current animate-pulse" />
                  {results.riskLevel}
                </span>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-2 gap-3">
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.1 }}
                  className="p-4 rounded-lg bg-surface-2 border border-border"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <Activity className="w-4 h-4 text-warning" />
                    <span className="text-xs text-text-tertiary">Affected Nodes</span>
                  </div>
                  <p className="text-2xl font-bold text-foreground">{results.blastRadius}</p>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.15 }}
                  className="p-4 rounded-lg bg-surface-2 border border-border"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <Zap className="w-4 h-4 text-primary" />
                    <span className="text-xs text-text-tertiary">Cascade Depth</span>
                  </div>
                  <p className="text-2xl font-bold text-foreground">{results.cascadeDepth}</p>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.2 }}
                  className="p-4 rounded-lg bg-surface-2 border border-border"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <Clock className="w-4 h-4 text-info" />
                    <span className="text-xs text-text-tertiary">Propagation</span>
                  </div>
                  <p className="text-2xl font-bold text-foreground">{results.propagationTime}</p>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.25 }}
                  className="p-4 rounded-lg bg-surface-2 border border-border"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <DollarSign className="w-4 h-4 text-success" />
                    <span className="text-xs text-text-tertiary">Est. Damage</span>
                  </div>
                  <p className="text-lg font-bold text-foreground">{results.estimatedDamage}</p>
                </motion.div>
              </div>

              {/* AI Analysis */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="p-4 rounded-lg bg-warning/5 border border-warning/20"
              >
                <div className="flex items-center gap-2 mb-3">
                  <AlertTriangle className="w-5 h-5 text-warning" />
                  <h3 className="font-semibold text-warning-light">AI Analysis</h3>
                </div>
                <p className="text-sm text-text-secondary leading-relaxed">
                  {results.aiAnalysis}
                </p>
              </motion.div>
            </motion.div>
          ) : (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center justify-center h-64 text-center"
            >
              <div className="w-16 h-16 rounded-full bg-surface-2 flex items-center justify-center mb-4">
                <Shield className="w-8 h-8 text-text-tertiary" />
              </div>
              <p className="text-text-secondary mb-1">No simulation results</p>
              <p className="text-sm text-text-tertiary">Select a vendor and run simulation</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default AnalysisResults;
