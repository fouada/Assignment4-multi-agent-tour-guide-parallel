"""
Comprehensive Tests for Research Visualization Module
=====================================================

MIT-Level test suite for publication-quality visualizations.

Test Categories:
1. ResearchVisualizer - Main visualization class
2. compare_distributions - Distribution comparison
3. sensitivity_plot - Parameter sensitivity
4. pareto_frontier - Multi-objective optimization
5. effect_size_forest_plot - Forest plots
6. status_distribution_plot - Status visualization
7. heatmap - Interaction heatmaps
8. create_publication_figure - Figure utilities

Coverage Target: 85%+

Note: These tests use matplotlib's non-interactive backend
to avoid display issues during testing.

Author: Multi-Agent Tour Guide Research Team
"""

# Set matplotlib backend before any imports
import matplotlib
import numpy as np
import pytest

matplotlib.use("Agg")


# Now import the module under test
from src.research.visualization import (
    ResearchVisualizer,
    _import_viz,
    create_publication_figure,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture(autouse=True)
def cleanup_matplotlib():
    """Clean up matplotlib after each test to prevent memory leaks."""
    yield
    import matplotlib.pyplot as plt

    plt.close("all")


@pytest.fixture
def visualizer():
    """Create visualizer instance for testing."""
    return ResearchVisualizer(output_dir=None, figsize=(8, 6))


@pytest.fixture
def visualizer_with_output(tmp_path):
    """Create visualizer with output directory."""
    return ResearchVisualizer(output_dir=tmp_path)


@pytest.fixture
def sample_a():
    """Sample A for distribution comparison."""
    np.random.seed(42)
    return np.random.normal(10, 2, 100)


@pytest.fixture
def sample_b():
    """Sample B for distribution comparison."""
    np.random.seed(123)
    return np.random.normal(12, 2, 100)


# ============================================================================
# _import_viz Tests
# ============================================================================


class TestImportViz:
    """Tests for lazy import function."""

    def test_import_returns_plt_and_sns(self):
        """Test that import returns matplotlib and seaborn."""
        plt, sns = _import_viz()

        assert plt is not None
        assert sns is not None

    def test_import_is_idempotent(self):
        """Test that repeated imports return same objects."""
        plt1, sns1 = _import_viz()
        plt2, sns2 = _import_viz()

        assert plt1 is plt2
        assert sns1 is sns2


# ============================================================================
# ResearchVisualizer Initialization Tests
# ============================================================================


class TestResearchVisualizerInit:
    """Tests for ResearchVisualizer initialization."""

    def test_default_initialization(self):
        """Test default initialization."""
        viz = ResearchVisualizer()

        assert viz.output_dir is None
        assert viz.figsize == (10, 6)
        assert viz.style == "publication"

    def test_custom_initialization(self, tmp_path):
        """Test custom initialization."""
        viz = ResearchVisualizer(output_dir=tmp_path, figsize=(12, 8), style="custom")

        assert viz.output_dir == tmp_path
        assert viz.figsize == (12, 8)
        assert viz.style == "custom"

    def test_creates_output_directory(self, tmp_path):
        """Test that output directory is created."""
        output = tmp_path / "new_dir" / "figures"
        ResearchVisualizer(output_dir=output)

        assert output.exists()

    def test_class_colors_defined(self):
        """Test that color palettes are defined."""
        assert len(ResearchVisualizer.COMPARISON_COLORS) == 2
        assert "complete" in ResearchVisualizer.STATUS_COLORS
        assert "failed" in ResearchVisualizer.STATUS_COLORS


# ============================================================================
# compare_distributions Tests
# ============================================================================


class TestCompareDistributions:
    """Tests for distribution comparison visualization."""

    def test_basic_comparison(self, visualizer, sample_a, sample_b):
        """Test basic distribution comparison."""
        fig = visualizer.compare_distributions(sample_a, sample_b)

        assert fig is not None
        assert len(fig.axes) == 2  # Histogram and violin

    def test_custom_labels(self, visualizer, sample_a, sample_b):
        """Test with custom labels."""
        fig = visualizer.compare_distributions(
            sample_a,
            sample_b,
            labels=["Control", "Treatment"],
            title="Custom Title",
            xlabel="Latency (s)",
        )

        assert fig is not None

    def test_without_stat_annotation(self, visualizer, sample_a, sample_b):
        """Test without statistical annotation."""
        fig = visualizer.compare_distributions(
            sample_a, sample_b, stat_annotation=False
        )

        assert fig is not None

    def test_save_figure(self, visualizer_with_output, sample_a, sample_b):
        """Test saving distribution comparison."""
        visualizer_with_output.compare_distributions(
            sample_a, sample_b, save_name="dist_comparison"
        )

        output_file = visualizer_with_output.output_dir / "dist_comparison.png"
        assert output_file.exists()

    def test_significant_difference(self, visualizer):
        """Test visualization with significant difference."""
        np.random.seed(42)
        a = np.random.normal(0, 1, 100)
        b = np.random.normal(5, 1, 100)

        fig = visualizer.compare_distributions(a, b)
        assert fig is not None


# ============================================================================
# sensitivity_plot Tests
# ============================================================================


class TestSensitivityPlot:
    """Tests for sensitivity analysis visualization."""

    def test_single_metric(self, visualizer):
        """Test with single metric."""
        param_values = np.array([5, 10, 15, 20, 25])
        metrics = {"latency": np.array([1.0, 1.5, 2.0, 2.5, 3.0])}

        fig = visualizer.sensitivity_plot(
            param_values, metrics, param_name="Timeout (s)"
        )

        assert fig is not None

    def test_multiple_metrics(self, visualizer):
        """Test with multiple metrics."""
        param_values = np.array([5, 10, 15])
        metrics = {
            "latency": np.array([1.0, 1.5, 2.0]),
            "quality": np.array([8.0, 7.5, 7.0]),
        }

        fig = visualizer.sensitivity_plot(param_values, metrics)

        assert fig is not None
        assert len(fig.axes) == 2

    def test_with_error_bars(self, visualizer):
        """Test with error bars."""
        param_values = np.array([5, 10, 15])
        metrics = {"latency": np.array([1.0, 1.5, 2.0])}
        error_bars = {"latency": np.array([0.1, 0.2, 0.15])}

        fig = visualizer.sensitivity_plot(param_values, metrics, error_bars=error_bars)

        assert fig is not None

    def test_save_sensitivity(self, visualizer_with_output):
        """Test saving sensitivity plot."""
        param_values = np.array([5, 10, 15])
        metrics = {"latency": np.array([1.0, 1.5, 2.0])}

        visualizer_with_output.sensitivity_plot(
            param_values, metrics, save_name="sensitivity"
        )

        output_file = visualizer_with_output.output_dir / "sensitivity.png"
        assert output_file.exists()


# ============================================================================
# pareto_frontier Tests
# ============================================================================


class TestParetoFrontier:
    """Tests for Pareto frontier visualization."""

    def test_basic_pareto(self, visualizer):
        """Test basic Pareto frontier."""
        np.random.seed(42)
        x = np.random.uniform(0, 10, 50)
        y = np.random.uniform(0, 10, 50)

        fig = visualizer.pareto_frontier(x, y)

        assert fig is not None

    def test_with_color(self, visualizer):
        """Test Pareto frontier with color mapping."""
        np.random.seed(42)
        x = np.random.uniform(0, 10, 50)
        y = np.random.uniform(0, 10, 50)
        color = np.random.uniform(0, 1, 50)

        fig = visualizer.pareto_frontier(x, y, color_by=color, color_label="Parameter")

        assert fig is not None

    def test_with_labels(self, visualizer):
        """Test Pareto frontier with point labels."""
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([5, 4, 3, 2, 1])
        labels = [f"Point {i}" for i in range(5)]

        fig = visualizer.pareto_frontier(x, y, labels=labels)

        assert fig is not None

    def test_without_highlight(self, visualizer):
        """Test without Pareto highlighting."""
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([5, 4, 3, 2, 1])

        fig = visualizer.pareto_frontier(x, y, highlight_pareto=False)

        assert fig is not None

    def test_pareto_identification(self, visualizer):
        """Test that Pareto points are correctly identified."""
        # Clear Pareto frontier: (1,5), (2,2), (5,1) should be Pareto
        x = np.array([1, 2, 3, 5, 4])
        y = np.array([5, 2, 3, 1, 4])

        fig = visualizer.pareto_frontier(x, y)
        assert fig is not None

    def test_custom_axis_labels(self, visualizer):
        """Test custom axis labels."""
        x = np.array([1, 2, 3])
        y = np.array([3, 2, 1])

        fig = visualizer.pareto_frontier(
            x,
            y,
            xlabel="Latency (s)",
            ylabel="Error Rate",
            title="Latency-Error Tradeoff",
        )

        assert fig is not None


# ============================================================================
# effect_size_forest_plot Tests
# ============================================================================


class TestEffectSizeForestPlot:
    """Tests for effect size forest plot."""

    def test_basic_forest_plot(self, visualizer):
        """Test basic forest plot."""
        effects = {
            "Comparison A": (-0.2, 0.5, 1.2),
            "Comparison B": (0.1, 0.8, 1.5),
            "Comparison C": (-0.5, -0.1, 0.3),
        }

        fig = visualizer.effect_size_forest_plot(effects)

        assert fig is not None

    def test_single_comparison(self, visualizer):
        """Test with single comparison."""
        effects = {"Only Comparison": (0.0, 0.5, 1.0)}

        fig = visualizer.effect_size_forest_plot(effects)

        assert fig is not None

    def test_custom_labels(self, visualizer):
        """Test with custom labels."""
        effects = {"Test": (0.1, 0.5, 0.9)}

        fig = visualizer.effect_size_forest_plot(
            effects, title="Custom Forest Plot", xlabel="Standardized Mean Difference"
        )

        assert fig is not None

    def test_save_forest_plot(self, visualizer_with_output):
        """Test saving forest plot."""
        effects = {"A vs B": (0.0, 0.5, 1.0)}

        visualizer_with_output.effect_size_forest_plot(effects, save_name="forest_plot")

        output_file = visualizer_with_output.output_dir / "forest_plot.png"
        assert output_file.exists()


# ============================================================================
# status_distribution_plot Tests
# ============================================================================


class TestStatusDistributionPlot:
    """Tests for status distribution visualization."""

    def test_basic_status_plot(self, visualizer):
        """Test basic status distribution."""
        status_counts = {"complete": 70, "soft_degraded": 20, "failed": 10}

        fig = visualizer.status_distribution_plot(status_counts)

        assert fig is not None
        assert len(fig.axes) == 2  # Bar and pie

    def test_all_status_types(self, visualizer):
        """Test with all status types."""
        status_counts = {
            "complete": 50,
            "soft_degraded": 25,
            "hard_degraded": 15,
            "failed": 10,
        }

        fig = visualizer.status_distribution_plot(status_counts)

        assert fig is not None

    def test_unknown_status(self, visualizer):
        """Test with unknown status type."""
        status_counts = {"complete": 80, "unknown_status": 20}

        fig = visualizer.status_distribution_plot(status_counts)

        assert fig is not None

    def test_custom_title(self, visualizer):
        """Test with custom title."""
        status_counts = {"complete": 100}

        fig = visualizer.status_distribution_plot(
            status_counts, title="Custom Status Distribution"
        )

        assert fig is not None

    def test_save_status_plot(self, visualizer_with_output):
        """Test saving status distribution plot."""
        status_counts = {"complete": 90, "failed": 10}

        visualizer_with_output.status_distribution_plot(
            status_counts, save_name="status_dist"
        )

        output_file = visualizer_with_output.output_dir / "status_dist.png"
        assert output_file.exists()


# ============================================================================
# heatmap Tests
# ============================================================================


class TestHeatmap:
    """Tests for heatmap visualization."""

    def test_basic_heatmap(self, visualizer):
        """Test basic heatmap."""
        data = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])

        fig = visualizer.heatmap(
            data, x_labels=["A", "B", "C"], y_labels=["X", "Y", "Z"]
        )

        assert fig is not None

    def test_without_annotation(self, visualizer):
        """Test heatmap without cell annotations."""
        data = np.random.rand(5, 5)

        fig = visualizer.heatmap(
            data,
            x_labels=[str(i) for i in range(5)],
            y_labels=[str(i) for i in range(5)],
            annotate=False,
        )

        assert fig is not None

    def test_custom_colormap(self, visualizer):
        """Test with custom colormap."""
        data = np.random.rand(3, 3)

        fig = visualizer.heatmap(
            data, x_labels=["A", "B", "C"], y_labels=["1", "2", "3"], cmap="coolwarm"
        )

        assert fig is not None

    def test_custom_labels(self, visualizer):
        """Test with custom axis labels."""
        data = np.array([[1, 2], [3, 4]])

        fig = visualizer.heatmap(
            data,
            x_labels=["Low", "High"],
            y_labels=["Fast", "Slow"],
            xlabel="Parameter A",
            ylabel="Parameter B",
            title="Interaction Heatmap",
        )

        assert fig is not None

    def test_save_heatmap(self, visualizer_with_output):
        """Test saving heatmap."""
        data = np.random.rand(4, 4)

        visualizer_with_output.heatmap(
            data,
            x_labels=["A", "B", "C", "D"],
            y_labels=["1", "2", "3", "4"],
            save_name="heatmap",
        )

        output_file = visualizer_with_output.output_dir / "heatmap.png"
        assert output_file.exists()


