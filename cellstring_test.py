import requests

URL = "https://cellstring.com/moco/events"

response = requests.get(URL, timeout=20)

print("Статус:", response.status_code)
print("Размер страницы:", len(response.text))

with open("cellstring.html", "w", encoding="utf-8") as f:
    f.write(response.text)

print("HTML сохранён в cellstring.html")