function flipCard(event, cardElement) {
    if (['INPUT', 'TEXTAREA', 'LABEL', 'I', 'BUTTON'].includes(event.target.tagName)) return;
    cardElement.classList.toggle('flipped');
}

// Управление фоном и разрешением Hero
function updateHeroBg(event) {
    let file = event.target.files[0];
    if (file) {
        let reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('heroHeader').style.backgroundImage = `linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.75)), url('${e.target.result}')`;
        }
        reader.readAsDataURL(file);
    }
}

let heroFit = 'cover';
function toggleHeroFit() {
    let hero = document.getElementById('heroHeader');
    heroFit = heroFit === 'cover' ? 'contain' : (heroFit === 'contain' ? 'auto' : 'cover');
    hero.style.backgroundSize = heroFit;
    alert('Режим масштабирования фона: ' + heroFit);
}

// Настройка размера карточек блюд
function adjustCardSize(delta) {
    let cards = document.querySelectorAll('.card-flip');
    let currentHeight = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--card-height')) || 340;
    let newHeight = Math.max(280, Math.min(450, currentHeight + delta));
    document.documentElement.style.setProperty('--card-height', newHeight + 'px');
}

function syncName(id) {
    document.getElementById('back-name-' + id).value = document.getElementById('front-name-' + id).value;
}
function syncFrontName(id) {
    document.getElementById('front-name-' + id).value = document.getElementById('back-name-' + id).value;
}
function syncPrice(id) {
    document.getElementById('front-price-' + id).innerText = document.getElementById('back-price-' + id).value;
}
function updateImage(event, id) {
    let file = event.target.files[0];
    if (file) {
        let reader = new FileReader();
        reader.onload = function(e) { document.getElementById('img-view-' + id).src = e.target.result; }
        reader.readAsDataURL(file);
    }
}

// Добавление перемещаемых блоков с описанием и фото
function addMovableBlock() {
    let area = document.getElementById('customDescriptionArea');
    let blockId = 'block-' + Date.now();
    
    let div = document.createElement('div');
    div.className = 'draggable-block';
    div.id = blockId;
    div.style.top = '20px';
    div.style.left = '20px';
    
    div.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-2">
            <small class="fw-bold text-primary"><i class="fas fa-arrows-alt me-1"></i> Перетащи меня</small>
            <button class="btn btn-sm btn-outline-danger py-0 px-1" onclick="this.closest('.draggable-block').remove()">&times;</button>
        </div>
        <textarea class="form-control form-control-sm mb-2" placeholder="Введите текст описания..."></textarea>
        <input type="file" class="form-control form-control-sm mb-2" accept="image/*" onchange="loadBlockImage(event, '${blockId}')">
        <div class="block-img-container"></div>
    `;
    
    area.appendChild(div);
    makeDraggable(div);
}

function loadBlockImage(event, blockId) {
    let file = event.target.files[0];
    if (file) {
        let reader = new FileReader();
        reader.onload = function(e) {
            let container = document.querySelector(`#${blockId} .block-img-container`);
            container.innerHTML = `<img src="${e.target.result}" alt="Custom">`;
        }
        reader.readAsDataURL(file);
    }
}

// Функция перемещения мыщью (Drag & Drop)
function makeDraggable(elmnt) {
    let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
    elmnt.onmousedown = dragMouseDown;

    function dragMouseDown(e) {
        if (['TEXTAREA', 'INPUT', 'BUTTON', 'IMG'].includes(e.target.tagName)) return;
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
    }

    function closeDragElement() {
        document.onmouseup = null;
        document.onmousemove = null;
    }
}

// Корзина
let cart = JSON.parse(localStorage.getItem('taverna_cart')) || [];

function saveCart() {
    localStorage.setItem('taverna_cart', JSON.stringify(cart));
    renderCart();
}

function addToCart(name, priceStr) {
    let price = parseFloat(priceStr.replace('€', '').trim());
    let existing = cart.find(item => item.name === name);
    if (existing) { existing.qty += 1; } else { cart.push({ name: name, price: price, qty: 1 }); }
    saveCart();
    alert('Блюдо добавлено в корзину!');
}

function addToCartFromBack(id) {
    addToCart(document.getElementById('back-name-' + id).value, document.getElementById('back-price-' + id).value);
}

function renderCart() {
    let container = document.getElementById('cartItemsList');
    let totalElem = document.getElementById('cartTotalPrice');
    let countElem = document.getElementById('floatingCartCount');
    let sumElem = document.getElementById('floatingCartSum');
    
    if (cart.length === 0) {
        container.innerHTML = 'Корзина пуста';
        totalElem.innerText = '0.00 €';
        countElem.innerText = '0';
        sumElem.innerText = '0.00 €';
        return;
    }
    let html = '';
    let total = 0;
    let totalCount = 0;
    cart.forEach((item, index) => {
        let sum = item.price * item.qty;
        total += sum;
        totalCount += item.qty;
        html += `<div class="d-flex justify-content-between align-items-center mb-2 border-bottom pb-1">
            <span>${item.name} (x${item.qty})</span>
            <span>${sum.toFixed(2)} € <i class="fas fa-trash text-danger ms-2" style="cursor:pointer;" onclick="removeItem(${index})"></i></span>
        </div>`;
    });
    container.innerHTML = html;
    totalElem.innerText = total.toFixed(2) + ' €';
    countElem.innerText = totalCount;
    sumElem.innerText = total.toFixed(2) + ' €';
}

function removeItem(index) {
    cart.splice(index, 1);
    saveCart();
}

function copyCartToClipboard() {
    if (cart.length === 0) return;
    let text = "Заказ из Taverna Yamas:\n";
    let total = 0;
    cart.forEach(item => {
        text += `- ${item.name} (x${item.qty}) — ${(item.price * item.qty).toFixed(2)} €\n`;
        total += item.price * item.qty;
    });
    text += `Итого: ${total.toFixed(2)} €`;
    
    navigator.clipboard.writeText(text).then(() => {
        alert('Состав заказа скопирован в буфер обмена!');
    });
}

function reserveTable(event) {
    event.preventDefault();
    alert('Спасибо! Бронирование успешное, мы с вами свяжемся в ближайшее время.');
    bootstrap.Modal.getInstance(document.getElementById('tablesModal')).hide();
}

document.addEventListener('DOMContentLoaded', renderCart);
