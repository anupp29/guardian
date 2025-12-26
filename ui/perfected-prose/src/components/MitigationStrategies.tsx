import { motion } from "framer-motion";
import { Shield, AlertCircle, Clock, DollarSign, Target, TrendingUp } from "lucide-react";
import { cn } from "@/lib/utils";
import { MitigationStrategy } from "@/api/types";

interface MitigationStrategiesProps {
    strategies: MitigationStrategy[];
    isLoading?: boolean;
}

const effectivenessColors = {
    very_high: { bg: "bg-success/10", text: "text-success", border: "border-success/30" },
    high: { bg: "bg-info/10", text: "text-info", border: "border-info/30" },
    medium: { bg: "bg-warning/10", text: "text-warning", border: "border-warning/30" },
    low: { bg: "bg-critical/10", text: "text-critical", border: "border-critical/30" },
};

const categoryIcons: Record<string, React.ElementType> = {
    redundancy: Shield,
    hardening: AlertCircle,
    authentication: Shield,
    payment: DollarSign,
    data: Target,
};

const MitigationStrategies = ({ strategies, isLoading }: MitigationStrategiesProps) => {
    if (isLoading) {
        return (
            <div className="bg-surface-1 rounded-lg border border-border p-6">
                <div className="flex items-center justify-center h-40">
                    <div className="w-8 h-8 border-4 border-primary/30 border-t-primary rounded-full animate-spin" />
                </div>
            </div>
        );
    }

    return (
        <div className="bg-surface-1 rounded-lg border border-border p-6">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="text-xl font-bold text-foreground">Mitigation Strategies</h2>
                    <p className="text-sm text-text-tertiary mt-1">Recommended actions to reduce supply chain risk</p>
                </div>
                <div className="flex items-center gap-2 text-xs text-text-tertiary">
                    <TrendingUp className="w-4 h-4 text-success" />
                    <span>{strategies.length} strategies identified</span>
                </div>
            </div>

            <div className="space-y-3">
                {strategies.map((strategy, index) => {
                    const Icon = categoryIcons[strategy.category] || Shield;
                    const colors = effectivenessColors[strategy.effectiveness];

                    return (
                        <motion.div
                            key={strategy.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.05 }}
                            className="group relative bg-surface-2 rounded-lg border border-border hover:border-primary/40 transition-all duration-200 p-4 cursor-pointer"
                        >
                            {/* Priority Badge */}
                            <div className="absolute top-3 right-3">
                                <span className={cn(
                                    "px-2 py-0.5 rounded-full text-xs font-medium",
                                    strategy.priority <= 2 ? "bg-critical/20 text-critical-light border border-critical/30" :
                                        strategy.priority <= 4 ? "bg-warning/20 text-warning-light border border-warning/30" :
                                            "bg-info/20 text-info-light border border-info/30"
                                )}>
                                    P{strategy.priority}
                                </span>
                            </div>

                            <div className="flex items-start gap-4">
                                {/* Icon */}
                                <div className={cn(
                                    "w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0 transition-colors",
                                    colors.bg, "border", colors.border
                                )}>
                                    <Icon className={cn("w-6 h-6", colors.text)} />
                                </div>

                                {/* Content */}
                                <div className="flex-1 min-w-0">
                                    <h3 className="font-semibold text-foreground mb-1 group-hover:text-primary transition-colors">
                                        {strategy.title}
                                    </h3>
                                    <p className="text-sm text-text-tertiary line-clamp-2 mb-3">
                                        {strategy.description}
                                    </p>

                                    {/* Stats */}
                                    <div className="flex flex-wrap items-center gap-4 text-xs">
                                        <div className="flex items-center gap-1.5">
                                            <Target className="w-3.5 h-3.5 text-success" />
                                            <span className="text-text-secondary">
                                                <span className="font-semibold text-success">{strategy.riskReduction}%</span> risk reduction
                                            </span>
                                        </div>

                                        <div className="flex items-center gap-1.5">
                                            <Clock className="w-3.5 h-3.5 text-text-tertiary" />
                                            <span className="text-text-secondary">{strategy.implementationTime}</span>
                                        </div>

                                        <div className="flex items-center gap-1.5">
                                            <DollarSign className="w-3.5 h-3.5 text-text-tertiary" />
                                            <span className="text-text-secondary">{strategy.cost}</span>
                                        </div>

                                        <div className="flex items-center gap-1.5">
                                            <span className="text-text-secondary">
                                                Affects <span className="font-semibold text-foreground">{strategy.affectedVendors}</span> vendors
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    );
                })}
            </div>
        </div>
    );
};

export default MitigationStrategies;
