import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import Layout from "@/components/Layout";
import { Play, AlertTriangle } from "lucide-react";
import { vendors } from "@/data/vendors";
import { getSimulationByVendor } from "@/data/simulations";
import { dependencies } from "@/data/dependencies";
import { cn } from "@/lib/utils";
import SupplyChainGraph from "@/components/SupplyChainGraph";
import VendorSelector from "@/components/VendorSelector";
import AnalysisResults from "@/components/AnalysisResults";

const Simulation = () => {
  const [selectedVendor, setSelectedVendor] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [affectedNodes, setAffectedNodes] = useState<string[]>([]);
  const [results, setResults] = useState<{
    blastRadius: number;
    cascadeDepth: number;
    propagationTime: string;
    estimatedDamage: string;
    riskLevel: "low" | "medium" | "high" | "critical";
    aiAnalysis: string;
  } | null>(null);

  // Calculate affected nodes when simulation runs
  const calculateCascade = (sourceId: string): string[] => {
    const affected = new Set<string>([sourceId]);
    const queue = [sourceId];
    let depth = 0;
    const maxDepth = 5;

    while (queue.length > 0 && depth < maxDepth) {
      const current = queue.shift()!;
      const connectedDeps = dependencies.filter(
        d => d.source === current || d.target === current
      );

      connectedDeps.forEach(dep => {
        const connectedNode = dep.source === current ? dep.target : dep.source;
        if (!affected.has(connectedNode) && dep.strength > 0.6) {
          affected.add(connectedNode);
          queue.push(connectedNode);
        }
      });
      depth++;
    }

    return Array.from(affected);
  };

  const runSimulation = () => {
    if (!selectedVendor) return;
    
    setIsRunning(true);
    setResults(null);
    setAffectedNodes([]);

    // Animate the cascade
    const cascade = calculateCascade(selectedVendor);
    
    // Progressively reveal affected nodes
    cascade.forEach((nodeId, index) => {
      setTimeout(() => {
        setAffectedNodes(prev => [...prev, nodeId]);
      }, index * 200);
    });

    // After animation, show results
    setTimeout(() => {
      const sim = getSimulationByVendor(selectedVendor);
      const vendor = vendors.find(v => v.id === selectedVendor);
      
      setResults({
        blastRadius: cascade.length,
        cascadeDepth: Math.min(4, Math.ceil(cascade.length / 8)),
        propagationTime: "1.5h",
        estimatedDamage: `$${Math.round(cascade.length * 2.5)}M - $${Math.round(cascade.length * 5)}M`,
        riskLevel: cascade.length > 25 ? "critical" : cascade.length > 15 ? "high" : cascade.length > 8 ? "medium" : "low",
        aiAnalysis: `A ${vendor?.name} compromise would immediately affect ${cascade.length - 1} connected vendors through ${vendor?.category} dependencies. This would trigger compliance violations across your ${vendor?.category} cluster. The cascade analysis reveals ${Math.ceil(cascade.length / 8)} propagation waves with critical exposure in Tier 1 infrastructure.`,
      });
      setIsRunning(false);
    }, cascade.length * 200 + 500);
  };

  return (
    <Layout>
      <div className="p-6 h-[calc(100vh-0px)] flex flex-col">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <h1 className="text-2xl font-bold text-foreground mb-1">Cascade Simulation</h1>
          <p className="text-text-secondary text-sm">Simulate vendor compromise scenarios and analyze cascade impacts</p>
        </motion.div>

        {/* Three Column Layout */}
        <div className="flex-1 grid grid-cols-[280px_1fr_320px] gap-4 min-h-0">
          {/* Left - Vendor Selector */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="flex flex-col gap-4"
          >
            <VendorSelector
              selectedVendor={selectedVendor}
              onSelect={setSelectedVendor}
            />
            
            {/* Run Button */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={runSimulation}
              disabled={!selectedVendor || isRunning}
              className={cn(
                "w-full py-4 rounded-lg font-semibold flex items-center justify-center gap-2 transition-all duration-200",
                selectedVendor && !isRunning
                  ? "bg-gradient-to-r from-primary to-primary/80 text-primary-foreground shadow-lg hover:shadow-glow-primary"
                  : "bg-surface-3 text-text-disabled cursor-not-allowed"
              )}
            >
              {isRunning ? (
                <>
                  <div className="w-5 h-5 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                  Simulating...
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  Run Simulation
                </>
              )}
            </motion.button>
          </motion.div>

          {/* Center - Interactive Graph */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
          >
            <SupplyChainGraph
              selectedVendor={selectedVendor}
              affectedNodes={affectedNodes}
              onNodeClick={setSelectedVendor}
              isSimulating={isRunning}
              showControls={true}
            />
          </motion.div>

          {/* Right - Analysis Results */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <AnalysisResults
              results={results}
              isLoading={isRunning}
            />
          </motion.div>
        </div>
      </div>
    </Layout>
  );
};

export default Simulation;
