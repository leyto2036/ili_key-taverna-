"""Flask backend for Taverna Yamas. Payment success is trusted only after a verified Stripe webhook."""
from __future__ import annotations

import hashlib
import hmac
import os
import re
import time
from datetime import date, datetime, time as datetime_time, timezone
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from functools import wraps
from pathlib import Path

import requests
from flask import (Flask, abort, flash, jsonify, redirect, render_template,
                   render_template_string, request, session, url_for)
from flask_login import (LoginManager, current_user, login_required, login_user,
                         logout_user)
from flask_wtf.csrf import CSRFProtect, generate_csrf
from werkzeug.utils import secure_filename

from extensions import db
from models import ContentBlock, MenuItem, Order, OrderItem, Reservation, User

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-this-secret-key"),
    SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", "sqlite:///taverna.db"),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    MAX_CONTENT_LENGTH=8 * 1024 * 1024,
    UPLOAD_FOLDER=str(BASE_DIR / "static" / "uploads"),
    WTF_CSRF_TIME_LIMIT=3600,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1",
)
db.init_app(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Please sign in to continue."

TRANSLATIONS = {
    'de': {
        'title': 'Taverna Yamas | Griechisches Restaurant in München',
        'subtitle': 'Traditionelle griechische Küche im Herzen von München',
        'about_title': 'Taverna Yamas München',
        'about_text': 'Willkommen in der Taverna Yamas! Genießen Sie authentische griechische Spezialitäten, frisch zubereitete Grillgerichte und erlesene Weine in gemütlicher Atmosphäre im Herzen von München.',
        'address_label': 'Dollmannstr. 27, 81541 München',
        'menu_btn': 'Speisekarte öffnen',
        'menu_photos_btn': 'Speisekarte Fotos',
        'menu_title': 'Unsere Speisekarte',
        'order_btn': 'Essen bestellen',
        'to_order': 'Bestellen',
        'back_to_menu': 'Zurück',
        'tables_btn': '🪑 Innen: 5/10 | Terrasse: 5/10 frei',
        'tables_edit': 'Plätze bearbeiten',
        'tables_modal_title': 'Tischreservierung & Verwaltung',
        'tables_info': 'Innenbereich: 10 Tische (5 frei). Außen / Terrasse: 10 Tische (5 frei).',
        'date_label': 'Datum',
        'time_label': 'Uhrzeit',
        'persons_label': 'Personenanzahl',
        'reserve_submit': 'Verbindlich reservieren',
        'reserve_success': 'Vielen Dank! Ihre Reservierung war erfolgreich.',
        'order_modal_title': 'Wählen Sie Ihre Bestellmethode',
        'pickup_title': 'Selbstabholung (-10%)',
        'pickup_sub': 'Abholung in ca. 20–25 Min. Telefon: 089 4483787',
        'partners_title': 'Oder über Lieferpartner:',
        'clipboard_copied': 'Bestellung in die Zwischenablage kopiert!',
        'delivery_info': 'Lieferinformationen',
        'min_order': 'Mindestbestellwert:',
        'del_cost': 'Lieferkosten:',
        'del_time': 'Ca. Lieferzeit:',
        'min_unit': 'Min.',
        'pcs_unit': 'Stk.',
        'cart_title': 'Warenkorb',
        'cart_empty': 'Ihr Warenkorb ist leer',
        'total_sum': 'Gesamtsumme:',
        'checkout_btn': 'Bestellung absenden',
        'sidebar_header': 'Information & Impressum',
        'toggle_tools': '🛠️ Editor-Werkzeuge umschalten',
        'block_btn': '+ Block',
        'hours_title': 'Öffnungszeiten',
        'hours_mon': 'Mo: Geschlossen',
        'hours_tue': 'Di - Do: 11:00–14:00, 17:00–23:00',
        'hours_fri': 'Fr - So: 11:00–23:00 (durchgehend)',
        'contact_venue': 'Kontakt zum Restaurant',
        'contact_dev': 'Kontakt zum Entwickler',
        'legal_title': 'Impressum & Rechtliches (DSGVO)',
        'legal_name': 'Taverna Yamas GmbH',
        'legal_address': 'Dollmannstr. 27, 81541 München',
        'legal_tax': 'Steuernummer: 145/205/01127',
        'privacy_policy': 'Datenschutzerklärung',
        'dev_by': 'Developed by ili key'
    },
    'en': {
        'title': 'Taverna Yamas | Greek Restaurant in Munich',
        'subtitle': 'Traditional Greek cuisine in the heart of Munich',
        'about_title': 'Taverna Yamas Munich',
        'about_text': 'Welcome to Taverna Yamas! Enjoy authentic Greek specialties, freshly grilled dishes, and fine wines in a cozy atmosphere in the heart of Munich.',
        'address_label': 'Dollmannstr. 27, 81541 München',
        'menu_btn': 'Open Menu',
        'menu_photos_btn': 'Menu Photos',
        'menu_title': 'Our Menu',
        'order_btn': 'Order Food',
        'to_order': 'Order',
        'back_to_menu': 'Back',
        'tables_btn': '🪑 Indoor: 5/10 | Terrace: 5/10 free',
        'tables_edit': 'Edit seats',
        'tables_modal_title': 'Table Reservation & Management',
        'tables_info': 'Indoor: 10 tables (5 free). Terrace: 10 tables (5 free).',
        'date_label': 'Date',
        'time_label': 'Time',
        'persons_label': 'Number of guests',
        'reserve_submit': 'Book Table',
        'reserve_success': 'Thank you! Your reservation was successful.',
        'order_modal_title': 'Select Ordering Method',
        'pickup_title': 'Self-Pickup (-10%)',
        'pickup_sub': 'Ready in ~20–25 min. Phone: 089 4483787',
        'partners_title': 'Or via delivery partners:',
        'clipboard_copied': 'Order copied to clipboard!',
        'delivery_info': 'Delivery Information',
        'min_order': 'Min. order:',
        'del_cost': 'Delivery fee:',
        'del_time': 'Est. delivery time:',
        'min_unit': 'min',
        'pcs_unit': 'pcs',
        'cart_title': 'Cart',
        'cart_empty': 'Your cart is empty',
        'total_sum': 'Total:',
        'checkout_btn': 'Send Order',
        'sidebar_header': 'Information & Impressum',
        'toggle_tools': '🛠️ Toggle Editor Tools',
        'block_btn': '+ Block',
        'hours_title': 'Opening Hours',
        'hours_mon': 'Mon: Closed',
        'hours_tue': 'Tue - Thu: 11:00–14:00, 17:00–23:00',
        'hours_fri': 'Fri - Sun: 11:00–23:00 (non-stop)',
        'contact_venue': 'Contact Venue',
        'contact_dev': 'Contact Developer',
        'legal_title': 'Impressum & Legal Info',
        'legal_name': 'Taverna Yamas GmbH',
        'legal_address': 'Dollmannstr. 27, 81541 München',
        'legal_tax': 'Steuernummer: 145/205/01127',
        'privacy_policy': 'Privacy Policy (DSGVO)',
        'dev_by': 'Developed by ili key'
    },
    'ru': {
        'title': 'Taverna Yamas | Греческий ресторан в Мюнхене',
        'subtitle': 'Традиционная греческая кухня в сердце Мюнхена',
        'about_title': 'Taverna Yamas München',
        'about_text': 'Добро пожаловать в Таверну Ямас! Насладитесь аутентичными греческими блюдами, свежими кушаньями на гриле и уютной атмосферой в самом центре Мюнхена.',
        'address_label': 'Dollmannstr. 27, 81541 München',
        'menu_btn': 'Открыть меню',
        'menu_photos_btn': 'Фото меню',
        'menu_title': 'Наше меню',
        'order_btn': 'Заказать еду',
        'to_order': 'Заказать',
        'back_to_menu': 'Назад',
        'tables_btn': '🪑 В зале: 5/10 | Терраса: 5/10 свободно',
        'tables_edit': 'Изменить места',
        'tables_modal_title': 'Бронирование столиков и управление',
        'tables_info': 'В зале: 10 столов (свободно 5). На улице (терраса): 10 столов (свободно 5).',
        'date_label': 'Дата',
        'time_label': 'Время',
        'persons_label': 'Количество гостей',
        'reserve_submit': 'Забронировать столик',
        'reserve_success': 'Спасибо! Бронирование успешное, мы с вами свяжемся в ближайшее время.',
        'order_modal_title': 'Выберите способ заказа',
        'pickup_title': 'Самовывоз (-10%)',
        'pickup_sub': 'Готовность через ~20-25 мин. Телефон: 089 4483787',
        'partners_title': 'Или через партнеров доставки:',
        'clipboard_copied': 'Состав заказа скопирован в буфер обмена!',
        'delivery_info': 'Информация о доставке',
        'min_order': 'Мин. сумма:',
        'del_cost': 'Стоимость доставки:',
        'del_time': 'Время доставки:',
        'min_unit': 'мин',
        'pcs_unit': 'шт.',
        'cart_title': 'Корзина заказа',
        'cart_empty': 'Корзина пуста',
        'total_sum': 'Итого к оплате:',
        'checkout_btn': 'Оформить заказ',
        'sidebar_header': 'Информация и Impressum',
        'toggle_tools': '🛠️ Включить/Выключить инструменты',
        'block_btn': '+ Блок',
        'hours_title': 'График работы',
        'hours_mon': 'Пн: Закрыто',
        'hours_tue': 'Вт - Чт: 11:00–14:00, 17:00–23:00',
        'hours_fri': 'Пт - Вс: 11:00–23:00 (без перерыва)',
        'contact_venue': 'Связь с заведением',
        'contact_dev': 'Связь с разработчиком',
        'legal_title': 'Impressum & Юр. информация (DSGVO)',
        'legal_name': 'Taverna Yamas GmbH',
        'legal_address': 'Dollmannstr. 27, 81541 München',
        'legal_tax': 'Steuernummer: 145/205/01127',
        'privacy_policy': 'Политика конфиденциальности (DSGVO)',
        'dev_by': 'Developed by ili key'
    }
}

MENU_ITEMS = [
    {"id": 1, "name": "Gyros Plate", "desc": "Zartes Fleisch vom Spieß mit Tzatziki, Pommes und Salat.", "price": "15.90 €", "img": "/static/images/dishes/WhatsApp Image 20-04-23 at 19.26.48.jpeg", "demand": 100},
    {"id": 2, "name": "Souvlaki Spieße", "desc": "Gegrillte Fleischspieße nach traditioneller Art mit Kräutern.", "price": "14.90 €", "img": "/static/images/dishes/WhatsApp Image 202-04-23 at 19.26.48.jpeg", "demand": 95},
    {"id": 3, "name": "Moussaka Classic", "desc": "Traditioneller Auflauf mit Auberginen, Hackfleisch und Béchamelsauce.", "price": "16.20 €", "img": "/static/images/dishes/WhatsApp Image 2026-0-23 at 19.26.48.jpeg", "demand": 90},
    {"id": 4, "name": "Bifteki Feta", "desc": "Gefülltes Hacksteak mit Schafskäse, dazu aromatischer Reis.", "price": "15.50 €", "img": "/static/images/dishes/WhatsApp Image 2026-04 at 19.26.48.jpeg", "demand": 85},
    {"id": 5, "name": "Griechischer Bauernsalat", "desc": "Tomaten, Gurken, Oliven, original Schafskäse und Olivenöl.", "price": "9.90 €", "img": "/static/images/dishes/WhatsApp Image 2026-04-2 at 19.26.48.jpeg", "demand": 80},
    {"id": 6, "name": "Tzatziki & Warme Pita", "desc": "Hausgemachter Joghurtdip mit frischem Knoblauch und Pita.", "price": "5.90 €", "img": "/static/images/dishes/WhatsApp Image 2026-04-23 at 1.26.48.jpeg", "demand": 75},
    {"id": 7, "name": "Suflaki Special", "desc": "Zarte Spieße vom Grill mit Spezialmarinade.", "price": "16.50 €", "img": "/static/images/dishes/WhatsApp Image 2026-04-23 at 19.26.4.jpeg", "demand": 70},
    {"id": 8, "name": "Keftedakia", "desc": "Griechische Hackbällchen in Tomatensoße.", "price": "12.90 €", "img": "/static/images/dishes/WhatsApp Image 2026-04-23 at 19.26.47.jpeg", "demand": 65},
    {"id": 9, "name": "Bifteki Special", "desc": "Gegrilltes Hacksteak mit Kräuterbutter.", "price": "14.50 €", "img": "/static/images/dishes/WhatsApp Image 2026-04-23 at 19.26.48.jpeg", "demand": 60},
    {"id": 10, "name": "Calamares", "desc": "Knusprig frittierte Tintenfischringe mit Zitrone und Aioli.", "price": "16.90 €", "img": "/static/images/dishes/WhatsApp Image 2026-04-23 at 19.26.jpeg", "demand": 55},
    {"id": 11, "name": "Exklusiver Grillteller", "desc": "Auswahl an verschiedenen Fleischsorten vom Grill.", "price": "19.90 €", "img": "/static/images/dishes/WhatsApp Image 2026-04-23 at 19.6.48.jpeg", "demand": 50},
    {"id": 12, "name": "Gyros Special", "desc": "Gyros mit Metaxasoße und Käse überbacken.", "price": "17.20 €", "img": "/static/images/dishes/WhatsApp Image 2026-04-23 at 9.26.48.jpeg", "demand": 45},
    {"id": 13, "name": "Gemista", "desc": "Gefüllte Tomaten und Paprika mit Reis und Kräutern.", "price": "13.90 €", "img": "/static/images/dishes/WhatsApp Image 2026-4-23 at 19.26.48.jpeg", "demand": 40},
    {"id": 14, "name": "Santorini Platte", "desc": "Große Auswahl für 2 Personen mit diversen Spezialitäten.", "price": "36.00 €", "img": "/static/images/dishes/WhatsApp Image 206-04-23 at 19.26.48.jpeg", "demand": 35},
    {"id": 15, "name": "Greek Dessert", "desc": "Traditionelles Gebäck mit Honig und Nüssen.", "price": "6.50 €", "img": "/static/images/dishes/WhatsApp Image 26-04-23 at 19.26.48.jpeg", "demand": 30}
]
MENU_IMAGES = [
    "/static/images/menu/photo_2026-04-26_17-39-45.jpg",
    "/static/images/menu/photo_2026-04-26_17-39-47.jpg",
    "/static/images/menu/photo_2026-04-26_17-39-49.jpg",
    "/static/images/menu/photo_2026-04-26_17-39-51.jpg",
    "/static/images/menu/photo_2026-04-26_17-39-53.jpg",
    "/static/images/menu/photo_2026-04-26_17-39-56.jpg",
    "/static/images/menu/photo_2026-04-27_14-07-52 (2).jpg",
]
LINKS = {
    "maps": "https://www.google.com/maps/place//data=!4m2!3m1!19sChIJoaYxZBTfnUcRTbUsyCEoArQ",
    "lieferando": "https://www.lieferando.de/en/menu/taverna-yamas-munchen",
    "wolt": "https://wolt.com/de/deu/munich/restaurant/taverna-yamas-dstr",
    "uber": "https://www.ubereats.com/de/store/taverna-yamas",
    "uber_code": "eats-34arbu6yk1", "phone": "tel:+49894483787",
}

TRANSLATIONS = {
    "de": {"title":"Taverna Yamas | Griechisches Restaurant in München", "subtitle":"Traditionelle griechische Küche im Herzen von München", "about_title":"Taverna Yamas München", "about_text":"Willkommen in der Taverna Yamas! Genießen Sie authentische griechische Spezialitäten, frisch zubereitete Grillgerichte und erlesene Weine in gemütlicher Atmosphäre im Herzen von München.", "address_label":"Dollmannstr. 27, 81541 München", "menu_btn":"Speisekarte öffnen", "menu_photos_btn":"Speisekarte Fotos", "menu_title":"Unsere Speisekarte", "order_btn":"Essen bestellen", "to_order":"Bestellen", "back_to_menu":"Zurück", "tables_btn":"🪑 Innen: 5/10 | Terrasse: 5/10 frei", "tables_edit":"Plätze bearbeiten", "tables_modal_title":"Tischreservierung & Verwaltung", "tables_info":"Innenbereich: 10 Tische (5 frei). Außen / Terrasse: 10 Tische (5 frei).", "date_label":"Datum", "time_label":"Uhrzeit", "persons_label":"Personenanzahl", "reserve_submit":"Verbindlich reservieren", "reserve_success":"Vielen Dank! Ihre Reservierung war erfolgreich.", "order_modal_title":"Wählen Sie Ihre Bestellmethode", "pickup_title":"Selbstabholung (-10%)", "pickup_sub":"Abholung in ca. 20–25 Min. Telefon: 089 4483787", "partners_title":"Oder über Lieferpartner:", "clipboard_copied":"Bestellung in die Zwischenablage kopiert!", "delivery_info":"Lieferinformationen", "min_order":"Mindestbestellwert:", "del_cost":"Lieferkosten:", "del_time":"Ca. Lieferzeit:", "min_unit":"Min.", "pcs_unit":"Stk.", "cart_title":"Warenkorb", "cart_empty":"Ihr Warenkorb ist leer", "total_sum":"Gesamtsumme:", "checkout_btn":"Bestellung absenden", "sidebar_header":"Information & Impressum", "toggle_tools":"🛠️ Editor-Werkzeuge umschalten", "block_btn":"+ Block", "hours_title":"Öffnungszeiten", "hours_mon":"Mo: Geschlossen", "hours_tue":"Di - Do: 11:00–14:00, 17:00–23:00", "hours_fri":"Fr - So: 11:00–23:00 (durchgehend)", "contact_venue":"Kontakt zum Restaurant", "contact_dev":"Kontakt zum Entwickler", "legal_title":"Impressum & Rechtliches (DSGVO)", "legal_name":"Taverna Yamas GmbH", "legal_address":"Dollmannstr. 27, 81541 München", "legal_tax":"Steuernummer: 145/205/01127", "privacy_policy":"Datenschutzerklärung", "dev_by":"Developed by ili key", "reserve_btn": "Reservierung", "clear_cart_btn": "Warenkorb leeren", "sort_label": "Sortieren & Filtern", "cat_food": "Essen", "cat_drinks": "Getränke", "cat_sauces": "Soßen & Dip"},
    "en": {"title":"Taverna Yamas | Greek Restaurant in Munich", "subtitle":"Traditional Greek cuisine in the heart of Munich", "about_title":"Taverna Yamas Munich", "about_text":"Welcome to Taverna Yamas! Enjoy authentic Greek specialties, freshly grilled dishes, and fine wines in a cozy atmosphere in the heart of Munich.", "address_label":"Dollmannstr. 27, 81541 München", "menu_btn":"Open Menu", "menu_photos_btn":"Menu Photos", "menu_title":"Our Menu", "order_btn":"Order Food", "to_order":"Order", "back_to_menu":"Back", "tables_btn":"🪑 Indoor: 5/10 | Terrace: 5/10 free", "tables_edit":"Edit seats", "tables_modal_title":"Table Reservation & Management", "tables_info":"Indoor: 10 tables (5 free). Terrace: 10 tables (5 free).", "date_label":"Date", "time_label":"Time", "persons_label":"Number of guests", "reserve_submit":"Book Table", "reserve_success":"Thank you! Your reservation was successful.", "order_modal_title":"Select Ordering Method", "pickup_title":"Self-Pickup (-10%)", "pickup_sub":"Ready in ~20–25 min. Phone: 089 4483787", "partners_title":"Or via delivery partners:", "clipboard_copied":"Order copied to the clipboard!", "delivery_info":"Delivery Information", "min_order":"Min. order:", "del_cost":"Delivery fee:", "del_time":"Est. delivery time:", "min_unit":"min", "pcs_unit":"pcs", "cart_title":"Cart", "cart_empty":"Your cart is empty", "total_sum":"Total:", "checkout_btn":"Send Order", "sidebar_header":"Information & Impressum", "toggle_tools":"🛠️ Toggle Editor Tools", "block_btn":"+ Block", "hours_title":"Opening Hours", "hours_mon":"Mon: Closed", "hours_tue":"Tue - Thu: 11:00–14:00, 17:00–23:00", "hours_fri":"Fri - Sun: 11:00–23:00 (non-stop)", "contact_venue":"Contact Venue", "contact_dev":"Contact Developer", "legal_title":"Impressum & Legal Info", "legal_name":"Taverna Yamas GmbH", "legal_address":"Dollmannstr. 27, 81541 München", "legal_tax":"Steuernummer: 145/205/01127", "privacy_policy":"Privacy Policy (DSGVO)", "dev_by":"Developed by ili key"},
    "ru": {"title":"Taverna Yamas | Греческий ресторан в Мюнхене", "subtitle":"Традиционная греческая кухня в сердце Мюнхена", "about_title":"Taverna Yamas München", "about_text":"Добро пожаловать в Таверну Ямас! Насладитесь аутентичными греческими блюдами и уютной атмосферой в самом сердце Мюнхена.", "address_label":"Dollmannstr. 27, 81541 München", "menu_btn":"Открыть меню", "menu_photos_btn":"Фото меню", "menu_title":"Наше меню", "order_btn":"Заказать еду", "to_order":"Заказать", "back_to_menu":"Назад", "tables_btn":"🪑 В зале: 5/10 | Терраса: 5/10 свободно", "tables_edit":"Изменить места", "tables_modal_title":"Бронирование столика и управление", "tables_info":"В зале: 10 столов (свободно 5). На террасе: 10 столов (свободно 5).", "date_label":"Дата", "time_label":"Время", "persons_label":"Количество гостей", "reserve_submit":"Забронировать столик", "reserve_success":"Спасибо! Бронирование успешно.", "order_modal_title":"Выберите способ заказа", "pickup_title":"Самовывоз (-10%)", "pickup_sub":"Готовность через ~20–25 мин. Телефон: 089 4483787", "partners_title":"Или через партнеров доставки:", "clipboard_copied":"Заказ скопирован в буфер обмена!", "delivery_info":"Информация о доставке", "min_order":"Мин. сумма:", "del_cost":"Стоимость доставки:", "del_time":"Время доставки:", "min_unit":"мин", "pcs_unit":"шт.", "cart_title":"Корзина заказа", "cart_empty":"Корзина пуста", "total_sum":"Итого к оплате:", "checkout_btn":"Оформить заказ", "sidebar_header":"Информация и Impressum", "toggle_tools":"🛠️ Включить/Выключить инструменты", "block_btn":"+ Блок", "hours_title":"График работы", "hours_mon":"Пн: Закрыто", "hours_tue":"Вт - Чт: 11:00–14:00, 17:00–23:00", "hours_fri":"Пт - Вс: 11:00–23:00 (без перерыва)", "contact_venue":"Связь с заведением", "contact_dev":"Связь с разработчиком", "legal_title":"Impressum & Юр. информация (DSGVO)", "legal_name":"Taverna Yamas GmbH", "legal_address":"Dollmannstr. 27, 81541 München", "legal_tax":"Steuernummer: 145/205/01127", "privacy_policy":"Политика конфиденциальности (DSGVO)", "dev_by":"Developed by ili key"},
        "mode_food": "Essen",
        "mode_drinks": "Getränke",
        "mode_pizza": "Pizza",
        "mode_pasta": "Pasta",
        "mode_sauces": "Soßen & Dips",
        "cart_choose_method": "Selbstabholung (-10%) oder über Lieferplattformen bestellen?"
    }

@login_manager.user_loader
def load_user(user_id: str):
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None

@app.context_processor
def inject_globals():
    lang = session.get("lang", "de")
    if lang not in TRANSLATIONS:
        lang = "de"
    items = MenuItem.query.order_by(MenuItem.id).all()
    menu = [{"id": i.id, "name": i.name, "desc": i.description,
             "price": f"{i.price:.2f} €", "img": i.image_url} for i in items]
    return {"t": TRANSLATIONS[lang], "current_lang": lang, "menu": menu,
            "menu_images": MENU_IMAGES, "links": LINKS, "csrf_token": generate_csrf}

@app.template_filter("money")
def money(value):
    return f"€{Decimal(value):.2f}"

@app.route("/")
def index():
    return render_template('index.html')
@app.route('/about')
def about():
    return render_template('about.html')

@app.route("/set_language/<lang>")
def set_language(lang):
    if lang in TRANSLATIONS:
        session["lang"] = lang
    return redirect(request.referrer or url_for("index"))

AUTH_TEMPLATE = """<!doctype html><html lang='en'><meta charset='utf-8'><meta name='viewport' content='width=device-width'><title>{{ title }}</title><body><main style='max-width:440px;margin:4rem auto;font:16px sans-serif'><h1>{{ title }}</h1>{% with messages=get_flashed_messages() %}{% for message in messages %}<p role='alert'>{{ message }}</p>{% endfor %}{% endwith %}<form method='post'><input type='hidden' name='csrf_token' value='{{ csrf_token() }}'>{{ fields|safe }}<button type='submit'>{{ submit }}</button></form><p><a href='{{ url_for("index") }}'>Taverna Yamas</a></p></main></body></html>"""

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('account'))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if len(username) < 2 or len(username) > 80 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            flash("Enter a valid username and email address.")
        elif len(password) < 10:
            flash("Password must be at least 10 characters long.")
        elif User.query.filter(db.or_(User.username == username, User.email == email)).first():
            flash("That username or email is already registered.")
        else:
            user = User(username=username, email=email,
                        is_admin=bool(os.environ.get("ADMIN_EMAIL")) and email == os.environ.get("ADMIN_EMAIL", "").lower())
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('account'))
    fields = "<label>Username <input name='username' required minlength='2' maxlength='80'></label><br><label>Email <input type='email' name='email' required maxlength='254'></label><br><label>Password <input type='password' name='password' required minlength='10' autocomplete='new-password'></label>"
    return render_template_string(AUTH_TEMPLATE, title="Create account", fields=fields, submit="Register")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('account'))
    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        user = User.query.filter(db.or_(User.email == identifier.lower(), User.username == identifier)).first()
        if user and user.check_password(request.form.get("password", "")):
            login_user(user, remember=bool(request.form.get("remember")))
            return redirect(request.args.get("next") if request.args.get("next", "").startswith("/") else url_for('account'))
        flash("Invalid username/email or password.")
    fields = "<label>Username or email <input name='identifier' required autocomplete='username'></label><br><label>Password <input type='password' name='password' required autocomplete='current-password'></label><br><label><input type='checkbox' name='remember'> Remember me</label>"
    return render_template_string(AUTH_TEMPLATE, title="Sign in", fields=fields, submit="Login")

