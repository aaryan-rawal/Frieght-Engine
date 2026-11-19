# Domain package

"""Domain entities for OptiFreight AI.

All models are Pydantic v2 data classes that mirror the schema defined in
`docs/DATA_MODEL.md`.  They purposefully avoid any ORM or framework imports so
that the core logic can be used in pure‑Python contexts (e.g. rule engine,
simulation, or testing) without side‑effects.
"""
