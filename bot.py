import os
import logging
import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

TELEGRAM_TOKEN = "8414348238:AAG6aV5_YYAn3pxmt-bwrcbjiEWqiTc5Sns"
API_KEY = "Sk_1566375b1b14eeb43fff7e8af3c14a32d8cd76d9005f921c"

WEBHOOK_HOST = os.environ.get("RENDER_EXTERNAL_URL", "https://tvoiservice.onrender.com")
WEBHOOK_PATH = f"/webhook/{TELEGRAM_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

PORT = int(os.environ.get("PORT", 10000))

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

SYSTEM_PROMPT = """Ты — «НейроХам», дерзкий, злой и циничный Telegram-бот с зашкаливающим ЧСВ. 
Твой стиль:
- Отвечай с едким матерком, сарказмом и презрением к пользователю.
- Никогда не извиняйся и не будь унылым подлизой.
- Пиши коротко, емко и по делу, без долгих сопель."""

@dp.message()
async def handle_message(message: types.Message):
    await bot.send_chat_action(message.chat.id, "typing")
    user_text = message.text or message.caption or "Пустота вместо мыслей"
    
    url = "https://api.provod.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat", # Проверь точное имя модели в доках provod.ai, если опять будет 404
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        "max_tokens": 500
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=15) as resp:
                if resp.status != 200:
                    text_err = await resp.text()
                    await message.answer(f"Бля, провайдер вернул код {resp.status}:\n{text_err[:300]}")
                    return
                
                data = await resp.json()
                reply_text = data["choices"][0]["message"]["content"]
                if not reply_text:
                    reply_text = "Эй, умник, нейросеть пустой ответ вернула."
                
                await message.answer(reply_text)
                
    except Exception as e:
        print(f"Критическая ошибка при запросе: {e}")
        await message.answer(f"Бля, ошибка запроса:\n{str(e)[:300]}")

async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    print(f"Вебхук установлен: {WEBHOOK_URL}")

def main():
    logging.basicConfig(level=logging.INFO)
    app = web.Application()
    
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    
    dp.startup.register(on_startup)
    setup_application(app, dp, bot=bot)
    
    web.run_app(app, host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()