@app.post("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/account")
@login_required
def account():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    reservations = Reservation.query.filter_by(user_id=current_user.id).order_by(Reservation.reservation_date.desc()).all()
    return render_template_string("""<!doctype html><meta charset='utf-8'><title>My account</title><h1>My account</h1><p>{{ user.username }} · {{ user.email }}</p><form method='post' action='{{ url_for("logout") }}'><input type='hidden' name='csrf_token' value='{{ csrf_token() }}'><button>Log out</button></form><h2>Orders</h2>{% for o in orders %}<p>Order #{{ o.id }} — {{ o.status }} / {{ o.payment_status }} — {{ o.total|money }}{% for item in o.items %}<br>{{ item.quantity }} × {{ item.name }}{% endfor %}</p>{% else %}<p>No orders yet.</p>{% endfor %}<h2>Reservations</h2>{% for r in reservations %}<p>{{ r.reservation_date }} {{ r.reservation_time }} · {{ r.guests }} guests · {{ r.zone }} — {{ r.status }}</p>{% else %}<p>No reservations yet.</p>{% endfor %}<p><a href='{{ url_for("index") }}'>Back to restaurant</a></p>""", user=current_user, orders=orders, reservations=reservations)

@app.post("/api/reservations")
@login_required
def create_reservation():
    data = request.get_json(silent=True) or request.form
    try:
        reservation_date = date.fromisoformat(data.get("date", ""))
        reservation_time = datetime_time.fromisoformat(data.get("time", ""))
        guests = int(data.get("guests", data.get("persons", "")))
    except (TypeError, ValueError):
        return jsonify(error="Provide valid date, time and guest count."), 400
    zone = data.get("zone", "indoor")
    if reservation_date < date.today() or not 1 <= guests <= 10 or zone not in {"indoor", "terrace"}:
        return jsonify(error="Date, guest count or zone is invalid."), 400
    reservation = Reservation(user_id=current_user.id, reservation_date=reservation_date,
                              reservation_time=reservation_time, guests=guests, zone=zone)
    db.session.add(reservation)
    db.session.commit()
    return jsonify(id=reservation.id, status=reservation.status), 201

