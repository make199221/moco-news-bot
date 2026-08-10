from http.server import BaseHTTPRequestHandler
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os
import re
import requests
from bs4 import BeautifulSoup


TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = "-1004337354549"

CELLSTRING_URL = "https://cellstring.com/moco/events"

KZ = ZoneInfo("Asia/Almaty")
UTC = ZoneInfo("UTC")


def send_photo(image_url, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "photo": image_url,
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

    return soup.get_text(
        " ",
        strip=True
    )


def parse_events(text):
    pattern = (
        r'(\d{1,2}:\d{2}\s(?:AM|PM))\s+'
        r'(Double Chaos Energy|Overcharged Alert)\s+'
        r'(?:ended|in\b)'
    )

    matches = re.findall(pattern, text)

    events = []

    current_date = datetime.now(KZ).date()
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
            tzinfo=UTC
        ).astimezone(KZ)

        events.append({
            "datetime": event_datetime,
            "time": event_datetime.strftime("%H:%M"),
            "name": event_name
        })

    return events


def get_event_message(event_name):

    if event_name == "Double Chaos Energy":

        return (
            "https://raw.githubusercontent.com/"
            "make199221/moco-news-bot/main/x2.jpg",
            "⚡ Двойная энергия хаоса уже через 10 минут!"
        )

    if event_name == "Overcharged Alert":

        return (
            "https://raw.githubusercontent.com/"
            "make199221/moco-news-bot/main/overcharged.jpg",
            "🔥 Сверхзаряженные монстры уже через 10 минут!"
        )

    return None, None


def check_events():

    text = get_cellstring_text()

    events = parse_events(text)

    now = datetime.now(KZ)

    results = []

    for event in events:

        event_datetime = event["datetime"]

        minutes_left = (
            event_datetime - now
        ).total_seconds() / 60

        results.append({
            "time": event["time"],
            "name": event["name"],
            "minutes_left": round(minutes_left, 2)
        })

        # Уведомление примерно за 10 минут
        if 9 <= minutes_left <= 10.5:

            image_url, message = get_event_message(
                event["name"]
            )

            if image_url:

                send_photo(
                    image_url,
                    message
                )

                print(
                    f"📤 Отправлено: "
                    f"{event['name']} "
                    f"{event['time']}"
                )

    return results


class handler(BaseHTTPRequestHandler):

    def do_GET(self):

        try:

            results = check_events()

            body = {
                "ok": True,
                "message": "MoCo events checked",
                "events": results
            }

            response = str(body).encode("utf-8")

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "application/json; charset=utf-8"
            )

            self.end_headers()

            self.wfile.write(response)

        except Exception as e:

            print("ERROR:", e)

            body = {
                "ok": False,
                "error": str(e)
            }

            response = str(body).encode("utf-8")

            self.send_response(500)

            self.send_header(
                "Content-Type",
                "application/json; charset=utf-8"
            )

            self.end_headers()

            self.wfile.write(response)