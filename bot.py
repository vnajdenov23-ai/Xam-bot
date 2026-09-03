import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from openai import OpenAI
from aiohttp import web

# Твои данные жестко вшиты
TELEGRAM_TOKEN = "8414348238:AAF0u7EhNIQKsfoTduia0wn7mXzNb97D7oo"
API_KEY = "Sk_1566375b1b14eeb43fff7e8af3c14a32d8cd76d9005f921c"

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

client = OpenAI(
    api_key=API_KEY, 
    base_url="https://api.deepseek.com"
)

# Характер НейроХама
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
        print(f"Ошибка: {e}")
        await message.answer("Бля, серваки от твоей духоты упали. Попробуй позже, если мозгов хватит.")

# Веб-заглушка, чтобы Render видел открытый порт и не ругался
async def handle_ping(request):
    return web.Response(text="НейроХам пашет и ждет жертв!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"ПОРТ ОТКРЫТ: {port}")

async def main():
    logging.basicConfig(level=logging.INFO)
    print("Запуск НейроХама...")
    
    # Сразу запускаем веб-сервер для порта Render
    await web_server()
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
