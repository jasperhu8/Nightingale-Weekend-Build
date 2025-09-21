# Test Branch

This branch contains the four micro-tests required by the Nightingale Weekend Build.  
These tests serve as **proof of quality and user-centric thinking**, ensuring that the demo system adheres to privacy, provenance, latency, and design requirements.

## Files

- **test_grounding.py**  
  Validates that every bullet point in the generated summaries has a provenance anchor `[S#]`.  
  Ensures traceability of information back to its original source, either by timecode or disease category.

- **test_redaction.py**  
  Runs on synthetic PHI (Personally Identifiable Information) samples to prove that sensitive information is fully redacted.  
  Prevents leakage of patient details into outputs or logs.

- **test_latency.py**  
  Profiles the redaction and provenance pipeline.  
  Reports P50 (median) and P95 (95th percentile) latencies to measure performance under realistic conditions.

- **test_summary.py**  
  Compares clinician vs. patient summary templates generated from the same synthetic consultation.  
  Validates that the clinician version is glanceable for rapid review, while the patient version is actionable and empathetic.

---

## Purpose of this Branch
The **test branch** is dedicated to verifying the correctness, safety, and usability of the system.  
It demonstrates compliance with the non-negotiables: **privacy, provenance, latency, and distinct clinician/patient UX design**.
