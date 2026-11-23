
const __tavernaMemStorage = {};
function tavernaStorageGet(key) {
    try {
        if (window.localStorage) return window.tavernaStorageGet(key);
    } catch (e) {}
    return Object.prototype.hasOwnProperty.call(__tavernaMemStorage, key) ? __tavernaMemStorage[key] : null;
}
function tavernaStorageSet(key, val) {
    try {
        if (window.localStorage) {
            window.tavernaStorageSet(key, val);
            return true;
        }
    } catch (e) {}
    __tavernaMemStorage[key] = String(val);
    return false;
}

let cart = [];

function addToCart(name, priceStr, itemId = null) {
    let price = parseFloat(String(priceStr).replace('€', '').replace(',', '.').trim());
    if (Number.isNaN(price)) price = 0;
    const parsedId = itemId !== null && itemId !== '' && !Number.isNaN(Number(itemId)) ? Number(itemId) : null;
    let existing = cart.find(i => i.name === name);
    if (existing) {
        existing.qty += 1;
        if (existing.id == null && parsedId != null) existing.id = parsedId;
    } else {
        cart.push({ id: parsedId, name, price, qty: 1 });
    }
    updateCartUI();
}

function addToCartFromBack(id) {
    let name = document.getElementById(`back-name-${id}`).value;
    let priceStr = document.getElementById(`back-price-${id}`).value;
    addToCart(name, priceStr);
}

function updateCartUI() {
    let totalQty = cart.reduce((sum, i) => sum + i.qty, 0);
    let totalPrice = cart.reduce((sum, i) => sum + (i.price * i.qty), 0);

    document.getElementById('floatingCartCount').innerText = totalQty;
    document.getElementById('floatingCartSum').innerText = totalPrice.toFixed(2) + ' €';
    document.getElementById('cartTotalPrice').innerText = totalPrice.toFixed(2) + ' €';

    let list = document.getElementById('cartItemsList');
    if (cart.length === 0) {
        list.innerHTML = 'Ihr Warenkorb ist leer';
    } else {
        list.innerHTML = cart.map(i => `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <span>${i.name} (x${i.qty})</span>
                <strong>${(i.price * i.qty).toFixed(2)} €</strong>
            </div>
        `).join('');
    }
}

function copyCartToClipboard() {
    try {
        const lines = (typeof cart !== 'undefined' && Array.isArray(cart) ? cart : []).map(
            i => `${i.name} x${i.qty} (${(i.price * i.qty).toFixed(2)} €)`
        );
        const text = lines.length ? lines.join('\n') : 'Taverna Yamas Bestellung';
        if (navigator && navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
            navigator.clipboard.writeText(text).catch(() => {});
        }
    } catch (e) {}
}

function syncName(id) {
    let val = document.getElementById(`front-name-${id}`).value;
    document.getElementById(`back-name-${id}`).value = val;
}

function syncFrontName(id) {
    let val = document.getElementById(`back-name-${id}`).value;
    document.getElementById(`front-name-${id}`).value = val;
}

function syncPrice(id) {
    let val = document.getElementById(`back-price-${id}`).value;
    document.getElementById(`front-price-${id}`).innerText = val;
}

function flipCard(event, cardElement) {
    cardElement.classList.toggle('flipped');
}

function toggleHeroFit() {
    let hero = document.getElementById('heroHeader');
    if (hero.style.backgroundSize === 'contain') {
        hero.style.backgroundSize = 'cover';
    } else {
        hero.style.backgroundSize = 'contain';
    }
}

function updateHeroBg(event) {
    let file = event.target.files[0];
    if (file) {
        let reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('heroHeader').style.backgroundImage = `url('${e.target.result}')`;
        }
        reader.readAsDataURL(file);
    }
}

let blockCounter = 0;

