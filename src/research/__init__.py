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

from .experimental_framework import (
    ExperimentConfig,
    ExperimentResult,
    ExperimentRunner,
    ReproducibleExperiment,
)

from .statistical_analysis import (
    StatisticalComparison,
    EffectSizeAnalysis,
    HypothesisTest,
    BootstrapAnalysis,
)

from .visualization import (
    ResearchVisualizer,
    create_publication_figure,
)

# === MIT-LEVEL INNOVATIONS ===

from .adaptive_learning import (
    # Multi-Armed Bandits
    ThompsonSampling,
    UCB,
    ContextualThompsonSampling,
    AdaptiveAgentSelector,
    BanditExperiment,
    # Data structures
    AgentType,
    Context,
    Reward,
    BanditStatistics,
)

from .causal_inference import (
    # Structural Causal Models
    StructuralCausalModel,
    StructuralEquation,
    CausalVariable,
    CausalEdge,
    CausalObservation,
    # Estimators
    CausalEffectEstimator,
    CausalDiscovery,
    # Analysis
    AgentPerformanceAnalyzer,
)

from .bayesian_optimization import (
    # Configuration Space
    ConfigurationSpace,
    Parameter,
    ParameterType,
    # Gaussian Process
    GaussianProcess,
    SquaredExponentialKernel,
    MaternKernel,
    # Acquisition Functions
    ExpectedImprovement,
    UCBAcquisition,
    ProbabilityOfImprovement,
    ThompsonSamplingAcquisition,
    # Optimization
    BayesianOptimizer,
    MultiObjectiveBO,
    OptimizationHistory,
    OptimizationResult,
)

from .explainability import (
    # SHAP
    SHAPExplainer,
    # LIME
    LIMEExplainer,
    # Counterfactuals
    CounterfactualExplainer,
    CounterfactualExplanation,
    # Natural Language
    NaturalLanguageExplainer,
    # Integrated Engine
    ExplainabilityEngine,
    # Data structures
    Feature,
    FeatureValue,
    Decision,
    ExplanationType,
)

from .information_theory import (
    # Entropy
    EntropyCalculator,
    MutualInformationCalculator,
    KLDivergence,
    # Regret Bounds
    InformationTheoreticRegretBounds,
    RegretBoundResult,
    # Channel Theory
    AgentUserChannel,
    # Rate-Distortion
    RateDistortionAnalyzer,
    # Diversity
    DiversityMetrics,
    # Complete Analysis
    InformationTheoreticAnalyzer,
    InformationTheoreticAnalysis,
)

# === NEW GROUNDBREAKING INNOVATIONS ===

from .sequential_optimization import (
    # MDP Components
    TourState,
    TourAction,
    EmotionalState,
    # Reward Shaping
    EmotionalArcReward,
    # Policy
    SoftmaxPolicy,
    # Main Interface
    SequentialContentOptimizer,
    DiversityConstrainedOptimizer,
)

from .agent_negotiation import (
    # Auction Components
    AgentBid,
    AuctionResult,
    # VCG Mechanism
    VCGAuction,
    # Nash Equilibrium
    NashEquilibriumAnalyzer,
    # Consensus
    ConsensusProtocol,
    # Strategic Agents
    StrategicAgent,
    # Cooperative Game Theory
    CooperativeContentGame,
    # Main Interface
    MultiAgentNegotiationSystem,
)

from .meta_learning import (
    # Data Structures
    UserInteraction,
    Task,
    # Preference Model
    PreferenceModel,
    # Meta-Learning Algorithms
    MAML,
    Reptile,
    # Prototypical Networks
    PrototypicalNetworks,
    # Main Interface
    ColdStartHandler,
    # Task Generator
    create_synthetic_task_generator,
)

from .graph_neural_content import (
    # Graph Components
    LocationNode,
    LocationType,
    RouteEdge,
    RouteGraph,
    # GNN Layers
    GraphConvLayer,
    GraphAttentionLayer,
    # GNN Model
    RouteGNN,
    # Positional Encoding
    PositionalEncoding,
    # Main Interface
    RouteAwareContentSelector,
)

from .uncertainty_quantification import (
    # Prediction Set
    PredictionSet,
    CalibrationResult,
    # Conformity Scores
    ConformityScore,
    SimpleProbabilityScore,
    AdaptiveProbabilityScore,
    RAPSScore,
    # Conformal Predictors
    ConformalPredictor,
    AdaptiveConformalPredictor,
    # Selective Prediction
    SelectivePredictor,
    # Main Interface
    UncertaintyAwareContentSelector,
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

