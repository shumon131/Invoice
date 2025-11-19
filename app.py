from flask import Flask, render_template, request, redirect, url_for, abort
from models import db, Invoice, InvoiceItem
import os

app = Flask(__name__)
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'invoices.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    invoices = Invoice.query.order_by(Invoice.id.desc()).all()
    return render_template('index.html', invoices=invoices)

@app.route('/invoice/new', methods=['GET', 'POST'])
def new_invoice():
    if request.method == 'POST':
        client_name = request.form.get('client_name', '').strip()
        date = request.form.get('date', '').strip()
        notes = request.form.get('notes', '').strip()
        items_text = request.form.get('items_text', '').strip()

        if not client_name:
            return "Client name is required", 400

        invoice = Invoice(client_name=client_name, date=date, notes=notes)
        db.session.add(invoice)
        db.session.flush()  # get invoice.id

        # items_text expected as lines: description,quantity,unit_price
        for line in items_text.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split(',')]
            # Flexible parsing
            description = parts[0] if len(parts) >= 1 else ''
            quantity = float(parts[1]) if len(parts) >= 2 and parts[1] else 1.0
            unit_price = float(parts[2]) if len(parts) >= 3 and parts[2] else 0.0
            item = InvoiceItem(invoice_id=invoice.id, description=description, quantity=quantity, unit_price=unit_price)
            db.session.add(item)

        db.session.commit()
        return redirect(url_for('view_invoice', invoice_id=invoice.id))

    # GET
    sample_items = "Design work,10,30\nConsulting,2,150"
    return render_template('new_invoice.html', sample_items=sample_items)

@app.route('/invoice/<int:invoice_id>')
def view_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    tax_rate = 0.0  # you can adjust or provide via query param
    return render_template('invoice.html', invoice=invoice, tax_rate=tax_rate)

if __name__ == '__main__':
    app.run(debug=True)
