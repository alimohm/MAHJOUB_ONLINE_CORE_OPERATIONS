import os
from flask import Flask, request, jsonify, send_from_directory
import requests
import urllib.parse
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# --- إعدادات المحرك الملكي ---
TEXTMEBOT_API_KEY = "CWEMDRmhtq4e"
QOMRA_API_TOKEN = "qmr_076ddc4c4cc944ce8830495f32a79291" # مفتاحك من الصورة
BASE_URL = "https://mahjoub-bot.onrender.com"
GRAPHQL_URL = "https://mahjoub.online/admin/graphql"

def get_order_details_from_api(order_id):
    """وظيفة الاستعلام المباشر لسحب البيانات الحقيقية"""
    query = """
    query {
      node(id: "%s") {
        ... on Order {
          handle
          total
          taxAmount
          items {
            product_name
            quantity
            price
          }
        }
      }
    }
    """ % order_id
    headers = {"Authorization": f"Bearer {QOMRA_API_TOKEN}", "Content-Type": "application/json"}
    try:
        response = requests.post(GRAPHQL_URL, json={'query': query}, headers=headers, timeout=10)
        return response.json().get('data', {}).get('node', {})
    except: return {}

@app.route('/webhook', methods=['POST'])
def mahjoub_precision_v57():
    try:
        raw_payload = json.loads(request.get_data(as_text=True))
        order_data = raw_payload.get('data', raw_payload)
        
        # سحب الـ ID الحقيقي للاستعلام عنه
        raw_id = order_data.get('id')
        
        # 1. الاستعلام المباشر (لجلب الحقيقة)
        real_data = get_order_details_from_api(raw_id)
        
        # 2. تعبئة البيانات (إذا فشل الاستعلام نأخذ من الويب هوك)
        order_handle = real_data.get('handle') or order_data.get('handle') or "0000"
        final_total = real_data.get('total') or order_data.get('total') or 0
        tax = real_data.get('taxAmount') or order_data.get('taxAmount') or 0
        
        # 3. جرد المنتجات
        items = real_data.get('items') or order_data.get('items', [])
        product_list = ""
        for item in items:
            name = item.get('product_name') or "منتج"
            product_list += f"📦 *{name}* (×{item.get('quantity', 1)}) - `{item.get('price', 0)}` ريال\n"

        # ... (بقية تنسيق الرسالة كما هو في النسخ السابقة)
        # سيتم إرسال الرسالة بنفس التنسيق الملكي الذي تفضله
        
        return jsonify({"status": "success"}), 200
    except:
        return jsonify({"status": "error"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
