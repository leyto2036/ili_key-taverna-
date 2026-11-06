// Корзина
let cart = [];

function addToCart(name, priceStr) {
    let price = parseFloat(priceStr.replace('€', '').trim());
    let existing = cart.find(i => i.name === name);
    if (existing) {
        existing.qty += 1;
    } else {
        cart.push({ name, price, qty: 1 });
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

// Синхронизация карточек меню
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

// Изменение размера карточек меню
function adjustCardSize(delta) {
    // Плавное изменение ширины или масштаба
}

// Переворот карточки
function flipCard(event, cardElement) {
    cardElement.classList.toggle('flipped');
}

// Смена фона Hero
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

// Редактор блоков с обтеканием и кнопкой «Сохранить»
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
    let fileInput = block.querySelector('.block-file-input');
    
    // Создаем зафиксированный элемент для контейнера ниже
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
    block.remove(); // Очищаем текущий редактор
}

// Функция перетаскивания мышкой
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

// Редактирование мест
function saveTableSeats() {
    let indoor = document.getElementById('inputIndoorFree').value;
    let terrace = document.getElementById('inputTerraceFree').value;
    let text = `🪑 Innen: ${indoor}/10 | Terrasse: ${terrace}/10 frei`;
    document.getElementById('tablesBadgeText').innerText = text;
    document.getElementById('modalTablesInfoText').innerText = `Innenbereich: 10 Tische (${indoor} frei). Außen / Terrasse: 10 Tische (${terrace} frei).`;
    
    let modal = bootstrap.Modal.getInstance(document.getElementById('editTablesModal'));
    modal.hide();
}

// Скрытие/показ инструментов редактора по клику в шторке
let toolsVisible = true;
function toggleEditorTools() {
    toolsVisible = !toolsVisible;
    let editTools = document.querySelectorAll('.edit-tool');
    editTools.forEach(el => {
        el.style.display = toolsVisible ? '' : 'none';
    });
}

// Лампочка (День / Ночь)
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
    event.preventDefault();
    alert('Vielen Dank! Ihre Reservierung war erfolgreich.');
    let modal = bootstrap.Modal.getInstance(document.getElementById('tablesModal'));
    modal.hide();
}

// Плавное открытие/скрытие меню (смещение левой колонки)
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
