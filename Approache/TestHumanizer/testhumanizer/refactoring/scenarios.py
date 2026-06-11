SCENARIO_MAP = {
    "tests-only": {
        "id": "Scenario-1",
        "description": "Only the EvoSuite test suite is provided to the LLM.",
        "requires_source_code": False,
        "requires_summary": False,
    },
    "code-centric": {
        "id": "Scenario-2",
        "description": "The EvoSuite test suite and the full source class are provided.",
        "requires_source_code": True,
        "requires_summary": False,
    },
    "summary-based": {
        "id": "Scenario-3",
        "description": "The EvoSuite test suite and a class-level natural-language summary are provided.",
        "requires_source_code": False,
        "requires_summary": True,
    },
}
