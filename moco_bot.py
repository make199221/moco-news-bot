import re
import json
import time
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup


# =========================================================
# НАСТРОЙКИ
# =========================================================

TOKEN = "ВСТАВЬ_НОВЫЙ_ТОКЕН"
CHAT_ID = "-1004337354549"

CELLSTRING_URL = "https://cellstring.com/moco/events"

# Проверяем CellString каждую минуту
CHECK_EVERY = 60

STATE_FILE = "sent_events.json"


# =========================================================
# ОТПРАВКА ФОТО
# =========================================================

def send_photo(image_file, text):

    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

    try:

        with open(image_file, "rb") as photo:

            response = requests.post(
                url,
                data={
                    "chat_id": CHAT_ID,
                    "caption": text
                },
                files={
                    "photo": photo
                },
                timeout=30
            )

        result = response.json()

        if not result.get("ok"):

            print("❌ Ошибка Telegram:", result)

            return False

        print("✅ Фото отправлено в Telegram")

        return True

    except Exception as e:

        print("❌ Ошибка отправки фото:", e)

        return False


# =========================================================
# ОТПРАВКА СООБЩЕНИЯ О НАЧАЛЕ СОБЫТИЯ
# =========================================================

def send_start_message(event_name):

    if event_name == "Double Chaos Energy":

        text = "⚡ Двойная энергия хаоса началась!"

    elif event_name == "Overcharged Alert":

        text = "🔥 Сверхзаряженные монстры начались!"

    else:

        return False

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    try:

        response = requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "text": text
            },
            timeout=20
        )

        result = response.json()

        if not result.get("ok"):

            print("❌ Ошибка Telegram:", result)

            return False

        print("✅ Сообщение о начале отправлено")

        return True

    except Exception as e:

        print("❌ Ошибка отправки:", e)

        return False


# =========================================================
# ЗАГРУЗКА CELLSTRING
# =========================================================

def get_cellstring_text():

    response = requests.get(
        CELLSTRING_URL,
        timeout=20
    )

    print(
        "CellString status:",
        response.status_code
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    return soup.get_text(
        " ",
        strip=True
    )


# =========================================================
# ПАРСИНГ СОБЫТИЙ
# =========================================================

def parse_events(text):

    pattern = (
        r'(\d{1,2}:\d{2}\s(?:AM|PM))\s+'
        r'(Double Chaos Energy|Overcharged Alert)\s+'
        r'(?:ended|in\b)'
    )

    matches = re.findall(
        pattern,
        text
    )

    events = []

    current_date = datetime.now().date()

    previous_time = None

    for time_text, event_name in matches:

        event_time = datetime.strptime(
            time_text,
            "%I:%M %p"
        ).time()

        # Переход через полночь
        if (
            previous_time is not None
            and event_time < previous_time
        ):

            current_date += timedelta(
                days=1
            )

        previous_time = event_time

        # CellString показывает время в UTC.
        # Для Казахстана добавляем +5 часов.
        event_datetime = (
            datetime.combine(
                current_date,
                event_time
            )
            + timedelta(hours=5)
        )

        events.append(
            {
                "datetime": event_datetime,
                "time": event_datetime.strftime(
                    "%H:%M"
                ),
                "name": event_name
            }
        )

    return events


# =========================================================
# ТЕКСТ + КАРТИНКА ДЛЯ УВЕДОМЛЕНИЯ ЗА 10 МИНУТ
# =========================================================

def get_event_message(
    event_name,
    event_time
):

    if event_name == "Double Chaos Energy":

        text = (
            "⚡ Двойная энергия хаоса "
            "уже через 10 минут!\n\n"
            "🎮 Ник: A_r_e_S"
        )

        return "x2.jpg", text

    if event_name == "Overcharged Alert":

        text = (
            "🔥 Сверхзаряженные монстры "
            "уже через 10 минут!\n\n"
            "🎮 Ник: A_r_e_S"
        )

        return "overcharged.jpg", text

    return None, None


# =========================================================
# ЗАГРУЗКА ОТПРАВЛЕННЫХ СОБЫТИЙ
# =========================================================

def load_sent():

    try:

        with open(
            STATE_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return set(
                json.load(f)
            )

    except FileNotFoundError:

        return set()


# =========================================================
# СОХРАНЕНИЕ ОТПРАВЛЕННЫХ СОБЫТИЙ
# =========================================================

def save_sent(sent):

    with open(
        STATE_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            list(sent),
            f,
            ensure_ascii=False,
            indent=2
        )


# =========================================================
# ОСНОВНАЯ ПРОГРАММА
# =========================================================

def main():

    print(
        "🤖 MoCo NEWS запускается..."
    )

    print(
        "📢 Автоматические события: "
        "x2 + сверхзаряженные монстры"
    )

    sent = load_sent()

    while True:

        try:

            print(
                "\n🔄 Проверяю CellString..."
            )

            text = get_cellstring_text()

            events = parse_events(text)

            now = datetime.now()

            print(
                f"📅 Найдено событий: "
                f"{len(events)}"
            )

            for event in events:

                event_datetime = (
                    event["datetime"]
                )

                seconds_left = (
                    event_datetime - now
                ).total_seconds()

                minutes_left = (
                    seconds_left / 60
                )

                print(
                    f"   {event['time']} — "
                    f"{event['name']} | "
                    f"осталось "
                    f"{minutes_left:.1f} мин."
                )

                # =================================================
                # УВЕДОМЛЕНИЕ ЗА 10 МИНУТ
                # =================================================

                if (
                    9.5
                    <= minutes_left
                    <= 10.5
                ):

                    key_10 = (
                        f"10MIN|"
                        f"{event_datetime.isoformat()}|"
                        f"{event['name']}"
                    )

                    if key_10 in sent:

                        print(
                            "⏭ Уведомление "
                            "за 10 минут уже отправлено"
                        )

                    else:

                        (
                            image_file,
                            message
                        ) = get_event_message(
                            event["name"],
                            event["time"]
                        )

                        if image_file is not None:

                            print(
                                "🚨 Событие через "
                                "10 минут: "
                                f"{event['name']}"
                            )

                            success = send_photo(
                                image_file,
                                message
                            )

                            if success:

                                sent.add(
                                    key_10
                                )

                                save_sent(
                                    sent
                                )

                                print(
                                    "📤 Уведомление "
                                    "за 10 минут "
                                    "отправлено"
                                )

                # =================================================
                # УВЕДОМЛЕНИЕ В МОМЕНТ НАЧАЛА
                # =================================================

                if (
                    -0.5
                    <= minutes_left
                    <= 0.5
                ):

                    key_start = (
                        f"START|"
                        f"{event_datetime.isoformat()}|"
                        f"{event['name']}"
                    )

                    if key_start in sent:

                        print(
                            "⏭ Сообщение "
                            "о начале уже отправлено"
                        )

                    else:

                        print(
                            "🚀 Событие началось: "
                            f"{event['name']}"
                        )

                        success = (
                            send_start_message(
                                event["name"]
                            )
                        )

                        if success:

                            sent.add(
                                key_start
                            )

                            save_sent(
                                sent
                            )

                            print(
                                "📤 Сообщение "
                                "о начале отправлено"
                            )

            print(
                f"💤 Следующая проверка через "
                f"{CHECK_EVERY} секунд"
            )

        except Exception as e:

            print(
                f"❌ Ошибка: {e}"
            )

        time.sleep(
            CHECK_EVERY
        )


# =========================================================
# ЗАПУСК
# =========================================================

if __name__ == "__main__":

    main()