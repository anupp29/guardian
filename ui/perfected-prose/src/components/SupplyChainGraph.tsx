import { useEffect, useRef, useState, useCallback } from "react";
import cytoscape, { Core, NodeSingular } from "cytoscape";
import { motion, AnimatePresence } from "framer-motion";
import { vendors, Vendor } from "@/data/vendors";
import { dependencies } from "@/data/dependencies";
import { X, ZoomIn, ZoomOut, Maximize2, Target, RotateCcw } from "lucide-react";
import GraphControls, { GraphFilters } from "./GraphControls";

interface SupplyChainGraphProps {
  selectedVendor?: string | null;
  affectedNodes?: string[];
  onNodeClick?: (vendorId: string) => void;
  isSimulating?: boolean;
  showControls?: boolean;
  compact?: boolean;
}

// Semantic color palette matching design system (HSL values)
const CATEGORY_COLORS = {
  authentication: { main: "#6366F1", light: "#818CF8", glow: "rgba(99, 102, 241, 0.4)" },  // Indigo
  payment: { main: "#F59E0B", light: "#FBBF24", glow: "rgba(245, 158, 11, 0.4)" },         // Amber
  data: { main: "#10B981", light: "#34D399", glow: "rgba(16, 185, 129, 0.4)" },            // Emerald
  api: { main: "#3B82F6", light: "#60A5FA", glow: "rgba(59, 130, 246, 0.4)" },             // Blue
  infrastructure: { main: "#8B5CF6", light: "#A78BFA", glow: "rgba(139, 92, 246, 0.4)" }, // Violet
};

const STATUS_COLORS = {
  secure: { main: "#10B981", border: "#34D399" },      // Emerald
  warning: { main: "#F59E0B", border: "#FBBF24" },     // Amber
  compromised: { main: "#DC2626", border: "#FCA5A5" }, // Red
};

const TIER_SIZES = {
  1: { base: 48, selected: 56 },
  2: { base: 40, selected: 48 },
  3: { base: 32, selected: 40 },
};

const categoryIcons: Record<string, string> = {
  authentication: "🔐",
  payment: "💳",
  data: "📊",
  api: "⚡",
  infrastructure: "☁️",
};

const getNodeColor = (category: string, status: string, isSource: boolean, isAffected: boolean) => {
  if (isSource) return STATUS_COLORS.compromised.main;
  if (status === "compromised") return STATUS_COLORS.compromised.main;
  if (isAffected) return STATUS_COLORS.warning.main;
  return CATEGORY_COLORS[category as keyof typeof CATEGORY_COLORS]?.main || "#10B981";
};

const getBorderColor = (status: string, isSelected: boolean, isSource: boolean, isAffected: boolean) => {
  if (isSource) return STATUS_COLORS.compromised.border;
  if (isAffected) return STATUS_COLORS.warning.border;
  if (isSelected) return "#6366F1";
  
  switch (status) {
    case "compromised": return STATUS_COLORS.compromised.border;
    case "warning": return STATUS_COLORS.warning.border;
    default: return "rgba(255,255,255,0.15)";
  }
};

const defaultFilters: GraphFilters = {
  categories: { authentication: true, payment: true, data: true, api: true, infrastructure: true },
  tiers: { 1: true, 2: true, 3: true },
  status: { secure: true, warning: true, compromised: true },
  showLabels: true,
  showEdges: true,
};

