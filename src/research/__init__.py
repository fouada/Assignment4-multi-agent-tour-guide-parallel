"""
Research Framework for MIT-Level Analysis
==========================================

🎓 MIT-LEVEL INNOVATION FRAMEWORK

This module provides advanced research tools for academic/industrial publishing:

Core Research Tools:
- Systematic sensitivity analysis
- Statistical hypothesis testing
- Monte Carlo simulations
- Experimental benchmarking

🆕 Advanced Innovations (Publication-Ready):
- Adaptive Learning (Multi-Armed Bandits with Thompson Sampling)
- Causal Inference (Structural Causal Models, do-calculus)
- Bayesian Optimization (Gaussian Process-based Configuration Tuning)
- Explainable AI (SHAP, LIME, Counterfactual Explanations)
- Information Theory (Regret Bounds, Channel Capacity, Rate-Distortion)

🌟 NEW GROUNDBREAKING INNOVATIONS:
- Sequential Optimization (RL for Journey-Aware Content Sequencing)
- Multi-Agent Negotiation (Game Theory, VCG Auctions, Nash Equilibrium)
- Meta-Learning (MAML/Reptile for Cold-Start Users)
- Graph Neural Networks (Route-Aware Spatial Content Selection)
- Uncertainty Quantification (Conformal Prediction with Coverage Guarantees)

Academic References:
    - Saltelli, A. et al. (2008). Global Sensitivity Analysis: The Primer. Wiley.
    - Montgomery, D.C. (2017). Design and Analysis of Experiments. Wiley.
    - Pearl, J. (2009). Causality: Models, Reasoning, and Inference. Cambridge.
    - Snoek, J. et al. (2012). Practical Bayesian Optimization of ML Algorithms.
    - Lundberg & Lee (2017). A Unified Approach to Interpreting Model Predictions.
    - Agrawal & Goyal (2012). Analysis of Thompson Sampling.
    - Cover & Thomas (2006). Elements of Information Theory.
    - Finn et al. (2017). Model-Agnostic Meta-Learning for Fast Adaptation.
    - Nisan et al. (2007). Algorithmic Game Theory.
    - Kipf & Welling (2017). Semi-Supervised Classification with GCNs.
    - Angelopoulos & Bates (2022). Conformal Prediction: A Gentle Introduction.
    - Sutton & Barto (2018). Reinforcement Learning: An Introduction.
"""

# === MIT-LEVEL INNOVATIONS ===
from .adaptive_learning import (
    UCB,
    AdaptiveAgentSelector,
    # Data structures
    AgentType,
    BanditExperiment,
    BanditStatistics,
    Context,
    ContextualThompsonSampling,
    Reward,
    # Multi-Armed Bandits
    ThompsonSampling,
)
from .agent_negotiation import (
    # Auction Components
    AgentBid,
    AuctionResult,
    # Consensus
    ConsensusProtocol,
    # Cooperative Game Theory
    CooperativeContentGame,
    # Main Interface
    MultiAgentNegotiationSystem,
    # Nash Equilibrium
    NashEquilibriumAnalyzer,
    # Strategic Agents
    StrategicAgent,
    # VCG Mechanism
    VCGAuction,
)
from .bayesian_optimization import (
    # Optimization
    BayesianOptimizer,
    # Configuration Space
    ConfigurationSpace,
    # Acquisition Functions
    ExpectedImprovement,
    # Gaussian Process
    GaussianProcess,
    MaternKernel,
    MultiObjectiveBO,
    OptimizationHistory,
    OptimizationResult,
    Parameter,
    ParameterType,
    ProbabilityOfImprovement,
    SquaredExponentialKernel,
    ThompsonSamplingAcquisition,
    UCBAcquisition,
)
from .causal_inference import (
    # Analysis
    AgentPerformanceAnalyzer,
    CausalDiscovery,
    CausalEdge,
    # Estimators
    CausalEffectEstimator,
    CausalObservation,
    CausalVariable,
    # Structural Causal Models
    StructuralCausalModel,
    StructuralEquation,
)
from .experimental_framework import (
    ExperimentConfig,
    ExperimentResult,
    ExperimentRunner,
    ReproducibleExperiment,
)
from .explainability import (
    # Counterfactuals
    CounterfactualExplainer,
    CounterfactualExplanation,
    Decision,
    # Integrated Engine
    ExplainabilityEngine,
    ExplanationType,
    # Data structures
    Feature,
    FeatureValue,
    # LIME
    LIMEExplainer,
    # Natural Language
    NaturalLanguageExplainer,
    # SHAP
    SHAPExplainer,
)
from .graph_neural_content import (
    GraphAttentionLayer,
    # GNN Layers
    GraphConvLayer,
    # Graph Components
    LocationNode,
    LocationType,
    # Positional Encoding
    PositionalEncoding,
    # Main Interface
    RouteAwareContentSelector,
    RouteEdge,
    # GNN Model
    RouteGNN,
    RouteGraph,
)
from .information_theory import (
    # Channel Theory
    AgentUserChannel,
    # Diversity
    DiversityMetrics,
    # Entropy
    EntropyCalculator,
    InformationTheoreticAnalysis,
    # Complete Analysis
    InformationTheoreticAnalyzer,
    # Regret Bounds
    InformationTheoreticRegretBounds,
    KLDivergence,
    MutualInformationCalculator,
    # Rate-Distortion
    RateDistortionAnalyzer,
    RegretBoundResult,
)
from .meta_learning import (
    # Meta-Learning Algorithms
    MAML,
    # Main Interface
    ColdStartHandler,
    # Preference Model
    PreferenceModel,
    # Prototypical Networks
    PrototypicalNetworks,
    Reptile,
    Task,
    # Data Structures
    UserInteraction,
    # Task Generator
    create_synthetic_task_generator,
)

