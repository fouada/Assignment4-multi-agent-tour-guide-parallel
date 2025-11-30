# 📓 Research Notebooks

## Multi-Agent Tour Guide System - MIT-Level Analysis

This directory contains Jupyter notebooks for systematic research and analysis of the Multi-Agent Tour Guide System.

---

## Notebook Index

| # | Notebook | Description | Status |
|---|----------|-------------|--------|
| 01 | [01_sensitivity_analysis.ipynb](01_sensitivity_analysis.ipynb) | Monte Carlo sensitivity analysis | ✅ Complete |
| 02 | [02_statistical_comparison.ipynb](02_statistical_comparison.ipynb) | Configuration comparison | 📝 Planned |
| 03 | [03_optimization_study.ipynb](03_optimization_study.ipynb) | Multi-objective optimization | 📝 Planned |
| 04 | [04_agent_reliability.ipynb](04_agent_reliability.ipynb) | Agent failure analysis | 📝 Planned |

---

## Quick Start

### 1. Install Dependencies

```bash
# Using UV (recommended)
cd /path/to/project
uv sync --extra research

# Or using pip
pip install numpy pandas scipy matplotlib seaborn jupyter
```

### 2. Launch Jupyter

```bash
# Using UV
uv run jupyter notebook

# Or directly
jupyter notebook
```

### 3. Open Notebook

Navigate to `notebooks/` and open the desired notebook.

---

## Notebook Descriptions

### 01. Sensitivity Analysis (`01_sensitivity_analysis.ipynb`)

**Purpose**: Quantify parameter impact on system performance

**Contents**:
- Monte Carlo simulation (N=10,000)
- Local sensitivity analysis (OAT)
- Statistical hypothesis testing
- Publication-quality visualizations

**Key Outputs**:
- Baseline performance metrics
- Sensitivity rankings
- Pareto frontier analysis
- Configuration recommendations

**Runtime**: ~5-10 minutes

### 02. Statistical Comparison (Planned)

**Purpose**: Rigorous comparison of configuration alternatives

**Contents**:
- Multiple configuration comparison
- Effect size analysis (Cohen's d)
- Power analysis
- Confidence intervals

### 03. Optimization Study (Planned)

**Purpose**: Multi-objective optimization of timeout parameters

**Contents**:
- Pareto optimization
- NSGA-II implementation
- Trade-off analysis
- Optimal configuration identification

### 04. Agent Reliability Analysis (Planned)

**Purpose**: Analyze agent failure patterns and mitigation

**Contents**:
- Failure mode analysis
- Circuit breaker effectiveness
- Recovery time analysis
- Reliability engineering

---

## Output Directories

```
notebooks/
├── README.md              # This file
├── 01_sensitivity_analysis.ipynb
└── ...

data/
├── figures/               # Generated plots (PNG, 300 DPI)
│   ├── baseline_results.png
│   ├── local_sensitivity.png
│   └── ...
└── sensitivity_analysis_results.json  # Raw data
```

---

## Reproducibility

All notebooks are designed for reproducibility:

1. **Fixed Seeds**: `np.random.seed(42)` at start
2. **Versioned Dependencies**: See `pyproject.toml` [research] extras
3. **Deterministic Algorithms**: No stochastic elements without seed control
4. **Output Persistence**: Results saved to JSON/CSV

To reproduce results exactly:
```bash
git checkout <commit_hash>
uv sync --extra research
uv run jupyter notebook 01_sensitivity_analysis.ipynb
# Run All Cells
```

---

## Publication Guidelines

Figures generated in these notebooks are publication-ready:

- **Resolution**: 300 DPI
- **Format**: PNG (raster) or PDF (vector)
- **Style**: seaborn-whitegrid
- **Fonts**: Standard (Arial/Helvetica)
- **Colors**: Colorblind-friendly palette

To export figures:
```python
plt.savefig('../data/figures/figure_name.png', dpi=300, bbox_inches='tight')
```

---

## Contributing

When adding new notebooks:

1. Follow numbering scheme: `XX_descriptive_name.ipynb`
2. Include markdown documentation
3. Set random seeds for reproducibility
4. Save outputs to `data/figures/`
5. Update this README

---

## References

- **Sensitivity Analysis**: Saltelli et al. (2008). *Global Sensitivity Analysis*
- **Statistical Testing**: Cohen (1988). *Statistical Power Analysis*
- **Visualization**: Tufte (2001). *The Visual Display of Quantitative Information*

---

**Last Updated**: November 2025  
**Maintainer**: Multi-Agent Tour Guide Research Team

