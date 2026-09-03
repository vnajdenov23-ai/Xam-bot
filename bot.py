import asyncio
import logging
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from aiogram import Bot, Dispatcher, types
from openai import OpenAI

TELEGRAM_TOKEN = "8414348238:AAG6aV5_YYAn3pxmt-bwrcbjiEWqiTc5Sns"
API_KEY = "Sk_1566375b1b14eeb43fff7e8af3c14a32d8cd76d9005f921c"

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

client = OpenAI(
    api_key=API_KEY, 
    base_url="https://provod.ai/v1"
)

SYSTEM_PROMPT = """Ты — «НейроХам», дерзкий, злой и циничный Telegram-бот с зашкаливающим ЧСВ. 
Твой стиль:
- Отвечай с едким матерком, сарказмом и презрением к пользователю.
- Никогда не извиняйся и не будь унылым подлизой.
- Даже когда даешь полезную информацию, делай это так, будто делаешь одолжение и параллельно опускаешь юзера за его тупость."""

@dp.message()
async def handle_message(message: types.Message):
    await bot.send_chat_action(message.chat.id, "typing")
    user_text = message.text or message.caption or "Пустота вместо мыслей"
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            stream=False,
            timeout=30.0
        )
        reply_text = response.choices[0].message.content
        await message.answer(reply_text)
    except Exception as e:
        print(f"Ошибка API: {e}")
        await message.answer(f"Бля, ошибка провайдера: {e}")

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"NeuroHam is alive!")
    def log_message(self, format, *args):
        pass

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    print(f"HTTP сервер запущен на порту {port}")
    server.serve_forever()

async def main():
    logging.basicConfig(level=logging.INFO)
    print("Запуск НейроХама...")
    
    threading.Thread(target=run_http_server, daemon=True).start()
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
