# 📦 Reusable Documentation Templates

## Open Source Contribution to the Community

This document catalogs all **reusable, MIT-licensed templates** from the Multi-Agent Tour Guide System that you can freely use in your own projects.

**License**: MIT - Free to use, modify, and distribute. Attribution appreciated but not required.

---

## 🗺️ Template Catalog

### 📁 Root-Level Community Files

Templates for establishing open-source community standards:

| Template | File | Use Case | How to Reuse |
|----------|------|----------|--------------|
| **Code of Conduct** | [`CODE_OF_CONDUCT.md`](../CODE_OF_CONDUCT.md) | Community standards | Copy and customize organization name |
| **Contributing Guide** | [`CONTRIBUTING.md`](../CONTRIBUTING.md) | Contributor guidelines | Adapt sections to your project |
| **Support Guide** | [`SUPPORT.md`](../SUPPORT.md) | Help channels | Update links and contact info |
| **Governance** | [`GOVERNANCE.md`](../GOVERNANCE.md) | Decision-making | Customize roles and processes |
| **Authors** | [`AUTHORS.md`](../AUTHORS.md) | Contributor recognition | Add your team members |
| **Security Policy** | [`SECURITY.md`](../SECURITY.md) | Vulnerability reporting | Update contact email |
| **Citation** | [`CITATION.cff`](../CITATION.cff) | Academic citation | Fill in your project details |
| **Changelog** | [`CHANGELOG.md`](../CHANGELOG.md) | Version history | Follow Keep a Changelog format |

---

### 📁 GitHub Templates (`.github/`)

Ready-to-use GitHub automation templates:

| Template | File | Use Case |
|----------|------|----------|
| **Bug Report Form** | [`.github/ISSUE_TEMPLATE/bug_report.yml`](../.github/ISSUE_TEMPLATE/bug_report.yml) | Structured bug reports |
| **Feature Request Form** | [`.github/ISSUE_TEMPLATE/feature_request.yml`](../.github/ISSUE_TEMPLATE/feature_request.yml) | Feature suggestions |
| **Issue Config** | [`.github/ISSUE_TEMPLATE/config.yml`](../.github/ISSUE_TEMPLATE/config.yml) | Issue template settings |
| **PR Template** | [`.github/PULL_REQUEST_TEMPLATE.md`](../.github/PULL_REQUEST_TEMPLATE.md) | Pull request checklist |
| **Code Owners** | [`.github/CODEOWNERS`](../.github/CODEOWNERS) | Review assignments |
| **Dependabot** | [`.github/dependabot.yml`](../.github/dependabot.yml) | Dependency updates |
| **Funding** | [`.github/FUNDING.yml`](../.github/FUNDING.yml) | Sponsorship links |

---

### 📁 Technical Documentation Templates

MIT-level documentation templates for technical projects:

| Template | File | Use Case | Key Features |
|----------|------|----------|--------------|
| **ADR Template** | [`docs/adr/template.md`](adr/template.md) | Architecture Decision Records | Status, context, decision, consequences |
| **Prompt Book** | [`docs/PROMPT_BOOK.md`](PROMPT_BOOK.md) | AI-assisted development | Copy-paste prompts for LLM coding |
| **Quick Fix Guide** | [`docs/QUICKFIX.md`](QUICKFIX.md) | Troubleshooting | Problem→Solution format |
| **Testing Guide** | [`docs/TESTING.md`](TESTING.md) | Test documentation | Test catalog with expected results |
| **API Reference** | [`docs/API_REFERENCE.md`](API_REFERENCE.md) | API documentation | Endpoints, parameters, responses |

---

### 📁 Quality & Compliance Templates

Templates for enterprise-grade quality standards:

| Template | File | Use Case | Standards |
|----------|------|----------|-----------|
| **ISO 25010 Compliance** | [`docs/ISO_IEC_25010_COMPLIANCE.md`](ISO_IEC_25010_COMPLIANCE.md) | Software quality | ISO/IEC 25010:2011 |
| **Quality Attributes** | [`docs/QUALITY_ATTRIBUTES.md`](QUALITY_ATTRIBUTES.md) | Non-functional requirements | Performance, reliability, etc. |
| **Project Checklist** | [`docs/PROJECT_CHECKLIST.md`](PROJECT_CHECKLIST.md) | Completion verification | MIT-level checklist |

