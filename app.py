# app.py (FINAL - No Homepage Route)

import os
import json
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# --- App & Database Configuration ---
app = Flask(__name__, static_folder='static', static_url_path='')
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'scans.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Database Model ---
class Redemption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    offer_id = db.Column(db.String(50), nullable=False)
    offering_biz = db.Column(db.String(50), nullable=False)
    referrer_id = db.Column(db.String(50), nullable=False)

# --- API Route for Tracking Redemptions ---
@app.route('/api/redeem')
def redeem_offer():
    offer_id = request.args.get('offer_id')
    offering_biz = request.args.get('offering_biz')
    referrer_id = request.args.get('referrer_id')

    if not all([offer_id, offering_biz, referrer_id]):
        return jsonify({"status": "error", "message": "Missing tracking information"}), 400

    new_redemption = Redemption(offer_id=offer_id, offering_biz=offering_biz, referrer_id=referrer_id)
    db.session.add(new_redemption)
    db.session.commit()

    return """
    <!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Offer Redeemed</title><style>
    body { display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f0f9f3; }
    .container { text-align: center; padding: 40px; background-color: #fff; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
    .checkmark { font-size: 100px; color: #28a745; line-height: 1; }
    h1 { color: #28a745; margin-top: 10px; } p { color: #555; font-size: 1.2em; }
    </style></head><body><div class="container">
    <div class="checkmark">✓</div><h1>Success!</h1><p>Offer redeemed and tracked.</p>
    </div></body></html>
    """

# --- Dashboard Route for Analytics ---
@app.route('/dashboard')
def dashboard():
    redemptions = Redemption.query.order_by(Redemption.timestamp.desc()).all()
    referral_counts = {}
    for r in redemptions:
        key = (r.referrer_id, r.offering_biz)
        referral_counts[key] = referral_counts.get(key, 0) + 1
    chart_labels = []
    chart_data = []
    for (referrer, offering), count in referral_counts.items():
        chart_labels.append(f"{referrer} ➡ {offering}")
        chart_data.append(count)
    return render_template('dashboard.html', redemptions=redemptions, chart_labels=json.dumps(chart_labels), chart_data=json.dumps(chart_data))

# This block is only used for local testing. PythonAnywhere does not use this.
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)