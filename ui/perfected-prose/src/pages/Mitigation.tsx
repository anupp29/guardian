import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Layout from "@/components/Layout";
import { ChevronDown, Clock, DollarSign, TrendingDown, CheckCircle } from "lucide-react";
import { mitigations, Mitigation } from "@/data/mitigations";
import { cn } from "@/lib/utils";

const MitigationCard = ({ mitigation, index }: { mitigation: Mitigation; index: number }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const effectivenessColors = {
    very_high: "text-success bg-success/10 border-success/20",
    high: "text-info bg-info/10 border-info/20",
    medium: "text-warning bg-warning/10 border-warning/20",
    low: "text-text-tertiary bg-surface-3 border-border",
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 + index * 0.08 }}
      className="bg-surface-1 rounded-lg border border-border overflow-hidden"
    >
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-6 text-left hover:bg-surface-2/50 transition-colors"
      >
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <span className="w-8 h-8 rounded-lg bg-primary/10 text-primary font-bold flex items-center justify-center text-sm">
                {mitigation.priority}
              </span>
              <h3 className="text-lg font-semibold text-foreground">{mitigation.title}</h3>
            </div>
            <p className="text-text-secondary text-sm line-clamp-2">{mitigation.description}</p>
          </div>
          <ChevronDown className={cn(
            "w-5 h-5 text-text-tertiary transition-transform duration-200",
            isExpanded && "rotate-180"
          )} />
        </div>

        <div className="flex flex-wrap gap-3 mt-4">
          <span className={cn(
            "px-3 py-1 rounded-full text-xs font-medium border",
            effectivenessColors[mitigation.effectiveness]
          )}>
            {mitigation.effectiveness.replace("_", " ")} effectiveness
          </span>
          <span className="px-3 py-1 rounded-full text-xs font-medium bg-surface-3 text-text-secondary flex items-center gap-1">
            <TrendingDown className="w-3 h-3" />
            {mitigation.riskReduction}% risk reduction
          </span>
          <span className="px-3 py-1 rounded-full text-xs font-medium bg-surface-3 text-text-secondary flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {mitigation.implementationTime}
          </span>
          <span className="px-3 py-1 rounded-full text-xs font-medium bg-surface-3 text-text-secondary flex items-center gap-1">
            <DollarSign className="w-3 h-3" />
            {mitigation.cost}
          </span>
        </div>
      </button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="px-6 pb-6 pt-2 border-t border-border space-y-6">
              <div>
                <h4 className="font-medium text-foreground mb-2">Technical Details</h4>
                <p className="text-sm text-text-secondary">{mitigation.technicalDetails}</p>
              </div>

              <div>
                <h4 className="font-medium text-foreground mb-2">Business Justification</h4>
                <p className="text-sm text-text-secondary">{mitigation.businessJustification}</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 rounded-lg bg-surface-2">
                  <p className="text-xs text-text-tertiary mb-2">Engineering Effort</p>
                  <p className="text-sm font-medium text-foreground">{mitigation.effort.engineering}</p>
                </div>
                <div className="p-4 rounded-lg bg-surface-2">
                  <p className="text-xs text-text-tertiary mb-2">Testing</p>
                  <p className="text-sm font-medium text-foreground">{mitigation.effort.testing}</p>
                </div>
                <div className="p-4 rounded-lg bg-surface-2">
                  <p className="text-xs text-text-tertiary mb-2">Deployment</p>
                  <p className="text-sm font-medium text-foreground">{mitigation.effort.deployment}</p>
                </div>
              </div>

              <div>
                <h4 className="font-medium text-foreground mb-3">Success Metrics</h4>
                <ul className="space-y-2">
                  {mitigation.successMetrics.map((metric, i) => (
                    <li key={i} className="flex items-center gap-2 text-sm text-text-secondary">
                      <CheckCircle className="w-4 h-4 text-success flex-shrink-0" />
                      {metric}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

const MitigationPage = () => {
  return (
    <Layout>
      <div className="p-8">
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-foreground mb-2">Mitigation Strategies</h1>
          <p className="text-text-secondary">Prioritized recommendations to reduce supply chain risk</p>
        </motion.div>

        {/* Summary Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8"
        >
          <div className="bg-surface-1 rounded-lg border border-border p-4">
            <p className="text-text-tertiary text-sm">Total Strategies</p>
            <p className="text-2xl font-bold text-foreground">{mitigations.length}</p>
          </div>
          <div className="bg-surface-1 rounded-lg border border-success/20 p-4">
            <p className="text-text-tertiary text-sm">Max Risk Reduction</p>
            <p className="text-2xl font-bold text-success">{Math.max(...mitigations.map(m => m.riskReduction))}%</p>
          </div>
          <div className="bg-surface-1 rounded-lg border border-border p-4">
            <p className="text-text-tertiary text-sm">Vendors Protected</p>
            <p className="text-2xl font-bold text-foreground">{mitigations.reduce((acc, m) => acc + m.affectedVendors, 0)}</p>
          </div>
          <div className="bg-surface-1 rounded-lg border border-border p-4">
            <p className="text-text-tertiary text-sm">Very High Effectiveness</p>
            <p className="text-2xl font-bold text-foreground">{mitigations.filter(m => m.effectiveness === 'very_high').length}</p>
          </div>
        </motion.div>

        {/* Mitigation List */}
        <div className="space-y-4">
          {mitigations.map((mitigation, i) => (
            <MitigationCard key={mitigation.id} mitigation={mitigation} index={i} />
          ))}
        </div>
      </div>
    </Layout>
  );
};

export default MitigationPage;
