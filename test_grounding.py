# -*- coding: utf-8 -*-
"""
Grounding (provenance) tests:
1) Time-based provenance: every summary bullet has an anchor [S#] and a timecode "MM:SS-MM:SS".
2) Disease-based provenance: every summary bullet has an anchor [S#] and a patient-friendly disease category.

Implementation contract (you will implement these in app/provenance.py):
    anchorize_by_time(transcript: str) -> (bullets: List[str], anchor_map: Dict[str, dict])
    anchorize_by_disease(transcript: str) -> (bullets: List[str], anchor_map: Dict[str, dict])

anchor_map entry example:
    {
      "S1": {
         "span": "Original sentence text",
         "index": 0,
         "timecode": "00:00-00:05",            # for time-based
         "disease": "Respiratory infection"    # for disease-based
      },
      ...
    }

This test is demo-friendly: only requires pytest + stdlib.
"""

import re
import random
import pytest

from app.provenance import anchorize_by_time, anchorize_by_disease

# Patient-friendly disease super-categories (not departments; easy for laypersons to grasp)
EXPECTED_PATIENT_FRIENDLY_DISEASES = {
    "General symptoms",           # 发热/乏力/体重变化等
    "Respiratory infection",      # 咳嗽/咳痰/喉咙痛/鼻塞等
    "Cardiovascular symptoms",    # 胸痛/心悸/呼吸急促等
    "Neurology (headache/dizziness/nerve pain)",
    "Digestive issues",           # 腹痛/腹泻/反酸/恶心等
    "Urinary symptoms",           # 频尿/尿痛/血尿等
    "Musculoskeletal pain",       # 关节痛/肌肉痛/背痛等
    "Skin & allergy",             # 皮疹/瘙痒/荨麻疹等
    "Eye/Ear/Nose/Throat",        # 眼红/耳痛/鼻出血/喉痛等
    "Endocrine & metabolic",      # 血糖异常/甲状腺相关等
    "Mental health",              # 焦虑/抑郁/睡眠问题等
    "Reproductive & sexual health"
}

# A tiny synthetic transcript (Chinese, multi-symptom) for demo purposes.
SYNTHETIC_TRANSCRIPT = (
    "I have had a headache for the past three days, and also developed a fever.\n"
    "In the last two days I started coughing with some yellow phlegm, and my throat hurts when I talk a lot.\n"
    "Yesterday I had diarrhea twice and some dull stomach pain.\n"
    "Occasionally I feel palpitations, but they go away quickly."
)

ANCHOR_PATTERN = re.compile(r"\[S\d+\]$")               # bullets must end with [S#]
TIMECODE_PATTERN = re.compile(r"^\d{2}:\d{2}-\d{2}:\d{2}$")  # "MM:SS-MM:SS"


def _assert_common_anchor_integrity(bullets, anchor_map):
    assert bullets, "Expected at least one bullet."
    # Each bullet has trailing [S#]
    for b in bullets:
        assert ANCHOR_PATTERN.search(b), f"Missing [S#] anchor in bullet: {b}"
        sid = b.split("[")[-1].strip("]")
        assert sid in anchor_map, f"Anchor id {sid} not found in anchor_map."
        # Basic anchor fields
        meta = anchor_map[sid]
        assert isinstance(meta.get("span", ""), str) and meta["span"], "Missing original span."
        assert isinstance(meta.get("index", 0), int), "Missing index field."


def test_grounding_by_time_has_anchors_and_timecodes():
    bullets, anchor_map = anchorize_by_time(SYNTHETIC_TRANSCRIPT)

    _assert_common_anchor_integrity(bullets, anchor_map)

    # Sample 2 anchors to check timecodes exist and follow "MM:SS-MM:SS"
    sample_ids = random.sample(list(anchor_map.keys()), k=min(2, len(anchor_map)))
    for sid in sample_ids:
        tc = anchor_map[sid].get("timecode", "")
        assert TIMECODE_PATTERN.match(tc), f"Invalid or missing timecode for {sid}: {tc}"


def test_grounding_by_disease_has_anchors_and_patient_friendly_categories():
    bullets, anchor_map = anchorize_by_disease(SYNTHETIC_TRANSCRIPT)

    _assert_common_anchor_integrity(bullets, anchor_map)

    # Every anchor should carry a patient-friendly disease label from our set
    for sid, meta in anchor_map.items():
        disease = meta.get("disease", "")
        assert disease in EXPECTED_PATIENT_FRIENDLY_DISEASES, (
            f"Disease category '{disease}' not in the patient-friendly set."
        )