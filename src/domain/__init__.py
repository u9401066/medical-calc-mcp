"""
Domain Layer - Core Business Logic

This layer contains the pure business logic with zero external dependencies.
All medical calculations, interpretations, and tool metadata live here.

Submodules:
    - entities: Core domain entities (ScoreResult, ToolMetadata)
    - services: Calculator implementations
    - value_objects: Immutable value types (Unit, Reference, Interpretation)
    - registry: Tool registry for discovery
"""
