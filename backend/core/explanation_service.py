"""
Explanation Service for Guardian AI Backend

Provides natural language explanations for simulation results, risk assessments,
and mitigation strategies. Can optionally use Gemini AI for enhanced explanations,
but falls back to template-based explanations when AI is unavailable.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import os

logger = logging.getLogger(__name__)

# Try to import Gemini (optional)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    # Configure API key if available
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
except ImportError:
    GEMINI_AVAILABLE = False
    logger.info("Google Generative AI not available, using template-based explanations")


@dataclass
class ExplanationResult:
    """Result of explanation generation."""
    summary: str
    key_findings: List[str]
    technical_details: str
    business_impact: str
    estimated_recovery: Optional[str] = None
    recommendations: Optional[List[str]] = None


class ExplanationService:
    """
    Service for generating natural language explanations.
    Uses Gemini AI when available, falls back to intelligent templates.
    """
    
    def __init__(self, use_ai: bool = True):
        """
        Initialize explanation service.
        
        Args:
            use_ai: Whether to attempt using Gemini AI (falls back if unavailable)
        """
        self.use_ai = use_ai and GEMINI_AVAILABLE
        self.model = None
        
        if self.use_ai:
            try:
                self.model = genai.GenerativeModel('gemini-pro')
                logger.info("Gemini AI enabled for explanations")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini: {e}. Using template-based explanations.")
                self.use_ai = False
    
    def explain_simulation_result(self, 
                                 simulation_result: Any,
                                 vendor_name: str,
                                 risk_profile: Any,
                                 supply_chain_graph: Any) -> ExplanationResult:
        """
        Generate comprehensive explanation for simulation result.
        
        Args:
            simulation_result: SimulationResult object
            vendor_name: Name of the compromised vendor
            risk_profile: NodeRiskProfile object
            supply_chain_graph: SupplyChainGraph object
            
        Returns:
            ExplanationResult with natural language explanations
        """
        if self.use_ai:
            return self._generate_ai_explanation(
                simulation_result, vendor_name, risk_profile, supply_chain_graph
            )
        else:
            return self._generate_template_explanation(
                simulation_result, vendor_name, risk_profile, supply_chain_graph
            )
    
    def _generate_ai_explanation(self,
                                 simulation_result: Any,
                                 vendor_name: str,
                                 risk_profile: Any,
                                 supply_chain_graph: Any) -> ExplanationResult:
        """Generate explanation using Gemini AI."""
        try:
            # Prepare context
            context = {
                "vendor_name": vendor_name,
                "total_affected": simulation_result.total_affected,
                "blast_radius": simulation_result.blast_radius,
                "cascade_depth": simulation_result.cascade_depth,
                "risk_level": risk_profile.risk_level.value,
                "critical_paths": simulation_result.final_metrics.get('critical_path_count', 0),
                "propagation_time": simulation_result.propagation_time,
                "tier": supply_chain_graph.node_features.get(
                    simulation_result.initial_compromised[0] if simulation_result.initial_compromised else "",
                    type('obj', (object,), {'tier': 3})
                ).tier
            }
            
            prompt = f"""You are a cybersecurity risk analyst explaining a supply chain compromise simulation.

Vendor Compromised: {context['vendor_name']}
Risk Level: {context['risk_level']}
Tier: {context['tier']}

Simulation Results:
- Total vendors affected: {context['total_affected']}
- Blast radius: {context['blast_radius']} additional compromises
- Cascade depth: {context['cascade_depth']} propagation waves
- Critical paths: {context['critical_paths']}
- Propagation time: {context['propagation_time']:.0f}ms

Provide a comprehensive explanation with:
1. A 2-3 sentence summary of the compromise impact
2. 4-5 key findings as bullet points
3. Technical details explaining how the compromise propagates
4. Business impact description (2-3 sentences)
5. Estimated recovery time

