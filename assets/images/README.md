# 🎨 Architecture Diagrams & Visual Assets

This folder contains beautiful, colorful architecture diagrams for the Multi-Agent Tour Guide System.

## 📁 Folder Structure

```
assets/images/
├── README.md                      # This file
├── architecture-overview.png      # Main system architecture
├── smart-queue-flow.png          # Smart Queue degradation flow
├── agent-pipeline.png            # Agent processing pipeline
├── research-framework.png        # Research components
├── pareto-frontier.png           # Quality-Latency tradeoff
└── dashboard-preview.png         # Dashboard screenshot
```

---

## 🛠️ Recommended Tools for Creating Beautiful Diagrams

### 🌟 Top Recommendations

| Tool | Best For | Cost | Link |
|------|----------|------|------|
| **Excalidraw** | Hand-drawn style, collaborative | Free | [excalidraw.com](https://excalidraw.com) |
| **draw.io (diagrams.net)** | Professional flowcharts | Free | [app.diagrams.net](https://app.diagrams.net) |
| **Figma** | Pixel-perfect, design systems | Free tier | [figma.com](https://figma.com) |
| **Mermaid Live** | Code-to-diagram | Free | [mermaid.live](https://mermaid.live) |
| **Lucidchart** | Enterprise diagrams | Free tier | [lucidchart.com](https://lucidchart.com) |
| **Miro** | Collaborative whiteboard | Free tier | [miro.com](https://miro.com) |

---

## 🎨 Creating the Main Architecture Diagram

### Option 1: Excalidraw (Recommended for Beautiful Hand-Drawn Style)

1. Go to [excalidraw.com](https://excalidraw.com)
2. Create your diagram with these components:
   - User Input box (top)
   - Parallel Agents (Video, Music, Text) - use different colors
   - Smart Queue with degradation states
   - Judge Agent
   - Final Playlist (bottom)
3. Use the library feature for icons
4. Export as PNG (2x scale for high resolution)

### Option 2: draw.io (Professional Style)

1. Go to [app.diagrams.net](https://app.diagrams.net)
2. Choose "Create New Diagram"
3. Use these shapes:
   - Rounded rectangles for components
   - Swimlanes for layers
   - Icons from the shape library
4. Color scheme suggestions:
   - Input: `#E3F2FD` (light blue)
   - Agents: `#E8F5E9` (light green)
   - Queue: `#FFF3E0` (light orange)
   - Judge: `#F3E5F5` (light purple)
   - Output: `#E8F5E9` (light green)
5. Export as PNG or SVG

### Option 3: Figma (Pixel-Perfect Professional)

1. Go to [figma.com](https://figma.com)
2. Create a new design file
3. Use auto-layout for aligned components
4. Add shadows and gradients for depth
5. Export at 2x for Retina displays

### Option 4: Mermaid Live Editor (Code-Based)

1. Go to [mermaid.live](https://mermaid.live)
2. Copy the Mermaid code from `docs/diagrams/system-architecture.mmd`
3. Customize colors in the code
4. Export as PNG or SVG

---

## 🎨 Recommended Color Palette

### MIT-Style Professional Colors

```css
/* Primary Colors */
--primary-blue: #1976D2;
--primary-green: #388E3C;
--primary-purple: #7B1FA2;
--primary-orange: #F57C00;

/* Background Colors */
--bg-light-blue: #E3F2FD;
--bg-light-green: #E8F5E9;
--bg-light-purple: #F3E5F5;
--bg-light-orange: #FFF3E0;

/* Accent Colors */
--accent-red: #E94560;
--accent-teal: #00BCD4;
--accent-yellow: #FFC107;

/* Gradients */
--gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
--gradient-success: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
--gradient-danger: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
```

### Component Color Assignments

| Component | Background | Border | Icon |
|-----------|------------|--------|------|
| **User Input** | `#E3F2FD` | `#1976D2` | 👤 |
| **Video Agent** | `#FFCDD2` | `#D32F2F` | 🎬 |
| **Music Agent** | `#C8E6C9` | `#388E3C` | 🎵 |
| **Text Agent** | `#BBDEFB` | `#1976D2` | 📖 |
| **Smart Queue** | `#FFF3E0` | `#F57C00` | 📬 |
| **Judge Agent** | `#E1BEE7` | `#7B1FA2` | ⚖️ |
| **Final Output** | `#E8F5E9` | `#388E3C` | 🎯 |

---

## 📐 Diagram Templates

### Main Architecture Template (draw.io)

```
┌─────────────────────────────────────────────────────────────────┐
│                    👤 USER INPUT                                 │
│            Route: "Tel Aviv" → "Jerusalem"                      │
│     ╔═══════════════════════════════════════════════════════╗   │
│     ║  Profile: age=25, interests=["history"], driver=false ║   │
│     ╚═══════════════════════════════════════════════════════╝   │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    🎯 ORCHESTRATOR                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              PARALLEL AGENT EXECUTION                     │   │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │   │
│  │   │ 🎬 VIDEO    │  │ 🎵 MUSIC    │  │ 📖 TEXT     │      │   │
│  │   │   AGENT     │  │   AGENT     │  │   AGENT     │      │   │
│  │   │  YouTube    │  │  Spotify    │  │ Wikipedia   │      │   │
│  │   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘      │   │
│  │          │                │                │              │   │
│  └──────────┼────────────────┼────────────────┼──────────────┘   │
│             └────────────────┼────────────────┘                  │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    📬 SMART QUEUE                         │   │
│  │   ┌─────────┐    ┌─────────┐    ┌─────────┐              │   │
│  │   │ 3/3 ✅  │───▶│ 2/3 ⚠️  │───▶│ 1/3 ⚡  │              │   │
│  │   │COMPLETE │ 15s│SOFT DEG │ 30s│HARD DEG │              │   │
│  │   └─────────┘    └─────────┘    └─────────┘              │   │
│  └──────────────────────────┬───────────────────────────────┘   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    ⚖️ JUDGE AGENT                         │   │
│  │      Thompson Sampling │ SHAP │ User Profile Matching    │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    🎯 FINAL PLAYLIST                             │
│   📍 Point 1: 📖 TEXT   │   📍 Point 2: 🎬 VIDEO   │   📍 Point 3: 🎵 │
│   "Silent Monks..."     │   "Latrun Documentary"  │   "Jerusalem..." │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📷 Image Specifications

### For README (GitHub)

| Type | Size | Format | DPI |
|------|------|--------|-----|
| Architecture Overview | 1200×800 px | PNG | 144 |
| Flow Diagrams | 800×600 px | PNG | 144 |
| Dashboard Preview | 1600×900 px | PNG | 144 |
| Icons | 128×128 px | PNG/SVG | 144 |

### For Documentation

| Type | Size | Format |
|------|------|--------|
| Detailed Diagrams | 1920×1080 px | PNG/SVG |
| Print Quality | 3000×2000 px | PNG |
| Vector Graphics | Any | SVG |

---

## 🔗 How to Use in README

### Embedding Images

```markdown
<!-- From assets folder -->
![Architecture Overview](assets/images/architecture-overview.png)

<!-- With alt text and link -->
[![System Architecture](assets/images/architecture-overview.png)](docs/ARCHITECTURE.md)

<!-- Centered with HTML -->
<p align="center">
  <img src="assets/images/architecture-overview.png" alt="System Architecture" width="800"/>
</p>

<!-- With caption -->
<p align="center">
  <img src="assets/images/architecture-overview.png" alt="System Architecture" width="800"/>
  <br/>
  <em>Figure 1: Multi-Agent Tour Guide System Architecture</em>
</p>
```

---

## 🚀 Quick Start: Create Your First Diagram

### Step 1: Open Excalidraw
Go to [excalidraw.com](https://excalidraw.com)

### Step 2: Load Template
Copy and import this basic structure, then customize with colors

### Step 3: Export
- Click "Export" (top-left menu)
- Choose PNG
- Set scale to 2x
- Enable "Background" if you want white background

### Step 4: Save to This Folder
Save as `architecture-overview.png` in this folder

### Step 5: Update README
Add to your README:
```markdown
<p align="center">
  <img src="assets/images/architecture-overview.png" alt="Architecture" width="800"/>
</p>
```

---

## 📚 Resources

- [Excalidraw Libraries](https://libraries.excalidraw.com/) - Pre-made icons and shapes
- [draw.io Templates](https://www.diagrams.net/blog/aws-diagrams) - AWS/Azure templates
- [Figma Community](https://www.figma.com/community) - Free design resources
- [Mermaid Documentation](https://mermaid.js.org/intro/) - Code-based diagrams

---

**Created for:** Multi-Agent Tour Guide System  
**Purpose:** Beautiful, colorful architecture visualization

