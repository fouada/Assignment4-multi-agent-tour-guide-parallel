# 🧪 Experiments

## Multi-Agent Tour Guide System - Experiment Tracking

This directory contains experiment configurations, results, and tracking for research reproducibility.

---

## Directory Structure

```
experiments/
├── README.md                    # This file
├── registry.json                # Experiment registry
├── active/                      # Currently running experiments
├── completed/                   # Finished experiments
│   └── YYYYMMDD_experiment_name/
│       ├── config.yaml          # Experiment configuration
│       ├── results.json         # Raw results
│       ├── analysis.md          # Analysis notes
│       └── figures/             # Generated plots
└── templates/                   # Experiment templates
    └── sensitivity_template.yaml
```

---

## Experiment Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                      EXPERIMENT LIFECYCLE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   1. DESIGN          2. CONFIGURE        3. EXECUTE              │
│   ┌──────────┐       ┌──────────┐       ┌──────────┐            │
│   │ Hypothesis│  →   │  YAML    │  →    │  Runner  │            │
│   │ Variables │       │  Config  │       │  Script  │            │
│   └──────────┘       └──────────┘       └──────────┘            │
│                                                │                 │
│                                                ▼                 │
│   6. ARCHIVE         5. DOCUMENT        4. ANALYZE               │
│   ┌──────────┐       ┌──────────┐       ┌──────────┐            │
│   │ completed│  ←    │ analysis │  ←    │ stats &  │            │
│   │ directory│       │   .md    │       │  plots   │            │
│   └──────────┘       └──────────┘       └──────────┘            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Creating an Experiment

### 1. Design Experiment

Define your research question:
- **Hypothesis**: What do you expect to find?
- **Variables**: What parameters will you vary?
- **Metrics**: What will you measure?
- **Sample Size**: How many iterations?

### 2. Create Configuration

```yaml
# experiments/active/YYYYMMDD_my_experiment/config.yaml
experiment:
  id: "20251130_timeout_sensitivity"
  name: "Soft Timeout Sensitivity Study"
  hypothesis: "Soft timeout has the largest effect on latency"
  author: "Research Team"
  date: "2025-11-30"

design:
  type: "one_at_a_time"  # oat, factorial, latin_hypercube
  independent_variable: "soft_timeout"
  values: [5, 8, 10, 12, 15, 18, 20, 25, 30]
  dependent_variables:
    - latency_mean
    - latency_p95
    - quality_mean
    - success_rate
  
control:
  fixed_parameters:
    hard_timeout: 30.0
    min_for_soft: 2
    min_for_hard: 1

replication:
  seed: 42
  iterations_per_value: 5000
  total_iterations: 45000  # 9 values × 5000

analysis:
  statistical_tests:
    - welch_t_test
    - mann_whitney
    - bootstrap_ci
  effect_size: cohens_d
  significance_level: 0.05
```

### 3. Run Experiment

```bash
python experiments/run_experiment.py \
  --config experiments/active/20251130_timeout_sensitivity/config.yaml \
  --output experiments/active/20251130_timeout_sensitivity/results.json
```

### 4. Analyze Results

```bash
python experiments/analyze_experiment.py \
  --results experiments/active/20251130_timeout_sensitivity/results.json \
  --output experiments/active/20251130_timeout_sensitivity/analysis.md
```

### 5. Archive

```bash
mv experiments/active/20251130_timeout_sensitivity \
   experiments/completed/
```

---

## Experiment Registry

The `registry.json` file tracks all experiments:

```json
{
  "experiments": [
    {
      "id": "20251130_timeout_sensitivity",
      "status": "completed",
      "hypothesis": "Soft timeout has the largest effect on latency",
      "conclusion": "SUPPORTED - soft_timeout explains 40% variance",
      "created": "2025-11-30T10:00:00Z",
      "completed": "2025-11-30T12:30:00Z"
    }
  ]
}
```

---

## Experiment Types

### One-at-a-Time (OAT)
Vary one parameter while holding others constant.

```yaml
design:
  type: one_at_a_time
  parameters:
    - name: soft_timeout
      values: [5, 10, 15, 20, 25, 30]
```

### Factorial Design
Test all combinations of parameter levels.

```yaml
design:
  type: full_factorial
  parameters:
    - name: soft_timeout
      levels: [10, 15, 20]
    - name: hard_timeout
      levels: [20, 30, 40]
  # 3 × 3 = 9 combinations
```

### Latin Hypercube Sampling
Efficiently sample multi-dimensional parameter space.

```yaml
design:
  type: latin_hypercube
  parameters:
    - name: soft_timeout
      range: [5, 30]
    - name: hard_timeout
      range: [15, 60]
  samples: 50
```

---

## Best Practices

1. **Pre-register Hypothesis**: Document before running
2. **Fix Seeds**: Ensure reproducibility
3. **Power Analysis**: Calculate required sample size
4. **Document Everything**: Config, results, analysis
5. **Version Control**: Commit experiment configs

---

**Last Updated**: November 2025