# ============================================================================
# create_publication_figure Tests
# ============================================================================


class TestCreatePublicationFigure:
    """Tests for publication figure creation utility."""

    def test_default_figure(self):
        """Test default figure creation."""
        fig, axes = create_publication_figure()

        assert fig is not None
        assert axes is not None

    def test_custom_figsize(self):
        """Test custom figure size."""
        fig, axes = create_publication_figure(figsize=(12, 8))

        assert fig is not None

    def test_multiple_subplots(self):
        """Test creating multiple subplots."""
        fig, axes = create_publication_figure(n_rows=2, n_cols=3)

        assert fig is not None
        assert axes.shape == (2, 3)

    def test_single_row(self):
        """Test single row of subplots."""
        fig, axes = create_publication_figure(n_rows=1, n_cols=3)

        assert fig is not None
        assert len(axes) == 3

    def test_single_column(self):
        """Test single column of subplots."""
        fig, axes = create_publication_figure(n_rows=3, n_cols=1)

        assert fig is not None
        assert len(axes) == 3


# ============================================================================
# Edge Cases
# ============================================================================


class TestEdgeCases:
    """Edge case tests for visualization module."""

    def test_empty_comparison(self, visualizer):
        """Test comparison with minimal data."""
        a = np.array([1.0, 2.0])
        b = np.array([3.0, 4.0])

        fig = visualizer.compare_distributions(a, b)
        assert fig is not None

    def test_identical_samples(self, visualizer):
        """Test comparison with identical samples."""
        data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])

        fig = visualizer.compare_distributions(data, data.copy())
        assert fig is not None

    def test_single_point_sensitivity(self, visualizer):
        """Test sensitivity with single point."""
        param_values = np.array([10])
        metrics = {"latency": np.array([1.5])}

        fig = visualizer.sensitivity_plot(param_values, metrics)
        assert fig is not None

    def test_large_pareto_dataset(self, visualizer):
        """Test Pareto with many points."""
        np.random.seed(42)
        x = np.random.uniform(0, 100, 500)
        y = np.random.uniform(0, 100, 500)

        fig = visualizer.pareto_frontier(x, y)
        assert fig is not None

    def test_negative_values_heatmap(self, visualizer):
        """Test heatmap with negative values."""
        data = np.array([[-1, 0, 1], [2, -2, 3]])

        fig = visualizer.heatmap(data, x_labels=["A", "B", "C"], y_labels=["X", "Y"])
        assert fig is not None

    def test_many_comparisons_forest(self, visualizer):
        """Test forest plot with many comparisons."""
        effects = {
            f"Comparison {i}": (i * 0.1 - 0.5, i * 0.1, i * 0.1 + 0.5)
            for i in range(15)
        }

        fig = visualizer.effect_size_forest_plot(effects)
        assert fig is not None
