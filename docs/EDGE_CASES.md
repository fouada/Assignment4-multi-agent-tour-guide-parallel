# Edge Cases Documentation

## Multi-Agent Tour Guide System - Comprehensive Edge Case Coverage

This document catalogs all identified edge cases across the system components, their expected behavior, and test coverage status.

**Coverage Target: 85%+**  
**Last Updated: December 2025**

---

## Table of Contents

1. [User Input Edge Cases](#1-user-input-edge-cases)
2. [Profile Configuration Edge Cases](#2-profile-configuration-edge-cases)
3. [Driver Mode Edge Cases](#3-driver-mode-edge-cases)
4. [Family Mode Edge Cases](#4-family-mode-edge-cases)
5. [Pipeline Processing Edge Cases](#5-pipeline-processing-edge-cases)
6. [Smart Queue Edge Cases](#6-smart-queue-edge-cases)
7. [Agent Response Edge Cases](#7-agent-response-edge-cases)
8. [Content Recommendation Edge Cases](#8-content-recommendation-edge-cases)
9. [Dashboard Visualization Edge Cases](#9-dashboard-visualization-edge-cases)
10. [Performance Edge Cases](#10-performance-edge-cases)
11. [Accessibility Edge Cases](#11-accessibility-edge-cases)
12. [Error Recovery Edge Cases](#12-error-recovery-edge-cases)

---

## 1. User Input Edge Cases

### 1.1 Empty Source Location
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| UI-001 | User submits with empty source | Use default or show validation error | `test_tour_guide_dashboard.py::TestEdgeCases::test_empty_source_input` |
| UI-002 | User clears source after entering | Handle gracefully, retain last valid | `test_tour_guide_dashboard_e2e.py::TestErrorScenarios::test_app_handles_empty_source` |

### 1.2 Empty Destination Location
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| UI-003 | User submits without destination | Use default or show validation error | `test_tour_guide_dashboard.py::TestEdgeCases::test_empty_destination_input` |
| UI-004 | Same source and destination | Allow but generate single-point tour | Integration tests |

### 1.3 Unicode and Special Characters
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| UI-005 | Hebrew location names (ירושלים) | Render correctly, no encoding errors | `test_tour_guide_dashboard.py::TestEdgeCases::test_unicode_location_names` |
| UI-006 | Arabic location names (القدس) | Render correctly, RTL handling | Dashboard tests |
| UI-007 | Special characters (<>&'") | Escape properly, no XSS | `conftest.py::dashboard_edge_case_inputs` |

### 1.4 Long Input Strings
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| UI-008 | Location name > 500 chars | Truncate display, store full value | `test_tour_guide_dashboard.py::TestEdgeCases::test_very_long_location_string` |
| UI-009 | Interests list > 1000 chars | Accept and parse correctly | Input validation tests |

---

## 2. Profile Configuration Edge Cases

### 2.1 Age Boundaries
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| PC-001 | Minimum age = 0 (infant) | Accept, apply infant content rules | `test_tour_guide_dashboard.py::TestEdgeCases::test_min_age_zero` |
| PC-002 | Maximum age = 120 | Accept as valid | `test_tour_guide_dashboard.py::TestEdgeCases::test_min_age_maximum` |
| PC-003 | Negative age input | Reject with validation error | Input validation |
| PC-004 | Non-numeric age input | Show error, retain previous value | UI validation |

### 2.2 Duration Boundaries
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| PC-005 | Minimum duration (30s) | Accept, filter to short content | `test_tour_guide_dashboard.py::TestEdgeCases::test_extreme_duration_values_minimum` |
| PC-006 | Maximum duration (600s) | Accept, allow long content | `test_tour_guide_dashboard.py::TestEdgeCases::test_extreme_duration_values_maximum` |

### 2.3 Profile Preset Switching
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| PC-007 | Rapid preset switching | UI updates without lag | `test_tour_guide_dashboard.py::TestEdgeCases::test_all_profile_presets_loadable` |
| PC-008 | Custom -> Preset -> Custom | Retain custom values on return | E2E tests |

---

## 3. Driver Mode Edge Cases

### 3.1 Content Restrictions
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| DM-001 | Driver mode enabled | **NO VIDEO CONTENT** returned | `test_tour_guide_dashboard.py::TestDriverModeEdgeCases::test_driver_mode_component_exists` |
| DM-002 | Only video available | Fall back to text summary | Smart queue tests |
| DM-003 | Driver + Family combined | Audio-only family content | Integration tests |

### 3.2 Safety Features
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| DM-004 | Visual content warning | Display clear "Audio Only" badge | `test_tour_guide_dashboard.py::TestDriverModeEdgeCases::test_driver_mode_label_present` |
| DM-005 | Driver exits driving mode | Re-enable video content | UI state tests |

---

## 4. Family Mode Edge Cases

### 4.1 Content Filtering
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| FM-001 | Family mode with min_age=5 | Filter all adult content | `test_tour_guide_dashboard.py::TestFamilyModeEdgeCases::test_family_mode_component_exists` |
| FM-002 | Family mode default enabled | Enabled by default for family preset | `test_tour_guide_dashboard.py::TestFamilyModeEdgeCases::test_family_mode_default_enabled` |
| FM-003 | Excluded topics list | Respect custom exclusions | Content agent tests |

### 4.2 Age-Appropriate Content
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| FM-004 | Kid (age 5-8) content | Educational, animated preference | Profile tests |
| FM-005 | Teenager (13-19) content | Modern, engaging but appropriate | Profile tests |

---

## 5. Pipeline Processing Edge Cases

### 5.1 Route Generation
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| PP-001 | No waypoints provided | Generate direct route | Route tests |
| PP-002 | 50+ waypoints | Process all, may paginate | Performance tests |
| PP-003 | Duplicate waypoints | Remove duplicates | Route validation |

### 5.2 Pipeline State
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| PP-004 | Pipeline step timeout | Move to next step, log warning | `test_tour_guide_dashboard_integration.py::TestPipelineFlowIntegration` |
| PP-005 | All agents fail | Return graceful degradation status | Smart queue tests |

---

## 6. Smart Queue Edge Cases

### 6.1 Timeout Scenarios
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| SQ-001 | Soft timeout reached (some results) | Return SOFT_DEGRADED status | `test_smart_queue.py` |
| SQ-002 | Hard timeout reached (no results) | Return HARD_DEGRADED status | `test_smart_queue.py` |
| SQ-003 | All agents respond before soft timeout | Return COMPLETE status | `test_smart_queue.py` |
| SQ-004 | Only one agent responds | Return partial results | `test_smart_queue.py` |

### 6.2 Result Collection
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| SQ-005 | Empty result from agent | Skip in collection | Queue tests |
| SQ-006 | Duplicate results | Deduplicate by content ID | Queue tests |

---

## 7. Agent Response Edge Cases

### 7.1 Video Agent
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| VA-001 | YouTube API rate limit | Fall back to cached results | Agent tests |
| VA-002 | No videos found | Return empty, let judge decide | Agent tests |
| VA-003 | Video unavailable in region | Filter out, try alternatives | Agent tests |

### 7.2 Music Agent
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| MA-001 | Spotify API unavailable | Fall back to text description | Agent tests |
| MA-002 | No music matches location | Return ambient/general music | Agent tests |

### 7.3 Text Agent
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| TA-001 | Location not in Wikipedia | Generate from alternative sources | Agent tests |
| TA-002 | Content too long | Summarize to max_duration | Agent tests |

### 7.4 Judge Agent
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| JA-001 | All content scores equal | Use content type preference | Judge tests |
| JA-002 | No candidates received | Return empty decision | Judge tests |
| JA-003 | Single candidate only | Return that candidate | Judge tests |

---

## 8. Content Recommendation Edge Cases

### 8.1 Empty Results
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| CR-001 | No recommendations generated | Show helpful message | E2E tests |
| CR-002 | Single recommendation | Display without distribution chart | Results tests |

### 8.2 Quality Scores
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| CR-003 | Quality score = 0 | Display but mark as low quality | Recommendation tests |
| CR-004 | Quality score > 10 | Cap at 10.0 | Validation tests |

---

## 9. Dashboard Visualization Edge Cases

### 9.1 Chart Rendering
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| DV-001 | Empty DataFrame | Render empty chart gracefully | `test_dashboard_components.py::TestVisualizationEdgeCases::test_empty_dataframe_handling` |
| DV-002 | Single data point | Render with appropriate scale | `test_dashboard_components.py::TestVisualizationEdgeCases::test_single_row_dataframe` |
| DV-003 | NaN values in data | Handle gracefully, skip or interpolate | `test_dashboard_components.py::TestVisualizationEdgeCases::test_nan_values_in_data` |
| DV-004 | Extreme values (0.0001 to 9999) | Auto-scale axes | `test_dashboard_components.py::TestVisualizationEdgeCases::test_extreme_values_in_data` |

### 9.2 Architecture Diagram
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| DV-005 | Diagram with no data | Show static structure | `test_tour_guide_dashboard.py::TestArchitectureDiagram` |
| DV-006 | Rapid tab switching | No rendering artifacts | E2E tests |

### 9.3 Real-time Monitoring
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| DV-007 | No monitoring data | Show placeholder | Monitoring tests |
| DV-008 | 1000+ data points | Downsample for performance | Performance tests |

---

## 10. Performance Edge Cases

### 10.1 Large Data Sets
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| PE-001 | 50 route points | Process within 5 seconds | `test_performance.py` |
| PE-002 | 10,000 simulation samples | Complete in reasonable time | `test_dashboard_components.py::TestVisualizationPerformance::test_large_dataset_handling` |

### 10.2 Concurrent Operations
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| PE-003 | Multiple diagram creations | All independent | `test_tour_guide_dashboard_integration.py::TestConcurrentOperations` |
| PE-004 | Multiple app instances | No shared state | `test_tour_guide_dashboard_integration.py::TestConcurrentOperations::test_multiple_app_creations` |

### 10.3 Memory Management
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| PE-005 | Long session (100+ tours) | No memory leaks | Long-running tests |
| PE-006 | Large result sets | Paginate or virtualize | UI performance tests |

---

## 11. Accessibility Edge Cases

### 11.1 Screen Reader Support
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| AC-001 | Form without labels | All inputs have labels | `test_tour_guide_dashboard.py::TestAccessibility::test_inputs_have_labels` |
| AC-002 | Heading hierarchy broken | Proper H1 -> H2 -> H3 | `test_tour_guide_dashboard.py::TestAccessibility::test_header_has_semantic_elements` |

### 11.2 Keyboard Navigation
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| AC-003 | Tab navigation | Logical tab order | Accessibility tests |
| AC-004 | Button focus | Visible focus indicator | CSS tests |

---

## 12. Error Recovery Edge Cases

### 12.1 Network Errors
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| ER-001 | API timeout | Show error, allow retry | Error handling tests |
| ER-002 | Network disconnection | Graceful degradation | E2E tests |

### 12.2 State Recovery
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| ER-003 | Page refresh | Restore last state from stores | State tests |
| ER-004 | Browser back/forward | Maintain consistent state | E2E tests |

### 12.3 Input Validation
| ID | Edge Case | Expected Behavior | Test File |
|----|-----------|-------------------|-----------|
| ER-005 | Invalid JSON in store | Reset to default | Store tests |
| ER-006 | Callback exception | Show user-friendly error | Error handling tests |

---

## Test Coverage Summary

| Category | Edge Cases | Covered | Coverage |
|----------|------------|---------|----------|
| User Input | 9 | 8 | 89% |
| Profile Configuration | 8 | 7 | 88% |
| Driver Mode | 5 | 4 | 80% |
| Family Mode | 5 | 4 | 80% |
| Pipeline Processing | 5 | 4 | 80% |
| Smart Queue | 6 | 6 | 100% |
| Agent Response | 10 | 8 | 80% |
| Content Recommendation | 4 | 3 | 75% |
| Dashboard Visualization | 8 | 8 | 100% |
| Performance | 6 | 5 | 83% |
| Accessibility | 4 | 3 | 75% |
| Error Recovery | 6 | 4 | 67% |
| **TOTAL** | **76** | **64** | **84%** |

---

## Edge Case Test Commands

```bash
# Run all edge case tests
uv run pytest tests/ -v -k "edge" --tb=short

# Run dashboard edge case tests
uv run pytest tests/unit/test_tour_guide_dashboard.py -v --tb=short

# Run integration edge case tests
uv run pytest tests/integration/test_tour_guide_dashboard_integration.py -v --tb=short

# Run E2E edge case tests
uv run pytest tests/e2e/test_tour_guide_dashboard_e2e.py -v --tb=short

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=term-missing --cov-report=html

# Run specific edge case category
uv run pytest tests/ -v -k "driver_mode" --tb=short
uv run pytest tests/ -v -k "family_mode" --tb=short
uv run pytest tests/ -v -k "empty" --tb=short
```

---

## Adding New Edge Cases

When adding new edge cases:

1. **Document First**: Add entry to this document with ID, description, expected behavior
2. **Write Test**: Create test in appropriate test file following naming convention
3. **Update Coverage**: Update the coverage summary table
4. **Review**: Ensure test actually exercises the edge case

### Naming Convention

- Test files: `test_{component}_edge_cases.py` or within existing test class
- Test methods: `test_{edge_case_category}_{specific_case}`
- Example: `test_driver_mode_no_video_content`

---

## References

- [Testing Guide](./TESTING.md)
- [Operations Guide](./OPERATIONS_GUIDE.md)
- [Architecture Documentation](./ARCHITECTURE.md)
- [Smart Queue ADR](./adr/002-smart-queue-timeout-strategy.md)

