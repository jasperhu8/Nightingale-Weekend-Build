# Nightingale Weekend Build — Brief

## Objective & Assumptions
This prototype explores how a VoiceAI assistant can streamline patient–clinician interactions in an outpatient single-consultation setting.  

**Assumptions**:  
- Single patient–clinician session.  
- Input provided as **transcribed text** (ASR is replaced with manual text input for this prototype).  
- A small manually labeled dataset is prepared to map patient complaints to standardized terminology. This demonstrates the direction of standardization, even though only a partial dataset is included due to limited time.

---

## Architecture / Workflow
The prototype pipeline follows four main stages:

1. **Redaction** — Remove personally identifiable health information (PHI) such as names, phone numbers, or addresses before further processing.  
2. **Provenance** — Every summary bullet is assigned a unique anchor (e.g., [S1]) that links back to the original transcript span.  
3. **Summarization** — Two templates generate outputs in parallel:  
   - Clinician summary: structured, glanceable.  
   - Patient summary: conversational, actionable.  
4. **Memory** — Treatment duration and advice are recorded to support post-care reminders and questionnaires.  

---

## Key Decisions
- Import a manually summarized library of **clinician medical history descriptors** as the reference standard.  
- Import a set of **patient complaints**, with a small portion manually labeled to connect complaints to the standard terminology.  
- Use this labeled set as the training base for a **classification model** to standardize complaints, with the clear note that the dataset is very limited due to time. Expansion and full labeling would be required in future iterations.  
- **Consent as Conversation**: VoiceAI asks *“To protect your privacy, may I record and summarize this consultation?”*. If the patient declines, the system responds: *“That’s fine, we can always start whenever you are ready. In the meantime, you may still record your symptoms for yourself.”*  

---

## Failures, Cuts, Successes, and Challenges
*(Section intentionally left blank for now.)*

---

## Clinician vs. Patient Templates

### Clinician Template
- Shows standardized complaints as bullet points.  
- Each bullet has a **“Show raw input”** option to reveal the original patient statement.  
- Clinician can input diagnosis, choose severity level (graded 1–3 with exclamation marks), and specify treatment duration.  

### Patient Template
- Mirrors standardized complaints and clinician results.  
- Displays a **process visualization**: *self-report submitted → clinician viewed → results issued*, with severity shown using both colors and exclamation marks (1 green, 2 orange, 3 red). This ensures efficient communication while remaining accessible for color-blind users.  
- Prescriptions are formatted as **action cards** (1, 2, 3) so that key actions are clear and memorable.  
- A notes section allows patients to add or edit reminders themselves.  
- Post-care reminders are phrased as empathetic questions: *“The doctor advised you to take daily medication — have you been able to complete this?”* to emphasize human-centered care.  
- A final-day follow-up questionnaire collects recovery scores (1–5) and adaptively suggests observation or follow-up based on patient responses.  

---

## Product Fit
- **Clinician side**: reduces paperwork by standardizing patient complaints, presents structured information, and offers quick access to raw input.  
- **Patient side**: empathetic, accessible, and supportive — acting as both diagnostic mirror and personal health manager.  
- Together, these perspectives deliver strong product fit: **glanceable for clinicians, delightful for patients**.
