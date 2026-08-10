import re
from bs4 import BeautifulSoup

with open("cellstring.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
text = soup.get_text(" ", strip=True)

pattern = r'(\d{1,2}:\d{2}\s(?:AM|PM))\s+(Double Chaos Energy|Overcharged Alert)\s+(?:ended|in\b)'

events = re.findall(pattern, text)

print("\n📅 СОБЫТИЯ:\n")

for time, event in events:
    print(f"🕐 {time} — {event}")

print(f"\nВсего найдено: {len(events)}")