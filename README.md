TumorHeal Backend v2
--------------------

This backend implements auth, plan run, and report endpoints to integrate with the TumorHeal mobile app.

Run locally:
1. python -m venv .venv
2. source .venv/bin/activate
3. pip install -r requirements.txt
4. uvicorn app.main:app --reload --port 8000
