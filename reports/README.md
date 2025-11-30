# 📑 Reports

## Multi-Agent Tour Guide System - Research Reports

This directory contains generated analysis reports and documentation.

---

## Directory Structure

```
reports/
├── README.md                    # This file
├── generated/                   # Auto-generated reports
│   ├── .gitkeep
│   └── YYYYMMDD_report_name.md
├── templates/                   # Report templates
│   ├── analysis_report.md
│   └── experiment_summary.md
└── published/                   # Finalized publications
    └── .gitkeep
```

---

## Report Types

### 1. Analysis Reports
Auto-generated from notebook outputs:
- Statistical summaries
- Sensitivity analysis results
- Configuration comparisons

### 2. Experiment Summaries
Per-experiment documentation:
- Hypothesis
- Methodology
- Results
- Conclusions

### 3. Technical Reports
In-depth technical analysis:
- Mathematical proofs
- Algorithm analysis
- Performance characterization

---

## Generating Reports

### From Notebooks

```python
# In Jupyter notebook
from src.research import ReportGenerator

generator = ReportGenerator(output_dir="reports/generated")
generator.create_analysis_report(
    title="Sensitivity Analysis Report",
    data=results_df,
    figures=["fig1.png", "fig2.png"],
    template="templates/analysis_report.md"
)
```

### From Command Line

```bash
# Generate sensitivity analysis report
python scripts/generate_report.py \
  --type analysis \
  --input data/sensitivity_analysis_results.json \
  --output reports/generated/

# Generate experiment summary
python scripts/generate_report.py \
  --type experiment \
  --config experiments/completed/20251130_study/config.yaml \
  --results experiments/completed/20251130_study/results.json
```

---

## Report Templates

### Analysis Report Template

```markdown
# [Title]

**Date**: YYYY-MM-DD  
**Author**: Name  
**Version**: X.Y.Z

## Executive Summary
Brief overview of findings.

## Methodology
- Data collection
- Statistical methods
- Tools used

## Results
### Key Findings
1. Finding 1
2. Finding 2

### Statistical Analysis
| Metric | Value | CI 95% |
|--------|-------|--------|
| ...    | ...   | ...    |

## Discussion
Interpretation of results.

## Conclusions
Summary and recommendations.

## Appendix
Additional tables, figures, raw data.
```

---

## Publishing Workflow

1. **Draft**: Generate in `generated/`
2. **Review**: Team review and edits
3. **Finalize**: Move to `published/`
4. **Version**: Tag with version number

```bash
# Finalize a report
mv reports/generated/analysis_v1.md reports/published/
git add reports/published/analysis_v1.md
git commit -m "docs: publish sensitivity analysis report v1"
git tag -a report-sensitivity-v1 -m "Sensitivity Analysis Report v1"
```

---

## Report Naming Convention

```
YYYYMMDD_type_subject_vX.md

Examples:
- 20251130_analysis_sensitivity_v1.md
- 20251130_experiment_timeout_study_v2.md
- 20251130_technical_queue_proofs_v1.md
```

---

**Last Updated**: November 2025

