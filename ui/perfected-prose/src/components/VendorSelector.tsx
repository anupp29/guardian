import { motion } from "framer-motion";
import { vendors, Vendor } from "@/data/vendors";
import { cn } from "@/lib/utils";
import { ChevronRight, Shield, CreditCard, Database, Zap, Cloud } from "lucide-react";

interface VendorSelectorProps {
  selectedVendor: string | null;
  onSelect: (vendorId: string) => void;
}

const categoryIcons: Record<string, React.ElementType> = {
  authentication: Shield,
  payment: CreditCard,
  data: Database,
  api: Zap,
  infrastructure: Cloud,
};

const VendorSelector = ({ selectedVendor, onSelect }: VendorSelectorProps) => {
  const tier1Vendors = vendors.filter(v => v.tier === 1);

  return (
    <div className="bg-surface-1 rounded-lg border border-border h-full flex flex-col">
      <div className="p-4 border-b border-border">
        <h2 className="text-lg font-semibold text-foreground">Select Vendor</h2>
        <p className="text-xs text-text-tertiary mt-1">Choose a Tier 1 vendor to simulate</p>
      </div>
      
      <div className="flex-1 overflow-auto scrollbar-custom p-2">
        <div className="space-y-1">
          {tier1Vendors.map((vendor, index) => {
            const Icon = categoryIcons[vendor.category] || Shield;
            const isSelected = selectedVendor === vendor.id;
            
            return (
              <motion.button
                key={vendor.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                onClick={() => onSelect(vendor.id)}
                className={cn(
                  "w-full flex items-center gap-3 px-3 py-3 rounded-lg transition-all duration-200 group",
                  isSelected 
                    ? "bg-primary/10 border border-primary/30" 
                    : "hover:bg-surface-2 border border-transparent"
                )}
              >
                <div className={cn(
                  "w-10 h-10 rounded-lg flex items-center justify-center transition-colors",
                  isSelected ? "bg-primary/20" : "bg-surface-2 group-hover:bg-surface-3"
                )}>
                  <Icon className={cn(
                    "w-5 h-5",
                    isSelected ? "text-primary" : "text-text-tertiary group-hover:text-text-secondary",
                    vendor.status === "warning" && "text-warning"
                  )} />
                </div>
                
                <div className="flex-1 text-left">
                  <p className={cn(
                    "font-medium text-sm",
                    isSelected ? "text-primary" : "text-foreground"
                  )}>
                    {vendor.name}
                  </p>
                  <p className="text-xs text-text-tertiary capitalize">
                    Tier {vendor.tier} • {vendor.category}
                  </p>
                </div>
                
                <ChevronRight className={cn(
                  "w-4 h-4 transition-all",
                  isSelected ? "text-primary translate-x-0 opacity-100" : "text-text-tertiary -translate-x-2 opacity-0 group-hover:translate-x-0 group-hover:opacity-100"
                )} />
              </motion.button>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default VendorSelector;
