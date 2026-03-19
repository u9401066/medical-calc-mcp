"""Shared MCP guidance text for weaker models and start-here resources."""

TOOL_USAGE_SEQUENCE = "discover(...) -> get_tool_schema(tool_id) -> calculate(tool_id, params)"


def get_tool_usage_playbook_markdown() -> str:
    """Return the canonical tool-usage playbook shared by prompts and resources."""
    return """# Tool Usage Playbook
小模型工具使用作戰手冊

## Goal
Use the MCP tools correctly with the fewest avoidable errors.

## Mandatory Sequence
Always follow this sequence unless the user already supplied a verified canonical tool_id and all exact parameters.

1. Call `discover(...)` first to identify the most suitable tool.
2. Call `get_tool_schema(tool_id)` second to read exact parameter names, required fields, enums, and units.
3. Call `calculate(tool_id, params)` only after reading the schema.

## Never Do These
- Never invent a tool_id from memory when `discover(...)` can confirm it.
- Never guess parameter names such as `creatinine` vs `serum_creatinine`.
- Never guess enum values or boolean meanings.
- Never retry with the same broken payload if the previous response already returned `guidance`, `suggestions`, or `param_template`.

## Safe Retry Policy
If a call fails:

1. Read `guidance.resolved_tool_id` or `resolved_value` if present.
2. Read `guidance.next_actions`.
3. Read `component_scores.param_template` and `guidance.required_params`.
4. Retry with corrected canonical tool_id and exact parameter names.

## Start Here
- Preferred prompt: `tool_usage_playbook()`
- Preferred resource: `guide://tool-usage-playbook`
- Calculator index: `calculator://list`

## Minimal Safe Examples

### Example A: Unknown tool
```python
discover(by="keyword", value="sepsis")
get_tool_schema("qsofa_score")
calculate("qsofa_score", {
    "respiratory_rate": 24,
    "systolic_bp": 92,
    "altered_mentation": True
})
```

### Example B: User already named a tool
```python
get_tool_schema("news2_score")
calculate("news2_score", {
    "respiratory_rate": 18,
    "spo2": 96,
    "on_supplemental_o2": False,
    "temperature": 37.0,
    "systolic_bp": 120,
    "heart_rate": 80,
    "consciousness": "A"
})
```

## Decision Rule
If you are choosing between speed and correctness, choose correctness:
`discover -> get_tool_schema -> calculate`
"""
