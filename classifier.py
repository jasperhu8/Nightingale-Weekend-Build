# data/classifier.py
# -*- coding: utf-8 -*-
"""
Two-stage text classification for Nightingale.

Stage 1: Complaint text  -> Standardized summary snippet (patient-friendly, clinician-glanceable).
Stage 2: Standardized ID -> ICD-11 top-level code & name (read from disease_labels.yaml).

Design principles:
- Minimal and explainable. Prefer TF-IDF + Logistic Regression; fall back to keyword rules if sklearn is absent.
- Read ICD labels from YAML so the label space stays aligned with your data branch.
- Keep a doctor override hook: model suggests a code, clinicians may override; we keep both for provenance.

CLI:
    python -m data.classifier "I've had a fever and cough for three days."
    python -m data.classifier "Thirsty and peeing a lot lately." 05   # with doctor override

Programmatic:
    from data.classifier import end_to_end_classify
    res = end_to_end_classify("Loose stools since yesterday with abdominal cramps.")
    print(res.standardized_text, res.icd_suggested, res.icd_effective)
"""

from __future__ import annotations
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Optional sklearn stack
_SKLEARN_AVAILABLE = True
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.utils.validation import check_is_fitted
except Exception:
    _SKLEARN_AVAILABLE = False

# YAML for ICD labels
try:
    import yaml
except Exception as e:
    raise RuntimeError("PyYAML is required. Please install via `pip install pyyaml`.") from e


# ----------------------------
# Paths (adjust if needed)
# ----------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSONL = REPO_ROOT / "data" / "synthetic_consults.jsonl"
DEFAULT_LABELS_YAML = REPO_ROOT / "data-classifier" / "disease_labels.yaml"


# -----------------------------------------------------
# Stage-1: Complaint -> Standardized summary (snippet)
# -----------------------------------------------------
# 这些标准化描述用于“可读的要点句”，既给医生速览，也可回显给患者
STD_DESCRIPTIONS = {
    "RESP_ACUTE": "Acute cough with fever and yellow sputum (~3 days)",
    "ENDO_CHRONIC_GLYC": "Chronic polydipsia/polyuria suggestive of glycemic dysregulation",
    "CARD_EXERTIONAL": "Exertional chest tightness with transient palpitations",
    "GI_ACUTE": "Acute diarrhea with crampy abdominal pain (~1 day)",
    "MSK_STIFF_PAIN": "Morning-predominant joint stiffness and pain",
    "GENERAL_UNSPECIFIED": "General symptoms requiring further triage",
}

# 简单关键词规则（英文为主；如需中文可自行添加）
KEYWORDS_TO_STD = [
    # Respiratory acute
    (("fever", "cough"), "RESP_ACUTE"),
    (("cough", "sputum"), "RESP_ACUTE"),
    # Endocrine glycemic
    (("thirsty", "urinate"), "ENDO_CHRONIC_GLYC"),
    (("polydipsia", "polyuria"), "ENDO_CHRONIC_GLYC"),
    # Cardiovascular exertional
    (("chest tightness",), "CARD_EXERTIONAL"),
    (("shortness of breath",), "CARD_EXERTIONAL"),
    (("heart racing",), "CARD_EXERTIONAL"),
    # GI acute
    (("diarrhea",), "GI_ACUTE"),
    (("abdominal pain",), "GI_ACUTE"),
    # MSK stiffness/pain
    (("joint", "stiff"), "MSK_STIFF_PAIN"),
    (("joint", "pain"), "MSK_STIFF_PAIN"),
]

def _weak_label_std_id(text: str) -> Optional[str]:
    """Heuristic labeler for Stage-1 when training data is tiny.
    Returns a standardized ID if all keywords in any rule are present; otherwise None.
    """
    s = (text or "").lower()
    for keys, std_id in KEYWORDS_TO_STD:
        if all(k in s for k in keys):
            return std_id
    return None

@dataclass
class Stage1Model:
    """Wrapper for Stage-1.
    If sklearn is available, trains a tiny TF-IDF + Logistic Regression model;
    otherwise, falls back to keyword rules.
    """
    pipe: Optional["Pipeline"] = None  # type: ignore[name-defined]

    def is_trained(self) -> bool:
        if self.pipe is None:
            return False
        try:
            check_is_fitted(self.pipe)
            return True
        except Exception:
            return False

    def predict_std(self, complaint: str) -> Tuple[str, str]:
        """Return (standardized_id, standardized_text)."""
        # 优先使用训练好的模型
        if self.pipe is not None and self.is_trained():
            std_id = self.pipe.predict([complaint])[0]
            return std_id, STD_DESCRIPTIONS.get(std_id, std_id)
        # 回退：关键词规则
        std_id = _weak_label_std_id(complaint)
        if std_id:
            return std_id, STD_DESCRIPTIONS.get(std_id, std_id)
        # 仍未命中
        return "GENERAL_UNSPECIFIED", STD_DESCRIPTIONS["GENERAL_UNSPECIFIED"]

