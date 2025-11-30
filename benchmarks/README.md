# 🏋️ Benchmarks

## Multi-Agent Tour Guide System - Performance Benchmarks

This directory contains reproducible benchmark configurations and results.

---

## Directory Structure

```
benchmarks/
├── README.md                    # This file
├── configs/                     # Benchmark configurations
│   ├── baseline.yaml            # Default configuration
│   ├── low_latency.yaml         # Optimized for speed
│   ├── high_quality.yaml        # Optimized for quality
│   └── stress_test.yaml         # High load scenarios
├── results/                     # Benchmark results (gitignored)
│   └── .gitkeep
└── scripts/                     # Benchmark runners
    └── run_benchmark.py
```

---

## Running Benchmarks

### Quick Start

```bash
# Run all benchmarks
python benchmarks/scripts/run_benchmark.py --all

# Run specific benchmark
python benchmarks/scripts/run_benchmark.py --config configs/baseline.yaml

# Run with custom iterations
python benchmarks/scripts/run_benchmark.py --config configs/baseline.yaml --iterations 1000
```

### Benchmark Configurations

| Config | Description | Use Case |
|--------|-------------|----------|
| `baseline.yaml` | Default settings (15s/30s) | Reference baseline |
| `low_latency.yaml` | Aggressive timeouts (8s/15s) | Real-time applications |
| `high_quality.yaml` | Conservative timeouts (25s/45s) | Batch processing |
| `stress_test.yaml` | High load simulation | Capacity planning |

---

## Metrics Collected

### Latency Metrics
- Mean response time
- P50, P90, P95, P99 latencies
- Standard deviation

### Quality Metrics
- Mean quality score
- Quality distribution
- Content type distribution

### Reliability Metrics
- Success rate (non-failed)
- Complete rate (3/3 agents)
- Degradation rate (1-2/3 agents)

### Resource Metrics
- Thread utilization
- Memory usage
- API call counts

---

## Results Format

Results are saved as JSON:

```json
{
  "benchmark_id": "baseline_20251130_120000",
  "config": "baseline.yaml",
  "timestamp": "2025-11-30T12:00:00Z",
  "iterations": 10000,
  "metrics": {
    "latency": {
      "mean": 4.523,
      "std": 3.412,
      "p50": 3.21,
      "p90": 8.45,
      "p95": 12.34,
      "p99": 15.00
    },
    "quality": {
      "mean": 7.02,
      "std": 1.45
    },
    "reliability": {
      "success_rate": 0.9987,
      "complete_rate": 0.8534,
      "soft_degraded_rate": 0.1234,
      "hard_degraded_rate": 0.0219
    }
  },
  "environment": {
    "python_version": "3.11.0",
    "platform": "darwin",
    "cpu_count": 8
  }
}
```

---

## Reproducibility

Each benchmark run:

1. Uses fixed random seed (from config)
2. Records environment details
3. Timestamps all results
4. Stores complete configuration

To reproduce a previous benchmark:
```bash
python benchmarks/scripts/run_benchmark.py \
  --config results/baseline_20251130_120000/config.yaml \
  --seed 42
```

---

## Adding New Benchmarks

1. Create config file in `configs/`:

```yaml
# configs/my_benchmark.yaml
name: my_benchmark
description: My custom benchmark

parameters:
  soft_timeout: 12.0
  hard_timeout: 25.0
  
simulation:
  seed: 42
  iterations: 10000
  
agents:
  video:
    mu: 1.0
    sigma: 0.5
    reliability: 0.92
  music:
    mu: 0.8
    sigma: 0.4
    reliability: 0.95
  text:
    mu: 0.6
    sigma: 0.3
    reliability: 0.98
```

2. Run the benchmark:
```bash
python benchmarks/scripts/run_benchmark.py --config configs/my_benchmark.yaml
```

3. Compare results:
```bash
python benchmarks/scripts/compare_benchmarks.py \
  results/baseline_*/results.json \
  results/my_benchmark_*/results.json
```

---

## CI/CD Integration

Benchmarks can be run in CI to catch performance regressions:

```yaml
# .github/workflows/benchmark.yml
- name: Run Benchmarks
  run: |
    python benchmarks/scripts/run_benchmark.py --config configs/baseline.yaml
    python benchmarks/scripts/check_thresholds.py results/latest/
```

Threshold checks ensure:
- Mean latency < 5.0s
- P99 latency < 30.0s
- Success rate > 99%

---

**Last Updated**: November 2025

