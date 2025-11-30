# System Diagrams

This directory contains architectural and flow diagrams for the Multi-Agent Tour Guide System.

## Diagram Index

| Diagram | Description | Format |
|---------|-------------|--------|
| [system-architecture.mmd](system-architecture.mmd) | High-level C4 system context | Mermaid |
| [smart-queue-flow.mmd](smart-queue-flow.mmd) | Smart Queue state machine | Mermaid |
| [agent-sequence.mmd](agent-sequence.mmd) | Agent interaction sequence | Mermaid |
| [research-pipeline.mmd](research-pipeline.mmd) | Research analysis pipeline | Mermaid |

## Rendering Diagrams

### Option 1: VS Code Extension
Install the "Markdown Preview Mermaid Support" extension.

### Option 2: Mermaid CLI
```bash
npm install -g @mermaid-js/mermaid-cli
mmdc -i diagram.mmd -o diagram.png
```

### Option 3: GitHub
GitHub renders Mermaid diagrams in markdown files automatically.

### Option 4: Online Editor
Use [mermaid.live](https://mermaid.live) for interactive editing.

## Conventions

- Use `.mmd` extension for Mermaid files
- Include diagram description in comments
- Use consistent color schemes
- Export PNG versions for documentation

