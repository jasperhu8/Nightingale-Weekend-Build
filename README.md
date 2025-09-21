# Nightingale-Weekend-Build

This repository contains a conceptual prototype for a VoiceAI system designed to improve the patient–clinician experience across three stages: **Pre-care**, **During-care**, and **Post-care**.  
Due to the limited build time, the focus is on **ideas and product fit** rather than fully implemented systems.  
Below is the design rationale.

---

## Pre-care

- **Classification model for patient complaints**:  
  A small training set is manually labeled to map raw patient complaints (e.g., "headache for three days") to a standardized medical terminology library.  
  Although only a partial dataset is prepared here, this demonstrates how scaling the dataset in the future could reduce clinicians’ paperwork burden and free more time for diagnosis, treatment, and follow-up. At the same time, patients will be given prompts on which aspects they can describe.

- **Consent as Conversation**:  
  Before recording begins, VoiceAI asks:  
  *“To protect your privacy, may I record and summarize this consultation?”*  
  - If the patient declines, VoiceAI responds: *“That’s fine, we can always start whenever you are ready. In the meantime, you may still record your symptoms for yourself.”*  
  This humanizes the consent process and ensures patient autonomy.

---

## During-care

### Patient side
- **Standardization + Mirroring**:  
  Patient complaints are standardized through the classification model, and mirrored to the clinician.  
  Clinician results (diagnosis, severity grading, reference treatment) are mirrored back to the patient.

- **Process Visualization**:  
  The patient sees a simple visual flow:  
  - *Self-report submitted → Clinician viewed → Results issued*  
  - Each stage uses **both color coding and exclamation marks** (1 green !, 2 orange !!, 3 red !!!).  
    This dual encoding improves visual efficiency while remaining inclusive for color-blind users.

- **Prescription as Action Cards**:  
  Prescriptions are displayed as prioritized action cards (1, 2, 3) so patients remember the most critical actions.  
  A notes section allows patients to edit or add personal reminders.  
  This positions VoiceAI not only as a diagnostic assistant, but also as a **personal health manager — a “small AI doctor at your side.”**

### Clinician side
- **Transparent Standardization**:  
  Standardized complaints are displayed as bullet points.  
  Each point has a button **“Show full raw complaint”** so the clinician can verify the original text and prevent misinterpretation.

- **Diagnosis Input & Severity Grading**:  
  The clinician enters a diagnosis, selects treatment type (medication vs. in-person), and chooses severity (1–3 exclamation marks).  
  A reference treatment duration is also provided, which links directly to the post-care module.

---

## Post-care

- **Conversational Reminders**:  
  The system automatically schedules reminders:  
  - One day before the reference treatment ends, the patient is prompted:  
    *“The doctor advised you to take daily medication — have you been able to complete this?”*  
  - Framing reminders as **dialogue** reflects empathy, strengthens patient–AI connection, and emphasizes human-centered care.  
  *(This is a central design choice.)*

- **Follow-up Questionnaire**:  
  On the final day of the treatment cycle, patients receive a recovery scale (1–5, from mild to severe).  
  - If symptoms are mild (1–2) but the patient still requests follow-up → a secondary notice suggests observation is possible.  
  - If symptoms are severe (3–5) but the patient declines follow-up → a secondary notice encourages reconsideration of consultation.  

This design ensures continuous engagement, proactive care reminders, and empathetic patient interaction.
