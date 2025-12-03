#!/bin/bash
# ============================================================================
# 📸 Screenshot Capture Guide for MIT Project Demo
# ============================================================================
# Run each command, then take a screenshot (Cmd+Shift+4 on Mac)
# Save screenshots to: assets/images/
# ============================================================================

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   📸 MIT PROJECT SCREENSHOT CAPTURE GUIDE                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

cd /Users/fouadaz/LearningFromUniversity/Learning/LLMSAndMultiAgentOrchestration/course-materials/assignments/Assignment4-multi-agent-tour-guide-parallel

# ============================================================================
# PHASE 1: INSTALLATION & SETUP (Already have: 04-make-check.png)
# ============================================================================
echo "═══════════════════════════════════════════════════════════════"
echo "📦 PHASE 1: Installation Screenshots"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "1️⃣  UV Version (Screenshot → 01-uv-installed.png):"
echo "    Command: uv --version"
echo ""
echo "2️⃣  Make Setup (Screenshot → 02-make-setup.png):"
echo "    Command: make setup"
echo ""
echo "3️⃣  Make Check (Screenshot → 04-make-check.png) ✅ Already have"
echo ""

# ============================================================================
# PHASE 2: TESTING (Already have: 05-test-results.png, 06-coverage-terminal.png)
# ============================================================================
echo "═══════════════════════════════════════════════════════════════"
echo "🧪 PHASE 2: Testing Screenshots"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "4️⃣  Test Results (Screenshot → 05-test-results.png) ✅ Already have"
echo "    Command: make test"
echo ""
echo "5️⃣  Coverage (Screenshot → 06-coverage-terminal.png) ✅ Already have"
echo "    Command: make test-cov"
echo ""

# ============================================================================
# PHASE 3: CORE FLOWS (Already have: 07-queue-mode.png, 08-family-mode.png)
# ============================================================================
echo "═══════════════════════════════════════════════════════════════"
echo "🎮 PHASE 3: Core Flow Screenshots"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "6️⃣  Queue Mode (Screenshot → 07-queue-mode.png) ✅ Already have"
echo "    Command: make run-queue"
echo ""
echo "7️⃣  Family Mode (Screenshot → 08-family-mode.png) ✅ Already have"
echo "    Command: make run-family"
echo ""
echo "8️⃣  History Mode (Screenshot → 11-history-mode.png):"
echo "    Command: make run-history"
echo ""
echo "9️⃣  Verbose Mode (Screenshot → 12-verbose-mode.png):"
echo "    Command: make run-verbose"
echo ""
echo "🔟 Streaming Mode (Screenshot → 13-streaming-mode.png):"
echo "    Command: make run-streaming"
echo ""

# ============================================================================
# PHASE 4: API SERVER
# ============================================================================
echo "═══════════════════════════════════════════════════════════════"
echo "🌐 PHASE 4: API Screenshots"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "1️⃣1️⃣ Start API Server (Screenshot → 15-api-server.png):"
echo "    Command: make run-api"
echo "    (In a new terminal)"
echo ""
echo "1️⃣2️⃣ API Health (Screenshot → 16-api-health.png):"
echo "    Command: curl http://localhost:8000/health | jq"
echo ""
echo "1️⃣3️⃣ Swagger Docs (Screenshot → 17-swagger-docs.png):"
echo "    Open: http://localhost:8000/docs"
echo ""

# ============================================================================
# PHASE 5: DASHBOARD
# ============================================================================
echo "═══════════════════════════════════════════════════════════════"
echo "📊 PHASE 5: Dashboard Screenshots"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "1️⃣4️⃣ Start Dashboard:"
echo "    Command: uv run python run_dashboard.py"
echo ""
echo "1️⃣5️⃣ Dashboard Overview (Screenshot → 20-dashboard-overview.png):"
echo "    Open: http://localhost:8050"
echo ""
echo "1️⃣6️⃣ System Monitor Tab (Screenshot → 21-dashboard-system.png)"
echo "1️⃣7️⃣ Sensitivity Tab (Screenshot → 22-dashboard-sensitivity.png)"
echo "1️⃣8️⃣ Pareto Tab (Screenshot → 23-dashboard-pareto.png)"
echo "1️⃣9️⃣ A/B Testing Tab (Screenshot → 24-dashboard-ab.png)"
echo "2️⃣0️⃣ Monte Carlo Tab (Screenshot → 25-dashboard-monte-carlo.png)"
echo ""

# ============================================================================
# PHASE 6: RESEARCH OUTPUTS
# ============================================================================
echo "═══════════════════════════════════════════════════════════════"
echo "🔬 PHASE 6: Research Screenshots"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "2️⃣1️⃣ Sensitivity Analysis:"
echo "    Command: uv run jupyter notebook notebooks/01_sensitivity_analysis.ipynb"
echo "    Screenshot → 26-notebook-sensitivity.png"
echo ""
echo "2️⃣2️⃣ Cost Analysis:"
echo "    Command: uv run jupyter notebook notebooks/03_cost_analysis.ipynb"
echo "    Screenshot → 31-cost-analysis.png"
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "✅ ESSENTIAL SCREENSHOTS (Minimum for MIT Demo):"
echo "═══════════════════════════════════════════════════════════════"
echo "  1. 07-queue-mode.png        ⭐⭐⭐ (Main Feature)"
echo "  2. 05-test-results.png      ⭐⭐⭐ (683+ Tests)"
echo "  3. 20-dashboard-overview.png ⭐⭐⭐ (Research Dashboard)"
echo "  4. 17-swagger-docs.png      ⭐⭐ (API Documentation)"
echo "  5. 06-coverage-terminal.png  ⭐⭐ (85%+ Coverage)"
echo "  6. architecture-Overview.png ⭐⭐ (System Design)"
echo ""
echo "You already have: 04, 05, 06, 07, 08, architecture, sequence"
echo "═══════════════════════════════════════════════════════════════"

