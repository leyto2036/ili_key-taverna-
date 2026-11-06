from flask import Flask, render_template, session, redirect, url_for, request
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'taverna-munich-secret-key-2026'

TRANSLATIONS = {
    'de': {
        'title': 'Taverna Yamas | Griechisches Restaurant in München',
        'subtitle': 'Traditionelle griechische Küche im Herzen von München',
        'about_title': 'Taverna Yamas München',
        'about_text': 'Willkommen in der Taverna Yamas! Genießen Sie authentische griechische Spezialitäten, frisch zubereitete Grillgerichte und erlesene Weine in gemütlicher Atmosphäre im Herzen von München.',
        'address_label': 'Dollmannstr. 27, 81541 München (Route planen)',
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
        'address_label': 'Dollmannstr. 27, 81541 München (Get Directions)',
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
        'about_text': 'Добро пожаловать в Таверну Ямас! Насладитесь аутентичными греческими блюдами, свежими кушаньями на гриле и уютной атмосферкой в самом центре Мюнхена.',
        'address_label': 'Dollmannstr. 27, 81541 München (Проложить маршрут)',
        'menu_btn': 'Открыть меню',
        'menu_photos_btn': 'Фото меню',
        'menu_title': 'Наше меню',
        'order_btn': 'Заказать еду',
        'to_order': 'Заказать',
        'back_to_menu': 'Назад',
        'tables_btn': '🪑 В зале: 5/10 | Терраса: 5/10 свободно',
        'tables_edit': 'Изменить места',
        'tables_modal_title': 'Бронирование столика и управление',
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
    {"id": 1, "name": "Gyros Plate", "desc": "Zartes Fleisch vom Spieß mit Tzatziki, Pommes und Salat.", "price": "15.90 €", "img": "/static/images/dishes/WhatsApp Image 20-04-23 at 19.26.48.jpeg"},
    {"id": 2, "name": "Souvlaki Spieße", "desc": "Gegrillte Fleischspieße nach traditioneller Art mit Kräutern.", "price": "14.90 €", "img": "/static/images/dishes/WhatsApp Image 202-04-23 at 19.26.48.jpeg"},
    {"id": 3, "name": "Moussaka Classic", "desc": "Traditioneller Auflauf mit Auberginen, Hackfleisch und Béchamelsauce.", "price": "16.20 €", "img": "/static/images/dishes/WhatsApp Image 2026-0-23 at 19.26.48.jpeg"},
    {"id": 4, "name": "Bifteki Feta", "desc": "Gefülltes Hacksteak mit Schafskäse, dazu aromatischer Reis.", "price": "15.50 €", "img": "/static/images/dishes/WhatsApp Image 2026-04 at 19.26.48.jpeg"},
    {"id": 5, "name": "Griechischer Bauernsalat", "desc": "Tomaten, Gurken, Oliven, original Schafskäse und Olivenöl.", "price": "9.90 €", "img": "/static/images/dishes/WhatsApp Image 2026-04-2 at 19.26.48.jpeg"},
    {"id": 6, "name": "Tzatziki & Warme Pita", "desc": "Hausgemachter Joghurtdip mit frischem Knoblauch und Pita.", "price": "5.90 €", "img": "/static/images/dishes/WhatsApp Image 2026-04-23 at 1.26.48.jpeg"},
    {"id": 7, "name": "Suflaki Special", "desc": "Zarte Spieße vom Grill mit Spezialmarinade.", "price": "16.50 €", "img": "/static/images/dishes/WhatsApp Image 2026-04-23 at 19.26.4.jpeg"},
    {"id": 8, "name": "Keftedakia", "desc": "Griechische Hackbällchen in Tomatensoße.", "price": "12.90 €", "img": "/static/images/dishes/WhatsApp Image 2026-04-23 at 19.26.47.jpeg"},
    {"id": 9, "name": "Bifteki Special", "desc": "Gegrilltes Hacksteak mit Kräuterbutter.", "price": "14.50 €", "img": "/static/images/dishes/WhatsApp Image 2026-04-23 at 19.26.48.jpeg"},
    {"id": 10, "name": "Calamares", "desc": "Knusprig frittierte Tintenfischringe mit Zitrone und Aioli.", "price": "16.90 €", "img": "/static/images/dishes/WhatsApp Image 2026-04-23 at 19.26.jpeg"},
    {"id": 11, "name": "Exklusiver Grillteller", "desc": "Auswahl an verschiedenen Fleischsorten vom Grill.", "price": "19.90 €", "img": "/static/images/dishes/WhatsApp Image 2026-04-23 at 19.6.48.jpeg"},
    {"id": 12, "name": "Gyros Special", "desc": "Gyros mit Metaxasoße und Käse überbacken.", "price": "17.20 €", "img": "/static/images/dishes/WhatsApp Image 2026-04-23 at 9.26.48.jpeg"},
    {"id": 13, "name": "Gemista", "desc": "Gefüllte Tomaten und Paprika mit Reis und Kräutern.", "price": "13.90 €", "img": "/static/images/dishes/WhatsApp Image 2026-4-23 at 19.26.48.jpeg"},
    {"id": 14, "name": "Santorini Platte", "desc": "Große Auswahl für 2 Personen mit diversen Spezialitäten.", "price": "36.00 €", "img": "/static/images/dishes/WhatsApp Image 206-04-23 at 19.26.48.jpeg"},
    {"id": 15, "name": "Greek Dessert", "desc": "Traditionelles Gebäck mit Honig und Nüssen.", "price": "6.50 €", "img": "/static/images/dishes/WhatsApp Image 26-04-23 at 19.26.48.jpeg"}
]

MENU_IMAGES = [
    "/static/images/menu/photo_2026-04-26_17-39-45.jpg",
    "/static/images/menu/photo_2026-04-26_17-39-47.jpg",
    "/static/images/menu/photo_2026-04-26_17-39-49.jpg",
    "/static/images/menu/photo_2026-04-26_17-39-51.jpg",
    "/static/images/menu/photo_2026-04-26_17-39-53.jpg",
    "/static/images/menu/photo_2026-04-26_17-39-56.jpg",
    "/static/images/menu/photo_2026-04-27_14-07-52 (2).jpg"
]

LINKS = {
    'maps': 'https://www.google.com/maps/place//data=!4m2!3m1!19sChIJoaYxZBTfnUcRTbUsyCEoArQ',
    'lieferando': 'https://www.lieferando.de/en/menu/taverna-yamas-munchen',
    'wolt': 'https://wolt.com/de/deu/munich/restaurant/taverna-yamas-dstr',
    'uber': 'https://www.ubereats.com/de/store/taverna-yamas',
    'uber_code': 'eats-34arbu6yk1',
    'phone': 'tel:+49894483787'
}

@app.context_processor
def inject_globals():
    lang = session.get('lang', 'de')
    if lang not in TRANSLATIONS:
        lang = 'de'
    return dict(t=TRANSLATIONS[lang], current_lang=lang, menu=MENU_ITEMS, menu_images=MENU_IMAGES, links=LINKS)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_language/<lang>')
def set_language(lang):
    if lang in TRANSLATIONS:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