function addMovableBlock() {
    blockCounter++;
    let area = document.getElementById('customDescriptionArea');
    
    let blockDiv = document.createElement('div');
    blockDiv.className = 'movable-block p-3 bg-light rounded-4 shadow-sm border mb-3 position-relative';
    blockDiv.id = `block-${blockCounter}`;
    blockDiv.style.cursor = 'move';
    
    blockDiv.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-2">
            <span class="fw-bold text-primary small"><i class="fas fa-arrows-alt me-1"></i> Блок описания</span>
            <div class="d-flex gap-1">
                <button class="btn btn-sm btn-success fw-bold px-2 py-0" onclick="saveBlock(${blockCounter})" title="Сохранить блок"><i class="fas fa-check me-1"></i> Сохранить</button>
                <button class="btn btn-sm btn-outline-danger py-0 px-2" onclick="this.closest('.movable-block').remove()"><i class="fas fa-times"></i></button>
            </div>
        </div>
        <div class="clearfix">
            <img src="" class="block-preview-img float-start me-3 mb-2 rounded border" style="max-width: 150px; display: none;" alt="Preview">
            <textarea class="form-control mb-2" rows="3" placeholder="Введите текст описания..."></textarea>
            <input type="file" class="form-control form-control-sm block-file-input" accept="image/*" onchange="previewBlockImage(event, ${blockCounter})">
        </div>
    `;
    
    makeElementDraggable(blockDiv);
    area.appendChild(blockDiv);
}

function previewBlockImage(event, id) {
    let file = event.target.files[0];
    if (file) {
        let reader = new FileReader();
        reader.onload = function(e) {
            let block = document.getElementById(`block-${id}`);
            let img = block.querySelector('.block-preview-img');
            img.src = e.target.result;
            img.style.display = 'block';
        }
        reader.readAsDataURL(file);
    }
}

function saveBlock(id) {
    let block = document.getElementById(`block-${id}`);
    let textarea = block.querySelector('textarea');
    let img = block.querySelector('.block-preview-img');
    
    let savedContainer = document.getElementById('savedBlocksContainer');
    let savedCard = document.createElement('div');
    savedCard.className = 'p-3 bg-white rounded-4 shadow-sm border mb-3 clearfix position-relative';
    
    let imgSrc = img.style.display !== 'none' ? img.src : '';
    let textVal = textarea.value;
    
    savedCard.innerHTML = `
        <button class="position-absolute top-0 end-0 m-2 btn btn-sm btn-outline-danger border-0" onclick="this.closest('div').remove()"><i class="fas fa-times"></i></button>
        ${imgSrc ? `<img src="${imgSrc}" class="float-start me-3 mb-2 rounded shadow-sm" style="max-width: 180px; object-fit: cover;" alt="Photo">` : ''}
        <p class="text-muted lh-lg mb-0" style="white-space: pre-wrap;">${textVal}</p>
    `;
    
    savedContainer.appendChild(savedCard);
    block.remove();

    if (textVal.trim() || imgSrc) {
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        const headers = { 'Content-Type': 'application/json' };
        if (csrfMeta && csrfMeta.content) headers['X-CSRFToken'] = csrfMeta.content;

        fetch('/api/content-blocks', {
            method: 'POST',
            headers,
            body: JSON.stringify({
                text: textVal.trim(),
                image_url: imgSrc || null,
                position: savedContainer.children.length
            })
        }).catch(() => {});
    }
}

function makeElementDraggable(elmnt) {
    let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
    elmnt.onmousedown = dragMouseDown;

    function dragMouseDown(e) {
        if (e.target.tagName === 'TEXTAREA' || e.target.tagName === 'INPUT' || e.target.tagName === 'BUTTON' || e.target.closest('button')) {
            return;
        }
        e.preventDefault();
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = closeDragElement;
        document.onmousemove = elementDrag;
    }

    function elementDrag(e) {
        e.preventDefault();
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;
        elmnt.style.top = (elmnt.offsetTop - pos2) + "px";
        elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
        elmnt.style.position = 'relative';
    }

    function closeDragElement() {
        document.onmouseup = null;
        document.onmousemove = null;
    }
}

function saveTableSeats() {
    let indoor = document.getElementById('inputIndoorFree').value;
    let terrace = document.getElementById('inputTerraceFree').value;
    let text = `🪑 Innen: ${indoor}/10 | Terrasse: ${terrace}/10 frei`;
    document.getElementById('tablesBadgeText').innerText = text;
    document.getElementById('modalTablesInfoText').innerText = `Innenbereich: 10 Tische (${indoor} frei). Außen / Terrasse: 10 Tische (${terrace} frei).`;
    
    let modal = bootstrap.Modal.getInstance(document.getElementById('editTablesModal'));
    modal.hide();
}

let toolsVisible = true;
function toggleEditorTools() {
    toolsVisible = !toolsVisible;
    let editTools = document.querySelectorAll('.edit-tool');
    editTools.forEach(el => {
        el.style.display = toolsVisible ? '' : 'none';
    });
}

function toggleTheme() {
    let body = document.body;
    let icon = document.getElementById('themeIcon');
    if (body.getAttribute('data-theme') === 'light') {
        body.setAttribute('data-theme', 'dark');
        body.classList.add('bg-dark', 'text-white');
        icon.className = 'fas fa-lightbulb text-warning';
    } else {
        body.setAttribute('data-theme', 'light');
        body.classList.remove('bg-dark', 'text-white');
        icon.className = 'fas fa-lightbulb text-secondary';
    }
}

function reserveTable(event) {
    if (event) event.preventDefault();
    const form = event && event.target && event.target.tagName === 'FORM'
        ? event.target
        : document.querySelector('#tablesModal form');
    const dateVal = form?.querySelector('#resDate, input[type="date"], input[name="date"]')?.value || '';
    const timeVal = form?.querySelector('#resTime, input[type="time"], input[name="time"]')?.value || '';
    const guestsVal = form?.querySelector('#resPersons, input[type="number"], input[name="guests"], input[name="persons"]')?.value || '2';
    const zoneVal = form?.querySelector('select[name="zone"]')?.value || 'indoor';

    const demoEmail = 'lehanefodov@gmail.com';
    const summaryText = [
        'Taverna Yamas — Tischreservierung (Demo)',
        `Ziel-E-Mail: ${demoEmail}`,
        `Datum: ${dateVal || '-'}`,
        `Uhrzeit: ${timeVal || '-'}`,
        `Personen: ${guestsVal}`,
        `Bereich: ${zoneVal}`
    ].join('\n');

    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    const headers = { 'Content-Type': 'application/json' };
    if (csrfMeta && csrfMeta.content) headers['X-CSRFToken'] = csrfMeta.content;

    if (dateVal && timeVal) {
        fetch('/api/reservations', {
            method: 'POST',
            headers,
            body: JSON.stringify({
                date: dateVal,
                time: timeVal,
                guests: Number(guestsVal) || 2,
                zone: zoneVal
            })
        }).catch(() => {});
    }

    fetch('/api/demo/notify', {
        method: 'POST',
        headers,
        body: JSON.stringify({
            kind: 'reservation',
            recipient: demoEmail,
            summary: summaryText
        })
    })
    .then(r => r.json().catch(() => ({})))
    .then(info => {
        if (info && info.email_sent) {
            alert(`Vielen Dank! Reservierung wurde real an ${demoEmail} gesendet.`);
        } else {
            const mailtoUrl = `mailto:${demoEmail}?subject=${encodeURIComponent('Taverna Yamas Demo — Tischreservierung')}&body=${encodeURIComponent(summaryText)}`;
            alert(`Бронь зафиксирована. Реальная отправка почты на ${demoEmail} сработает автоматически после добавления RESEND_API_KEY или SMTP_* в окружение. Можно также открыть почтовый клиент: ${mailtoUrl}`);
        }
    })
    .catch(() => {
        alert(`Reservierung erfasst (${demoEmail}).`);
    });

    const modalEl = document.getElementById('tablesModal');
    const modal = modalEl && window.bootstrap ? bootstrap.Modal.getInstance(modalEl) : null;
    if (modal) modal.hide();
}

function toggleMenuColumn() {
    let leftCol = document.getElementById('leftColumn');
    let menuSec = document.getElementById('menuSection');
    
    if (menuSec.classList.contains('d-none')) {
        menuSec.classList.remove('d-none');
        leftCol.classList.remove('col-lg-12');
        leftCol.classList.add('col-lg-6');
    } else {
        menuSec.classList.add('d-none');
        leftCol.classList.remove('col-lg-6');
        leftCol.classList.add('col-lg-12');
    }
}

function getFulfillmentMode() {
    const picked = document.querySelector('input[name="fulfillmentMode"]:checked');
    return picked ? picked.value : 'delivery';
}

function selectFulfillmentAndOpenCart(mode) {
    const radio = document.getElementById(mode === 'pickup' ? 'modePickup' : 'modeDelivery');
    if (radio) radio.checked = true;
    updateCartUI();
    const modalEl = document.getElementById('cartModal');
    if (modalEl && window.bootstrap) {
        bootstrap.Modal.getOrCreateInstance(modalEl).show();
    }
}

const _origUpdateCartUI = typeof updateCartUI === 'function' ? updateCartUI : null;
updateCartUI = function () {
    if (_origUpdateCartUI) _origUpdateCartUI();
    const subtotal = cart.reduce((sum, i) => sum + (i.price * i.qty), 0);
    const isPickup = getFulfillmentMode() === 'pickup';
    const discount = isPickup ? subtotal * 0.10 : 0;
    const finalSum = Math.max(0, subtotal - discount);

    const discRow = document.getElementById('pickupDiscountRow');
    const discAmt = document.getElementById('cartDiscountAmount');
    if (discRow && discAmt) {
        discRow.classList.toggle('d-none', !isPickup || subtotal <= 0);
        discAmt.innerText = `-${discount.toFixed(2)} €`;
    }
    const totalEl = document.getElementById('cartTotalPrice');
    const floatSumEl = document.getElementById('floatingCartSum');
    if (totalEl) totalEl.innerText = `${finalSum.toFixed(2)} €`;
    if (floatSumEl) floatSumEl.innerText = `${finalSum.toFixed(2)} €`;
};

let _lastReceiptPlainText = '';

function completeOrderAndGenerateReceipt() {
    if (!cart || cart.length === 0) {
        alert('Корзина пуста / Warenkorb ist leer');
        return;
    }
    const subtotal = cart.reduce((sum, i) => sum + (i.price * i.qty), 0);
    const isPickup = getFulfillmentMode() === 'pickup';
    const discount = isPickup ? subtotal * 0.10 : 0;
    const total = Math.max(0, subtotal - discount);
    const paySel = document.getElementById('paymentMethodSelect');
    const payMethod = paySel ? paySel.value : 'Online';
    const orderId = 'TY-' + String(Date.now()).slice(-6);
    const nowStr = new Date().toLocaleString('de-DE');

    const rowsHtml = cart.map(i =>
        `<div class="d-flex justify-content-between mb-1"><span>${i.name} × ${i.qty}</span><strong>${(i.price * i.qty).toFixed(2)} €</strong></div>`
    ).join('');

    const demoEmail = 'lehanefodov@gmail.com';
    const wantsOnlineStripe = /online|karte|stripe/i.test(payMethod);
    const itemsWithDbId = cart.filter(i => i.id !== null && i.id !== undefined && !Number.isNaN(Number(i.id)));

    const orderSummaryText = [
        `Taverna Yamas — Beleg ${orderId} (Demo)`,
        `Benachrichtigung an: ${demoEmail}`,
        `Datum: ${nowStr}`,
        `Art: ${isPickup ? 'Selbstabholung (-10%)' : 'Lieferung'} | Zahlung: ${payMethod}`,
        ...cart.map(i => `- ${i.name} x${i.qty}: ${(i.price * i.qty).toFixed(2)} €`),
        isPickup ? `Rabatt (-10%): -${discount.toFixed(2)} €` : null,
        `Gesamt: ${total.toFixed(2)} €`
    ].filter(Boolean).join('\n');

    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    const headers = { 'Content-Type': 'application/json' };
    if (csrfMeta && csrfMeta.content) headers['X-CSRFToken'] = csrfMeta.content;

    if (isPickup) {
        fetch('/api/demo/notify', {
            method: 'POST',
            headers,
            body: JSON.stringify({
                kind: 'pickup_order',
                recipient: demoEmail,
                order_id: orderId,
                subtotal: subtotal.toFixed(2),
                discount: discount.toFixed(2),
                total: total.toFixed(2),
                summary: orderSummaryText
            })
        }).catch(() => {});
    }

    if (wantsOnlineStripe && isPickup && itemsWithDbId.length === cart.length && cart.length > 0) {
        fetch('/api/checkout', {
            method: 'POST',
            headers,
            body: JSON.stringify({
                pickup: true,
                items: cart.map(i => ({ id: Number(i.id), quantity: Number(i.qty) }))
            })
        })
        .then(async res => {
            const payload = await res.json().catch(() => ({}));
            if (res.status === 201 && payload.checkout_url) {
                window.location.href = payload.checkout_url;
            }
        })
        .catch(() => {});
    }

    const htmlBody = `
        <div class="mb-2"><strong>Beleg-Nr.:</strong> ${orderId}<br><strong>Datum:</strong> ${nowStr}<br><strong>Taverna Yamas</strong> • Dollmannstr. 27, 81541 München<br><strong>Steuernummer:</strong> 145/205/01127</div>
        <div class="alert alert-success py-1 px-2 small mb-2">Demo-Benachrichtigung an: <strong>${demoEmail}</strong></div>
        <hr class="my-2">
        <div class="mb-2"><strong>Art:</strong> ${isPickup ? 'Selbstabholung (-10%)' : 'Lieferung'}<br><strong>Zahlung:</strong> ${payMethod}</div>
        <hr class="my-2">
        <div class="mb-2">${rowsHtml}</div>
        <div class="d-flex justify-content-between small text-muted"><span>Zwischensumme:</span><span>${subtotal.toFixed(2)} €</span></div>
        ${isPickup ? `<div class="d-flex justify-content-between small text-success fw-bold"><span>Rabatt Selbstabholung (-10%):</span><span>-${discount.toFixed(2)} €</span></div>` : ''}
        <div class="d-flex justify-content-between fs-6 fw-bold border-top pt-2 mt-1"><span>Gesamtbetrag:</span><span>${total.toFixed(2)} €</span></div>
    `;

    _lastReceiptPlainText = [
        `Taverna Yamas — Beleg ${orderId} (${nowStr})`,
        `Dollmannstr. 27, 81541 München | Steuernummer: 145/205/01127`,
        `Art: ${isPickup ? 'Selbstabholung (-10%)' : 'Lieferung'} | Zahlung: ${payMethod}`,
        ...cart.map(i => `- ${i.name} x${i.qty}: ${(i.price * i.qty).toFixed(2)} €`),
        isPickup ? `Rabatt (-10%): -${discount.toFixed(2)} €` : null,
        `Gesamt: ${total.toFixed(2)} €`
    ].filter(Boolean).join('\n');

    const bodyContainer = document.getElementById('receiptBodyContent');
    if (bodyContainer) bodyContainer.innerHTML = htmlBody;

    const cartModalEl = document.getElementById('cartModal');
    if (cartModalEl && window.bootstrap) {
        const inst = bootstrap.Modal.getInstance(cartModalEl);
        if (inst) inst.hide();
    }
    const receiptModalEl = document.getElementById('receiptModal');
    if (receiptModalEl && window.bootstrap) {
        bootstrap.Modal.getOrCreateInstance(receiptModalEl).show();
    }
}

function copyReceiptText() {
    if (!_lastReceiptPlainText) return;
    navigator.clipboard?.writeText(_lastReceiptPlainText);
}

function syncDishQtyBadges() {
    const qtyMap = new Map();
    if (Array.isArray(cart)) {
        cart.forEach(item => {
            qtyMap.set(item.name, (qtyMap.get(item.name) || 0) + item.qty);
        });
    }
    document.querySelectorAll('[data-dish-qty]').forEach(el => {
        const dishName = el.getAttribute('data-dish-qty');
        const q = qtyMap.get(dishName) || 0;
        el.textContent = String(q);
        el.classList.toggle('is-empty', q === 0);
    });
}

function changeDishQty(name, priceStr, delta) {
    const price = parseFloat(String(priceStr).replace('€', '').replace(',', '.').trim()) || 0;
    const idx = cart.findIndex(i => i.name === name);
    if (delta > 0) {
        if (idx >= 0) cart[idx].qty += delta;
        else cart.push({ name, price, qty: delta });
    } else if (delta < 0 && idx >= 0) {
        cart[idx].qty += delta;
        if (cart[idx].qty <= 0) cart.splice(idx, 1);
    }
    updateCartUI();
    syncDishQtyBadges();
}

const _prevUpdateCartUI = typeof updateCartUI === 'function' ? updateCartUI : null;
updateCartUI = function () {
    if (_prevUpdateCartUI) _prevUpdateCartUI();
    syncDishQtyBadges();
};

document.addEventListener('DOMContentLoaded', () => {
    syncDishQtyBadges();
});

function syncRouteCardSummary() {
    const countEl = document.getElementById('routeSummaryCount');
    const itemsEl = document.getElementById('routeSummaryItems');
    const subEl = document.getElementById('routeSummarySubtotal');
    const pickupEl = document.getElementById('routeSummaryPickupTotal');
    const modeBadgeEl = document.getElementById('routeSummaryModeBadge');
    if (!countEl || !itemsEl || !subEl || !pickupEl) return;

    const list = Array.isArray(cart) ? cart : [];
    const totalQty = list.reduce((sum, i) => sum + i.qty, 0);
    const subtotal = list.reduce((sum, i) => sum + (i.price * i.qty), 0);
    const pickupTotal = Math.max(0, subtotal * 0.90);
    const isPickup = typeof getFulfillmentMode === 'function' && getFulfillmentMode() === 'pickup';

    countEl.textContent = String(totalQty);
    subEl.textContent = `${subtotal.toFixed(2)} €`;
    pickupEl.textContent = `${pickupTotal.toFixed(2)} €`;

    if (modeBadgeEl) {
        modeBadgeEl.textContent = isPickup ? 'Abholung (-10%) aktiv' : 'Abholung -10% möglich';
    }

    if (list.length === 0) {
        itemsEl.textContent = '—';
    } else {
        itemsEl.innerHTML = list
            .map(i => `<div class="d-flex justify-content-between"><span>${i.name} × ${i.qty}</span><strong>${(i.price * i.qty).toFixed(2)} €</strong></div>`)
            .join('');
    }
}

const _beforeRouteSummaryUpdate = typeof updateCartUI === 'function' ? updateCartUI : null;
updateCartUI = function () {
    if (_beforeRouteSummaryUpdate) _beforeRouteSummaryUpdate();
    syncRouteCardSummary();
};

document.addEventListener('DOMContentLoaded', () => {
    syncRouteCardSummary();
});


function clearCart() {
    cart = [];
    updateCartUI();
}

const activeMenuCategories = new Set();

function toggleMenuCategory(cat, btnEl) {
    if (activeMenuCategories.has(cat)) {
        activeMenuCategories.delete(cat);
        if (btnEl) {
            btnEl.classList.remove('active', 'btn-warning');
            btnEl.classList.add('btn-outline-warning');
        }
    } else {
        activeMenuCategories.add(cat);
        if (btnEl) {
            btnEl.classList.add('active', 'btn-warning');
            btnEl.classList.remove('btn-outline-warning');
        }
    }
    applyMenuCombinedSort();
}

function applyMenuCombinedSort() {
    const grid = document.getElementById('menuItemsGrid');
    if (!grid) return;
    const cards = Array.from(grid.querySelectorAll('.menu-dish-item'));
    cards.sort((a, b) => {
        const aCat = a.dataset.category || 'food';
        const bCat = b.dataset.category || 'food';
        const aMatch = activeMenuCategories.size === 0 ? 1 : (activeMenuCategories.has(aCat) ? 1 : 0);
        const bMatch = activeMenuCategories.size === 0 ? 1 : (activeMenuCategories.has(bCat) ? 1 : 0);
        if (aMatch !== bMatch) return bMatch - aMatch;
        return Number(a.dataset.origIndex || 0) - Number(b.dataset.origIndex || 0);
    });
    cards.forEach((card, idx) => {
        const isMatched = activeMenuCategories.size === 0 || activeMenuCategories.has(card.dataset.category);
        card.style.order = isMatched ? String(idx) : String(1000 + idx);
        card.classList.toggle('d-none', activeMenuCategories.size > 0 && !isMatched);
        card.classList.remove('opacity-50');
        grid.appendChild(card);
    });
}


function goToMenuForPickup(event) {
    if (event) event.preventDefault();
    try {
        tavernaStorageSet('taverna_fulfillment', 'pickup');
    } catch (e) {}

    const pickupRadio = document.getElementById('modePickup');
    if (pickupRadio) {
        pickupRadio.checked = true;
        pickupRadio.dispatchEvent(new Event('change', { bubbles: true }));
    }
    if (typeof updateCartUI === 'function') {
        updateCartUI();
    }

    const orderModalEl = document.getElementById('orderModal');
    if (orderModalEl && window.bootstrap) {
        const inst = bootstrap.Modal.getInstance(orderModalEl);
        if (inst) inst.hide();
    }

    const currentCart = Array.isArray(window.cart) ? window.cart : (typeof cart !== 'undefined' ? cart : []);
    const hasItems = Array.isArray(currentCart) && currentCart.length > 0;

    if (!hasItems) {
        const menuSec = document.getElementById('menuSection') || document.getElementById('menuItemsGrid');
        if (menuSec) {
            menuSec.classList.remove('d-none');
            menuSec.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        let hint = document.getElementById('pickupEmptyHint');
        if (!hint && menuSec) {
            hint = document.createElement('div');
            hint.id = 'pickupEmptyHint';
            hint.className = 'alert alert-warning fw-bold mb-3';
            hint.textContent = 'Корзина пуста — выберите и добавьте блюда из меню для самовывоза (-10%).';
            menuSec.prepend(hint);
        } else if (hint) {
            hint.classList.remove('d-none');
        }
        return;
    }

    const confirmed = window.confirm('Вы уже выбрали всё необходимое для заказа на самовывоз (-10%)?');
    if (confirmed) {
        const cartModalEl = document.getElementById('cartModal');
        if (cartModalEl && window.bootstrap) {
            bootstrap.Modal.getOrCreateInstance(cartModalEl).show();
        }
    }
}

function focusSection(sectionId, event) {
    if (event) event.preventDefault();
    if (sectionId === 'menuSection') {
        const menuSec = document.getElementById('menuSection');
        const leftCol = document.getElementById('leftColumn');
        if (menuSec && menuSec.classList.contains('d-none')) {
            menuSec.classList.remove('d-none');
            if (leftCol) {
                leftCol.classList.remove('col-lg-12');
                leftCol.classList.add('col-lg-6');
            }
        }
        if (typeof sortMenuByDemand === 'function') {
            sortMenuByDemand();
        }
    }
    const el = document.getElementById(sectionId);
    if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function getDemandScore(card) {
    const baseDemand = Number(card.dataset.demand || 50);
    const name = (card.querySelector('.card-title, h5, h6')?.textContent || '').trim();
    let boosts = 0;
    try {
        const stats = JSON.parse(tavernaStorageGet('taverna_item_demand') || '{}');
        if (name && stats[name]) boosts = Number(stats[name]) * 10;
    } catch (e) {}
    return baseDemand + boosts;
}

function sortMenuByDemand() {
    const grid = document.getElementById('menuItemsGrid');
    if (!grid) return;
    const cards = Array.from(grid.querySelectorAll('.menu-dish-item'));
    cards.sort((a, b) => {
        const diff = getDemandScore(b) - getDemandScore(a);
        if (diff !== 0) return diff;
        return Number(a.dataset.origIndex || 0) - Number(b.dataset.origIndex || 0);
    });
    cards.forEach((card, idx) => {
        card.style.order = String(idx);
        grid.appendChild(card);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    sortMenuByDemand();
});


function chooseCartPickup() {
    const pickupRadio = document.getElementById('modePickup');
    if (pickupRadio) {
        pickupRadio.checked = true;
        pickupRadio.dispatchEvent(new Event('change', { bubbles: true }));
    }
    try { tavernaStorageSet('taverna_fulfillment', 'pickup'); } catch (e) {}
    if (typeof updateCartUI === 'function') updateCartUI();
}

document.addEventListener('DOMContentLoaded', () => {
    const cartModalEl = document.getElementById('cartModal');
    if (cartModalEl) {
        cartModalEl.addEventListener('show.bs.modal', () => {
            const promptEl = document.getElementById('cartFulfillmentPrompt');
            const currentCart = Array.isArray(window.cart) ? window.cart : (typeof cart !== 'undefined' ? cart : []);
            if (promptEl) {
                if (Array.isArray(currentCart) && currentCart.length > 0) {
                    promptEl.classList.remove('d-none');
                } else {
                    promptEl.classList.add('d-none');
                }
            }
        });
    }
});


function toggleFloatingModesDrawer() {
    const drawer = document.getElementById('floatingModesDrawer');
    if (drawer) drawer.classList.toggle('d-none');
}

function selectModeAndJump(cat, btnEl) {
    const menuSec = document.getElementById('menuSection');
    if (menuSec) {
        menuSec.classList.remove('d-none');
    }
    if (typeof toggleMenuCategory === 'function') {
        toggleMenuCategory(cat, btnEl);
    }
    const targetEl = menuSec || document.getElementById('menuCategoryFilters');
    if (targetEl) {
        const headerOffset = (document.getElementById('stickyTopHeader')?.offsetHeight || 90) + 12;
        const y = targetEl.getBoundingClientRect().top + window.scrollY - headerOffset;
        window.scrollTo({ top: Math.max(0, y), behavior: 'smooth' });
    }
    const drawer = document.getElementById('floatingModesDrawer');
    if (drawer) drawer.classList.add('d-none');
}


function estimateWaitTimeMinutes(items, isPickup) {
    if (!Array.isArray(items) || items.length === 0) {
        return { text: '—', minMinutes: 0, maxMinutes: 0 };
    }
    let totalPrep = 0;
    let totalQty = 0;
    items.forEach(item => {
        const name = String(item.name || '').toLowerCase();
        const qty = Math.max(1, Number(item.qty) || 1);
        totalQty += qty;
        let perUnit = 16;
        if (/pizza|пицц/i.test(name)) perUnit = 18;
        else if (/pasta|паст|nudel/i.test(name)) perUnit = 16;
        else if (/gyros|souvlaki|grill|teller|lamm|fisch|steak|мяс|рыб|гриль/i.test(name)) perUnit = 22;
        else if (/drink|spritz|negroni|beer|bier|ouzo|wein|коктейл|пив|напит|sauce|соус|tzatziki|meze|закус/i.test(name)) perUnit = 8;
        totalPrep += perUnit * qty;
    });
    const baseMin = Math.max(10, Math.min(45, Math.round(totalPrep / Math.max(1, totalQty * 0.85)) + (isPickup ? 0 : 5)));
    const maxMin = baseMin + 8;
    return { text: `~${baseMin}–${maxMin} Min.`, minMinutes: baseMin, maxMinutes: maxMin };
}

function refreshWaitTimeBadges() {
    const isPickup = typeof getFulfillmentMode === 'function' ? (getFulfillmentMode() === 'pickup') : false;
    const est = estimateWaitTimeMinutes(typeof cart !== 'undefined' ? cart : [], isPickup);
    const badge = document.getElementById('cartWaitTimeBadge');
    if (badge) badge.textContent = est.text;
    const mockWait = document.getElementById('mockPayWaitLabel');
    if (mockWait) mockWait.textContent = est.text;
}

function addBarItemToCart(name, price, prepMinutes, isAlcohol) {
    const doAdd = () => {
        if (typeof addToCart === 'function') {
            addToCart(name, Number(price).toFixed(2));
        }
        if (typeof refreshWaitTimeBadges === 'function') {
            refreshWaitTimeBadges();
        }
    };
    if (isAlcohol && !_ageVerifiedDemo) {
        openAgeVerifyModal(doAdd);
        return;
    }
    doAdd();
}

function switchPlatformZone(zone) {
    if (zone === 'bar') {
        const barSec = document.getElementById('neighborBarSection');
        if (barSec) barSec.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else {
        const menuSec = document.getElementById('menuSection');
        if (menuSec) menuSec.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function copyVenuePhone(phoneStr) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(phoneStr).catch(() => {});
    }
    alert(`Номер скопирован: ${phoneStr}`);
}

let _pendingMockOrder = null;

function openMockPaymentModal() {
    if (!cart || cart.length === 0) {
        alert('Корзина пуста / Warenkorb ist leer');
        return;
    }
    const subtotal = cart.reduce((sum, i) => sum + (i.price * i.qty), 0);
    const isPickup = typeof getFulfillmentMode === 'function' ? (getFulfillmentMode() === 'pickup') : false;
    const discount = isPickup ? subtotal * 0.10 : 0;
    const total = Math.max(0, subtotal - discount);
    const paySel = document.getElementById('paymentMethodSelect');
    const payMethod = paySel ? paySel.value : 'Online (Demo)';
    const est = estimateWaitTimeMinutes(cart, isPickup);

    _pendingMockOrder = {
        subtotal,
        isPickup,
        discount,
        total,
        payMethod,
        waitText: est.text,
        orderId: 'TY-' + String(Date.now()).slice(-6),
        nowStr: new Date().toLocaleString('de-DE'),
    };

    const mLabel = document.getElementById('mockPayMethodLabel');
    const dLabel = document.getElementById('mockPayDiscountLabel');
    const wLabel = document.getElementById('mockPayWaitLabel');
    const tLabel = document.getElementById('mockPayTotalLabel');
    if (mLabel) mLabel.textContent = payMethod;
    if (dLabel) dLabel.textContent = isPickup ? `-${discount.toFixed(2)} €` : '0.00 €';
    if (wLabel) wLabel.textContent = est.text;
    if (tLabel) tLabel.textContent = `${total.toFixed(2)} €`;

    const modalEl = document.getElementById('mockPaymentModal');
    if (modalEl && window.bootstrap) {
        const inst = bootstrap.Modal.getOrCreateInstance(modalEl);
        inst.show();
    } else {
        confirmMockPayment();
    }
}

function confirmMockPayment() {
    if (!_pendingMockOrder) {
        openMockPaymentModal();
        return;
    }
    const { subtotal, isPickup, discount, total, payMethod, waitText, orderId, nowStr } = _pendingMockOrder;
    const customerName = (document.getElementById('mockCustomerName')?.value || '').trim() || 'Demo-Gast';
    const demoEmail = 'lehanefodov@gmail.com';
    const paymentTag = `${payMethod} [FAKE/DEMO PAID]`;

    const payModalEl = document.getElementById('mockPaymentModal');
    if (payModalEl && window.bootstrap) {
        const inst = bootstrap.Modal.getInstance(payModalEl);
        if (inst) inst.hide();
    }

    const orderSummaryText = [
        `Taverna Yamas & Bar — Beleg ${orderId} (Demo-Zahlung)`,
        `Kunde: ${customerName}`,
        `Benachrichtigung an: ${demoEmail}`,
        `Datum: ${nowStr}`,
        `Art: ${isPickup ? 'Selbstabholung (-10%)' : 'Lieferung'} | Zahlung: ${paymentTag}`,
        `Geschätzte Wartezeit: ${waitText}`,
        `Altersbestätigung 18+: ${_ageVerifiedDemo ? 'Ja (ohne Speicherung personenbezogener Daten)' : 'Nicht erforderlich / Standard'}`,
        ...cart.map(i => `- ${i.name} x${i.qty}: ${(i.price * i.qty).toFixed(2)} €`),
        isPickup ? `Rabatt (-10%): -${discount.toFixed(2)} €` : null,
        `Gesamt: ${total.toFixed(2)} €`
    ].filter(Boolean).join('\n');

    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    const headers = { 'Content-Type': 'application/json' };
    if (csrfMeta && csrfMeta.content) headers['X-CSRFToken'] = csrfMeta.content;

    fetch('/api/demo/notify', {
        method: 'POST',
        headers,
        body: JSON.stringify({
            kind: isPickup ? 'pickup_order' : 'demo_order',
            recipient: demoEmail,
            order_id: orderId,
            subtotal: subtotal.toFixed(2),
            discount: discount.toFixed(2),
            total: total.toFixed(2),
            wait_time: waitText,
            summary: orderSummaryText
        })
    })
    .then(r => r.json().catch(() => ({})))
    .then(info => {
        if (info && info.email_sent) {
            alert(`Демо-оплата прошла! Заказ и квитанция отправлены на ${demoEmail}. Ориентировочное ожидание: ${waitText}.`);
        }
    })
    .catch(() => {});

    const rowsHtml = cart.map(i =>
        `<div class="d-flex justify-content-between mb-1"><span>${i.name} × ${i.qty}</span><strong>${(i.price * i.qty).toFixed(2)} €</strong></div>`
    ).join('');

    const htmlBody = `
        <div class="mb-2"><strong>Beleg-Nr.:</strong> ${orderId}<br><strong>Datum:</strong> ${nowStr}<br><strong>Kunde:</strong> ${customerName}<br><strong>Taverna Yamas &amp; Bar</strong> • Dollmannstr. 27, 81541 München</div>
        <div class="alert alert-success py-1 px-2 small mb-2">Demo-Zahlung bestätigt • Почта: <strong>${demoEmail}</strong> • Ожидание: <strong>${waitText}</strong></div>
        <hr class="my-2">
        <div class="mb-2"><strong>Art:</strong> ${isPickup ? 'Selbstabholung (-10%)' : 'Lieferung'}<br><strong>Zahlung:</strong> ${paymentTag}</div>${_ageVerifiedDemo ? '<br><strong>18+ Check:</strong> Отмечено (данные не сохраняются)' : ''}
        <hr class="my-2">
        ${rowsHtml}
        <hr class="my-2">
        <div class="d-flex justify-content-between small"><span>Zwischensumme</span><span>${subtotal.toFixed(2)} €</span></div>
        ${isPickup ? `<div class="d-flex justify-content-between small text-success fw-bold"><span>Rabatt Selbstabholung (-10%)</span><span>-${discount.toFixed(2)} €</span></div>` : ''}
        <div class="d-flex justify-content-between fs-6 fw-bold mt-1"><span>Gesamt</span><span>${total.toFixed(2)} €</span></div>
    `;

    _lastReceiptPlainText = orderSummaryText;
    const bodyEl = document.getElementById('receiptBodyContent');
    if (bodyEl) bodyEl.innerHTML = htmlBody;
    const recEl = document.getElementById('receiptModal');
    if (recEl && window.bootstrap) {
        bootstrap.Modal.getOrCreateInstance(recEl).show();
    }
    _pendingMockOrder = null;
}




let _ageVerifiedDemo = false;
let _pendingBarAction = null;

function updateAgeBadgeUI() {
    const badge = document.getElementById('ageStatusBadge');
    if (!badge) return;
    if (_ageVerifiedDemo) {
        badge.className = 'badge bg-success text-white px-3 py-2';
        badge.innerHTML = '<i class="fas fa-check-circle me-1"></i>18+ отмечено (без хранения данных)';
    } else {
        badge.className = 'badge bg-secondary text-light px-3 py-2';
        badge.innerHTML = '<i class="fas fa-shield-halved me-1"></i>Требуется отметка 18+';
    }
}

function openAgeVerifyModal(onVerifiedCallback) {
    _pendingBarAction = typeof onVerifiedCallback === 'function' ? onVerifiedCallback : null;
    const cbEl = document.getElementById('ageConfirmCheckbox');
    if (cbEl) cbEl.checked = false;
    const modalEl = document.getElementById('ageVerifyModal');
    if (modalEl && window.bootstrap) {
        bootstrap.Modal.getOrCreateInstance(modalEl).show();
    } else {
        confirmAgeVerification();
    }
}

function confirmAgeVerification() {
    const cbEl = document.getElementById('ageConfirmCheckbox');
    if (cbEl && !cbEl.checked) {
        alert('Отметьте, что заказчику исполнилось 18 лет.');
        return;
    }
    _ageVerifiedDemo = true;
    updateAgeBadgeUI();

    const modalEl = document.getElementById('ageVerifyModal');
    if (modalEl && window.bootstrap) {
        const inst = bootstrap.Modal.getInstance(modalEl);
        if (inst) inst.hide();
    }

    const action = _pendingBarAction;
    _pendingBarAction = null;
    if (typeof action === 'function') {
        action();
    }
}

function filterBarItems(category, btnEl) {
    const cards = document.querySelectorAll('#neighborBarCards .bar-item-card');
    cards.forEach(card => {
        const c = card.getAttribute('data-bar-cat');
        if (category === 'all' || c === category) {
            card.classList.remove('d-none');
        } else {
            card.classList.add('d-none');
        }
    });
    const btns = document.querySelectorAll('#barFilterButtons button');
    btns.forEach(b => {
        b.classList.remove('btn-warning', 'text-dark', 'active');
        b.classList.add('btn-outline-warning');
    });
    if (btnEl) {
        btnEl.classList.remove('btn-outline-warning');
        btnEl.classList.add('btn-warning', 'text-dark', 'active');
    }
}



function openDrinkPhotoPreview(src, title) {
    const imgEl = document.getElementById('drinkPhotoImg');
    const titleEl = document.getElementById('drinkPhotoTitle');
    if (imgEl) imgEl.src = src;
    if (titleEl) titleEl.textContent = title || 'Напиток';
    const modalEl = document.getElementById('drinkPhotoModal');
    if (modalEl && window.bootstrap) {
        bootstrap.Modal.getOrCreateInstance(modalEl).show();
    }
}

function setCookieConsent(mode) {
    try {
        localStorage.setItem('taverna_cookie_consent', mode);
        document.cookie = 'taverna_cookie_consent=' + encodeURIComponent(mode) + '; path=/; max-age=2592000; SameSite=Lax';
    } catch (e) {}
    const banner = document.getElementById('cookieConsentBanner');
    if (banner) banner.style.display = 'none';
}

function initCookieConsentBanner() {
    let saved = '';
    try {
        saved = localStorage.getItem('taverna_cookie_consent') || '';
    } catch (e) {}
    if (!saved && typeof document.cookie === 'string') {
        const m = document.cookie.match(/(?:^|;\s*)taverna_cookie_consent=([^;]+)/);
        if (m) saved = decodeURIComponent(m[1]);
    }
    const banner = document.getElementById('cookieConsentBanner');
    if (banner && !saved) {
        banner.style.display = 'block';
    }
}

function transferCartToPartner(platformName, baseUrl) {
    const items = (typeof cart !== 'undefined' && Array.isArray(cart)) ? cart : [];
    const lines = items.map(i => `${i.name} x${i.qty} (${(Number(i.price) * Number(i.qty)).toFixed(2)} €)`);
    const payloadText = lines.length
        ? `Taverna Yamas / Yamas Lounge & Bar (${platformName}):\n` + lines.join('\n')
        : `Taverna Yamas / Yamas Lounge & Bar (${platformName})`;
    try {
        if (navigator && navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
            navigator.clipboard.writeText(payloadText).catch(() => {});
        }
    } catch (e) {}
    alert(`Состав заказа скопирован в буфер обмена для ${platformName} (внешние платформы не позволяют автоматически заполнить чужую корзину по ссылке — вставьте список при оформлении).`);
    const sep = baseUrl.includes('?') ? '&' : '?';
    window.open(`${baseUrl}${sep}utm_source=taverna_yamas&utm_medium=partner_transfer`, '_blank', 'noopener,noreferrer');
}

document.addEventListener('DOMContentLoaded', function() {
    initCookieConsentBanner();
});



const CART_RECOVERY_TTL_MS = 2 * 60 * 1000; // 2 минуты
const CART_RECOVERY_KEY = 'taverna_cart_recovery_v1';
let _cartRecoveryMemory = null;

function _getCurrentCartArray() {
    if (Array.isArray(window.cart)) return window.cart;
    if (typeof cart !== 'undefined' && Array.isArray(cart)) return cart;
    return null;
}

function saveCartTwoMinuteBackup() {
    const arr = _getCurrentCartArray();
    if (!arr) return;
    const payload = {
        savedAt: Date.now(),
        items: arr.map(i => ({
            name: String(i.name || ''),
            price: Number(i.price) || 0,
            qty: Number(i.qty) || 1
        })).filter(i => i.name && i.qty > 0)
    };
    _cartRecoveryMemory = payload;
    try {
        if (window.sessionStorage) {
            window.sessionStorage.setItem(CART_RECOVERY_KEY, JSON.stringify(payload));
        }
    } catch (e) {}
    try {
        if (window.localStorage) {
            window.localStorage.setItem(CART_RECOVERY_KEY, JSON.stringify(payload));
        }
    } catch (e) {}
}

function _readCartTwoMinuteBackup() {
    let raw = '';
    try {
        if (window.sessionStorage) {
            raw = window.sessionStorage.getItem(CART_RECOVERY_KEY) || '';
        }
    } catch (e) {}
    if (!raw) {
        try {
            if (window.localStorage) {
                raw = window.localStorage.getItem(CART_RECOVERY_KEY) || '';
            }
        } catch (e) {}
    }
    if (raw) {
        try {
            const parsed = JSON.parse(raw);
            if (parsed && typeof parsed.savedAt === 'number' && Array.isArray(parsed.items)) {
                return parsed;
            }
        } catch (e) {}
    }
    return _cartRecoveryMemory;
}

function _clearCartTwoMinuteBackup() {
    _cartRecoveryMemory = null;
    try { if (window.sessionStorage) window.sessionStorage.removeItem(CART_RECOVERY_KEY); } catch (e) {}
    try { if (window.localStorage) window.localStorage.removeItem(CART_RECOVERY_KEY); } catch (e) {}
}

function restoreCartWithinTwoMinutes() {
    const backup = _readCartTwoMinuteBackup();
    if (!backup || typeof backup.savedAt !== 'number' || !Array.isArray(backup.items)) {
        return false;
    }
    const ageMs = Date.now() - backup.savedAt;
    if (ageMs < 0 || ageMs > CART_RECOVERY_TTL_MS) {
        _clearCartTwoMinuteBackup();
        return false;
    }
    const arr = _getCurrentCartArray();
    if (!arr || backup.items.length === 0) return false;

    arr.length = 0;
    backup.items.forEach(i => {
        arr.push({
            name: String(i.name),
            price: Number(i.price) || 0,
            qty: Number(i.qty) || 1
        });
    });
    if (Array.isArray(window.cart) && window.cart !== arr) {
        window.cart = arr;
    }
    if (typeof updateCartUI === 'function') {
        try { updateCartUI(); } catch (e) {}
    }
    if (typeof refreshWaitTimeBadges === 'function') {
        try { refreshWaitTimeBadges(); } catch (e) {}
    }
    return true;
}

(function installTwoMinuteCartPersistence() {
    if (window.__tavernaCart2MinInstalled) return;
    window.__tavernaCart2MinInstalled = true;

    const wrapFn = (fnName) => {
        const orig = window[fnName];
        if (typeof orig === 'function') {
            window[fnName] = function(...args) {
                const res = orig.apply(this, args);
                saveCartTwoMinuteBackup();
                return res;
            };
        }
    };

    ['addToCart', 'addBarItemToCart', 'updateCartUI', 'changeQty', 'removeFromCart', 'clearCart'].forEach(wrapFn);

    window.addEventListener('beforeunload', saveCartTwoMinuteBackup);
    window.addEventListener('pagehide', saveCartTwoMinuteBackup);
    window.addEventListener('online', () => {
        restoreCartWithinTwoMinutes();
    });

    document.addEventListener('DOMContentLoaded', () => {
        restoreCartWithinTwoMinutes();
        setInterval(() => {
            const b = _readCartTwoMinuteBackup();
            if (b && (Date.now() - b.savedAt) > CART_RECOVERY_TTL_MS) {
                _clearCartTwoMinuteBackup();
            }
        }, 15000);
    });
})();



const TAVERNA_TAX_INFO = {
    steuernummer: '145/205/01127',
    mwstRate: 0.19,
    kassenseriennummer: 'WO-3ED7FA44AF2EA20FFBA23DA4F38',
    tseSeriennummer: '883ECE8AA6B2B4AC70E3E678C2E2CD08E7ED171C8BD7A4BB6C088437B7EC0DB5'
};



let _tavernaOutOfStock = [];

function _isItemOutOfStock(name) {
    const n = String(name || '').trim().toLowerCase();
    if (!n) return false;
    return _tavernaOutOfStock.some(o => String(o).trim().toLowerCase() === n);
}

function applyOutOfStockStateToDom(outList) {
    _tavernaOutOfStock = Array.isArray(outList) ? outList : [];
    const cardsOrButtons = document.querySelectorAll('[data-dish-name], [data-item-name], .menu-item, .bar-item, .dish-card, button');
    cardsOrButtons.forEach(el => {
        const explicitName = el.getAttribute('data-dish-name') || el.getAttribute('data-item-name') || '';
        const text = (explicitName || el.textContent || '').trim();
        if (!text) return;
        const matched = _tavernaOutOfStock.find(o => text.toLowerCase().includes(String(o).trim().toLowerCase()));
        if (el.tagName === 'BUTTON' && (el.onclick || (el.getAttribute('onclick') || '').includes('Cart') || (el.getAttribute('onclick') || '').includes('cart'))) {
            const parentCard = el.closest('.card, .menu-item, .bar-item, .dish-card, li, .col, .col-md-6, .col-lg-4');
            const cardText = (parentCard ? parentCard.textContent : '') + ' ' + explicitName;
            const isOut = _tavernaOutOfStock.some(o => cardText.toLowerCase().includes(String(o).trim().toLowerCase()));
            if (isOut) {
                if (!el.dataset.origHtml) el.dataset.origHtml = el.innerHTML;
                el.disabled = true;
                el.classList.add('disabled', 'opacity-50');
                el.innerHTML = 'Нет в наличии / Ausverkauft';
            } else if (el.dataset.origHtml) {
                el.disabled = false;
                el.classList.remove('disabled', 'opacity-50');
                el.innerHTML = el.dataset.origHtml;
                delete el.dataset.origHtml;
            }
        }
        if (matched && el.tagName !== 'BUTTON') {
            el.setAttribute('data-out-of-stock', '1');
        } else if (el.hasAttribute('data-out-of-stock')) {
            el.removeAttribute('data-out-of-stock');
        }
    });
}

async function fetchTavernaAvailability() {
    try {
        const resp = await fetch('/api/menu/availability', { cache: 'no-store' });
        if (!resp.ok) return;
        const data = await resp.json();
        if (data && data.ok) {
            applyOutOfStockStateToDom(data.out_of_stock || []);
        }
    } catch (e) {}
}

document.addEventListener('DOMContentLoaded', () => {
    fetchTavernaAvailability();
    setInterval(fetchTavernaAvailability, 20000);
});

