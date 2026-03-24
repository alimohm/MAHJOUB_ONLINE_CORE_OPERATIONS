# أضف هذا الجزء في ملف app.py لصناعة الفاتورة برمجياً
from fpdf import FPDF

def create_real_pdf(order_handle, customer_name, total):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Invoice: {order_handle}", ln=1, align='C')
    pdf.cell(200, 10, txt=f"Customer: {customer_name}", ln=2, align='L')
    pdf.cell(200, 10, txt=f"Total: {total} YER", ln=3, align='L')
    file_path = f"order_{order_handle}.pdf"
    pdf.output(file_path)
    return file_path
