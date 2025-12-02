# 🎨 Architecture Diagrams & Visual Assets

This folder contains the **official architecture diagrams** for the Multi-Agent Tour Guide System, designed for **MIT-level project documentation**.

## 📁 Current Diagrams

| File | Description | Referenced In |
|------|-------------|---------------|
| **`architecture-Overview.png`** | 8-phase system architecture flowchart | README.md Figure 1 |
| **`System-sequence-Overview.png`** | Complete sequence diagram with all phases | README.md Figure 2 |

---

## 🖼️ Diagram Descriptions

### 1. `architecture-Overview.png` - System Architecture

**Purpose:** High-level horizontal flow diagram showing the complete 8-phase pipeline from User Input to Tour Output.

**Phases Shown:**
| Phase | Component | Color | Description |
|:-----:|-----------|-------|-------------|
| 1 | 👤 USER | Purple | origin, destination, profile inputs |
| 2 | 🗺️ GOOGLE MAPS | Purple | Route fetching via `GoogleMapsClient` |
| 3 | ⏱️ TRAVEL SIMULATOR | Pink | Scheduler controls tour pacing |
| 4 | 🎭 POINT PROCESSOR | Orange | `ThreadPoolExecutor` orchestration |
| 5 | ⚡ PARALLEL AGENTS | Blue | Video (Red), Music (Yellow), Text (Green) |
| 6 | 🚦 SMART QUEUE | Teal | Graceful degradation (3/3, 2/3, 1/3) |
| 7 | ⚖️ JUDGE AGENT | Cyan | Thompson Sampling + SHAP |
| 8 | 📥 COLLECTOR | Blue | Final `TourGuideOutput` generation |

---

### 2. `System-sequence-Overview.png` - Sequence Diagram

**Purpose:** Temporal sequence flow showing message passing between all system components with parallel execution visualization.

**Key Sections:**
- **Phase 1:** Route Initialization (User → GoogleMaps)
- **Phase 2:** Scheduler Initialization (TravelSimulator setup)
- **Phase 3:** Point Processing Loop (with nested parallel execution)
  - `par` block for Video, Music, Text agents
  - `alt` block for graceful degradation states
  - Judge evaluation with Thompson Sampling
  - Collector storage
- **Phase 4:** Final Output (TourGuideOutput generation)

---

## 🛠️ Source Files (Mermaid)

These diagrams were generated from Mermaid source files located in `docs/diagrams/`:

| Rendered Image | Source File | Render Tool |
|----------------|-------------|-------------|
| `architecture-Overview.png` | [`architecture-mit.mmd`](../../docs/diagrams/architecture-mit.mmd) | [mermaid.live](https://mermaid.live) |
| `System-sequence-Overview.png` | [`sequence-with-scheduler.mmd`](../../docs/diagrams/sequence-with-scheduler.mmd) | [mermaid.live](https://mermaid.live) |

### How to Regenerate Diagrams

1. Open the `.mmd` source file from `docs/diagrams/`
2. Go to [mermaid.live](https://mermaid.live)
3. Paste the Mermaid code
4. Click "Actions" → "Download PNG"
5. Save to this folder with the appropriate name

---

## 📐 Theme Configuration

The diagrams use a **dark theme with vibrant accents** designed for readability:

```yaml
# Theme Variables (from .mmd files)
background: '#0f172a'        # Dark navy background
primaryColor: '#6366f1'      # Indigo primary
secondaryColor: '#ec4899'    # Pink accent
tertiaryColor: '#14b8a6'     # Teal accent
actorBkg: '#312e81'          # Purple actor backgrounds
lineColor: '#818cf8'         # Light indigo lines
```

### Phase Color Mapping

```css
PHASE 1 (INPUT):      #312e81 (Deep Purple)
PHASE 2 (ROUTE):      #4c1d95 (Purple)
PHASE 3 (SCHEDULER):  #831843 (Pink)
PHASE 4 (PROCESSOR):  #7c2d12 (Orange)
PHASE 5 (AGENTS):     #1e3a5f (Blue) + Red/Yellow/Green
PHASE 6 (QUEUE):      #134e4a (Teal)
PHASE 7 (JUDGE):      #164e63 (Cyan)
PHASE 8 (OUTPUT):     #1e3a8a (Blue)
```

---

## 📷 Image Specifications

| Property | Value |
|----------|-------|
| **Format** | PNG |
| **Background** | Transparent / Dark |
| **Resolution** | 2x scale (for Retina) |
| **Width** | 100% responsive in README |

---

## 🔗 Usage in README

```markdown
<!-- Architecture Diagram -->
<p align="center">
  <img src="assets/images/architecture-Overview.png" alt="System Architecture" width="100%"/>
</p>

<!-- Sequence Diagram -->
<p align="center">
  <img src="assets/images/System-sequence-Overview.png" alt="Sequence Diagram" width="100%"/>
</p>
```

---

## 📚 Additional Diagram Resources

For creating new diagrams:

| Tool | Best For | Link |
|------|----------|------|
| **Mermaid Live** | Sequence/Flow diagrams | [mermaid.live](https://mermaid.live) |
| **Excalidraw** | Hand-drawn style | [excalidraw.com](https://excalidraw.com) |
| **draw.io** | Professional flowcharts | [app.diagrams.net](https://app.diagrams.net) |

---

**Last Updated:** December 2025  
**Project:** Multi-Agent Tour Guide System (MIT-Level)
