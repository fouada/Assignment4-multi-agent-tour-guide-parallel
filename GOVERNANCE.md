# 🏛️ Project Governance

## Multi-Agent Tour Guide System

This document describes the governance model for the Multi-Agent Tour Guide System.

---

## 📋 Table of Contents

1. [Project Mission](#project-mission)
2. [Governance Model](#governance-model)
3. [Roles & Responsibilities](#roles--responsibilities)
4. [Decision Making](#decision-making)
5. [Contribution Path](#contribution-path)
6. [Conflict Resolution](#conflict-resolution)
7. [Changes to Governance](#changes-to-governance)

---

## 🎯 Project Mission

The Multi-Agent Tour Guide System exists to:

1. **Advance AI orchestration research** through open-source collaboration
2. **Provide a production-grade reference implementation** for multi-agent systems
3. **Enable personalized travel experiences** through AI technology
4. **Foster a welcoming community** for researchers and developers
5. **Maintain MIT-level academic standards** while being accessible to all

---

## 🏗️ Governance Model

We follow a **Benevolent Dictatorship** model during the early project phase, transitioning toward a **Meritocratic Governance** model as the community grows.

### Current Phase: Foundation (2025)

```
┌─────────────────────────────────────────────┐
│              Project Lead                    │
│         (Benevolent Dictator)               │
├─────────────────────────────────────────────┤
│              Core Maintainers               │
│        (Trusted Contributors)               │
├─────────────────────────────────────────────┤
│              Contributors                    │
│          (Active Developers)                │
├─────────────────────────────────────────────┤
│              Community                       │
│        (Users, Reporters, Advocates)        │
└─────────────────────────────────────────────┘
```

### Future Phase: Mature Community

```
┌─────────────────────────────────────────────┐
│              Steering Committee             │
│          (Elected Representatives)          │
├─────────────────────────────────────────────┤
│              Working Groups                  │
│     (Core, Research, Docs, Community)       │
├─────────────────────────────────────────────┤
│              Maintainers                     │
│         (Area Specialists)                  │
├─────────────────────────────────────────────┤
│              Contributors                    │
│          (Active Developers)                │
├─────────────────────────────────────────────┤
│              Community                       │
│        (Users, Reporters, Advocates)        │
└─────────────────────────────────────────────┘
```

---

## 👥 Roles & Responsibilities

### 🎯 Project Lead

**Current:** Dr. Yoram Segal (Course Director)

**Responsibilities:**
- Set overall project direction
- Make final decisions on contentious issues
- Appoint and remove maintainers
- Represent the project publicly
- Ensure academic integrity

**Term:** Indefinite during foundation phase

### 🔧 Core Maintainers

**Responsibilities:**
- Review and merge pull requests
- Triage issues and discussions
- Guide architectural decisions
- Mentor contributors
- Maintain code quality

**Requirements:**
- Significant contributions to the project
- Demonstrated understanding of codebase
- Commitment to project values
- Nomination by existing maintainer + approval

**Current Maintainers:**
| Name | Area | GitHub |
|------|------|--------|
| TBD | Core | @username |
| TBD | Research | @username |
| TBD | Documentation | @username |

### 🌟 Contributors

**Responsibilities:**
- Submit quality pull requests
- Follow contribution guidelines
- Participate in discussions
- Help other community members

**How to become one:**
1. Have a merged pull request
2. Follow the [CONTRIBUTING.md](CONTRIBUTING.md) guidelines

### 🌍 Community Members

**Everyone is welcome to:**
- Use the software
- Report bugs and issues
- Suggest features
- Participate in discussions
- Spread the word

---

## 🗳️ Decision Making

### Types of Decisions

| Type | Examples | Process |
|------|----------|---------|
| **Trivial** | Typo fixes, small doc updates | Any maintainer merges |
| **Minor** | Bug fixes, small features | PR review + 1 maintainer approval |
| **Standard** | New features, refactoring | PR review + 2 maintainer approvals |
| **Major** | Breaking changes, architecture | RFC process + community input |
| **Foundational** | License, governance changes | Project Lead + supermajority |

### Request for Comments (RFC) Process

For major changes:

1. **Propose**: Open a GitHub Discussion with `[RFC]` prefix
2. **Discuss**: 2-week community discussion period
3. **Refine**: Author incorporates feedback
4. **Vote**: Maintainers vote (supermajority required)
5. **Implement**: Approved RFCs may be implemented
6. **Document**: Update ADR documentation

### Voting Rules

| Decision Type | Required Votes | Quorum |
|---------------|----------------|--------|
| Minor changes | 1 maintainer | N/A |
| Standard changes | 2 maintainers | 50% |
| Major changes | Supermajority (66%) | 75% |
| Foundational | Project Lead + 80% | 100% |

---

## 📈 Contribution Path

```
Community Member
       │
       ▼ (first contribution)
  Contributor
       │
       ▼ (sustained contributions + nomination)
  Maintainer
       │
       ▼ (exceptional leadership)
  Core Maintainer
       │
       ▼ (elected by community)
  Steering Committee Member (future)
```

### Path to Maintainer

1. **Contribute consistently** for 3+ months
2. **Review PRs** and help other contributors
3. **Demonstrate expertise** in one or more areas
4. **Get nominated** by an existing maintainer
5. **Pass vote** by core maintainers (majority)

### Maintainer Responsibilities

- Respond to issues within 1 week
- Review assigned PRs within 2 weeks
- Attend monthly maintainer meetings
- Mentor new contributors
- Uphold code of conduct

### Stepping Down

Maintainers may step down at any time by notifying the project lead. Inactive maintainers (>3 months) may be moved to emeritus status.

---

## ⚖️ Conflict Resolution

### Escalation Path

```
1. Direct Discussion
       │
       ▼ (unresolved)
2. Maintainer Mediation
       │
       ▼ (unresolved)
3. Project Lead Decision
       │
       ▼ (code of conduct violation)
4. Enforcement (see CODE_OF_CONDUCT.md)
```

### Principles

1. **Assume good intent** - Most conflicts arise from miscommunication
2. **Focus on issues, not people** - Attack the problem, not the person
3. **Seek understanding** - Listen before responding
4. **Document decisions** - Keep records for transparency
5. **Respect privacy** - Handle sensitive matters privately

---

## 📝 Changes to Governance

This governance document may be changed through:

1. **Proposal**: GitHub Discussion with `[GOVERNANCE]` prefix
2. **Discussion**: 4-week community discussion period
3. **Vote**: Project Lead approval + 80% maintainer vote
4. **Implementation**: Update this document with effective date

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | Dec 2025 | Initial governance document |

---

## 📞 Contact

### For Governance Questions

- 💬 [GitHub Discussions](https://github.com/yourusername/multi-agent-tour-guide/discussions)
- 📧 governance@example.com

### For Code of Conduct Issues

- See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- 📧 conduct@example.com

---

## 📜 License

This governance document is licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

---

<p align="center">
  <strong>Open governance for an open-source project.</strong>
</p>

<p align="center">
  <em>Built by the community, for the community.</em>
</p>

