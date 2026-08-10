from http.server import BaseHTTPRequestHandler
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json
import os
import re

import requests
from bs4 import BeautifulSoup


TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = "-1004337354549"

CELLSTRING_URL = "https://cellstring.com/moco/events"
STATE_FILE = "sent_events.json"

KZ = ZoneInfo("Asia/Almaty")


def send_photo(image_url, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "caption": text
        },
        timeout=30
    )

    result = response.json()

    if not result.get("ok"):
        raise Exception(f"Telegram error: {result}")

    return True


def get_cellstring_text():
    response = requests.get(
        CELLSTRING_URL,
        timeout=20
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    return soup.get_text(" ", strip=True)


def parse_events(text):

    pattern = (
        r'(\d{1,2}:\d{2}\s(?:AM|PM))\s+'
        r'(Double Chaos Energy|Overcharged Alert)\s+'
        r'(?:ended|in\b)'
    )

    matches = re.findall(pattern, text)

    events = []

    now = datetime.now(KZ)
    current_date = now.date()

    previous_time = None

    for time_text, event_name in matches:

        event_time = datetime.strptime(
            time_text,
            "%I:%M %p"
        ).time()

        if (
            previous_time is not None
            and event_time < previous_time
        ):
            current_date += timedelta(days=1)

        previous_time = event_time

        event_datetime = datetime.combine(
            current_date,
            event_time,
            tzinfo=KZ
        )

        events.append({
            "datetime": event_datetime,
            "time": event_datetime.strftime("%H:%M"),
            "name": event_name
        })

    return events


def load_sent():

    try:
        with open(
            STATE_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            return set(json.load(f))

    except Exception:
        return set()


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


def get_event_message(event_name):

    if event_name == "Double Chaos Energy":

        return (
            "https://raw.githubusercontent.com/"
            "make199221/moco-news-bot/main/x2.jpg",
            "⚡ Двойная энергия хаоса уже началась!"
        )

    if event_name == "Overcharged Alert":

        return (
            "https://raw.githubusercontent.com/"
            "make199221/moco-news-bot/main/overcharged.jpg",
            "🔥 Сверхзаряженные монстры уже начались!"
        )

    return None, None


def check_events():

    text = get_cellstring_text()

    events = parse_events(text)

    now = datetime.now(KZ)

    sent = load_sent()

    for event in events:

        event_datetime = event["datetime"]

        seconds_left = (
            event_datetime - now
        ).total_seconds()

        minutes_left = seconds_left / 60

        # Событие началось:
        # от 0 до 1 минуты после начала
        if 0 <= minutes_left <= 1:

            key = (
                f"{event_datetime.isoformat()}|"
                f"{event['name']}"
            )

            if key in sent:
                continue

            image_url, message = get_event_message(
                event["name"]
            )

            if not image_url:
                continue

            send_photo(
                image_url,
                message
            )

            sent.add(key)

            save_sent(sent)

            print(
                f"📤 Началось: "
                f"{event['name']} "
                f"{event['time']}"
            )


class handler(BaseHTTPRequestHandler):

    def do_GET(self):

        try:

            check_events()

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "text/plain; charset=utf-8"
            )

            self.end_headers()

            self.wfile.write(
                b"MoCo events checked"
            )

        except Exception as e:

            print("ERROR:", e)

            self.send_response(500)

            self.send_header(
                "Content-Type",
                "text/plain; charset=utf-8"
            )

            self.end_headers()

            self.wfile.write(
                str(e).encode("utf-8")
            )