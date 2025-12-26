import { motion } from "framer-motion";
import { Eye, EyeOff, Filter, Layers, Shield, AlertTriangle, CheckCircle, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";

export interface GraphFilters {
  categories: {
    authentication: boolean;
    payment: boolean;
    data: boolean;
    api: boolean;
    infrastructure: boolean;
  };
  tiers: {
    1: boolean;
    2: boolean;
    3: boolean;
  };
  status: {
    secure: boolean;
    warning: boolean;
    compromised: boolean;
  };
  showLabels: boolean;
  showEdges: boolean;
}

interface GraphControlsProps {
  filters: GraphFilters;
  onFilterChange: (filters: GraphFilters) => void;
  isExpanded: boolean;
  onToggleExpand: () => void;
}

const categoryConfig = {
  authentication: { icon: "🔐", color: "bg-[#6366F1]", label: "Auth" },
  payment: { icon: "💳", color: "bg-[#F59E0B]", label: "Payment" },
  data: { icon: "📊", color: "bg-[#10B981]", label: "Data" },
  api: { icon: "⚡", color: "bg-[#3B82F6]", label: "API" },
  infrastructure: { icon: "☁️", color: "bg-[#8B5CF6]", label: "Infra" },
};

const tierConfig = {
  1: { label: "Tier 1", color: "text-critical" },
  2: { label: "Tier 2", color: "text-warning" },
  3: { label: "Tier 3", color: "text-text-secondary" },
};

const statusConfig = {
  secure: { icon: CheckCircle, color: "text-success", bg: "bg-success/20", label: "Secure" },
  warning: { icon: AlertTriangle, color: "text-warning", bg: "bg-warning/20", label: "Warning" },
  compromised: { icon: XCircle, color: "text-critical", bg: "bg-critical/20", label: "Critical" },
};

const GraphControls = ({ filters, onFilterChange, isExpanded, onToggleExpand }: GraphControlsProps) => {
  const toggleCategory = (category: keyof GraphFilters["categories"]) => {
    onFilterChange({
      ...filters,
      categories: { ...filters.categories, [category]: !filters.categories[category] },
    });
  };

  const toggleTier = (tier: 1 | 2 | 3) => {
    onFilterChange({
      ...filters,
      tiers: { ...filters.tiers, [tier]: !filters.tiers[tier] },
    });
  };

  const toggleStatus = (status: keyof GraphFilters["status"]) => {
    onFilterChange({
      ...filters,
      status: { ...filters.status, [status]: !filters.status[status] },
    });
  };

  const toggleLabels = () => {
    onFilterChange({ ...filters, showLabels: !filters.showLabels });
  };

  const toggleEdges = () => {
    onFilterChange({ ...filters, showEdges: !filters.showEdges });
  };

  const resetFilters = () => {
    onFilterChange({
      categories: { authentication: true, payment: true, data: true, api: true, infrastructure: true },
      tiers: { 1: true, 2: true, 3: true },
      status: { secure: true, warning: true, compromised: true },
      showLabels: true,
      showEdges: true,
    });
  };

  const activeFiltersCount = 
    Object.values(filters.categories).filter(v => !v).length +
    Object.values(filters.tiers).filter(v => !v).length +
    Object.values(filters.status).filter(v => !v).length;

  return (
    <div className="absolute top-4 right-4 z-20">
      {/* Toggle Button */}
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={onToggleExpand}
        className={cn(
          "flex items-center gap-2 px-3 py-2 rounded-lg transition-all duration-200",
          "bg-surface-1/90 backdrop-blur-sm border border-border hover:border-primary/30",
          isExpanded && "border-primary/50"
        )}
      >
        <Filter className="w-4 h-4 text-primary" />
        <span className="text-sm font-medium text-foreground">View</span>
        {activeFiltersCount > 0 && (
          <span className="px-1.5 py-0.5 rounded-full bg-primary text-primary-foreground text-xs font-bold">
            {activeFiltersCount}
          </span>
        )}
      </motion.button>

      {/* Expanded Controls Panel */}
      {isExpanded && (
        <motion.div
          initial={{ opacity: 0, y: -10, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -10, scale: 0.95 }}
          className="absolute top-12 right-0 w-72 bg-surface-1/95 backdrop-blur-md border border-border rounded-xl shadow-2xl overflow-hidden"
        >
          {/* Header */}
          <div className="px-4 py-3 border-b border-border flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-primary" />
              <span className="font-semibold text-foreground text-sm">Graph View</span>
            </div>
            <button
              onClick={resetFilters}
              className="text-xs text-text-tertiary hover:text-primary transition-colors"
            >
              Reset
            </button>
          </div>

          <div className="p-4 space-y-5">
            {/* Categories */}
            <div>
              <p className="text-xs font-medium text-text-tertiary uppercase tracking-wide mb-2">Categories</p>
              <div className="flex flex-wrap gap-1.5">
                {Object.entries(categoryConfig).map(([key, config]) => {
                  const isActive = filters.categories[key as keyof GraphFilters["categories"]];
                  return (
                    <button
                      key={key}
                      onClick={() => toggleCategory(key as keyof GraphFilters["categories"])}
                      className={cn(
                        "flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs font-medium transition-all",
                        isActive
                          ? "bg-surface-3 text-foreground border border-transparent"
                          : "bg-surface-2/50 text-text-disabled border border-border/50 opacity-50"
                      )}
                    >
                      <span className="text-sm">{config.icon}</span>
                      <span>{config.label}</span>
                      {isActive ? (
                        <Eye className="w-3 h-3 ml-0.5 text-success" />
                      ) : (
                        <EyeOff className="w-3 h-3 ml-0.5" />
                      )}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Tiers */}
            <div>
              <p className="text-xs font-medium text-text-tertiary uppercase tracking-wide mb-2">Tiers</p>
              <div className="flex gap-2">
                {([1, 2, 3] as const).map((tier) => {
                  const isActive = filters.tiers[tier];
                  const config = tierConfig[tier];
                  return (
                    <button
                      key={tier}
                      onClick={() => toggleTier(tier)}
                      className={cn(
                        "flex-1 px-3 py-2 rounded-lg text-xs font-semibold transition-all border",
                        isActive
                          ? "bg-surface-3 border-transparent " + config.color
                          : "bg-surface-2/50 border-border/50 text-text-disabled opacity-50"
                      )}
                    >
                      {config.label}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Status */}
            <div>
              <p className="text-xs font-medium text-text-tertiary uppercase tracking-wide mb-2">Status</p>
              <div className="flex gap-2">
                {Object.entries(statusConfig).map(([key, config]) => {
                  const isActive = filters.status[key as keyof GraphFilters["status"]];
                  const Icon = config.icon;
                  return (
                    <button
                      key={key}
                      onClick={() => toggleStatus(key as keyof GraphFilters["status"])}
                      className={cn(
                        "flex-1 flex items-center justify-center gap-1.5 px-2 py-2 rounded-lg text-xs font-medium transition-all border",
                        isActive
                          ? `${config.bg} border-transparent ${config.color}`
                          : "bg-surface-2/50 border-border/50 text-text-disabled opacity-50"
                      )}
                    >
                      <Icon className="w-3.5 h-3.5" />
                      <span>{config.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Display Options */}
            <div className="pt-2 border-t border-border">
              <p className="text-xs font-medium text-text-tertiary uppercase tracking-wide mb-2">Display</p>
              <div className="flex gap-2">
                <button
                  onClick={toggleLabels}
                  className={cn(
                    "flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-all border",
                    filters.showLabels
                      ? "bg-primary/10 border-primary/30 text-primary"
                      : "bg-surface-2/50 border-border/50 text-text-disabled"
                  )}
                >
                  {filters.showLabels ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
                  Labels
                </button>
                <button
                  onClick={toggleEdges}
                  className={cn(
                    "flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-all border",
                    filters.showEdges
                      ? "bg-primary/10 border-primary/30 text-primary"
                      : "bg-surface-2/50 border-border/50 text-text-disabled"
                  )}
                >
                  {filters.showEdges ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
                  Edges
                </button>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default GraphControls;
