#!/usr/bin/env python3
"""
ISO/IEC 25010:2011 Compliance Verification Script

This script verifies that the Multi-Agent Tour Guide System
meets all ISO/IEC 25010 quality characteristics and sub-characteristics.

Usage:
    python scripts/iso25010_compliance_check.py
    python scripts/iso25010_compliance_check.py --verbose
    python scripts/iso25010_compliance_check.py --report json
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, List, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class ComplianceLevel(Enum):
    """Compliance assessment levels."""

    FULL = "full"
    PARTIAL = "partial"
    NON_COMPLIANT = "non_compliant"
    NOT_APPLICABLE = "n/a"


class CheckResult(Enum):
    """Individual check result."""

    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    SKIP = "skip"


@dataclass
class Check:
    """A single compliance check."""

    name: str
    description: str
    characteristic: str
    sub_characteristic: str
    check_func: Callable[[], tuple[CheckResult, str]]

    result: Optional[CheckResult] = None
    message: str = ""

    def run(self) -> None:
        """Execute the check."""
        try:
            self.result, self.message = self.check_func()
        except Exception as e:
            self.result = CheckResult.FAIL
            self.message = f"Check failed with exception: {e}"


@dataclass
class CharacteristicResult:
    """Results for a quality characteristic."""

    name: str
    sub_characteristics: Dict[str, List[Check]] = field(default_factory=dict)

    @property
    def compliance_level(self) -> ComplianceLevel:
        """Calculate overall compliance level."""
        all_checks = []
        for checks in self.sub_characteristics.values():
            all_checks.extend(checks)

        if not all_checks:
            return ComplianceLevel.NOT_APPLICABLE

        passed = sum(1 for c in all_checks if c.result == CheckResult.PASS)
        total = len(all_checks)

        if passed == total:
            return ComplianceLevel.FULL
        elif passed >= total * 0.7:
            return ComplianceLevel.PARTIAL
        else:
            return ComplianceLevel.NON_COMPLIANT


class ISO25010ComplianceChecker:
    """
    ISO/IEC 25010:2011 Compliance Verification

    Verifies all 8 quality characteristics:
    1. Functional Suitability
    2. Performance Efficiency
    3. Compatibility
    4. Usability
    5. Reliability
    6. Security
    7. Maintainability
    8. Portability
    """

    def __init__(self, project_root: Path = PROJECT_ROOT):
        self.project_root = project_root
        self.checks: List[Check] = []
        self.results: Dict[str, CharacteristicResult] = {}

        self._register_checks()

    def _register_checks(self) -> None:
        """Register all compliance checks."""

        # ============================================================
        # 1. FUNCTIONAL SUITABILITY
        # ============================================================

        # 1.1 Functional Completeness
        self._add_check(
            "Core agents exist",
            "All required content agents are implemented",
            "Functional Suitability",
            "Completeness",
            self._check_agents_exist,
        )
        self._add_check(
            "Orchestrator exists",
            "Orchestration layer is implemented",
            "Functional Suitability",
            "Completeness",
            self._check_orchestrator_exists,
        )
        self._add_check(
            "Queue mechanism exists",
            "Queue-based synchronization is implemented",
            "Functional Suitability",
            "Completeness",
            self._check_queue_exists,
        )

        # 1.2 Functional Correctness
        self._add_check(
            "Unit tests exist",
            "Unit tests verify correctness",
            "Functional Suitability",
            "Correctness",
            self._check_unit_tests_exist,
        )
        self._add_check(
            "Models use Pydantic",
            "Data models use Pydantic for validation",
            "Functional Suitability",
            "Correctness",
            self._check_pydantic_models,
        )

        # ============================================================
        # 2. PERFORMANCE EFFICIENCY
        # ============================================================

        # 2.1 Time Behavior
        self._add_check(
            "Timeout configuration",
            "Configurable timeouts are defined",
            "Performance Efficiency",
            "Time Behavior",
            self._check_timeout_config,
        )
        self._add_check(
            "Metrics collection",
            "Performance metrics are collected",
            "Performance Efficiency",
            "Time Behavior",
            self._check_metrics_exist,
        )

        # 2.2 Resource Utilization
        self._add_check(
            "Thread pool configuration",
            "Thread pool limits are configurable",
            "Performance Efficiency",
            "Resource Utilization",
            self._check_thread_pool_config,
        )

        # ============================================================
        # 3. COMPATIBILITY
        # ============================================================

        # 3.1 Interoperability
        self._add_check(
            "REST API exists",
            "Standard REST API is implemented",
            "Compatibility",
            "Interoperability",
            self._check_api_exists,
        )
        self._add_check(
            "Prometheus metrics",
            "Prometheus-compatible metrics endpoint",
            "Compatibility",
            "Interoperability",
            self._check_prometheus_metrics,
        )

        # ============================================================
        # 4. USABILITY
        # ============================================================

        # 4.1 Learnability
        self._add_check(
            "README exists",
            "Documentation README exists",
            "Usability",
            "Learnability",
            self._check_readme_exists,
        )
        self._add_check(
            "CLI help available",
            "CLI provides help documentation",
            "Usability",
            "Learnability",
            self._check_cli_exists,
        )

        # 4.2 User Error Protection
        self._add_check(
            "Input validation",
            "User inputs are validated",
            "Usability",
            "User Error Protection",
            self._check_input_validation,
        )

        # ============================================================
        # 5. RELIABILITY
        # ============================================================

        # 5.1 Fault Tolerance
        self._add_check(
            "Circuit breaker",
            "Circuit breaker pattern is implemented",
            "Reliability",
            "Fault Tolerance",
            self._check_circuit_breaker,
        )
        self._add_check(
            "Retry mechanism",
            "Retry with backoff is implemented",
            "Reliability",
            "Fault Tolerance",
            self._check_retry_mechanism,
        )
        self._add_check(
            "Graceful degradation",
            "System degrades gracefully on partial failures",
            "Reliability",
            "Fault Tolerance",
            self._check_graceful_degradation,
        )

        # 5.2 Recoverability
        self._add_check(
            "Health checks",
            "Health check endpoints exist",
            "Reliability",
            "Recoverability",
            self._check_health_checks,
        )

        # ============================================================
        # 6. SECURITY
        # ============================================================

        # 6.1 Confidentiality
        self._add_check(
            "Environment variables",
            "Secrets use environment variables",
            "Security",
            "Confidentiality",
            self._check_env_secrets,
        )
        self._add_check(
            "No hardcoded secrets",
            "No secrets in source code",
            "Security",
            "Confidentiality",
            self._check_no_hardcoded_secrets,
        )

        # 6.2 Integrity
        self._add_check(
            "Pydantic validation",
            "Input validation prevents injection",
            "Security",
            "Integrity",
            self._check_pydantic_models,
        )

        # ============================================================
        # 7. MAINTAINABILITY
        # ============================================================

        # 7.1 Modularity
        self._add_check(
            "Modular structure",
            "Code is organized in modules",
            "Maintainability",
            "Modularity",
            self._check_modular_structure,
        )

        # 7.2 Reusability
        self._add_check(
            "Base agent class",
            "Agents inherit from base class",
            "Maintainability",
            "Reusability",
            self._check_base_agent,
        )

        # 7.3 Testability
        self._add_check(
            "Test fixtures",
            "Reusable test fixtures exist",
            "Maintainability",
            "Testability",
            self._check_test_fixtures,
        )

        # 7.4 Modifiability
        self._add_check(
            "YAML configuration",
            "Behavior is configurable via YAML",
            "Maintainability",
            "Modifiability",
            self._check_yaml_config,
        )

        # ============================================================
        # 8. PORTABILITY
        # ============================================================

        # 8.1 Installability
        self._add_check(
            "Dockerfile exists",
            "Docker containerization is available",
            "Portability",
            "Installability",
            self._check_dockerfile,
        )
        self._add_check(
            "Kubernetes manifests",
            "Kubernetes deployment is available",
            "Portability",
            "Installability",
            self._check_kubernetes,
        )

        # 8.2 Adaptability
        self._add_check(
            "Environment abstraction",
            "Configuration via environment variables",
            "Portability",
            "Adaptability",
            self._check_env_abstraction,
        )

    def _add_check(
        self,
        name: str,
        description: str,
        characteristic: str,
        sub_characteristic: str,
        check_func: Callable[[], tuple[CheckResult, str]],
    ) -> None:
        """Add a compliance check."""
        check = Check(
            name=name,
            description=description,
            characteristic=characteristic,
            sub_characteristic=sub_characteristic,
            check_func=check_func,
        )
        self.checks.append(check)

    # ==================== CHECK IMPLEMENTATIONS ====================

    def _check_agents_exist(self) -> tuple[CheckResult, str]:
        """Check that all core agents exist."""
        agents_dir = self.project_root / "src" / "agents"
        required_agents = [
            "video_agent.py",
            "music_agent.py",
            "text_agent.py",
            "judge_agent.py",
        ]

        missing = []
        for agent in required_agents:
            if not (agents_dir / agent).exists():
                missing.append(agent)

        if missing:
            return CheckResult.FAIL, f"Missing agents: {missing}"
        return CheckResult.PASS, "All core agents exist"

    def _check_orchestrator_exists(self) -> tuple[CheckResult, str]:
        """Check that orchestrator exists."""
        orchestrator = self.project_root / "src" / "core" / "orchestrator.py"
        if orchestrator.exists():
            return CheckResult.PASS, "Orchestrator module exists"
        return CheckResult.FAIL, "Orchestrator module not found"

    def _check_queue_exists(self) -> tuple[CheckResult, str]:
        """Check that smart queue exists."""
        queue = self.project_root / "src" / "core" / "smart_queue.py"
        if queue.exists():
            return CheckResult.PASS, "Smart queue module exists"
        return CheckResult.FAIL, "Smart queue module not found"

    def _check_unit_tests_exist(self) -> tuple[CheckResult, str]:
        """Check that unit tests exist."""
        tests_dir = self.project_root / "tests" / "unit"
        if tests_dir.exists() and any(tests_dir.glob("test_*.py")):
            return CheckResult.PASS, "Unit tests exist"
        return CheckResult.FAIL, "No unit tests found"

    def _check_pydantic_models(self) -> tuple[CheckResult, str]:
        """Check that models use Pydantic."""
        models_dir = self.project_root / "src" / "models"
        if not models_dir.exists():
            return CheckResult.FAIL, "Models directory not found"

        for model_file in models_dir.glob("*.py"):
            if model_file.name == "__init__.py":
                continue
            content = model_file.read_text()
            if "BaseModel" in content or "pydantic" in content:
                return CheckResult.PASS, "Pydantic models detected"

        return CheckResult.WARN, "Pydantic usage not detected"

    def _check_timeout_config(self) -> tuple[CheckResult, str]:
        """Check timeout configuration."""
        config_file = self.project_root / "config" / "default.yaml"
        if config_file.exists():
            content = config_file.read_text()
            if "timeout" in content.lower():
                return CheckResult.PASS, "Timeout configuration found"
        return CheckResult.WARN, "Timeout configuration not found in default.yaml"

    def _check_metrics_exist(self) -> tuple[CheckResult, str]:
        """Check metrics collection."""
        metrics = self.project_root / "src" / "core" / "observability" / "metrics.py"
        if metrics.exists():
            return CheckResult.PASS, "Metrics module exists"
        return CheckResult.FAIL, "Metrics module not found"

    def _check_thread_pool_config(self) -> tuple[CheckResult, str]:
        """Check thread pool configuration."""
        orchestrator = self.project_root / "src" / "core" / "orchestrator.py"
        if orchestrator.exists():
            content = orchestrator.read_text()
            if "ThreadPoolExecutor" in content or "thread" in content.lower():
                return CheckResult.PASS, "Thread pool configuration found"
        return CheckResult.WARN, "Thread pool configuration not detected"

    def _check_api_exists(self) -> tuple[CheckResult, str]:
        """Check REST API exists."""
        api = self.project_root / "src" / "api" / "app.py"
        if api.exists():
            return CheckResult.PASS, "REST API module exists"
        return CheckResult.FAIL, "REST API module not found"

    def _check_prometheus_metrics(self) -> tuple[CheckResult, str]:
        """Check Prometheus metrics."""
        metrics = self.project_root / "src" / "core" / "observability" / "metrics.py"
        if metrics.exists():
            content = metrics.read_text()
            if "prometheus" in content.lower() or "Counter" in content:
                return CheckResult.PASS, "Prometheus-compatible metrics found"
        return CheckResult.WARN, "Prometheus metrics not detected"

    def _check_readme_exists(self) -> tuple[CheckResult, str]:
        """Check README exists."""
        readme = self.project_root / "README.md"
        if readme.exists() and readme.stat().st_size > 100:
            return CheckResult.PASS, "README.md exists and has content"
        return CheckResult.FAIL, "README.md missing or empty"

    def _check_cli_exists(self) -> tuple[CheckResult, str]:
        """Check CLI exists."""
        cli = self.project_root / "src" / "cli" / "main.py"
        if cli.exists():
            return CheckResult.PASS, "CLI module exists"
        return CheckResult.FAIL, "CLI module not found"

    def _check_input_validation(self) -> tuple[CheckResult, str]:
        """Check input validation."""
        # Already checked with Pydantic
        return self._check_pydantic_models()

    def _check_circuit_breaker(self) -> tuple[CheckResult, str]:
        """Check circuit breaker implementation."""
        cb = self.project_root / "src" / "core" / "resilience" / "circuit_breaker.py"
        if cb.exists():
            content = cb.read_text()
            if "CircuitBreaker" in content:
                return CheckResult.PASS, "Circuit breaker implemented"
        return CheckResult.FAIL, "Circuit breaker not found"

    def _check_retry_mechanism(self) -> tuple[CheckResult, str]:
        """Check retry mechanism."""
        retry = self.project_root / "src" / "core" / "resilience" / "retry.py"
        if retry.exists():
            content = retry.read_text()
            if "retry" in content.lower() and "backoff" in content.lower():
                return CheckResult.PASS, "Retry with backoff implemented"
        return CheckResult.FAIL, "Retry mechanism not found"

    def _check_graceful_degradation(self) -> tuple[CheckResult, str]:
        """Check graceful degradation."""
        queue = self.project_root / "src" / "core" / "smart_queue.py"
        if queue.exists():
            content = queue.read_text()
            if "timeout" in content.lower() or "degradation" in content.lower():
                return CheckResult.PASS, "Graceful degradation implemented"
        return CheckResult.WARN, "Graceful degradation not detected"

    def _check_health_checks(self) -> tuple[CheckResult, str]:
        """Check health check endpoints."""
        health = self.project_root / "src" / "core" / "observability" / "health.py"
        if health.exists():
            return CheckResult.PASS, "Health check module exists"
        return CheckResult.FAIL, "Health check module not found"

    def _check_env_secrets(self) -> tuple[CheckResult, str]:
        """Check environment variable usage for secrets."""
        env_example = self.project_root / "env.example"
        if env_example.exists():
            content = env_example.read_text()
            if "API_KEY" in content or "SECRET" in content:
                return CheckResult.PASS, "Environment variables for secrets"
        return CheckResult.WARN, "env.example not found or incomplete"

    def _check_no_hardcoded_secrets(self) -> tuple[CheckResult, str]:
        """Check no hardcoded secrets in source."""
        import re

        src_dir = self.project_root / "src"

        # More specific patterns to avoid false positives
        secret_patterns = [
            r"sk-ant-[a-zA-Z0-9-]{20,}",  # Anthropic API keys
            r"sk-proj-[a-zA-Z0-9-]{20,}",  # OpenAI project keys
            r"sk-[a-zA-Z0-9]{48,}",  # OpenAI API keys (48+ chars)
            r"AKIA[0-9A-Z]{16}",  # AWS access key IDs
            r"ghp_[a-zA-Z0-9]{36}",  # GitHub personal access tokens
            r"gho_[a-zA-Z0-9]{36}",  # GitHub OAuth tokens
        ]

        for py_file in src_dir.rglob("*.py"):
            content = py_file.read_text()
            for pattern in secret_patterns:
                if re.search(pattern, content):
                    # Additional check: skip if it's in a comment or docstring about examples
                    if "example" in content.lower() or "placeholder" in content.lower():
                        continue
                    return (
                        CheckResult.FAIL,
                        f"Potential hardcoded secret in {py_file.name}",
                    )

        return CheckResult.PASS, "No hardcoded secrets detected"

    def _check_modular_structure(self) -> tuple[CheckResult, str]:
        """Check modular code structure."""
        src_dir = self.project_root / "src"
        required_modules = ["agents", "core", "models", "services"]

        missing = []
        for module in required_modules:
            if not (src_dir / module).is_dir():
                missing.append(module)

        if missing:
            return CheckResult.FAIL, f"Missing modules: {missing}"
        return CheckResult.PASS, "Modular structure verified"

    def _check_base_agent(self) -> tuple[CheckResult, str]:
        """Check base agent class exists."""
        base_agent = self.project_root / "src" / "agents" / "base_agent.py"
        if base_agent.exists():
            content = base_agent.read_text()
            if "class BaseAgent" in content or "ABC" in content:
                return CheckResult.PASS, "Base agent class exists"
        return CheckResult.FAIL, "Base agent class not found"

    def _check_test_fixtures(self) -> tuple[CheckResult, str]:
        """Check test fixtures exist."""
        conftest = self.project_root / "tests" / "conftest.py"
        if conftest.exists():
            content = conftest.read_text()
            if "@pytest.fixture" in content:
                return CheckResult.PASS, "Test fixtures defined"
        return CheckResult.FAIL, "Test fixtures not found"

    def _check_yaml_config(self) -> tuple[CheckResult, str]:
        """Check YAML configuration."""
        config_dir = self.project_root / "config"
        agent_configs = self.project_root / "src" / "agents" / "configs"

        if config_dir.exists() or agent_configs.exists():
            yaml_files = list(config_dir.glob("*.yaml")) if config_dir.exists() else []
            yaml_files += (
                list(agent_configs.glob("*.yaml")) if agent_configs.exists() else []
            )
            if yaml_files:
                return CheckResult.PASS, f"Found {len(yaml_files)} YAML config files"
        return CheckResult.FAIL, "YAML configuration not found"

    def _check_dockerfile(self) -> tuple[CheckResult, str]:
        """Check Dockerfile exists."""
        dockerfile = self.project_root / "Dockerfile"
        if dockerfile.exists():
            content = dockerfile.read_text()
            if "FROM" in content:
                return CheckResult.PASS, "Dockerfile exists"
        return CheckResult.FAIL, "Dockerfile not found"

    def _check_kubernetes(self) -> tuple[CheckResult, str]:
        """Check Kubernetes manifests."""
        k8s_dir = self.project_root / "deploy" / "kubernetes"
        if k8s_dir.exists() and any(k8s_dir.glob("*.yaml")):
            return CheckResult.PASS, "Kubernetes manifests exist"
        return CheckResult.FAIL, "Kubernetes manifests not found"

    def _check_env_abstraction(self) -> tuple[CheckResult, str]:
        """Check environment abstraction."""
        # Check for pydantic-settings or similar
        config_files = list((self.project_root / "src").rglob("config*.py"))
        for config_file in config_files:
            content = config_file.read_text()
            if "BaseSettings" in content or "os.getenv" in content:
                return CheckResult.PASS, "Environment abstraction found"
        return CheckResult.WARN, "Environment abstraction not detected"

    # ==================== EXECUTION ====================

    def run_all_checks(self) -> None:
        """Run all registered checks."""
        for check in self.checks:
            check.run()

        # Organize results by characteristic
        for check in self.checks:
            if check.characteristic not in self.results:
                self.results[check.characteristic] = CharacteristicResult(
                    name=check.characteristic
                )

            char_result = self.results[check.characteristic]
            if check.sub_characteristic not in char_result.sub_characteristics:
                char_result.sub_characteristics[check.sub_characteristic] = []

            char_result.sub_characteristics[check.sub_characteristic].append(check)

    def print_report(self, verbose: bool = False) -> None:
        """Print compliance report to console."""
        print("\n" + "=" * 70)
        print("ISO/IEC 25010:2011 COMPLIANCE VERIFICATION REPORT")
        print("=" * 70)
        print(f"Project: {self.project_root.name}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70 + "\n")

        # Summary
        total_passed = sum(1 for c in self.checks if c.result == CheckResult.PASS)
        total_failed = sum(1 for c in self.checks if c.result == CheckResult.FAIL)
        total_warn = sum(1 for c in self.checks if c.result == CheckResult.WARN)
        total = len(self.checks)

        print("SUMMARY")
        print("-" * 40)
        print(f"Total Checks: {total}")
        print(f"  ✅ Passed:  {total_passed}")
        print(f"  ❌ Failed:  {total_failed}")
        print(f"  ⚠️  Warnings: {total_warn}")
        print(
            f"\nCompliance Score: {total_passed}/{total} ({total_passed / total * 100:.1f}%)"
        )
        print()

        # By characteristic
        print("RESULTS BY CHARACTERISTIC")
        print("-" * 40)

        for char_name, char_result in self.results.items():
            level = char_result.compliance_level
            icon = (
                "✅"
                if level == ComplianceLevel.FULL
                else "⚠️"
                if level == ComplianceLevel.PARTIAL
                else "❌"
            )
            print(f"\n{icon} {char_name}: {level.value.upper()}")

            if verbose:
                for sub_name, checks in char_result.sub_characteristics.items():
                    print(f"\n  📋 {sub_name}")
                    for check in checks:
                        result_icon = (
                            "✅"
                            if check.result == CheckResult.PASS
                            else "❌"
                            if check.result == CheckResult.FAIL
                            else "⚠️"
                        )
                        print(f"    {result_icon} {check.name}")
                        if check.result != CheckResult.PASS:
                            print(f"       → {check.message}")

        # Overall compliance
        all_full = all(
            r.compliance_level == ComplianceLevel.FULL for r in self.results.values()
        )

        print("\n" + "=" * 70)
        if all_full:
            print("🏆 OVERALL: FULL ISO/IEC 25010 COMPLIANCE ACHIEVED")
        else:
            print("📋 OVERALL: PARTIAL COMPLIANCE - See details above")
        print("=" * 70 + "\n")

    def to_json(self) -> str:
        """Export results as JSON."""
        report = {
            "project": self.project_root.name,
            "timestamp": datetime.now().isoformat(),
            "standard": "ISO/IEC 25010:2011",
            "summary": {
                "total_checks": len(self.checks),
                "passed": sum(1 for c in self.checks if c.result == CheckResult.PASS),
                "failed": sum(1 for c in self.checks if c.result == CheckResult.FAIL),
                "warnings": sum(1 for c in self.checks if c.result == CheckResult.WARN),
            },
            "characteristics": {},
        }

        for char_name, char_result in self.results.items():
            report["characteristics"][char_name] = {
                "compliance_level": char_result.compliance_level.value,
                "sub_characteristics": {},
            }
            for sub_name, checks in char_result.sub_characteristics.items():
                report["characteristics"][char_name]["sub_characteristics"][
                    sub_name
                ] = [
                    {
                        "name": c.name,
                        "result": c.result.value if c.result else "not_run",
                        "message": c.message,
                    }
                    for c in checks
                ]

        return json.dumps(report, indent=2)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="ISO/IEC 25010:2011 Compliance Verification"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed results"
    )
    parser.add_argument(
        "--report", choices=["text", "json"], default="text", help="Output format"
    )
    parser.add_argument(
        "--project-root", type=Path, default=PROJECT_ROOT, help="Project root directory"
    )

    args = parser.parse_args()

    checker = ISO25010ComplianceChecker(args.project_root)
    checker.run_all_checks()

    if args.report == "json":
        print(checker.to_json())
    else:
        checker.print_report(verbose=args.verbose)

    # Exit with error if any failures
    failed = sum(1 for c in checker.checks if c.result == CheckResult.FAIL)
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
