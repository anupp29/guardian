import { motion, AnimatePresence } from "framer-motion";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { LayoutDashboard, Activity, ShieldCheck, Info, ChevronRight, Home, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import Logo from "./Logo";

const navItems = [
  { icon: LayoutDashboard, label: "Dashboard", path: "/dashboard", description: "Overview & metrics" },
  { icon: Activity, label: "Simulation", path: "/simulation", description: "Cascade analysis" },
  { icon: ShieldCheck, label: "Mitigation", path: "/mitigation", description: "Risk strategies" },
  { icon: Info, label: "About", path: "/about", description: "Platform info" },
];

interface LayoutProps {
  children: React.ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background flex">
      {/* Sidebar */}
      <motion.aside
        initial={{ x: -100, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.35, ease: "easeOut" }}
        className="w-64 bg-surface-1 border-r border-border flex flex-col fixed h-full z-40"
      >
        {/* Logo */}
        <div className="p-5 border-b border-border">
          <button onClick={() => navigate("/dashboard")} className="block w-full">
            <Logo size="md" showText={true} />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-3 overflow-y-auto scrollbar-custom">
          <ul className="space-y-1">
            {navItems.map((item, index) => {
              const isActive = location.pathname === item.path;
              return (
                <motion.li 
                  key={item.path}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 + index * 0.05 }}
                >
                  <Link
                    to={item.path}
                    className={cn(
                      "flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 group relative",
                      isActive
                        ? "bg-primary/10 text-primary"
                        : "text-text-secondary hover:bg-surface-2 hover:text-foreground"
                    )}
                  >
                    {isActive && (
                      <motion.div
                        layoutId="activeTab"
                        className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-primary rounded-r-full"
                        transition={{ type: "spring", bounce: 0.2, duration: 0.4 }}
                      />
                    )}
                    <item.icon className={cn(
                      "w-5 h-5 transition-colors flex-shrink-0",
                      isActive && "text-primary"
                    )} />
                    <div className="flex-1 min-w-0">
                      <span className="font-medium block">{item.label}</span>
                      <span className={cn(
                        "text-xs transition-colors",
                        isActive ? "text-primary/70" : "text-text-tertiary"
                      )}>{item.description}</span>
                    </div>
                    {isActive && <ChevronRight className="w-4 h-4 flex-shrink-0" />}
                  </Link>
                </motion.li>
              );
            })}
          </ul>
        </nav>

        {/* Footer */}
        <div className="p-3 border-t border-border space-y-2">
          {/* AI Status */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="px-4 py-3 rounded-lg bg-gradient-to-r from-primary/5 to-transparent border border-primary/10"
          >
            <div className="flex items-center gap-2 mb-1">
              <Sparkles className="w-3.5 h-3.5 text-primary" />
              <p className="text-xs text-text-tertiary font-medium">GenAI Engine</p>
            </div>
            <p className="text-sm text-foreground font-medium">Ready for Analysis</p>
          </motion.div>

          {/* System Status */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.45 }}
            className="px-4 py-2.5 rounded-lg bg-surface-2"
          >
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-success animate-pulse-glow" />
              <span className="text-xs text-success-light font-medium">All Systems Operational</span>
            </div>
          </motion.div>
        </div>
      </motion.aside>

      {/* Main content with left margin for fixed sidebar */}
      <main className="flex-1 ml-64 overflow-auto">
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            className="bg-mesh min-h-screen"
          >
            {children}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
};

export default Layout;
