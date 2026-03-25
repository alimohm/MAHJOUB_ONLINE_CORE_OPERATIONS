import os
from flask import Flask, request, jsonify, send_from_directory
import requests
import json
import threading # أضفنا هذا لكي يعمل الكود في الخلفية ولا يتأخر

app = Flask(__name__)

# إعداداتك الثابتة
TEXTMEBOT_API_KEY = "CWEMDRmhtq4e"
QOMRA_TOKEN = "qmr_076ddc4c4cc944ce8830495f32a79291"
BASE_URL = "https://mahjoub-bot.onrender.com"

def send_whatsapp_async(order_data):
    """هذه الدالة تعمل في الخلفية لكي لا تسبب Timeout"""
    try:
        data = order_data.get('data', {})
        order_id = data.get('handle', '0000')
        # استخدمنا السعر من الويب هوك مباشرة (127 ريال) كما في صورتك (image_89cd83)
        total = data.get('totalPriceWithTax', 0)
        
        msg = f"✨ *طلب جديد من متجر محجوب* ✨\n🧾 رقم الطلب: `{order_id}`\n💰 الإجمالي: `{total}` ريال\n🔗 تتبع طلبك: https://mahjoub.online/customer/thank-you/{order_id}"
        
        phone = "967" + str(data.get('customerPhone', '')).replace('+', '')
        api_url = f"https://api.textmebot.com/send.php?recipient={phone}&apikey={TEXTMEBOT_API_KEY}&text={requests.utils.quote(msg)}"
        requests.get(api_url, timeout=5)
    except:
        pass

@app.route('/webhook', methods=['POST'])
def fast_webhook():
    try:
        payload = request.get_json()
        
        # تشغيل الإرسال في "خيط منفصل" لكي نرد على قمرة فوراً
        thread = threading.Thread(target=send_whatsapp_async, args=(payload,))
        thread.start()
        
        # الرد فوراً بـ 200 لكي لا يحدث Timeout
        return jsonify({"status": "received"}), 200
    except:
        return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
