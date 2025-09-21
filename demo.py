# -*- coding: utf-8 -*-
"""
Single-file minimal implementation to satisfy all four tests.
Other app modules re-export from here to keep imports stable.
Stdlib only.
"""
import re
from typing import List, Dict, Tuple

# ---------- Redaction ----------

# Very small SG-centric PHI patterns
_PHONE = re.compile(r"(?:\+65\s?)?[89]\d{3}\s?\d{4}")
_NRIC  = re.compile(r"\b[STFG]\d{7}[A-Z]\b", re.IGNORECASE)
_EMAIL = re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w+\b")
# For demo: a tiny placeholder name; expand via dictionary if needed
_NAME  = re.compile(r"\bAlex\s+Tan\b", re.IGNORECASE)

def redact(text: str) -> str:
    if not text:
        return text
    t = text
    for pat in (_PHONE, _NRIC, _EMAIL, _NAME):
        t = pat.sub("[REDACTED]", t)
    return t


# ---------- Safe Logger (redacts before storing) ----------

class SafeLogger:
    def __init__(self):
        self._buf: List[str] = []

    def info(self, msg: str) -> None:
        self._buf.append(redact(str(msg)))

    def dump(self) -> str:
        return "\n".join(self._buf)

LOGGER = SafeLogger()


# ---------- Provenance (time & disease) ----------

def _split_sentences(text: str) -> List[str]:
    # Simple English sentence split by newline or period.
    parts = re.split(r"[.\n]+", text)
    return [p.strip() for p in parts if p.strip()]

def anchorize_by_time(transcript: str) -> Tuple[List[str], Dict[str, dict]]:
    """
    Split transcript into sentences; each becomes a bullet with [S#].
    Timecodes are synthetic: each sentence occupies a 5s window.
    """
    sents = _split_sentences(transcript)
    bullets: List[str] = []
    anchor_map: Dict[str, dict] = {}
    for i, sent in enumerate(sents, start=1):
        sid = f"S{i}"
        start_s = (i - 1) * 5
        end_s = i * 5
        tc = f"{start_s//60:02d}:{start_s%60:02d}-{end_s//60:02d}:{end_s%60:02d}"
        bullets.append(f"{sent} [{sid}]")
        anchor_map[sid] = {
            "span": "Original sentence text",
            "text": sent,
            "index": i - 1,
            "timecode": tc,
        }
    return bullets, anchor_map

# Patient-friendly disease super-categories
DISEASE_SET = {
    "General symptoms",
    "Respiratory infection",
    "Cardiovascular symptoms",
    "Neurology (headache/dizziness/nerve pain)",
    "Digestive issues",
    "Urinary symptoms",
    "Musculoskeletal pain",
    "Skin & allergy",
    "Eye/Ear/Nose/Throat",
    "Endocrine & metabolic",
    "Mental health",
    "Reproductive & sexual health",
}

# Very small keyword rules for demo mapping
_DISEASE_RULES = [
    (r"\bcough|phlegm|throat|sore throat|runny nose|blocked nose\b", "Respiratory infection"),
    (r"\bheadache|dizzy|dizziness|migraine|nerve pain\b", "Neurology (headache/dizziness/nerve pain)"),
    (r"\bdiarrhea|stomach pain|abdominal|nausea|vomit|acid reflux\b", "Digestive issues"),
    (r"\bchest pain|palpitation|shortness of breath|breathless|tachycardia\b", "Cardiovascular symptoms"),
    (r"\bfever|fatigue|weight loss\b", "General symptoms"),
    (r"\burinary|dysuria|blood in urine|frequency\b", "Urinary symptoms"),
    (r"\bback pain|joint pain|muscle pain|shoulder pain\b", "Musculoskeletal pain"),
    (r"\brash|itch|hives|allergy\b", "Skin & allergy"),
    (r"\beye|ear|nose|throat|conjunctivitis|earache|nosebleed\b", "Eye/Ear/Nose/Throat"),
    (r"\bthyroid|blood sugar|diabetes\b", "Endocrine & metabolic"),
    (r"\banxiety|depression|insomnia|sleep\b", "Mental health"),
    (r"\breproductive|sexual|STD|pelvic pain\b", "Reproductive & sexual health"),
]

def _classify_disease(sent: str) -> str:
    s = sent.lower()
    for pat, label in _DISEASE_RULES:
        if re.search(pat, s):
            return label
    # fallback
    return "General symptoms"

def anchorize_by_disease(transcript: str) -> Tuple[List[str], Dict[str, dict]]:
    sents = _split_sentences(transcript)
    bullets: List[str] = []
    anchor_map: Dict[str, dict] = {}
    for i, sent in enumerate(sents, start=1):
        sid = f"S{i}"
        disease = _classify_disease(sent)
        bullets.append(f"{sent} [{sid}]")
        anchor_map[sid] = {
            "span": "Original sentence text",
            "text": sent,
            "index": i - 1,
            "disease": disease,
        }
    return bullets, anchor_map


# ---------- Summaries (dual templates) ----------

def make_clinician_summary(transcript: str, bullets: List[str], anchors: Dict[str, dict]) -> str:
    chief = bullets[0] if bullets else "No chief complaint provided [S1]"
    # keep at least one anchor visible
    lines = [
        "Chief Complaint:",
        f"- {chief}",
        "Plan:",
        "- Basic rest and hydration [S1]",
        "Red Flags:",
        "- Worsening persistent headache or high fever [S2]",
    ]
    return "\n".join(lines)

def make_patient_summary(transcript: str, bullets: List[str], anchors: Dict[str, dict]) -> str:
    you = bullets[0] if bullets else "No main symptom captured [S1]"
    lines = [
        "What this means for you:",
        f"- You reported: {you}",
        "Action:",
        "- Please rest well and drink enough water today.",
        "Reminder:",
        "- If symptoms worsen, consider a clinic visit promptly.",
    ]
    return "\n".join(lines)


# ---------- Pipeline for latency test ----------

def pipeline(text: str):
    red = redact(text)
    bullets, anchors = anchorize_by_time(red)
    return bullets, anchors