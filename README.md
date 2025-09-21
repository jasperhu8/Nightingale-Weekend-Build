# Data-Classifier Branch

This branch contains the **classification pipeline** for transforming raw patient complaints into standardized descriptions and linking them to ICD-11 disease categories. It demonstrates the **two-stage classifier design**:

1. **Stage-1: Standardization**  
   - Maps free-text patient complaints into a standardized medical description.  
   - Example: *"I've had a fever and cough for three days."* → *"Acute cough with fever and yellow sputum (~3 days)"*  
   - Provides both a standardized text and a shorthand ID (e.g., `RESP_ACUTE`).  

2. **Stage-2: ICD-11 Classification**  
   - Takes the standardized text and maps it into ICD-11 categories.  
   - Example: *Respiratory system disorders* → Code `12`.

## Purpose of This Branch

- **`synthetic_consults.jsonl`**  
  A synthetic dataset of patient complaints and aligned standard descriptions.  
  This serves as the **training/bootstrapping dataset** for the Stage-1 classifier.

- **`disease_labels.yaml`**  
  ICD-11–based taxonomy of 26 disease categories (plus V and X codes).  
  Each label includes a name, description, and representative keywords.  
  Used in **Stage-2 classification**.

- **`classifier.py`**  
  Implements the two-stage classifier:  
  - Stage-1: Complaint → Standardized description  
  - Stage-2: Standardized description → ICD-11 category  
  Includes a **keyword-based fallback** if the ML model is not available.

---

## Why This Matters

This branch simulates how the system will:  

- Help clinicians by reducing paperwork (complaints come pre-standardized).  
- Provide patients with consistent, clear labels for their conditions.  
- Enable future research and reminders by storing ICD-11 codes alongside clinical text.  

---

## Example Run

Command:

```bash
python data-classifier/classifier.py "I've had a fever and cough for three days."

=== Stage-1: Standardization ===
ID:   RESP_ACUTE
Text: Acute cough with fever and yellow sputum (~3 days)

=== Stage-2: ICD-11 ===
Suggested: 12 — Diseases of the respiratory system
Effective: 12 — Diseases of the respiratory system
```