---

### 📁 Research Documentation Templates

Templates for academic/research projects:

| Template | File | Use Case | Features |
|----------|------|----------|----------|
| **Research README** | [`docs/research/README.md`](research/README.md) | Research framework overview | Methods, tools, references |
| **Mathematical Analysis** | [`docs/research/MATHEMATICAL_ANALYSIS.md`](research/MATHEMATICAL_ANALYSIS.md) | Formal proofs | Theorems, proofs, complexity |
| **Innovation Framework** | [`docs/research/INNOVATION_FRAMEWORK.md`](research/INNOVATION_FRAMEWORK.md) | Research innovation | Methodology, evaluation |

---

### 📁 Configuration Templates

| Template | File | Use Case |
|----------|------|----------|
| **Default Config** | [`config/default.yaml`](../config/default.yaml) | Application configuration |
| **Environment Example** | [`env.example`](../env.example) | Environment variables |
| **Plugin Manifest** | [`plugins/weather/plugin.yaml`](../plugins/weather/plugin.yaml) | Plugin configuration |
| **Benchmark Config** | [`benchmarks/configs/`](../benchmarks/configs/) | Performance benchmarks |
| **Experiment Template** | [`experiments/templates/`](../experiments/templates/) | Research experiments |

---

## 🚀 How to Reuse These Templates

### Option 1: Copy Individual Files

```bash
# Copy a single template
curl -O https://raw.githubusercontent.com/yourusername/multi-agent-tour-guide/main/CODE_OF_CONDUCT.md

# Copy GitHub templates
mkdir -p .github/ISSUE_TEMPLATE
curl -O https://raw.githubusercontent.com/yourusername/multi-agent-tour-guide/main/.github/ISSUE_TEMPLATE/bug_report.yml
```

### Option 2: Use as Git Template

```bash
# Clone and use as template
git clone --depth 1 https://github.com/yourusername/multi-agent-tour-guide.git my-project
cd my-project
rm -rf .git
git init
# Customize and start fresh!
```

### Option 3: GitHub Template Repository

1. Click "Use this template" on GitHub
2. Create new repository from template
3. Customize for your project

---

## ✏️ Customization Guide

### Minimal Changes Required

For each template, you typically need to change:

| Template Type | What to Change |
|---------------|----------------|
| **Community files** | Project name, URLs, contact emails |
| **GitHub templates** | Repository URLs, component names |
| **Technical docs** | Project-specific content |
| **Config files** | Your settings and API keys |

### Example: Customizing CODE_OF_CONDUCT.md

```markdown
# Before (template)
📧 **conduct@example.com**

# After (your project)
📧 **conduct@yourproject.org**
```

### Example: Customizing Bug Report Template

```yaml
# Before (template)
- label: I have searched [existing issues](https://github.com/yourusername/multi-agent-tour-guide/issues)

# After (your project)
- label: I have searched [existing issues](https://github.com/yourorg/yourproject/issues)
```

---

## 📋 Template Checklist

When reusing templates, ensure you:

- [ ] Replace all `yourusername` with your GitHub username/org
- [ ] Update project name throughout
- [ ] Change contact emails
- [ ] Update URLs to your repository
- [ ] Customize component names in issue templates
- [ ] Add your specific configuration options
- [ ] Update version numbers
- [ ] Add your team to AUTHORS.md
- [ ] Customize CITATION.cff with your details

---

## 🤝 Contributing Back

Found an improvement? We welcome contributions to make these templates better!

1. **Fork this repository**
2. **Improve a template**
3. **Submit a Pull Request**

Your improvements will help the entire community!

---

## 📜 License

All templates in this repository are licensed under the **MIT License**.

```
MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```

**You are free to:**
- ✅ Use commercially
- ✅ Modify
- ✅ Distribute
- ✅ Use privately

**No attribution required** (but appreciated!)

---

## 📞 Questions?

- 💬 [GitHub Discussions](https://github.com/yourusername/multi-agent-tour-guide/discussions)
- 📧 templates@example.com

---

<p align="center">
  <strong>Built for the community, by the community.</strong>
</p>

<p align="center">
  <em>Take what you need. Share what you learn.</em>
</p>

