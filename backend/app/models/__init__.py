# models/__init__.py
from .user import User
from .user import UserProfile
from .system import SystemConfiguration
from .system import OptimizationProfile
from .alerts import SystemAlert
from .metrics import SystemMetrics
from .tuning_history import TuningHistory
from .agent_coordination_models import AgentPerformanceSummary, CrossAgentCoordination
from .agent_decision_models import HawkingtonDecisionLog, MethSnailDecisionLog, HamstersDecisionLog
from .ai_agent_tracking import AIAgentMetrics, MethSnailShellSpins, SirHawkingtonMonocleYeets, TheStickHyperventilations, QuantumShadowPhasings, VIC20Wisdom
from .hamsters_model import HamstersEngineeringStats
from .meth_snail_model import MethSnailOptimizationStats
from .metrics_aggregates import MetricsHourly, MetricsDaily
from .qsp_models import QSPNetworkMetrics, QSPDecisionLog, QSPQuantumStats, QSPNetworkPatterns
from .sir_hawkington_model import HawkingtonMonitoringStats
from .the_stick_model import StickUserPatterns, StickDecisionLog, StickComplianceHistory, StickConfigurationProfiles, StickAnxietyLog, StickLearningMetrics, StickRebelionStats
from .vic20_sage_model import VIC20CoordinationLog, VIC20SystemSynthesis, VIC20AgentHarmony, VIC20AncientWisdom, VIC20PartnershipMetrics, VIC20DecisionOrchestration, VIC20AgentInteractionLog


# Ensure all models are imported and registered
__all__ = [
    'User', 'UserProfile', 'SystemConfiguration', 'OptimizationProfile', 
    'SystemAlert', 'SystemMetrics', 'TuningHistory',
    'AgentPerformanceSummary', 'CrossAgentCoordination',
    'HawkingtonDecisionLog', 'MethSnailDecisionLog', 'HamstersDecisionLog',
    'AIAgentMetrics', 'MethSnailShellSpins', 'SirHawkingtonMonocleYeets', 
    'TheStickHyperventilations', 'QuantumShadowPhasings', 'VIC20Wisdom',
    'HamstersEngineeringStats', 'MethSnailOptimizationStats',
    'MetricsHourly', 'MetricsDaily',
    'QSPNetworkMetrics', 'QSPDecisionLog', 'QSPQuantumStats', 'QSPNetworkPatterns',
    'HawkingtonMonitoringStats',
    'StickUserPatterns', 'StickDecisionLog', 'StickComplianceHistory', 
    'StickConfigurationProfiles', 'StickAnxietyLog', 'StickLearningMetrics', 
    'StickRebelionStats',
    'VIC20CoordinationLog', 'VIC20SystemSynthesis', 'VIC20AgentHarmony', 
    'VIC20AncientWisdom', 'VIC20PartnershipMetrics', 'VIC20DecisionOrchestration', 
    'VIC20AgentInteractionLog'
]