from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    items = db.relationship('InvoiceItem', backref='invoice', cascade='all, delete-orphan')

    def subtotal(self):
        return sum(item.total() for item in self.items)

    def tax(self, tax_rate=0.0):
        return self.subtotal() * tax_rate

    def total(self, tax_rate=0.0):
        return self.subtotal() + self.tax(tax_rate)

class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    quantity = db.Column(db.Float, default=1)
    unit_price = db.Column(db.Float, default=0.0)

    def total(self):
        return (self.quantity or 0) * (self.unit_price or 0)