@app.get("/api/reservations/availability")
def reservation_availability():
    """Return a simple daily seat counter; reservations are counted against 10 tables per zone."""
    try:
        day = date.fromisoformat(request.args.get("date", date.today().isoformat()))
    except ValueError:
        return jsonify(error="Invalid date."), 400
    occupied = {zone: Reservation.query.filter_by(reservation_date=day, zone=zone, status="confirmed").count()
                for zone in ("indoor", "terrace")}
    return jsonify(date=day.isoformat(), indoor_free=max(0, 10 - occupied["indoor"]),
                   terrace_free=max(0, 10 - occupied["terrace"]))

@app.get("/api/csrf-token")
def csrf_token_endpoint():
    return jsonify(csrf_token=generate_csrf())

@app.post("/api/checkout")
@login_required
def create_checkout():
    """Create a pending order and Stripe Checkout session; never marks it paid."""
    stripe_key = os.environ.get("STRIPE_SECRET_KEY")
    if not stripe_key:
        return jsonify(error="Online payment is not configured."), 503
    data = request.get_json(silent=True) or request.form
    raw_items = data.get("items", [])
    if isinstance(raw_items, str):
        try:
            import json
            raw_items = json.loads(raw_items)
        except (ValueError, TypeError):
            return jsonify(error="Items must be a list."), 400
    if not isinstance(raw_items, list) or not raw_items or len(raw_items) > 30:
        return jsonify(error="Cart is empty or too large."), 400
    quantity_by_id = {}
    try:
        for entry in raw_items:
            item_id = int(entry.get("id"))
            quantity = int(entry.get("quantity", entry.get("qty", 0)))
            if quantity < 1 or quantity > 50:
                raise ValueError
            quantity_by_id[item_id] = quantity_by_id.get(item_id, 0) + quantity
    except (AttributeError, TypeError, ValueError):
        return jsonify(error="Invalid cart item."), 400
    menu_items = {item.id: item for item in MenuItem.query.filter(MenuItem.id.in_(quantity_by_id), MenuItem.is_available.is_(True)).all()}
    if set(menu_items) != set(quantity_by_id):
        return jsonify(error="One or more menu items are unavailable."), 400
    pickup = str(data.get("pickup", "true")).lower() not in {"false", "0", "no"}
    subtotal = sum((Decimal(menu_items[i].price) * qty for i, qty in quantity_by_id.items()), Decimal("0")).quantize(CENT)
    discount = (subtotal * PICKUP_DISCOUNT).quantize(CENT, rounding=ROUND_HALF_UP) if pickup else Decimal("0.00")
    total = subtotal - discount
    if total <= 0:
        return jsonify(error="Order total must be positive."), 400
    order = Order(user_id=current_user.id, subtotal=subtotal, discount=discount, total=total,
                  pickup=pickup, status="pending_payment", payment_status="unpaid")
    db.session.add(order)
    db.session.flush()
    for item_id, quantity in quantity_by_id.items():
        item = menu_items[item_id]
        unit = Decimal(item.price)
        if pickup:
            unit = (unit * (Decimal("1") - PICKUP_DISCOUNT)).quantize(CENT, rounding=ROUND_HALF_UP)
        db.session.add(OrderItem(order=order, menu_item_id=item.id, name=item.name,
                                 quantity=quantity, unit_price=unit))
    db.session.commit()
    # Stripe receives the server-calculated final amount; client-supplied prices are ignored.
    success_url = url_for("payment_success", order_id=order.id, _external=True) + "?session_id={CHECKOUT_SESSION_ID}"
    cancel_url = url_for("payment_cancel", order_id=order.id, _external=True)
    payload = {
        "mode": "payment", "success_url": success_url, "cancel_url": cancel_url,
        "customer_email": current_user.email,
        "client_reference_id": str(order.id),
        "metadata[order_id]": str(order.id),
        "line_items[0][price_data][currency]": "eur",
        "line_items[0][price_data][unit_amount]": str(int(total * 100)),
        "line_items[0][price_data][product_data][name]": f"Taverna Yamas order #{order.id}" + (" (10% pickup discount)" if pickup else ""),
        "line_items[0][quantity]": "1",
    }
    try:
        response = requests.post("https://api.stripe.com/v1/checkout/sessions", data=payload,
                                 auth=(stripe_key, ""), timeout=15)
        response.raise_for_status()
        stripe_session = response.json()
        if not stripe_session.get("id") or not stripe_session.get("url"):
            raise ValueError("Stripe did not return a checkout session.")
        order.payment_session_id = stripe_session["id"]
        db.session.commit()
    except (requests.RequestException, ValueError, KeyError) as exc:
        app.logger.exception("Stripe checkout creation failed for order %s", order.id)
        order.status = "payment_setup_failed"
        db.session.commit()
        return jsonify(error="Could not start secure checkout. Please try again."), 502
    return jsonify(order_id=order.id, checkout_url=stripe_session["url"]), 201

