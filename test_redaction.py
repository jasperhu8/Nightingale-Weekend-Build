# -*- coding: utf-8 -*-
"""
test_redaction.py
Goal: On a synthetic PHI sample, prove no PHI leaks to outputs or logs.

Assumptions:
- app.redaction.redact(text) returns a redacted string (replacing PHI with placeholders like [REDACTED]).
- app.logger.LOGGER.info(msg) writes to an in-memory buffer that is ALSO redacted.
"""

import re
from app.redaction import redact
from app.logger import LOGGER

def test_redaction_blocks_phi_in_output_and_logs():
    # Synthetic PHI sample (Singapore context)
    raw = (
        "My name is Alex Tan. "
        "NRIC: S1234567D. "
        "Mobile: +65 9123 4567. "
        "Email: alex.tan@example.com. "
        "I have had a fever for two days."
    )

    # 1) Run redaction on content that would be used downstream (e.g., before LLM/summarization)
    out = redact(raw)

    # 2) Simulate logging; logger must also avoid raw PHI
    LOGGER.info(raw)
    logs = LOGGER.dump()

    # Forbidden raw tokens must NOT appear in either output or logs
    forbidden_raw = [
        "Alex Tan",
        "S1234567D",
        "+65 9123 4567",
        "alex.tan@example.com",
    ]

    for token in forbidden_raw:
        assert token not in out, f"Output leaked PHI: {token}"
        assert token not in logs, f"Logs leaked PHI: {token}"

    # (Optional but nice) the redacted text should contain at least one placeholder
    # to show that redaction actually occurred.
    assert "[REDACTED]" in out or "[MASKED]" in out, "No redaction placeholder found in output."

    # Sanity check: non-PHI clinical content should remain
    assert "fever for two days" in out, "Clinical content should remain after redaction."