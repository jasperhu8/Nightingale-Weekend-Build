# App Branch

This branch contains the **demo application code** for the Nightingale Weekend Build.  
It is not a full production system, but a minimal framework to demonstrate how different modules could be connected and tested.

## Files

- `demo.py`  
  Entry point that ties together redaction, provenance, summarization, and logging.  
  Used mainly to show an end-to-end flow.

- `redaction.py`, `logger.py`, `provenance.py`, `summarize.py`, `pipeline.py`  
  Modular components that define basic functions for privacy, provenance, summary generation, and orchestration.  
  These are thin wrappers — their main role is to connect with the **test branch** for validation.

- `__init__.py`  
  Makes the folder importable as a Python package.

## Purpose

The **app branch** provides a minimal demo implementation that links all required modules.  
It is designed to be lightweight and illustrative — the focus is on showing structure and integration, not building a full production-grade system.
