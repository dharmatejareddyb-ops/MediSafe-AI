# MediSafe e-AI — Hackathon prototype

A small full-stack pharmacy inventory demo that flags expired medicines and items expiring within 30 days.

## Requirements
- Python 3.10+
- Internet is needed only to install dependencies; the app itself runs locally.

## Run on Windows
1. Extract `medisafe_eai.zip`.
2. Open Command Prompt/PowerShell in the extracted `medisafe_eai` folder.
3. Create a virtual environment (recommended):
   ```bash
   py -m venv .venv
   .venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Start the app:
   ```bash
   python app.py
   ```
6. Open http://127.0.0.1:5000 in your browser.

On first run, the app creates `instance/medisafe.db` and adds three demo records: one safe, one expiring soon, and one expired. Delete/add records to demonstrate the alert workflow.

## Features
- Dashboard counts: total, expired, expiring within 30 days, low stock (10 or fewer).
- Add medicine records with name, batch, expiry, quantity, and supplier.
- Search inventory.
- Status classification computed on the server.
- Alerts endpoint: `GET /api/alerts`.
- JSON API: `GET/POST /api/medicines`, `DELETE /api/medicines/<id>`, `GET /api/summary`.

## API examples
List medicines:
```bash
curl http://127.0.0.1:5000/api/medicines
```
Add a medicine:
```bash
curl -X POST http://127.0.0.1:5000/api/medicines -H "Content-Type: application/json" -d "{\"name\":\"Test tablet\",\"batch\":\"T-101\",\"expiry_date\":\"2027-12-31\",\"quantity\":20,\"supplier\":\"Demo supplier\"}"
```

## Important limitations
This is a hackathon demonstration, not a certified medical/pharmacy system. It relies on expiry dates entered by the operator and does not read labels with OCR, validate batch recalls, or send SMS/email alerts. For production, add authentication, audit logs, backups, role-based access, secure deployment, and validated notification integrations. Do not rely on the prototype alone to decide whether a medicine is safe.
