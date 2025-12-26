import { motion } from "framer-motion";
import Layout from "@/components/Layout";
import { Shield, AlertTriangle, Activity, TrendingDown, Users, Clock, CheckCircle, AlertCircle, PlusCircle, MinusCircle, Zap } from "lucide-react";
import { dashboardMetrics } from "@/data/metrics";
import { getRecentActivity } from "@/data/timeline";
import { vendors } from "@/data/vendors";
import { dependencies } from "@/data/dependencies";
import { cn } from "@/lib/utils";
import SupplyChainGraph from "@/components/SupplyChainGraph";

const iconMap: Record<string, React.ElementType> = {
  AlertTriangle,
  CheckCircle,
  AlertCircle,
  PlusCircle,
  MinusCircle,
  Shield,
  Clock,
  Activity,
  TrendingDown,
};

const MetricCard = ({ 
  title, 
  value, 
  subtitle, 
  icon: Icon, 
  trend,
  variant = "default",
  delay = 0 
}: { 
  title: string; 
  value: string | number; 
  subtitle: string; 
  icon: React.ElementType;
  trend?: { value: number; positive: boolean };
  variant?: "default" | "danger" | "warning" | "success";
  delay?: number;
}) => {
  const variantStyles = {
    default: "border-border hover:border-primary/30",
    danger: "border-critical/30 hover:border-critical/50",
    warning: "border-warning/30 hover:border-warning/50",
    success: "border-success/30 hover:border-success/50",
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay, ease: "easeOut" }}
      className={cn(
        "bg-surface-1 rounded-lg p-5 border hover:shadow-card-hover hover:-translate-y-0.5 transition-all duration-200 cursor-pointer group",
        variantStyles[variant]
      )}
    >
      <div className="flex items-start justify-between mb-3">
        <div className={cn(
          "w-10 h-10 rounded-lg flex items-center justify-center transition-colors",
          variant === "danger" && "bg-critical/10 group-hover:bg-critical/20",
          variant === "warning" && "bg-warning/10 group-hover:bg-warning/20",
          variant === "success" && "bg-success/10 group-hover:bg-success/20",
          variant === "default" && "bg-primary/10 group-hover:bg-primary/20"
        )}>
          <Icon className={cn(
            "w-5 h-5",
            variant === "danger" && "text-critical",
            variant === "warning" && "text-warning",
            variant === "success" && "text-success",
            variant === "default" && "text-primary"
          )} />
        </div>
        {trend && (
          <div className={cn(
            "flex items-center gap-1 text-sm font-medium px-2 py-0.5 rounded-full",
            trend.positive ? "bg-success/10 text-success" : "bg-critical/10 text-critical"
          )}>
            <TrendingDown className={cn("w-3 h-3", trend.positive && "rotate-180")} />
            <span>{Math.abs(trend.value)}%</span>
          </div>
        )}
      </div>
      <h3 className="text-text-tertiary text-sm mb-1">{title}</h3>
      <p className="text-3xl font-bold text-foreground mb-0.5">{value}</p>
      <p className="text-text-tertiary text-xs">{subtitle}</p>
    </motion.div>
  );
};

const Dashboard = () => {
  const activity = getRecentActivity(6);
  const highRiskVendors = vendors.filter(v => v.riskScore >= 40 || v.status === 'warning').slice(0, 5);

  return (
    <Layout>
      <div className="p-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, ease: "easeOut" }}
          className="mb-6"
        >
          <h1 className="text-2xl font-bold text-foreground mb-1">Supply Chain Overview</h1>
          <p className="text-text-secondary text-sm">Real-time risk intelligence across your vendor ecosystem</p>
        </motion.div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <MetricCard
            title="Total Vendors"
            value={dashboardMetrics.current.totalVendors}
            subtitle="Across all tiers"
            icon={Users}
            delay={0.1}
          />
          <MetricCard
            title="Critical Vendors"
            value={dashboardMetrics.current.criticalVendors}
            subtitle="Tier 1 dependencies"
            icon={Shield}
            variant="danger"
            delay={0.15}
          />
          <MetricCard
            title="High Risk Vendors"
            value={dashboardMetrics.current.highRiskVendors}
            subtitle="Require attention"
            icon={AlertTriangle}
            variant="warning"
            delay={0.2}
          />
          <MetricCard
            title="Overall Risk Score"
            value={dashboardMetrics.current.overallRiskScore}
            subtitle="Lower is better"
            icon={Activity}
            variant="success"
            trend={{ value: 5, positive: true }}
            delay={0.25}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Graph */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.45, delay: 0.3, ease: "easeOut" }}
            className="lg:col-span-2"
          >
            <SupplyChainGraph showControls={true} />
          </motion.div>

          {/* Activity Feed */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.35, delay: 0.35, ease: "easeOut" }}
            className="bg-surface-1 rounded-lg border border-border p-5"
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-foreground">Recent Activity</h2>
              <span className="w-2 h-2 rounded-full bg-success animate-pulse" />
            </div>
            <div className="space-y-2 max-h-[360px] overflow-auto scrollbar-custom">
              {activity.map((event, i) => {
                const IconComponent = iconMap[event.icon] || Activity;
                return (
                  <motion.div
                    key={event.id}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.2, delay: 0.4 + i * 0.05 }}
                    className="flex gap-3 p-3 rounded-lg hover:bg-surface-2 transition-colors cursor-pointer group"
                  >
                    <div className={cn(
                      "w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 transition-colors",
                      event.severity === "critical" && "bg-critical/10 group-hover:bg-critical/20",
                      event.severity === "warning" && "bg-warning/10 group-hover:bg-warning/20",
                      event.severity === "success" && "bg-success/10 group-hover:bg-success/20",
                      event.severity === "info" && "bg-info/10 group-hover:bg-info/20"
                    )}>
                      <IconComponent className={cn(
                        "w-4 h-4",
                        event.severity === "critical" && "text-critical",
                        event.severity === "warning" && "text-warning",
                        event.severity === "success" && "text-success",
                        event.severity === "info" && "text-info"
                      )} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-foreground font-medium truncate">{event.title}</p>
                      <p className="text-xs text-text-tertiary">{event.details}</p>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        </div>

        {/* High Risk Vendors */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, delay: 0.5 }}
          className="mt-4 bg-surface-1 rounded-lg border border-border p-5"
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-foreground">High Risk Vendors</h2>
            <span className="text-xs text-text-tertiary">{highRiskVendors.length} vendors require attention</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
            {highRiskVendors.map((vendor, i) => (
              <motion.div
                key={vendor.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.55 + i * 0.05 }}
                className="p-4 rounded-lg bg-surface-2 border border-warning/20 hover:border-warning/40 transition-all hover:-translate-y-0.5 cursor-pointer"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-foreground">{vendor.name}</span>
                  <span className={cn(
                    "text-xs px-2 py-0.5 rounded-full font-medium",
                    vendor.riskScore >= 50 ? "bg-critical/10 text-critical-light" : "bg-warning/10 text-warning-light"
                  )}>
                    {vendor.riskScore}
                  </span>
                </div>
                <p className="text-xs text-text-tertiary capitalize">{vendor.category} • Tier {vendor.tier}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </Layout>
  );
};

export default Dashboard;
