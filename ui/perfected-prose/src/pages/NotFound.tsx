import { useLocation, useNavigate } from "react-router-dom";
import { useEffect } from "react";
import { motion } from "framer-motion";
import { Home, ArrowLeft, AlertCircle } from "lucide-react";
import Logo from "@/components/Logo";

const NotFound = () => {
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    console.error("404 Error: User attempted to access non-existent route:", location.pathname);
  }, [location.pathname]);

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center relative overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0 bg-mesh opacity-40" />
      
      {/* Animated grid */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0" style={{
          backgroundImage: `linear-gradient(rgba(99, 102, 241, 0.3) 1px, transparent 1px),
                           linear-gradient(90deg, rgba(99, 102, 241, 0.3) 1px, transparent 1px)`,
          backgroundSize: '50px 50px',
        }} />
      </div>

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center text-center px-6 max-w-lg">
        {/* Logo */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4 }}
          className="mb-6"
        >
          <Logo size="md" showText={false} />
        </motion.div>

        {/* Error Icon */}
        <motion.div
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.1, type: "spring" }}
          className="w-24 h-24 rounded-2xl bg-critical/10 border border-critical/20 flex items-center justify-center mb-6"
        >
          <AlertCircle className="w-12 h-12 text-critical" />
        </motion.div>

        {/* 404 Text */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.2 }}
          className="text-7xl font-extrabold tracking-tight mb-4"
        >
          <span className="text-gradient-primary">4</span>
          <span className="text-foreground">0</span>
          <span className="text-gradient-primary">4</span>
        </motion.h1>

        {/* Message */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.3 }}
          className="text-text-secondary text-lg mb-3"
        >
          Route Not Found
        </motion.p>
        
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="text-text-tertiary text-sm mb-8"
        >
          The path <code className="px-2 py-1 bg-surface-2 rounded text-primary font-mono text-xs">{location.pathname}</code> doesn't exist in our network.
        </motion.p>

        {/* Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.5 }}
          className="flex items-center gap-3"
        >
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => navigate(-1)}
            className="px-5 py-2.5 rounded-lg font-medium text-sm bg-surface-2 border border-border text-foreground hover:border-primary/30 transition-all flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Go Back
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.02, y: -1 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => navigate("/dashboard")}
            className="px-6 py-2.5 rounded-lg font-medium text-sm bg-gradient-to-r from-primary to-primary/80 text-primary-foreground shadow-md hover:shadow-glow-primary transition-all flex items-center gap-2"
          >
            <Home className="w-4 h-4" />
            Dashboard
          </motion.button>
        </motion.div>
      </div>

      {/* Footer */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.7 }}
        className="absolute bottom-8 text-text-tertiary text-xs"
      >
        Guardian AI • Supply Chain Risk Intelligence
      </motion.p>
    </div>
  );
};

export default NotFound;