@app.get("/payment/success/<int:order_id>")
@login_required
def payment_success(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    # A browser redirect is not proof of payment. The verified webhook updates the order.
    return render_template_string("<h1>Payment processing</h1><p>Order #{{ order.id }} status: {{ order.payment_status }}. Please refresh your account in a moment.</p><a href='{{ url_for('account') }}'>My account</a>", order=order)

@app.get("/payment/cancel/<int:order_id>")
@login_required
def payment_cancel(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    if order.payment_status != "paid":
        order.status = "payment_cancelled"
        db.session.commit()
    return redirect(url_for('account'))

def valid_stripe_signature(payload: bytes, header: str, secret: str, tolerance: int = 300) -> bool:
    timestamp = None
    signatures = []
    for part in header.split(","):
        key, sep, value = part.partition("=")
        if sep and key == "t":
            timestamp = value
        elif sep and key == "v1":
            signatures.append(value)
    try:
        stamp = int(timestamp or "")
    except ValueError:
        return False
    if abs(int(time.time()) - stamp) > tolerance:
        return False
    signed_payload = f"{stamp}.".encode("ascii") + payload
    expected = hmac.new(secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()
    return any(hmac.compare_digest(expected, signature) for signature in signatures)

@csrf.exempt
@app.post("/payments/stripe/webhook")
def stripe_webhook():
    secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
    signature = request.headers.get("Stripe-Signature", "")
    raw = request.get_data(cache=False)
    if not secret or not valid_stripe_signature(raw, signature, secret):
        return jsonify(error="Invalid webhook signature."), 400
    try:
        event = request.get_json(force=True)
        event_type = event.get("type")
        checkout = event.get("data", {}).get("object", {})
    except (ValueError, AttributeError):
        return jsonify(error="Malformed event."), 400
    if event_type not in {"checkout.session.completed", "checkout.session.async_payment_succeeded"}:
        return jsonify(received=True)
    if checkout.get("payment_status") != "paid":
        return jsonify(received=True)
    try:
        order_id = int(checkout.get("metadata", {}).get("order_id", ""))
    except (TypeError, ValueError):
        return jsonify(error="Missing order reference."), 400
    order = db.session.get(Order, order_id)
    if not order or order.payment_session_id != checkout.get("id"):
        return jsonify(error="Unknown checkout session."), 400
    if checkout.get("currency", "").lower() != "eur" or int(checkout.get("amount_total", -1)) != int(order.total * 100):
        return jsonify(error="Payment amount or currency does not match order."), 400
    if order.payment_status != "paid":
        order.payment_status = "paid"
        order.status = "paid"
        order.paid_at = datetime.now(timezone.utc)
        db.session.commit()
    if order.telegram_status != "sent":
        notify_restaurant_telegram(order)
    return jsonify(received=True)

def notify_restaurant_telegram(order: Order) -> bool:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        order.telegram_status = "not_configured"
        order.telegram_error = "Telegram bot credentials are not configured."
        db.session.commit()
        app.logger.error("Telegram notification is not configured for paid order %s", order.id)
        return False
    item_lines = [f"• {item.name} × {item.quantity} — €{Decimal(item.unit_price) * item.quantity:.2f}" for item in order.items]
    message = (f"✅ PAID ORDER #{order.id}\nCustomer: {order.user.username} ({order.user.email})\n"
               f"Pickup: {'Yes' if order.pickup else 'No'}\n" + "\n".join(item_lines) +
               f"\nSubtotal: €{order.subtotal:.2f}\nDiscount: €{order.discount:.2f}\nTOTAL PAID: €{order.total:.2f}")
    try:
        response = requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                                 json={"chat_id": chat_id, "text": message}, timeout=10)
        response.raise_for_status()
        result = response.json()
        if not result.get("ok"):
            raise RuntimeError("Telegram API rejected the message.")
        order.telegram_status = "sent"
        order.telegram_error = None
        db.session.commit()
        return True
    except (requests.RequestException, ValueError, RuntimeError) as exc:
        order.telegram_status = "failed"
        order.telegram_error = str(exc)[:500]
        db.session.commit()
        app.logger.exception("Telegram notification failed for paid order %s", order.id)
        return False

@app.post("/api/content-blocks")
@login_required
def save_content_block():
    data = request.get_json(silent=True) or request.form
    text = str(data.get("text", "")).strip()
    if len(text) > 10000:
        return jsonify(error="Block text is too long."), 400
    block = ContentBlock(user_id=current_user.id, text=text,
                         image_url=data.get("image_url") or None,
                         position=int(data.get("position", 0) or 0))
    db.session.add(block)
    db.session.commit()
    return jsonify(id=block.id, text=block.text, image_url=block.image_url), 201

@app.route("/admin/menu/<int:item_id>", methods=["PATCH", "POST"])
@login_required
def edit_menu_item(item_id):
    if not current_user.is_admin:
        abort(403)
    item = db.session.get(MenuItem, item_id)
    if item is None:
        abort(404)
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    if "name" in data:
        name = str(data["name"]).strip()
        if not name or len(name) > 160:
            return jsonify(error="Invalid name."), 400
        item.name = name
    if "price" in data:
        try:
            price = Decimal(str(data["price"]).replace("€", "").strip()).quantize(CENT)
            if price <= 0 or price > Decimal("9999.99"):
                raise InvalidOperation
        except (InvalidOperation, ValueError):
            return jsonify(error="Invalid price."), 400
        item.price = price
    upload = request.files.get("image")
    if upload and upload.filename:
        filename = secure_filename(upload.filename)
        extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if extension not in ALLOWED_IMAGE_EXTENSIONS:
            return jsonify(error="Unsupported image format."), 400
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        filename = f"menu-{item.id}-{int(time.time())}.{extension}"
        upload.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        item.image_url = f"/static/uploads/{filename}"
    db.session.commit()
    return jsonify(id=item.id, name=item.name, price=f"{item.price:.2f}", image_url=item.image_url)

def initialize_database():
    with app.app_context():
        db.create_all()
        for entry in MENU_ITEMS:
            item_id = entry["id"]
            existing = db.session.get(MenuItem, item_id)
            expected_img = entry.get("img") or f"/static/images/dishes/dish-{item_id}.jpg"
            if existing is None:
                raw_price = str(entry["price"]).replace("€", "").replace(",", ".").strip()
                db.session.add(
                    MenuItem(
                        id=item_id,
                        name=entry["name"],
                        description=entry["desc"],
                        price=Decimal(raw_price),
                        image_url=expected_img,
                    )
                )
            elif not existing.image_url or not os.path.exists(os.path.join("static", existing.image_url.lstrip("/").replace("static/", "", 1))):
                existing.image_url = expected_img
        db.session.commit()

@app.cli.command("init-db")
def init_db_command():
    initialize_database()
    print("Database tables and default menu are ready.")

initialize_database()


@app.route("/map")
def map_directions():
    lang = session.get("lang", "de")
    t = TRANSLATIONS.get(lang, TRANSLATIONS["de"])
    return render_template("map.html", t=t, links=LINKS, lang=lang)



@app.route('/favicon.ico')
def favicon():
    for candidate in ('favicon.ico', 'images/favicon.png', 'images/dishes/gyros.jpg'):
        full_path = os.path.join(app.static_folder or 'static', candidate)
        if os.path.isfile(full_path):
            return send_from_directory(app.static_folder or 'static', candidate)
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><circle cx="32" cy="32" r="30" fill="#ffc107"/><text x="32" y="42" text-anchor="middle" font-size="30" fill="#212529">Y</text></svg>'
    return Response(svg, mimetype='image/svg+xml')


@app.after_request
def apply_security_headers(response):
    response.headers.setdefault('X-Content-Type-Options', 'nosniff')
    response.headers.setdefault('X-Frame-Options', 'SAMEORIGIN')
    response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
    return response

if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "0.0.0.0"),
            port=int(os.environ.get("PORT", "5000")),
            debug=os.environ.get("FLASK_DEBUG", "0") == "1")
