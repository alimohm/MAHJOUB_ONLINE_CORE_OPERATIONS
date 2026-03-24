import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- إعدادات حوكمة محجوب أونلاين ---
MAHJOUB_KEY = os.environ.get("MAHJOUB_ONLINE_KEY")
TEXTMEBOT_API_KEY = os.environ.get("TEXTMEBOT_KEY") # تأكد من إضافة هذا في Render
GRAPHQL_URL = "https://mahjoub.online/admin/graphql"

def send_whatsapp_notification(phone, message):
    """إرسال إشعار رسمي عبر واتساب محجوب أونلاين"""
    url = f"https://api.textmebot.com/send.php?recipient={phone}&apikey={TEXTMEBOT_API_KEY}&text={message}"
    requests.get(url)

def get_order_details(order_id):
    query = """
    query GetOrder($id: ID!) {
      order(id: $id) {
        handel
        priceWithShipping
        salesLead { firstName phone }
      }
    }
    """
    headers = {"Authorization": f"Bearer {MAHJOUB_KEY}", "Content-Type": "application/json"}
    response = requests.post(GRAPHQL_URL, json={'query': query, 'variables': {'id': order_id}}, headers=headers)
    return response.json().get('data', {}).get('order', {})

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    order_id = data.get('data', {}).get('id')
    event_type = data.get('event') # مثل order.updated أو order.created

    if order_id and event_type == "order.updated":
        order_info = get_order_details(order_id)
        
        if order_info:
            customer_name = order_info['salesLead']['firstName']
            customer_phone = order_info['salesLead']['phone']
            total_price = order_info['priceWithShipping']
            order_no = order_info['handel']

            # صياغة رسالة تليق بهوية محجوب أونلاين
            msg = f"عزيزي {customer_name}،\nتم تحديث حالة طلبك رقم #{order_no} بنجاح.\nإجمالي المبلغ: {total_price} YER.\nشكراً لثقتك بـ محجوب أونلاين."
            
            # تنفيذ الإرسال
            send_whatsapp_notification(customer_phone, msg)
            print(f"تم إرسال رسالة واتساب للعميل {customer_name}")

    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
