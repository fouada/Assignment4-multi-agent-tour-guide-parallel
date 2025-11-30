# ADR-005: Statistical Analysis Framework

## Status

Accepted

## Date

2025-11

## Context

For MIT-level academic quality, the project requires:

1. **Rigorous Analysis**: Beyond anecdotal performance claims
2. **Reproducibility**: Results must be reproducible
3. **Statistical Validity**: Proper hypothesis testing
4. **Sensitivity Analysis**: Understanding parameter impact
5. **Publication Quality**: Figures and reports suitable for papers

Current gaps:
- No formal experiment tracking
- Ad-hoc performance measurements
- No sensitivity analysis
- No statistical significance testing

## Decision

Implement a comprehensive **Statistical Analysis Framework** with:

### Framework Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    RESEARCH FRAMEWORK                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Experimental Framework                        │   │
│  │  • ExperimentConfig (reproducible settings)               │   │
│  │  • ExperimentRunner (parameter sweeps)                    │   │
│  │  • ResultPersistence (JSON export)                        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Statistical Analysis                          │   │
│  │  • Hypothesis Testing (t-test, Mann-Whitney, KS)          │   │
│  │  • Effect Sizes (Cohen's d, Hedges' g)                    │   │
│  │  • Bootstrap CI                                            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Sensitivity Analysis                          │   │
│  │  • Local (One-at-a-time)                                  │   │
│  │  • Global (Sobol indices)                                 │   │
│  │  • Morris Screening                                        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Visualization                                 │   │
│  │  • Publication-quality figures (300 DPI)                  │   │
│  │  • Pareto frontiers                                        │   │
│  │  • Effect size forest plots                               │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Statistical Tests Suite

| Test | Purpose | Effect Size |
|------|---------|-------------|
| Welch's t-test | Mean comparison (unequal variance) | Cohen's d |
| Mann-Whitney U | Non-parametric rank comparison | Rank-biserial r |
| Kolmogorov-Smirnov | Distribution shape comparison | D statistic |
| Chi-square | Categorical comparison | Cramér's V |
| Bootstrap | Confidence intervals | - |
| Permutation | Exact p-values | - |

### Effect Size Interpretation

| Cohen's d | Interpretation |
|-----------|----------------|
| < 0.2 | Negligible |
| 0.2 - 0.5 | Small |
| 0.5 - 0.8 | Medium |
| > 0.8 | Large |

### Reproducibility Requirements

```python
@dataclass
class ExperimentConfig:
    name: str
    seed: int = 42              # Fixed random seed
    n_replications: int = 10    # Number of runs
    parameters: Dict[str, Any]  # Configuration
    
    @property
    def hash(self) -> str:
        """Deterministic hash for caching"""
        return hashlib.sha256(
            json.dumps(self.__dict__, sort_keys=True).encode()
        ).hexdigest()[:12]
```

## Consequences

### Positive

- **Academic Rigor**: Meets publication standards
- **Reproducibility**: Deterministic experiments
- **Confidence**: Statistical significance quantified
- **Insights**: Sensitivity analysis reveals key parameters
- **Communication**: Publication-quality visualizations

### Negative

- **Complexity**: Additional code and concepts
- **Computational Cost**: Monte Carlo requires many runs
- **Learning Curve**: Statistical concepts required
- **Dependencies**: numpy, scipy, pandas, matplotlib

### Neutral

- Requires understanding of statistical testing
- Results may invalidate intuitions

## Alternatives Considered

### Alternative 1: Simple Benchmarking

**Description**: Just measure mean/std of metrics

**Pros**:
- Simple
- Fast

**Cons**:
- No statistical validity
- Can't claim significance
- Not publishable

**Why Rejected**: Insufficient for academic standards

### Alternative 2: External Tools (JMeter, Locust)

**Description**: Use existing benchmarking tools

**Pros**:
- Battle-tested
- Rich features

**Cons**:
- Not integrated with codebase
- Limited statistical analysis
- Can't simulate queue behavior

**Why Rejected**: Need custom simulation of Smart Queue

### Alternative 3: Machine Learning Approach

**Description**: Use ML to model system behavior

**Pros**:
- Can capture complex interactions
- Predictive capability

**Cons**:
- Black box
- Requires large datasets
- Overkill for parameter study

**Why Rejected**: Classical statistics more appropriate

## References

- [Saltelli, A. et al. (2008). Global Sensitivity Analysis: The Primer](https://onlinelibrary.wiley.com/doi/book/10.1002/9780470725184)
- [Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences](https://www.routledge.com/Statistical-Power-Analysis-for-the-Behavioral-Sciences/Cohen/p/book/9780805802832)
- [Efron, B. & Tibshirani, R. (1993). An Introduction to the Bootstrap](https://www.routledge.com/An-Introduction-to-the-Bootstrap/Efron-Tibshirani/p/book/9780412042317)

## Notes

Key findings from initial analysis:
- `soft_timeout` is the most sensitive parameter (40% variance explained)
- Agent reliability dominates quality variation
- Pareto-optimal configurations identified for different use cases
- All major comparisons show statistical significance (p < 0.001)

See `notebooks/01_sensitivity_analysis.ipynb` for full analysis.