# === NEW GROUNDBREAKING INNOVATIONS ===
from .sequential_optimization import (
    DiversityConstrainedOptimizer,
    # Reward Shaping
    EmotionalArcReward,
    EmotionalState,
    # Main Interface
    SequentialContentOptimizer,
    # Policy
    SoftmaxPolicy,
    TourAction,
    # MDP Components
    TourState,
)
from .statistical_analysis import (
    BootstrapAnalysis,
    EffectSizeAnalysis,
    HypothesisTest,
    StatisticalComparison,
)
from .uncertainty_quantification import (
    AdaptiveConformalPredictor,
    AdaptiveProbabilityScore,
    CalibrationResult,
    # Conformal Predictors
    ConformalPredictor,
    # Conformity Scores
    ConformityScore,
    # Prediction Set
    PredictionSet,
    RAPSScore,
    # Selective Prediction
    SelectivePredictor,
    SimpleProbabilityScore,
    # Main Interface
    UncertaintyAwareContentSelector,
)
from .visualization import (
    ResearchVisualizer,
    create_publication_figure,
)

__all__ = [
    # === Core Research Framework ===
    # Experimental Framework
    "ExperimentConfig",
    "ExperimentResult",
    "ExperimentRunner",
    "ReproducibleExperiment",
    # Statistical Analysis
    "StatisticalComparison",
    "EffectSizeAnalysis",
    "HypothesisTest",
    "BootstrapAnalysis",
    # Visualization
    "ResearchVisualizer",
    "create_publication_figure",
    # === MIT-LEVEL INNOVATIONS ===
    # Adaptive Learning (Multi-Armed Bandits)
    "ThompsonSampling",
    "UCB",
    "ContextualThompsonSampling",
    "AdaptiveAgentSelector",
    "BanditExperiment",
    "AgentType",
    "Context",
    "Reward",
    "BanditStatistics",
    # Causal Inference
    "StructuralCausalModel",
    "StructuralEquation",
    "CausalVariable",
    "CausalEdge",
    "CausalObservation",
    "CausalEffectEstimator",
    "CausalDiscovery",
    "AgentPerformanceAnalyzer",
    # Bayesian Optimization
    "ConfigurationSpace",
    "Parameter",
    "ParameterType",
    "GaussianProcess",
    "SquaredExponentialKernel",
    "MaternKernel",
    "ExpectedImprovement",
    "UCBAcquisition",
    "ProbabilityOfImprovement",
    "ThompsonSamplingAcquisition",
    "BayesianOptimizer",
    "MultiObjectiveBO",
    "OptimizationHistory",
    "OptimizationResult",
    # Explainable AI
    "SHAPExplainer",
    "LIMEExplainer",
    "CounterfactualExplainer",
    "CounterfactualExplanation",
    "NaturalLanguageExplainer",
    "ExplainabilityEngine",
    "Feature",
    "FeatureValue",
    "Decision",
    "ExplanationType",
    # Information Theory
    "EntropyCalculator",
    "MutualInformationCalculator",
    "KLDivergence",
    "InformationTheoreticRegretBounds",
    "RegretBoundResult",
    "AgentUserChannel",
    "RateDistortionAnalyzer",
    "DiversityMetrics",
    "InformationTheoreticAnalyzer",
    "InformationTheoreticAnalysis",
    # === NEW GROUNDBREAKING INNOVATIONS ===
    # Sequential Optimization (Reinforcement Learning)
    "TourState",
    "TourAction",
    "EmotionalState",
    "EmotionalArcReward",
    "SoftmaxPolicy",
    "SequentialContentOptimizer",
    "DiversityConstrainedOptimizer",
    # Agent Negotiation (Game Theory)
    "AgentBid",
    "AuctionResult",
    "VCGAuction",
    "NashEquilibriumAnalyzer",
    "ConsensusProtocol",
    "StrategicAgent",
    "CooperativeContentGame",
    "MultiAgentNegotiationSystem",
    # Meta-Learning (Cold Start)
    "UserInteraction",
    "Task",
    "PreferenceModel",
    "MAML",
    "Reptile",
    "PrototypicalNetworks",
    "ColdStartHandler",
    "create_synthetic_task_generator",
    # Graph Neural Networks
    "LocationNode",
    "LocationType",
    "RouteEdge",
    "RouteGraph",
    "GraphConvLayer",
    "GraphAttentionLayer",
    "RouteGNN",
    "PositionalEncoding",
    "RouteAwareContentSelector",
    # Uncertainty Quantification (Conformal Prediction)
    "PredictionSet",
    "CalibrationResult",
    "ConformityScore",
    "SimpleProbabilityScore",
    "AdaptiveProbabilityScore",
    "RAPSScore",
    "ConformalPredictor",
    "AdaptiveConformalPredictor",
    "SelectivePredictor",
    "UncertaintyAwareContentSelector",
]
