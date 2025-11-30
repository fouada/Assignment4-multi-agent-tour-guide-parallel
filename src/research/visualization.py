"""
Research Visualization Tools
============================

Publication-quality visualization for MIT-level research output.

Provides:
1. Statistical comparison plots
2. Sensitivity analysis visualization
3. Pareto frontier visualization
4. Effect size forest plots
5. Distribution comparison plots

Author: Multi-Agent Tour Guide Research Team
Version: 1.0.0
Date: November 2025
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np

# Lazy imports for visualization dependencies
_plt = None
_sns = None


def _import_viz():
    """Lazy import of visualization libraries."""
    global _plt, _sns
    if _plt is None:
        import matplotlib.pyplot as plt
        import seaborn as sns
        _plt = plt
        _sns = sns
        
        # Set publication-quality style
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.rcParams.update({
            'font.size': 12,
            'axes.titlesize': 14,
            'axes.labelsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 10,
            'figure.titlesize': 16,
            'figure.dpi': 100,
            'savefig.dpi': 300,
            'savefig.bbox': 'tight',
        })
    return _plt, _sns


class ResearchVisualizer:
    """
    Publication-quality visualization for research results.
    
    Example:
        viz = ResearchVisualizer(output_dir=Path("./figures"))
        
        # Distribution comparison
        viz.compare_distributions(
            sample_a, sample_b, 
            labels=["Default", "Aggressive"],
            title="Latency Distribution Comparison"
        )
        
        # Sensitivity plot
        viz.sensitivity_plot(
            param_values=[5, 10, 15, 20, 25],
            metrics={'latency': [2.1, 2.5, 3.0, 3.8, 4.5]},
            param_name="Soft Timeout (s)"
        )
    """
    
    # Color palettes for different use cases
    COMPARISON_COLORS = ['#3498db', '#e74c3c']  # Blue vs Red
    STATUS_COLORS = {
        'complete': '#2ecc71',
        'soft_degraded': '#f1c40f', 
        'hard_degraded': '#e67e22',
        'failed': '#e74c3c'
    }
    GRADIENT_CMAP = 'viridis'
    
    def __init__(
        self, 
        output_dir: Optional[Path] = None,
        figsize: Tuple[int, int] = (10, 6),
        style: str = 'publication'
    ):
        self.output_dir = Path(output_dir) if output_dir else None
        self.figsize = figsize
        self.style = style
        
        if self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _save_figure(self, fig, name: str):
        """Save figure if output_dir is set."""
        if self.output_dir:
            path = self.output_dir / f"{name}.png"
            fig.savefig(path, dpi=300, bbox_inches='tight')
            print(f"📊 Saved: {path}")
    
    def compare_distributions(
        self,
        sample_a: np.ndarray,
        sample_b: np.ndarray,
        labels: List[str] = ["A", "B"],
        title: str = "Distribution Comparison",
        xlabel: str = "Value",
        stat_annotation: bool = True,
        save_name: Optional[str] = None
    ):
        """
        Compare two distributions with overlapping histograms and KDE.
        
        Args:
            sample_a, sample_b: Samples to compare
            labels: Labels for the two groups
            title: Plot title
            xlabel: X-axis label
            stat_annotation: Add statistical test annotation
            save_name: Filename for saving (without extension)
        """
        plt, sns = _import_viz()
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Overlapping histograms with KDE
        ax1 = axes[0]
        sns.histplot(sample_a, stat='density', alpha=0.5, label=labels[0], 
                    color=self.COMPARISON_COLORS[0], kde=True, ax=ax1)
        sns.histplot(sample_b, stat='density', alpha=0.5, label=labels[1],
                    color=self.COMPARISON_COLORS[1], kde=True, ax=ax1)
        ax1.set_xlabel(xlabel)
        ax1.set_ylabel('Density')
        ax1.set_title(f'{title} - Overlapping', fontweight='bold')
        ax1.legend()
        
        # Violin plot
        ax2 = axes[1]
        data = [sample_a, sample_b]
        parts = ax2.violinplot(data, showmeans=True, showmedians=True)
        for i, pc in enumerate(parts['bodies']):
            pc.set_facecolor(self.COMPARISON_COLORS[i])
            pc.set_alpha(0.7)
        ax2.set_xticks([1, 2])
        ax2.set_xticklabels(labels)
        ax2.set_ylabel(xlabel)
        ax2.set_title(f'{title} - Violin Plot', fontweight='bold')
        
        # Add statistical annotation
        if stat_annotation:
            from scipy import stats
            _, p_value = stats.ttest_ind(sample_a, sample_b, equal_var=False)
            sig = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else "ns"
            ax2.annotate(f'p = {p_value:.2e} ({sig})', xy=(0.5, 0.95), 
                        xycoords='axes fraction', ha='center', fontsize=10)
        
        plt.tight_layout()
        
        if save_name:
            self._save_figure(fig, save_name)
        
        plt.show()
        return fig
    
    def sensitivity_plot(
        self,
        param_values: np.ndarray,
        metrics: Dict[str, np.ndarray],
        param_name: str = "Parameter",
        title: str = "Sensitivity Analysis",
        error_bars: Optional[Dict[str, np.ndarray]] = None,
        save_name: Optional[str] = None
    ):
        """
        Plot sensitivity analysis results.
        
        Args:
            param_values: Parameter values tested
            metrics: Dictionary of metric names to values
            param_name: Name of varied parameter
            title: Plot title
            error_bars: Optional dictionary of standard deviations
            save_name: Filename for saving
        """
        plt, sns = _import_viz()
        
        n_metrics = len(metrics)
        fig, axes = plt.subplots(1, n_metrics, figsize=(5*n_metrics, 5))
        if n_metrics == 1:
            axes = [axes]
        
        colors = sns.color_palette("husl", n_metrics)
        
        for idx, (metric_name, values) in enumerate(metrics.items()):
            ax = axes[idx]
            
            ax.plot(param_values, values, 'o-', color=colors[idx], 
                   linewidth=2, markersize=8, label=metric_name)
            
            if error_bars and metric_name in error_bars:
                ax.fill_between(param_values,
                               np.array(values) - np.array(error_bars[metric_name]),
                               np.array(values) + np.array(error_bars[metric_name]),
                               alpha=0.3, color=colors[idx])
            
            ax.set_xlabel(param_name, fontsize=12)
            ax.set_ylabel(metric_name, fontsize=12)
            ax.set_title(f'{metric_name} vs {param_name}', fontweight='bold')
            ax.grid(True, alpha=0.3)
        
        fig.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        if save_name:
            self._save_figure(fig, save_name)
        
        plt.show()
        return fig
    
    def pareto_frontier(
        self,
        x: np.ndarray,
        y: np.ndarray,
        color_by: Optional[np.ndarray] = None,
        labels: Optional[List[str]] = None,
        xlabel: str = "Objective 1",
        ylabel: str = "Objective 2",
        color_label: str = "Parameter",
        title: str = "Pareto Frontier",
        highlight_pareto: bool = True,
        save_name: Optional[str] = None
    ):
        """
        Visualize Pareto frontier for multi-objective optimization.
        
        Args:
            x, y: Objective values
            color_by: Optional values for coloring points
            labels: Point labels for annotation
            xlabel, ylabel: Axis labels
            color_label: Color bar label
            title: Plot title
            highlight_pareto: Highlight Pareto-optimal points
            save_name: Filename for saving
        """
        plt, sns = _import_viz()
        
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Identify Pareto-optimal points (assuming minimization of both)
        is_pareto = []
        for i in range(len(x)):
            pareto = True
            for j in range(len(x)):
                if i != j and x[j] <= x[i] and y[j] <= y[i] and (x[j] < x[i] or y[j] < y[i]):
                    pareto = False
                    break
            is_pareto.append(pareto)
        
        is_pareto = np.array(is_pareto)
        
        # Plot all points
        if color_by is not None:
            scatter = ax.scatter(x[~is_pareto], y[~is_pareto], c=color_by[~is_pareto],
                               cmap=self.GRADIENT_CMAP, alpha=0.4, s=60, edgecolors='gray')
            plt.colorbar(scatter, ax=ax, label=color_label)
        else:
            ax.scatter(x[~is_pareto], y[~is_pareto], color='gray', alpha=0.4, s=60)
        
        # Highlight Pareto-optimal points
        if highlight_pareto and np.any(is_pareto):
            if color_by is not None:
                ax.scatter(x[is_pareto], y[is_pareto], c=color_by[is_pareto],
                          cmap=self.GRADIENT_CMAP, s=150, edgecolors='red', linewidths=2,
                          marker='*', zorder=5)
            else:
                ax.scatter(x[is_pareto], y[is_pareto], color='red', s=150, 
                          edgecolors='black', marker='*', zorder=5, label='Pareto-optimal')
            
            # Connect Pareto points
            pareto_x = x[is_pareto]
            pareto_y = y[is_pareto]
            sort_idx = np.argsort(pareto_x)
            ax.plot(pareto_x[sort_idx], pareto_y[sort_idx], 'r--', alpha=0.5, linewidth=2)
        
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        if labels is not None:
            for i, label in enumerate(labels):
                if is_pareto[i]:
                    ax.annotate(label, (x[i], y[i]), fontsize=8, 
                               xytext=(5, 5), textcoords='offset points')
        
        plt.tight_layout()
        
        if save_name:
            self._save_figure(fig, save_name)
        
        plt.show()
        return fig
    
    def effect_size_forest_plot(
        self,
        effects: Dict[str, Tuple[float, float, float]],
        title: str = "Effect Size Comparison",
        xlabel: str = "Effect Size (Cohen's d)",
        save_name: Optional[str] = None
    ):
        """
        Create forest plot for effect sizes with confidence intervals.
        
        Args:
            effects: Dictionary mapping comparison names to (lower, estimate, upper) CI
            title: Plot title
            xlabel: X-axis label
            save_name: Filename for saving
        """
        plt, sns = _import_viz()
        
        names = list(effects.keys())
        estimates = [effects[n][1] for n in names]
        ci_lower = [effects[n][0] for n in names]
        ci_upper = [effects[n][2] for n in names]
        
        fig, ax = plt.subplots(figsize=(10, len(names) * 0.8 + 2))
        
        y_positions = range(len(names))
        
        # Plot CIs
        for i, name in enumerate(names):
            ax.plot([ci_lower[i], ci_upper[i]], [i, i], 'b-', linewidth=2)
            ax.plot(estimates[i], i, 'bo', markersize=10)
        
        # Reference line at 0
        ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
        
        # Effect size boundaries
        for boundary, label in [(0.2, 'Small'), (0.5, 'Medium'), (0.8, 'Large')]:
            ax.axvline(x=boundary, color='gray', linestyle=':', alpha=0.3)
            ax.axvline(x=-boundary, color='gray', linestyle=':', alpha=0.3)
        
        ax.set_yticks(y_positions)
        ax.set_yticklabels(names)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        
        if save_name:
            self._save_figure(fig, save_name)
        
        plt.show()
        return fig
    
    def status_distribution_plot(
        self,
        status_counts: Dict[str, int],
        title: str = "Queue Status Distribution",
        save_name: Optional[str] = None
    ):
        """
        Visualize queue status distribution with custom colors.
        
        Args:
            status_counts: Dictionary of status -> count
            title: Plot title
            save_name: Filename for saving
        """
        plt, sns = _import_viz()
        
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        statuses = list(status_counts.keys())
        counts = list(status_counts.values())
        colors = [self.STATUS_COLORS.get(s, '#95a5a6') for s in statuses]
        
        # Bar chart
        ax1 = axes[0]
        bars = ax1.bar(statuses, counts, color=colors, edgecolor='black')
        ax1.set_xlabel('Status', fontsize=12)
        ax1.set_ylabel('Count', fontsize=12)
        ax1.set_title(f'{title} - Bar Chart', fontweight='bold')
        
        # Add percentages
        total = sum(counts)
        for bar, count in zip(bars, counts):
            pct = count / total * 100
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + total*0.01,
                    f'{pct:.1f}%', ha='center', fontsize=10)
        
        # Pie chart
        ax2 = axes[1]
        ax2.pie(counts, labels=statuses, colors=colors, autopct='%1.1f%%',
               startangle=90, explode=[0.02]*len(statuses))
        ax2.set_title(f'{title} - Pie Chart', fontweight='bold')
        
        plt.tight_layout()
        
        if save_name:
            self._save_figure(fig, save_name)
        
        plt.show()
        return fig
    
    def heatmap(
        self,
        data: np.ndarray,
        x_labels: List[str],
        y_labels: List[str],
        xlabel: str = "X",
        ylabel: str = "Y",
        title: str = "Heatmap",
        cmap: str = 'RdYlGn',
        annotate: bool = True,
        save_name: Optional[str] = None
    ):
        """
        Create annotated heatmap for parameter interactions.
        
        Args:
            data: 2D array of values
            x_labels, y_labels: Axis tick labels
            xlabel, ylabel: Axis labels
            title: Plot title
            cmap: Colormap
            annotate: Show values in cells
            save_name: Filename for saving
        """
        plt, sns = _import_viz()
        
        fig, ax = plt.subplots(figsize=self.figsize)
        
        sns.heatmap(data, ax=ax, cmap=cmap, annot=annotate, fmt='.2f',
                   xticklabels=x_labels, yticklabels=y_labels,
                   cbar_kws={'label': 'Value'})
        
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        if save_name:
            self._save_figure(fig, save_name)
        
        plt.show()
        return fig


def create_publication_figure(
    figsize: Tuple[float, float] = (7, 5),
    n_rows: int = 1,
    n_cols: int = 1
):
    """
    Create figure with publication-ready settings.
    
    Returns:
        Tuple of (figure, axes)
    """
    plt, _ = _import_viz()
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
    
    return fig, axes

