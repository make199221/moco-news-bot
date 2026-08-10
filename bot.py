import requests

TOKEN = "8858109214:AAGa5drgGTecTc0iuHP2JbobbEX08or-Ef4"
CHAT_ID = "-1004337354549"

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

response = requests.post(
    url,
    data={
        "chat_id": CHAT_ID,
        "text": "🤖 Тест: бот успешно подключён к MoCo NEWS!"
    }
)

print(response.json())