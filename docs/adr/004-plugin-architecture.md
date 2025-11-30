# ADR-004: Plugin Architecture for Extensibility

## Status

Accepted

## Date

2025-11

## Context

The system needs to support:
1. **New Content Types**: Beyond Video, Music, Text
2. **External Integrations**: Weather, Food, Events
3. **Custom Agents**: User-defined content providers
4. **Zero Downtime**: Add features without core changes

Design goals:
- Open/Closed Principle: Open for extension, closed for modification
- Single Responsibility: Plugins handle their own logic
- Dependency Inversion: Core depends on abstractions

## Decision

Implement a **Plugin Architecture** with:

### Components

```
┌─────────────────────────────────────────────────────────────────┐
│                          CORE SYSTEM                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ Plugin       │    │ Plugin       │    │ Lifecycle    │      │
│  │ Registry     │◄───│ Manager      │───►│ Hooks        │      │
│  │              │    │              │    │              │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │               │
│         │            ┌──────┴──────┐           │               │
│         │            │   Events    │           │               │
│         │            │   System    │           │               │
│         │            └─────────────┘           │               │
└─────────┼───────────────────────────────────────┼───────────────┘
          │                                       │
          ▼                                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                          PLUGINS                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Weather    │    │    Food      │    │   Events     │      │
│  │   Plugin     │    │   Plugin     │    │   Plugin     │      │
│  │              │    │              │    │              │      │
│  │ plugin.yaml  │    │ plugin.yaml  │    │ plugin.yaml  │      │
│  │ plugin.py    │    │ plugin.py    │    │ plugin.py    │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Plugin Interface

```python
class PluginBase(ABC):
    """Base class for all plugins"""
    
    @property
    @abstractmethod
    def name(self) -> str: ...
    
    @property
    @abstractmethod
    def version(self) -> str: ...
    
    def on_load(self) -> None: ...
    def on_start(self) -> None: ...
    def on_stop(self) -> None: ...
    def on_unload(self) -> None: ...

class ContentProviderPlugin(PluginBase):
    """Plugin that provides content"""
    
    @abstractmethod
    def search_content(self, location: str, context: dict) -> ContentResult: ...
```

### Plugin Manifest

```yaml
# plugins/weather/plugin.yaml
name: weather
version: 1.0.0
description: Weather forecasts for route points
author: Tour Guide Team

capabilities:
  - CONTENT_PROVIDER

dependencies:
  - openweathermap-api>=1.0.0

configuration:
  api_key: ${WEATHER_API_KEY}
  units: metric

enabled: true
```

### Auto-Discovery

```python
# Plugins discovered from plugins/ directory
plugins/
├── weather/
│   ├── plugin.yaml    # Manifest (required)
│   ├── plugin.py      # Entry point (required)
│   └── agent.py       # Implementation
└── food/
    ├── plugin.yaml
    └── plugin.py
```

## Consequences

### Positive

- **Extensibility**: Add new agents without modifying core
- **Isolation**: Plugin failures don't crash core
- **Configuration**: YAML-based, no code changes
- **Versioning**: Independent plugin versions
- **Community**: Third-party plugin development

### Negative

- **Complexity**: Plugin lifecycle management
- **Discovery**: Need to scan directories
- **Security**: Plugins can execute arbitrary code
- **Testing**: Integration testing more complex

### Neutral

- Plugins loaded at startup (not hot-reload)
- Configuration via environment variables

## Alternatives Considered

### Alternative 1: Inheritance-Based Extension

**Description**: Subclass base agents for new types

**Pros**:
- Simple
- Familiar pattern

**Cons**:
- Requires core code changes
- Tight coupling

**Why Rejected**: Violates Open/Closed principle

### Alternative 2: Configuration-Only

**Description**: Define new agents via YAML config

**Pros**:
- No code required
- Easy to modify

**Cons**:
- Limited flexibility
- Can't handle complex logic

**Why Rejected**: Too restrictive for rich integrations

### Alternative 3: Dynamic Import

**Description**: Import modules at runtime by name

**Pros**:
- Flexible
- No registry needed

**Cons**:
- Security risks
- Error-prone
- No manifest/metadata

**Why Rejected**: Lacks structure and security controls

## References

- [Martin, R.C. (2017). Clean Architecture - Plugin Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Gamma et al. (1994). Design Patterns - Strategy Pattern](https://refactoring.guru/design-patterns/strategy)
- [Python Plugin Architectures](https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/)

## Notes

Current plugins:
- `weather/` - Weather forecast integration (example)
- `food/` - Restaurant recommendations (placeholder)

Future plugins:
- `events/` - Local events and festivals
- `ar/` - Augmented reality content
- `social/` - Social media integration

