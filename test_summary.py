# -*- coding: utf-8 -*-
"""
test_summary.py
Goal: Validate that from the same transcript we can produce two distinct summaries:
1) Clinician template (structured, glanceable).
2) Patient template (conversational, actionable).
Also check that provenance anchors [S#] are present and no PHI is leaked.
"""

import re
from app.provenance import anchorize_by_time
from app.summarize import make_clinician_summary, make_patient_summary

SYNTHETIC_TRANSCRIPT = (
    "I have had a headache for the past three days, and also developed a fever.\n"
    "In the last two days I started coughing with some yellow phlegm.\n"
    "Yesterday I had diarrhea twice and some dull stomach pain.\n"
    "Occasionally I feel palpitations, but they go away quickly."
)

ANCHOR_PATTERN = re.compile(r"\[S\d+\]")

def test_dual_templates_have_expected_sections_and_provenance():
    bullets, anchor_map = anchorize_by_time(SYNTHETIC_TRANSCRIPT)

    clinician = make_clinician_summary(SYNTHETIC_TRANSCRIPT, bullets, anchor_map)
    patient = make_patient_summary(SYNTHETIC_TRANSCRIPT, bullets, anchor_map)

    # --- Clinician template checks ---
    assert "Chief Complaint:" in clinician
    assert "Plan:" in clinician
    assert "Red Flags:" in clinician

    # --- Patient template checks ---
    assert "Action:" in patient
    assert "Reminder:" in patient

    # --- Both should contain provenance anchors ---
    assert ANCHOR_PATTERN.search(clinician), "Clinician summary missing [S#] anchors"
    assert ANCHOR_PATTERN.search(patient), "Patient summary missing [S#] anchors"

    # --- They should not be identical ---
    assert clinician != patient

    # --- Consistency: at least one shared anchor appears in both ---
    shared = False
    for sid in anchor_map.keys():
        if sid in clinician and sid in patient:
            shared = True
            break
    assert shared, "Expected at least one [S#] anchor to be shared between clinician and patient summaries"

def test_no_phi_in_summaries():
    bullets, anchor_map = anchorize_by_time(SYNTHETIC_TRANSCRIPT)

    clinician = make_clinician_summary(SYNTHETIC_TRANSCRIPT, bullets, anchor_map)
    patient = make_patient_summary(SYNTHETIC_TRANSCRIPT, bullets, anchor_map)

    forbidden_raw = ["Alex Tan", "S1234567D", "+65 9123 4567", "alex.tan@example.com"]
    for token in forbidden_raw:
        assert token not in clinician, f"Clinician summary leaked PHI: {token}"
        assert token not in patient, f"Patient summary leaked PHI: {token}"