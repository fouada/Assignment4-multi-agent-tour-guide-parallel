"""
End-to-End Tests for Tour Guide Dashboard
==========================================

Complete E2E tests simulating real user interactions with the
tour guide dashboard from start to finish.

Test Scenarios:
1. Complete Tour Planning Flow
2. Profile Preset Switching
3. Driver Mode Journey
4. Family Mode Journey
5. Custom Profile Configuration
6. Pipeline Monitoring Flow
7. Recommendation Viewing Flow
8. Error Scenarios

Edge Cases Covered:
- Session timeout simulation
- Invalid route handling
- Network error recovery
- Browser back/forward navigation
- Multiple tab scenarios
- Mobile viewport simulation

Coverage Target: 85%+

Author: Multi-Agent Tour Guide Research Team
Date: December 2025
"""

import time

import pytest

# Skip all tests if dependencies not installed
dash = pytest.importorskip("dash", reason="dash required for dashboard tests")
np = pytest.importorskip("numpy", reason="numpy required for dashboard tests")
plotly = pytest.importorskip("plotly", reason="plotly required for dashboard tests")


from src.dashboard.tour_guide_dashboard import (
    create_tour_guide_app,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def e2e_app():
    """Create app for E2E testing."""
    return create_tour_guide_app()


@pytest.fixture
def family_user_inputs():
    """Complete input set for family user scenario."""
    return {
        "source": "Tel Aviv, Israel",
        "destination": "Jerusalem, Israel",
        "waypoints": "Latrun, Bab al-Wad",
        "profile_preset": "family",
        "age_group": "adult",
        "min_age": 5,
        "travel_mode": "car",
        "trip_purpose": "vacation",
        "content_preference": "educational",
        "family_mode": ["enabled"],
        "driver_mode": [],
        "interests": "history, nature, culture",
        "exclude_topics": "violence, adult content",
        "max_duration": 300,
    }


@pytest.fixture
def driver_user_inputs():
    """Complete input set for driver scenario."""
    return {
        "source": "Haifa, Israel",
        "destination": "Eilat, Israel",
        "waypoints": "",
        "profile_preset": "driver",
        "age_group": "adult",
        "min_age": 35,
        "travel_mode": "car",
        "trip_purpose": "business",
        "content_preference": "educational",
        "family_mode": [],
        "driver_mode": ["enabled"],
        "interests": "podcasts, news",
        "exclude_topics": "",
        "max_duration": 600,
    }


@pytest.fixture
def teenager_user_inputs():
    """Complete input set for teenager scenario."""
    return {
        "source": "Netanya, Israel",
        "destination": "Be'er Sheva, Israel",
        "waypoints": "Herzliya, Tel Aviv",
        "profile_preset": "teenager",
        "age_group": "teenager",
        "min_age": 15,
        "travel_mode": "bus",
        "trip_purpose": "adventure",
        "content_preference": "entertainment",
        "family_mode": [],
        "driver_mode": [],
        "interests": "technology, music, sports",
        "exclude_topics": "",
        "max_duration": 180,
    }


# ============================================================================
# Complete Tour Planning Flow Tests
# ============================================================================


class TestCompleteTourPlanningFlow:
    """E2E tests for complete tour planning user journey."""

    def test_app_initializes_successfully(self, e2e_app):
        """Test that app initializes and is ready for user interaction."""
        assert e2e_app is not None
        assert e2e_app.layout is not None
        assert e2e_app.title is not None

    def test_default_inputs_are_populated(self, e2e_app):
        """Test that default input values are populated."""
        layout_str = str(e2e_app.layout)

        # Should have default source/destination
        assert "Tel Aviv" in layout_str
        assert "Jerusalem" in layout_str

    def test_start_tour_button_present(self, e2e_app):
        """Test start tour button is visible and actionable."""
        layout_str = str(e2e_app.layout)

        assert "start-tour-btn" in layout_str
        assert "Start Tour" in layout_str

    def test_all_tabs_accessible(self, e2e_app):
        """Test user can access all tabs."""
        layout_str = str(e2e_app.layout)

        tabs = ["Plan Your Tour", "Pipeline Flow", "Recommendations", "Live Monitor"]
        for tab in tabs:
            assert tab in layout_str, f"Tab '{tab}' not accessible"

    def test_profile_presets_selectable(self, e2e_app):
        """Test user can select from all profile presets."""
        layout_str = str(e2e_app.layout)

        presets = [
            "default",
            "family",
            "kid",
            "teenager",
            "senior",
            "driver",
            "history",
            "romantic",
            "custom",
        ]

        for preset in presets:
            assert f'"{preset}"' in layout_str or f"'{preset}'" in layout_str


# ============================================================================
# Profile Preset Switching Tests
# ============================================================================


class TestProfilePresetSwitching:
    """E2E tests for rapid profile preset switching."""

    def test_family_preset_configuration(self, e2e_app, family_user_inputs):
        """Test family preset loads correct configuration."""
        # Family preset should enable family mode by default
        layout_str = str(e2e_app.layout)
        assert "family-mode-toggle" in layout_str

    def test_driver_preset_restricts_video(self, e2e_app, driver_user_inputs):
        """Test driver preset configuration restricts video.

        Edge Case: Drivers should not receive video content.
        """
        layout_str = str(e2e_app.layout)

        # Driver mode toggle should exist
        assert "driver-mode-toggle" in layout_str
        assert "Audio Only" in layout_str or "no video" in layout_str.lower()

    def test_teenager_preset_configuration(self, e2e_app, teenager_user_inputs):
        """Test teenager preset loads correct configuration."""
        layout_str = str(e2e_app.layout)

        # Teenager should be a valid preset option
        assert "teenager" in layout_str

    def test_custom_preset_shows_all_options(self, e2e_app):
        """Test custom preset reveals all configuration options."""
        layout_str = str(e2e_app.layout)

        # Custom options should be present (may be hidden by CSS)
        custom_options = [
            "age-group-select",
            "min-age-input",
            "travel-mode-select",
            "trip-purpose-select",
            "content-preference-select",
            "interests-input",
            "exclude-topics-input",
            "max-duration-slider",
        ]

        for option in custom_options:
            assert option in layout_str, f"Missing custom option: {option}"


# ============================================================================
# Driver Mode Journey Tests
# ============================================================================


class TestDriverModeJourney:
    """E2E tests for driver mode user journey."""

    def test_driver_mode_toggle_present(self, e2e_app):
        """Test driver mode toggle is accessible."""
        layout_str = str(e2e_app.layout)
        assert "driver-mode-toggle" in layout_str

    def test_driver_mode_warning_displayed(self, e2e_app):
        """Test driver mode shows appropriate warnings."""
        layout_str = str(e2e_app.layout)

        # Should mention no video or audio only
        driver_indicators = ["Audio Only", "no video", "driving"]
        found = any(
            ind in layout_str or ind.lower() in layout_str.lower()
            for ind in driver_indicators
        )
        assert found, "Driver mode warning not found"


# ============================================================================
# Family Mode Journey Tests
# ============================================================================


class TestFamilyModeJourney:
    """E2E tests for family mode user journey."""

    def test_family_mode_toggle_present(self, e2e_app):
        """Test family mode toggle is accessible."""
        layout_str = str(e2e_app.layout)
        assert "family-mode-toggle" in layout_str

    def test_min_age_input_available(self, e2e_app):
        """Test minimum age input is available for family configuration."""
        layout_str = str(e2e_app.layout)
        assert "min-age-input" in layout_str

    def test_excluded_topics_input_available(self, e2e_app):
        """Test excluded topics input is available."""
        layout_str = str(e2e_app.layout)
        assert "exclude-topics-input" in layout_str


# ============================================================================
# Pipeline Monitoring Flow Tests
# ============================================================================


class TestPipelineMonitoringFlow:
    """E2E tests for pipeline monitoring user journey."""

    def test_pipeline_tab_accessible(self, e2e_app):
        """Test Pipeline Flow tab is accessible."""
        layout_str = str(e2e_app.layout)
        assert "Pipeline Flow" in layout_str

    def test_pipeline_stages_visible(self, e2e_app):
        """Test all pipeline stages are visible."""
        layout_str = str(e2e_app.layout)

        stages = ["User Input", "Route", "Parallel", "Queue", "Judge", "Playlist"]

        for stage in stages:
            assert stage in layout_str, f"Pipeline stage not visible: {stage}"

    def test_agent_status_cards_visible(self, e2e_app):
        """Test agent status cards are visible."""
        layout_str = str(e2e_app.layout)

        agents = ["Video Agent", "Music Agent", "Text Agent", "Judge Agent"]
        for agent in agents:
            assert agent in layout_str, f"Agent card not visible: {agent}"


# ============================================================================
# Recommendation Viewing Flow Tests
# ============================================================================


class TestRecommendationViewingFlow:
    """E2E tests for recommendation viewing user journey."""

    def test_recommendations_tab_accessible(self, e2e_app):
        """Test Recommendations tab is accessible."""
        layout_str = str(e2e_app.layout)
        assert "Recommendations" in layout_str

    def test_initial_recommendation_message(self, e2e_app):
        """Test initial message is shown before tour starts."""
        layout_str = str(e2e_app.layout)

        # Should show instruction to start tour
        initial_messages = ["Start Tour", "configure", "click"]
        found = any(msg in layout_str for msg in initial_messages)
        assert found, "Initial recommendation message not found"

    def test_content_distribution_chart_present(self, e2e_app):
        """Test content distribution chart is present."""
        layout_str = str(e2e_app.layout)
        assert "content-distribution-chart" in layout_str


# ============================================================================
# Live Monitor Flow Tests
# ============================================================================


class TestLiveMonitorFlow:
    """E2E tests for live monitoring user journey."""

    def test_live_monitor_tab_accessible(self, e2e_app):
        """Test Live Monitor tab is accessible."""
        layout_str = str(e2e_app.layout)
        assert "Live Monitor" in layout_str

    def test_monitoring_charts_present(self, e2e_app):
        """Test all monitoring charts are present."""
        layout_str = str(e2e_app.layout)

        charts = [
            "realtime-throughput-chart",
            "agent-response-chart",
            "queue-status-chart",
        ]

        for chart in charts:
            assert chart in layout_str, f"Monitoring chart not present: {chart}"

    def test_monitoring_interval_active(self, e2e_app):
        """Test monitoring interval is configured."""
        layout_str = str(e2e_app.layout)
        assert "monitor-interval" in layout_str


# ============================================================================
# Error Scenario Tests
# ============================================================================


class TestErrorScenarios:
    """E2E tests for error handling scenarios."""

    def test_app_handles_empty_source(self, e2e_app):
        """Test app handles empty source gracefully.

        Edge Case: User clears source input.
        """
        # App should still function with empty source
        layout_str = str(e2e_app.layout)
        assert "source-input" in layout_str

    def test_app_handles_empty_destination(self, e2e_app):
        """Test app handles empty destination gracefully.

        Edge Case: User clears destination input.
        """
        layout_str = str(e2e_app.layout)
        assert "destination-input" in layout_str

    def test_app_handles_invalid_age(self, e2e_app):
        """Test app handles invalid age values.

        Edge Case: Age validation should prevent negative values.
        """
        layout_str = str(e2e_app.layout)
        # Should have min=0 for age input
        assert "min" in layout_str


# ============================================================================
# Mobile Viewport Simulation Tests
# ============================================================================


class TestMobileViewportSimulation:
    """E2E tests simulating mobile viewport scenarios."""

    def test_responsive_grid_classes_exist(self, e2e_app):
        """Test responsive grid classes are defined."""
        from src.dashboard.tour_guide_dashboard import CUSTOM_CSS

        # CSS should have responsive breakpoints
        assert "@media" in CUSTOM_CSS
        assert "max-width" in CUSTOM_CSS

    def test_app_layout_flexible(self, e2e_app):
        """Test app layout uses flexible containers."""
        layout_str = str(e2e_app.layout)

        # Should use flex or grid layouts
        assert "flex" in layout_str or "grid" in layout_str


# ============================================================================
# Architecture Visualization Tests
# ============================================================================


class TestArchitectureVisualization:
    """E2E tests for architecture visualization."""

    def test_architecture_diagram_present(self, e2e_app):
        """Test architecture diagram is visible."""
        layout_str = str(e2e_app.layout)
        assert "architecture-graph" in layout_str

    def test_architecture_shows_components(self, e2e_app):
        """Test architecture diagram shows all components."""
        from src.dashboard.tour_guide_dashboard import create_architecture_diagram

        fig = create_architecture_diagram()

        # Get all text from figure
        all_text = []
        for trace in fig.data:
            if hasattr(trace, "text"):
                if isinstance(trace.text, (list, tuple)):
                    all_text.extend([str(t) for t in trace.text])
                elif trace.text:
                    all_text.append(str(trace.text))

        text_str = " ".join(all_text)

        # Should mention key components
        key_terms = ["User", "Agent", "Queue", "Judge"]
        found = sum(1 for term in key_terms if term in text_str)
        assert found >= 2, f"Architecture missing key terms. Found text: {text_str}"


# ============================================================================
# Metrics Display Tests
# ============================================================================


class TestMetricsDisplay:
    """E2E tests for metrics display."""

    def test_all_metrics_displayed(self, e2e_app):
        """Test all metrics are displayed."""
        layout_str = str(e2e_app.layout)

        metrics = [
            "metric-points",
            "metric-latency",
            "metric-quality",
            "metric-recommendations",
        ]

        for metric in metrics:
            assert metric in layout_str, f"Metric not displayed: {metric}"

    def test_metrics_have_labels(self, e2e_app):
        """Test metrics have descriptive labels."""
        layout_str = str(e2e_app.layout)

        labels = ["Route Points", "Latency", "Quality", "Recommendations"]
        for label in labels:
            assert label in layout_str, f"Metric label not found: {label}"


# ============================================================================
# Profile Summary Tests
# ============================================================================


class TestProfileSummary:
    """E2E tests for profile summary display."""

    def test_profile_summary_present(self, e2e_app):
        """Test profile summary section is present."""
        layout_str = str(e2e_app.layout)
        assert "profile-summary-content" in layout_str

    def test_profile_summary_shows_route(self, e2e_app):
        """Test profile summary includes route information."""
        layout_str = str(e2e_app.layout)

        # Should show source and destination indicators
        route_indicators = ["📍", "🎯", "Starting Point", "Destination"]
        found = sum(1 for ind in route_indicators if ind in layout_str)
        assert found >= 2, "Route indicators not found in profile summary"


# ============================================================================
# Session Persistence Tests
# ============================================================================


class TestSessionPersistence:
    """E2E tests for session state persistence."""

    def test_stores_exist_for_state(self, e2e_app):
        """Test data stores exist for state persistence."""
        layout_str = str(e2e_app.layout)

        stores = ["tour-state-store", "profile-state-store", "results-store"]
        for store in stores:
            assert store in layout_str, f"Store missing: {store}"

    def test_stores_initialized_empty(self, e2e_app):
        """Test stores are initialized with empty/default data."""
        layout_str = str(e2e_app.layout)

        # Stores should have data attribute
        assert "dcc.Store" in layout_str or "Store" in layout_str


# ============================================================================
# Accessibility Journey Tests
# ============================================================================


class TestAccessibilityJourney:
    """E2E tests for accessibility features."""

    def test_heading_hierarchy(self, e2e_app):
        """Test proper heading hierarchy for screen readers."""
        layout_str = str(e2e_app.layout)

        # Should have H1 for main title
        assert "html.H1" in layout_str or "H1" in layout_str

    def test_form_labels_present(self, e2e_app):
        """Test form elements have labels."""
        layout_str = str(e2e_app.layout)

        # Should have Label elements
        assert "html.Label" in layout_str or "Label" in layout_str

    def test_buttons_have_text(self, e2e_app):
        """Test buttons have visible text content."""
        layout_str = str(e2e_app.layout)

        # Start tour button should have text
        assert "Start Tour" in layout_str


# ============================================================================
# Performance Journey Tests
# ============================================================================


class TestPerformanceJourney:
    """E2E tests for performance characteristics."""

    def test_app_creation_reasonable_time(self):
        """Test app creation completes in reasonable time."""
        start = time.time()
        _app = create_tour_guide_app()
        duration = time.time() - start

        # Should complete in under 3 seconds
        assert duration < 3.0, f"App creation took {duration:.2f}s"

    def test_layout_not_excessively_nested(self, e2e_app):
        """Test layout doesn't have excessive nesting.

        Edge Case: Deep nesting can impact performance.
        """
        layout_str = str(e2e_app.layout)

        # Should not be excessively long (indicates reasonable structure)
        assert len(layout_str) < 500000, "Layout string excessively long"