const SupplyChainGraph = ({ 
  selectedVendor, 
  affectedNodes = [],
  onNodeClick,
  isSimulating = false,
  showControls = true,
  compact = false,
}: SupplyChainGraphProps) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const [hoveredNode, setHoveredNode] = useState<Vendor | null>(null);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });
  const [stats, setStats] = useState({ healthy: 0, warning: 0, critical: 0 });
  const [filters, setFilters] = useState<GraphFilters>(defaultFilters);
  const [isFilterExpanded, setIsFilterExpanded] = useState(false);

  // Calculate stats
  useEffect(() => {
    const healthy = vendors.filter(v => v.status === "secure" && !affectedNodes.includes(v.id)).length;
    const warning = vendors.filter(v => v.status === "warning" || (affectedNodes.includes(v.id) && v.id !== selectedVendor)).length;
    const critical = vendors.filter(v => v.status === "compromised" || v.id === selectedVendor).length;
    setStats({ healthy, warning, critical });
  }, [affectedNodes, selectedVendor]);

  // Filter vendors
  const getFilteredVendors = useCallback(() => {
    return vendors.filter(v => {
      if (!filters.categories[v.category]) return false;
      if (!filters.tiers[v.tier]) return false;
      const effectiveStatus = affectedNodes.includes(v.id) ? "warning" : v.status;
      if (v.id === selectedVendor) return filters.status.compromised;
      if (!filters.status[effectiveStatus as keyof typeof filters.status]) return false;
      return true;
    });
  }, [filters, affectedNodes, selectedVendor]);

  const initGraph = useCallback(() => {
    if (!containerRef.current) return;

    const filteredVendors = getFilteredVendors();
    const filteredVendorIds = new Set(filteredVendors.map(v => v.id));

    // Create nodes from filtered vendors
    const nodes = filteredVendors.map((vendor) => {
      const isAffected = affectedNodes.includes(vendor.id);
      const isSelected = selectedVendor === vendor.id;
      const isSource = isSimulating && selectedVendor === vendor.id;
      
      return {
        data: {
          id: vendor.id,
          label: filters.showLabels ? vendor.name : "",
          category: vendor.category,
          tier: vendor.tier,
          status: isSource ? "compromised" : isAffected ? "warning" : vendor.status,
          riskScore: vendor.riskScore,
          isSelected,
          isAffected,
          isSource,
        },
      };
    });

    // Create edges from dependencies (only if both nodes visible)
    const edges = filters.showEdges 
      ? dependencies
          .filter(dep => filteredVendorIds.has(dep.source) && filteredVendorIds.has(dep.target))
          .map((dep) => ({
            data: {
              id: dep.id,
              source: dep.source,
              target: dep.target,
              strength: dep.strength,
              isAffectedPath: affectedNodes.includes(dep.source) && affectedNodes.includes(dep.target),
            },
          }))
      : [];

    // Destroy existing instance
    if (cyRef.current) {
      cyRef.current.destroy();
    }

    // Initialize Cytoscape
    cyRef.current = cytoscape({
      container: containerRef.current,
      elements: { nodes, edges },
      style: [
        {
          selector: "node",
          style: {
            "background-color": (ele) => getNodeColor(
              ele.data("category"), 
              ele.data("status"),
              ele.data("isSource"),
              ele.data("isAffected")
            ),
            "border-width": (ele) => {
              if (ele.data("isSource") || ele.data("isAffected")) return 3;
              if (ele.data("status") === "warning") return 2.5;
              return 2;
            },
            "border-color": (ele) => getBorderColor(
              ele.data("status"),
              ele.data("isSelected"),
              ele.data("isSource"),
              ele.data("isAffected")
            ),
            width: (ele) => {
              const tier = ele.data("tier") as 1 | 2 | 3;
              const sizes = TIER_SIZES[tier] || TIER_SIZES[3];
              return ele.data("isSource") || ele.data("isSelected") ? sizes.selected : sizes.base;
            },
            height: (ele) => {
              const tier = ele.data("tier") as 1 | 2 | 3;
              const sizes = TIER_SIZES[tier] || TIER_SIZES[3];
              return ele.data("isSource") || ele.data("isSelected") ? sizes.selected : sizes.base;
            },
            label: "data(label)",
            "font-size": compact ? "8px" : "10px",
            "font-family": "Inter, sans-serif",
            "font-weight": 500,
            color: "#E5E7EB",
            "text-valign": "bottom",
            "text-margin-y": 8,
            "text-background-color": "#111827",
            "text-background-opacity": 0.85,
            "text-background-padding": "3px",
            "text-background-shape": "roundrectangle",
            "overlay-opacity": 0,
            "transition-property": "background-color, border-color, width, height, border-width",
            "transition-duration": "250ms",
          } as any,
        },
        {
          selector: "node:active",
          style: {
            "overlay-opacity": 0,
          },
        },
        {
          selector: "edge",
          style: {
            width: (ele) => Math.max(1, ele.data("strength") * 2.5),
            "line-color": (ele) => {
              if (ele.data("isAffectedPath")) return "#F59E0B";
              return "rgba(99, 102, 241, 0.12)";
            },
            "target-arrow-color": (ele) => {
              if (ele.data("isAffectedPath")) return "#F59E0B";
              return "rgba(99, 102, 241, 0.25)";
            },
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
            opacity: (ele) => ele.data("isAffectedPath") ? 1 : 0.5,
            "arrow-scale": 0.7,
            "transition-property": "line-color, opacity, width",
            "transition-duration": "300ms",
          } as any,
        },
        {
          selector: ".highlighted",
          style: {
            "border-width": 4,
            "border-color": "#6366F1",
          } as any,
        },
        {
          selector: ".faded",
          style: {
            opacity: 0.3,
          } as any,
        },
      ],
      layout: {
        name: "cose",
        idealEdgeLength: compact ? 100 : 140,
        nodeOverlap: 25,
        refresh: 20,
        fit: true,
        padding: compact ? 25 : 50,
        randomize: false,
        componentSpacing: compact ? 80 : 120,
        nodeRepulsion: compact ? 6000 : 9000,
        edgeElasticity: 80,
        nestingFactor: 5,
        gravity: 60,
        numIter: 1000,
        initialTemp: 200,
        coolingFactor: 0.95,
        minTemp: 1.0,
        animate: true,
        animationDuration: 400,
      } as any,
      wheelSensitivity: 0.15,
      minZoom: 0.25,
      maxZoom: 3,
    });

    // Event handlers
    cyRef.current.on("tap", "node", (evt) => {
      const nodeId = evt.target.id();
      onNodeClick?.(nodeId);
    });

    cyRef.current.on("mouseover", "node", (evt) => {
      const node = evt.target as NodeSingular;
      const vendor = vendors.find(v => v.id === node.id());
      if (vendor) {
        const renderedPos = node.renderedPosition();
        setHoveredNode(vendor);
        setTooltipPos({ x: renderedPos.x, y: renderedPos.y });
        node.addClass("highlighted");
        
        // Highlight connected edges
        node.connectedEdges().style({
          "line-color": CATEGORY_COLORS[vendor.category as keyof typeof CATEGORY_COLORS]?.main || "#6366F1",
          opacity: 1,
        });

        // Fade unconnected nodes
        const connectedNodeIds = new Set([node.id()]);
        node.connectedEdges().forEach(edge => {
          connectedNodeIds.add(edge.source().id());
          connectedNodeIds.add(edge.target().id());
        });
        
        cyRef.current?.nodes().forEach(n => {
          if (!connectedNodeIds.has(n.id())) {
            n.addClass("faded");
          }
        });
      }
    });

    cyRef.current.on("mouseout", "node", (evt) => {
      const node = evt.target as NodeSingular;
      setHoveredNode(null);
      node.removeClass("highlighted");
      
      // Reset edge styles
      node.connectedEdges().style({
        "line-color": "rgba(99, 102, 241, 0.12)",
        opacity: 0.5,
      });

      // Remove faded class
      cyRef.current?.nodes().removeClass("faded");
    });

  }, [selectedVendor, affectedNodes, isSimulating, onNodeClick, filters, compact, getFilteredVendors]);

  useEffect(() => {
    initGraph();
    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
      }
    };
  }, [initGraph]);

  // Animate affected nodes during simulation
  useEffect(() => {
    if (!cyRef.current || !isSimulating) return;

    const animateNodes = () => {
      affectedNodes.forEach((nodeId, index) => {
        setTimeout(() => {
          const node = cyRef.current?.getElementById(nodeId);
          if (node && node.length > 0) {
            node.animate({
              style: {
                "border-width": 5,
                "border-color": "#F59E0B",
              } as any,
            }, {
              duration: 300,
              easing: "ease-out" as any,
            });
          }
        }, index * 120);
      });
    };

    animateNodes();
  }, [affectedNodes, isSimulating]);

  const handleZoomIn = () => cyRef.current?.zoom(cyRef.current.zoom() * 1.3);
  const handleZoomOut = () => cyRef.current?.zoom(cyRef.current.zoom() / 1.3);
  const handleFit = () => cyRef.current?.fit(undefined, 40);
  const handleReset = () => {
    setFilters(defaultFilters);
    setTimeout(() => cyRef.current?.fit(undefined, 40), 100);
  };
  const handleCenter = () => {
    if (selectedVendor && cyRef.current) {
      const node = cyRef.current.getElementById(selectedVendor);
      if (node && node.length > 0) {
        cyRef.current.center(node);
        cyRef.current.zoom(1.5);
      }
    }
  };

  return (
    <div className="relative w-full h-full min-h-[400px] bg-surface-2 rounded-xl overflow-hidden border border-border">
      {/* Header Stats */}
      <div className="absolute top-4 left-4 z-10">
        <div className="flex items-center gap-3">
          <span className="text-sm text-text-tertiary font-medium flex items-center gap-1.5">
            <span className="text-primary">⚡</span> Supply Chain
          </span>
          <div className="h-4 w-px bg-border" />
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-success/15 text-success border border-success/20">
              {stats.healthy}
            </span>
            <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-warning/15 text-warning border border-warning/20">
              {stats.warning}
            </span>
            <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-critical/15 text-critical border border-critical/20">
              {stats.critical}
            </span>
          </div>
        </div>
      </div>

      {/* View Controls */}
      {showControls && (
        <GraphControls
          filters={filters}
          onFilterChange={setFilters}
          isExpanded={isFilterExpanded}
          onToggleExpand={() => setIsFilterExpanded(!isFilterExpanded)}
        />
      )}

      {/* Graph Container */}
      <div 
        ref={containerRef} 
        className="w-full h-full cursor-grab active:cursor-grabbing"
        style={{ minHeight: compact ? "300px" : "400px" }}
      />

      {/* Zoom Controls */}
      {showControls && (
        <div className="absolute bottom-4 right-4 flex flex-col gap-1.5 z-10">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleZoomIn}
            className="w-9 h-9 rounded-lg bg-surface-1/90 backdrop-blur-sm border border-border flex items-center justify-center text-text-secondary hover:text-foreground hover:border-primary/40 transition-all"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleZoomOut}
            className="w-9 h-9 rounded-lg bg-surface-1/90 backdrop-blur-sm border border-border flex items-center justify-center text-text-secondary hover:text-foreground hover:border-primary/40 transition-all"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleFit}
            className="w-9 h-9 rounded-lg bg-surface-1/90 backdrop-blur-sm border border-border flex items-center justify-center text-text-secondary hover:text-foreground hover:border-primary/40 transition-all"
            title="Fit to View"
          >
            <Maximize2 className="w-4 h-4" />
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleReset}
            className="w-9 h-9 rounded-lg bg-surface-1/90 backdrop-blur-sm border border-border flex items-center justify-center text-text-secondary hover:text-foreground hover:border-primary/40 transition-all"
            title="Reset View"
          >
            <RotateCcw className="w-4 h-4" />
          </motion.button>
          {selectedVendor && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleCenter}
              className="w-9 h-9 rounded-lg bg-primary/20 border border-primary/30 flex items-center justify-center text-primary hover:bg-primary/30 transition-all"
              title="Center on Selected"
            >
              <Target className="w-4 h-4" />
            </motion.button>
          )}
        </div>
      )}

      {/* Node Tooltip */}
      <AnimatePresence>
        {hoveredNode && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 10 }}
            className="absolute z-50 pointer-events-none"
            style={{
              left: tooltipPos.x,
              top: tooltipPos.y - 90,
              transform: "translateX(-50%)",
            }}
          >
            <div className="bg-surface-1/95 backdrop-blur-md border border-border rounded-xl shadow-2xl p-3.5 min-w-[200px]">
              <div className="flex items-center gap-2.5 mb-2.5">
                <div 
                  className="w-9 h-9 rounded-lg flex items-center justify-center text-lg"
                  style={{ 
                    backgroundColor: `${CATEGORY_COLORS[hoveredNode.category as keyof typeof CATEGORY_COLORS]?.main}20`,
                    border: `1px solid ${CATEGORY_COLORS[hoveredNode.category as keyof typeof CATEGORY_COLORS]?.main}40`
                  }}
                >
                  {categoryIcons[hoveredNode.category]}
                </div>
                <div>
                  <p className="font-semibold text-foreground text-sm">{hoveredNode.name}</p>
                  <p className="text-xs text-text-tertiary capitalize">{hoveredNode.category} • Tier {hoveredNode.tier}</p>
                </div>
              </div>
              <div className="flex items-center justify-between pt-2.5 border-t border-border">
                <span className="text-xs text-text-tertiary">Risk Score</span>
                <div className="flex items-center gap-2">
                  <div className="w-16 h-1.5 bg-surface-3 rounded-full overflow-hidden">
                    <div 
                      className="h-full rounded-full transition-all"
                      style={{ 
                        width: `${hoveredNode.riskScore}%`,
                        backgroundColor: hoveredNode.riskScore >= 50 ? "#DC2626" : 
                          hoveredNode.riskScore >= 30 ? "#F59E0B" : "#10B981"
                      }}
                    />
                  </div>
                  <span className={`text-sm font-bold ${
                    hoveredNode.riskScore >= 50 ? "text-critical" :
                    hoveredNode.riskScore >= 30 ? "text-warning" : "text-success"
                  }`}>
                    {hoveredNode.riskScore}
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 flex flex-wrap gap-1.5 z-10">
        {Object.entries(categoryIcons).map(([cat, icon]) => {
          const color = CATEGORY_COLORS[cat as keyof typeof CATEGORY_COLORS]?.main;
          const isFiltered = !filters.categories[cat as keyof typeof filters.categories];
          return (
            <div
              key={cat}
              className={`flex items-center gap-1.5 px-2 py-1 rounded-md bg-surface-1/80 backdrop-blur-sm border text-xs transition-all ${
                isFiltered ? "border-border/30 opacity-40" : "border-border/50"
              }`}
            >
              <div 
                className="w-2.5 h-2.5 rounded-full" 
                style={{ backgroundColor: color }}
              />
              <span className="text-text-tertiary capitalize">{cat}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default SupplyChainGraph;
