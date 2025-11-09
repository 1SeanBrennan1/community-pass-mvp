# generate_site.py (FINAL version with Admin Homepage)

import os
import qrcode
import io
import base64

# --- Configuration ---
OUTPUT_DIR = 'static'
ENTRY_QR_DIR = 'entry_qrs'
API_BASE_URL = "http://downtownloop-seani.pythonanywhere.com"

# --- Data ---
offer_templates = { "Austen Jewellers": ["15% off your next purchase", "Free cleaning on one item"], "French 50": ["10% off your total bill", "Free coffee with any food purchase"], "94 Take the Cake": ["15% off any specialty drink", "Buy one pastry, get one 50% off"], "Full Circle": ["Your first class free", "20% off a 5-class pass"], "Tribal Connections": ["10% off any retail item", "Free beverage with purchase over $20"], "Ginger Laurier": ["15% off one full-priced item", "$10 off your purchase of $50 or more"], "Naughty Grape": ["10% off any bottle of local wine", "Free wine tasting sample"], "Eyes 360": ["20% off designer frames", "$50 off a complete pair of glasses"], "Hubtown": ["Buy one flight, get a second 50% off", "15% off merchandise"], "Salt and Lime": ["15% off one full-priced item", "$10 off your purchase of $50 or more"], "Underground Styles": ["20% off your first service", "Free conditioning treatment with any haircut"], "Descubre Beauty": ["15% off any service over $50", "Free eyebrow shaping with any facial"], "Monkey Mountain": ["10% off any board game", "Buy one, get one 50% off on plush toys"], "Yoonique Books": ["15% off any paperback book", "Free bookmark with any purchase"], "Rebel Bean Roasters": ["20% off your first bag of beans", "Free espresso shot with any purchase"]}
companies = [{ 'name': 'Austen Jewellers', 'file': 'austen.html', 'prefix': 'AJL' }, { 'name': 'French 50', 'file': 'french50.html', 'prefix': 'F50' }, { 'name': '94 Take the Cake', 'file': '94takethecake.html', 'prefix': 'TTC' }, { 'name': 'Full Circle', 'file': 'fullcircle.html', 'prefix': 'FCL' }, { 'name': 'Tribal Connections', 'file': 'tribalconnections.html', 'prefix': 'TCN' }, { 'name': 'Ginger Laurier', 'file': 'gingerlaurier.html', 'prefix': 'GLR' }, { 'name': 'Naughty Grape', 'file': 'naughtygrape.html', 'prefix': 'NGR' }, { 'name': 'Eyes 360', 'file': 'eyes360.html', 'prefix': 'E36' }, { 'name': 'Hubtown', 'file': 'hubtown.html', 'prefix': 'HTN' }, { 'name': 'Salt and Lime', 'file': 'saltandlime.html', 'prefix': 'SLT' }, { 'name': 'Underground Styles', 'file': 'undergroundstyles.html', 'prefix': 'UGS' }, { 'name': 'Descubre Beauty', 'file': 'descubrebeauty.html', 'prefix': 'DBY' }, { 'name': 'Monkey Mountain', 'file': 'monkeymountain.html', 'prefix': 'MMN' }, { 'name': 'Yoonique Books', 'file': 'yooniquebooks.html', 'prefix': 'YBK' }, { 'name': 'Rebel Bean Roasters', 'file': 'rebelbeanroasters.html', 'prefix': 'RBR' }]

def generate_qr_as_data_url(data):
    img = qrcode.make(data)
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_str}"

def generate_site():
    print("🚀 Starting website generation...")
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    if not os.path.exists(ENTRY_QR_DIR): os.makedirs(ENTRY_QR_DIR)

    # --- 1. Generate Level 1 "Entry" QR Codes ---
    for company in companies:
        entry_url = f"{API_BASE_URL}/{company['file']}"
        img = qrcode.make(entry_url)
        img.save(os.path.join(ENTRY_QR_DIR, f"{company['prefix']}_entry.png"))
    print(f"✅ Generated {len(companies)} Level 1 Entry QR codes.")

    # --- 2. Generate each company's unique HTML page with accordions ---
    for referring_company in companies:
        offers_html = ""
        for offering_company in companies:
            if referring_company['prefix'] == offering_company['prefix']: continue
            offers_html += '<details style="border: 1px solid #ccc; border-radius: 5px; margin-bottom: 10px;">'
            offers_html += f'<summary style="padding: 15px; font-weight: bold; font-size: 1.2em; cursor: pointer; background-color: #f9f9f9;">{offering_company["name"]}</summary>'
            offers_html += '<div class="offers-content" style="padding: 0 15px 15px 15px;">'
            for i, offer_desc in enumerate(offer_templates[offering_company['name']]):
                offer_id = f"{offering_company['prefix']}-offer{i+1}"
                redemption_url = f"{API_BASE_URL}/api/redeem?offer_id={offer_id}&offering_biz={offering_company['prefix']}&referrer_id={referring_company['prefix']}"
                qr_data_url = generate_qr_as_data_url(redemption_url)
                offers_html += f"""
                <div style="border-top: 1px solid #eee; padding-top: 10px; margin-top: 10px;">
                    <p><strong>Offer:</strong> {offer_desc}</p>
                    <p>Show this QR code to the cashier to redeem:</p>
                    <img src="{qr_data_url}" alt="Redemption QR Code" style="width: 200px; height: 200px;">
                </div>"""
            offers_html += '</div></details>'
        page_content = f"""
        <!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Offers for {referring_company['name']}</title><style>body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; background-color: #f0f2f5; }} summary::-webkit-details-marker {{ display: none; }} summary {{ list-style: none; }}</style></head>
        <body><header style="text-align: center; border-bottom: 1px solid #ccc; padding-bottom: 10px; background-color: #fff; padding: 20px; border-radius: 8px 8px 0 0;"><h1>Downtown Loop</h1>
        <p>Exclusive offers for customers of <strong>{referring_company['name']}</strong></p></header>
        <main style="margin-top: 20px;">{offers_html}</main></body></html>"""
        with open(os.path.join(OUTPUT_DIR, referring_company['file']), 'w') as f: f.write(page_content)
        print(f"📄 Generated page: {referring_company['file']}")

    # --- 3. NEW: Generate the Admin Homepage (index.html) with Printable QR Codes ---
    admin_qr_html = ""
    for company in sorted(companies, key=lambda c: c['name']):
        qr_image_path = f"/entry_qrs/{company['prefix']}_entry.png"
        admin_qr_html += f"""
        <div style="border: 1px solid #ccc; border-radius: 8px; padding: 20px; margin-bottom: 20px; text-align: center; background: #fff;">
            <h2>{company['name']}</h2>
            <img src="{qr_image_path}" alt="Entry QR for {company['name']}" style="width: 250px; height: 250px;">
            <p style="margin-top: 15px;">Download and print this QR code for the business.</p>
        </div>
        """

    index_page_content = f"""
    <!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Downtown Loop - Admin QR Codes</title>
    <style>body {{ font-family: sans-serif; max-width: 800px; margin: auto; padding: 20px; background-color: #f4f4f4; }}</style></head>
    <body><div style="text-align:center;"><h1>Downtown Loop - Printable Entry QR Codes</h1>
    <p>This page is for the administrator. Provide each business with its corresponding QR code below.</p></div>{admin_qr_html}</body></html>
    """
    with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w') as f: f.write(index_page_content)
    print("✅ Generated Admin Homepage (index.html)")

    print("\n✅🎉 Success! Website generation is complete.")

if __name__ == "__main__":
    generate_site()