# 🆘 Getting Help & Support

## Multi-Agent Tour Guide System

Welcome! We're here to help you succeed with the Multi-Agent Tour Guide System.

---

## 🗺️ Where to Get Help

Choose the right channel based on your needs:

| Need | Channel | Response Time |
|------|---------|---------------|
| 🐛 Bug Reports | [GitHub Issues](https://github.com/yourusername/multi-agent-tour-guide/issues) | 1-3 days |
| 💡 Feature Requests | [GitHub Discussions](https://github.com/yourusername/multi-agent-tour-guide/discussions) | 1-5 days |
| ❓ Questions | [GitHub Discussions](https://github.com/yourusername/multi-agent-tour-guide/discussions) | 1-3 days |
| 🔒 Security Issues | [SECURITY.md](SECURITY.md) | 48 hours |
| 🎓 Academic Queries | research@example.com | 1 week |

---

## 🔍 Before Asking for Help

### 1. Check the Documentation

We have comprehensive documentation that covers most topics:

| Topic | Document |
|-------|----------|
| **Getting Started** | [README.md](README.md) |
| **Installation Issues** | [QUICKFIX.md](docs/QUICKFIX.md) |
| **Architecture Questions** | [ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| **API Usage** | [API_REFERENCE.md](docs/API_REFERENCE.md) |
| **Testing** | [TESTING.md](docs/TESTING.md) |
| **Research** | [Research Framework](docs/research/README.md) |

### 2. Search Existing Issues

Your question might already be answered:

- 🔍 [Search Open Issues](https://github.com/yourusername/multi-agent-tour-guide/issues)
- 🔍 [Search Closed Issues](https://github.com/yourusername/multi-agent-tour-guide/issues?q=is%3Aissue+is%3Aclosed)
- 🔍 [Search Discussions](https://github.com/yourusername/multi-agent-tour-guide/discussions)

### 3. Check the Changelog

For version-specific issues:
- 📋 [CHANGELOG.md](CHANGELOG.md)

---

## 📝 How to Report a Bug

When reporting a bug, please include:

```markdown
### Environment
- OS: [e.g., macOS 14.0, Ubuntu 22.04]
- Python Version: [e.g., 3.11.5]
- Project Version: [e.g., 2.0.0]

### Description
A clear description of the bug.

### Steps to Reproduce
1. Go to '...'
2. Run '...'
3. See error

### Expected Behavior
What should have happened.

### Actual Behavior
What actually happened.

### Logs/Screenshots
If applicable, add logs or screenshots.

### Additional Context
Any other relevant information.
```

---

## 💡 How to Request a Feature

For feature requests, please provide:

```markdown
### Problem Statement
What problem does this feature solve?

### Proposed Solution
How would you like to solve it?

### Alternatives Considered
What alternatives have you considered?

### Use Cases
Who would benefit and how?

### Priority
How important is this to your workflow?
```

---

## 🚀 Quick Self-Help Guide

### Common Issues & Solutions

<details>
<summary><b>🔴 Installation Failed</b></summary>

```bash
# Clean reinstall
make clean-all
make setup

# Or manually
rm -rf .venv
uv venv
uv sync --extra dev
```

</details>

<details>
<summary><b>🔴 API Key Not Working</b></summary>

```bash
# Check environment
echo $ANTHROPIC_API_KEY

# Ensure .env is loaded
cat .env

# Recreate .env
cp env.example .env
# Edit with your keys
```

</details>

<details>
<summary><b>🔴 Tests Failing</b></summary>

```bash
# Run with verbose output
uv run pytest tests/ -v

# Check specific test
uv run pytest tests/unit/test_queue.py -v

# Generate coverage report
make test-cov
open htmlcov/index.html
```

</details>

<details>
<summary><b>🔴 Import Errors</b></summary>

```bash
# Ensure virtual environment is active
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows

# Reinstall dependencies
uv sync --extra dev
```

</details>

<details>
<summary><b>🔴 Queue Always Timing Out</b></summary>

```yaml
# In config/default.yaml, increase timeouts:
queue:
  soft_timeout_seconds: 25.0  # Default: 15
  hard_timeout_seconds: 45.0  # Default: 30
```

</details>

---

## 🎓 Academic & Research Support

### For Research Questions

If you're using this project for academic research:

1. **Read the research documentation:**
   - [Research Framework](docs/research/README.md)
   - [Mathematical Analysis](docs/research/MATHEMATICAL_ANALYSIS.md)
   - [Sensitivity Analysis Notebook](notebooks/01_sensitivity_analysis.ipynb)

2. **For collaboration inquiries:**
   - 📧 research@example.com
   - Include your institution and research area

### Citing This Project

If you use this project in your research, please cite:

```bibtex
@software{multi_agent_tour_guide_2025,
  title = {Multi-Agent Tour Guide System},
  author = {LLMs and Multi-Agent Orchestration Course},
  year = {2025},
  version = {2.0.0},
  url = {https://github.com/yourusername/multi-agent-tour-guide}
}
```

See [CITATION.cff](CITATION.cff) for the full citation format.

---

## 🤝 Community Channels

### GitHub Discussions

Our primary community platform:

| Category | Purpose |
|----------|---------|
| **📣 Announcements** | Official project updates |
| **💬 General** | General questions and chat |
| **💡 Ideas** | Feature suggestions |
| **🙏 Q&A** | Technical questions |
| **🎉 Show and Tell** | Share your projects using this system |

### Stay Updated

- ⭐ **Star** the repository for updates
- 👁️ **Watch** for release notifications
- 🐦 Follow project updates (TBD)

---

## ⏱️ Response Time Expectations

| Priority | Response Time | Examples |
|----------|---------------|----------|
| 🔴 Critical | 24-48 hours | Security issues, data loss |
| 🟠 High | 3-5 days | Major bugs, broken features |
| 🟡 Medium | 1-2 weeks | Minor bugs, improvements |
| 🟢 Low | Best effort | Nice-to-haves, cosmetic issues |

---

## 🙏 Thank You

Thank you for using and contributing to the Multi-Agent Tour Guide System!

Your feedback helps us improve. Don't hesitate to reach out.

---

<p align="center">
  <a href="README.md">📚 Docs</a> •
  <a href="https://github.com/yourusername/multi-agent-tour-guide/issues">🐛 Issues</a> •
  <a href="https://github.com/yourusername/multi-agent-tour-guide/discussions">💬 Discussions</a>
</p>