def load_consults(jsonl_path: Path) -> List[Dict]:
    """Load jsonl samples. Each line is a JSON object."""
    samples: List[Dict] = []
    if not jsonl_path.exists():
        return samples
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                samples.append(json.loads(line))
            except Exception:
                # 忽略坏行
                continue
    return samples

def train_stage1(jsonl_path: Path = DEFAULT_JSONL) -> Stage1Model:
    """Train a minimal Stage-1 model if sklearn is available; else return rule-based wrapper.

    Supervision: weak labels generated by keyword rules on 'complaint'.
    When your dataset grows and you add a gold 'standardized' field,
    replace the y-construction to use that field directly.
    """
    model = Stage1Model(pipe=None)
    if not _SKLEARN_AVAILABLE:
        return model  # 无 sklearn，直接规则

    samples = load_consults(jsonl_path)
    X, y = [], []
    for rec in samples:
        text = (rec.get("complaint") or "").strip()
        if not text:
            continue
        std_id = _weak_label_std_id(text)
        if std_id is not None:
            X.append(text)
            y.append(std_id)

    # 数据太少时不训练，使用规则作为兜底
    if len(X) < 3:
        return model

    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
        ("clf", LogisticRegression(max_iter=500))
    ])
    pipe.fit(X, y)
    model.pipe = pipe
    return model


# -------------------------------------------------------
# Stage-2: Standardized -> ICD-11 (read YAML for names)
# -------------------------------------------------------
def load_icd_labels(yaml_path: Path = DEFAULT_LABELS_YAML) -> Dict[str, Dict]:
    """Load ICD-11 top-level label dict from YAML (supports both with/without top-level 'labels')."""
    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    labels = data.get("labels", data)
    return labels

# 目前固定映射（与你的当前5类样本一致）；后续可替换为学习到的映射或多标签模型
STD_TO_ICD = {
    "RESP_ACUTE": "12",          # Respiratory
    "ENDO_CHRONIC_GLYC": "05",   # Endocrine/metabolic
    "CARD_EXERTIONAL": "11",     # Circulatory
    "GI_ACUTE": "13",            # Digestive
    "MSK_STIFF_PAIN": "15",      # Musculoskeletal
    "GENERAL_UNSPECIFIED": "21", # Symptoms/signs/clinical findings
}

def map_std_to_icd(std_id: str, icd_dict: Dict[str, Dict]) -> Dict[str, str]:
    """Return {'code': <ICD code>, 'name': <ICD name>} with safe fallback to '21'."""
    code = STD_TO_ICD.get(std_id, "21")
    info = icd_dict.get(code, {"name": "Unknown", "description": ""})
    return {"code": code, "name": info.get("name", "Unknown")}


# ----------------------------------------
# Doctor override & provenance-friendly IO
# ----------------------------------------
@dataclass
class ClassificationResult:
    standardized_id: str
    standardized_text: str
    icd_suggested: Dict[str, str]
    icd_effective: Dict[str, str]
    override_applied: bool

def end_to_end_classify(
    complaint_text: str,
    doctor_icd_override: Optional[str] = None,
    jsonl_path: Path = DEFAULT_JSONL,
    yaml_path: Path = DEFAULT_LABELS_YAML,
) -> ClassificationResult:
    """Run the two-stage pipeline with an optional doctor override."""
    # Stage-1
    s1 = train_stage1(jsonl_path)
    std_id, std_text = s1.predict_std(complaint_text)

    # Stage-2
    icd_dict = load_icd_labels(yaml_path)
    icd_suggested = map_std_to_icd(std_id, icd_dict)

    # Doctor override
    if doctor_icd_override and doctor_icd_override in icd_dict:
        icd_effective = {"code": doctor_icd_override, "name": icd_dict[doctor_icd_override]["name"]}
        override_applied = True
    else:
        icd_effective = icd_suggested
        override_applied = False

    return ClassificationResult(
        standardized_id=std_id,
        standardized_text=std_text,
        icd_suggested=icd_suggested,
        icd_effective=icd_effective,
        override_applied=override_applied,
    )


# ---------------
# CLI quick demo
# ---------------
def _cli():
    if len(sys.argv) < 2:
        print("Usage: python -m data.classifier \"complaint text here\" [override_code_optional]")
        sys.exit(1)
    complaint = sys.argv[1]
    override = sys.argv[2] if len(sys.argv) > 2 else None

    res = end_to_end_classify(complaint, doctor_icd_override=override)
    print("=== Stage-1: Standardization ===")
    print(f"ID:   {res.standardized_id}")
    print(f"Text: {res.standardized_text}")
    print()
    print("=== Stage-2: ICD-11 ===")
    print(f"Suggested: {res.icd_suggested['code']} — {res.icd_suggested['name']}")
    if res.override_applied:
        print(f"Effective (overridden): {res.icd_effective['code']} — {res.icd_effective['name']}")
    else:
        print(f"Effective: {res.icd_effective['code']} — {res.icd_effective['name']}")

if __name__ == "__main__":
    _cli()