import { motion } from "framer-motion";
import guardianLogo from "@/assets/guardian-logo.png";

interface LogoProps {
  size?: "sm" | "md" | "lg" | "xl";
  showText?: boolean;
  animate?: boolean;
}

const sizes = {
  sm: { img: 32, text: "text-sm" },
  md: { img: 40, text: "text-base" },
  lg: { img: 64, text: "text-xl" },
  xl: { img: 80, text: "text-2xl" },
};

const Logo = ({ size = "md", showText = true, animate = false }: LogoProps) => {
  const { img, text } = sizes[size];

  return (
    <div className="flex items-center gap-3">
      <motion.div 
        className="relative"
        initial={animate ? { scale: 0.9, opacity: 0 } : undefined}
        animate={animate ? { scale: 1, opacity: 1 } : undefined}
        transition={animate ? { duration: 0.5, ease: "easeOut" } : undefined}
      >
        <img 
          src={guardianLogo} 
          alt="Guardian AI Logo" 
          width={img} 
          height={img}
          className="object-contain"
        />
        {animate && (
          <motion.div
            className="absolute inset-0 rounded-full bg-primary/20"
            initial={{ scale: 1, opacity: 0.5 }}
            animate={{ scale: 1.5, opacity: 0 }}
            transition={{ 
              duration: 2, 
              repeat: Infinity,
              ease: "easeOut"
            }}
          />
        )}
      </motion.div>
      {showText && (
        <div>
          <h1 className={`font-bold text-foreground ${text}`}>GUARDIAN</h1>
          {size !== "sm" && (
            <p className="text-xs text-text-tertiary">Risk Intelligence</p>
          )}
        </div>
      )}
    </div>
  );
};

export default Logo;
