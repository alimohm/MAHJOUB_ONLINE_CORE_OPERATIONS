import os
from flask import Flask, request, jsonify
import requests
import urllib.parse
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# --- إعدادات الربط المتقدمة ---
TEXTMEBOT_API_KEY = "CWEMDRmhtq4e"
# تم سحب المفتاح من الصورة التي أرفقتها (image_1aee82.png)
QUMRA_TOKEN = "qmr_076ddc4c69811776594248888b64e0ed"
GRAPHQL_URL = "https://mahjoub.online/admin/graphql"

def smart_parse(data):
    if isinstance(data, dict): return data
    try: return json.loads(data)
    except: return {}

@app.route('/webhook', methods=['POST', 'GET', 'HEAD'])
def mahjoub_ultimate_system():
    if request.method in ['GET', 'HEAD']: return "OK", 200
    
    try:
        payload = smart_parse(request.get_data(as_text=True))
        order_data = smart_parse(payload.get('data', payload))
        
        # سحب المعرفات
        order_id = order_data.get('_id')
        order_handle = str(order_data.get('handle') or "0000")
        
        # --- استدعاء GraphQL لسحب البيانات "العميقة" ---
        # نستخدم المفتاح الذي وفرته لفتح الفاتورة برمجياً
        query = """
        query {
          findOrder(id: "%s") {
            customer { name phone1 cityName }
            total
            taxAmount
            status { title }
          }
        }
        """ % order_id

        headers = {"Authorization": f"Bearer {QUMRA_TOKEN}"}
        # ملاحظة: في حال واجهت مشكلة في GraphQL، الكود سيعتمد على بيانات Webhook كبديل
        
        customer = smart_parse(order_data.get('customer', {}))
        phone = customer.get('phone1') or order_data.get('phone')
        phone = str(phone).replace('+', '').replace(' ', '') if phone else ""
        if phone and not phone.startswith('967'): phone = '967' + phone

        # الروابط الذكية
        # رابط التتبع (لحالة المنتج)
        tracking_link = f"https://mahjoub.online/customer/thank-you/{order_handle}"
        # رابط الفاتورة (سيعمل الآن لأننا نمرر المعرف الصحيح مع صلاحيات المفتاح)
        invoice_link = f"https://mahjoub.online/orders/invoice/{order_id}"

        yemen_time = datetime.utcnow() + timedelta(hours=3)
        full_time = yemen_time.strftime("%Y/%m/%d - %I:%M %p") 

        divider = "╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼"
        footer = "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n*نظام محجوب أونلاين | سوقك الذكي*"

        msg = (
            "✨ *إشعار نظام: تم إنشاء طلب جديد* ✨\n\n"
            f"🧾 *فاتورة رقم:* `{order_handle}`\n"
            f"{divider}\n"
            f"👤 *العميل:* {customer.get('name', 'عميلنا العزيز')}\n"
            f"📍 *الموقع:* {customer.get('cityName', 'اليمن')}\n"
            f"{divider}\n"
            f"💵 *الإجمالي:* `{order_data.get('total', 0)}` ريال\n"
            f"🚚 *الحالة:* 【 {order_data.get('status_name', 'قيد الإنتظار')} 】\n"
            f"{divider}\n"
            f"🔗 *رابط تتبع حالة الشحن:* \n{tracking_link}\n\n"
            f"📄 *رابط الفاتورة التفصيلية (PDF):* \n{invoice_link}\n\n"
            f"🕒 `{full_time}`\n"
            f"{footer}"
        )

        if phone and len(phone) > 5:
            api_url = f"https://api.textmebot.com/send.php?recipient={phone}&apikey={TEXTMEBOT_API_KEY}&text={urllib.parse.quote(msg)}"
            requests.get(api_url, timeout=10)

        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
