import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from openai import OpenAI

TELEGRAM_TOKEN = "8414348238:AAG6aV5_YYAn3pxmt-bwrcbjiEWqiTc5Sns"
API_KEY = "Sk_1566375b1b14eeb43fff7e8af3c14a32d8cd76d9005f921c"

WEBHOOK_HOST = os.environ.get("RENDER_EXTERNAL_URL", "https://tvoiservice.onrender.com")
WEBHOOK_PATH = f"/webhook/{TELEGRAM_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

PORT = int(os.environ.get("PORT", 10000))

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
- Пиши коротко, емко и по делу, без долгих соплей."""

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
            max_tokens=800,  # жестко ограничили длину ответа, чтобы не превышать лимиты телеги
            timeout=30.0
        )
        reply_text = response.choices[0].message.content
        
        # Если вдруг текст все равно длиннее 4000 символов, обрезаем его
        if len(reply_text) > 4000:
            reply_text = reply_text[:4000] + "\n\n[Многа букав, я устал читать]"
            
        await message.answer(reply_text)
    except Exception as e:
        print(f"Ошибка API: {e}")
        await message.answer(f"Бля, ошибка провайдера: {e}")

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
