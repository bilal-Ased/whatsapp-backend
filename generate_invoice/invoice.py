from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

def generate_invoice(payment, tenant, property, lease=None):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "Payment Invoice")

    # Invoice details
    p.setFont("Helvetica", 12)
    y = height - 100
    p.drawString(50, y, f"Invoice #: {getattr(payment, 'id', 'N/A')}")
    p.drawString(50, y - 20, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    p.drawString(
        50, y - 40,
        f"Tenant: {getattr(tenant, 'first_name', '')} {getattr(tenant, 'last_name', '')}".strip()
    )
    p.drawString(
        50, y - 60,
        f"Property: {getattr(property, 'property_name', 'N/A')}, {getattr(property, 'address', 'N/A')}"
    )
    p.drawString(
        50, y - 80,
        f"Unit: {getattr(lease, 'unit_number', 'N/A')}" if lease else "Unit: N/A"
    )

    # Payment details
    y -= 120
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Payment Details")

    p.setFont("Helvetica", 12)
    p.drawString(50, y - 20, f"Amount: Ksh {getattr(payment, 'amount', 'N/A')}")
    p.drawString(50, y - 40, f"Method: {getattr(payment, 'payment_method', 'N/A')}")
    p.drawString(50, y - 60, f"Reference: {getattr(payment, 'transaction_reference', 'N/A')}")
    p.drawString(50, y - 80, f"Status: {getattr(payment, 'payment_status', 'N/A')}")

    # Footer
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(50, 50, "Thank you for your payment!")

    # Finalize PDF
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
