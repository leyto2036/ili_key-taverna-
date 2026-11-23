import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
API_BASE_URL = os.environ.get("TAVERNA_API_BASE_URL", "http://127.0.0.1:5000").strip().rstrip("/")
STAFF_API_TOKEN = os.environ.get("STAFF_API_TOKEN", "").strip()
ALLOWED_IDS_RAW = os.environ.get("TELEGRAM_ALLOWED_USER_IDS", "").strip()

ALLOWED_USER_IDS = {
    int(x.strip())
    for x in ALLOWED_IDS_RAW.split(",")
    if x.strip().lstrip("-").isdigit()
}


def tg_request(method: str, params: dict | None = None) -> dict:
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    data = urllib.parse.urlencode(params or {}).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=35) as resp:
        return json.loads(resp.read().decode("utf-8"))


def send_message(chat_id: int | str, text: str) -> None:
    try:
        tg_request("sendMessage", {"chat_id": chat_id, "text": text})
    except Exception as exc:
        print("Failed to send Telegram message:", exc)


def call_staff_api(action: str, item: str = "") -> dict:
    url = f"{API_BASE_URL}/api/staff/availability"
    body = json.dumps({"action": action, "item": item}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "X-Staff-Token": STAFF_API_TOKEN,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def call_get_availability() -> list[str]:
    url = f"{API_BASE_URL}/api/menu/availability"
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("out_of_stock", []) if isinstance(data, dict) else []


def is_authorized(user_id: int | None) -> bool:
    if not ALLOWED_USER_IDS:
        return False
    return user_id in ALLOWED_USER_IDS


def handle_message(msg: dict) -> None:
    chat = msg.get("chat") or {}
    chat_id = chat.get("id")
    sender = msg.get("from") or {}
    user_id = sender.get("id")
    text = (msg.get("text") or "").strip()

    if chat_id is None or not text:
        return

    if not is_authorized(user_id):
        send_message(chat_id, f"Доступ запрещён. Ваш Telegram ID: {user_id}")
        return

    parts = text.split(maxsplit=1)
    cmd = parts[0].lower().split("@")[0]
    arg = parts[1].strip() if len(parts) > 1 else ""

    if cmd in ("/start", "/help"):
        send_message(
            chat_id,
            "Управление наличием блюд и напитков (24/7):\n"
            "/list — показать, чего сейчас нет в наличии\n"
            "/out <Название> — отметить как «нет в наличии»\n"
            "/in <Название> — вернуть позицию в наличие\n"
            "/clear — очистить список недоступных позиций",
        )
        return

    if cmd == "/list":
        items = call_get_availability()
        if not items:
            send_message(chat_id, "Все позиции сейчас доступны к заказу.")
        else:
            send_message(chat_id, "Нет в наличии:\n• " + "\n• ".join(items))
        return

    if cmd == "/out":
        if not arg:
            send_message(chat_id, "Укажите название позиции: /out Gyros Metaxa")
            return
        res = call_staff_api("mark_out", arg)
        items = res.get("out_of_stock", [])
        send_message(chat_id, f"Отмечено как «нет в наличии»: {arg}\nТекущий список: {', '.join(items) or 'пусто'}")
        return

    if cmd == "/in":
        if not arg:
            send_message(chat_id, "Укажите название позиции: /in Gyros Metaxa")
            return
        res = call_staff_api("mark_in", arg)
        items = res.get("out_of_stock", [])
        send_message(chat_id, f"Возвращено в наличие: {arg}\nТекущий список: {', '.join(items) or 'все доступно'}")
        return

    if cmd == "/clear":
        call_staff_api("clear")
        send_message(chat_id, "Список недоступных позиций очищен — все блюда и напитки снова доступны.")
        return

    send_message(chat_id, "Неизвестная команда. Используйте /help.")


def main() -> None:
    if not BOT_TOKEN:
        print("Error: set TELEGRAM_BOT_TOKEN environment variable.")
        return
    if not STAFF_API_TOKEN:
        print("Error: set STAFF_API_TOKEN environment variable.")
        return
    if not ALLOWED_USER_IDS:
        print("Error: set TELEGRAM_ALLOWED_USER_IDS (comma-separated Telegram user IDs).")
        return

    print("Taverna 24/7 availability bot started...")
    offset = 0
    while True:
        try:
            res = tg_request("getUpdates", {"offset": offset, "timeout": 25})
            if res.get("ok"):
                for upd in res.get("result", []):
                    offset = int(upd["update_id"]) + 1
                    message = upd.get("message") or upd.get("edited_message")
                    if message:
                        try:
                            handle_message(message)
                        except Exception as e:
                            chat_id = (message.get("chat") or {}).get("id")
                            if chat_id is not None:
                                send_message(chat_id, f"Ошибка при обращении к серверу: {e}")
        except urllib.error.URLError as e:
            print("Network error in bot polling:", e)
            time.sleep(3)
        except Exception as e:
            print("Unexpected bot error:", e)
            time.sleep(3)


if __name__ == "__main__":
    main()
