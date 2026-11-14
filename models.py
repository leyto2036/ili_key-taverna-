"""SQLAlchemy models for Taverna Yamas."""
from datetime import datetime, timezone
from decimal import Decimal

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    orders = db.relationship("Order", back_populates="user", cascade="all, delete-orphan")
    reservations = db.relationship("Reservation", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    price = db.Column(db.Numeric(8, 2), nullable=False)
    image_url = db.Column(db.String(500), nullable=False, default="")
    is_available = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    status = db.Column(db.String(24), nullable=False, default="pending_payment")
    payment_status = db.Column(db.String(24), nullable=False, default="unpaid", index=True)
    payment_provider = db.Column(db.String(30), nullable=False, default="stripe")
    payment_session_id = db.Column(db.String(255), unique=True, nullable=True, index=True)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    discount = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    total = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default="EUR")
    pickup = db.Column(db.Boolean, nullable=False, default=True)
    telegram_status = db.Column(db.String(24), nullable=False, default="not_sent")
    telegram_error = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    paid_at = db.Column(db.DateTime(timezone=True), nullable=True)

    user = db.relationship("User", back_populates="orders")
    items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id", ondelete="CASCADE"), nullable=False, index=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey("menu_item.id", ondelete="SET NULL"), nullable=True)
    name = db.Column(db.String(160), nullable=False)  # Snapshot for order history.
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(8, 2), nullable=False)  # Price charged per unit after discounts.

    order = db.relationship("Order", back_populates="items")
    menu_item = db.relationship("MenuItem")


class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    reservation_date = db.Column(db.Date, nullable=False, index=True)
    reservation_time = db.Column(db.Time, nullable=False)
    guests = db.Column(db.Integer, nullable=False)
    zone = db.Column(db.String(16), nullable=False)  # indoor or terrace
    status = db.Column(db.String(24), nullable=False, default="confirmed", index=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    user = db.relationship("User", back_populates="reservations")


class ContentBlock(db.Model):
    """Saved custom description block, owned by the account that created it."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    text = db.Column(db.Text, nullable=False, default="")
    image_url = db.Column(db.String(500), nullable=True)
    position = db.Column(db.Integer, nullable=False, default=0)
    is_published = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    user = db.relationship("User")
