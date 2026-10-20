from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime, timedelta
from sqlalchemy import or_
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///medisafe.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    batch = db.Column(db.String(80), nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    supplier = db.Column(db.String(120), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def status(self):
        today = date.today()
        if self.expiry_date < today:
            return "Expired"
        if self.expiry_date <= today + timedelta(days=30):
            return "Expiring Soon"
        return "Safe"

    def as_dict(self):
        return {
            "id": self.id, "name": self.name, "batch": self.batch,
            "expiry_date": self.expiry_date.isoformat(), "quantity": self.quantity,
            "supplier": self.supplier, "status": self.status(),
            "days_left": (self.expiry_date - date.today()).days
        }

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/medicines")
def list_medicines():
    search = request.args.get("search", "").strip()
    q = Medicine.query
    if search:
        term = f"%{search}%"
        q = q.filter(or_(Medicine.name.ilike(term), Medicine.batch.ilike(term), Medicine.supplier.ilike(term)))
    medicines = q.order_by(Medicine.expiry_date.asc()).all()
    return jsonify([m.as_dict() for m in medicines])

@app.post("/api/medicines")
def add_medicine():
    data = request.get_json(silent=True) or {}
    try:
        name = str(data.get("name", "")).strip()
        batch = str(data.get("batch", "")).strip()
        expiry = date.fromisoformat(str(data.get("expiry_date", "")))
        quantity = int(data.get("quantity", 0))
        supplier = str(data.get("supplier", "")).strip()
        if not name or not batch or quantity < 0:
            raise ValueError("Enter medicine name, batch number, and a non-negative quantity.")
    except (ValueError, TypeError):
        return jsonify({"error": "Please enter valid medicine details and an expiry date."}), 400
    medicine = Medicine(name=name, batch=batch, expiry_date=expiry, quantity=quantity, supplier=supplier)
    db.session.add(medicine)
    db.session.commit()
    return jsonify(medicine.as_dict()), 201

@app.delete("/api/medicines/<int:medicine_id>")
def delete_medicine(medicine_id):
    medicine = db.session.get(Medicine, medicine_id)
    if not medicine:
        return jsonify({"error": "Medicine not found."}), 404
    db.session.delete(medicine)
    db.session.commit()
    return jsonify({"message": "Medicine record deleted."})

@app.get("/api/summary")
def summary():
    all_meds = Medicine.query.all()
    return jsonify({
        "total": len(all_meds),
        "expired": sum(m.status() == "Expired" for m in all_meds),
        "soon": sum(m.status() == "Expiring Soon" for m in all_meds),
        "safe": sum(m.status() == "Safe" for m in all_meds),
        "low_stock": sum(m.quantity <= 10 for m in all_meds)
    })

@app.get("/api/alerts")
def alerts():
    today = date.today()
    meds = Medicine.query.filter(Medicine.expiry_date <= today + timedelta(days=30)).order_by(Medicine.expiry_date.asc()).all()
    return jsonify([m.as_dict() for m in meds])

with app.app_context():
    db.create_all()
    # Seed demo records only for a fresh database
    if Medicine.query.count() == 0:
        today = date.today()
        demo = [
            Medicine(name="Paracetamol 500mg", batch="PCM-2401", expiry_date=today + timedelta(days=240), quantity=120, supplier="Demo Pharma"),
            Medicine(name="Amoxicillin 250mg", batch="AMX-110", expiry_date=today + timedelta(days=12), quantity=36, supplier="Demo Pharma"),
            Medicine(name="Cough Syrup", batch="CS-009", expiry_date=today - timedelta(days=3), quantity=8, supplier="Sample Supplier"),
        ]
        db.session.add_all(demo)
        db.session.commit()

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