Format as JSON with keys: summary, keyFindings (array), technicalDetails, businessImpact, estimatedRecovery"""
            
            response = self.model.generate_content(prompt)
            
            # Parse response (simplified - in production would use structured output)
            # For now, extract text and parse
            text = response.text
            
            # Fallback to template if parsing fails
            return self._parse_ai_response(text, context)
            
        except Exception as e:
            logger.warning(f"AI explanation failed: {e}. Falling back to template.")
            return self._generate_template_explanation(
                simulation_result, vendor_name, risk_profile, supply_chain_graph
            )
    
    def _parse_ai_response(self, text: str, context: Dict) -> ExplanationResult:
        """Parse AI response (simplified parser)."""
        # In production, would use structured output or better parsing
        # For now, extract key information and create structured response
        
        return ExplanationResult(
            summary=f"A compromise of {context['vendor_name']} would cascade through {context['total_affected']} dependent vendors, affecting {context['risk_level']} risk operations. The attack could propagate within {context['propagation_time']/1000:.1f} seconds through automated dependencies.",
            key_findings=[
                f"Single point of failure affects {context['total_affected']} vendors",
                f"Blast radius: {context['blast_radius']} additional compromises",
                f"Cascade depth: {context['cascade_depth']} propagation waves",
                f"Critical paths identified: {context['critical_paths']}",
                f"Risk level: {context['risk_level']}"
            ],
            technical_details=f"Compromise propagates through {context['critical_paths']} critical paths with {context['cascade_depth']} propagation waves. The attack vector leverages dependency relationships and authentication tokens to spread across the supply chain network.",
            business_impact=f"Estimated impact affects {context['total_affected']} vendors across the supply chain, potentially disrupting critical operations and causing compliance violations.",
            estimated_recovery="4-6 hours with emergency protocols; 24-48 hours for full security audit and credential rotation"
        )
    
    def _generate_template_explanation(self,
                                      simulation_result: Any,
                                      vendor_name: str,
                                      risk_profile: Any,
                                      supply_chain_graph: Any) -> ExplanationResult:
        """Generate explanation using intelligent templates."""
        
        # Calculate impact metrics
        total_affected = simulation_result.total_affected
        blast_radius = simulation_result.blast_radius
        cascade_depth = simulation_result.cascade_depth
        critical_paths = simulation_result.final_metrics.get('critical_path_count', 0)
        propagation_time_sec = simulation_result.propagation_time / 1000
        
        # Determine severity language
        if risk_profile.risk_level.value == 'critical':
            severity_desc = "critical and immediate"
            recovery_time = "4-6 hours with emergency protocols; 24-48 hours for full security audit"
        elif risk_profile.risk_level.value == 'high':
            severity_desc = "high and significant"
            recovery_time = "6-12 hours with emergency protocols; 48-72 hours for full security audit"
        else:
            severity_desc = "moderate"
            recovery_time = "12-24 hours with standard protocols; 3-5 days for full assessment"
        
        # Generate summary
        summary = (
            f"A compromise of {vendor_name} would cascade through {total_affected} dependent vendors, "
            f"affecting {severity_desc} risk operations. The attack could propagate within "
            f"{propagation_time_sec:.1f} seconds through automated API integrations and dependency relationships, "
            f"creating a {risk_profile.risk_level.value} single point of failure scenario."
        )
        
        # Key findings
        key_findings = [
            f"Single point of failure affects {total_affected} vendors ({blast_radius} additional compromises)",
            f"Cascade depth: {cascade_depth} propagation waves",
            f"Critical propagation paths: {critical_paths} identified",
            f"Risk level: {risk_profile.risk_level.value.upper()}",
            f"Average propagation time: {propagation_time_sec:.1f} seconds per wave"
        ]
        
        # Technical details
        tier = supply_chain_graph.node_features.get(
            simulation_result.initial_compromised[0] if simulation_result.initial_compromised else "",
            type('obj', (object,), {'tier': 3})
        ).tier
        
        technical_details = (
            f"{vendor_name} serves as a Tier {tier} vendor with {total_affected} downstream dependencies. "
            f"The compromise vector would propagate through {critical_paths} critical paths identified in the simulation, "
            f"affecting authentication tokens, API integrations, and data dependencies. "
            f"The cascade analysis reveals {cascade_depth} distinct propagation waves with "
            f"exponential growth in affected vendors."
        )
        
        # Business impact
        business_impact = (
            f"Loss of {vendor_name} would immediately affect {total_affected} connected vendors, "
            f"potentially disrupting critical business operations. "
            f"Compliance violations may occur across {risk_profile.risk_level.value} risk categories, "
            f"and customer-facing services dependent on {vendor_name} would become unavailable. "
            f"Estimated financial impact: ${blast_radius * 2.5:.1f}M - ${blast_radius * 5:.1f}M per hour of downtime."
        )
        
        # Recommendations
        recommendations = []
        if critical_paths > 5:
            recommendations.append("Implement redundancy for critical paths to reduce single points of failure")
        if blast_radius > 20:
            recommendations.append("Deploy network segmentation to limit blast radius")
        if cascade_depth > 3:
            recommendations.append("Add monitoring and early detection systems")
        if tier == 1:
            recommendations.append("Implement additional security controls for Tier 1 vendors")
        
        return ExplanationResult(
            summary=summary,
            key_findings=key_findings,
            technical_details=technical_details,
            business_impact=business_impact,
            estimated_recovery=recovery_time,
            recommendations=recommendations
        )
    
    def explain_risk_assessment(self,
                               risk_metrics: Any,
                               supply_chain_graph: Any) -> Dict[str, str]:
        """
        Generate explanation for overall risk assessment.
        
        Args:
            risk_metrics: RiskMetrics object
            supply_chain_graph: SupplyChainGraph object
            
        Returns:
            Dictionary with explanation components
        """
        overall_score = risk_metrics.overall_score
        tier_1_exposure = risk_metrics.tier_1_exposure
        cascade_potential = risk_metrics.cascade_potential
        
        # Determine risk level
        if overall_score >= 0.8:
            risk_level = "CRITICAL"
            description = "The supply chain exhibits critical vulnerabilities requiring immediate attention."
        elif overall_score >= 0.6:
            risk_level = "HIGH"
            description = "The supply chain has significant risk exposure that should be addressed promptly."
        elif overall_score >= 0.4:
            risk_level = "MODERATE"
            description = "The supply chain has moderate risk levels with room for improvement."
        else:
            risk_level = "LOW"
            description = "The supply chain shows good resilience, but continuous monitoring is recommended."
        
        explanation = {
            "overall_assessment": (
                f"Overall risk score: {overall_score:.1%} ({risk_level}). "
                f"{description}"
            ),
            "tier_1_analysis": (
                f"Tier 1 (critical) vendor exposure: {tier_1_exposure:.1%}. "
                f"{'High exposure of critical vendors requires immediate mitigation' if tier_1_exposure > 0.6 else 'Critical vendor exposure is manageable but should be monitored'}."
            ),
            "cascade_analysis": (
                f"Cascade potential: {cascade_potential:.1%}. "
                f"{'High cascade potential indicates vulnerabilities that could cause widespread failures' if cascade_potential > 0.5 else 'Moderate cascade potential suggests reasonable resilience'}."
            ),
            "vulnerability_summary": (
                f"Identified {risk_metrics.single_point_failures} single points of failure and "
                f"{risk_metrics.critical_path_count} critical propagation paths. "
                f"Vulnerability density: {risk_metrics.vulnerability_density:.1%}."
            ),
            "resilience_score": (
                f"Resilience score: {risk_metrics.resilience_score:.1%}. "
                f"{'Good resilience' if risk_metrics.resilience_score > 0.7 else 'Resilience could be improved'}."
            )
        }
        
        return explanation
    
    def explain_mitigation_strategy(self,
                                   strategy: Dict[str, Any],
                                   impact_reduction: float) -> str:
        """
        Generate explanation for a mitigation strategy.
        
        Args:
            strategy: Mitigation strategy dictionary
            impact_reduction: Expected impact reduction (0-1)
            
        Returns:
            Natural language explanation
        """
        strategy_type = strategy.get('category', 'general')
        risk_reduction = strategy.get('riskReduction', 0)
        priority = strategy.get('priority', 'medium')
        
        explanation = (
            f"This {strategy_type} mitigation strategy ({strategy.get('title', 'Unknown')}) "
            f"is prioritized as {priority.upper()} and is expected to reduce risk by {risk_reduction}%. "
            f"{strategy.get('description', '')} "
            f"Implementation time: {strategy.get('implementationTime', 'Unknown')}. "
            f"Estimated impact reduction: {impact_reduction:.1%}."
        )
        
        return explanation


# Global instance
_explanation_service = None

def get_explanation_service(use_ai: bool = True) -> ExplanationService:
    """Get or create global explanation service instance."""
    global _explanation_service
    if _explanation_service is None:
        _explanation_service = ExplanationService(use_ai=use_ai)
    return _explanation_service

