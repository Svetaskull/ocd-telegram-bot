import os
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from openai import OpenAI


bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher()

client = OpenAI()


with open("mark_prompt.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()


@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Марк на связи.\n"
        "Кидай пост — посмотрим, что он из него выкопает."
    )


@dp.message()
async def message_handler(message: Message):
    post = message.text or message.caption or ""

    try:
        response = client.responses.create(
            model="gpt-5.6-luna",
            instructions=system_prompt,
            input=f"Пост канала:\n{post}\n\nНапиши один комментарий Марка."
        )

        await message.reply(response.output_text)

    except Exception as e:
        print("Ошибка OpenAI:", e)
        await message.answer(
            "Марк временно сломался. Где-то опять ебаное API."
        )


async def main():
    print("Марк запущен в Telegram.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())